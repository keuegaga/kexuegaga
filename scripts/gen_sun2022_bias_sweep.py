# -*- coding: utf-8 -*-
"""Generate a low-bias diagnostic sweep for the standard Sun 2022 model."""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_fgr.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_bias_180_220.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        "Sun 2022 MOCVD 9 um DAU MS QCL, 216.384 mV per period, 300 K, FGR diagnostic.",
        "Sun 2022 MOCVD 9 um standard-scattering bias sweep 180, 200, 220 mV.",
    )
    text = text.replace(
        "        Min = 216.384\n"
        "        Max = 216.384\n"
        "        Delta = 10",
        "        Min = 180\n"
        "        Max = 220\n"
        "        Delta = 20",
    )
    text = text.replace(
        "        EphotonMinSelfConsistent = 120\n"
        "        EphotonMaxSelfConsistent = 155",
        "        EphotonMinSelfConsistent = 105\n"
        "        EphotonMaxSelfConsistent = 145",
    )
    text = text.replace("        BiasForInitialElectronicModes = 216.384",
                        "        BiasForInitialElectronicModes = 200")
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
