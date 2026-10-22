# -*- coding: utf-8 -*-
"""Create a clamped 9 um variant from the Sun 2022 low-scattering case."""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_lowscatter.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_lowscatter_clamp.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        "Sun 2022 MOCVD 9 um low-scattering calibration, Delta 0.04 nm, Lambda 10 nm, alloy strength 0.1.",
        "Sun 2022 MOCVD 9 um clamped test at 137.8 meV, cavity loss 3 per cm, overlap 0.5.",
    )
    text = text.replace(
        "        EphotonMinSelfConsistent = 120\n"
        "        EphotonMaxSelfConsistent = 155",
        "        EphotonMinSelfConsistent = 132\n"
        "        EphotonMaxSelfConsistent = 144",
    )
    text = text.replace(
        "        Vmax = 260\n\n        FermiGoldenRule{",
        "        Vmax = 260\n"
        "        CavityLosses = 3.0\n"
        "        OverlapFactor = 0.5\n"
        "        GainClamping = yes\n\n"
        "        FermiGoldenRule{",
    )
    marker = "\n    Gain{"
    photon_block = (
        "\n    EMfield{\n"
        "        EMmode{\n"
        "            PhotonEnergy = 137.8\n"
        "            ElectricField = 0.0\n"
        "        }\n"
        "    }\n"
    )
    position = text.rfind(marker)
    if position < 0:
        raise RuntimeError("Could not locate Gain block")
    text = text[:position] + photon_block + text[position:]
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
