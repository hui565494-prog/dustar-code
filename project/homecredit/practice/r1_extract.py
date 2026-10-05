# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pypdf

src = r"D:\Dustar_code\project\homecredit\R1. 数据工程基础实践实验指导书-2026版 V2.pdf"
r = pypdf.PdfReader(src)
pages = []
for i, p in enumerate(r.pages):
    try:
        t = p.extract_text() or ""
    except Exception as e:
        t = f"[extract error: {e}]"
    pages.append(f"=== PAGE {i+1} ===\n{t}")
txt = "\n".join(pages)
with open("r1_full.txt", "w", encoding="utf-8") as f:
    f.write(txt)
print("pages:", len(r.pages), "chars:", len(txt))
