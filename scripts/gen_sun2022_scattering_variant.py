# -*- coding: utf-8 -*-
"""Generate controlled alloy-scattering sensitivity variants for Sun 2022."""

from __future__ import annotations

import argparse
from pathlib import Path


BASE = (
    Path(r"D:\Codex-Obsidian\QCL-nextnano\designs")
    / "sun2022_mocvd_9um_independent_material.negf"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("strength", type=float)
    parser.add_argument("output", type=Path)
    parser.add_argument("--self-consistent-boundary", action="store_true")
    args = parser.parse_args()

    text = BASE.read_text(encoding="utf-8")
    original = (
        'Content = "Sun 2022 independent material baseline: mwell 0.043, '
        'mbarrier 0.089, CBO 0.773 eV."'
    )
    replacement = (
        'Content = "Sun 2022 independent material baseline; controlled alloy '
        f'scattering sensitivity strength {args.strength:g}. '
        'IFR fixed at Delta 0.08 nm, Lambda 7 nm."'
    )
    if original not in text:
        raise RuntimeError("Unexpected independent-material header")
    text = text.replace(original, replacement)
    text = text.replace(
        "AlloyScatteringStrength = 1.0",
        f"AlloyScatteringStrength = {args.strength:g}",
    )
    if args.self_consistent_boundary:
        text = text.replace(
            "        GainMethod = 1\n",
            "        GainMethod = 1\n        SelfConsistentBoundary = yes\n",
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
