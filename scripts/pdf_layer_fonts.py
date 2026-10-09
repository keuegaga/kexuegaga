# -*- coding: utf-8 -*-
"""Print every number of the Fei 2021 layer sequence together with its font,
so the barrier (bold) / well (roman) pattern can be verified layer by layer.

Usage:
    python scripts/pdf_layer_fonts.py <pdf_path>
"""
import sys

import pdfplumber


def main():
    pdf_path = sys.argv[1]
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            chars = page.chars
            seq = "".join(c["text"] for c in chars)
            idx = seq.find("are as follows")
            if idx < 0:
                continue
            print(f"--- page {pno} ---")
            top0 = chars[idx]["top"]
            # take the two/three text lines that contain the sequence
            band = [c for c in chars if top0 - 3 < c["top"] < top0 + 40]
            lines = {}
            for c in band:
                lines.setdefault(round(c["top"]), []).append(c)
            n = 0
            for _, items in sorted(lines.items()):
                items.sort(key=lambda c: c["x0"])
                text = "".join(c["text"] for c in items)
                if not any(ch.isdigit() for ch in text):
                    continue
                print("line:", text)
                token, font = [], None
                for c in items + [None]:
                    if c is not None and c["text"] not in ("/",) and c["text"] != " ":
                        if font is None:
                            font = c["fontname"]
                        if c["fontname"] != font:
                            if token:
                                n += 1
                                num = "".join(t["text"] for t in token)
                                kind = "BOLD(barrier)" if "Bold" in font else "roman(well)"
                                print(f"   {n:2d}: {num:>6s}   {kind}")
                            token, font = [], c["fontname"]
                        token.append(c)
                    elif token:
                        n += 1
                        num = "".join(t["text"] for t in token)
                        kind = "BOLD(barrier)" if font and "Bold" in font else "roman(well)"
                        print(f"   {n:2d}: {num:>6s}   {kind}")
                        token, font = [], None


if __name__ == "__main__":
    main()
