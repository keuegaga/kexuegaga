# -*- coding: utf-8 -*-
"""Plot Liu 2022 NEGF calibration trends."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
OUT = ROOT / "attachments" / "fig_liu2022_negf_calibration.png"

bias = [220, 240, 260, 295]
current = [7016.7, 8034.4, 8691.9, 9432.6]
temperature = [1118.1, 1192.3, 1301.1, 1466.0]
selfconsistent = [-18.174, -17.203, -18.348, -18.453]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

ax = axes[0]
ax.plot(bias, current, "o-", color="#4c72b0", lw=2, label="电流")
ax.set_xlabel("周期偏压 [mV]")
ax.set_ylabel("电流密度 [A/cm²]", color="#4c72b0")
ax.tick_params(axis="y", labelcolor="#4c72b0")
ax.grid(alpha=0.25)
ax.set_xticks(bias)

ax2 = ax.twinx()
ax2.plot(bias, temperature, "s--", color="#c44e52", lw=2, label="电子温度")
ax2.set_ylabel("有效电子温度 [K]", color="#c44e52")
ax2.tick_params(axis="y", labelcolor="#c44e52")
ax.set_title("高掺杂基准：偏压扫描")

ax = axes[1]
ax.plot(bias, selfconsistent, "o-", color="#dd8452", lw=2,
        label="高掺杂")
ax.scatter([240], [-4.724], s=110, color="#55a868", zorder=4,
           label="低掺杂 7.0e10 cm-2")
ax.scatter([240], [-4.943], s=110, marker="x", color="#8172b2", zorder=4,
           label="低掺杂 + CBO 0.60 eV")
ax.axhline(0, color="k", lw=0.8)
ax.axhline(10, color="#8172b2", ls=":", lw=1.5,
           label="模态增益达到 5 cm-1 所需材料增益")
ax.set_xlim(215, 300)
ax.set_ylim(-21, 12)
ax.set_xticks(bias)
ax.set_xlabel("周期偏压 [mV]")
ax.set_ylabel("155 meV 自洽增益 [cm-1]")
ax.set_title("自洽增益始终为负")
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc="lower right")

fig.suptitle("Liu 2022 DAU NEGF 校准：偏压、掺杂与 CBO")
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT, dpi=180)
print(OUT)
