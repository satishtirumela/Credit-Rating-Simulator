import urllib.request
import urllib.error
import time
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

# Load reference project inputs for TP-2 or SolairePower
fixture_path = r"c:\Users\DELL\projects\Credit-Rating-Simulator\tests\fixtures\reference_projects_v3_0.json"
with open(fixture_path, "r", encoding="utf-8") as f:
    ref_data = json.load(f)["projects"][1]["inputs"]

payload_bytes = json.dumps(ref_data).encode("utf-8")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(
    'https://credit-rating-simulator.web.app/api/projects/SolairePower/approve',
    data=payload_bytes,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

start = time.time()
print("================================================================================")
print("SENDING POST /api/projects/SolairePower/approve TO LIVE FIREBASE HOSTING SITE")
print("================================================================================")

try:
    resp = opener.open(req, timeout=90)
    print('Status:', resp.getcode(), 'Time:', round(time.time()-start, 2))
    print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, 'Time:', round(time.time()-start, 2))
    print(e.read().decode('utf-8'))
except Exception as e:
    print('Exception:', e, 'Time:', round(time.time()-start, 2))

print("================================================================================")
