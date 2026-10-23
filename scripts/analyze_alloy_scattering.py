# -*- coding: utf-8 -*-
"""Audit nextnano alloy-disorder input and scattering-rate scaling."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def read_columns(path: Path) -> np.ndarray:
    return np.loadtxt(path, skiprows=1)


def parse_rates(path: Path) -> np.ndarray:
    rows = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 4 and parts[0].isdigit():
                rows.append([float(value) for value in parts[:4]])
    return np.asarray(rows)


def nearest_indices(reference: np.ndarray, target: np.ndarray) -> np.ndarray:
    return np.array([int(np.argmin(np.abs(reference - value))) for value in target])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--independent-dv-ev", default="0.30,0.44,0.50,0.70,1.00")
    args = parser.parse_args()

    reference_input = args.reference / "Input"
    content = read_columns(reference_input / "AlloyContent.dat")
    term = read_columns(reference_input / "AlloyScatteringTerm.dat")
    common_x = np.intersect1d(content[:, 0], term[:, 0])
    content_y = content[np.isin(content[:, 0], common_x)]
    term_y = term[np.isin(term[:, 0], common_x)]
    order = np.argsort(common_x)
    common_x = common_x[order]
    content_y = content_y[order]
    term_y = term_y[order]

    print("Reference alloy-scattering term")
    print(f"x range: {content_y[:, 1].min():.6g} to {content_y[:, 1].max():.6g}")
    print(f"term range: {term_y[:, 1].min():.6g} to {term_y[:, 1].max():.6g} eV^2")
    unique_levels = np.unique(np.round(content_y[:, 1], 6))
    for level in unique_levels:
        mask = np.isclose(content_y[:, 1], level, atol=1e-6)
        values = term_y[mask, 1]
        print(
            f"x={level:.6f}: term mean={values.mean():.9g}, "
            f"min={values.min():.9g}, max={values.max():.9g}, n={len(values)}"
        )

    effective_potential = float(np.sqrt(term_y[:, 1].mean()))
    print(f"\nEquivalent sqrt(mean term) = {effective_potential:.6f} eV")
    print("Independent dV (eV)  equivalent strength if term=dV^2")
    for d_v in [float(value) for value in args.independent_dv_ev.split(",")]:
        print(f"{d_v:19.3f}  {(d_v / effective_potential) ** 2:10.5f}")

    persistent_levels = []
    for level in unique_levels:
        mask = np.isclose(content_y[:, 1], level, atol=1e-6)
        if int(mask.sum()) >= 10:
            persistent_levels.append((float(level), float(term_y[mask, 1].mean())))
    print("\nLayer-resolved interpretation")
    for level, value in persistent_levels:
        print(
            f"x={level:.6f}: sqrt(term)={np.sqrt(value):.6f} eV"
        )
        for d_v in [float(value) for value in args.independent_dv_ev.split(",")]:
            print(f"  dV={d_v:.3f} eV -> strength {(d_v**2 / value):.5f}")

    rate_sets = {}
    for run in args.runs:
        matches = sorted(run.rglob("ScatteringRate_mechanisms.dat"))
        if not matches:
            raise FileNotFoundError(f"No ScatteringRate_mechanisms.dat under {run}")
        rates_path = matches[0]
        rates = parse_rates(rates_path)
        rate_sets[run.name] = rates

    names = list(rate_sets)
    base = rate_sets[names[0]]
    print("\nScattering-rate scaling relative to first run")
    print("state  alloy_rate_first  ratio_to_first")
    for row in base[:14]:
        state = int(row[0])
        values = []
        for name in names:
            match = rate_sets[name][rate_sets[name][:, 0] == state, 3]
            values.append(float(match[0]) if len(match) else np.nan)
        ratios = np.asarray(values[1:]) / values[0] if values[0] else np.array([])
        ratio_text = ", ".join(f"{ratio:.5f}" for ratio in ratios)
        print(f"{state:5d} {values[0]:18.6g}  {ratio_text}")


if __name__ == "__main__":
    main()
