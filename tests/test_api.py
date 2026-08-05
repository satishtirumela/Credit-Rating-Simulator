"""
Unit tests for FastAPI HTTP API endpoint (/score and /health).
"""

import json
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "reference_projects_v3_0.json")

with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
    PROJECTS = json.load(f)["projects"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Credit Rating Simulator API"


def test_score_endpoint_tp1():
    tp1 = PROJECTS[0]["inputs"]
    response = client.post("/score", json=tp1)
    assert response.status_code == 200
    data = response.json()
    assert data["indicative_band"] == "AAA"
    assert data["final_band"] == "AAA"
    assert data["confidence"] == "High"


def test_score_endpoint_tp8_unrated():
    tp8 = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-8")
    response = client.post("/score", json=tp8)
    assert response.status_code == 200
    data = response.json()
    assert data["indicative_band"] == "Not Rated"
    assert data["confidence"] == "Not Rated"
    assert len(data["validation_results"]) == 13


def test_score_endpoint_with_rationale():
    tp2 = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-2")
    response = client.post("/score?include_rationale=true", json=tp2)
    assert response.status_code == 200
    data = response.json()
    assert data["indicative_band"] == "BB"
    assert "rationale" in data
    assert "rationale_text" in data["rationale"]


def test_upload_screen_html():
    response = client.get("/upload")
    assert response.status_code == 200
    assert "Credit Rating Simulator — File Upload" in response.text
    assert 'accept=".docx"' in response.text
    assert 'accept=".xlsx"' in response.text


def test_upload_api_endpoint():
    t1_content = b"Mock docx binary content"
    t2_content = b"Mock xlsx binary content"

    files = {
        "template1": ("Template_1.docx", t1_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "template2": ("Template_2.xlsx", t2_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    }
    data = {"project_id": "TP-TEST-API"}

    response = client.post("/api/upload", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["project_id"] == "TP-TEST-API"
    assert len(res_data["files"]) == 2
    assert res_data["files"][0]["filename"] == "Template_1.docx"
    assert res_data["files"][1]["filename"] == "Template_2.xlsx"


def test_review_screen_endpoint():
    response = client.get("/review/TP-2-Mid-Wind")
    assert response.status_code == 200
    assert "Project Input Review & Approval" in response.text


def test_unapproved_project_scoring_gate():
    # Attempting to score an unapproved project must return HTTP 400
    response = client.post("/api/projects/UNAPPROVED-PROJECT-XYZ/score")
    assert response.status_code == 400
    assert "must be reviewed and approved before scoring" in response.json()["detail"]


def test_approve_and_score_flow():
    # 1. Setup mock project state in firestore module
    from app.extraction import save_to_firestore
    import json, os

    ref_path = os.path.join(os.path.dirname(__file__), "fixtures", "reference_projects_v3_0.json")
    with open(ref_path, "r", encoding="utf-8") as f:
        ref_projs = json.load(f)["projects"]

    tp2_inputs = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-2"))
    save_to_firestore("TP-TEST-REVIEW", tp2_inputs)

    # 2. User modifies project_name
    approved_payload = dict(tp2_inputs)
    approved_payload["project_name"] = "User Corrected Name"

    # 3. POST /api/projects/TP-TEST-REVIEW/approve
    res = client.post("/api/projects/TP-TEST-REVIEW/approve", json=approved_payload)
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "success"
    assert res_json["redirect_url"] == "/results/TP-TEST-REVIEW"
    assert "score" in res_json
    assert res_json["score"]["final_band"] == "BB"

    # 4. POST /api/projects/TP-TEST-REVIEW/score succeeds
    score_res = client.post("/api/projects/TP-TEST-REVIEW/score")
    assert score_res.status_code == 200
    assert "indicative_band" in score_res.json()


def test_approved_pipeline_flow():
    # 1. Setup mock project state in firestore module
    from app.extraction import save_to_firestore
    from app.firestore import get_project_document
    import json, os

    ref_path = os.path.join(os.path.dirname(__file__), "fixtures", "reference_projects_v3_0.json")
    with open(ref_path, "r", encoding="utf-8") as f:
        ref_projs = json.load(f)["projects"]

    tp2_inputs = dict(next(p["inputs"] for p in ref_projs if p["id"] == "TP-2"))
    save_to_firestore("TP-TEST-PIPELINE", tp2_inputs)

    # 2. Approve project via POST /api/projects/TP-TEST-PIPELINE/approve
    approved_payload = dict(tp2_inputs)
    approved_payload["project_name"] = "Pipeline Test Project Name"

    res = client.post("/api/projects/TP-TEST-PIPELINE/approve", json=approved_payload)
    assert res.status_code == 200
    res_data = res.json()

    # 3. Assert Phase 2 response payload attributes
    assert res_data["status"] == "success"
    assert res_data["redirect_url"] == "/results/TP-TEST-PIPELINE"
    assert res_data["pdf_report_generated"] is True
    assert "score" in res_data

    # 4. Assert Firestore persistence state
    doc = get_project_document("TP-TEST-PIPELINE")
    assert doc["status"] == "approved"
    assert "score" in doc
    assert "rationale" in doc["score"]
    
    citations = doc["score"]["rationale"]["citations"]
    assert len(citations) == 3
    for c in citations:
        assert c["grounding_status"] == "VERIFIED_VERBATIM"

    # 5. Assert PDF download endpoint
    pdf_res = client.get("/api/projects/TP-TEST-PIPELINE/download-rationale")
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_res.content) > 1000


def test_download_rationale_pdf_endpoint():
    # 1. Test PDF download for approved project TP-2-Mid-Wind
    response = client.get("/api/projects/TP-2-Mid-Wind/download-rationale")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000

    # 2. Test PDF download for unapproved project returns HTTP 400
    unapp_res = client.get("/api/projects/UNAPPROVED-PROJECT-XYZ/download-rationale")
    assert unapp_res.status_code == 400


def test_home_and_backtest_endpoints():
    # 1. GET / (Home page)
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert "Credit Rating Simulator" in res_home.text

    # 2. GET /backtest (Back-test tab)
    res_bt_page = client.get("/backtest")
    assert res_bt_page.status_code == 200
    assert "Reference Project Back-Test Suite" in res_bt_page.text

    # 3. POST /api/backtest
    res_bt_api = client.post("/api/backtest")
    assert res_bt_api.status_code == 200
    bt_data = res_bt_api.json()
    assert isinstance(bt_data, list)
    # 9 reference projects: TP-1 through TP-8, plus NEG-CAP-1 (split out from what was
    # previously a mislabeled "TP-4" -- a TP-1 clone with a CP_WEAK offtaker, built to
    # isolate the SS8.4 band-cap mechanism. TP-4 now holds its own genuine data
    # (Vindhya Hybrid Power Private Limited) instead of duplicating that test case.
    assert len(bt_data) == 9


def test_results_endpoint_content_assertions():
    tp2_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-2")
    tp4_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-4")
    neg_cap_1_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "NEG-CAP-1")
    tp8_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-8")
    tp7_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-7")

    # 1. Test TP-2 Results Screen & Score
    res_tp2_html = client.get("/results/TP-2-Mid-Wind")
    assert res_tp2_html.status_code == 200
    assert "Credit Rating Assessment Results" in res_tp2_html.text

    res_tp2_score = client.post("/score", json=tp2_inputs)
    assert res_tp2_score.status_code == 200
    tp2_score = res_tp2_score.json()
    # CORE SS3.5's closing rule: literal reading (sub-score 1.5) confirmed as the governing
    # methodology -- Block A 27.5, raw 84.0, post-notching 77.0. The alternative reading
    # (sub-score 2.0 -> raw 84.5) remains documented but is not what this engine implements.
    assert tp2_score.get("raw_score") == 84.0
    assert tp2_score.get("final_band") == "BB"

    # 2. Test TP-4 Results Screen & Score -- genuine Vindhya Hybrid Power Private Limited
    # data (180 MW hybrid). This project has NO band cap: its governing offtaker tier is
    # Strong (DISCOM grade A+ at 58%, C&I AA- at 42%), so its only notch is -7 from SS7.2
    # refinancing risk (22% partial bullet, no mitigant). The cap-mechanism test case that
    # used to live under the "TP-4" id has been correctly split out to NEG-CAP-1 below --
    # see that section for the capped-band assertions.
    res_tp4_html = client.get("/results/TP-4")
    assert res_tp4_html.status_code == 200

    res_tp4_score = client.post("/score", json=tp4_inputs)
    assert res_tp4_score.status_code == 200
    tp4_score = res_tp4_score.json()
    assert tp4_score.get("raw_score") == 84.5
    assert tp4_score.get("post_notching_score") == 77.5
    assert tp4_score.get("indicative_band") == "BB"
    assert tp4_score.get("final_band") == "BB"
    assert not tp4_score.get("cap_notice")

    # 3. Test Capped Project NEG-CAP-1 Results Screen & Cap Notice -- SS8.4 band-cap
    # isolation case (TP-1's business/financial profile, cloned, with a CP_WEAK offtaker
    # substituted in). Raw score 115 (uncapped, same as TP-1), but the Weak offtaker tier
    # drives a -14 notch to post-notching 101, score-implied AA, capped down to BB.
    res_neg_cap_html = client.get("/results/NEG-CAP-1")
    assert res_neg_cap_html.status_code == 200

    res_neg_cap_score = client.post("/score", json=neg_cap_1_inputs)
    assert res_neg_cap_score.status_code == 200
    neg_cap_score = res_neg_cap_score.json()
    assert "Band capped at BB — Offtaker tier Weak. Score-implied band was AA." in neg_cap_score.get("cap_notice", "")

    # 4. Test Stage 3 Validation Block Project TP-8 Results Screen & Validation Block
    res_tp8_html = client.get("/results/TP-8")
    assert res_tp8_html.status_code == 200

    res_tp8_score = client.post("/score", json=tp8_inputs)
    assert res_tp8_score.status_code == 200
    tp8_score = res_tp8_score.json()
    assert tp8_score.get("final_band") == "Not Rated"
    assert "Validation Block" in tp8_score.get("confidence_reason", "")
    assert tp8_score.get("validation_results", [{}])[0].get("outcome") == "Block"

    # 5. Test Stage 1 Critical Null Project TP-7 Results Screen & Exit Reason
    res_tp7_html = client.get("/results/TP-7")
    assert res_tp7_html.status_code == 200

    res_tp7_score = client.post("/score", json=tp7_inputs)
    assert res_tp7_score.status_code == 200
    tp7_score = res_tp7_score.json()
    assert tp7_score.get("final_band") == "Not Rated"
    assert "Critical null" in tp7_score.get("confidence_reason", "")


def test_results_screen_rendered_playwright():
    """
    Playwright browser test: renders results.html in headless browser against live server
    to verify rendered DOM text for uncapped (TP-4), capped (NEG-CAP-1), validation-blocked
    (TP-8), and unrated (TP-7) projects.
    """
    from playwright.sync_api import sync_playwright
    from app.pipeline import run_approved_assessment_pipeline

    tp4_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-4")
    neg_cap_1_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "NEG-CAP-1")
    tp8_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-8")
    tp7_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-7")

    run_approved_assessment_pipeline("TP-4", tp4_inputs)
    run_approved_assessment_pipeline("NEG-CAP-1", neg_cap_1_inputs)
    run_approved_assessment_pipeline("TP-8", tp8_inputs)
    run_approved_assessment_pipeline("TP-7", tp7_inputs)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Render TP-4 -- genuine Vindhya Hybrid Power Private Limited, no band cap
        # (governing offtaker tier is Strong; the -7 notch comes from SS7.2 refinancing
        # risk alone). This project must NOT show capped-band language.
        page.goto("http://127.0.0.1:8000/results/TP-4", wait_until="networkidle")
        tp4_text = page.inner_text("body")
        assert "BB" in tp4_text  # final band
        assert "Band capped at BB" not in tp4_text
        assert "Limited by Override Cap" not in tp4_text

        # 2. Render Capped Project NEG-CAP-1 -- the SS8.4 band-cap isolation case that
        # previously lived under the "TP-4" id (TP-1's profile, cloned, with a CP_WEAK
        # offtaker substituted in). Score-implied AA, capped down to BB.
        page.goto("http://127.0.0.1:8000/results/NEG-CAP-1", wait_until="networkidle")
        neg_cap_text = page.inner_text("body")
        assert "Band capped at BB" in neg_cap_text
        assert "Offtaker tier Weak" in neg_cap_text
        assert "Limited by Override Cap" in neg_cap_text

        # 3. Render Validation Block Project TP-8
        page.goto("http://127.0.0.1:8000/results/TP-8", wait_until="networkidle")
        tp8_text = page.inner_text("body")
        assert "Validation Block — Not Rated" in tp8_text
        assert "Validation Block Triggered — V1: Average DSCR 1.1000 < Minimum DSCR 1.2000" in tp8_text

        # 4. Render Critical Null Project TP-7
        page.goto("http://127.0.0.1:8000/results/TP-7", wait_until="networkidle")
        tp7_text = page.inner_text("body")
        assert "Insufficient Input — Not Rated" in tp7_text
        assert "Critical Blocking Null" in tp7_text

        browser.close()

