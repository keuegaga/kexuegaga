# -*- coding: utf-8 -*-
"""Create low- and high-bias extensions for the Sun 2022 NEGF case."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
SOURCE = ROOT / "designs/sun2022_mocvd_9um_alloy006_independent_dv060_biasscan.negf"


def replace_first(text: str, pattern: str, replacement: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
    if count != 1:
        raise ValueError(f"Expected exactly one match for {pattern!r}")
    return result


def remove_gain_block(text: str) -> str:
    match = re.search(r"(?m)^[ \t]*Gain\s*\{", text)
    if not match:
        raise ValueError("Gain block not found")
    depth = 1
    index = match.end()
    while depth and index < len(text):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    if depth:
        raise ValueError("Unbalanced Gain block")
    return text[: match.start()] + text[index:]


def make_variant(
    *,
    output: Path,
    minimum: int,
    maximum: int,
    initial_bias: int,
    include_gain: bool,
    gf_tolerance: float = 1e-3,
    current_tolerance: float = 1e-3,
    nmax: int = 160,
) -> None:
    text = SOURCE.read_text(encoding="utf-8", errors="ignore")
    text = replace_first(text, r"(?m)^(\s*Min\s*=\s*)\d+", rf"\g<1>{minimum}")
    text = replace_first(text, r"(?m)^(\s*Max\s*=\s*)\d+", rf"\g<1>{maximum}")
    text = replace_first(
        text,
        r"(?m)^(\s*BiasForInitialElectronicModes\s*=\s*)\d+",
        rf"\g<1>{initial_bias}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*ConvergenceValueGF\s*=\s*)[0-9.eE+-]+",
        rf"\g<1>{gf_tolerance:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*ConvergenceValueCurrent\s*=\s*)[0-9.eE+-]+",
        rf"\g<1>{current_tolerance:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*NMaxIterations\s*=\s*)\d+",
        rf"\g<1>{nmax}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 DAU/MS QCL bias extension; '
            f'{minimum}-{maximum} mV/period; '
            + ("gain enabled." if include_gain else "gain output disabled.")
            + '"'
        ),
    )
    if include_gain:
        text = replace_first(
            text,
            r"(?m)^(\s*Vmin\s*=\s*)\d+",
            rf"\g<1>{minimum}",
        )
        text = replace_first(
            text,
            r"(?m)^(\s*Vmax\s*=\s*)\d+",
            rf"\g<1>{maximum}",
        )
    else:
        text = remove_gain_block(text)
        text = replace_first(
            text,
            r"(?m)^(\s*EnergyResolvedGain\s*=\s*)\w+",
            r"\g<1>no",
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)


def make_clamped_variant(output: Path, bias: float) -> None:
    text = SOURCE.read_text(encoding="utf-8", errors="ignore")
    for key, value in (
        ("Min", f"{bias:g}"),
        ("Max", f"{bias:g}"),
        ("Vmin", f"{bias:g}"),
        ("Vmax", f"{bias:g}"),
        ("BiasForInitialElectronicModes", f"{bias:g}"),
    ):
        text = replace_first(
            text,
            rf"(?m)^(\s*{key}\s*=\s*)[0-9.]+",
            rf"\g<1>{value}",
        )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMinSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>132",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMaxSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>140",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 DAU/MS QCL, fixed 9.17-um optical mode, '
            f'{bias:g} mV/period gain clamping; '
            'modal loss 2.227 1/cm, overlap 0.751."'
        ),
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedGain\s*=\s*)\w+",
        r"\g<1>no",
    )
    emfield = """
    EMfield{
        EMmode{
            PhotonEnergy = 135.26
            ElectricField = 0.0
        }
    }

"""
    gain_match = re.search(r"(?m)^[ \t]*Gain\s*\{", text)
    if not gain_match:
        raise ValueError("Gain block not found")
    text = text[: gain_match.start()] + emfield + text[gain_match.start() :]

    gain_start = re.search(r"(?m)^[ \t]*Gain\s*\{", text)
    if not gain_start:
        raise ValueError("Gain block not found after insertion")
    depth = 1
    index = gain_start.end()
    while depth and index < len(text):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    gain_block = text[gain_start.start() : index]
    insertion = (
        "        CavityLosses = 2.227\n"
        "        OverlapFactor = 0.751\n"
        "        GainClamping = yes\n\n"
    )
    fgr = re.search(r"(?m)^\s*FermiGoldenRule\s*\{", gain_block)
    if not fgr:
        raise ValueError("FermiGoldenRule block not found")
    gain_block = (
        gain_block[: fgr.start()] + insertion + gain_block[fgr.start() :]
    )
    gain_block, removed = re.subn(
        r"(?ms)^[ \t]*FermiGoldenRule\s*\{\s*Linewidth\s*=\s*10\s*\}\s*",
        "",
        gain_block,
        count=1,
    )
    if removed != 1:
        raise ValueError("Could not remove clamp-run FermiGoldenRule block")
    text = text[: gain_start.start()] + gain_block + text[index:]
    output.write_text(text, encoding="utf-8")
    print(output)


def main() -> None:
    make_variant(
        output=ROOT / "designs/sun2022_mocvd_9um_ldos_low_0_120mV.negf",
        minimum=0,
        maximum=120,
        initial_bias=0,
        include_gain=False,
    )
    make_variant(
        output=ROOT / "designs/sun2022_mocvd_9um_ldos_high_240_260mV.negf",
        minimum=240,
        maximum=260,
        initial_bias=220,
        include_gain=True,
    )
    make_variant(
        output=ROOT / "designs/sun2022_mocvd_9um_ldos_low_80_120mV.negf",
        minimum=80,
        maximum=120,
        initial_bias=60,
        include_gain=False,
        gf_tolerance=5e-3,
        current_tolerance=1e-2,
        nmax=120,
    )
    make_variant(
        output=ROOT / "designs/sun2022_mocvd_9um_ldos_0_260mV.negf",
        minimum=0,
        maximum=260,
        initial_bias=0,
        include_gain=True,
    )
    make_clamped_variant(
        ROOT / "designs/sun2022_mocvd_9um_9p17um_clamp_216p384mV.negf",
        216.384,
    )
    make_clamped_variant(
        ROOT / "designs/sun2022_mocvd_9um_9p17um_clamp_220mV.negf",
        220.0,
    )
    make_clamped_variant(
        ROOT / "designs/sun2022_mocvd_9um_9p17um_clamp_240mV.negf",
        240.0,
    )


if __name__ == "__main__":
    main()
