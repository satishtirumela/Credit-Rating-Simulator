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

    try:
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
    finally:
        _delete_project_document("TP-TEST-REVIEW")


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

    try:
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
    finally:
        _delete_project_document("TP-TEST-PIPELINE")


def test_download_rationale_pdf_endpoint():
    # 1. Test PDF download for a freshly approved project (self-contained -- must not
    # depend on any project persisting in Firestore between runs).
    from app.extraction import save_to_firestore

    project_id = "TP-TEST-PDF-DOWNLOAD"
    tp2_inputs = dict(next(p["inputs"] for p in PROJECTS if p["id"] == "TP-2"))
    save_to_firestore(project_id, tp2_inputs)

    try:
        approve_res = client.post(f"/api/projects/{project_id}/approve", json=tp2_inputs)
        assert approve_res.status_code == 200

        response = client.get(f"/api/projects/{project_id}/download-rationale")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000
    finally:
        _delete_project_document(project_id)

    # 2. Test PDF download for unapproved project returns HTTP 400
    unapp_res = client.get("/api/projects/UNAPPROVED-PROJECT-XYZ/download-rationale")
    assert unapp_res.status_code == 400


def test_home_endpoint():
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert "Credit Rating Simulator" in res_home.text


def test_backtest_route_removed():
    # Back-Test tab and its API were removed; confirm they no longer resolve.
    assert client.get("/backtest").status_code == 404
    assert client.post("/api/backtest").status_code == 404


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
    to verify rendered DOM text for uncapped (TP-4 profile), capped (NEG-CAP-1 profile),
    validation-blocked (TP-8 profile), and unrated (TP-7 profile) projects.

    Runs against disposable TP-TEST-RESULTS-* ids carrying the same fixture input data as
    the canonical TP-4/NEG-CAP-1/TP-8/TP-7 documents, rather than the canonical ids
    themselves -- every assertion below is driven entirely by the input data (band/cap/
    validation-outcome text), never by the literal project id, so this is a like-for-like
    substitution. The canonical documents must never be mutated by running this suite;
    approving/scoring live reference documents on every test run silently overwrites their
    approved_at/scored_at with a spurious new timestamp.
    """
    from playwright.sync_api import sync_playwright
    from app.pipeline import run_approved_assessment_pipeline

    tp4_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-4")
    neg_cap_1_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "NEG-CAP-1")
    tp8_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-8")
    tp7_inputs = next(p["inputs"] for p in PROJECTS if p["id"] == "TP-7")

    test_ids = {
        "tp4": "TP-TEST-RESULTS-TP4",
        "neg_cap_1": "TP-TEST-RESULTS-NEGCAP1",
        "tp8": "TP-TEST-RESULTS-TP8",
        "tp7": "TP-TEST-RESULTS-TP7",
    }

    try:
        run_approved_assessment_pipeline(test_ids["tp4"], tp4_inputs)
        run_approved_assessment_pipeline(test_ids["neg_cap_1"], neg_cap_1_inputs)
        run_approved_assessment_pipeline(test_ids["tp8"], tp8_inputs)
        run_approved_assessment_pipeline(test_ids["tp7"], tp7_inputs)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Render TP-4 profile -- genuine Vindhya Hybrid Power Private Limited, no band
            # cap (governing offtaker tier is Strong; the -7 notch comes from SS7.2
            # refinancing risk alone). This project must NOT show capped-band language.
            page.goto(f"http://127.0.0.1:8000/results/{test_ids['tp4']}", wait_until="networkidle")
            tp4_text = page.inner_text("body")
            assert "BB" in tp4_text  # final band
            assert "Band capped at BB" not in tp4_text
            assert "Limited by Override Cap" not in tp4_text

            # 2. Render Capped Project NEG-CAP-1 profile -- the SS8.4 band-cap isolation case
            # that previously lived under the "TP-4" id (TP-1's profile, cloned, with a
            # CP_WEAK offtaker substituted in). Score-implied AA, capped down to BB.
            page.goto(f"http://127.0.0.1:8000/results/{test_ids['neg_cap_1']}", wait_until="networkidle")
            neg_cap_text = page.inner_text("body")
            assert "Band capped at BB" in neg_cap_text
            assert "Offtaker tier Weak" in neg_cap_text
            assert "Limited by Override Cap" in neg_cap_text

            # 3. Render Validation Block Project TP-8 profile
            page.goto(f"http://127.0.0.1:8000/results/{test_ids['tp8']}", wait_until="networkidle")
            tp8_text = page.inner_text("body")
            assert "Validation Block — Not Rated" in tp8_text
            assert "Validation Block Triggered — V1: Average DSCR 1.1000 < Minimum DSCR 1.2000" in tp8_text

            # 4. Render Critical Null Project TP-7 profile
            page.goto(f"http://127.0.0.1:8000/results/{test_ids['tp7']}", wait_until="networkidle")
            tp7_text = page.inner_text("body")
            assert "Insufficient Input — Not Rated" in tp7_text
            assert "Critical Blocking Null" in tp7_text

            browser.close()
    finally:
        for pid in test_ids.values():
            _delete_project_document(pid)


def _write_project_document(project_id, doc_data):
    """Writes a raw project document directly (Firestore if configured, else local fallback),
    bypassing the approve/score pipeline -- used only to seed a test fixture that reproduces a
    specific stored-data shape (approved_data present but with individual fields blanked out
    while extracted_data holds the real values), which the pipeline itself cannot produce."""
    from app.firestore import UPLOAD_DIR
    try:
        import firebase_admin
        from firebase_admin import firestore
        if firebase_admin._apps:
            db = firestore.client()
            db.collection("projects").document(project_id).set(doc_data)
            return
    except Exception:
        pass
    local_path = os.path.join(UPLOAD_DIR, f"firestore_{project_id}.json")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, default=str)


def _delete_project_document(project_id):
    from app.firestore import UPLOAD_DIR
    try:
        import firebase_admin
        from firebase_admin import firestore
        if firebase_admin._apps:
            firestore.client().collection("projects").document(project_id).delete()
    except Exception:
        pass
    local_path = os.path.join(UPLOAD_DIR, f"firestore_{project_id}.json")
    if os.path.exists(local_path):
        os.remove(local_path)


def test_review_screen_falls_back_to_extracted_for_blanked_scalar_and_p90_fields():
    """
    Reproduces the TP-1 production bug: approved_data exists (from an earlier partial/bad
    approval) with project_name and the three text p90_attestation fields blanked to "",
    while extracted_data holds the real values. The Review screen's load-time binding must
    fall back per-field to extracted_data for these scalars -- exactly as it already does for
    the offtakers/debt_instruments/dscr_schedule array fields -- rather than rendering (and on
    next submit, re-persisting) the blank.
    """
    from playwright.sync_api import sync_playwright

    project_id = "REVIEW-FALLBACK-TEST"
    extracted = {
        "project_name": "Real Project Name Pvt Ltd",
        "p90_attestation": {
            "p90_plf": 0.222,
            "p90_attestation_basis": "ATTESTED_P90",
            "p90_resource_study": "Real P90 Resource Study Reference",
            "p90_preparer": "Real P90 Preparer"
        }
    }
    approved = {
        "project_name": "",
        "p90_attestation": {
            "p90_plf": 0.222,
            "p90_attestation_basis": "",
            "p90_resource_study": "",
            "p90_preparer": ""
        }
    }
    _write_project_document(project_id, {
        "project_id": project_id,
        "status": "approved",
        "extracted_data": extracted,
        "approved_data": approved,
        "field_provenance": {}
    })

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:8000/review/{project_id}", wait_until="networkidle")

            name_val = page.input_value("#field-project_name")
            assert name_val == "Real Project Name Pvt Ltd", f"project_name rendered blank/wrong: {name_val!r}"

            page.click("button:has-text('5. P90 Attestation')")
            basis_val = page.eval_on_selector("#field-p90_attestation\\.p90_attestation_basis", "el => el.value")
            study_val = page.input_value("#field-p90_attestation\\.p90_resource_study")
            preparer_val = page.input_value("#field-p90_attestation\\.p90_preparer")
            assert basis_val == "ATTESTED_P90", f"p90_attestation_basis rendered blank: {basis_val!r}"
            assert study_val == "Real P90 Resource Study Reference", f"p90_resource_study rendered blank: {study_val!r}"
            assert preparer_val == "Real P90 Preparer", f"p90_preparer rendered blank: {preparer_val!r}"

            browser.close()
    finally:
        _delete_project_document(project_id)


def test_scored_at_refreshes_on_each_score_persist():
    """
    Regression test: run_approved_assessment_pipeline (the real Score & Rating / approve
    code path) previously persisted the score via a duplicated raw Firestore write that
    never included scored_at, so it only ever reflected whatever timestamp an earlier,
    unrelated call path had set. It must now stamp a fresh scored_at on every call.
    """
    import time
    from app.pipeline import run_approved_assessment_pipeline
    from app.firestore import get_project_document

    project_id = "SCORED-AT-REFRESH-TEST"
    tp1_inputs = dict(next(p["inputs"] for p in PROJECTS if p["id"] == "TP-1"))

    try:
        run_approved_assessment_pipeline(project_id, tp1_inputs)
        scored_at_1 = get_project_document(project_id).get("scored_at")
        assert scored_at_1 is not None

        time.sleep(1.5)

        run_approved_assessment_pipeline(project_id, tp1_inputs)
        scored_at_2 = get_project_document(project_id).get("scored_at")
        assert scored_at_2 is not None
        assert scored_at_2 != scored_at_1, "scored_at did not change across two successive scoring runs"
    finally:
        _delete_project_document(project_id)

