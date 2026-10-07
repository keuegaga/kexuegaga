# -*- coding: utf-8 -*-
"""Generate a nextnano++ input file for the Fei 2021 QCL with graded interfaces.

Model: every abrupt interface is replaced by a 0.3 nm digital-alloy grade made of
two 0.15 nm quaternary AlGaInAs sub-layers at 1/3 and 2/3 of the composition step.
Each layer is shortened by 0.15 nm at both ends so the period stays 57.3 nm.

Usage:
    python scripts/gen_graded_nnp.py <outfile.nnp> [grading_nm] [field_V_per_m] [num_periods]
"""
import sys

# (type, thickness_nm); "B" = AlInAs barrier, "W" = InGaAs well
LAYERS = [
    ("B", 4.0), ("W", 1.3), ("B", 1.0), ("W", 5.2), ("B", 0.9), ("W", 5.1),
    ("B", 1.0), ("W", 4.7), ("B", 1.6), ("W", 3.6), ("B", 2.2), ("W", 2.9),
    ("B", 1.8), ("W", 2.7), ("B", 1.9), ("W", 2.6), ("B", 2.0), ("W", 2.4),
    ("B", 2.5), ("W", 2.5), ("B", 3.1), ("W", 2.3),
]

AL_BARRIER = 0.48      # Al fraction in Al0.48In0.52As
GA_WELL = 0.47         # Ga fraction in In0.53Ga0.47As


def comp(kind):
    """(Al, Ga) fractions of the two endpoint materials."""
    return (AL_BARRIER, 0.0) if kind == "B" else (0.0, GA_WELL)


def material_block(kind, indent):
    pad = " " * indent
    if kind == "B":
        return f'{pad}ternary_constant{{ name = "Al(x)In(1-x)As"  alloy_x = {AL_BARRIER} }}\n'
    return f'{pad}ternary_constant{{ name = "In(x)Ga(1-x)As"  alloy_x = {1 - GA_WELL:.2f} }}\n'


def quaternary_block(al, ga, indent):
    pad = " " * indent
    inn = 1.0 - al - ga
    return (f'{pad}quaternary_constant{{ name = "Al(x)Ga(y)In(1-x-y)As"  '
            f'alloy_x = {al:.6f}  alloy_y = {ga:.6f} }}\n')


def main():
    out = sys.argv[1]
    grade = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
    field = float(sys.argv[3]) if len(sys.argv) > 3 else -50e5
    nper = int(sys.argv[4]) if len(sys.argv) > 4 else 3

    # optional per-layer thickness deltas, e.g. "0,0,0,0.2,0,0.2,0,0.2,..."
    layers = list(LAYERS)
    if len(sys.argv) > 5 and sys.argv[5].strip():
        deltas = [float(v) for v in sys.argv[5].split(",")]
        if len(deltas) != len(layers):
            raise SystemExit(f"need {len(layers)} deltas, got {len(deltas)}")
        layers = [(k, t + d) for (k, t), d in zip(layers, deltas)]

    period = sum(t for _, t in layers)
    half = grade / 2.0
    total = period * nper

    # cumulative interface positions inside one period
    cum = [0.0]
    for _, t in layers:
        cum.append(cum[-1] + t)

    lines = []
    lines.append("!TEXT\n")
    lines.append("    Fei 2021 QCL with graded interfaces (digital-alloy grade)\n")
    lines.append(f"    grading width = {grade} nm, period = {period:.1f} nm, {nper} periods\n")
    lines.append(f"    interface grade approximated by two quaternary sub-layers of {half} nm\n")
    lines.append("!ENDTEXT\n\n")
    lines.append(f"$electric_field = {field}\n")
    lines.append("$num_electrons   = 60\n")
    lines.append(f"$period          = {period}\n")
    lines.append(f"$num_periods     = {nper}\n\n")
    lines.append("run{ quantum{ } }\n")
    lines.append("output{ material_parameters{ } }\n\n")
    lines.append('global{\n    simulate1D{ }\n'
                 '    crystal_zb{ x_hkl = [1,0,0]  y_hkl = [0,1,0] }\n'
                 '    substrate{ name = "InP" }\n    temperature = 300.0\n}\n\n')
    lines.append('contacts{ fermi{ name = "fermi_zero"  bias = 0.0 } }\n\n')
    lines.append("structure{\n    output_material_index{ }\n    output_region_index{ }\n")
    lines.append('    region{\n        everywhere{ }\n'
                 '        ternary_constant{ name = "In(x)Ga(1-x)As"  alloy_x = 0.53 }\n'
                 '        contact{ name = fermi_zero }\n    }\n')

    boundaries = set()
    for i, (kind, t) in enumerate(layers):
        a = cum[i] + half
        b = cum[i + 1] - half
        boundaries.update((a, b))
        lines.append(f"    region{{  # layer {i+1}: {kind} {t} nm core\n")
        lines.append(f"        line{{ x = [{a:.3f}, {b:.3f}] }}\n")
        lines.append(material_block(kind, 8))
        lines.append(f"        array_x{{ max = $num_periods  shift = $period }}\n    }}\n")

        nxt = layers[(i + 1) % len(layers)][0]
        c0 = comp(kind)
        c1 = comp(nxt)
        a_ramp = cum[i + 1] - half
        b_ramp = cum[i + 1] + half
        m = (b_ramp - a_ramp) / 2.0
        boundaries.update((a_ramp, a_ramp + m, b_ramp))
        for s, (p, q) in ((1.0 / 3.0, (a_ramp, a_ramp + m)), (2.0 / 3.0, (a_ramp + m, b_ramp))):
            al = (1 - s) * c0[0] + s * c1[0]
            ga = (1 - s) * c0[1] + s * c1[1]
            lines.append(f"    region{{  # interface grade {i+1}->{i+2}, step {s:.2f}\n")
            lines.append(f"        line{{ x = [{p:.3f}, {q:.3f}] }}\n")
            lines.append(quaternary_block(al, ga, 8))
            lines.append(f"        array_x{{ max = $num_periods  shift = $period }}\n    }}\n")

    lines.append("    output_alloy_composition{ }\n}\n\n")

    grid = sorted(b + k * period for k in range(nper + 1) for b in boundaries)
    lines.append("grid{\n    xgrid{\n")
    prev = None
    for g in grid:
        if g < -1e-9 or g > total + 1e-9:
            continue
        if prev is not None and g - prev < 1e-6:
            continue
        lines.append(f"        line{{ pos = {g:.3f}  spacing = 0.2 }}\n")
        prev = g
    lines.append("    }\n}\n\n")

    lines.append('classical{\n    Gamma{ }\n    L{ }\n    X{ }\n    HH{ }\n    LH{ }\n    SO{ }\n'
                 '    output_bandedges{ averaged = no }\n    output_bandgap{ }\n}\n\n')
    lines.append('poisson{\n    electric_field{\n        strength            = $electric_field\n'
                 '        reference_potential = 0.0\n    }\n'
                 '    output_potential{ }\n    output_electric_field{ }\n}\n\n')
    lines.append('quantum{\n    region{\n        name = "quantum_region"\n'
                 f'        x = [0.0, {total:.1f}]\n        no_density = yes\n'
                 '        boundary{ x = dirichlet }\n'
                 '        kp_8band{ num_electrons = $num_electrons }\n'
                 '        transition_energies{ KP8{ } }\n'
                 '        output_wavefunctions{ max_num = 200  all_k_points = yes  amplitudes = no  probabilities = yes }\n'
                 '        momentum_matrix_elements{ polarization{ name = "component_x"  re = [1,0,0] }  KP8{ } }\n'
                 '        dipole_moment_matrix_elements{ polarization{ name = "component_x"  re = [1,0,0] }  KP8{ }\n'
                 '            output_matrix_elements = yes  output_oscillator_strengths = yes }\n    }\n}\n')

    with open(out, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))
    print(f"written {out}: period {period:.1f} nm, grading {grade} nm, "
          f"{len(layers)*2} regions per period, grid points {len(grid)}")


if __name__ == "__main__":
    main()
