# -*- coding: utf-8 -*-
"""Plot material (Fermi golden rule) gain of the 8 um design vs the baseline."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"D:\Codex-Obsidian\QCL-nextnano\attachments\fig_design8um_gain.png"

CASES = [
    (r"runs\fei2021_negf_biasscan\240mV", "基线（Fei 2021 原结构，240 mV）", "tab:gray"),
    (r"runs\fei2021_negf_design8um\240mV", "设计版（有源宽阱 +0.3 nm，240 mV）", "tab:red"),
]


def load(folder):
    g = os.path.join(folder, "Gain")
    f = [x for x in os.listdir(g) if x.startswith("Gain_FermiGoldenRule_vs_Energy")][0]
    return np.loadtxt(os.path.join(g, f), skiprows=1)


fig, ax = plt.subplots(figsize=(10, 5.8))
for folder, label, color in CASES:
    d = load(folder)
    m = (d[:, 0] >= 90) & (d[:, 0] <= 210)
    ax.plot(d[m, 0], d[m, 1], lw=1.8, color=color, label=label)
    i = int(np.argmax(d[m, 1]))
    ax.annotate(f"{d[m][i,1]:+.1f} /cm @ {d[m][i,0]:.0f} meV\n({1240/d[m][i,0]:.2f} um)",
                (d[m][i, 0], d[m][i, 1]), xytext=(6, 8), textcoords="offset points",
                fontsize=9, color=color)
ax.axhline(0, color="k", lw=0.8)
ax.axvline(155, color="tab:blue", ls=":", lw=1.2)
ax.text(155.5, ax.get_ylim()[1] * 0.85, "8.0 µm 目标\n(155 meV)", fontsize=9, color="tab:blue")
ax.set_xlabel("光子能量 [meV]")
ax.set_ylabel("材料增益 [1/cm]")
ax.set_title("8 µm QCL 设计验证：材料增益谱（NEGF，300 K，低掺杂）")
ax.legend(fontsize=9)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT, dpi=170)
print("saved:", OUT)
