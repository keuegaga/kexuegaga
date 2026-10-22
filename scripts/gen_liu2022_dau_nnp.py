# -*- coding: utf-8 -*-
"""Generate nextnano++ k.p inputs for the Liu 2022 dual-upper-state QCL.

Reference structure:
  Y. Liu et al., Opt. Express 30, 2022, DOI 10.1364/OE.472942.
  Strain-compensated In0.60Ga0.40As / Al0.58In0.42As, 22 layers.
  Published field: 48 kV/cm.

The paper's sequence is in angstrom, starting from the injection barrier.
Odd-numbered entries (1-based) are barriers and even-numbered entries are
wells.  This generator keeps the full period and can widen selected wells
for a controlled wavelength scan.

Usage:
  python scripts/gen_liu2022_dau_nnp.py --name base_f48 --field-kvcm 48
  python scripts/gen_liu2022_dau_nnp.py --name red_03 --field-kvcm 48 \
      --widen 2:0.3 4:0.3 6:0.3 8:0.3
"""
import argparse
from pathlib import Path


LAYERS_A = [
    38, 24, 27, 61, 9, 49, 11, 45, 12, 37, 15,
    32, 16, 31, 19, 29, 22, 29, 25, 28, 29, 26,
]


def parse_widen(items):
    widen = {}
    for item in items or []:
        layer_text, width_text = item.split(":", 1)
        layer = int(layer_text)
        if layer < 2 or layer > len(LAYERS_A) or layer % 2:
            raise ValueError(f"layer {layer} is not a well layer")
        widen[layer] = widen.get(layer, 0.0) + float(width_text)
    return widen


def calculate_layout(widen):
    layers_nm = [value / 10 for value in LAYERS_A]
    for layer, delta in widen.items():
        layers_nm[layer - 1] += delta

    x = 0.0
    barriers = []
    layer_rows = []
    for index, width in enumerate(layers_nm, start=1):
        start, end = x, x + width
        kind = "B" if index % 2 else "W"
        if kind == "B":
            barriers.append((index, start, end))
        layer_rows.append((index, kind, width, start, end))
        x = end
    return layers_nm, barriers, layer_rows, x


def format_regions(barriers, periods):
    lines = []
    for index, start, end in barriers:
        lines.extend([
            f"    region{{  # barrier layer {index}",
            f"        line{{ x = [{start:.4f}, {end:.4f}] }}",
            '        ternary_constant{ name = "Al(x)In(1-x)As" alloy_x = 0.58 }',
            f"        array_x{{ max = {periods} shift = $period }}",
            "    }",
        ])
    return "\n".join(lines)


def format_grid(barriers, period, periods):
    positions = [0.0]
    for _, start, end in barriers:
        positions.extend([start, end])
    positions.append(period)
    positions.extend(period * n for n in range(2, periods + 1))
    seen = set()
    lines = []
    for pos in positions:
        key = round(pos, 4)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"        line{{ pos = {pos:.4f} spacing = 0.2 }}")
    return "\n".join(lines)


NNP_TEMPLATE = r"""!TEXT
    Liu et al., Opt. Express 30 (2022), DOI 10.1364/OE.472942
    Dual-upper-state QCL, strain-compensated In0.60Ga0.40As/Al0.58In0.42As.
    Case: {name}; field: {field:.1f} kV/cm.
    Barrier layers are B, well layers are W. Well-widening: {widen_text}
!ENDTEXT

$electric_field = -{field_vm:.6g}
$period = {period:.4f}
$num_periods = {periods}
$num_electrons = {num_electrons}

run{{
    strain{{ }}
    quantum{{ }}
}}

output{{
    material_parameters{{ }}
}}

global{{
    simulate1D{{ }}
    crystal_zb{{
        x_hkl = [1, 0, 0]
        y_hkl = [0, 1, 0]
    }}
    substrate{{ name = "InP" }}
    temperature = 300.0
}}

contacts{{
    fermi{{
        name = "fermi_zero"
        bias = 0.0
    }}
}}

structure{{
    output_material_index{{ }}
    output_region_index{{ }}

    region{{
        everywhere{{ }}
        ternary_constant{{
            name = "In(x)Ga(1-x)As"
            alloy_x = 0.60
        }}
        contact{{ name = "fermi_zero" }}
    }}

{regions}

    output_alloy_composition{{ }}
}}

grid{{
    xgrid{{
{grid}
    }}
}}

classical{{
    Gamma{{ }}
    L{{ }}
    X{{ }}
    HH{{ }}
    LH{{ }}
    SO{{ }}
    output_bandedges{{ averaged = no }}
    output_bandgap{{ }}
}}

strain{{
    pseudomorphic_strain{{ }}
    output_strain_tensor{{ }}
    output_hydrostatic_strain{{ }}
}}

poisson{{
    electric_field{{
        strength = $electric_field
        reference_potential = 0.0
    }}
    output_potential{{ }}
    output_electric_field{{ }}
}}

quantum{{
    region{{
        name = "quantum_region"
        x = [0.0, {total_length:.4f}]
        no_density = yes
        boundary{{ x = dirichlet }}

        kp_8band{{
            num_electrons = $num_electrons
            avoid_spurious = yes
        }}

        transition_energies{{ KP8{{ }} }}

        output_wavefunctions{{
            max_num = 240
            all_k_points = yes
            amplitudes = no
            probabilities = yes
        }}

        momentum_matrix_elements{{
            polarization{{ name = "component_x" re = [1, 0, 0] }}
            KP8{{ }}
        }}
        dipole_moment_matrix_elements{{
            polarization{{ name = "component_x" re = [1, 0, 0] }}
            KP8{{ }}
            output_matrix_elements = yes
            output_oscillator_strengths = yes
        }}
    }}
}}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--field-kvcm", type=float, default=48.0)
    parser.add_argument("--periods", type=int, default=3)
    parser.add_argument("--num-electrons", type=int, default=100)
    parser.add_argument(
        "--widen", action="append", default=[],
        help="well layer and added width in nm, e.g. 4:0.3; repeatable",
    )
    parser.add_argument(
        "--out-dir", default="designs",
        help="directory for the generated .nnp file",
    )
    args = parser.parse_args()

    widen = parse_widen(args.widen)
    _, barriers, rows, period = calculate_layout(widen)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    widen_text = ", ".join(
        f"L{layer}+{delta:.2f}nm" for layer, delta in sorted(widen.items())
    ) or "none"
    source = NNP_TEMPLATE.format(
        name=args.name,
        field=args.field_kvcm,
        field_vm=args.field_kvcm * 1e5,
        period=period,
        periods=args.periods,
        num_electrons=args.num_electrons,
        regions=format_regions(barriers, args.periods),
        grid=format_grid(barriers, period, args.periods),
        total_length=period * args.periods,
        widen_text=widen_text,
    )

    nnp_path = out_dir / f"liu2022_dau_{args.name}.nnp"
    csv_path = out_dir / f"liu2022_dau_{args.name}_layers.csv"
    nnp_path.write_text(source, encoding="utf-8")
    csv_path.write_text(
        "layer,type,material,thickness_nm,start_nm,end_nm\n"
        + "\n".join(
            f"{idx},{kind},"
            f"{'Al0.58In0.42As' if kind == 'B' else 'In0.60Ga0.40As'},"
            f"{width:.4f},{start:.4f},{end:.4f}"
            for idx, kind, width, start, end in rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(nnp_path)
    print(csv_path)
    print(f"period_nm={period:.4f}")


if __name__ == "__main__":
    main()
