# -*- coding: utf-8 -*-
"""Plot and compare the fixed 10.33-um Sun2022 mode with the 9.17-um round."""

from __future__ import annotations

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
RUN_10 = ROOT / "runs/sun2022_mocvd/negf_10p33um_clamp_160_240"
EXACT_10 = ROOT / "runs/sun2022_mocvd/negf_10p33um_clamp_216p384"
CONSISTENT_10 = (
    ROOT / "runs/sun2022_mocvd/negf_10p33um_clamp_waveguide_consistent_216p384"
)
RUNS_9 = {
    216.384: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_216p384mV_retry",
    220.0: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_220mV",
    240.0: ROOT / "runs/sun2022_mocvd/sun2022_9p17um_clamp_240mV",
}
BASELINE_SUMMARY = (
    ROOT / "results/sun2022_homepage_style/summary.csv"
)
OUT = ROOT / "results/sun2022_10p33um_design"

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


def current_from_misc(bias_dir: Path) -> float | None:
    path = bias_dir / "Current-miscellaneous.txt"
    if not path.exists():
        return None
    match = re.search(
        r"Current density\s*=\s*([-+0-9.eE]+)",
        path.read_text(encoding="utf-8", errors="ignore"),
    )
    return float(match.group(1)) if match else None


def load_li_table(run: Path) -> dict[float, dict[str, float]]:
    li = run / "L-I-V.dat"
    if not li.exists():
        return {}
    rows = np.loadtxt(li, skiprows=1, ndmin=2)
    return {
        float(row[1]): {
            "current": float(row[0]),
            "bias": float(row[1]),
            "net_power": float(row[2]),
            "emitted_power": float(row[3]),
            "absorbed_power": float(row[4]),
            "wpe": float(row[5]),
        }
        for row in rows
        if row.shape[0] >= 6
    }


def load_populations(run: Path) -> dict[float, np.ndarray]:
    path = run / "Populations_Eigenstates.dat"
    if path.exists():
        data = np.loadtxt(path, skiprows=1, ndmin=2)
        return {
            float(row[0]): row[1:15]
            for row in data
            if row.shape[0] >= 15
        }
    result = {}
    for bias_dir in run.glob("*mV"):
        try:
            bias = float(bias_dir.name.removesuffix("mV"))
        except ValueError:
            continue
        path = bias_dir / "EnergyEigenstates/Populations.txt"
        if not path.exists():
            continue
        values = []
        with path.open(encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    values.append(float(parts[1]))
        if len(values) >= 14:
            result[bias] = np.asarray(values[:14])
    return result


def inversion_from_populations(pop: np.ndarray) -> float:
    return float(pop[5:7].sum() - pop[7:9].sum())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    regular_biases = np.arange(160.0, 241.0, 20.0)
    bias_dirs = [RUN_10 / f"{int(bias)}mV" for bias in regular_biases]
    missing = [
        path for path in bias_dirs if not (
            path / "2D_plots/data/DensityOfStates_ZoneCenter.ascii"
        ).exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing fixed-mode outputs: {missing}")

    frames = [load_dos(path) for path in bias_dirs]
    shifted = []
    for x, energy, dos, band_x, band_e in frames:
        shift = -float(np.min(band_e))
        shifted.append((x, energy + shift, dos, band_x, band_e + shift))
    norm = Normalize(
        vmin=0,
        vmax=max(
            float(np.percentile(np.maximum(frame[2], 0), 99.7))
            for frame in shifted
        ),
    )

    fig, ax = plt.subplots(figsize=(8.3, 5.6))
    fig.colorbar(
        ScalarMappable(norm=norm, cmap="turbo"),
        ax=ax,
        label="LDOS (nm$^{-1}$ eV$^{-1}$)",
    )

    def update(index: int):
        ax.clear()
        x, energy, dos, band_x, band_e = shifted[index]
        ax.pcolormesh(
            x,
            energy,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm,
        )
        mask = (band_x >= x[0]) & (band_x <= x[-1])
        ax.plot(band_x[mask], band_e[mask], color="white", lw=1.0)
        ax.set_xlim(x[0], x[-1])
        ax.set_ylim(-0.02, 0.72)
        ax.set_xlabel("Position (nm)")
        ax.set_ylabel("Energy above local band minimum (eV)")
        ax.set_title(
            f"10.33 µm mode: LDOS at {regular_biases[index]:.0f} mV/period"
        )
        return []

    update(0)
    fig.tight_layout()
    fig.savefig(OUT / "figure1_ldos_160mV.png", dpi=190)
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(regular_biases),
        interval=900,
        blit=False,
        repeat=True,
    )
    ani.save(
        OUT / "figure1_ldos_vs_bias_10p33um.gif",
        writer=animation.PillowWriter(fps=1.1),
    )
    plt.close(fig)

    exact_dir = EXACT_10 / "216.384mV"
    if exact_dir.exists():
        x, energy, dos, band_x, band_e = load_dos(exact_dir)
        shift = -float(np.min(band_e))
        fig_exact, ax_exact = plt.subplots(figsize=(8.3, 5.6))
        image = ax_exact.pcolormesh(
            x,
            energy + shift,
            dos,
            shading="auto",
            cmap="turbo",
            norm=norm,
        )
        mask = (band_x >= x[0]) & (band_x <= x[-1])
        ax_exact.plot(
            band_x[mask],
            band_e[mask] + shift,
            color="white",
            lw=1.0,
        )
        ax_exact.set_xlim(x[0], x[-1])
        ax_exact.set_ylim(-0.02, 0.72)
        ax_exact.set_xlabel("Position (nm)")
        ax_exact.set_ylabel("Energy above local band minimum (eV)")
        ax_exact.set_title("10.33 µm mode: LDOS at 216.384 mV/period")
        fig_exact.colorbar(
            image,
            ax=ax_exact,
            label="LDOS (nm$^{-1}$ eV$^{-1}$)",
        )
        fig_exact.tight_layout()
        fig_exact.savefig(OUT / "figure1_ldos_216p384mV.png", dpi=190)
        plt.close(fig_exact)

    baseline = np.genfromtxt(
        BASELINE_SUMMARY,
        delimiter=",",
        names=True,
    )
    current_10 = []
    for bias in regular_biases:
        value = current_from_misc(RUN_10 / f"{int(bias)}mV")
        if value is None:
            raise FileNotFoundError(f"Missing current for {bias:g} mV")
        current_10.append(value)
    current_10 = np.asarray(current_10)

    exact_current = current_from_misc(EXACT_10 / "216.384mV")
    plot_bias_10 = regular_biases
    plot_current_10 = current_10
    if exact_current is not None:
        plot_bias_10 = np.sort(np.append(regular_biases, 216.384))
        plot_current_10 = np.interp(plot_bias_10, regular_biases, current_10)
        nearest = np.where(np.isclose(plot_bias_10, 216.384))[0][0]
        plot_current_10[nearest] = exact_current

    np.savetxt(
        OUT / "current_voltage_10p33um.csv",
        np.column_stack(
            (plot_bias_10, 50 * plot_bias_10 / 1000, plot_current_10)
        ),
        delimiter=",",
        header="bias_mV,total_voltage_V,current_A_cm2",
        comments="",
    )

    fig2, ax2 = plt.subplots(figsize=(7.6, 5.3))
    ax2.plot(
        baseline["bias_mV_per_period"],
        baseline["current_A_cm2"] / 1000,
        "o--",
        color="#777777",
        label="No optical field",
    )
    ax2.plot(
        plot_bias_10,
        plot_current_10 / 1000,
        "o-",
        color="#16697A",
        lw=1.7,
        label="Fixed 10.33 µm mode",
    )
    ax2.axhline(1.52, color="#C44E52", ls=":", label="Paper Jth")
    ax2.set_xlim(150, 250)
    ax2.set_xlabel("Potential drop per period (mV)")
    ax2.set_ylabel("Current density (kA cm$^{-2}$)")
    ax2.set_title("Sun 2022 I–V under the 10.33 µm design mode")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    top2 = ax2.secondary_xaxis(
        "top",
        functions=(lambda value: value * 50 / 1000, lambda value: value * 1000 / 50),
    )
    top2.set_xlabel("Voltage across 50 active stages (V)")
    fig2.tight_layout()
    fig2.savefig(OUT / "figure2_current_voltage_10p33um.png", dpi=190)
    plt.close(fig2)

    li_10 = load_li_table(RUN_10)
    li_10.update(load_li_table(EXACT_10))
    li10_bias = np.asarray(sorted(li_10), dtype=float)
    np.savetxt(
        OUT / "fixed_mode_10p33um_li.csv",
        np.asarray(
            [
                [
                    bias,
                    50 * bias / 1000,
                    li_10[bias]["current"],
                    li_10[bias]["net_power"],
                    li_10[bias]["emitted_power"],
                    li_10[bias]["absorbed_power"],
                    li_10[bias]["wpe"],
                ]
                for bias in li10_bias
            ]
        ),
        delimiter=",",
        header=(
            "bias_mV,total_voltage_V,current_A_cm2,"
            "net_internal_power_W_cm3,total_emitted_W_cm3,"
            "total_absorbed_W_cm3,internal_WPE"
        ),
        comments="",
    )

    pop_10 = load_populations(RUN_10)
    pop_10.update(load_populations(EXACT_10))
    pop_9 = {}
    for run in RUNS_9.values():
        pop_9.update(load_populations(run))

    common = sorted(set(RUNS_9) & set(pop_10) & set(pop_9))
    p9_current = []
    p10_current = []
    p9_inversion = []
    p10_inversion = []
    p9_power = []
    p10_power = []
    p9_wpe = []
    p10_wpe = []
    for bias in common:
        li9 = load_li_table(RUNS_9[bias]).get(bias)
        li10 = li_10.get(bias)
        if li9 is None or li10 is None:
            continue
        p9_current.append(li9["current"])
        p10_current.append(li10["current"])
        p9_inversion.append(inversion_from_populations(pop_9[bias]))
        p10_inversion.append(inversion_from_populations(pop_10[bias]))
        p9_power.append(max(li9["net_power"], 1.0))
        p10_power.append(max(li10["net_power"], 1.0))
        p9_wpe.append(max(li9["wpe"], 1e-12))
        p10_wpe.append(max(li10["wpe"], 1e-12))

    fig3, axes3 = plt.subplots(2, 1, figsize=(8.1, 8.2), sharex=True)
    axes3[0].plot(common, p9_inversion, "o-", label="9.17 µm clamp")
    axes3[0].plot(common, p10_inversion, "s-", label="10.33 µm clamp")
    axes3[0].set_ylabel("P$_{S6+S7}$ − P$_{S8+S9}$")
    axes3[0].set_title("Population inversion comparison")
    axes3[0].grid(alpha=0.25)
    axes3[0].legend(fontsize=8)

    axes3[1].semilogy(common, p9_power, "o-", label="9.17 µm")
    axes3[1].semilogy(common, p10_power, "s-", label="10.33 µm")
    axes3[1].set_xlabel("Potential drop per period (mV)")
    axes3[1].set_ylabel("Net internal power (W cm$^{-3}$)")
    axes3[1].set_title("Fixed-mode output comparison")
    axes3[1].grid(alpha=0.25)
    axes3[1].legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "figure3_round_comparison.png", dpi=190)
    plt.close(fig3)

    consistent_li = load_li_table(CONSISTENT_10).get(216.384)
    if consistent_li is not None:
        corrected_rows = [
            [
                216.384,
                50 * 216.384 / 1000,
                120.0,
                10.33,
                3.2768,
                0.7055,
                2.248,
                consistent_li["current"],
                consistent_li["net_power"],
                consistent_li["wpe"],
            ]
        ]
        np.savetxt(
            OUT / "waveguide_consistent_216p384.csv",
            np.asarray(corrected_rows),
            delimiter=",",
            header=(
                "bias_mV,total_voltage_V,photon_energy_meV,wavelength_um,"
                "n_eff,overlap,modal_loss_per_cm,current_A_cm2,"
                "net_internal_power_W_cm3,internal_WPE"
            ),
            comments="",
        )
        labels = ["9.17 µm\napprox. WG", "10.33 µm\napprox. WG", "10.33 µm\nconsistent WG"]
        powers = [
            li_10[216.384]["net_power"] if 216.384 in li_10 else np.nan,
            li_10[216.384]["net_power"] if 216.384 in li_10 else np.nan,
            consistent_li["net_power"],
        ]
        if 216.384 in RUNS_9:
            li9_exact = load_li_table(RUNS_9[216.384]).get(216.384)
            if li9_exact is not None:
                powers[0] = li9_exact["net_power"]
        if 216.384 in li_10:
            powers[1] = li_10[216.384]["net_power"]
        fig4, ax4 = plt.subplots(figsize=(7.3, 5.1))
        bars = ax4.bar(labels, powers, color=["#7A1FA2", "#E76F51", "#2A9D8F"])
        ax4.set_yscale("log")
        ax4.set_ylabel("Net internal optical power (W cm$^{-3}$)")
        ax4.set_title("Waveguide-parameter robustness at 216.384 mV")
        ax4.grid(axis="y", alpha=0.25)
        for bar, value in zip(bars, powers):
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                value * 1.15,
                f"{value:.3g}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        fig4.tight_layout()
        fig4.savefig(OUT / "figure4_waveguide_robustness.png", dpi=190)
        plt.close(fig4)

    comparison = np.column_stack(
        (
            common,
            np.asarray(p9_current) / 1000,
            np.asarray(p10_current) / 1000,
            np.asarray(p9_inversion),
            np.asarray(p10_inversion),
            np.asarray(p9_power),
            np.asarray(p10_power),
            np.asarray(p9_wpe),
            np.asarray(p10_wpe),
        )
    )
    np.savetxt(
        OUT / "round_comparison.csv",
        comparison,
        delimiter=",",
        header=(
            "bias_mV,J_9p17_mode_kA_cm2,J_10p33_mode_kA_cm2,"
            "inversion_9p17,inversion_10p33,"
            "internal_power_9p17_W_cm3,internal_power_10p33_W_cm3,"
            "internal_WPE_9p17,internal_WPE_10p33"
        ),
        comments="",
    )

    design_input = ROOT / "designs/sun2022_mocvd_9um_10p33um_clamp_160_240mV.negf"
    (OUT / "README.txt").write_text(
        "\n".join(
            [
                "Sun et al., Opt. Express 30, 37272 (2022)",
                "Round 2: fixed 10.33-um (120 meV) optical mode.",
                f"Input: {design_input}",
                f"Output root: {RUN_10}",
                f"Exact 216.384 mV output: {EXACT_10}",
                "No optical field baseline: results/sun2022_homepage_style",
                "9.17-um clamp outputs: sun2022_9p17um_clamp_*",
                "The no-field LDOS/I-V are independent of mode label; "
                "this round uses actual fixed-mode photon-assisted transport.",
                f"Waveguide-consistent 216.384 mV check: {CONSISTENT_10}",
                "Data: current_voltage_10p33um.csv; "
                "fixed_mode_10p33um_li.csv; round_comparison.csv",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
