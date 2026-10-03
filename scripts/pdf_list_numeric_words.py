# -*- coding: utf-8 -*-
"""List words containing digits on the page that contains a phrase.

Usage:
    python scripts/pdf_list_numeric_words.py <pdf_path> <page_index_1based> [x0_min] [x0_max]
"""
import re
import sys

import pdfplumber


def main():
    pdf_path = sys.argv[1]
    page_no = int(sys.argv[2])
    x0_min = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    x0_max = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no - 1]
        words = page.extract_words(use_text_flow=True)
        for w in words:
            if not re.search(r"\d", w["text"]):
                continue
            if not (x0_min <= w["x0"] <= x0_max):
                continue
            width = w["x1"] - w["x0"]
            height = w["bottom"] - w["top"]
            print("text=%-14r top=%7.2f x0=%7.2f x1=%7.2f w=%5.1f h=%4.1f"
                  % (w["text"], w["top"], w["x0"], w["x1"], width, height))


if __name__ == "__main__":
    main()
