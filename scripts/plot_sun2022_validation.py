# -*- coding: utf-8 -*-
"""Plot calibrated-scattering gain and threshold comparison for Sun 2022."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
WIDE = (
    ROOT
    / "runs/sun2022_mocvd/negf_alloy006_wide_216mV/216.384mV/Gain"
    / "Gain_SelfConsistent_vs_Energy.dat"
)
WIDE_THRESHOLD = (
    ROOT
    / "runs/sun2022_mocvd/negf_alloy006_threshold183_wide/183mV/Gain"
    / "Gain_SelfConsistent_vs_Energy.dat"
)
WIDE_160 = (
    ROOT
    / "runs/sun2022_mocvd/negf_alloy006_160mV_wide/160mV/Gain"
    / "Gain_SelfConsistent_vs_Energy.dat"
)
SCAN = ROOT / "runs/sun2022_mocvd/negf_alloy006_biasscan_140_220"
OUT = ROOT / "results/qcl_validation/sun2022_negf_validation.png"
SUMMARY = ROOT / "results/qcl_validation/sun2022_negf_validation.txt"
METHOD_COMPARISON = ROOT / "results/qcl_validation/sun2022_gain_method_comparison.csv"


def read_two_columns(path: Path) -> np.ndarray:
    return np.loadtxt(path, skiprows=1)


def main() -> None:
    wide = read_two_columns(WIDE)
    wide_threshold = read_two_columns(WIDE_THRESHOLD)
    wide_160 = read_two_columns(WIDE_160)
    scan_current = read_two_columns(SCAN / "Current_vs_Voltage.dat")
    bias = scan_current[:, 0]
    current = scan_current[:, 1]

    gain_at_135 = []
    gain_at_window_maximum = []
    for bias_mv in bias:
        spectrum = read_two_columns(
            SCAN / f"{int(bias_mv)}mV/Gain/Gain_SelfConsistent_vs_Energy.dat"
        )
        gain_at_135.append(float(spectrum[np.argmin(abs(spectrum[:, 0] - 135)), 1]))
        gain_at_window_maximum.append(float(spectrum[:, 1].max()))
    gain_at_135 = np.asarray(gain_at_135)
    wide_gain_at_135 = float(np.interp(135.0, wide[:, 0], wide[:, 1]))

    threshold_gain = 2.966167
    threshold_bias = float(
        np.interp(threshold_gain, gain_at_135, bias)
    )
    threshold_current_ka = float(
        np.interp(threshold_gain, gain_at_135, current / 1000.0)
    )
    method_data = np.loadtxt(METHOD_COMPARISON, delimiter=",", skiprows=1)
    fgr_gain = method_data[:, 2]
    threshold_current_ka_fgr = float(
        np.interp(threshold_gain, fgr_gain, current / 1000.0)
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    axes[0].plot(wide_160[:, 0], wide_160[:, 1], "D-.",
                 color="#6A994E", lw=1.6, label="160 mV，约 1.55 kA/cm2")
    axes[0].plot(wide_threshold[:, 0], wide_threshold[:, 1], "^--",
                 color="#7A5195", lw=1.8, label="183 mV，约 2.12 kA/cm2")
    axes[0].plot(wide[:, 0], wide[:, 1], "o-", color="#16697A", lw=2,
                 label="216 mV，约 2.58 kA/cm2")
    axes[0].axhline(threshold_gain, color="#C44536", ls="--",
                    label=f"材料增益阈值 {threshold_gain:.2f} cm-1")
    axes[0].axvline(135.26, color="#333333", ls=":", lw=1.5,
                    label="9.17 um / 135.26 meV")
    axes[0].scatter([135.26], [wide_gain_at_135], color="#C44536", zorder=4)
    axes[0].annotate(
        f"{wide_gain_at_135:.2f} cm-1",
        (135.26, wide_gain_at_135),
        xytext=(8, 18),
        textcoords="offset points",
    )
    axes[0].set_xlabel("光子能量 (meV)")
    axes[0].set_ylabel("自洽材料增益 (cm-1)")
    axes[0].set_title("宽能量窗自洽增益：偏压引起的长波峰蓝移")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)

    axes[1].plot(current / 1000.0, gain_at_135, "s-", color="#16697A", lw=2,
                 label="9.17 um 处自洽增益")
    axes[1].plot(current / 1000.0, fgr_gain, "o--", color="#7A5195", lw=1.8,
                 label="Fermi golden rule 增益")
    axes[1].axhline(threshold_gain, color="#C44536", ls="--",
                    label="波导阈值")
    axes[1].axvline(1.52, color="#6A994E", ls=":", lw=1.6,
                    label="论文 Jth=1.52 kA/cm2")
    axes[1].axvline(threshold_current_ka, color="#333333", ls="-.", lw=1.2,
                    label=f"模型阈值≈{threshold_current_ka:.2f} kA/cm2")
    axes[1].axvline(threshold_current_ka_fgr, color="#7A5195", ls=":", lw=1.2,
                    label=f"FGR 阈值≈{threshold_current_ka_fgr:.2f} kA/cm2")
    low_wave_gain = np.array([wide_160[:, 1].max(), wide_threshold[:, 1].max()])
    low_wave_current_ka = np.array([1.55493, 2.11751])
    low_wave_threshold_ka = float(
        np.interp(threshold_gain, low_wave_gain, low_wave_current_ka)
    )
    axes[1].axvline(low_wave_threshold_ka, color="#6A994E", ls="-", lw=1.3,
                    label=f"长波峰阈值≈{low_wave_threshold_ka:.2f} kA/cm2")
    axes[1].set_xlabel("电流密度 (kA/cm2)")
    axes[1].set_ylabel("自洽材料增益 (cm-1)")
    axes[1].set_title("校准合金散射后的阈值比较")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=190)
    plt.close(fig)

    lines = [
        "calibrated_alloy_strength=0.06",
        "wide_gain_peak_mev=120.0",
        "wide_gain_peak_wavelength_um=10.33",
        "threshold_near_wide_gain_peak_mev=115.0",
        "threshold_near_wide_gain_peak_wavelength_um=10.78",
        f"broad_peak_threshold_current_kA_cm2={low_wave_threshold_ka:.6f}",
        f"gain_at_9p17um_216mV={wide_gain_at_135:.6f}",
        f"material_threshold_gain_cm={threshold_gain:.6f}",
        f"interpolated_threshold_bias_mV={threshold_bias:.3f}",
        f"interpolated_threshold_current_kA_cm2={threshold_current_ka:.6f}",
        f"interpolated_fgr_threshold_current_kA_cm2={threshold_current_ka_fgr:.6f}",
        "paper_threshold_current_kA_cm2=1.52",
    ]
    for bias_value, current_value, gain_value in zip(bias, current, gain_at_135):
        lines.append(
            f"bias_{bias_value:g}mV_current_kA_cm2={current_value / 1000:.6f}"
            f"_gain_9p17um={gain_value:.6f}"
        )
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {OUT}")
    print(f"Saved {SUMMARY}")
    print(f"Interpolated thresholds: self-consistent {threshold_bias:.2f} mV, "
          f"{threshold_current_ka:.3f} kA/cm2; FGR {threshold_current_ka_fgr:.3f} kA/cm2")


if __name__ == "__main__":
    main()
