# -*- coding: utf-8 -*-
"""Plot Page2001 QCL conduction band edge + key wavefunctions (nextnano++ output)."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = r"C:\Users\ciomp\Documents\QCL-nextnano\runs\page2001\out_z\page2001_z\bias_00000"
OUT = r"C:\Users\ciomp\Documents\QCL-nextnano\attachments\page2001_bandstructure.png"

# --- conduction band edge (Gamma) ---
be = np.loadtxt(os.path.join(BASE, "bandedges.dat"), skiprows=1)
x_be = be[:, 0]
cb = be[:, 1]

# --- eigenvalues + energy-shifted |psi|^2 ---
ps = np.loadtxt(
    os.path.join(BASE, "Quantum", "quantum_region", "Gamma", "probabilities_shift_k00000.dat"),
    skiprows=1,
)
x_ps = ps[:, 0]
psi2 = ps[:, 21:]          # columns 22..41 = Psi^2_1..Psi^2_20 (shifted by eigenvalue)
states = {4: "red", 6: "blue", 8: "green", 10: "magenta"}
labels = {4: "State 4 (ground)", 6: "State 6 (lower laser)", 8: "State 8 (injector)", 10: "State 10 (upper laser)"}

fig, ax = plt.subplots(figsize=(11, 6.2))
ax.plot(x_be, cb, color="black", lw=1.6, label="Conduction band edge (Gamma)")
for i, c in states.items():
    ax.plot(x_ps, psi2[:, i - 1], color=c, lw=1.4, label=labels[i])

# highlight laser transition 10 -> 6
E10 = ps[0, 10]
E6 = ps[0, 6]
dE = E10 - E6
ax.annotate(
    "", xy=(22.0, E10), xytext=(22.0, E6),
    arrowprops=dict(arrowstyle="<->", color="k", lw=1.0),
)
ax.text(22.4, (E10 + E6) / 2, r"$\Delta E_{10,6}$ = %.1f meV" % (dE * 1e3), va="center", fontsize=10)

ax.set_xlim(-27, 51)
ax.set_xlabel("x [nm] (growth direction)", fontsize=11)
ax.set_ylabel("Energy [eV]", fontsize=11)
ax.set_title("Page2001 GaAs/AlGaAs QCL (9 um) - nextnano++ run (2026-08-20)", fontsize=12)
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
ax.grid(alpha=0.25)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=170)
print("saved:", OUT)
