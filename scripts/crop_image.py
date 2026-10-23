"""Crop a raster image with an explicit left, top, right, bottom box."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("box", nargs=4, type=int, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()

    image = Image.open(args.source)
    cropped = image.crop(tuple(args.box))
    if args.scale != 1.0:
        cropped = cropped.resize(
            (round(cropped.width * args.scale), round(cropped.height * args.scale)),
            Image.Resampling.LANCZOS,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(args.output)
    print(f"Saved {args.output} ({cropped.width} x {cropped.height})")


if __name__ == "__main__":
    main()
