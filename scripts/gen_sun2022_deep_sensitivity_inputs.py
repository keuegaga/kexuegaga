# -*- coding: utf-8 -*-
"""Generate Sun 2022 temperature, mode-competition, and tolerance cases."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
BASE_NEGF = (
    ROOT / "designs/sun2022_mocvd_9um_alloy006_independent_dv060.negf"
)
CLAMP_TEMPLATE = (
    ROOT
    / "designs/sun2022_mocvd_9um_10p33um_clamp_waveguide_consistent_216p384mV.negf"
)
DESIGN_BIAS = 216.384
BASE_LAYERS = [
    2.80, 3.00, 1.25, 6.27, 1.00, 5.35, 0.88, 4.85,
    1.09, 4.16, 1.22, 3.66, 1.42, 3.15, 1.68, 3.30,
]


def replace_first(text: str, pattern: str, replacement: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
    if count != 1:
        raise ValueError(f"Expected one match for {pattern!r}")
    return result


def set_single_bias(text: str, bias_mv: float) -> str:
    for key in ("Min", "Max", "Vmin", "Vmax", "BiasForInitialElectronicModes"):
        text = replace_first(
            text,
            rf"(?m)^(\s*{key}\s*=\s*)[0-9.]+",
            rf"\g<1>{bias_mv:.6f}",
        )
    return text


def set_layers(text: str, layers: list[float]) -> str:
    matches = list(
        re.finditer(
            r"(?m)^(\s*Layer\{\s*Material\s*=\s*\w+\s*Thickness\s*=\s*)"
            r"([0-9.]+)(\s*\})",
            text,
        )
    )
    if len(matches) != len(layers):
        raise ValueError(f"Expected {len(layers)} layers, found {len(matches)}")
    parts = []
    cursor = 0
    for match, width in zip(matches, layers):
        parts.append(text[cursor : match.start()])
        parts.append(match.group(1) + f"{width:.3f}" + match.group(3))
        cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts)


def make_sensitivity_case(
    name: str,
    *,
    well_delta_nm: float = 0.0,
    barrier_delta_nm: float = 0.0,
    composition_delta: float = 0.0,
    doping_scale: float = 1.0,
    ifr_amplitude: float = 0.08,
    alloy_strength: float = 0.06,
) -> Path:
    text = BASE_NEGF.read_text(encoding="utf-8", errors="ignore")
    layers = []
    for index, width in enumerate(BASE_LAYERS, start=1):
        delta = well_delta_nm if index % 2 == 0 else barrier_delta_nm
        layers.append(width + delta)
    text = set_layers(text, layers)
    period_nm = sum(layers)
    bias_mv = 48.0 * period_nm * 0.1
    text = set_single_bias(text, bias_mv)

    text = replace_first(
        text,
        r"(?m)^(\s*AlloyComposition\s*=\s*)0\.593",
        rf"\g<1>{0.593 + composition_delta:.3f}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*AlloyComposition\s*=\s*)0\.638",
        rf"\g<1>{0.638 + composition_delta:.3f}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*DopingDensity\s*=\s*)1\.5e17",
        rf"\g<1>{1.5e17 * doping_scale:.6g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*AmplitudeInZ\s*=\s*)[0-9.]+",
        rf"\g<1>{ifr_amplitude:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*AlloyScatteringStrength\s*=\s*)[0-9.]+",
        rf"\g<1>{alloy_strength:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedPlots\s*=\s*)\w+",
        r"\g<1>no",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedGain\s*=\s*)\w+",
        r"\g<1>no",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMinSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>120",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMaxSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>120",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 sensitivity case; '
            f'well_delta={well_delta_nm:g} nm; '
            f'barrier_delta={barrier_delta_nm:g} nm; '
            f'composition_delta={composition_delta:g}; '
            f'doping_scale={doping_scale:g}; '
            f'IFR={ifr_amplitude:g} nm; '
            f'alloy={alloy_strength:g}; '
            f'bias={bias_mv:.3f} mV."'
        ),
    )
    output = ROOT / "designs" / f"sun2022_sensitivity_{name}.negf"
    output.write_text(text, encoding="utf-8")
    print(f"{output} | period={period_nm:.3f} nm | bias={bias_mv:.3f} mV")
    return output


def make_temperature_case(temperature: int) -> Path:
    text = CLAMP_TEMPLATE.read_text(encoding="utf-8", errors="ignore")
    text = replace_first(
        text,
        r"(?m)^(\s*Temperature\s*=\s*)\d+",
        rf"\g<1>{temperature}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 10.33-um fixed mode, corrected waveguide, '
            f'{temperature} K, 216.384 mV/period."'
        ),
    )
    output = ROOT / "designs" / f"sun2022_temperature_{temperature}K_10p33.negf"
    output.write_text(text, encoding="utf-8")
    print(output)
    return output


def make_mode_case(
    name: str,
    *,
    photon_mev: float,
    wavelength_um: float,
    overlap: float,
    modal_loss: float,
) -> Path:
    text = CLAMP_TEMPLATE.read_text(encoding="utf-8", errors="ignore")
    replacements = {
        "PhotonEnergy": f"{photon_mev:g}",
        "EphotonMinSelfConsistent": f"{max(photon_mev - 5, 1):g}",
        "EphotonMaxSelfConsistent": f"{photon_mev + 5:g}",
        "OverlapFactor": f"{overlap:g}",
        "CavityLosses": f"{modal_loss:g}",
    }
    for key, value in replacements.items():
        text = replace_first(
            text,
            rf"(?m)^(\s*{key}\s*=\s*)[0-9.]+",
            rf"\g<1>{value}",
        )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 mode competition, '
            f'{wavelength_um:.2f} um, corrected waveguide, 216.384 mV."'
        ),
    )
    output = ROOT / "designs" / f"sun2022_mode_competition_{name}.negf"
    output.write_text(text, encoding="utf-8")
    print(output)
    return output


def make_coherence_case(
    periods: int,
    *,
    energy_grid: float = 5.0,
    axial_range: float = 550.0,
    energy_plots: bool = True,
    suffix: str = "",
) -> Path:
    text = CLAMP_TEMPLATE.read_text(encoding="utf-8", errors="ignore")
    text = replace_first(
        text,
        r"(?m)^(\s*CoherenceLengthInPeriods\s*=\s*)\d+",
        rf"\g<1>{periods}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*CoherenceLengthInNm\s*=\s*)[0-9.]+",
        rf"\g<1>{45.08 * periods:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyGridSpacing\s*=\s*)[0-9.]+",
        rf"\g<1>{energy_grid:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyRangeAxial\s*=\s*)[0-9.]+",
        rf"\g<1>{axial_range:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedPlots\s*=\s*)\w+",
        rf"\g<1>{'yes' if energy_plots else 'no'}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 10.33-um fixed mode, '
            f'coherence={periods} periods, 216.384 mV."'
        ),
    )
    output = (
        ROOT / "designs" / f"sun2022_coherence_{periods}p{suffix}_10p33.negf"
    )
    output.write_text(text, encoding="utf-8")
    print(output)
    return output


def make_fine_gain_case() -> Path:
    text = BASE_NEGF.read_text(encoding="utf-8", errors="ignore")
    text = set_single_bias(text, DESIGN_BIAS)
    text = replace_first(
        text,
        r"(?m)^(\s*dEPhotSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>2",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMinSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>110",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMaxSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>130",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedGain\s*=\s*)\w+",
        r"\g<1>no",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 fine gain spectrum, 110-130 meV, '
            '2 meV spacing, 216.384 mV."'
        ),
    )
    output = ROOT / "designs/sun2022_fine_gain_110_130_216p384.negf"
    output.write_text(text, encoding="utf-8")
    print(output)
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyGridSpacing\s*=\s*)[0-9.]+",
        r"\g<1>2",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*dEPhotSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>1",
    )
    fine_output = ROOT / "designs/sun2022_fine_gain_110_130_216p384_2meV.negf"
    fine_output.write_text(text, encoding="utf-8")
    print(fine_output)
    return output


def make_coherence_gain_case(periods: int) -> Path:
    text = BASE_NEGF.read_text(encoding="utf-8", errors="ignore")
    text = set_single_bias(text, DESIGN_BIAS)
    text = replace_first(
        text,
        r"(?m)^(\s*CoherenceLengthInPeriods\s*=\s*)\d+",
        rf"\g<1>{periods}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*CoherenceLengthInNm\s*=\s*)[0-9.]+",
        rf"\g<1>{45.08 * periods:g}",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyGridSpacing\s*=\s*)[0-9.]+",
        r"\g<1>10",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyRangeAxial\s*=\s*)[0-9.]+",
        r"\g<1>500",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedPlots\s*=\s*)\w+",
        r"\g<1>no",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EnergyResolvedGain\s*=\s*)\w+",
        r"\g<1>no",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMinSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>120",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*EphotonMaxSelfConsistent\s*=\s*)[0-9.]+",
        r"\g<1>120",
    )
    text = replace_first(
        text,
        r"(?m)^(\s*Content\s*=\s*)\".*\"",
        (
            r'\g<1>"Sun 2022 zero-field gain check, '
            f'coherence={periods} periods, 216.384 mV."'
        ),
    )
    output = ROOT / "designs" / f"sun2022_coherence_gain_{periods}p.negf"
    output.write_text(text, encoding="utf-8")
    print(output)
    return output


def main() -> None:
    make_sensitivity_case("well_minus_010", well_delta_nm=-0.10)
    make_sensitivity_case("well_plus_010", well_delta_nm=0.10)
    make_sensitivity_case("barrier_minus_010", barrier_delta_nm=-0.10)
    make_sensitivity_case("barrier_plus_010", barrier_delta_nm=0.10)
    make_sensitivity_case("composition_minus_001", composition_delta=-0.01)
    make_sensitivity_case("composition_plus_001", composition_delta=0.01)
    make_sensitivity_case("doping_minus_20pct", doping_scale=0.8)
    make_sensitivity_case("doping_plus_20pct", doping_scale=1.2)
    make_sensitivity_case("ifr_high_012", ifr_amplitude=0.12)
    make_sensitivity_case("alloy_low_004", alloy_strength=0.04)
    make_sensitivity_case("alloy_high_008", alloy_strength=0.08)

    for temperature in (293, 313, 333, 353):
        make_temperature_case(temperature)

    make_mode_case(
        "10p16um",
        photon_mev=122.0,
        wavelength_um=10.16,
        overlap=0.712,
        modal_loss=2.246,
    )
    make_mode_case(
        "9p92um",
        photon_mev=125.0,
        wavelength_um=9.92,
        overlap=0.719,
        modal_loss=2.238,
    )
    make_mode_case(
        "10p78um",
        photon_mev=115.0,
        wavelength_um=10.78,
        overlap=0.6887,
        modal_loss=2.257,
    )
    make_coherence_case(2)
    make_coherence_case(3)
    make_coherence_case(
        2,
        energy_grid=10.0,
        axial_range=500.0,
        energy_plots=False,
        suffix="_reduced",
    )
    make_coherence_case(
        3,
        energy_grid=10.0,
        axial_range=500.0,
        energy_plots=False,
        suffix="_reduced",
    )
    make_coherence_gain_case(2)
    make_coherence_gain_case(3)
    make_fine_gain_case()


if __name__ == "__main__":
    main()
