from pypdf import PdfReader
import os
import re

files = {
    "2d_tutorial": r"C:\Csuprem\Doc\PDF\CSuprem_2D_tutorial.pdf",
    "3d_tutorial": r"C:\Csuprem\Doc\PDF\CSuprem_3D_tutorial.pdf",
    "manual": r"C:\Csuprem\Doc\PDF\csuprem_manual.pdf",
}
outdir = r"books\csuprem-complex-structure\_source"
os.makedirs(outdir, exist_ok=True)

for key, path in files.items():
    r = PdfReader(path)
    n = len(r.pages)
    print(key, "pages:", n)
    with open(os.path.join(outdir, f"{key}.txt"), "w", encoding="utf-8") as f:
        for i in range(n):
            try:
                t = r.pages[i].extract_text() or ""
            except Exception:
                t = ""
            f.write(f"\n===== PDF page {i+1} =====\n{t}\n")

# print first page of manual to see TOC start
r = PdfReader(files["manual"])
print("manual page1:", re.sub(r"\s+", " ", (r.pages[0].extract_text() or ""))[:300])
