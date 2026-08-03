import urllib.request
import urllib.error
import json
import time
import sys
import os

sys.path.insert(0, os.path.abspath("."))

with open(os.path.join("tests", "fixtures", "reference_projects_v3_0.json"), "r", encoding="utf-8") as f:
    ref_data = json.load(f)

tp2_proj = next(p for p in ref_data["projects"] if p["id"] == "TP-2")
tp2_data = tp2_proj["inputs"]

print("================================================================================")
print("RUNNING FULL APPROVAL FLOW FOR TP-2-Mid-Wind ON LIVE FIREBASE-HOSTED APP")
print("================================================================================")
print("Project ID: TP-2-Mid-Wind")
print("Input Technology:", tp2_data.get("technology_type"))
print("Input Capacity:  ", tp2_data.get("installed_capacity_mw_ac"))

payload_bytes = json.dumps(tp2_data).encode("utf-8")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(
    'https://credit-rating-simulator.web.app/api/projects/TP-2-Mid-Wind/approve',
    data=payload_bytes,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

start = time.time()
try:
    resp = opener.open(req, timeout=60)
    print('HTTP Status:', resp.getcode(), 'Time:', round(time.time()-start, 2))
    raw_res = resp.read().decode('utf-8')
    res_json = json.loads(raw_res)
    score = res_json.get("score", {})
    rationale = score.get("rationale", {})
    
    print("\n================================================================================")
    print("TP-2-Mid-Wind ASSESSMENT RESULTS")
    print("================================================================================")
    print("Indicative Band:    ", score.get("indicative_band"))
    print("Final Band:         ", score.get("final_band"))
    print("Post-Notching Score:", score.get("post_notching_score"))
    print("QA Status:          ", score.get("qa_review", {}).get("qa_status"))
    print("Citations Count:    ", len(rationale.get("citations", [])))
    print("\nRationale Executive Summary:")
    print(rationale.get("executive_summary"))
    print("\nRationale Rationale Text (first 500 chars):")
    print(rationale.get("rationale_text", "")[:500])
    
    print("\n================================================================================")
    print("FULL RAW RESPONSE PAYLOAD")
    print("================================================================================")
    print(json.dumps(res_json, indent=2))

except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, 'Time:', round(time.time()-start, 2))
    print(e.read().decode('utf-8'))
except Exception as e:
    print('Exception:', e, 'Time:', round(time.time()-start, 2))

print("================================================================================")
