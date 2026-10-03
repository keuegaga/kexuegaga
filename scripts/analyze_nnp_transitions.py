# -*- coding: utf-8 -*-
"""Analyse intersubband transitions of a nextnano++ kp-8band QCL run.

Reads the eigen-energies, the dipole matrix elements and the wavefunction
probability densities, then lists the strongest transitions inside a photon
energy window together with the spatial position of both states.

Usage:
    python scripts/analyze_nnp_transitions.py <bias_folder> [emin_meV] [emax_meV] [period_nm]

Example:
    python scripts/analyze_nnp_transitions.py D:\\...\\runs\\fei2021\\Fm50\\...\\bias_00000 120 170 57.3
"""
import os
import sys

import numpy as np


def main():
    bias = sys.argv[1]
    emin = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    emax = float(sys.argv[3]) if len(sys.argv) > 3 else 170.0
    period = float(sys.argv[4]) if len(sys.argv) > 4 else 57.3

    qdir = os.path.join(bias, "Quantum", "quantum_region")
    energy = np.loadtxt(os.path.join(qdir, "kp8", "energy_spectrum_k00000.dat"),
                        skiprows=1)[:, 1]
    prob = np.loadtxt(os.path.join(qdir, "kp8", "probabilities_k00000.dat"), skiprows=1)
    x = prob[:, 0]
    psi2 = prob[:, 1:]
    dip = np.loadtxt(os.path.join(qdir, "kp8_kp8",
                                  "dipole_moment_matrix_elements_k00000_component_x.txt"),
                     skiprows=1)

    def centroid(i):
        w = psi2[:, i - 1]
        s = w.sum()
        return (x * w).sum() / s if s > 0 else float("nan")

    rows = []
    for i, j, z, _ in dip:
        i, j = int(i), int(j)
        if i >= j:
            continue
        de = abs(energy[i - 1] - energy[j - 1]) * 1e3
        if emin < de < emax:
            rows.append((abs(z), i, j, de))
    rows.sort(reverse=True)

    print(f"folder      : {bias}")
    print(f"states      : {len(energy)}  (spin pairs included)")
    print(f"window      : {emin:.0f}-{emax:.0f} meV")
    print("  i    j    |z|[nm]   dE[meV]   lambda[um]   pos_i[nm]  pos_j[nm]  in-period_i  in-period_j")
    for z, i, j, de in rows[:12]:
        ci, cj = centroid(i), centroid(j)
        print(f" {i:3d}  {j:3d}   {z:7.2f}   {de:7.1f}   {1240 / de:9.2f}   "
              f"{ci:9.1f}  {cj:9.1f}   {ci % period:8.1f}  {cj % period:8.1f}")


if __name__ == "__main__":
    main()
