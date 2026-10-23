# -*- coding: utf-8 -*-
"""Analyze nextnano.NEGF density-matrix diagonals and coherences."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np


PATTERN = re.compile(
    r"<Psi_(\d+)\|\s*rho\s*\|Psi_(\d+)>\s*=\s*"
    r"\(([^,]+),([^)]+)\)"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    text = args.path.read_text(encoding="utf-8", errors="replace")
    entries = [
        (int(i), int(j), float(real), float(imag))
        for i, j, real, imag in PATTERN.findall(text)
    ]
    size = max(max(row_i, row_j) for row_i, row_j, _, _ in entries)
    matrix = np.zeros((size, size), dtype=complex)
    for i, j, real, imag in entries:
        matrix[i - 1, j - 1] = real + 1j * imag

    print(f"States: {size}")
    print(f"Trace real: {np.trace(matrix).real:.9g}")
    print(f"Hermiticity max error: {np.max(np.abs(matrix - matrix.conj().T)):.3e}")

    print("\nLargest off-diagonal coherences")
    print("i  j  Re(rho)       Im(rho)       |rho|")
    rows = []
    for i in range(size):
        for j in range(i + 1, size):
            value = matrix[i, j]
            rows.append((abs(value), i + 1, j + 1, value.real, value.imag))
    for magnitude, i, j, real, imag in sorted(rows, reverse=True)[: args.top]:
        print(f"{i:3d} {j:3d} {real:+.6e} {imag:+.6e} {magnitude:.6e}")

    print("\nDiagonal populations")
    for i, value in enumerate(np.diag(matrix).real, start=1):
        print(f"{i:3d} {value:.9g}")


if __name__ == "__main__":
    main()
