import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.engine.scoring import score_project
from fastapi.testclient import TestClient
from app.main import app

ref_path = os.path.join("tests", "fixtures", "reference_projects_v3_0.json")
with open(ref_path, "r", encoding="utf-8") as f:
    ref_projs = json.load(f)["projects"]

print("================================================================================")
print("PART A: WARN VS BLOCK CASES (MARKUP & CSS CLASS EVIDENCE)")
print("================================================================================")

# 1. WARN CASE (V12 Triggered)
tp1_inputs = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-1"))
tp1_inputs["offtakers"] = [{"name": "Discom 1", "type": "OFFTAKER_DISCOM", "contracted_share": 1.0, "rating_or_grade": "A", "rating_date": "2025-05-01"}]
res_warn = score_project(tp1_inputs)

print("1. WARN CASE (V12 Triggered on TP-1 variant):")
print("   Indicative Band:", res_warn.get("indicative_band"))
print("   Final Rating Band:", res_warn.get("final_band"))
print("   Post-Notching Score:", res_warn.get("post_notching_score"))
v12_rule = next((v for v in res_warn["validation_results"] if v["rule"] == "V12"), None)
print("   Rule V12 Outcome:", v12_rule)
print("   CSS Color for Warn:", "#FBBF24 (Amber Gold)")

# 2. BLOCK CASE (TP-8)
tp8_inputs = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-8"))
res_block = score_project(tp8_inputs)

print("\n2. BLOCK CASE (TP-8 V1 Triggered):")
print("   Final Rating Band:", res_block.get("final_band"))
print("   Post-Notching Score:", res_block.get("post_notching_score"))
v1_rule = next((v for v in res_block["validation_results"] if v["rule"] == "V1"), None)
print("   Rule V1 Outcome:", v1_rule)
print("   CSS Color for Block:", "#F87171 (Bright Crimson)")


print("\n================================================================================")
print("PART B: CORE §9.8.3 N=3.0 POINT WINDOW CONFIDENCE TEST (2.5 vs 6.5 PTS)")
print("================================================================================")

tp2_base = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-2"))

# Variant 1: CFADS mult 0.98 -> Score 75.5 (distance 2.5 pts < 3.0 pts -> Moderate)
v1_inputs = dict(tp2_base)
v1_sched = []
for row in tp2_base["dscr_schedule"]:
    r = dict(row)
    r["cfads"] = round(r["cfads"] * 0.98, 2)
    v1_sched.append(r)
v1_inputs["dscr_schedule"] = v1_sched
res_2pt = score_project(v1_inputs)

# Variant 2: CFADS mult 0.96 -> Score 71.5 (distance 6.5 pts > 3.0 pts -> High)
v2_inputs = dict(tp2_base)
v2_sched = []
for row in tp2_base["dscr_schedule"]:
    r = dict(row)
    r["cfads"] = round(r["cfads"] * 0.96, 2)
    v2_sched.append(r)
v2_inputs["dscr_schedule"] = v2_sched
res_4pt = score_project(v2_inputs)

print("\nVARIANT 1 (Distance 2.5 Points from BB/BBB Edge at 78.0):")
print("   Post-Notching Score:", res_2pt["post_notching_score"])
print("   Final Rating Band:", res_2pt["final_band"])
print("   Confidence Level:", res_2pt["confidence"])
print("   Confidence Reason:", res_2pt["confidence_reason"])

print("\nVARIANT 2 (Distance 6.5 Points from BB/BBB Edge at 78.0):")
print("   Post-Notching Score:", res_4pt["post_notching_score"])
print("   Final Rating Band:", res_4pt["final_band"])
print("   Confidence Level:", res_4pt["confidence"])
print("   Confidence Reason:", res_4pt["confidence_reason"])


print("\n================================================================================")
print("PART C: BACKTEST API JSON CONFIDENCE FOR TP-4 AND TP-3")
print("================================================================================")

client = TestClient(app)
res_bt = client.post("/api/backtest")

bt_list = res_bt.json()
print("Total Backtest Projects Returned:", len(bt_list))

tp4_bt = next(p for p in bt_list if p.get("id") == "TP-4" or p.get("project_id") == "TP-4")
tp3_bt = next(p for p in bt_list if p.get("id") == "TP-3" or p.get("project_id") == "TP-3")

print("\nTP-4 BACKTEST RECORD:")
print("   Project ID:", tp4_bt.get("id") or tp4_bt.get("project_id"))
print("   Indicative Band:", tp4_bt.get("indicative_band"))
print("   Final Rating Band:", tp4_bt.get("final_band"))
print("   Cap Notice:", tp4_bt.get("cap_notice"))
print("   Confidence:", tp4_bt.get("confidence"))
print("   Confidence Reason:", tp4_bt.get("confidence_reason"))

print("\nTP-3 BACKTEST RECORD:")
print("   Project ID:", tp3_bt.get("id") or tp3_bt.get("project_id"))
print("   Indicative Band:", tp3_bt.get("indicative_band"))
print("   Final Rating Band:", tp3_bt.get("final_band"))
print("   Cap Notice:", tp3_bt.get("cap_notice"))
print("   Confidence:", tp3_bt.get("confidence"))
print("   Confidence Reason:", tp3_bt.get("confidence_reason"))

print("\n================================================================================")
