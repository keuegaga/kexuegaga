# -*- coding: utf-8 -*-
"""Plot nextnano.NEGF LDOS and current sweeps in the homepage Figure 1/2 style."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
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
DEFAULT_OUT = ROOT / "results/nextnano_home_figures_bai"


def load_dos(bias_dir: Path):
    data = np.loadtxt(
        bias_dir / "2D_plots/data/DensityOfStates_ZoneCenter.ascii"
    )
    positions = np.unique(data[:, 0])
    energies = np.unique(data[:, 1])
    dos = data[:, 2].reshape(len(energies), len(positions))

    band = np.loadtxt(bias_dir / "ConductionBandEdge.dat", skiprows=2)
    band_x, band_e = band[:, 0], band[:, 1]
    return positions, energies, dos, band_x, band_e


def current_density_from_directory(bias_dir: Path) -> float | None:
    """Recover a completed point if a later point interrupted the sweep."""
    path = bias_dir / "Current-miscellaneous.txt"
    if not path.exists():
        return None
    match = re.search(
        r"Current density\s*=\s*([-+0-9.eE]+)",
        path.read_text(encoding="utf-8", errors="ignore"),
    )
    return float(match.group(1)) if match else None


def load_current_rows(run: Path) -> list[tuple[float, float]]:
    rows: dict[float, float] = {}
    summary = run / "Current_vs_Voltage.dat"
    if summary.exists():
        data = np.loadtxt(summary, skiprows=1, ndmin=2)
        rows.update({float(bias): float(current) for bias, current in data})

    for bias_dir in run.glob("*mV"):
        match = re.fullmatch(r"(-?\d+)mV", bias_dir.name)
        if not match:
            continue
        bias = float(match.group(1))
        if bias in rows:
            continue
        current = current_density_from_directory(bias_dir)
        if current is not None:
            rows[bias] = current
    return sorted(rows.items())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        type=Path,
        action="append",
        default=None,
        help=(
            "Run directory. Repeat this option for segmented sweeps. "
            "Defaults to the five Bai reproduction segments."
        ),
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--source",
        default=(
            "MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf "
            "(gain removed for passive I-V)"
        ),
    )
    parser.add_argument("--title", default="Bai APL 2011")
    parser.add_argument(
        "--reference-energy",
        type=float,
        default=1.0,
        help=(
            "Shift every LDOS frame by a common constant so that the minimum "
            "conduction-band edge is placed at this energy (eV)."
        ),
    )
    parser.add_argument(
        "--no-energy-shift",
        action="store_true",
        help="Keep the simulation's native energy reference.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [path.resolve() for path in (args.run or DEFAULT_RUNS)]
    out = args.out.resolve()

    current_rows = np.asarray(
        [row for run in runs for row in load_current_rows(run)],
        dtype=float,
    )
    current_rows = np.unique(current_rows, axis=0)
    bias_values = current_rows[:, 0]
    current_values = current_rows[:, 1]
    bias_dirs = []
    for value in bias_values:
        dirname = f"{int(round(value))}mV"
        candidates = [run / dirname for run in runs]
        existing = [
            path
            for path in candidates
            if (
                path
                / "2D_plots/data/DensityOfStates_ZoneCenter.ascii"
            ).exists()
        ]
        if existing:
            bias_dirs.append(existing[0])
        else:
            bias_dirs.append(candidates[0])
    missing = [path for path in bias_dirs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing bias directories: {missing}")

    frames = [load_dos(path) for path in bias_dirs]
    if args.no_energy_shift:
        energy_shift = 0.0
    else:
        # Use the first sweep point as the reference, matching the homepage
        # figure whose low-bias band edge starts near 1.0 eV.
        native_minimum = float(np.min(frames[0][4]))
        energy_shift = args.reference_energy - native_minimum
    frames = [
        (positions, energies + energy_shift, dos, band_x, band_e + energy_shift)
        for positions, energies, dos, band_x, band_e in frames
    ]
    global_max = max(
        float(np.percentile(np.maximum(frame[2], 0), 99.8))
        for frame in frames
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    norm = Normalize(vmin=0, vmax=global_max)
    fig.colorbar(
        ScalarMappable(norm=norm, cmap="turbo"),
        ax=axes[0],
        label="Density of states (nm$^{-1}$ eV$^{-1}$)",
    )

    def update(index: int):
        axes[0].clear()
        axes[1].clear()
        positions, energies, dos, band_x, band_e = frames[index]
        image = axes[0].pcolormesh(
            positions,
            energies,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm,
        )
        band_mask = (band_x >= positions[0]) & (band_x <= positions[-1])
        axes[0].plot(band_x[band_mask], band_e[band_mask], color="white", lw=1.0)
        axes[0].set_xlim(positions[0], positions[-1])
        axes[0].set_xlabel("Position (nm)")
        axes[0].set_ylabel("Energy (eV)")
        axes[0].set_title(
            f"Local Density of States: {bias_values[index]:.0f} mV/period"
        )

        axes[1].plot(bias_values, current_values, color="#7A1FA2", lw=1.5)
        axes[1].scatter(
            [bias_values[index]],
            [current_values[index]],
            color="black",
            s=120,
            zorder=3,
        )
        axes[1].set_xlim(-10, 505)
        axes[1].set_ylim(
            min(-100, float(np.min(current_values)) - 50),
            max(5000, float(np.max(current_values)) + 300),
        )
        axes[1].set_xlabel("Potential drop per period (mV)")
        axes[1].set_ylabel("Current Density (A cm$^{-2}$)")
        axes[1].set_title(
            f"Current: {current_values[index]:.1f} A cm$^{{-2}}$"
        )
        axes[1].grid(alpha=0.25)
        return []

    out.mkdir(parents=True, exist_ok=True)
    update(0)
    fig.savefig(out / "figure1_figure2_static_0mV.png", dpi=170)

    selected = min(range(len(bias_values)), key=lambda i: abs(bias_values[i] - 300))
    update(selected)
    fig.savefig(out / f"figure1_figure2_static_{int(bias_values[selected])}mV.png", dpi=170)

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(frames),
        interval=500,
        blit=False,
        repeat=True,
    )
    ani.save(out / "nextnano_home_figures_reproduction.gif", writer=animation.PillowWriter(fps=2))
    plt.close(fig)

    # Figure 1 on its own, matching the homepage LDOS animation.
    fig1, ax1 = plt.subplots(figsize=(8.2, 5.6))
    norm1 = Normalize(vmin=0, vmax=global_max)
    fig1.colorbar(
        ScalarMappable(norm=norm1, cmap="turbo"),
        ax=ax1,
        label="Density of states (nm$^{-1}$ eV$^{-1}$)",
    )

    def update_ldos(index: int):
        ax1.clear()
        positions, energies, dos, band_x, band_e = frames[index]
        ax1.pcolormesh(
            positions,
            energies,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm1,
        )
        band_mask = (band_x >= positions[0]) & (band_x <= positions[-1])
        ax1.plot(band_x[band_mask], band_e[band_mask], color="white", lw=1.0)
        ax1.set_xlim(positions[0], positions[-1])
        ax1.set_xlabel("Position (nm)")
        ax1.set_ylabel("Energy (eV)")
        ax1.set_title(
            f"Local density of states, {bias_values[index]:.0f} mV/period"
        )
        return []

    update_ldos(0)
    fig1.tight_layout()
    fig1.savefig(out / "figure1_ldos_0mV.png", dpi=190)
    fig1_ani = animation.FuncAnimation(
        fig1,
        update_ldos,
        frames=len(frames),
        interval=500,
        blit=False,
        repeat=True,
    )
    fig1_ani.save(
        out / "figure1_ldos_vs_bias.gif", writer=animation.PillowWriter(fps=2)
    )
    plt.close(fig1)

    # Figure 2 on its own, with a moving operating point.
    figc, axc = plt.subplots(figsize=(7.2, 5.2))
    axc.plot(bias_values, current_values, color="#7A1FA2", lw=1.5)
    marker = axc.scatter([bias_values[0]], [current_values[0]], color="black", s=120)
    axc.set_xlim(-10, 505)
    axc.set_ylim(
        min(-100, float(np.min(current_values)) - 50),
        max(5000, float(np.max(current_values)) + 300),
    )
    axc.set_xlabel("Potential drop per period (mV)")
    axc.set_ylabel("Current Density (A cm$^{-2}$)")
    axc.set_title("Current-voltage characteristics")
    axc.grid(alpha=0.25)

    def update_current(index: int):
        marker.set_offsets([[bias_values[index], current_values[index]]])
        axc.set_title(
            f"Current-voltage: {bias_values[index]:.0f} mV, "
            f"{current_values[index]:.1f} A cm$^{{-2}}$"
        )
        return [marker]

    figc.tight_layout()
    figc.savefig(out / "figure2_current_voltage_animated_start.png", dpi=190)
    current_ani = animation.FuncAnimation(
        figc,
        update_current,
        frames=len(bias_values),
        interval=500,
        blit=False,
        repeat=True,
    )
    current_ani.save(
        out / "figure2_current_sweep.gif", writer=animation.PillowWriter(fps=2)
    )
    plt.close(figc)

    # Clean standalone current-voltage chart.
    fig2, ax2 = plt.subplots(figsize=(7.2, 5.2))
    ax2.plot(bias_values, current_values, ".-", color="#7A1FA2")
    ax2.set_xlabel("Potential drop per period (mV)")
    ax2.set_ylabel("Current density (A cm$^{-2}$)")
    ax2.set_title("Current Density")
    ax2.grid(alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(out / "figure2_current_voltage.png", dpi=190)
    plt.close(fig2)

    valid = bias_values >= 320
    fig2v, ax2v = plt.subplots(figsize=(7.2, 5.2))
    ax2v.plot(
        bias_values[valid],
        current_values[valid],
        ".-",
        color="#7A1FA2",
    )
    ax2v.set_xlabel("Potential drop per period (mV)")
    ax2v.set_ylabel("Current density (A cm$^{-2}$)")
    ax2v.set_title("Current Density: 320–500 mV")
    ax2v.grid(alpha=0.25)
    fig2v.tight_layout()
    fig2v.savefig(out / "figure2_current_voltage_valid_range.png", dpi=190)
    plt.close(fig2v)

    convergence_text = "not available"
    convergence_parts = []
    for run in runs:
        convergence_path = run / "_ConvergenceFactors.dat"
        if convergence_path.exists():
            convergence_parts.append(np.loadtxt(convergence_path, skiprows=1))
    if convergence_parts:
        convergence = np.vstack(convergence_parts)
        max_green = float(np.max(convergence[:, 1]))
        max_current = float(np.max(convergence[:, 3]))
        convergence_text = (
            f"max Green convergence factor={max_green:.6g}; "
            f"max current convergence factor={max_current:.6g}"
        )

    summary = out / "README.txt"
    summary.write_text(
        "\n".join(
            [
                f"Source example: {args.source}",
                "Run directories:",
                *[f"  {run}" for run in runs],
                "Sweep: 0 to 500 mV/period, Delta=20 mV",
                "Figure1: 2D_plots/data/DensityOfStates_ZoneCenter.ascii",
                "Figure2: Current_vs_Voltage.dat",
                f"Bias points: {len(bias_values)}",
                f"Maximum current: {current_values.max():.6f} A/cm2",
                f"Maximum-current bias: {bias_values[np.argmax(current_values)]:.6f} mV",
                (
                    "LDOS energy shift applied for plotting only: "
                    f"{energy_shift:.6f} eV"
                ),
                f"Convergence: {convergence_text}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
