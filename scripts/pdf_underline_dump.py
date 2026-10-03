# -*- coding: utf-8 -*-
"""Dump graphics edges (lines/rects/curves) near the layer-sequence line of a PDF.

Usage:
    python scripts/pdf_underline_dump.py <pdf_path> <phrase_in_page> <anchor_word>
"""
import sys

import pdfplumber


def main():
    pdf_path, phrase, anchor = sys.argv[1], sys.argv[2], sys.argv[3]
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if phrase.lower() not in text.lower():
                continue
            print(f"--- page {pno} ---")
            words = page.extract_words(use_text_flow=True)
            hits = [w for w in words if w["text"] == anchor]
            if not hits:
                print(f"anchor '{anchor}' not found")
                continue
            # group words into lines by top coordinate
            lines = {}
            for w in words:
                key = round(w["top"], 0)
                lines.setdefault(key, []).append(w)
            for hit in hits:
                key = round(hit["top"], 0)
                line = sorted(lines[key], key=lambda w: w["x0"])
                print("line text:", " ".join(w["text"] for w in line))
                print("line boxes: x0=%.1f x1=%.1f top=%.1f bottom=%.1f"
                      % (line[0]["x0"], line[-1]["x1"], line[0]["top"], line[0]["bottom"]))
                top, bottom = line[0]["top"], line[0]["bottom"]
                band = [e for e in page.edges
                        if top - 4 <= e["top"] <= bottom + 6]
                print(f"edges in band: {len(band)}")
                for e in sorted(band, key=lambda e: e["x0"]):
                    print("   x0=%7.2f x1=%7.2f top=%7.2f bottom=%7.2f orient=%s"
                          % (e["x0"], e["x1"], e["top"], e["bottom"], e.get("orientation")))
            print()


if __name__ == "__main__":
    main()
