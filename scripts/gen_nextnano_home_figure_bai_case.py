# -*- coding: utf-8 -*-
"""Create the 0-500 mV, no-gain reproduction input for nextnano homepage Fig. 1/2."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


SOURCE = Path(
    r"C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\examples"
    r"\MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\nextnano_home_figures_bai_0_500mV.negf"
)


def remove_block(text: str, block_name: str) -> str:
    """Remove one brace-delimited top-level input block."""
    match = re.search(rf"(?m)^[ \t]*{re.escape(block_name)}\s*\{{", text)
    if not match:
        raise ValueError(f"Block not found: {block_name}")

    depth = 1
    index = match.end()
    while depth and index < len(text):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    if depth:
        raise ValueError(f"Unbalanced braces in block: {block_name}")
    return text[: match.start()] + text[index:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum", type=float, default=0.0)
    parser.add_argument("--maximum", type=float, default=500.0)
    parser.add_argument("--step", type=float, default=20.0)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--nmax", type=int, default=None)
    parser.add_argument("--current-tolerance", type=float, default=None)
    parser.add_argument("--gf-tolerance", type=float, default=None)
    parser.add_argument("--spatial-grid", type=float, default=None)
    parser.add_argument("--energy-grid", type=float, default=None)
    parser.add_argument("--axial-range", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = SOURCE.read_text(encoding="utf-8", errors="ignore")

    sweep_match = re.search(
        r"SweepParameters\s*\{.*?\}",
        text,
        flags=re.S,
    )
    if not sweep_match:
        raise ValueError("SweepParameters block not found")
    sweep = sweep_match.group(0)
    for key, value in (
        ("Min", f"{args.minimum:g}"),
        ("Max", f"{args.maximum:g}"),
        ("Delta", f"{args.step:g}"),
    ):
        sweep, count = re.subn(
            rf"(?m)^(\s*{key}\s*=\s*)[^\s#]+",
            rf"\g<1>{value}",
            sweep,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not set SweepParameters.{key}")
    text = text[: sweep_match.start()] + sweep + text[sweep_match.end() :]

    # Figures 1 and 2 are passive transport results. Removing gain clamping
    # avoids unnecessary self-consistent photon iterations and preserves I(V).
    text = remove_block(text, "Gain")
    if re.search(r"(?m)^[ \t]*EMfield\s*\{", text):
        text = remove_block(text, "EMfield")

    if args.nmax is not None:
        text, count = re.subn(
            r"(?m)^(\s*NMaxIterations\s*=\s*)[^\s#]+",
            rf"\g<1>{args.nmax}",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError("Could not set NMaxIterations")
    if args.current_tolerance is not None:
        text, count = re.subn(
            r"(?m)^(\s*ConvergenceValueCurrent\s*=\s*)[^\s#]+",
            rf"\g<1>{args.current_tolerance:g}",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError("Could not set ConvergenceValueCurrent")
    for key, value in (
        ("ConvergenceValueGF", args.gf_tolerance),
        ("SpatialGridSpacing", args.spatial_grid),
        ("EnergyGridSpacing", args.energy_grid),
        ("EnergyRangeAxial", args.axial_range),
    ):
        if value is None:
            continue
        text, count = re.subn(
            rf"(?m)^(\s*{key}\s*=\s*)[^\s#]+",
            rf"\g<1>{value:g}",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not set {key}")

    header = (
        "!TEXT\n"
        "nextnano homepage Figure 1/2 reproduction candidate.\n"
        "Official structure: MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf\n"
        f"Changes: voltage sweep {args.minimum:g}:{args.step:g}:"
        f"{args.maximum:g} mV/period; gain and EM field removed.\n"
        "The active-region geometry and physical parameters are unchanged.\n"
        "!ENDTEXT\n\n"
    )
    output = args.output.resolve()
    output.write_text(header + text, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
