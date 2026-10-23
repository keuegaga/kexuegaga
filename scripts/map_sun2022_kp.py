# -*- coding: utf-8 -*-
"""Map the Sun-2022 k.p states to the paper's E1...E5 ladder."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


LAYERS = [
    (0.00, 2.80, "B1"),
    (2.80, 5.80, "W2"),
    (5.80, 7.05, "B3"),
    (7.05, 13.32, "W4"),
    (13.32, 14.32, "B5"),
    (14.32, 19.67, "W6"),
    (19.67, 20.55, "B7"),
    (20.55, 25.40, "W8"),
    (25.40, 26.49, "B9"),
    (26.49, 30.65, "W10"),
    (30.65, 31.87, "B11"),
    (31.87, 35.53, "W12"),
    (35.53, 36.95, "B13"),
    (36.95, 40.10, "W14"),
    (40.10, 41.78, "B15"),
    (41.78, 45.08, "W16"),
]


def layer_name(position_nm: float, period_nm: float) -> str:
    local = position_nm % period_nm
    for start, end, name in LAYERS:
        if start <= local < end:
            return name
    return "?"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bias_dir", type=Path)
    parser.add_argument("--period", type=float, default=45.08)
    parser.add_argument("--period-index", type=int, default=0)
    parser.add_argument("--emin", type=float, default=120.0)
    parser.add_argument("--emax", type=float, default=150.0)
    args = parser.parse_args()

    qdir = args.bias_dir / "Quantum" / "quantum_region"
    energies = np.loadtxt(
        qdir / "kp8" / "energy_spectrum_k00000.dat", skiprows=1
    )[:, 1] * 1e3
    probability = np.loadtxt(
        qdir / "kp8" / "probabilities_k00000.dat", skiprows=1
    )
    positions = probability[:, 0]
    densities = probability[:, 1:]
    dipoles = np.loadtxt(
        qdir / "kp8_kp8" / "dipole_moment_matrix_elements_k00000_component_x.txt",
        skiprows=1,
    )

    centroids = np.array(
        [
            float(np.trapz(positions * density, positions) / np.trapz(density, positions))
            for density in densities.T
        ]
    )

    low = args.period_index * args.period
    high = low + args.period
    print(f"States with centroid in physical period [{low:g}, {high:g}) nm")
    print("state   E_meV    centroid_nm  local_nm  layer")
    local_states = []
    for index, (energy, centroid) in enumerate(zip(energies, centroids), start=1):
        if low <= centroid < high:
            local_states.append(index)
            print(
                f"{index:5d} {energy:9.3f} {centroid:12.3f} "
                f"{centroid - low:9.3f}  {layer_name(centroid, args.period)}"
            )

    print(f"\nStrongest transitions with {args.emin:g}-{args.emax:g} meV, "
          "same selected period")
    rows = []
    local_set = set(local_states)
    for i_raw, j_raw, z_nm, oscillator in dipoles:
        i, j = int(i_raw), int(j_raw)
        if i >= j or i not in local_set or j not in local_set:
            continue
        de = abs(energies[j - 1] - energies[i - 1])
        if args.emin <= de <= args.emax:
            rows.append((abs(float(z_nm)), de, i, j, float(oscillator)))
    for z_abs, de, i, j, oscillator in sorted(rows, reverse=True)[:30]:
        upper, lower = (i, j) if energies[i - 1] > energies[j - 1] else (j, i)
        print(
            f"{lower:3d}->{upper:3d} dE={de:7.2f} meV "
            f"lambda={1240/de:5.2f} um |z|={z_abs:7.3f} nm "
            f"O={oscillator:9.4g} "
            f"x_upper={centroids[upper-1]-low:5.1f} "
            f"x_lower={centroids[lower-1]-low:5.1f}"
        )


if __name__ == "__main__":
    main()
