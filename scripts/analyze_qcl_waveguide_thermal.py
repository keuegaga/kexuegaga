# -*- coding: utf-8 -*-
"""Slab-waveguide, mirror-loss and first-order thermal screen for the 9 um QCL.

The optical mode is solved with a scalar finite-difference Helmholtz equation.
Material indices and bulk losses are explicitly listed assumptions, not fitted
values.  The output is intended for design screening and for defining the
nextnano/beam-propagation inputs, not as a replacement for a calibrated
vectorial mode solver.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


@dataclass(frozen=True)
class Layer:
    name: str
    thickness_um: float
    index: float
    bulk_loss_cm: float
    conductivity_w_mk: float


def build_layers(
    core_index: float,
    inp_index: float,
    cladding_loss_cm: float,
    core_loss_cm: float,
) -> list[Layer]:
    active_thickness_um = 50 * 0.04508
    return [
        Layer("upper InP cladding", 3.4, inp_index, cladding_loss_cm, 68.0),
        Layer("active core", active_thickness_um, core_index, core_loss_cm, 5.0),
        Layer("lower InP cladding", 3.4, inp_index, cladding_loss_cm, 68.0),
        Layer("InP substrate", 8.0, inp_index, cladding_loss_cm, 68.0),
    ]


def solve_te_mode(layers: list[Layer], wavelength_um: float, points_per_um: int = 40):
    total_um = sum(layer.thickness_um for layer in layers)
    n_grid = int(total_um * points_per_um) + 1
    dz_um = total_um / (n_grid - 1)
    z_um = np.linspace(0.0, total_um, n_grid)
    index_profile = np.empty(n_grid)
    start = 0.0
    boundaries = []
    for layer in layers:
        stop = start + layer.thickness_um
        mask = (z_um >= start) & (z_um <= stop)
        index_profile[mask] = layer.index
        boundaries.append((start, stop, layer))
        start = stop

    k0_um = 2 * np.pi / wavelength_um
    potential = k0_um**2 * index_profile**2
    diagonal = -2.0 / dz_um**2 + potential
    off_diagonal = np.ones(n_grid - 1) / dz_um**2
    operator = np.diag(diagonal) + np.diag(off_diagonal, 1) + np.diag(off_diagonal, -1)

    # Dirichlet boundaries; solve for the fundamental guided mode.
    interior = operator[1:-1, 1:-1]
    values, vectors = np.linalg.eigh(interior)
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    mode_interior = vectors[:, 0]
    mode = np.zeros(n_grid)
    mode[1:-1] = mode_interior
    neff = float(np.sqrt(values[0]) / k0_um)

    intensity = mode**2
    intensity /= np.trapz(intensity, z_um)
    fractions = {}
    bulk_losses = {}
    for start, stop, layer in boundaries:
        mask = (z_um >= start) & (z_um <= stop)
        fractions[layer.name] = float(np.trapz(intensity[mask], z_um[mask]))
        bulk_losses[layer.name] = layer.bulk_loss_cm
    passive_loss_cm = sum(fractions[name] * bulk_losses[name] for name in fractions)
    return z_um, mode, intensity, neff, fractions, passive_loss_cm, boundaries


def mirror_loss(length_cm: float, r_front: float, r_rear: float) -> float:
    return float(np.log(1.0 / (r_front * r_rear)) / (2.0 * length_cm))


def thermal_resistance_area(layers: list[Layer]) -> float:
    return sum(
        layer.thickness_um * 1e-6 / layer.conductivity_w_mk for layer in layers
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/qcl_waveguide_thermal"))
    parser.add_argument("--wavelength-um", type=float, default=9.17)
    parser.add_argument("--core-index", type=float, default=3.46)
    parser.add_argument("--inp-index", type=float, default=3.10)
    parser.add_argument("--core-loss-cm", type=float, default=0.5)
    parser.add_argument("--length-mm", type=float, default=4.0)
    parser.add_argument("--ridge-width-um", type=float, default=10.5)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    print("Vertical slab model at %.3f um" % args.wavelength_um)
    print("n_core=%.3f, n_InP=%.3f, core background loss=%.3f cm^-1"
          % (args.core_index, args.inp_index, args.core_loss_cm))
    print("clad_loss_cm  n_eff  Gamma_core  Gamma_clad  passive_loss_cm^-1")
    loss_cases = [0.1, 0.5, 1.0, 2.0, 5.0]
    results = []
    plot_data = None
    for loss in loss_cases:
        layers = build_layers(args.core_index, args.inp_index, loss, args.core_loss_cm)
        z_um, mode, intensity, neff, fractions, passive, boundaries = solve_te_mode(
            layers, args.wavelength_um
        )
        gamma_core = fractions["active core"]
        gamma_clad = fractions["upper InP cladding"] + fractions["lower InP cladding"]
        results.append((loss, neff, gamma_core, gamma_clad, passive))
        print(f"{loss:11.3f} {neff:7.4f} {gamma_core:12.4f} {gamma_clad:12.4f} {passive:18.4f}")
        if plot_data is None:
            plot_data = (z_um, intensity, boundaries)

    length_cm = args.length_mm * 0.1
    alpha_m = mirror_loss(length_cm, 0.29, 0.95)
    gamma_core = results[2][2]
    passive_case = results[2][4]
    modal_threshold = passive_case + alpha_m
    material_threshold = modal_threshold / gamma_core
    print("\nCavity screen")
    print(f"length = {args.length_mm:g} mm, R_front = 0.29, R_rear = 0.95")
    print(f"mirror loss = {alpha_m:.3f} cm^-1")
    print(f"passive loss at 1.0 cm^-1 cladding loss = {passive_case:.3f} cm^-1")
    print(f"modal threshold gain = {modal_threshold:.3f} cm^-1")
    print(f"active-material threshold gain = {material_threshold:.3f} cm^-1")

    layers_for_thermal = build_layers(args.core_index, args.inp_index, 1.0, args.core_loss_cm)
    area_resistance = thermal_resistance_area(layers_for_thermal)
    device_area = (args.ridge_width_um * 1e-6) * (args.length_mm * 1e-3)
    rth_1d = area_resistance / device_area
    current_density = 1520.0  # A/cm^2, paper threshold
    width_cm = args.ridge_width_um * 1e-4
    area_cm2 = width_cm * (args.length_mm * 0.1)
    current_a = current_density * area_cm2
    voltage = 10.5
    heat_w = voltage * current_a
    # The one-dimensional stack is an upper bound because heat spreads
    # laterally into the cladding/substrate and heat sink.  These factors
    # bracket that spreading rather than adding an arbitrary series resistor.
    spreading_rth = {
        1.00: 1.00 * rth_1d,
        0.50: 0.50 * rth_1d,
        0.25: 0.25 * rth_1d,
        0.10: 0.10 * rth_1d,
    }
    print("\nThermal screen (threshold, first order)")
    print(f"series vertical area resistance = {area_resistance:.3e} m^2 K/W")
    print(f"unsplit 1D ridge Rth (upper bound) = {rth_1d:.2f} K/W")
    print(f"threshold current = {current_a:.3f} A, heat at {voltage:.1f} V = {heat_w:.2f} W")
    for factor, resistance in spreading_rth.items():
        print(f"spreading factor {factor:4.2f}: Rth={resistance:6.2f} K/W, "
              f"DeltaT={resistance * heat_w:6.1f} K")

    z_um, intensity, boundaries = plot_data
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1.7, 1]})
    axes[0].plot(z_um, intensity / intensity.max(), color="#16697A", lw=2)
    for start, stop, layer in boundaries:
        if start > 0:
            axes[0].axvline(start, color="#777777", lw=0.8, ls="--")
        axes[0].text((start + stop) / 2, 1.03, layer.name.replace(" ", "\n"),
                     ha="center", va="bottom", fontsize=8)
    axes[0].set_ylim(0, 1.25)
    axes[0].set_xlabel("纵向位置 z (um)")
    axes[0].set_ylabel("归一化光强")
    axes[0].set_title(f"9.17 um 垂直 TE 模：n_eff={results[2][1]:.4f}, Γ_core={gamma_core:.3f}")
    axes[0].grid(alpha=0.25)

    losses = [row[0] for row in results]
    passive = [row[4] for row in results]
    axes[1].plot(losses, passive, "o-", color="#C44536")
    axes[1].axhline(alpha_m, color="#333333", ls="--", label=f"mirror loss={alpha_m:.2f} /cm")
    axes[1].set_xlabel("InP 包层体损耗 (cm^-1)")
    axes[1].set_ylabel("本征无源损耗 (cm^-1)")
    axes[1].set_title("波导损耗敏感性")
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    fig.tight_layout()
    figure_path = args.output / "sun2022_waveguide_screen.png"
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    metrics_path = args.output / "sun2022_waveguide_thermal.txt"
    metrics_path.write_text(
        "\n".join(
            [
                f"wavelength_um={args.wavelength_um}",
                f"n_core={args.core_index}",
                f"n_InP={args.inp_index}",
                f"n_eff={results[2][1]:.6f}",
                f"gamma_core={gamma_core:.6f}",
                f"mirror_loss_cm={alpha_m:.6f}",
                f"passive_loss_cm={passive_case:.6f}",
                f"modal_threshold_gain_cm={modal_threshold:.6f}",
                f"material_threshold_gain_cm={material_threshold:.6f}",
                f"ideal_vertical_Rth_K_per_W={rth_1d:.6f}",
                f"threshold_current_A={current_a:.6f}",
                f"threshold_heat_W={heat_w:.6f}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved {figure_path}")
    print(f"Saved {metrics_path}")


if __name__ == "__main__":
    main()
