# -*- coding: utf-8 -*-
"""Plot Sun 2022 bias-dependent LDOS, I-V, populations, and gain."""

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


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
CORE_RUN = ROOT / "runs/sun2022_mocvd/negf_alloy006_biasscan_140_220"
LOW_RUN = ROOT / "runs/sun2022_mocvd/sun2022_ldos_low_0_120"
LOW_REST_RUN = ROOT / "runs/sun2022_mocvd/sun2022_ldos_low_80_120"
HIGH_RUN = ROOT / "runs/sun2022_mocvd/sun2022_ldos_high_240_260"
DESIGN_RUN = ROOT / "runs/sun2022_mocvd/negf_alloy006_216mV"
CLAMP_RUNS = {
    216.384: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_216p384mV_retry",
    220.0: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_220mV",
    240.0: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_240mV",
}
DEFAULT_RUNS = [LOW_REST_RUN, LOW_RUN, CORE_RUN, HIGH_RUN]
DEFAULT_OUT = ROOT / "results/sun2022_homepage_style"

PERIOD_NM = 45.08
TARGET_MEV = 135.26
MATERIAL_THRESHOLD = 2.97  # 1/cm, from the documented waveguide model

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def load_dos(bias_dir: Path):
    data = np.loadtxt(
        bias_dir / "2D_plots/data/DensityOfStates_ZoneCenter.ascii"
    )
    x = np.unique(data[:, 0])
    energy = np.unique(data[:, 1])
    dos = data[:, 2].reshape(len(energy), len(x))
    band = np.loadtxt(bias_dir / "ConductionBandEdge.dat", skiprows=2)
    return x, energy, dos, band[:, 0], band[:, 1]


def current_from_directory(bias_dir: Path) -> float | None:
    path = bias_dir / "Current-miscellaneous.txt"
    if not path.exists():
        return None
    match = re.search(
        r"Current density\s*=\s*([-+0-9.eE]+)",
        path.read_text(encoding="utf-8", errors="ignore"),
    )
    return float(match.group(1)) if match else None


def load_currents(runs: list[Path]) -> dict[float, float]:
    result: dict[float, float] = {}
    for run in runs:
        summary = run / "Current_vs_Voltage.dat"
        if summary.exists():
            data = np.loadtxt(summary, skiprows=1, ndmin=2)
            result.update(
                {float(bias): float(current) for bias, current in data}
            )
        for bias_dir in run.glob("*mV"):
            try:
                bias = float(bias_dir.name.removesuffix("mV"))
            except ValueError:
                continue
            current = current_from_directory(bias_dir)
            if current is not None:
                result[bias] = current
    return result


def find_bias_dir(bias: float, runs: list[Path]) -> Path | None:
    names = [f"{int(round(bias))}mV"]
    if abs(bias - round(bias)) > 1e-6:
        names.append(f"{bias:.3f}mV")
    for run in runs:
        for name in names:
            candidate = run / name
            if (
                candidate
                / "2D_plots/data/DensityOfStates_ZoneCenter.ascii"
            ).exists():
                return candidate
    return None


def load_population_table(run: Path) -> dict[float, np.ndarray]:
    path = run / "Populations_Eigenstates.dat"
    if not path.exists():
        return {}
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    return {
        float(row[0]): row[1:15]
        for row in data
        if row.shape[0] >= 15
    }


def load_energy_table(run: Path) -> dict[float, np.ndarray]:
    path = run / "Energy_Eigenstates.dat"
    if not path.exists():
        return {}
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    return {
        float(row[0]): row[1:15]
        for row in data
        if row.shape[0] >= 15
    }


def load_gain_spectrum(bias_dir: Path) -> np.ndarray | None:
    path = bias_dir / "Gain/Gain_SelfConsistent_vs_Energy.dat"
    if not path.exists():
        return None
    return np.loadtxt(path, skiprows=1, ndmin=2)


def interpolate_crossing(x: np.ndarray, y: np.ndarray, level: float) -> float:
    shifted = y - level
    crossings = np.where(shifted[:-1] * shifted[1:] <= 0)[0]
    for index in crossings:
        if y[index + 1] == y[index]:
            continue
        fraction = (level - y[index]) / (y[index + 1] - y[index])
        return float(x[index] + fraction * (x[index + 1] - x[index]))
    return float("nan")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    currents = load_currents([*DEFAULT_RUNS, DESIGN_RUN])
    regular_biases = np.arange(0.0, 261.0, 20.0)
    missing = [
        float(bias)
        for bias in regular_biases
        if find_bias_dir(float(bias), DEFAULT_RUNS) is None
    ]
    if missing:
        raise FileNotFoundError(f"Missing Sun2022 bias outputs: {missing}")

    bias_dirs = [find_bias_dir(float(bias), DEFAULT_RUNS) for bias in regular_biases]
    bias_dirs = [path for path in bias_dirs if path is not None]
    frames = [load_dos(path) for path in bias_dirs]

    shifted_frames = []
    minimum_band_edge = []
    for x, energy, dos, band_x, band_e in frames:
        shift = -float(np.min(band_e))
        minimum_band_edge.append(shift)
        shifted_frames.append(
            (x, energy + shift, dos, band_x, band_e + shift)
        )

    global_max = max(
        float(np.percentile(np.maximum(frame[2], 0), 99.7))
        for frame in shifted_frames
    )
    norm = Normalize(vmin=0, vmax=global_max)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(13.2, 5.4),
        gridspec_kw={"width_ratios": [1.8, 1.0]},
    )
    fig.colorbar(
        ScalarMappable(norm=norm, cmap="turbo"),
        ax=axes[0],
        label="LDOS (nm$^{-1}$ eV$^{-1}$)",
    )

    current_biases = np.asarray(sorted(currents), dtype=float)
    current_values = np.asarray(
        [currents[value] for value in current_biases],
        dtype=float,
    )

    def update(index: int):
        axes[0].clear()
        axes[1].clear()
        x, energy, dos, band_x, band_e = shifted_frames[index]
        axes[0].pcolormesh(
            x,
            energy,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm,
        )
        mask = (band_x >= x[0]) & (band_x <= x[-1])
        axes[0].plot(band_x[mask], band_e[mask], color="white", lw=1.0)
        axes[0].set_xlim(x[0], x[-1])
        axes[0].set_ylim(-0.02, 0.90)
        axes[0].set_xlabel("Position (nm)")
        axes[0].set_ylabel("Energy above local band minimum (eV)")
        axes[0].set_title(
            f"Sun 2022 LDOS, {regular_biases[index]:.0f} mV/period "
            f"(total {50 * regular_biases[index] / 1000:.2f} V)"
        )

        axes[1].plot(
            current_biases,
            current_values / 1000,
            color="#7A1FA2",
            lw=1.6,
        )
        axes[1].scatter(
            [regular_biases[index]],
            [currents[float(regular_biases[index])] / 1000],
            color="black",
            s=80,
            zorder=3,
        )
        axes[1].axhline(1.52, color="#C44E52", ls="--", lw=1.2)
        axes[1].text(
            4,
            1.58,
            "paper J$_{th}$ = 1.52 kA/cm²",
            color="#C44E52",
            fontsize=8,
        )
        axes[1].set_xlim(-10, 270)
        axes[1].set_ylim(0, max(4.2, current_values.max() / 1000 + 0.4))
        axes[1].set_xlabel("Potential drop per period (mV)")
        axes[1].set_ylabel("Current density (kA cm$^{-2}$)")
        axes[1].set_title("Current-voltage characteristics")
        axes[1].grid(alpha=0.25)
        return []

    update(0)
    fig.tight_layout()
    fig.savefig(out / "figure1_figure2_static_0mV.png", dpi=180)
    selected = int(np.argmin(np.abs(regular_biases - 200)))
    update(selected)
    fig.savefig(out / "figure1_figure2_static_200mV.png", dpi=180)
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(regular_biases),
        interval=700,
        blit=False,
        repeat=True,
    )
    ani.save(
        out / "sun2022_combined_ldos_current.gif",
        writer=animation.PillowWriter(fps=1.4),
    )
    plt.close(fig)

    fig1, ax1 = plt.subplots(figsize=(8.3, 5.6))
    fig1.colorbar(
        ScalarMappable(norm=norm, cmap="turbo"),
        ax=ax1,
        label="LDOS (nm$^{-1}$ eV$^{-1}$)",
    )

    def update_ldos(index: int):
        ax1.clear()
        x, energy, dos, band_x, band_e = shifted_frames[index]
        ax1.pcolormesh(
            x,
            energy,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm,
        )
        mask = (band_x >= x[0]) & (band_x <= x[-1])
        ax1.plot(band_x[mask], band_e[mask], color="white", lw=1.0)
        ax1.set_xlim(x[0], x[-1])
        ax1.set_ylim(-0.02, 0.90)
        ax1.set_xlabel("Position (nm)")
        ax1.set_ylabel("Energy above local band minimum (eV)")
        ax1.set_title(
            f"Local density of states, {regular_biases[index]:.0f} mV/period"
        )
        return []

    update_ldos(0)
    fig1.tight_layout()
    fig1.savefig(out / "figure1_ldos_0mV.png", dpi=190)
    ldos_ani = animation.FuncAnimation(
        fig1,
        update_ldos,
        frames=len(regular_biases),
        interval=700,
        blit=False,
        repeat=True,
    )
    ldos_ani.save(
        out / "figure1_ldos_vs_bias.gif",
        writer=animation.PillowWriter(fps=1.4),
    )
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(7.4, 5.2))
    mask = np.isfinite(current_biases) & np.isfinite(current_values)
    ax2.plot(
        current_biases[mask],
        current_values[mask] / 1000,
        "o-",
        color="#7A1FA2",
        ms=4,
        lw=1.5,
    )
    ax2.axhline(1.52, color="#C44E52", ls="--", label="Paper J$_{th}$")
    ax2.axvline(216.384, color="#2A9D8F", ls=":", label="48 kV/cm design point")
    ax2.set_xlabel("Potential drop per period (mV)")
    ax2.set_ylabel("Current density (kA cm$^{-2}$)")
    ax2.set_title("Sun 2022 QCL current-voltage characteristics")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    top2 = ax2.secondary_xaxis(
        "top",
        functions=(lambda value: value * 50 / 1000, lambda value: value * 1000 / 50),
    )
    top2.set_xlabel("Voltage across 50 active stages (V)")
    fig2.tight_layout()
    fig2.savefig(out / "figure2_current_voltage.png", dpi=190)
    plt.close(fig2)

    fig2a, ax2a = plt.subplots(figsize=(7.4, 5.2))
    line, = ax2a.plot(
        current_biases[mask],
        current_values[mask] / 1000,
        color="#7A1FA2",
        lw=1.5,
    )
    marker = ax2a.scatter(
        [current_biases[0]],
        [current_values[0] / 1000],
        color="black",
        s=85,
        zorder=3,
    )
    ax2a.set_xlim(-10, 270)
    ax2a.set_ylim(0, max(4.2, current_values.max() / 1000 + 0.4))
    ax2a.set_xlabel("Potential drop per period (mV)")
    ax2a.set_ylabel("Current density (kA cm$^{-2}$)")
    ax2a.grid(alpha=0.25)

    def update_current(index: int):
        bias = regular_biases[index]
        marker.set_offsets([[bias, currents[float(bias)] / 1000]])
        ax2a.set_title(
            f"Current density: {bias:.0f} mV/period, "
            f"J={currents[float(bias)] / 1000:.2f} kA/cm²"
        )
        return [marker]

    current_ani = animation.FuncAnimation(
        fig2a,
        update_current,
        frames=len(regular_biases),
        interval=700,
        blit=False,
        repeat=True,
    )
    current_ani.save(
        out / "figure2_current_sweep.gif",
        writer=animation.PillowWriter(fps=1.4),
    )
    plt.close(fig2a)

    populations_by_bias: dict[float, np.ndarray] = {}
    energies_by_bias: dict[float, np.ndarray] = {}
    for run in DEFAULT_RUNS:
        populations_by_bias.update(load_population_table(run))
        energies_by_bias.update(load_energy_table(run))
    populations_by_bias.update(load_population_table(DESIGN_RUN))
    energies_by_bias.update(load_energy_table(DESIGN_RUN))

    regular = [
        value
        for value in regular_biases
        if float(value) in populations_by_bias and float(value) in energies_by_bias
    ]
    diagnostic_biases = sorted(
        set(regular)
        | (
            {216.384}
            if 216.384 in populations_by_bias and 216.384 in energies_by_bias
            else set()
        )
    )
    p_upper = np.asarray(
        [populations_by_bias[value][5:7].sum() for value in diagnostic_biases]
    )
    p_lower = np.asarray(
        [populations_by_bias[value][7:9].sum() for value in diagnostic_biases]
    )
    inversion = p_upper - p_lower

    fig3, ax3 = plt.subplots(figsize=(8.0, 5.2))
    ax3.plot(diagnostic_biases, p_upper, "o-", label="Upper manifold S6+S7")
    ax3.plot(diagnostic_biases, p_lower, "s-", label="Lower manifold S8+S9")
    ax3.plot(
        diagnostic_biases,
        inversion,
        "^-",
        color="#C44E52",
        label="Inversion",
    )
    ax3.axhline(0, color="black", lw=0.7)
    ax3.axvline(160, color="#888888", ls="--", label="Paper threshold ≈160 mV")
    ax3.axvline(216.384, color="#2A9D8F", ls=":", label="Design field")
    ax3.set_xlabel("Potential drop per period (mV)")
    ax3.set_ylabel("Normalized Wannier–Stark occupation")
    ax3.set_title("Population inversion diagnostic for DAU/MS states")
    ax3.grid(alpha=0.25)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(out / "figure3_population_inversion.png", dpi=190)
    plt.close(fig3)

    state_matrix = np.vstack(
        [populations_by_bias[value] for value in diagnostic_biases]
    )
    fig4, ax4 = plt.subplots(figsize=(8.2, 5.5))
    image = ax4.imshow(
        state_matrix.T,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        cmap="magma",
        extent=[
            diagnostic_biases[0] - 10,
            diagnostic_biases[-1] + 10,
            0.5,
            14.5,
        ],
    )
    ax4.axvline(160, color="#7DE2D1", ls="--", lw=1.0)
    ax4.axvline(216.384, color="#7DE2D1", ls=":", lw=1.0)
    ax4.set_xlabel("Potential drop per period (mV)")
    ax4.set_ylabel("Wannier–Stark state index")
    ax4.set_title("Occupation map of the 14 states in one period")
    fig4.colorbar(image, ax=ax4, label="Normalized occupation")
    fig4.tight_layout()
    fig4.savefig(out / "figure3_population_occupation_map.png", dpi=190)
    plt.close(fig4)

    gain_biases = []
    gain_at_9um = []
    peak_gain = []
    peak_energy = []
    spectra = {}
    gain_candidates = sorted({float(value) for value in regular} | {216.384})
    for bias in gain_candidates:
        if bias < 140:
            continue
        bias_dir = find_bias_dir(float(bias), [*DEFAULT_RUNS, DESIGN_RUN])
        if bias_dir is None:
            continue
        spectrum = load_gain_spectrum(bias_dir)
        if spectrum is None:
            continue
        gain_biases.append(float(bias))
        spectra[float(bias)] = spectrum
        gain_at_9um.append(float(np.interp(TARGET_MEV, spectrum[:, 0], spectrum[:, 1])))
        peak_index = int(np.argmax(spectrum[:, 1]))
        peak_gain.append(float(spectrum[peak_index, 1]))
        peak_energy.append(float(spectrum[peak_index, 0]))

    gain_biases = np.asarray(gain_biases)
    gain_at_9um = np.asarray(gain_at_9um)
    peak_gain = np.asarray(peak_gain)
    peak_energy = np.asarray(peak_energy)

    threshold_bias = interpolate_crossing(gain_biases, gain_at_9um, MATERIAL_THRESHOLD)
    broad_threshold_bias = interpolate_crossing(gain_biases, peak_gain, MATERIAL_THRESHOLD)
    all_biases = np.asarray(sorted(currents), dtype=float)
    all_current = np.asarray([currents[value] for value in all_biases])
    threshold_current = (
        float(np.interp(threshold_bias, all_biases, all_current)) / 1000
        if np.isfinite(threshold_bias)
        else float("nan")
    )
    broad_threshold_current = (
        float(np.interp(broad_threshold_bias, all_biases, all_current)) / 1000
        if np.isfinite(broad_threshold_bias)
        else float("nan")
    )

    fig5, ax5 = plt.subplots(figsize=(8.2, 5.3))
    ax5.plot(gain_biases, gain_at_9um, "o-", color="#16697A", label="Gain at 135.26 meV")
    ax5.plot(gain_biases, peak_gain, "s--", color="#7A1FA2", label="Maximum gain")
    ax5.axhline(
        MATERIAL_THRESHOLD,
        color="#C44E52",
        ls=":",
        label=f"Material threshold {MATERIAL_THRESHOLD:.2f} cm$^{{-1}}$",
    )
    ax5.axhline(0, color="black", lw=0.7)
    ax5.axvline(
        threshold_bias,
        color="#2A9D8F",
        ls="-.",
        lw=1.0,
        label="9-µm threshold estimate",
    )
    ax5.set_xlabel("Potential drop per period (mV)")
    ax5.set_ylabel("Material gain (cm$^{-1}$)")
    ax5.set_title("Gain evolution and predicted threshold")
    ax5.grid(alpha=0.25)
    ax5.legend(fontsize=8)
    ax5b = ax5.twinx()
    ax5b.plot(
        gain_biases,
        1239.84 / peak_energy,
        "^:",
        color="#E76F51",
        alpha=0.8,
        label="Wavelength at peak",
    )
    ax5b.set_ylabel("Wavelength at peak gain (µm)")
    lines1, labels1 = ax5.get_legend_handles_labels()
    lines2, labels2 = ax5b.get_legend_handles_labels()
    ax5.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")
    fig5.tight_layout()
    fig5.savefig(out / "figure4_gain_vs_bias.png", dpi=190)
    plt.close(fig5)

    energies = np.unique(
        np.concatenate([spectrum[:, 0] for spectrum in spectra.values()])
    )
    gain_map = np.full((len(energies), len(gain_biases)), np.nan)
    for column, bias in enumerate(gain_biases):
        spectrum = spectra[float(bias)]
        gain_map[:, column] = np.interp(
            energies,
            spectrum[:, 0],
            spectrum[:, 1],
        )
    fig6, ax6 = plt.subplots(figsize=(8.2, 5.5))
    image6 = ax6.pcolormesh(
        gain_biases,
        energies,
        gain_map,
        shading="auto",
        cmap="coolwarm",
        vmin=-8,
        vmax=10,
    )
    ax6.axhline(TARGET_MEV, color="black", ls="--", lw=1.0)
    ax6.axvline(threshold_bias, color="#2A9D8F", ls="-.", lw=1.0)
    ax6.set_xlabel("Potential drop per period (mV)")
    ax6.set_ylabel("Photon energy (meV)")
    ax6.set_title("Self-consistent gain spectrum versus bias")
    fig6.colorbar(image6, ax=ax6, label="Gain (cm$^{-1}$)")
    fig6.tight_layout()
    fig6.savefig(out / "figure5_gain_heatmap.png", dpi=190)
    plt.close(fig6)

    fig7, process_axes = plt.subplots(
        3,
        1,
        figsize=(8.4, 9.0),
        sharex=True,
    )
    regular_current = (
        np.asarray([currents[value] for value in diagnostic_biases]) / 1000
    )
    process_axes[0].plot(
        diagnostic_biases,
        regular_current,
        "o-",
        color="#7A1FA2",
    )
    process_axes[0].axhline(1.52, color="#C44E52", ls="--", label="Paper Jth")
    process_axes[0].axvline(
        threshold_bias,
        color="#2A9D8F",
        ls="-.",
        label="Model 9-µm threshold",
    )
    process_axes[0].set_ylabel("J (kA cm$^{-2}$)")
    process_axes[0].legend(fontsize=8)

    process_axes[1].plot(
        diagnostic_biases,
        inversion,
        "^-",
        color="#C44E52",
    )
    process_axes[1].axhline(0, color="black", lw=0.7)
    process_axes[1].set_ylabel("P$_{S6+S7}$ − P$_{S8+S9}$")

    process_axes[2].plot(
        gain_biases,
        gain_at_9um,
        "o-",
        color="#16697A",
        label="gain @ 9.17 µm",
    )
    process_axes[2].axhline(
        MATERIAL_THRESHOLD,
        color="#C44E52",
        ls=":",
        label="material threshold",
    )
    process_axes[2].set_ylabel("Gain (cm$^{-1}$)")
    process_axes[2].set_xlabel("Potential drop per period (mV)")
    process_axes[2].legend(fontsize=8)
    for axis in process_axes:
        axis.axvline(160, color="#888888", ls="--", alpha=0.7)
        axis.axvline(216.384, color="#2A9D8F", ls=":", alpha=0.8)
        axis.grid(alpha=0.25)
    process_axes[0].set_title("Sun 2022: current → inversion → gain")
    fig7.tight_layout()
    fig7.savefig(out / "figure6_lasing_process.png", dpi=190)
    plt.close(fig7)

    clamp_rows = []
    for bias, run in CLAMP_RUNS.items():
        li_path = run / "L-I-V.dat"
        if not li_path.exists():
            continue
        row = np.loadtxt(li_path, skiprows=1, ndmin=2)[0]
        clamp_rows.append(
            [
                bias,
                50 * bias / 1000,
                row[0],
                row[2],
                row[3],
                row[4],
                row[5],
            ]
        )
    clamp_rows.sort(key=lambda row: row[0])
    if clamp_rows:
        clamp = np.asarray(clamp_rows)
        np.savetxt(
            out / "fixed_mode_li.csv",
            clamp,
            delimiter=",",
            header=(
                "bias_mV,total_voltage_V,current_A_cm2,"
                "net_internal_power_W_cm3,total_emitted_W_cm3,"
                "total_absorbed_W_cm3,internal_WPE"
            ),
            comments="",
        )
        fig8, ax8 = plt.subplots(figsize=(7.6, 5.3))
        ax8.plot(clamp[:, 2] / 1000, clamp[:, 3] / 1e3, "o-", color="#7A1FA2")
        ax8.set_xlabel("Current density (kA cm$^{-2}$)")
        ax8.set_ylabel("Net internal optical power (kW cm$^{-3}$)")
        ax8.set_title("Fixed 9.17 µm optical mode: threshold transition")
        ax8.grid(alpha=0.25)
        for row in clamp:
            ax8.annotate(
                f"{row[0]:g} mV",
                (row[2] / 1000, row[3] / 1e3),
                xytext=(4, 5),
                textcoords="offset points",
                fontsize=8,
            )
        ax8b = ax8.twinx()
        ax8b.plot(
            clamp[:, 2] / 1000,
            clamp[:, 6],
            "s--",
            color="#E76F51",
        )
        ax8b.set_ylabel("Internal wall-plug efficiency")
        fig8.tight_layout()
        fig8.savefig(out / "figure7_fixed_mode_lasing.png", dpi=190)
        plt.close(fig8)

    summary_path = out / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(
            "bias_mV_per_period,total_active_voltage_V,current_A_cm2,"
            "upper_population,lower_population,inversion\n"
        )
        for bias in diagnostic_biases:
            index = list(diagnostic_biases).index(bias)
            handle.write(
                f"{bias:.6f},{50 * bias / 1000:.6f},"
                f"{currents[bias]:.6f},{p_upper[index]:.9f},"
                f"{p_lower[index]:.9f},{inversion[index]:.9f}\n"
            )

    report = out / "README.txt"
    report.write_text(
        "\n".join(
            [
                "Sun et al., Opt. Express 30, 37272 (2022), DOI 10.1364/OE.469573",
                f"Bias grid: 0-260 mV/period, step 20 mV "
                f"({len(regular)} regular points)",
                "One additional exact design point: 216.384 mV/period",
                f"Design field: 48 kV/cm = 216.384 mV/period",
                f"Target transition: {TARGET_MEV:.2f} meV = 9.17 um",
                "Upper-state diagnostic: S6+S7; lower-state diagnostic: S8+S9",
                f"Material gain threshold used: {MATERIAL_THRESHOLD:.3f} /cm",
                f"Predicted 9-um threshold: {threshold_bias:.3f} mV/period, "
                f"{threshold_current:.3f} kA/cm2",
                f"Predicted broad-peak threshold: {broad_threshold_bias:.3f} mV/period, "
                f"{broad_threshold_current:.3f} kA/cm2",
                "Fixed-mode clamp points: 216.384, 220, 240 mV/period",
                "Population manifold is an energy/dipole-based diagnostic, "
                "not a literal paper E3/E4 label assignment.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Saved {out}")
    print(f"9-um threshold estimate: {threshold_bias:.3f} mV, "
          f"{threshold_current:.3f} kA/cm2")


if __name__ == "__main__":
    main()
