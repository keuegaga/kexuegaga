# -*- coding: utf-8 -*-
"""Plot conduction band edge + selected kp wavefunctions from a nextnano++ run.

Usage:
    python scripts/plot_nnp_kp_states.py <bias_folder> <outfile.png> [state ...]

If no states are given, the 6 strongest dipole transitions in the 120-170 meV
window are used automatically.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def auto_states(bias):
    qdir = os.path.join(bias, "Quantum", "quantum_region")
    energy = np.loadtxt(os.path.join(qdir, "kp8", "energy_spectrum_k00000.dat"),
                        skiprows=1)[:, 1]
    dip = np.loadtxt(os.path.join(qdir, "kp8_kp8",
                                  "dipole_moment_matrix_elements_k00000_component_x.txt"),
                     skiprows=1)
    rows = []
    for i, j, z, _ in dip:
        i, j = int(i), int(j)
        if i >= j:
            continue
        de = abs(energy[i - 1] - energy[j - 1]) * 1e3
        if 120 < de < 170:
            rows.append((abs(z), i, j, de))
    rows.sort(reverse=True)
    picked = []
    for z, i, j, de in rows:
        for s in (i, j):
            if s not in picked:
                picked.append(s)
        if len(picked) >= 6:
            break
    return picked[:6]


def main():
    bias = sys.argv[1]
    out = sys.argv[2]
    states = [int(s) for s in sys.argv[3:]] or auto_states(bias)

    be = np.loadtxt(os.path.join(bias, "bandedges.dat"), skiprows=1)
    xb, cb = be[:, 0], be[:, 1]

    ps = np.loadtxt(os.path.join(bias, "Quantum", "quantum_region", "kp8",
                                 "probabilities_shift_k00000.dat"), skiprows=1)
    n = (ps.shape[1] - 1) // 2
    x = ps[:, 0]
    energies = ps[0, 1:1 + n]
    psi2 = ps[:, 1 + n:]

    # align the wavefunction energy scale with the band edge scale
    offset = np.median(cb) - np.median(energies[:max(5, n // 4)])

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(xb, cb, color="k", lw=1.6, label="导带边 (Gamma)")
    for s in states:
        y = psi2[:, s - 1] + offset
        ax.plot(x, y, lw=1.3, label=f"态 {s}  (E={energies[s-1]:.4f} eV)")
    ax.set_xlabel("位置 x [nm]")
    ax.set_ylabel("能量 [eV]")
    ax.set_title(f"Fei 2021 结构能带与波函数  —  {os.path.basename(os.path.dirname(bias))}")
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("saved:", out, " states:", states)


if __name__ == "__main__":
    main()
