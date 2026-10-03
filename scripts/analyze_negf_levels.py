# -*- coding: utf-8 -*-
"""Analyze nextnano.NEGF eigenstates at one bias point.

Prints, for a given output folder (e.g. .../scan_w/w32/320mV):
  1. eigen-energies per period and the intra-period spacings
  2. which quantum well each level sits in
  3. level populations
  4. strongest dipole pairs, their energy separation and whether the
     population is inverted (upper > lower)

Usage:
    python scripts/analyze_negf_levels.py <bias_output_folder> [period_nm] [layer_spec]

Example:
    python scripts/analyze_negf_levels.py D:\\...\\runs\\scan_w\\w32\\320mV 22.5 "3.4/4.0/1.3/5.2/0.9/2.6/1.9/3.2"
"""
import os
import re
import sys

import numpy as np


def parse_layers(spec):
    """'3.4/4.0/1.3/...' starting with a barrier -> list of (start, end, name)."""
    layers = []
    pos = 0.0
    is_barrier = True
    for i, tok in enumerate(spec.split("/"), start=1):
        t = float(tok)
        kind = "B" if is_barrier else "W"
        layers.append((pos, pos + t, f"{kind}{t:g}#{i}"))
        pos += t
        is_barrier = not is_barrier
    return layers


def layer_of(x, layers, period):
    xm = x % period
    for a, b, name in layers:
        if a <= xm < b:
            return name
    return f"{xm:.2f}"


def main():
    folder = sys.argv[1]
    period = float(sys.argv[2]) if len(sys.argv) > 2 else 22.5
    spec = sys.argv[3] if len(sys.argv) > 3 else "3.4/4.0/1.3/5.2/0.9/2.6/1.9/3.2"
    layers = parse_layers(spec)

    es = os.path.join(folder, "EnergyEigenstates")
    data = np.loadtxt(os.path.join(es, "EigenStates.dat"), skiprows=2)
    x = data[:, 0]
    psi = data[:, 2:]
    n = psi.shape[1]

    # eigen-energies: take from Energy_Eigenstates.dat of the parent run if available
    parent = os.path.dirname(folder)
    bias = os.path.basename(folder).replace("mV", "")
    energies = None
    ee = os.path.join(parent, "Energy_Eigenstates.dat")
    if os.path.exists(ee):
        rows = np.atleast_2d(np.loadtxt(ee, skiprows=1))
        for r in rows:
            if abs(r[0] - float(bias)) < 1e-6:
                energies = r[1:]
                break
    if energies is None:
        raise SystemExit("could not find eigen-energies in Energy_Eigenstates.dat")

    # populations
    pops = {}
    with open(os.path.join(es, "Populations.txt")) as fh:
        for line in fh.read().splitlines()[1:]:
            p = line.split()
            if len(p) >= 2:
                pops[int(p[0])] = float(p[1])

    per = max(1, n // 3)
    print(f"=== {folder} ===")
    print(f"levels per period = {per}")
    for p in range(3):
        seg = energies[p * per:(p + 1) * per]
        spac = " | ".join(f"{abs(seg[i] - seg[i + 1]):6.1f}" for i in range(len(seg) - 1))
        print("  period %d: %s   intra-spacings: %s" % (p, " ".join(f"{v:8.2f}" for v in seg), spac))

    print("level -> hosting layer (period 0):")
    for i in range(per):
        w = np.abs(psi[:, i]) ** 2
        pk = x[int(np.argmax(w))]
        print(f"  lev.{i+1}: E={energies[i]:8.2f} meV  peak x={pk:7.2f} nm  layer={layer_of(pk, layers, period)}"
              f"  pop={pops.get(i+1, float('nan')):.3f}")

    # dipole pairs
    txt = open(os.path.join(es, "Dipoles.txt")).read()
    dip = {}
    for m in re.finditer(r"<Psi_(\d+)\| z \|Psi_(\d+)> = ([-\d.eE+]+)", txt):
        i, j, v = int(m.group(1)), int(m.group(2)), float(m.group(3))
        dip[(i, j)] = v
    print("strongest dipole pairs (i<j) with inversion check:")
    rows = []
    for (i, j), v in dip.items():
        if i >= j:
            continue
        de = abs(energies[i - 1] - energies[j - 1])
        rows.append((abs(v), i, j, de))
    rows.sort(reverse=True)
    for z, i, j, de in rows[:10]:
        pi, pj = pops.get(i, float("nan")), pops.get(j, float("nan"))
        inv = "inverted" if pi > pj else "not inverted"
        print(f"  {i:2d}<->{j:2d}: |z|={z:6.3f} nm  dE={de:7.1f} meV "
              f"(lambda {1240/de if de else float('inf'):5.2f} um)  pop {pi:.3f}/{pj:.3f}  {inv}")


if __name__ == "__main__":
    main()
