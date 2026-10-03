# -*- coding: utf-8 -*-
"""Recover the layer-sequence line and any underlines drawn under its numbers.

Usage:
    python scripts/pdf_layer_line_dump.py <pdf_path> ["are as follows"]
"""
import sys

import pdfplumber


def main():
    pdf_path = sys.argv[1]
    phrase = sys.argv[2] if len(sys.argv) > 2 else "are as follows"
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if phrase not in text:
                continue
            print(f"--- page {pno} ---")
            chars = page.chars
            # locate the phrase, then take everything on the same text line
            idx = None
            seq = "".join(c["text"] for c in chars)
            idx = seq.find(phrase)
            if idx < 0:
                print("phrase not found in char stream")
                return
            anchor = chars[idx]
            top = anchor["top"]
            band = [c for c in chars if abs(c["top"] - top) < 8]
            band.sort(key=lambda c: c["x0"])
            line_text = "".join(c["text"] for c in band)
            print("line:", line_text)
            x0, x1 = band[0]["x0"], band[-1]["x1"]
            bottom = max(c["bottom"] for c in band)
            print(f"band: x0={x0:.1f} x1={x1:.1f} top={top:.1f} bottom={bottom:.1f}")

            edges = [e for e in page.edges
                     if bottom - 2 <= e["top"] <= bottom + 8
                     and e["x1"] > x0 - 5 and e["x0"] < x1 + 5]
            print(f"candidate underline strokes: {len(edges)}")
            for e in sorted(edges, key=lambda e: e["x0"]):
                # which characters sit above this stroke?
                covered = "".join(c["text"] for c in band
                                  if c["x0"] >= e["x0"] - 0.6 and c["x1"] <= e["x1"] + 0.6)
                print("   stroke x0=%7.2f x1=%7.2f top=%7.2f  covers: %s"
                      % (e["x0"], e["x1"], e["top"], covered))


if __name__ == "__main__":
    main()
