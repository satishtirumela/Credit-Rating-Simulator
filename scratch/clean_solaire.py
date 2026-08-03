import urllib.request
import urllib.error
import json
import time
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.firestore import get_project_document

print("================================================================================")
print("FETCHING AUTHENTIC EXTRACTED DATA FOR SolairePower FROM FIRESTORE")
print("================================================================================")

doc = get_project_document("SolairePower")
real_extracted_data = doc.get("extracted_data", {})

print("Extracted Technology:", real_extracted_data.get("technology_type"))
print("Extracted Capacity:  ", real_extracted_data.get("installed_capacity_mw_ac"))
print("Extracted Offtaker: ", real_extracted_data.get("offtakers"))
print("Extracted P90:      ", real_extracted_data.get("p90_attestation"))
print("Extracted DSCR:     ", real_extracted_data.get("minimum_dscr"), real_extracted_data.get("average_dscr"))

payload_bytes = json.dumps(real_extracted_data).encode("utf-8")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(
    'https://credit-rating-simulator.web.app/api/projects/SolairePower/approve',
    data=payload_bytes,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

start = time.time()
print("\n================================================================================")
print("APPROVING AUTHENTIC SolairePower INPUTS ON LIVE FIREBASE-HOSTED APP")
print("================================================================================")

try:
    resp = opener.open(req, timeout=60)
    print('HTTP Status:', resp.getcode(), 'Time:', round(time.time()-start, 2))
    raw_res = resp.read().decode('utf-8')
    res_json = json.loads(raw_res)
    print("FULL RAW RESPONSE PAYLOAD:")
    print(json.dumps(res_json, indent=2))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, 'Time:', round(time.time()-start, 2))
    print(e.read().decode('utf-8'))
except Exception as e:
    print('Exception:', e, 'Time:', round(time.time()-start, 2))

print("================================================================================")
