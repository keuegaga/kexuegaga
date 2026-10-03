# -*- coding: utf-8 -*-
"""Detect underlined numbers by rendering the PDF page and looking for dark pixels
just below each number's bounding box.

Usage:
    python scripts/pdf_underline_pixels.py <pdf_path> <page_no_1based> <search_phrase>
"""
import sys

import numpy as np
import pdfplumber
import pypdfium2 as pdfium
from PIL import Image


def main():
    pdf_path = sys.argv[1]
    page_no = int(sys.argv[2])
    phrase = sys.argv[3]
    dpi = 400
    scale = dpi / 72.0

    pdf = pdfium.PdfDocument(pdf_path)
    page_img: Image.Image = pdf[page_no - 1].render(scale=scale).to_pil().convert("L")
    arr = np.array(page_img)
    print(f"rendered page {page_no} at {dpi} dpi -> {arr.shape}")

    with pdfplumber.open(pdf_path) as pl:
        page = pl.pages[page_no - 1]
        chars = page.chars
        seq = "".join(c["text"] for c in chars)
        i = seq.find(phrase)
        if i < 0:
            raise SystemExit("phrase not found")
        top0 = chars[i]["top"]
        band = sorted([c for c in chars if top0 - 2 < c["top"] < top0 + 40],
                      key=lambda c: (round(c["top"]), c["x0"]))

    # split the char stream into tokens at '/' boundaries
    lines = {}
    for c in band:
        lines.setdefault(round(c["top"]), []).append(c)
    for _, items in sorted(lines.items()):
        items.sort(key=lambda c: c["x0"])
        print("line:", "".join(c["text"] for c in items))
        token = []
        for c in items + [None]:
            if c is None or c["text"] == "/":
                if token:
                    text = "".join(t["text"] for t in token)
                    x0 = min(t["x0"] for t in token) * scale
                    x1 = max(t["x1"] for t in token) * scale
                    bot = max(t["bottom"] for t in token) * scale
                    best = 0.0
                    best_row = None
                    for off in range(1, 26):
                        row = arr[int(bot + off):int(bot + off) + 1,
                                  int(x0):int(x1) + 1]
                        if row.size == 0:
                            continue
                        frac = float((row[0] < 128).mean())
                        if frac > best:
                            best, best_row = frac, off
                    print(f"   {text:>6s}  max dark coverage below = {best:5.2f}"
                          f" (at +{best_row} px)"
                          + ("   <== UNDERLINED" if best > 0.8 else ""))
                    token = []
            else:
                token.append(c)


if __name__ == "__main__":
    main()
