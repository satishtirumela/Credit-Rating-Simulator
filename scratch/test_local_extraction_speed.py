import time
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.extraction import extract_project_data

t1_path = r"c:\Users\DELL\projects\Credit-Rating-Simulator\tests\fixtures\worked_examples\Worked_Example_TP2_Template_1_v3_0.docx"
t2_path = r"c:\Users\DELL\projects\Credit-Rating-Simulator\tests\fixtures\worked_examples\Worked_Example_TP2_Template_2_v3_0.xlsx"

with open(t1_path, "rb") as f:
    t1_bytes = f.read()

with open(t2_path, "rb") as f:
    t2_bytes = f.read()

print("Timing extract_project_data() Gemini call...")
start_t = time.time()
res = extract_project_data("TP-2-Mid-Wind", t1_bytes, t2_bytes, write_firestore=False)
end_t = time.time()

print(f"Extraction Completed in {end_t - start_t:.2f} seconds!")
print("Extracted Keys:", list(res.get("extracted_data", {}).keys()))
