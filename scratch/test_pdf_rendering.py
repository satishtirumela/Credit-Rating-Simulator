import os
import sys
import json
from pypdf import PdfReader
import io

sys.path.insert(0, os.path.abspath("."))

from app.pdf import generate_rationale_pdf
from app.firestore import get_project_document
from app.engine.scoring import score_project
from app.rationale.draft import draft_rationale

doc = get_project_document("TP-2-Mid-Wind")
approved_data = doc.get("approved_data") or doc.get("extracted_data")

score_result = score_project(approved_data)
score_result["rationale"] = draft_rationale(approved_data, score_result)

print("================================================================================")
print("GENERATING & VERIFYING PDF REPORT FOR TP-2-Mid-Wind")
print("================================================================================")

pdf_bytes = generate_rationale_pdf("TP-2-Mid-Wind", approved_data, score_result)
print("Generated PDF size:", len(pdf_bytes), "bytes")

reader = PdfReader(io.BytesIO(pdf_bytes))
full_text = "\n".join(page.extract_text() for page in reader.pages)

print("\n--- EXTRACTED PDF TEXT SNIPPET ---")
for line in full_text.splitlines():
    if "O&M" in line or "OEM" in line:
        print("Found line:", repr(line))

if "O&M" in full_text:
    print("\n--> SUCCESS: 'O&M' is cleanly present in rendered PDF text!")
else:
    print("\n--> ERROR: 'O&M' missing from PDF text!")

if "O&M;" in full_text:
    print("--> ERROR: 'O&M;' corrupted entity string found in PDF text!")
else:
    print("--> SUCCESS: No 'O&M;' corruption found in PDF text!")

print("================================================================================")
