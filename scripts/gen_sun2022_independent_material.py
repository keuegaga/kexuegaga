# -*- coding: utf-8 -*-
"""Generate an independent-material parameter variant for Sun 2022.

Reference for the close-composition parameter set:
Bugajski et al., Photonics 11, 1195 (2024), DOI 10.3390/photonics11121195.
Values used here: m_well=0.043 m0, m_barrier=0.089 m0, CBO=0.773 eV.
"""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_fgr.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_independent_material.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        "Sun 2022 MOCVD 9 um DAU MS QCL, 216.384 mV per period, 300 K, FGR diagnostic.",
        "Sun 2022 independent material baseline: mwell 0.043, mbarrier 0.089, CBO 0.773 eV.",
    )
    text = text.replace(
        "            EffectiveMassFromKpParameters = no\n"
        "            Overwrite{ ConductionBandOffset = 0.0 }",
        "            EffectiveMassFromKpParameters = no\n"
        "            Overwrite{\n"
        "                ConductionBandOffset = 0.0\n"
        "                ElectronMass = 0.043\n"
        "            }",
    )
    text = text.replace(
        "            EffectiveMassFromKpParameters = no\n"
        "            Overwrite{ ConductionBandOffset = 0.81 }",
        "            EffectiveMassFromKpParameters = no\n"
        "            Overwrite{\n"
        "                ConductionBandOffset = 0.773\n"
        "                ElectronMass = 0.089\n"
        "            }",
    )
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
