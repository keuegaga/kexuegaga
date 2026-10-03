# -*- coding: utf-8 -*-
"""Find underlined words on the PDF page that contains a search phrase.

Underline is drawn as a thin rectangle/line in the PDF, so it is recovered by
looking for rects/lines just below the baseline of each word.

Usage:
    python scripts/pdf_underline_check.py <pdf_path> "<search phrase>"
"""
import sys

import pdfplumber


def main():
    pdf_path = sys.argv[1]
    phrase = sys.argv[2] if len(sys.argv) > 2 else "injection barrier"

    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if phrase.lower() not in text.lower():
                continue
            print(f"--- page {pno} ---")
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            rects = list(page.rects) + list(page.lines) + list(page.curves)
            for w in words:
                top, bottom = w["top"], w["bottom"]
                m = [(r["x0"], r["x1"]) for r in rects
                     if bottom - 1.6 <= r["top"] <= bottom + 2.6
                     and r["x1"] > w["x0"] - 1 and r["x0"] < w["x1"] + 1
                     and (r["x1"] - r["x0"]) < 12]
                flag = "  <== UNDERLINED" if m else ""
                print(f"  {w['text']:>10s}  x0={w['x0']:7.2f} x1={w['x1']:7.2f} "
                      f"top={top:7.2f}{flag}")
            print()


if __name__ == "__main__":
    main()
