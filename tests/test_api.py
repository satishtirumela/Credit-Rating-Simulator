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
    assert len(bt_data) == 8


def test_results_endpoint_content_assertions():
    # 1. Test TP-2-Mid-Wind Results Screen HTML Template
    res_tp2 = client.get("/results/TP-2-Mid-Wind")
    assert res_tp2.status_code == 200
    assert "Credit Rating Assessment Results" in res_tp2.text
    assert "Print as PDF" in res_tp2.text
    assert "fetchAssessment()" in res_tp2.text

    # 2. Test Capped Project TP-4 Results Screen
    res_tp4 = client.get("/results/TP-4")
    assert res_tp4.status_code == 200
    assert "Credit Rating Assessment Results" in res_tp4.text

    # 3. Test Stage 3 Validation Block Project TP-8 Results Screen
    res_tp8 = client.get("/results/TP-8")
    assert res_tp8.status_code == 200
    assert "Credit Rating Assessment Results" in res_tp8.text

    # 4. Test Stage 1 Critical Null Project TP-7 Results Screen
    res_tp7 = client.get("/results/TP-7")
    assert res_tp7.status_code == 200
    assert "Credit Rating Assessment Results" in res_tp7.text

