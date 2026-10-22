# -*- coding: utf-8 -*-
"""Generate a physically constrained IFR-only variant for Sun 2022."""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_fgr.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\sun2022_mocvd_9um_ifr004.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        "Sun 2022 MOCVD 9 um DAU MS QCL, 216.384 mV per period, 300 K, FGR diagnostic.",
        "Sun 2022 MOCVD 9 um IFR-only sensitivity test: 0.04 nm, standard alloy strength 1.0.",
    )
    text = text.replace("AmplitudeInZ = 0.08", "AmplitudeInZ = 0.04")
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
