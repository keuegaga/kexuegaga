# -*- coding: utf-8 -*-
"""Animate NEGF Wannier-Stark populations and gain while voltage is swept."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
RUN = ROOT / "runs/sun2022_mocvd/negf_alloy006_biasscan_140_220"
OUT = ROOT / "attachments/animations/sun2022_population_gain_sweep.gif"


def main() -> None:
    populations = np.loadtxt(RUN / "Populations_Eigenstates.dat", skiprows=1)
    bias = populations[:, 0]
    state_populations = populations[:, 1:15]
    currents = np.loadtxt(RUN / "Current_vs_Voltage.dat", skiprows=1)[:, 1] / 1000
    temperatures = np.loadtxt(RUN / "Effective_Temperature.dat", skiprows=1)[:, 1]

    gain_spectra = []
    for bias_mv in bias:
        gain_spectra.append(
            np.loadtxt(
                RUN / f"{int(bias_mv)}mV/Gain/Gain_SelfConsistent_vs_Energy.dat",
                skiprows=1,
            )
        )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(11, 8),
        gridspec_kw={"height_ratios": [1.25, 1.0]},
    )
    fig.subplots_adjust(hspace=0.38, left=0.09, right=0.97, top=0.92, bottom=0.10)

    def update(frame: int):
        axes[0].clear()
        axes[1].clear()

        pops = state_populations[frame]
        colors = ["#4C78A8"] * 14
        colors[6] = "#E45756"
        colors[7] = "#F2A900"
        axes[0].bar(np.arange(1, 15), pops, color=colors)
        axes[0].set_xlim(0.4, 14.6)
        axes[0].set_ylim(0, max(0.36, 1.1 * state_populations.max()))
        axes[0].set_xlabel("NEGF Wannier–Stark 状态编号")
        axes[0].set_ylabel("归一化电子占据")
        inversion = pops[6] - pops[7]
        axes[0].set_title(
            f"偏压 {bias[frame]:.0f} mV/周期，J={currents[frame]:.2f} kA/cm²，"
            f"Te={temperatures[frame]:.0f} K；S7−S8={inversion:.3f}"
        )
        axes[0].grid(axis="y", alpha=0.25)
        axes[0].text(
            0.99,
            0.95,
            "红色：S7；金色：S8\n该差值仅作占据反转诊断",
            transform=axes[0].transAxes,
            ha="right",
            va="top",
            fontsize=9,
        )

        spectrum = gain_spectra[frame]
        axes[1].plot(spectrum[:, 0], spectrum[:, 1], "o-", color="#16697A", lw=2)
        axes[1].axvline(135.26, color="#333333", ls=":", label="9.17 µm")
        axes[1].axhline(0, color="black", lw=0.7)
        axes[1].set_xlim(118, 157)
        axes[1].set_ylim(-9, 11)
        axes[1].set_xlabel("光子能量 (meV)")
        axes[1].set_ylabel("自洽材料增益 (cm$^{-1}$)")
        axes[1].set_title("该偏压下的自洽增益谱")
        axes[1].grid(alpha=0.25)
        axes[1].legend(loc="upper right", fontsize=8)

        return []

    OUT.parent.mkdir(parents=True, exist_ok=True)
    poster = OUT.with_name("sun2022_population_gain_sweep_poster.png")
    update(2)
    fig.savefig(poster, dpi=160)

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(bias),
        interval=900,
        blit=False,
        repeat=True,
    )
    ani.save(OUT, writer=animation.PillowWriter(fps=1.0))
    plt.close(fig)

    with Image.open(OUT) as image:
        print(f"Saved {OUT}: {image.size[0]}x{image.size[1]}, {image.n_frames} frames")
    print(f"Saved {poster}")


if __name__ == "__main__":
    main()
