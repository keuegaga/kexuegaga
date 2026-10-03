# -*- coding: utf-8 -*-
"""Draw a conduction-band-edge schematic for a QCL period.

Wells and barriers are colour-coded and labelled, so the layer stack is
unambiguous without relying on bold text.

Usage:
    python scripts/plot_layer_stack.py

Outputs (into the vault's attachments folder):
    fig_layer_stack_fei2021.png    (Fei 2021, 8.5 um MOCVD design, 57.3 nm period)
    fig_layer_stack_friedrich.png  (Friedrich 2005, no-injector, 22.5 nm period)
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# CJK font so the Chinese layer labels render correctly
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ATT = r"D:\Codex-Obsidian\QCL-nextnano\attachments"

# (material, thickness_nm) alternating starting with a barrier
FEI2021 = [
    ("AlInAs", 4.0), ("InGaAs", 1.3), ("AlInAs", 1.0), ("InGaAs", 5.2),
    ("AlInAs", 0.9), ("InGaAs", 5.1), ("AlInAs", 1.0), ("InGaAs", 4.7),
    ("AlInAs", 1.6), ("InGaAs", 3.6), ("AlInAs", 2.2), ("InGaAs", 2.9),
    ("AlInAs", 1.8), ("InGaAs", 2.7), ("AlInAs", 1.9), ("InGaAs", 2.6),
    ("AlInAs", 2.0), ("InGaAs", 2.4), ("AlInAs", 2.5), ("InGaAs", 2.5),
    ("AlInAs", 3.1), ("InGaAs", 2.3),
]

FRIEDRICH = [
    ("AlInAs", 3.4), ("InGaAs", 4.0), ("AlInAs", 1.3), ("InGaAs", 5.2),
    ("AlInAs", 0.9), ("InGaAs", 2.6), ("AlInAs", 1.9), ("InGaAs", 3.2),
]

WELL_COLOR = "#7fb3d5"      # 蓝 = 阱
BARRIER_COLOR = "#f2c185"   # 橙 = 垒


def draw(layers, cbo, field_kV_cm, title, outfile, label_fontsize=7.5):
    edges = [0.0]
    for _, t in layers:
        edges.append(edges[-1] + t)
    total = edges[-1]

    fig, axes = plt.subplots(2, 1, figsize=(13, 7.2), sharex=True,
                             gridspec_kw={"height_ratios": [1.35, 1.0]})

    for ax, field in zip(axes, (0.0, field_kV_cm)):
        for i, (mat, t) in enumerate(layers):
            x0, x1 = edges[i], edges[i + 1]
            isbar = mat == "AlInAs"
            top = cbo if isbar else 0.0
            # band edge incl. applied field (electrons gain energy along +x)
            slope = -field / 10.0        # kV/cm -> meV/nm
            y0 = top + slope * x0
            y1 = top + slope * x1
            ax.fill_between([x0, x1], [y0, y1], [y0 + 0.62, y1 + 0.62],
                            color=BARRIER_COLOR if isbar else WELL_COLOR,
                            alpha=0.75, lw=0)
            ax.plot([x0, x1], [y0, y1], color="k", lw=1.1)
            ax.text((x0 + x1) / 2, y0 + 0.30,
                    ("垒\n" if isbar else "阱\n") + f"{t:g}",
                    ha="center", va="center", fontsize=label_fontsize,
                    linespacing=0.95)
        ax.set_ylabel("电子能量 (相对阱底) [meV]", fontsize=10)
        ax.set_xlim(-1, total + 1)
        tag = "平带（零电场）" if field == 0 else f"工作电场 {field:g} kV/cm"
        ax.set_title(tag, fontsize=9, loc="right")
        ax.grid(axis="x", alpha=0.25)

    axes[0].legend(handles=[Patch(facecolor=WELL_COLOR, label="阱层 InGaAs (well)"),
                            Patch(facecolor=BARRIER_COLOR, label="垒层 InAlAs (barrier)")],
                   loc="upper left", fontsize=9, framealpha=0.95)
    axes[1].set_xlabel("生长方向位置 x [nm]", fontsize=10)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs(ATT, exist_ok=True)
    path = os.path.join(ATT, outfile)
    fig.savefig(path, dpi=170)
    plt.close(fig)
    print("saved:", path, f"(period {total:.1f} nm)")


if __name__ == "__main__":
    draw(FEI2021, cbo=520, field_kV_cm=50,
         title="Fei 2021 设计（λ≈8.5 µm，晶格匹配 InGaAs/InAlAs/InP）：一个周期 57.3 nm",
         outfile="fig_layer_stack_fei2021.png")
    draw(FRIEDRICH, cbo=690, field_kV_cm=64,
         title="Friedrich 2005 设计（无注入区，应变 InGaAs/AlInAs/InP）：一个周期 22.5 nm",
         outfile="fig_layer_stack_friedrich.png", label_fontsize=8.5)
