import urllib.request
import json
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.engine.scoring import score_project
from tests.test_engine import PROJECTS

print("================================================================================")
print("1. TESTING DRIVER SELECTION THRESHOLD LOGIC IN SCORING ENGINE")
print("================================================================================")

tp2 = next(p for p in PROJECTS if p["id"] == "TP-2")
res_tp2 = score_project(tp2["inputs"])

print("TP-2 (BBB/84.5) Drivers:")
print(json.dumps(res_tp2.get("drivers"), indent=2))
print("TP-2 Constraints:")
print(json.dumps(res_tp2.get("constraints"), indent=2))
print("TP-2 Notches Applied:")
print(json.dumps(res_tp2.get("notches_applied"), indent=2))

tp4 = next(p for p in PROJECTS if p["id"] == "TP-4")
res_tp4 = score_project(tp4["inputs"])

print("\nTP-4 (Capped BB) Notches Applied:")
print(json.dumps(res_tp4.get("notches_applied"), indent=2))

print("\n================================================================================")
print("2. FETCHING LIVE RENDERED HTML FOR TP-2-Mid-Wind (0 Notches)")
print("================================================================================")

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request("https://credit-rating-simulator.web.app/results/TP-2-Mid-Wind")
resp = opener.open(req)
html_tp2 = resp.read().decode('utf-8')

if "undefined" in html_tp2:
    print("--> ERROR: 'undefined' string found in TP-2-Mid-Wind HTML!")
else:
    print("--> SUCCESS: No 'undefined' string found in TP-2-Mid-Wind HTML!")

if "No notching adjustments applied." in html_tp2:
    print("--> SUCCESS: 'No notching adjustments applied.' correctly displayed!")

print("================================================================================")
