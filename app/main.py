"""
FastAPI application exposing the Credit Rating Simulator scoring engine HTTP endpoint
and template file upload screen.
"""

import json
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import jsonschema

from app.engine.scoring import score_project
from app.rationale.draft import draft_rationale
from app.storage import save_project_file

app = FastAPI(
    title="Credit Rating Simulator API & Web App",
    description="HTTP API endpoint for CORE v3.0 credit rating scoring engine and file upload module.",
    version="3.0.0"
)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "project.schema.json")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "upload.html")


def _get_schema() -> Dict[str, Any]:
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as sf:
            return json.load(sf)
    return {}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Credit Rating Simulator API", "version": "3.0.0"}


@app.get("/", response_class=HTMLResponse)
@app.get("/upload", response_class=HTMLResponse)
def get_upload_page():
    """Serves the plain template upload HTML screen."""
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Upload Screen</h1><p>Template not found.</p></body></html>"


@app.post("/api/upload")
async def upload_templates(
    project_id: str = Form("default_project"),
    template1: UploadFile = File(..., description="Key Input Template 1 (.docx)"),
    template2: UploadFile = File(..., description="Key Input Template 2 (.xlsx)")
) -> Dict[str, Any]:
    """
    Accepts .docx and .xlsx template files, validates file extensions,
    and stores them under projects/{project_id}/ in Firebase Storage.
    """
    if not template1.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Template 1 must be a .docx file")

    if not template2.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Template 2 must be a .xlsx file")

    t1_bytes = await template1.read()
    t2_bytes = await template2.read()

    res1 = save_project_file(project_id, template1.filename, t1_bytes)
    res2 = save_project_file(project_id, template2.filename, t2_bytes)

    return {
        "status": "success",
        "message": f"Successfully uploaded template files for project '{project_id}'",
        "project_id": project_id,
        "files": [res1, res2]
    }


@app.post("/score")
def score(
    project: Dict[str, Any] = Body(..., description="Project inputs matching project.schema.json or raw Appendix B dict"),
    validate_schema: bool = False,
    include_rationale: bool = False
) -> Dict[str, Any]:
    """
    Accepts project inputs as JSON, executes score_project() through the 5-stage pipeline,
    and returns the complete scoring output object.
    """
    if not project or not isinstance(project, dict):
        raise HTTPException(status_code=400, detail="Invalid request body: expected a JSON object")

    if validate_schema:
        schema = _get_schema()
        if schema:
            try:
                jsonschema.validate(instance=project, schema=schema)
            except jsonschema.ValidationError as err:
                raise HTTPException(status_code=422, detail=f"JSON Schema Validation Error: {err.message}")

    result = score_project(project)

    if include_rationale:
        rationale_res = draft_rationale(project, result)
        result["rationale"] = rationale_res

    return result
