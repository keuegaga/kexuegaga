"""Render selected pages from a PDF using the bundled Poppler runtime."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    bundled = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native"
        / "poppler/Library/bin"
        / f"{name}.exe"
    )
    if bundled.exists():
        return str(bundled)
    raise FileNotFoundError(f"{name} was not found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output_prefix", type=Path)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, default=0)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    if args.pdf.is_dir():
        candidates = sorted(
            args.pdf.glob("*9um*MOCVD*.pdf"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError(f"No matching PDF in {args.pdf}")
        args.pdf = candidates[0]

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    command = [
        tool("pdftoppm"),
        "-png",
        "-r",
        str(args.dpi),
        "-f",
        str(args.first),
    ]
    if args.last:
        command.extend(["-l", str(args.last)])
    command.extend([str(args.pdf), str(args.output_prefix)])
    subprocess.run(command, check=True)
    print(f"Rendered to {args.output_prefix}-*.png")


if __name__ == "__main__":
    main()
