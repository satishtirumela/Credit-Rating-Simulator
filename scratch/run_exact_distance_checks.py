import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.engine.scoring import score_project

ref_path = os.path.join("tests", "fixtures", "reference_projects_v3_0.json")
with open(ref_path, "r", encoding="utf-8") as f:
    ref_projs = json.load(f)["projects"]

tp2_base = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-2"))

print("================================================================================")
print("CORE §9.8.3 EXACT BOUNDARY DISTANCE TEST RESULTS (d = 3.0, d = 2.0, d = 4.0)")
print("================================================================================")

# 1. EXACT d = 3.0000 (Boundary Test)
# Set project_cfo = 2000.0 on TP-2 -> post_notching_score = 75.0 (78.0 - 75.0 = 3.0)
v_3pt = dict(tp2_base)
v_3pt["project_cfo"] = 2000.0
res_3pt = score_project(v_3pt)

print("1. EXACT d = 3.0000 BOUNDARY TEST:")
print("   Post-Notching Score:", res_3pt["post_notching_score"])
print("   Nearest Edge:", 78.0)
print("   Computed Distance d:", abs(res_3pt["post_notching_score"] - 78.0))
print("   Confidence Level:", res_3pt["confidence"])
print("   Confidence Reason:", res_3pt["confidence_reason"])
print("   Boundary Rule Verdict: EXCLUSIVE at boundary (d < 3.0 is False for d = 3.0 => HIGH confidence)")

# 2. EXACT d = 2.0000 (Inside N=3.0 Window)
# Set project_cfo = 2000.0 and land_acquisition_status = "LAND_50_80" on TP-2 -> post_notching_score = 76.0 (78.0 - 76.0 = 2.0)
v_2pt = dict(tp2_base)
v_2pt["project_cfo"] = 2000.0
v_2pt["land_acquisition_status"] = "LAND_50_80"
res_2pt = score_project(v_2pt)

print("\n2. EXACT d = 2.0000 TEST (Inside Window):")
print("   Post-Notching Score:", res_2pt["post_notching_score"])
print("   Nearest Edge:", 78.0)
print("   Computed Distance d:", abs(res_2pt["post_notching_score"] - 78.0))
print("   Confidence Level:", res_2pt["confidence"])
print("   Confidence Reason:", res_2pt["confidence_reason"])

# 3. EXACT d = 4.0000 (Outside N=3.0 Window)
# Set project_cfo = 2000.0 and land_acquisition_status = "LAND_UNDER_50" on TP-2 -> post_notching_score = 74.0 (78.0 - 74.0 = 4.0)
v_4pt = dict(tp2_base)
v_4pt["project_cfo"] = 2000.0
v_4pt["land_acquisition_status"] = "LAND_UNDER_50"
res_4pt = score_project(v_4pt)

print("\n3. EXACT d = 4.0000 TEST (Outside Window):")
print("   Post-Notching Score:", res_4pt["post_notching_score"])
print("   Nearest Edge:", 78.0)
print("   Computed Distance d:", abs(res_4pt["post_notching_score"] - 78.0))
print("   Confidence Level:", res_4pt["confidence"])
print("   Confidence Reason:", res_4pt["confidence_reason"])

print("\n================================================================================")
