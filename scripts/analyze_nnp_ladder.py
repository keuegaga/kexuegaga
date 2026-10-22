# -*- coding: utf-8 -*-
"""Summarize a spin-degenerate nextnano++ k.p QCL level ladder.

Usage:
  python scripts/analyze_nnp_ladder.py <bias_folder> [emin] [emax] [period_nm]
"""
import os
import sys

import numpy as np


def main():
    bias = sys.argv[1]
    emin = float(sys.argv[2]) if len(sys.argv) > 2 else 100
    emax = float(sys.argv[3]) if len(sys.argv) > 3 else 220
    period = float(sys.argv[4]) if len(sys.argv) > 4 else 61.4

    root = os.path.join(bias, "Quantum", "quantum_region")
    energies = np.loadtxt(
        os.path.join(root, "kp8", "energy_spectrum_k00000.dat"), skiprows=1
    )[:, 1]
    probabilities = np.loadtxt(
        os.path.join(root, "kp8", "probabilities_k00000.dat"), skiprows=1
    )
    x = probabilities[:, 0]
    psi2 = probabilities[:, 1:]
    dipoles = np.loadtxt(
        os.path.join(
            root,
            "kp8_kp8",
            "dipole_moment_matrix_elements_k00000_component_x.txt",
        ),
        skiprows=1,
    )

    def centroid(state):
        weight = psi2[:, state - 1]
        return float((x * weight).sum() / weight.sum())

    print("Spin-doubled levels in the active-state energy region:")
    print(" state  E[eV]     E[meV]   pos[nm]  in_period[nm]")
    first = max(1, np.searchsorted(energies, energies[0] + 0.08))
    for state in range(first, len(energies) + 1):
        if state % 2 == 0:
            continue
        pos = centroid(state)
        print(
            f" {state:5d}  {energies[state-1]:.6f}  "
            f"{energies[state-1]*1e3:8.2f}  {pos:8.2f}  {pos % period:9.2f}"
        )

    rows = []
    for i, j, z, oscillator in dipoles:
        i, j, z = int(i), int(j), abs(float(z))
        de = abs(energies[i - 1] - energies[j - 1]) * 1e3
        if emin <= de <= emax:
            rows.append((de, z, i, j, float(oscillator)))

    groups = {}
    for de, z, i, j, oscillator in rows:
        key = round(de / 0.25) * 0.25
        current = groups.get(key)
        if current is None or z > current[1]:
            groups[key] = (de, z, i, j, oscillator)

    print("\nUnique transition-energy groups (largest |z| retained):")
    print(" dE[meV]  lambda[um]  |z|[nm]  pair     pos_i  pos_j")
    for key in sorted(groups):
        de, z, i, j, _ = groups[key]
        print(
            f" {de:8.2f}  {1240/de:9.2f}  {z:7.2f}  "
            f"{i:3d}-{j:<3d}  {centroid(i):6.1f} {centroid(j):6.1f}"
        )


if __name__ == "__main__":
    main()
