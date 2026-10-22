# -*- coding: utf-8 -*-
"""Plot Liu 2022 8 um NEGF FGR and self-consistent gains."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
RUN = ROOT / "runs" / "liu2022_dau_negf" / "fgr_270_final"
GAIN = RUN / "270mV" / "Gain"
OUT = ROOT / "attachments" / "fig_liu2022_dau_gain_fgr_vs_selfconsistent.png"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def read_two_columns(path):
    data = np.loadtxt(path, skiprows=1)
    return data[:, 0], data[:, 1]


fgr_e, fgr_g = read_two_columns(
    GAIN / "Gain_FermiGoldenRule_vs_Energy_[0,0,1].dat"
)
sc_e, sc_g = read_two_columns(GAIN / "Gain_SelfConsistent_vs_Energy.dat")

fig, ax = plt.subplots(figsize=(10, 6))
window = (fgr_e >= 120) & (fgr_e <= 200)
ax.plot(fgr_e[window], fgr_g[window], lw=2.2, label="FGR 材料增益")
ax.plot(sc_e, sc_g, "o-", lw=2.0, label="自洽增益")
ax.axhline(0, color="k", lw=0.8, alpha=0.6)
ax.axvline(155, color="#c44e52", ls="--", lw=1.5, label="8 µm = 155 meV")
ax.axhline(5, color="#8172b2", ls=":", lw=1.6, label="腔损耗 5 cm-1")
ax.set_xlabel("光子能量 [meV]")
ax.set_ylabel("增益 [cm-1]")
ax.set_title("Liu 2022 DAU 8 µm 候选：FGR 与自洽增益（270 mV/周期，300 K）")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=180)
print(OUT)
