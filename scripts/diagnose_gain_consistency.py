# -*- coding: utf-8 -*-
"""Consistency check for a nextnano.NEGF gain calculation.

Physics background: for a two-level intersubband transition the gain and the
spontaneous emission share the same lineshape, so

    gain(E) / spontaneous_emission(E) = const   (equal to the population factor)

If that ratio changes sign or varies strongly with photon energy, the gain
reading should be treated with caution.

The script also compares the gain peak energy with the eigen-state spacings
listed in Energy_Eigenstates.dat.

Usage:
    python scripts/diagnose_gain_consistency.py <bias_output_folder> [peak_energy_meV]
"""
import os
import re
import sys

import numpy as np


def load_decomposed(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix)]
    if not files:
        return None, None, None
    path = os.path.join(folder, files[0])
    header = [h.strip() for h in open(path).readline().split("\t") if h.strip()]
    data = np.loadtxt(path, skiprows=1)
    return header, data[:, 0], data[:, 1:]


def main():
    bias_dir = sys.argv[1]
    gdir = os.path.join(bias_dir, "Gain")

    hg, eg, mg = load_decomposed(gdir, "Gain_FermiGoldenRuleDecomposed")
    hs, es, ms = load_decomposed(gdir, "SpontaneousEmission_FermiGoldenRuleDecomposed")
    if hg is None or hs is None:
        raise SystemExit("decomposed gain / spontaneous emission files not found")

    # total gain spectrum -> peak
    #   "fgr"  : small-signal material gain (Fermi golden rule) - use for design work
    #   default: self-consistent gain (photon-field / loss clamped) if available
    force_fgr = len(sys.argv) > 2 and sys.argv[2].lower() == "fgr"
    sc_path = os.path.join(gdir, "Gain_SelfConsistent_vs_Energy.dat")
    if force_fgr or not os.path.exists(sc_path):
        cands = [f for f in os.listdir(gdir) if f.startswith("Gain_FermiGoldenRule_vs_Energy")]
        if cands:
            sc_path = os.path.join(gdir, cands[0])
            if force_fgr:
                print("note: using Fermi golden rule (small-signal material gain)")
        elif not os.path.exists(sc_path):
            raise SystemExit("no gain file found")
    if not os.path.exists(sc_path):
        cands = [f for f in os.listdir(gdir) if f.startswith("Gain_FermiGoldenRule_vs_Energy")]
        if not cands:
            raise SystemExit("neither self-consistent nor Fermi golden rule gain file found")
        sc_path = os.path.join(gdir, cands[0])
        print("note: self-consistent gain not available yet, using Fermi golden rule file")
    sc = np.loadtxt(sc_path, skiprows=1)
    peak_i = int(np.argmax(sc[:, 1]))
    peak_e, peak_g = sc[peak_i, 0], sc[peak_i, 1]
    print(f"bias folder      : {bias_dir}")
    print(f"gain peak        : {peak_g:+.2f} 1/cm at {peak_e:.0f} meV "
          f"(lambda {1240 / peak_e:.2f} um)")

    # dominant transition at the peak
    k = int(np.argmin(np.abs(eg - peak_e)))
    order = np.argsort(-np.abs(mg[k]))[:4]
    print("dominant transitions at the peak (decomposed FGR gain):")
    for idx in order:
        print(f"   {hg[idx + 1]:26s} {mg[k, idx]:+10.2f}")

    label = hg[order[0] + 1]
    kg, ks = hg.index(label) - 1, hs.index(label) - 1
    print(f"\nlineshape consistency for '{label}':")
    print("   E[meV]     gain       SE        gain/SE")
    ratios = []
    lo, hi = max(0, peak_e - 60), peak_e + 40
    for t in np.arange(lo, hi + 1, 10):
        a = int(np.argmin(np.abs(eg - t)))
        b = int(np.argmin(np.abs(es - t)))
        g, s = mg[a, kg], ms[b, ks]
        r = g / s if abs(s) > 1e-12 else float("nan")
        ratios.append(r)
        print(f"  {eg[a]:7.1f}  {g:9.2f}  {s:10.3g}  {r:9.4f}")
    fin = [r for r in ratios if np.isfinite(r)]
    if fin:
        sign_change = min(fin) < 0 < max(fin)
        print(f"\n-> ratio range [{min(fin):.4f}, {max(fin):.4f}], "
              f"sign change: {sign_change}")
        if sign_change:
            print("   WARNING: gain and spontaneous emission are not proportional;")
            print("   the positive gain reading needs numerical validation.")

    # eigen-state spacings vs peak energy
    parent = os.path.dirname(bias_dir.rstrip("\\/"))
    ee = os.path.join(parent, "Energy_Eigenstates.dat")
    if os.path.exists(ee):
        bias = float(os.path.basename(bias_dir).replace("mV", ""))
        rows = np.atleast_2d(np.loadtxt(ee, skiprows=1))
        for row in rows:
            if abs(row[0] - bias) < 1e-6:
                energies = row[1:]
                break
        else:
            energies = None
        if energies is not None:
            print(f"\neigen-state spacings near the peak ({peak_e:.0f} meV):")
            hits = []
            for i in range(len(energies)):
                for j in range(i + 1, len(energies)):
                    de = abs(energies[i] - energies[j])
                    if abs(de - peak_e) < 20:
                        hits.append((abs(de - peak_e), i + 1, j + 1, de))
            hits.sort()
            if hits:
                for _, i, j, de in hits[:6]:
                    print(f"   state {i:2d} <-> {j:2d}: {de:7.1f} meV "
                          f"(off by {abs(de - peak_e):4.1f} meV)")
            else:
                print("   none within 20 meV -> the gain peak does not correspond")
                print("   to any transition between the listed eigen-states")


if __name__ == "__main__":
    main()
