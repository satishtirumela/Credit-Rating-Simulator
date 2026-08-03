import json
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("================================================================================")
print("B.1 — TP-2-Mid-Wind RESULTS SCREEN RAW EVIDENCE")
print("================================================================================")
res_tp2 = client.get('/results/TP-2-Mid-Wind')
print('HTTP Status Code:', res_tp2.status_code)
for line in res_tp2.text.split('\n'):
    if any(k in line for k in ['score-val', 'Indicative Band', 'Final Rating Band', 'confidence-badge', 'Confidence Reason:', 'Block A:', 'Block B:', 'Block C:', 'Block D:', 'BB / BBB Boundary']):
        print('  ', line.strip())

print("\n================================================================================")
print("B.2 — TP-8 UNRATED DISPLAY RAW EVIDENCE")
print("================================================================================")
res_tp8 = client.get('/results/TP-8')
print('HTTP Status Code:', res_tp8.status_code)
print('Contains "Insufficient Input — Not Rated":', 'Insufficient Input — Not Rated' in res_tp8.text)
print('Contains "Critical Blocking Null":', 'Critical Blocking Null' in res_tp8.text)
print('Contains rated band badge markup (<div class="band-badge band-not rated):', '<div class="band-badge band-not rated' in res_tp8.text)

print("\n================================================================================")
print("B.3 — /api/backtest BATCH EXECUTION RAW EVIDENCE")
print("================================================================================")
res_bt = client.post('/api/backtest')
print('HTTP Status Code:', res_bt.status_code)
print(json.dumps(res_bt.json(), indent=2))

print("\n================================================================================")
print("B.4 — HOME SCREEN RECENT PROJECTS RAW EVIDENCE")
print("================================================================================")
res_home = client.get('/')
print('HTTP Status Code:', res_home.status_code)
for line in res_home.text.split('\n'):
    if any(k in line for k in ['TP-2-Mid-Wind', 'TP-1', 'TP-4', 'TP-8']):
        print('  ', line.strip())
