# -*- coding: utf-8 -*-
"""Summarise the official nextnano.NEGF examples: period, temperature and numerics.

Handy to compare our own input settings against structures of similar period.
"""
import os
import re

EX = r"C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\examples"


def grab(pattern, text, default="-"):
    m = re.search(pattern, text)
    return m.group(1) if m else default


def main():
    header = f'{"file":44s} {"period":>7s} {"T[K]":>5s} {"layers":>6s} {"coh":>4s}' \
             f' {"axWin":>6s} {"latWin":>6s} {"latVal":>6s}'
    print(header)
    print("-" * len(header))
    for f in sorted(os.listdir(EX)):
        if not f.endswith(".negf"):
            continue
        text = open(os.path.join(EX, f), errors="ignore").read()
        thick = [float(x) for x in re.findall(r"Thickness\s*=\s*([0-9.]+)", text)]
        period = sum(thick)
        row = [
            f[:44],
            f"{period:7.1f}",
            grab(r"Temperature\s*=\s*([0-9.]+)", text),
            f"{len(thick):6d}",
            grab(r"CoherenceLengthInPeriods\s*=\s*([0-9.]+)", text),
            grab(r"EnergyRangeAxial\s*=\s*([0-9.]+)", text),
            grab(r"EnergyRangeLateral\s*=\s*([0-9.]+)", text),
            grab(r"Value\s*=\s*([0-9.]+)", text),
        ]
        print(f"{row[0]:44s} {row[1]:>7s} {row[2]:>5s} {row[3]:>6s} {row[4]:>4s}"
              f" {row[5]:>6s} {row[6]:>6s} {row[7]:>6s}")


if __name__ == "__main__":
    main()
