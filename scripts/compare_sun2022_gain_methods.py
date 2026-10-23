# -*- coding: utf-8 -*-
"""Compare FGR and self-consistent gain at the 9.17 um target."""

from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
RUN = ROOT / "runs/sun2022_mocvd/negf_alloy006_biasscan_140_220"
OUT = ROOT / "results/qcl_validation/sun2022_gain_method_comparison.csv"


def value_at(path: Path, energy_mev: float) -> float:
    data = np.loadtxt(path, skiprows=1)
    return float(data[np.argmin(np.abs(data[:, 0] - energy_mev)), 1])


def main() -> None:
    current = np.loadtxt(RUN / "Current_vs_Voltage.dat", skiprows=1)
    lines = ["bias_mV,current_kA_cm2,fgr_gain_135meV,selfconsistent_gain_135meV"]
    for bias, current_density in current:
        gain_dir = RUN / f"{int(bias)}mV/Gain"
        fgr = value_at(
            gain_dir / "Gain_FermiGoldenRule_vs_Energy_[0,0,1].dat", 135.0
        )
        self_consistent = value_at(
            gain_dir / "Gain_SelfConsistent_vs_Energy.dat", 135.0
        )
        lines.append(
            f"{bias:g},{current_density / 1000:.6f},{fgr:.6f},{self_consistent:.6f}"
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
