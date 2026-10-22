# -*- coding: utf-8 -*-
"""Plot Sun 2022 NEGF self-consistent gains for the two scattering models."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
BASE = ROOT / "runs" / "sun2022_mocvd" / "negf_fgr_216mV" / "216.384mV" / "Gain"
LOW = ROOT / "runs" / "sun2022_mocvd" / "negf_lowscatter_216mV" / "216.384mV" / "Gain"
OUT = ROOT / "attachments" / "fig_sun2022_gain_scattering_calibration.png"


def read(path):
    data = np.loadtxt(path, skiprows=1)
    return data[:, 0], data[:, 1]


be, bg = read(BASE / "Gain_SelfConsistent_vs_Energy.dat")
le, lg = read(LOW / "Gain_SelfConsistent_vs_Energy.dat")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(be, bg, "o-", lw=2, label="初始散射：IFR 0.08 nm，alloy 1.0")
ax.plot(le, lg, "s-", lw=2, label="低散射：IFR 0.04 nm，alloy 0.1")
ax.axhline(0, color="k", lw=0.8)
ax.axvline(137.8, color="#c44e52", ls="--", lw=1.5, label="9 µm = 137.8 meV")
ax.set_xlabel("光子能量 [meV]")
ax.set_ylabel("自洽材料增益 [cm-1]")
ax.set_title("Sun 2022 9 µm 结构：散射参数对自洽增益的影响")
ax.grid(alpha=0.25)
ax.legend(fontsize=8)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=180)
print(OUT)
