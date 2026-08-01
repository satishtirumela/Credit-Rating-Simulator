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
    data = {"project_id": "TP-2-Mid-Wind"}

    response = client.post("/api/upload", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["project_id"] == "TP-2-Mid-Wind"
    assert len(res_data["files"]) == 2
    assert res_data["files"][0]["filename"] == "Template_1.docx"
    assert res_data["files"][1]["filename"] == "Template_2.xlsx"
