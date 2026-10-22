# -*- coding: utf-8 -*-
"""Extract design-relevant text from the MinerU markdown papers in the QCL library.

For every *.md file it prints:
  - the first lines (title / authors / abstract)
  - paragraphs that mention design keywords, de-duplicated

Usage:
    python scripts/extract_qcl_literature.py <library_dir> [max_paras_per_paper]
"""
import os
import re
import sys

KEYWORDS = [
    "bound-to-continuum", "bound to continuum", "continuum-to-continuum",
    "continuum to continuum", "continuum-to-bound", "dual-upper-state",
    "dual upper state", "three-phonon", "three phonon", "two-phonon",
    "active region design", "active-region design", "design",
    "upper laser level", "lower laser level", "depopulation", "injector",
    "miniband", "anticrossing", "oscillator strength", "dipole",
    "conduction band offset", "band offset", "T0", "T_0",
]


def clean(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)      # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)    # links
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def main():
    root = sys.argv[1]
    max_paras = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    files = [f for f in sorted(os.listdir(root)) if f.endswith(".md")]
    print(f"# {len(files)} markdown papers in {root}\n")
    for fn in files:
        path = os.path.join(root, fn)
        raw = open(path, encoding="utf-8", errors="ignore").read()
        paras = [clean(p) for p in re.split(r"\n\s*\n", raw)]
        paras = [p for p in paras if len(p) > 40]
        print("=" * 100)
        print("## " + fn)
        # header: first few substantive paragraphs
        for p in paras[:3]:
            print("  H:", p[:400])
        picked, seen = [], set()
        for p in paras:
            low = p.lower()
            if not any(k.lower() in low for k in KEYWORDS):
                continue
            key = p[:80]
            if key in seen:
                continue
            seen.add(key)
            picked.append(p)
            if len(picked) >= max_paras:
                break
        for p in picked:
            print("  -", p[:500])
        print()


if __name__ == "__main__":
    main()
