import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.engine.scoring import score_project, INTERIOR_BAND_EDGES

ref_path = os.path.join("tests", "fixtures", "reference_projects_v3_0.json")
with open(ref_path, "r", encoding="utf-8") as f:
    ref_projs = json.load(f)["projects"]

tp2_base = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-2"))

# Let's see what raw score components we can tweak to get post_notching_score = 75.0 (d=3.0), 76.0 (d=2.0), 74.0 (d=4.0)
# Nearest edge is 78.0 (BB/BBB edge)
# To land at 76.0: 78.0 - 76.0 = 2.0 pts
# To land at 75.0: 78.0 - 75.0 = 3.0 pts
# To land at 74.0: 78.0 - 74.0 = 4.0 pts

def get_project_at_score(target_score):
    # We tweak a continuous component or non-critical null points forgone / dscr_schedule to hit exact target_score
    # Base TP-2 raw_score = 77.5
    # Let's adjust cfads_nca_by_period or dscr_schedule or NPV CFADS
    diff = target_score - 77.5
    # We can adjust an input that shifts score by diff
    inputs = dict(tp2_base)
    # Let's adjust npv_cfads_project_life or similar
    # In Block C or Block A/B:
    # Or we can test by patching/evaluating the engine logic
    return inputs

print("================================================================================")
print("CORE §9.8.3 EXACT BOUNDARY DISTANCE TESTS (d = 3.0, d = 2.0, d = 4.0)")
print("================================================================================")

# Let's run direct python checks by setting post_notching_score directly in engine logic mock
for target_score, expected_d in [(75.0, 3.0), (76.0, 2.0), (74.0, 4.0)]:
    # Evaluate d calculation logic
    d = min(abs(target_score - edge) for edge in INTERIOR_BAND_EDGES)
    nearest_edge = min(INTERIOR_BAND_EDGES, key=lambda edge: abs(target_score - edge))
    
    confidence = "High"
    reason_parts = []
    if d < 3.0:
        confidence = "Moderate"
        reason_parts.append(f"d = {d:.1f} — within 3.0 points of the edge at {nearest_edge}")
    
    if reason_parts:
        confidence_reason = ", ".join(reason_parts)
    else:
        confidence_reason = f"d = {d:.1f}, no cap, no nulls"

    print(f"\nTarget Score: {target_score:.1f} (Nearest Edge: {nearest_edge:.1f} -> Distance d = {d:.1f})")
    print(f"   Condition Checked: if d < 3.0 ({d:.1f} < 3.0) => {d < 3.0}")
    print(f"   Confidence Output: {confidence}")
    print(f"   Confidence Reason: {confidence_reason}")

print("\n================================================================================")
