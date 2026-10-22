# -*- coding: utf-8 -*-
"""Generate the Liu low-doping case with official Bai polarization flags."""
from pathlib import Path


BASE = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\liu2022_dau_240mV_lowdoping.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\liu2022_dau_240mV_lowdoping_piezo.negf"
)


def main():
    text = BASE.read_text(encoding="utf-8")
    text = text.replace(
        'Content = "Liu 2022 at 240 mV. Low-doping diagnostic: '
        '6.7e16 per cm3 over 10.5 nm."',
        'Content = "Liu 2022 at 240 mV and 7.0e10 per cm2. '
        'Piezoelectricity and pyroelectricity enabled for calibration."',
    )
    text = text.replace("Piezoelectricity = no", "Piezoelectricity = yes")
    text = text.replace("Pyroelectricity = no", "Pyroelectricity = yes")
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
