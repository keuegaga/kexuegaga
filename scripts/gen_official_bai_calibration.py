# -*- coding: utf-8 -*-
"""Create a single-bias copy of nextnano's official Bai APL 2011 case."""
import re
from pathlib import Path


SOURCE = Path(
    r"C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\examples"
    r"\MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf"
)
OUTPUT = Path(
    r"D:\Codex-Obsidian\QCL-nextnano\designs"
    r"\bai2011_official_360mV_calibration.negf"
)


def main():
    text = SOURCE.read_text(encoding="utf-8", errors="ignore")
    text, count = re.subn(
        r"(SweepParameters\s*\{.*?Min\s*=\s*)280(.*?Max\s*=\s*)420",
        r"\g<1>360\g<2>360",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not replace the official sweep limits")

    header = (
        "!TEXT\n"
        "Single-bias calibration copy of nextnano's official input\n"
        "MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf.\n"
        "Only the sweep was changed from 280:420 to the known lasing point 360 mV.\n"
        "!ENDTEXT\n\n"
    )
    OUTPUT.write_text(header + text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
