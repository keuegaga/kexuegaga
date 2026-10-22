# -*- coding: utf-8 -*-
"""Generate a low-scattering calibration variant of the Sun 2022 NEGF case."""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_fgr.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_lowscatter.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        "Sun 2022 MOCVD 9 um DAU MS QCL, 216.384 mV per period, 300 K, FGR diagnostic.",
        "Sun 2022 MOCVD 9 um low-scattering calibration, Delta 0.04 nm, Lambda 10 nm, alloy strength 0.1.",
    )
    text = text.replace("AmplitudeInZ = 0.08", "AmplitudeInZ = 0.04")
    text = text.replace("CorrelationLengthInXY = 7.0", "CorrelationLengthInXY = 10.0")
    text = text.replace("AlloyScatteringStrength = 1.0", "AlloyScatteringStrength = 0.1")
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
