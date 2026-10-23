# -*- coding: utf-8 -*-
"""Plot advanced NEGF outputs: dispersion, lifetimes, spectral function, populations."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
SCAN = ROOT / "runs/sun2022_mocvd/negf_alloy006_biasscan_140_220"
THRESHOLD = ROOT / "runs/sun2022_mocvd/negf_alloy006_threshold183_wide/183mV/EnergyEigenstates"
OUT = ROOT / "results/qcl_validation/sun2022_advanced_negf_analysis.png"


def read_indexed(path: Path) -> np.ndarray:
    rows = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                rows.append([float(value) for value in parts[:4]])
    return np.asarray(rows)


def main() -> None:
    dispersion = np.loadtxt(THRESHOLD / "InplaneDispersion.dat", skiprows=2)
    lifetimes = read_indexed(THRESHOLD / "Lifetimes.dat")[:14]
    scattering = read_indexed(THRESHOLD / "ScatteringRate_mechanisms.dat")[:14]
    spectral = np.loadtxt(THRESHOLD / "SpectralFunctions.dat", skiprows=1)
    populations = np.loadtxt(SCAN / "Populations_Eigenstates.dat", skiprows=1)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for state in range(1, 15):
        axes[0, 0].plot(
            dispersion[:, 0],
            dispersion[:, state] * 1e3,
            lw=1.0,
            label=f"S{state}" if state in (1, 7, 8, 14) else None,
        )
    axes[0, 0].set_xlabel("面内波矢 k (nm$^{-1}$)")
    axes[0, 0].set_ylabel("能量 (meV)")
    axes[0, 0].set_title("183 mV：面内色散")
    axes[0, 0].grid(alpha=0.25)
    axes[0, 0].legend(fontsize=8)

    width = 0.27
    x = scattering[:, 0]
    axes[0, 1].bar(x - width, scattering[:, 1], width, label="LO")
    axes[0, 1].bar(x, scattering[:, 2], width, label="IFR")
    axes[0, 1].bar(x + width, scattering[:, 3], width, label="Alloy")
    axes[0, 1].set_xlabel("Wannier–Stark 状态")
    axes[0, 1].set_ylabel("散射率 (ps$^{-1}$)")
    axes[0, 1].set_title("阈值附近散射分解")
    axes[0, 1].grid(axis="y", alpha=0.25)
    rate_axis = axes[0, 1].twinx()
    rate_axis.plot(lifetimes[:, 0], lifetimes[:, 1], "ko-", label="lifetime")
    rate_axis.set_ylabel("寿命 (ps)")
    lines, labels = axes[0, 1].get_legend_handles_labels()
    lines2, labels2 = rate_axis.get_legend_handles_labels()
    axes[0, 1].legend(lines + lines2, labels + labels2, fontsize=8)

    image = axes[1, 0].pcolormesh(
        np.arange(1, 15),
        spectral[:, 0] * 1e3,
        np.log10(np.maximum(spectral[:, 1:15], 1e-20)),
        shading="auto",
        cmap="magma",
    )
    axes[1, 0].set_xlabel("Wannier–Stark 状态")
    axes[1, 0].set_ylabel("能量 (meV)")
    axes[1, 0].set_title("183 mV：谱函数 log10(A)")
    fig.colorbar(image, ax=axes[1, 0], label="log10(eV$^{-1}$)")

    for state in range(1, 15):
        axes[1, 1].plot(
            populations[:, 0],
            populations[:, state],
            "o-",
            lw=1.0,
            label=f"S{state}" if state in (1, 7, 8, 14) else None,
        )
    axes[1, 1].set_xlabel("偏压 (mV/周期)")
    axes[1, 1].set_ylabel("归一化占据")
    axes[1, 1].set_title("变电压下的状态占据")
    axes[1, 1].grid(alpha=0.25)
    axes[1, 1].legend(fontsize=8)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
