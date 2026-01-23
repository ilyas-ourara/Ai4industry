from pypdf import PdfReader
import json, os

pdf_paths = [
    "data/DDRM_vienne_86.pdf", 
]


out_path = "docs.jsonl"
with open(out_path, "w", encoding="utf-8") as out:
    for pdf in pdf_paths:
        reader = PdfReader(pdf)
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = " ".join(text.split())
            if text.strip():
                out.write(json.dumps({"doc_id": os.path.basename(pdf), "page": i, "text": text}, ensure_ascii=False) + "\n")

print("done ->", out_path)