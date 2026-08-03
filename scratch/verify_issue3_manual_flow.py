import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.extraction import save_to_firestore

client = TestClient(app)

print("================================================================================")
print("MANUAL VERIFICATION SEQUENCE FOR FRESH PROJECT: FRESH-PROJECT-SOLAR-99")
print("================================================================================")

# Load real inputs from reference project TP-1
ref_path = os.path.join("tests", "fixtures", "reference_projects_v3_0.json")
with open(ref_path, "r", encoding="utf-8") as f:
    ref_data = json.load(f)["projects"]

fresh_inputs = dict(next(p["inputs"] for p in ref_data if p["id"] == "TP-1"))
fresh_inputs["project_name"] = "Fresh Solar Assessment Project 99"

# 1. SETUP INITIAL PROJECT IN FIRESTORE
save_to_firestore("FRESH-PROJECT-SOLAR-99", fresh_inputs)
print("1. Initial project uploaded & stored under ID: FRESH-PROJECT-SOLAR-99")

# 2. GET /review/FRESH-PROJECT-SOLAR-99
res_review = client.get("/review/FRESH-PROJECT-SOLAR-99")
print("\n2. GET /review/FRESH-PROJECT-SOLAR-99 Status:", res_review.status_code)
assert res_review.status_code == 200
print("   Review UI loaded successfully.")

# 3. POST /api/projects/FRESH-PROJECT-SOLAR-99/approve
res_approve = client.post("/api/projects/FRESH-PROJECT-SOLAR-99/approve", json=fresh_inputs)
print("\n3. POST /api/projects/FRESH-PROJECT-SOLAR-99/approve Status:", res_approve.status_code)
assert res_approve.status_code == 200
app_json = res_approve.json()
print("   Response Status:", app_json.get("status"))
print("   Redirect URL:", app_json.get("redirect_url"))
print("   PDF Report Generated:", app_json.get("pdf_report_generated"))
print("   Final Rating Band:", app_json.get("score", {}).get("final_band"))

# 4. GET /results/FRESH-PROJECT-SOLAR-99
res_results = client.get("/results/FRESH-PROJECT-SOLAR-99")
print("\n4. GET /results/FRESH-PROJECT-SOLAR-99 Status:", res_results.status_code)
assert res_results.status_code == 200

print("\n=== RATIONALE & CITATIONS SECTION RENDERED ON /results/FRESH-PROJECT-SOLAR-99 ===")
found_section = False
for line in res_results.text.split("\n"):
    if "Credit Rationale & Grounded Citations" in line or "Methodology Citation" in line or "citation-text" in line:
        found_section = True
    if found_section and any(k in line for k in ["Credit Rationale", "Methodology Citation", "citation-text", "CARE", "Crisil"]):
        print("  ", line.strip())

# 5. GET /api/projects/FRESH-PROJECT-SOLAR-99/download-rationale (PDF Download)
res_pdf = client.get("/api/projects/FRESH-PROJECT-SOLAR-99/download-rationale")
print("\n5. GET /api/projects/FRESH-PROJECT-SOLAR-99/download-rationale Status:", res_pdf.status_code)
print("   Content-Type:", res_pdf.headers.get("content-type"))
print("   PDF Size in Bytes:", len(res_pdf.content))
assert res_pdf.status_code == 200
assert res_pdf.headers.get("content-type") == "application/pdf"
assert len(res_pdf.content) > 1000

print("\n================================================================================")
print("SUCCESS: Full manual verification sequence completed flawlessly for FRESH-PROJECT-SOLAR-99!")
print("================================================================================")
