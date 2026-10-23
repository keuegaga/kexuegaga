# -*- coding: utf-8 -*-
"""Analyze nextnano position- and energy-resolved self-consistent gain."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
SOURCE = (
    ROOT
    / "runs/sun2022_mocvd/negf_alloy006_wide_216mV/216.384mV/Gain/data"
    / "Gain_vs_Position_and_Energy_SelfConsistent.ascii"
)
OUT_FIGURE = ROOT / "results/qcl_validation/sun2022_position_resolved_gain.png"
OUT_TEXT = ROOT / "results/qcl_validation/sun2022_position_gain.txt"
PERIOD_NM = 45.08


def local_layer(position_nm: float) -> str:
    x = position_nm % PERIOD_NM
    edges = [
        (0.00, 2.80, "B1"),
        (2.80, 5.80, "W2"),
        (5.80, 7.05, "B3"),
        (7.05, 13.32, "W4"),
        (13.32, 14.32, "B5"),
        (14.32, 19.67, "W6"),
        (19.67, 20.55, "B7"),
        (20.55, 25.40, "W8"),
        (25.40, 26.49, "B9"),
        (26.49, 30.65, "W10"),
        (30.65, 31.87, "B11"),
        (31.87, 35.53, "W12"),
        (35.53, 36.95, "B13"),
        (36.95, 40.10, "W14"),
        (40.10, 41.78, "B15"),
        (41.78, 45.08, "W16"),
    ]
    for start, end, name in edges:
        if start <= x < end:
            return name
    return "?"


def main() -> None:
    data = np.loadtxt(SOURCE)
    positions = np.unique(data[:, 0])
    energies = np.unique(data[:, 1])
    gain = data[:, 2].reshape(len(energies), len(positions))

    fig, ax = plt.subplots(figsize=(15, 6.8))
    vmax = float(np.max(np.abs(gain)))
    image = ax.pcolormesh(
        positions,
        energies,
        gain,
        shading="auto",
        cmap="RdBu_r",
        vmin=-vmax,
        vmax=vmax,
    )
    ax.axhline(120.0, color="#111111", lw=1.2, ls="--", label="10.33 µm")
    ax.axhline(135.26, color="#333333", lw=1.2, ls=":", label="9.17 µm")
    ax.set_xlabel("位置 (nm)")
    ax.set_ylabel("光子能量 (meV)")
    ax.set_title("Sun 2022：位置分辨自洽增益，alloy strength=0.06")
    ax.legend(loc="upper right", fontsize=8)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("增益密度")
    fig.tight_layout()
    OUT_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIGURE, dpi=190)
    plt.close(fig)

    lines = []
    for target in (120.0, 130.0, 135.26, 140.0):
        row = gain[np.argmin(np.abs(energies - target))]
        positive = np.maximum(row, 0)
        centroid = float(np.trapz(positions * positive, positions) / np.trapz(positive, positions))
        peak_index = int(np.argmax(row))
        lines.extend(
            [
                f"energy_meV={target:.3f}",
                f"mean_gain={row.mean():.6f}",
                f"max_gain={row.max():.6f}",
                f"max_position_nm={positions[peak_index]:.4f}",
                f"max_layer={local_layer(positions[peak_index])}",
                f"positive_centroid_nm={centroid:.4f}",
                f"positive_fraction={float(np.mean(row > 0)):.6f}",
            ]
        )
    OUT_TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {OUT_FIGURE}")
    print(f"Saved {OUT_TEXT}")


if __name__ == "__main__":
    main()
