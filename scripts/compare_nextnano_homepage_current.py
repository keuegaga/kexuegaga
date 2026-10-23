# -*- coding: utf-8 -*-
"""Compare the computed QCL I-V curve with the current homepage animation."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
DEFAULT_GIF = ROOT / "attachments/nextnano_home_current.gif"
DEFAULT_RUNS = [
    ROOT / "runs/nextnano_negf_home_figures/bai_p0_fast",
    ROOT / "runs/nextnano_negf_home_figures/bai_p1_phys",
    ROOT / "runs/nextnano_negf_home_figures/bai_p1_rest",
    ROOT / "runs/nextnano_negf_home_figures/bai_p2_phys",
    ROOT / "runs/nextnano_negf_home_figures/bai_p2_rest",
    ROOT / "runs/nextnano_negf_home_figures/bai_p3",
    ROOT / "runs/nextnano_negf_home_figures/bai_p3_phys",
    ROOT / "runs/nextnano_negf_home_figures/bai_p3_rest",
    ROOT / "runs/nextnano_negf_home_figures/bai_p4",
    ROOT / "runs/nextnano_negf_home_figures/bai_p4_phys",
    ROOT / "runs/nextnano_negf_home_figures/bai_p4_480",
    ROOT / "runs/nextnano_negf_home_figures/bai_p4_last",
]
DEFAULT_OUT = ROOT / "results/nextnano_home_figures_bai/current_comparison.png"


def load_reference(gif_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Digitize the pure-purple curve in the 1000 x 600 homepage GIF."""
    image = np.asarray(Image.open(gif_path).convert("RGB"))
    mask = np.all(image == np.array([148, 0, 211]), axis=2)

    # Plot frame determined from the published animation.
    left, right, top, bottom = 99, 966, 54, 538
    xs = []
    ys = []
    for x in range(left, right + 1):
        columns = np.where(mask[top : bottom + 1, x])[0]
        if len(columns):
            xs.append(x)
            ys.append(float(np.median(columns + top)))

    xs_array = np.asarray(xs, dtype=float)
    ys_array = np.asarray(ys, dtype=float)
    bias = (xs_array - left) * 500.0 / (right - left)
    current = 5000.0 - (ys_array - top) * 5500.0 / (bottom - top)
    return bias, current


def load_computed(runs: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    data: dict[float, float] = {}
    for run in runs:
        summary = run / "Current_vs_Voltage.dat"
        if summary.exists():
            rows = np.loadtxt(summary, skiprows=1, ndmin=2)
            data.update({float(bias): float(current) for bias, current in rows})
        for bias_dir in run.glob("*mV"):
            match_idx = bias_dir.name.removesuffix("mV")
            try:
                bias = float(match_idx)
            except ValueError:
                continue
            if bias in data:
                continue
            misc = bias_dir / "Current-miscellaneous.txt"
            if not misc.exists():
                continue
            text = misc.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"Current density\s*=\s*([-+0-9.eE]+)", text)
            if match:
                data[bias] = float(match.group(1))
    data = np.asarray(sorted(data.items()), dtype=float)
    return data[:, 0], data[:, 1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gif", type=Path, default=DEFAULT_GIF)
    parser.add_argument("--run", type=Path, action="append", default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    runs = args.run or DEFAULT_RUNS
    ref_bias, ref_current = load_reference(args.gif)
    bias, current = load_computed(runs)
    ref_at_points = np.interp(bias, ref_bias, ref_current)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix(".csv")
    np.savetxt(
        csv_path,
        np.column_stack((bias, current, ref_at_points, current - ref_at_points)),
        delimiter=",",
        header="bias_mV,computed_A_cm2,homepage_A_cm2,difference_A_cm2",
        comments="",
    )

    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.plot(ref_bias, ref_current, "--", color="#666666", label="Homepage GIF")
    ax.plot(bias, current, "o-", color="#7A1FA2", lw=1.4, ms=3.5, label="Computed")
    ax.set_xlim(-10, 510)
    ax.set_ylim(-600, 5200)
    ax.set_xlabel("Potential drop per period (mV)")
    ax.set_ylabel("Current density (A cm$^{-2}$)")
    ax.set_title("Computed I-V vs homepage Figure 2")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out, dpi=190)
    plt.close(fig)

    rmse = float(np.sqrt(np.mean((current - ref_at_points) ** 2)))
    print(f"Saved {args.out}")
    print(f"Saved {csv_path}")
    print(f"RMSE = {rmse:.3f} A/cm2")


if __name__ == "__main__":
    main()
