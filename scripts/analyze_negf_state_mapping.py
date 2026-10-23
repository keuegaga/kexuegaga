# -*- coding: utf-8 -*-
"""Map nextnano.NEGF states to local periods and optical transitions.

This script is deliberately diagnostic: it does not fit any scattering
parameter.  It combines eigen-energies, wavefunction positions, occupations,
dipole elements, lifetimes and transition-resolved gain so that a state pair
is only assigned to E3/E4 when its spatial and optical evidence agree.

Usage:
    python scripts/analyze_negf_state_mapping.py RUN_DIR BIAS_DIR PERIOD_NM
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np


LAYERS = [
    (0.00, 2.80, "B1", 2.80),
    (2.80, 5.80, "W2", 3.00),
    (5.80, 7.05, "B3", 1.25),
    (7.05, 13.32, "W4", 6.27),
    (13.32, 14.32, "B5", 1.00),
    (14.32, 19.67, "W6", 5.35),
    (19.67, 20.55, "B7", 0.88),
    (20.55, 25.40, "W8", 4.85),
    (25.40, 26.49, "B9", 1.09),
    (26.49, 30.65, "W10", 4.16),
    (30.65, 31.87, "B11", 1.22),
    (31.87, 35.53, "W12", 3.66),
    (35.53, 36.95, "B13", 1.42),
    (36.95, 40.10, "W14", 3.15),
    (40.10, 41.78, "B15", 1.68),
    (41.78, 45.08, "W16", 3.30),
]


def layer_at(x_nm: float, period_nm: float) -> str:
    x_local = x_nm % period_nm
    for start, end, name, _ in LAYERS:
        if start <= x_local < end:
            return name
    return f"x={x_local:.2f}nm"


def ideal_energy(position_nm: float, field_kv_cm: float, reference_nm: float = 0.0):
    """Electron band edge tilt in meV (100 meV/(kV/cm)/nm)."""
    return -100.0 * field_kv_cm * 1e-3 * (position_nm - reference_nm)


def parse_energies(path: Path) -> np.ndarray:
    rows = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if rows.shape[0] != 1:
        raise ValueError(f"Expected one bias row in {path}, found {rows.shape[0]}")
    return rows[0, 1:]


def parse_row_values(path: Path) -> np.ndarray:
    rows = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if rows.shape[0] != 1:
        raise ValueError(f"Expected one periodic row in {path}, found {rows.shape[0]}")
    return rows[0, 1:]


def parse_indexed_values(path: Path) -> dict[int, float]:
    values = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                values[int(parts[0])] = float(parts[1])
    return values


def parse_dipoles(path: Path) -> dict[tuple[int, int], float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = r"<Psi_(\d+)\| z \|Psi_(\d+)> = ([-\d.eE+]+)"
    out = {}
    for match in re.finditer(pattern, text):
        i, j, value = int(match.group(1)), int(match.group(2)), float(match.group(3))
        out[(i, j)] = value
    return out


def parse_scattering(path: Path) -> dict[int, tuple[float, float, float]]:
    out = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 4 and parts[0].isdigit():
                out[int(parts[0])] = tuple(float(v) for v in parts[1:4])
    return out


def parse_decomposed_gain(path: Path, photon_energy_mev: float):
    with path.open(encoding="utf-8", errors="replace") as handle:
        header = handle.readline().rstrip("\n").split("\t")
    labels = [part.strip() for part in header[1:] if part.strip()]
    data = np.loadtxt(path, skiprows=1)
    energies = data[:, 0]
    gains = data[:, 1:]
    print(
        f"[gain parser] header labels={len(labels)}, energy rows={len(energies)}, "
        f"data columns after energy={gains.shape[1]}"
    )
    if gains.shape[1] != len(labels):
        # Some nextnano files contain trailing empty tab-separated columns.
        labels = labels[: gains.shape[1]]

    idx = int(np.argmin(np.abs(energies - photon_energy_mev)))
    values_at_target = gains[idx]
    peak_indices = np.argmax(np.abs(gains), axis=0)
    peaks = []
    for col, label in enumerate(labels):
        match = re.search(r"Transition\s+(\d+)\s*=>\s*(\d+)", label)
        if not match:
            continue
        peaks.append(
            {
                "i": int(match.group(1)),
                "j": int(match.group(2)),
                "value_at_target": float(values_at_target[col]),
                "peak_energy": float(energies[peak_indices[col]]),
                "peak_abs_value": float(gains[peak_indices[col], col]),
                "peak_signed_value": float(gains[peak_indices[col], col]),
            }
        )
    return float(energies[idx]), peaks


def parse_eigenstates(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        handle.readline()
        header = handle.readline().rstrip("\n").split("\t")
    data = np.loadtxt(path, skiprows=2)
    return header, data[:, 0], data[:, 2:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("bias_dir", type=Path)
    parser.add_argument("period_nm", type=float, nargs="?", default=45.08)
    parser.add_argument("--field-kv-cm", type=float, default=48.0)
    parser.add_argument("--target-mev", type=float, default=135.0)
    args = parser.parse_args()

    energies = parse_energies(args.run_dir / "Energy_Eigenstates.dat")
    population_values = parse_row_values(args.run_dir / "Populations_Eigenstates.dat")
    populations = {index + 1: float(value) for index, value in enumerate(population_values)}
    eigen_dir = args.bias_dir / "EnergyEigenstates"
    lifetimes = parse_indexed_values(eigen_dir / "Lifetimes.dat")
    scattering = parse_scattering(eigen_dir / "ScatteringRate_mechanisms.dat")
    dipoles = parse_dipoles(eigen_dir / "Dipoles.txt")
    header, positions, psi = parse_eigenstates(eigen_dir / "EigenStates.dat")

    if len(energies) != psi.shape[1]:
        raise ValueError("Energies and wavefunction column count differ")

    print(f"RUN: {args.run_dir}")
    print(f"BIAS: {args.bias_dir}")
    print(f"N states: {len(energies)}; wavefunction points: {len(positions)}")
    print("\nState localization and dynamic quantities")
    print("state  energy_meV  period  peak_nm  centroid_nm  layer   population  lifetime_ps  LO/IFR/Alloy")

    local_rows = []
    for idx in range(len(energies)):
        # EigenStates.dat already contains |Psi_i(z)|^2, shifted vertically
        # by E_i.  It is not a complex amplitude.
        density = np.maximum(psi[:, idx], 0.0)
        density = density - float(np.min(density))
        norm = float(np.trapz(density, positions))
        if norm > 0:
            density = density / norm
            peak = float(positions[int(np.argmax(density))])
            centroid = float(np.trapz(positions * density, positions))
        else:
            peak = float(positions[int(np.argmax(psi[:, idx]))])
            centroid = float("nan")
        period = int(np.floor(peak / args.period_nm))
        local_mev = (
            float(energies[idx] - ideal_energy(centroid, args.field_kv_cm))
            if np.isfinite(centroid)
            else float("nan")
        )
        rates = scattering.get(idx + 1, (np.nan, np.nan, np.nan))
        row = {
            "index": idx + 1,
            "energy": energies[idx],
            "period": period,
            "peak": peak,
            "centroid": centroid,
            "local_mev": local_mev,
            "layer": layer_at(peak, args.period_nm),
            "population": populations.get(idx + 1, np.nan),
            "lifetime": lifetimes.get(idx + 1, np.nan),
        }
        local_rows.append(row)
        print(
            f"{idx + 1:5d} {energies[idx]:10.3f} {period:6d} {peak:8.2f} "
            f"{centroid:11.2f} {row['layer']:7s} {row['population']:11.5f} "
            f"{row['lifetime']:11.5f} {rates[0]:6.3f}/{rates[1]:6.3f}/{rates[2]:6.3f}"
        )

    print(f"\nOptical pairs with |dE-{args.target_mev:g}| <= 12 meV")
    print("pair       dE_meV  |z|_nm  upper/lower  populatons  lifetime_ps  local_periods/layers")
    candidates = []
    for (i, j), z_nm in dipoles.items():
        if i >= j:
            continue
        de = float(energies[j - 1] - energies[i - 1])
        if abs(de - args.target_mev) <= 12:
            pi, pj = populations.get(i, np.nan), populations.get(j, np.nan)
            if pi >= pj:
                upper, lower, pu, pl = i, j, pi, pj
            else:
                upper, lower, pu, pl = j, i, pj, pi
            candidates.append((abs(pu - pl), abs(z_nm), upper, lower, de, pu, pl))
    for _, z_abs, upper, lower, de, pu, pl in sorted(candidates, reverse=True):
        upper_row = local_rows[upper - 1]
        lower_row = local_rows[lower - 1]
        print(
            f"{lower:2d}<->{upper:2d} {abs(de):9.3f} {z_abs:7.3f} "
            f"{upper:2d}/{lower:2d}       {pu:.5f}/{pl:.5f} "
            f"{upper_row['lifetime']:.5f}/{lower_row['lifetime']:.5f} "
            f"p{upper_row['period']}:{upper_row['layer']}->p{lower_row['period']}:{lower_row['layer']}"
        )

    gain_file = next((args.bias_dir / "Gain").glob("Gain_FermiGoldenRuleDecomposed_vs_Energy_*.dat"))
    actual_target, transitions = parse_decomposed_gain(gain_file, args.target_mev)
    print(f"\nTransition-resolved gain near {actual_target:g} meV from {gain_file.name}")
    print("pair       gain_at_target  signed_peak  peak_meV")
    for item in sorted(transitions, key=lambda value: value["value_at_target"], reverse=True)[:20]:
        print(
            f"{item['i']:2d}=>{item['j']:2d} "
            f"{item['value_at_target']:14.5f} {item['peak_signed_value']:12.5f} "
            f"{item['peak_energy']:9.3f}"
        )
    print("\nMost negative transition-resolved gain near target")
    for item in sorted(transitions, key=lambda value: value["value_at_target"])[:10]:
        print(
            f"{item['i']:2d}=>{item['j']:2d} "
            f"{item['value_at_target']:14.5f} {item['peak_signed_value']:12.5f} "
            f"{item['peak_energy']:9.3f}"
        )


if __name__ == "__main__":
    main()
