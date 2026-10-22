# -*- coding: utf-8 -*-
"""Generate nextnano++ k.p input for the Sun 2022 9 um MOCVD QCL."""
from pathlib import Path


PERIOD_LAYERS_NM = [
    2.80, 3.00, 1.25, 6.27, 1.00, 5.35, 0.88, 4.85,
    1.09, 4.16, 1.22, 3.66, 1.42, 3.15, 1.68, 3.30,
]
PERIOD_NM = sum(PERIOD_LAYERS_NM)
FIELD_KV_CM = 48.0
PERIODS = 3
ELECTRONS = 100


def layout():
    x = 0.0
    barriers = []
    rows = []
    for index, width in enumerate(PERIOD_LAYERS_NM, start=1):
        kind = "B" if index % 2 else "W"
        material = "Al0.638In0.362As" if kind == "B" else "In0.593Ga0.407As"
        if kind == "B":
            barriers.append((index, x, x + width))
        rows.append((index, kind, material, width, x, x + width))
        x += width
    return barriers, rows


def region_block(barriers):
    out = []
    for index, start, end in barriers:
        out.extend([
            f"    region{{  # barrier layer {index}",
            f"        line{{ x = [{start:.4f}, {end:.4f}] }}",
            '        ternary_constant{ name = "Al(x)In(1-x)As" alloy_x = 0.638 }',
            f"        array_x{{ max = {PERIODS} shift = $period }}",
            "    }",
        ])
    return "\n".join(out)


def grid_block(barriers):
    positions = [0.0]
    for _, start, end in barriers:
        positions.extend([start, end])
    positions.extend([PERIOD_NM * n for n in range(1, PERIODS + 1)])
    seen = set()
    lines = []
    for pos in positions:
        key = round(pos, 4)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"        line{{ pos = {pos:.4f} spacing = 0.2 }}")
    return "\n".join(lines)


TEMPLATE = r"""!TEXT
    Sun et al., Opt. Express 30 (2022), DOI 10.1364/OE.469573.
    Nine-micron MOCVD DAU/MS QCL, 50 stages.
    Well In0.593Ga0.407As; barrier Al0.638In0.362As.
    One period = {period:.4f} nm; field = {field:.1f} kV/cm.
    B = barrier, W = well in the accompanying CSV.
!ENDTEXT

$electric_field = -{field_vm:.7g}
$period = {period:.4f}
$num_periods = {periods}
$num_electrons = {electrons}

run{{
    strain{{ }}
    quantum{{ }}
}}

output{{ material_parameters{{ }} }}

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
            alloy_x = 0.593
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
    root = Path(r"D:\Codex-Obsidian\QCL-nextnano")
    designs = root / "designs"
    barriers, rows = layout()
    source = TEMPLATE.format(
        period=PERIOD_NM,
        field=FIELD_KV_CM,
        field_vm=FIELD_KV_CM * 1e5,
        periods=PERIODS,
        electrons=ELECTRONS,
        regions=region_block(barriers),
        grid=grid_block(barriers),
        total_length=PERIOD_NM * PERIODS,
    )
    nnp = designs / "sun2022_mocvd_9um_f48.nnp"
    csv = designs / "sun2022_mocvd_9um_f48_layers.csv"
    nnp.write_text(source, encoding="utf-8")
    csv.write_text(
        "layer,type,material,thickness_nm,start_nm,end_nm,doped\n"
        + "\n".join(
            f"{idx},{kind},{mat},{width:.4f},{start:.4f},{end:.4f},"
            f"{'yes' if idx in (13, 14) else 'no'}"
            for idx, kind, mat, width, start, end in rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(nnp)
    print(csv)
    print(f"period={PERIOD_NM:.4f} nm, bias={0.0048 * PERIOD_NM * 1000:.4f} mV")


if __name__ == "__main__":
    main()
