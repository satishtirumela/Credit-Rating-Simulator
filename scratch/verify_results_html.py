import urllib.request
import urllib.error
import json
import time
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.firestore import get_project_document

print("================================================================================")
print("1. APPROVING AUTHENTIC SolairePower INPUTS ON LIVE APP")
print("================================================================================")

doc = get_project_document("SolairePower")
real_extracted_data = doc.get("extracted_data", {})

payload_bytes = json.dumps(real_extracted_data).encode("utf-8")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(
    'https://credit-rating-simulator.web.app/api/projects/SolairePower/approve',
    data=payload_bytes,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

resp = opener.open(req, timeout=60)
print('Approve Status:', resp.getcode())
res_json = json.loads(resp.read().decode('utf-8'))

print("\n================================================================================")
print("2. CHECKING score.null_register IN API RESPONSE")
print("================================================================================")
null_reg = res_json.get("score", {}).get("null_register", [])
print("null_register length:", len(null_reg))
print(json.dumps(null_reg, indent=2))

print("================================================================================")
