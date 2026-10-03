# -*- coding: utf-8 -*-
"""Compare self-consistent gain spectra of the well-width scan cases (w32/w34/w36).

Usage:
    python scripts/compare_scan_spectra.py <scan_output_root> [bias_label ...]

Example:
    python scripts/compare_scan_spectra.py D:\\Codex-Obsidian\\QCL-nextnano\\runs\\scan_w 300mV 320mV
"""
import os
import sys

import numpy as np


def load(root, case, bias):
    path = os.path.join(root, case, bias, "Gain", "Gain_SelfConsistent_vs_Energy.dat")
    if not os.path.exists(path):
        return None
    return np.loadtxt(path, skiprows=1)


def main():
    root = sys.argv[1]
    biases = sys.argv[2:] or ["300mV", "320mV"]
    cases = ["w32", "w34", "w36"]

    for bias in biases:
        spectra = {c: load(root, c, bias) for c in cases}
        if all(v is None for v in spectra.values()):
            print(f"[{bias}] no data")
            continue
        energy = next(v[:, 0] for v in spectra.values() if v is not None)
        print(f"=== bias {bias} : photon energy [meV] vs gain [1/cm] ===")
        header = "  E   " + "".join(f"{c:>10}" for c in cases)
        print(header)
        for i, e in enumerate(energy):
            if i % 2:      # print every other point to keep it readable
                continue
            row = f"{e:6.0f}"
            for c in cases:
                v = spectra[c]
                row += f"{v[i, 1]:10.2f}" if v is not None else f"{'-':>10}"
            print(row)
        # peak info
        for c in cases:
            v = spectra[c]
            if v is None:
                continue
            k = int(np.argmax(v[:, 1]))
            print(f"  {c}: peak {v[k, 1]:+.2f} 1/cm at {v[k, 0]:.0f} meV "
                  f"(lambda {1240 / v[k, 0]:.2f} um)")
        print()


if __name__ == "__main__":
    main()
