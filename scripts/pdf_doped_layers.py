# -*- coding: utf-8 -*-
"""Try to recover which layer numbers are underlined (= doped) in the Fei 2021 PDF.

Renders the layer-sequence lines at high DPI and, for every number token, measures
the dark-pixel coverage in the narrow band just below the glyph baseline.  A real
underline produces a continuous dark run across the token width; ordinary letters
leave that band clean.

Usage:
    python scripts/pdf_doped_layers.py <pdf_path>
"""
import sys

import numpy as np
import pdfplumber
import pypdfium2 as pdfium


def main():
    pdf_path = sys.argv[1]
    page_no = 3
    dpi = 600
    scale = dpi / 72.0

    doc = pdfium.PdfDocument(pdf_path)
    img = np.array(doc[page_no - 1].render(scale=scale).to_pil().convert("L"))
    print(f"rendered page {page_no} at {dpi} dpi -> {img.shape}")

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no - 1]
        chars = page.chars
        seq = "".join(c["text"] for c in chars)
        idx = seq.find("are as follows")
        top0 = chars[idx]["top"]
        band = [c for c in chars if top0 - 3 < c["top"] < top0 + 40]

    lines = {}
    for c in band:
        lines.setdefault(round(c["top"]), []).append(c)

    counter = 0
    print("\n n   number   font          underline coverage   verdict")
    for _, items in sorted(lines.items()):
        items.sort(key=lambda c: c["x0"])
        text = "".join(c["text"] for c in items)
        if not any(ch.isdigit() for ch in text):
            continue
        token = []
        for c in items + [None]:
            is_sep = c is None or c["text"] == "/"
            if not is_sep:
                token.append(c)
                continue
            if not token:
                continue
            num = "".join(t["text"] for t in token)
            if any(ch.isdigit() for ch in num):
                counter += 1
                x0 = min(t["x0"] for t in token) * scale
                x1 = max(t["x1"] for t in token) * scale
                bottom = max(t["bottom"] for t in token) * scale
                best, best_off = 0.0, 0
                for off in range(2, 18):
                    row = img[int(bottom + off):int(bottom + off) + 2,
                              int(x0):int(x1) + 1]
                    if row.size == 0:
                        continue
                    frac = float((row < 140).all(axis=0).mean())
                    if frac > best:
                        best, best_off = frac, off
                bold = "BOLD" if "Bold" in token[0]["fontname"] else "roman"
                verdict = "UNDERLINED" if best > 0.75 else ("partial" if best > 0.4 else "-")
                print(f"{counter:3d}  {num:>6s}   {bold:<10s}  {best:5.2f} (at +{best_off:2d}px)   {verdict}")
            token = []


if __name__ == "__main__":
    main()
