import urllib.request
import urllib.error
import json
import time
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.firestore import get_project_document

doc = get_project_document("TP-2-Mid-Wind")
real_approved_data = doc.get("approved_data") or doc.get("extracted_data")

print("================================================================================")
print("FETCHING AUTHENTIC FIRESTORE APPROVED DATA FOR TP-2-Mid-Wind")
print("================================================================================")
print("Project Name:       ", real_approved_data.get("project_name"))
print("Technology:         ", real_approved_data.get("technology_type"))
print("Capacity (MW AC):   ", real_approved_data.get("installed_capacity_mw_ac"))
print("Offtaker:           ", real_approved_data.get("offtakers"))

payload_bytes = json.dumps(real_approved_data).encode("utf-8")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(
    'https://credit-rating-simulator.web.app/api/projects/TP-2-Mid-Wind/approve',
    data=payload_bytes,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

start = time.time()
print("\n================================================================================")
print("POSTING REAL FIRESTORE APPROVED DATA TO /approve ON LIVE FIREBASE-HOSTED APP")
print("================================================================================")

try:
    resp = opener.open(req, timeout=60)
    print('HTTP Status:', resp.getcode(), 'Time:', round(time.time()-start, 2))
    raw_res = resp.read().decode('utf-8')
    res_json = json.loads(raw_res)
    score = res_json.get("score", {})
    rationale = score.get("rationale", {})
    
    print("\n================================================================================")
    print("LIVE ASSESSMENT RESULTS FOR REAL TP-2-Mid-Wind FIRESTORE DATA")
    print("================================================================================")
    print("Indicative Band:    ", score.get("indicative_band"))
    print("Final Band:         ", score.get("final_band"))
    print("Raw Score:          ", score.get("raw_score"))
    print("Post-Notching Score:", score.get("post_notching_score"))
    print("Confidence:         ", score.get("confidence"))
    print("Confidence Reason:  ", score.get("confidence_reason"))
    print("QA Status:          ", score.get("qa_review", {}).get("qa_status"))
    print("Citations Count:    ", len(rationale.get("citations", [])))
    
    print("\nRationale Executive Summary:")
    print(rationale.get("executive_summary"))
    print("\nRationale Rationale Text:")
    print(rationale.get("rationale_text"))

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
