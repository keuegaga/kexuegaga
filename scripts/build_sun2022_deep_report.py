# -*- coding: utf-8 -*-
"""Build the deep Sun2022 validation tables and figures."""

from __future__ import annotations

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
RUN_ROOT = ROOT / "runs/sun2022_mocvd"
OUT = ROOT / "results/sun2022_deep_validation"
BIAS = 216.384
WAVELENGTH_UM = 10.33
MATERIAL_THRESHOLD = 2.248 / 0.7055

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def table_rows(path: Path) -> np.ndarray:
    return np.loadtxt(path, skiprows=1, ndmin=2)


def current_at(run: Path, bias: float = BIAS) -> float:
    path = run / "Current_vs_Voltage.dat"
    if path.exists():
        data = table_rows(path)
        index = int(np.argmin(np.abs(data[:, 0] - bias)))
        return float(data[index, 1])
    path = run / f"{bias:g}mV/Current-miscellaneous.txt"
    if not path.exists():
        raise FileNotFoundError(f"No current output in {run}")
    match = re.search(
        r"Current density\s*=\s*([-+0-9.eE]+)",
        path.read_text(encoding="utf-8", errors="ignore"),
    )
    if not match:
        raise ValueError(f"Cannot parse current from {path}")
    return float(match.group(1))


def li_at(run: Path, bias: float = BIAS) -> dict[str, float]:
    path = run / "L-I-V.dat"
    data = table_rows(path)
    index = int(np.argmin(np.abs(data[:, 1] - bias)))
    return {
        "current": float(data[index, 0]),
        "net_power": float(data[index, 2]),
        "emitted_power": float(data[index, 3]),
        "absorbed_power": float(data[index, 4]),
        "wpe": float(data[index, 5]),
    }


def electron_temperature(run: Path) -> float:
    data = table_rows(run / "Effective_Temperature.dat")
    return float(data[0, 1])


def gain_at(run: Path, energy_mev: float = 120.0) -> float:
    candidates = list(run.glob(f"*mV/Gain/Gain_SelfConsistent_vs_Energy.dat"))
    if not candidates:
        raise FileNotFoundError(f"No gain spectrum in {run}")
    data = table_rows(candidates[0])
    return float(np.interp(energy_mev, data[:, 0], data[:, 1]))


def parse_indexed(path: Path) -> dict[int, list[float]]:
    rows = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                rows[int(parts[0])] = [float(value) for value in parts[1:]]
    return rows


def parse_density_matrix(path: Path) -> np.ndarray:
    rows = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("Psi_"):
                continue
            pairs = re.findall(r"\(([-+0-9.eE]+),([-+0-9.eE]+)\)", line)
            rows.append(
                [complex(float(real), float(imag)) for real, imag in pairs]
            )
    matrix = np.asarray(rows, dtype=complex)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Non-square density matrix: {matrix.shape}")
    return matrix


def save_temperature() -> None:
    points = [
        (293, RUN_ROOT / "sun2022_temperature_293K_rerun"),
        (300, RUN_ROOT / "negf_10p33um_clamp_waveguide_consistent_216p384"),
        (313, RUN_ROOT / "sun2022_temperature_313K_rerun"),
        (333, RUN_ROOT / "sun2022_temperature_333K_rerun"),
        (353, RUN_ROOT / "sun2022_temperature_353K_rerun"),
    ]
    rows = []
    for temperature, run in points:
        li = li_at(run)
        rows.append(
            [
                temperature,
                li["current"],
                li["net_power"],
                li["wpe"],
                electron_temperature(run),
            ]
        )
    rows = np.asarray(rows)
    np.savetxt(
        OUT / "temperature_sweep.csv",
        rows,
        delimiter=",",
        header=(
            "lattice_temperature_K,current_A_cm2,net_internal_power_W_cm3,"
            "internal_WPE,effective_electron_temperature_K"
        ),
        comments="",
    )

    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.8), sharex=True)
    axes[0].plot(rows[:, 0], rows[:, 1] / 1000, "o-", color="#7A1FA2")
    axes[0].set_ylabel("J (kA cm$^{-2}$)")
    axes[0].set_title("Fixed 10.33 µm mode at 216.384 mV: temperature sweep")
    axes[1].semilogy(rows[:, 0], np.maximum(rows[:, 2], 1e-12), "s-", color="#2A9D8F")
    axes[1].set_ylabel("Net internal power (W cm$^{-3}$)")
    axes[2].semilogy(rows[:, 0], np.maximum(rows[:, 3], 1e-12), "^-", color="#E76F51")
    axes[2].set_ylabel("Internal WPE")
    axes[2].set_xlabel("Lattice temperature (K)")
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "temperature_sweep.png", dpi=190)
    plt.close(fig)


def save_mode_competition() -> None:
    modes = [
        ("9.17", 135.26, RUN_ROOT / "sun2022_9p17um_clamp_216p384mV_retry"),
        ("9.92", 125.0, RUN_ROOT / "sun2022_mode_competition_9p92um"),
        ("10.16", 122.0, RUN_ROOT / "sun2022_mode_competition_10p16um"),
        (
            "10.33",
            120.0,
            RUN_ROOT / "negf_10p33um_clamp_waveguide_consistent_216p384",
        ),
        ("10.78", 115.0, RUN_ROOT / "sun2022_mode_competition_10p78um"),
    ]
    rows = []
    labels = []
    powers = []
    wp_e = []
    for label, photon, run in modes:
        li = li_at(run)
        rows.append(
            [
                photon,
                1239.84 / photon,
                li["current"],
                li["net_power"],
                li["wpe"],
            ]
        )
        labels.append(label)
        powers.append(max(li["net_power"], 1.0))
        wp_e.append(max(li["wpe"], 1e-12))
    np.savetxt(
        OUT / "mode_competition.csv",
        np.asarray(rows),
        delimiter=",",
        header=(
            "photon_energy_meV,wavelength_um,current_A_cm2,"
            "net_internal_power_W_cm3,internal_WPE"
        ),
        comments="",
    )

    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.8), sharex=True)
    x = np.arange(len(labels))
    axes[0].bar(x, powers, color="#2A9D8F")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Net internal power (W cm$^{-3}$)")
    axes[0].set_title("Mode competition at 216.384 mV")
    axes[1].bar(x, wp_e, color="#E76F51")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Internal WPE")
    axes[1].set_xticks(x, [f"{label} µm" for label in labels])
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "mode_competition.png", dpi=190)
    plt.close(fig)


def save_coherence_and_sensitivity() -> None:
    baseline = RUN_ROOT / "negf_alloy006_216mV"
    coherence = np.asarray(
        [
            [1, current_at(baseline), gain_at(baseline), electron_temperature(baseline)],
            [2, 6337.09, -12.1082, 2911.64],
            [3, np.nan, np.nan, np.nan],
        ]
    )
    np.savetxt(
        OUT / "coherence_sensitivity.csv",
        coherence,
        delimiter=",",
        header=(
            "coherence_periods,current_A_cm2,gain_at_120meV_per_cm,"
            "effective_electron_temperature_K"
        ),
        comments="",
    )

    cases = [
        ("baseline", RUN_ROOT / "negf_alloy006_216mV"),
        ("well -0.1 nm", RUN_ROOT / "sun2022_sensitivity_well_minus_010"),
        ("well +0.1 nm", RUN_ROOT / "sun2022_sensitivity_well_plus_010"),
        ("barrier -0.1 nm", RUN_ROOT / "sun2022_sensitivity_barrier_minus_010"),
        ("barrier +0.1 nm", RUN_ROOT / "sun2022_sensitivity_barrier_plus_010"),
        ("composition -0.01", RUN_ROOT / "sun2022_sensitivity_composition_minus_001"),
        (
            "composition +0.01",
            RUN_ROOT / "sun2022_sensitivity_composition_plus_001_rerun",
        ),
        ("doping -20%", RUN_ROOT / "sun2022_sensitivity_doping_minus_20pct"),
        ("doping +20%", RUN_ROOT / "sun2022_sensitivity_doping_plus_20pct"),
        ("IFR 0.12 nm", RUN_ROOT / "sun2022_sensitivity_ifr_high_012"),
        ("alloy 0.04", RUN_ROOT / "sun2022_sensitivity_alloy_low_004"),
        ("alloy 0.08", RUN_ROOT / "sun2022_sensitivity_alloy_high_008"),
    ]
    rows = []
    labels = []
    for label, run in cases:
        rows.append([current_at(run) / 1000, gain_at(run)])
        labels.append(label)
    rows = np.asarray(rows)
    with (OUT / "tolerance_sensitivity.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        handle.write("case,current_kA_cm2,gain_at_120meV_per_cm\n")
        for label, row in zip(labels, rows):
            handle.write(
                f'"{label}",{row[0]:.9f},{row[1]:.9f}\n'
            )

    fig, axes = plt.subplots(2, 1, figsize=(10.2, 8.4), sharex=True)
    x = np.arange(len(labels))
    colors = [
        "#2A9D8F" if value >= MATERIAL_THRESHOLD else "#C44E52"
        for value in rows[:, 1]
    ]
    axes[0].bar(x, rows[:, 0], color="#4C78A8")
    axes[0].set_ylabel("J (kA cm$^{-2}$)")
    axes[0].set_title("Single-factor tolerance and scattering sensitivity")
    axes[1].bar(x, rows[:, 1], color=colors)
    axes[1].axhline(
        MATERIAL_THRESHOLD,
        color="black",
        ls="--",
        label=f"threshold {MATERIAL_THRESHOLD:.2f} cm$^{{-1}}$",
    )
    axes[1].axhline(0, color="black", lw=0.7)
    axes[1].set_ylabel("Gain at 120 meV (cm$^{-1}$)")
    axes[1].set_xticks(x, labels, rotation=42, ha="right")
    axes[1].legend(fontsize=8)
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "tolerance_sensitivity.png", dpi=190)
    plt.close(fig)

    valid = np.isfinite(coherence[:, 2])
    figc, axesc = plt.subplots(2, 1, figsize=(7.5, 7.8), sharex=True)
    axesc[0].plot(
        coherence[valid, 0],
        coherence[valid, 1] / 1000,
        "o-",
        color="#4C78A8",
    )
    axesc[0].set_ylabel("J (kA cm$^{-2}$)")
    axesc[0].set_title("Coherence-length sensitivity at 216.384 mV")
    axesc[1].plot(
        coherence[valid, 0],
        coherence[valid, 2],
        "s-",
        color="#2A9D8F",
    )
    axesc[1].axhline(MATERIAL_THRESHOLD, color="#C44E52", ls=":")
    axesc[1].axhline(0, color="black", lw=0.7)
    axesc[1].set_ylabel("Gain at 120 meV (cm$^{-1}$)")
    axesc[1].set_xlabel("Coherence length (periods)")
    axesc[1].set_xticks(coherence[:, 0])
    axesc[1].text(
        3,
        0,
        "failed at\niteration 0",
        ha="center",
        va="center",
        fontsize=9,
        color="#C44E52",
    )
    for axis in axesc:
        axis.grid(alpha=0.25)
    figc.tight_layout()
    figc.savefig(OUT / "coherence_sensitivity.png", dpi=190)
    plt.close(figc)

    (OUT / "coherence_notes.txt").write_text(
        "\n".join(
            [
                "2-period full-output run:",
                "  converged electronically but failed while writing the "
                "gain/L-I output due memory; core values: J=6337.09 A/cm2, "
                "material gain from emitted power=-12.1082 /cm, "
                "modal gain=-8.54234 /cm, optical field approximately zero.",
                "3-period reduced-output run:",
                "  NEGF iteration 0 failed numerically with NaN self-energy "
                "and an invalid LAPACK matrix factorization.",
                "Conclusion: one-period operation should be treated as an "
                "upper-confidence model, not a validated multi-period result.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def save_fine_gain() -> None:
    run = RUN_ROOT / "sun2022_fine_gain_110_130_216p384_2meV"
    path = next(run.glob("216.384mV/Gain/Gain_SelfConsistent_vs_Energy.dat"))
    data = table_rows(path)
    np.savetxt(
        OUT / "fine_gain_110_130.csv",
        data,
        delimiter=",",
        header="photon_energy_meV,gain_per_cm",
        comments="",
    )
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    ax.plot(data[:, 0], data[:, 1], "o-", color="#16697A", ms=3)
    ax.axvline(120.0, color="black", ls="--", label="10.33 µm")
    ax.axhline(MATERIAL_THRESHOLD, color="#C44E52", ls=":", label="material threshold")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xlabel("Photon energy (meV)")
    ax.set_ylabel("Self-consistent material gain (cm$^{-1}$)")
    ax.set_title("Fine gain spectrum at 216.384 mV")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fine_gain_spectrum.png", dpi=190)
    plt.close(fig)


def save_scattering_and_density() -> None:
    eigen_dir = RUN_ROOT / "negf_alloy006_216mV/216.384mV/EnergyEigenstates"
    lifetimes = parse_indexed(eigen_dir / "Lifetimes.dat")
    scattering = parse_indexed(eigen_dir / "ScatteringRate_mechanisms.dat")
    states = np.arange(1, 15)
    lifetime_values = np.asarray([lifetimes[state][0] for state in states])
    rates = np.asarray([scattering[state][:3] for state in states])

    np.savetxt(
        OUT / "scattering_lifetime.csv",
        np.column_stack((states, lifetime_values, rates)),
        delimiter=",",
        header=(
            "state,lifetime_ps,LO_rate_per_ps,IFR_rate_per_ps,"
            "alloy_rate_per_ps"
        ),
        comments="",
    )
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 7.4), sharex=True)
    width = 0.27
    axes[0].bar(states - width, rates[:, 0], width, label="LO")
    axes[0].bar(states, rates[:, 1], width, label="IFR")
    axes[0].bar(states + width, rates[:, 2], width, label="Alloy")
    axes[0].set_ylabel("Scattering rate (ps$^{-1}$)")
    axes[0].set_title("Scattering decomposition at 216.384 mV")
    axes[0].legend(fontsize=8)
    axes[1].plot(states, lifetime_values, "o-", color="#C44E52")
    axes[1].set_ylabel("Lifetime (ps)")
    axes[1].set_xlabel("Wannier–Stark state")
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "scattering_lifetime.png", dpi=190)
    plt.close(fig)

    matrix = parse_density_matrix(eigen_dir / "DensityMatrix.txt")
    local = np.abs(matrix[:14, :14])
    np.fill_diagonal(local, 0)
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    image = ax.imshow(local, origin="lower", cmap="magma")
    ax.set_xlabel("State j")
    ax.set_ylabel("State i")
    ax.set_title("|ρij| in the first period at 216.384 mV")
    fig.colorbar(image, ax=ax, label="|ρij|")
    fig.tight_layout()
    fig.savefig(OUT / "density_matrix_coherence.png", dpi=190)
    plt.close(fig)

    off_diagonal = []
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            if row == column:
                continue
            value = abs(matrix[row, column])
            if value > 1e-10:
                off_diagonal.append((value, row + 1, column + 1))
    off_diagonal.sort(reverse=True)
    (OUT / "density_matrix_top_coherences.txt").write_text(
        "\n".join(
            f"S{i:02d}-S{j:02d}: |rho|={value:.6e}"
            for value, i, j in off_diagonal[:25]
        )
        + "\n",
        encoding="utf-8",
    )

    spectral = np.loadtxt(eigen_dir / "SpectralFunctions.dat", skiprows=1)
    fig, ax = plt.subplots(figsize=(8.3, 5.4))
    image = ax.pcolormesh(
        np.arange(1, 43),
        spectral[:, 0] * 1e3,
        np.log10(np.maximum(spectral[:, 1:43], 1e-20)),
        shading="auto",
        cmap="magma",
    )
    ax.set_xlabel("Wannier–Stark state index")
    ax.set_ylabel("Energy (meV)")
    ax.set_title("Spectral function at 216.384 mV")
    fig.colorbar(image, ax=ax, label="log10 spectral function")
    fig.tight_layout()
    fig.savefig(OUT / "spectral_functions.png", dpi=190)
    plt.close(fig)


def save_ldos_and_occupancy() -> None:
    bias_dir = (
        RUN_ROOT
        / "negf_10p33um_clamp_waveguide_consistent_216p384/216.384mV"
    )
    data_dir = bias_dir / "2D_plots/data"
    band = np.loadtxt(bias_dir / "ConductionBandEdge.dat", skiprows=2)

    def load_map(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        data = np.loadtxt(data_dir / name)
        x = np.unique(data[:, 0])
        energy = np.unique(data[:, 1])
        values = data[:, 2].reshape(len(energy), len(x))
        return x, energy, values

    x, energy, ldos = load_map("DensityOfStates_ZoneCenter.ascii")
    _, _, carrier = load_map("CarrierDensity_ZoneCenter.ascii")
    shift = -float(np.min(band[:, 1]))
    energy = energy + shift
    band_e = band[:, 1] + shift

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.3), sharey=True)
    panel_data = [
        (ldos, "LDOS (nm$^{-1}$ eV$^{-1}$)", "Available states"),
        (carrier, "Carrier density (cm$^{-3}$ eV$^{-1}$)", "Occupied states"),
    ]
    for axis, (values, label, title) in zip(axes, panel_data):
        positive = np.maximum(values, 0)
        image = axis.pcolormesh(
            x,
            energy,
            positive,
            shading="auto",
            cmap="turbo",
            norm=Normalize(
                vmin=0,
                vmax=max(float(np.percentile(positive, 99.7)), 1e-20),
            ),
        )
        mask = (band[:, 0] >= x[0]) & (band[:, 0] <= x[-1])
        axis.plot(band[mask, 0], band_e[mask], color="white", lw=1.0)
        axis.set_xlim(x[0], x[-1])
        axis.set_ylim(-0.02, 0.72)
        axis.set_xlabel("Position (nm)")
        axis.set_title(title)
        fig.colorbar(image, ax=axis, label=label)
    axes[0].set_ylabel("Energy above band minimum (eV)")
    fig.suptitle("10.33 µm fixed mode at 216.384 mV")
    fig.tight_layout()
    fig.savefig(OUT / "ldos_vs_occupancy_216p384mV.png", dpi=190)
    plt.close(fig)


def save_status_table() -> None:
    rows = [
        (
            "temperature",
            "conditional-pass",
            "293-333 K retains MW/cm3-class internal power; "
            "353 K drops to 0.353 MW/cm3",
        ),
        (
            "mode_competition",
            "pass",
            "10.78 um strongest; 10.16/10.33 um nearly equal; 9.17 um fails",
        ),
        (
            "coherence_1_to_2",
            "fail",
            "2-period state becomes high-current, high-Te, negative-gain; "
            "full gain output unavailable",
        ),
        (
            "coherence_3",
            "fail",
            "3-period reduced run fails at iteration 0 with NaN/LAPACK error",
        ),
        (
            "single_factor_tolerance",
            "conditional-pass",
            "all tested one-factor cases retain gain above 3.19 /cm; "
            "not yet a full factorial or correlated-disorder study",
        ),
        (
            "fine_gain",
            "pass",
            "2 meV grid finds maximum at 122 meV = 10.16 um",
        ),
        (
            "scattering_lifetime",
            "warning",
            "upper-manifold lifetimes remain far shorter than the paper values",
        ),
        (
            "density_matrix",
            "warning",
            "off-diagonal coherences reach about 0.008 and cannot be reduced "
            "to a simple two-level rate-equation picture",
        ),
    ]
    with (OUT / "validation_status.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        handle.write("item,status,finding\n")
        for item, status, finding in rows:
            handle.write(f'"{item}","{status}","{finding}"\n')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    save_temperature()
    save_mode_competition()
    save_coherence_and_sensitivity()
    save_fine_gain()
    save_scattering_and_density()
    save_ldos_and_occupancy()
    save_status_table()
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
