"""
FastAPI application exposing the Credit Rating Simulator scoring engine HTTP endpoint
and template file upload screen.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

sys_path_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_path_root not in sys.path:
    sys.path.insert(0, sys_path_root)

from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form, Response, Request
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

@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path in ["/", "/home", "/upload"] or path.startswith("/review") or path.startswith("/results"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

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


@app.get("/api/display-labels")
def get_display_labels() -> Dict[str, Any]:
    """
    Serves the single shared enum-code / field-name / corpus-filename display-label lookup
    (schemas/display_labels.json + corpus/Corpus_Display_Names_v3_0.csv) so the frontend can
    route every raw code, field path, or corpus filename shown to a user through the exact
    same table the PDF generator (app/labels.py, app/pdf.py) already uses -- never a second,
    independently-maintained copy.
    """
    from app.labels import get_display_labels as _get_display_labels
    from app.pdf import get_corpus_display_names

    labels = _get_display_labels()
    labels["corpus_display_names"] = get_corpus_display_names()
    return labels


# The canonical reference project set for the Home screen's "Reference Projects & Saved
# Assessments" table -- an explicit list, not "whatever documents currently exist in
# Firestore", so a stray test/scratch document can never silently appear on the Home page
# again (see this session's Firestore cleanup). TP-5/TP-6 are canonical CORE fixture ids but
# have no live Firestore document yet; they're intentionally omitted below rather than shown
# as fabricated placeholder rows. TP-2-Mid-Wind was retired from this list -- it had no
# approved_data/extracted_data in Firestore, and the Home "View Benchmark" button now
# points directly at TP-2, which does have a scored reference fixture.
CANONICAL_PROJECT_IDS = ["TP-1", "TP-2", "TP-3", "TP-4", "TP-7", "TP-8", "NEG-CAP-1", "SolairePower"]


@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
def get_home_page():
    """Serves the Home / New Assessment HTML screen with a live Firestore-backed project list."""
    home_path = os.path.join(os.path.dirname(__file__), "templates", "home.html")
    if not os.path.exists(home_path):
        return "<html><body><h1>Home Screen</h1></body></html>"

    with open(home_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    from app.firestore import get_project_document
    from app.labels import label_for_enum

    table_rows_html = ""
    for pid in CANONICAL_PROJECT_IDS:
        doc = get_project_document(pid)
        project_data = doc.get("approved_data") or doc.get("extracted_data")
        if not project_data:
            # No real record for this id yet (never uploaded/approved) -- omit rather than
            # show a fabricated row, same reasoning as TP-5/TP-6 above.
            continue

        tech_label = label_for_enum(project_data.get("technology_type")) or "—"
        try:
            capacity_val = float(project_data.get("installed_capacity_mw_ac"))
            capacity_label = f"{capacity_val:g} MW"
        except (TypeError, ValueError):
            capacity_label = "—"

        # Always recompute fresh from approved_data rather than trust a persisted score --
        # a stored score can predate an engine fix and would otherwise show a stale band
        # here, exactly the kind of cross-screen inconsistency this table was fixed for.
        if doc.get("status") == "approved" and doc.get("approved_data"):
            score = score_project(doc["approved_data"])
        else:
            score = {}

        final_band = score.get("final_band") or "Not Rated"
        cap_triggers = score.get("cap_triggers") or []
        is_capped = any(t.get("binding") for t in cap_triggers)

        if final_band == "Not Rated":
            status_label = "Not Rated"
            status_class = "status-draft"
        elif is_capped:
            status_label = f"Capped ({final_band})"
            status_class = "status-approved"
        else:
            status_label = final_band
            status_class = "status-approved"

        table_rows_html += f"""
        <tr>
            <td><strong>{pid}</strong></td>
            <td>{tech_label}</td>
            <td><span class="num">{capacity_label}</span></td>
            <td><span class="badge-status {status_class}">{status_label}</span></td>
            <td>
                <a href="/review/{pid}" class="action-link">Review</a>
                <a href="/results/{pid}" class="action-link">Results</a>
            </td>
        </tr>
        """

    html_rendered = html_template.replace('<!-- FIRESTORE_PROJECT_ROWS -->', table_rows_html)
    return html_rendered


@app.get("/upload", response_class=HTMLResponse)
def get_upload_page():
    """Serves the template upload HTML screen."""
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Upload Screen</h1><p>Template not found.</p></body></html>"


def _load_reference_projects() -> list:
    ref_path = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "reference_projects_v3_0.json")
    if os.path.exists(ref_path):
        try:
            with open(ref_path, "r", encoding="utf-8") as f:
                return json.load(f).get("projects", [])
        except Exception:
            pass
    return []


@app.get("/results", response_class=HTMLResponse)
def get_results_page_default():
    """
    Serves the Results screen with no project id in the URL (e.g. from the main nav's
    Results tab, which has no specific project in context). The client-side script resolves
    an active project from session state and redirects to /results/{id}, or renders an
    explicit empty state if no project has been reviewed or uploaded yet in this session --
    it must never fall back to a hardcoded reference project.
    """
    results_path = os.path.join(os.path.dirname(__file__), "templates", "results.html")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Results Screen</h1></body></html>"


@app.get("/results/{project_id}", response_class=HTMLResponse)
def get_results_page(project_id: str):
    """Serves the CORE section 8.4 compliant Results HTML screen with server-side pre-rendered content."""
    results_path = os.path.join(os.path.dirname(__file__), "templates", "results.html")
    if not os.path.exists(results_path):
        return "<html><body><h1>Results Screen</h1></body></html>"

    with open(results_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    from app.firestore import get_project_document
    from app.engine.scoring import score_project

    doc = get_project_document(project_id)
    project_data = doc.get("approved_data") or doc.get("extracted_data")

    # Fallback to reference projects fixture if not in Firestore
    if not project_data:
        ref_projs = _load_reference_projects()
        ref = next((p for p in ref_projs if p["id"] == project_id or p["id"] == project_id.split("-")[0]), None)
        if ref:
            project_data = ref["inputs"]

    if not project_data:
        return html_template

    # Always recompute: never serve a persisted score -- the stored value may predate engine fixes
    # and would silently contaminate results.html with stale values (BUG 4 root cause)
    score = score_project(project_data)

    # Server-side HTML pre-rendering block injected into initial-state
    if score.get("final_band") == "Not Rated" or score.get("confidence") == "Not Rated":
        validation_results = score.get("validation_results", [])
        blocking_rules = [v for v in validation_results if v.get("outcome") == "Block"]

        if blocking_rules:
            block_detail = "; ".join(f"{b['rule']}: {b['detail']}" for b in blocking_rules)
            ssr_content = f"""
            <div id="ssr-container">
                <h1>{project_id}</h1>
                <h2>Validation Block -- Not Rated</h2>
                <div class="banner banner-cap">Validation Block Triggered -- {block_detail}</div>
                <p>Pipeline Halted at Stage 3 Validation -- Rule V1: Average DSCR below Minimum DSCR</p>
            </div>
            """
        else:
            ssr_content = f"""
            <div id="ssr-container">
                <h1>{project_id}</h1>
                <h2>Insufficient Input -- Not Rated</h2>
                <p>Critical Blocking Null</p>
            </div>
            """
    else:
        raw_score = score.get("raw_score", 0.0)
        post_score = score.get("post_notching_score", 0.0)
        ind_band = score.get("indicative_band", "N/A")
        final_band = score.get("final_band", "N/A")
        cap_notice = score.get("cap_notice", "")
        conf = score.get("confidence", "High")
        conf_reason = score.get("confidence_reason", "")
        
        blkA = score.get("block_a_score", 0.0)
        blkB = score.get("block_b_score", 0.0)
        blkC = score.get("block_c_score", 0.0)
        blkD = score.get("block_d_score", 0.0)

        cap_html = f'<div class="banner banner-cap">{cap_notice}</div>' if cap_notice else ''
        band_badge_html = f'<div class="band-badge band-{final_band.lower()}">{final_band}</div>'

        rationale_obj = score.get("rationale", {})
        exec_summary = rationale_obj.get("executive_summary") or rationale_obj.get("rationale_text", "Rationale report generated.")
        citations_list = rationale_obj.get("citations", [])

        citations_html = ""
        for idx, cit in enumerate(citations_list):
            claim_text = cit.get("display_claim") or cit.get("claim")
            citations_html += f"""
            <details open>
                <summary>Methodology Citation [{idx+1}]: {cit.get("source_document","")} ({cit.get("source_section","")})</summary>
                <div class="citation-text">"{claim_text}"</div>
            </details>
            """

        ssr_content = f"""
        <div id="ssr-container">
            <h1>{project_id}</h1>
            {band_badge_html}
            {cap_html}
            <p>Raw score: {raw_score:.1f} | Post-notching score: {post_score:.1f}</p>
            <p>Indicative band: {ind_band} | Final band: {final_band}</p>
            <p>Confidence: {conf} ({conf_reason})</p>
            <p>Block A: {blkA:.1f} | Block B: {blkB:.1f} | Block C: {blkC:.1f} | Block D: {blkD:.1f}</p>
            <div class="rationale-summary">{exec_summary}</div>
            {citations_html}
        </div>
        """

    html_rendered = html_template.replace('<!-- SSR_CONTENT -->', ssr_content)
    return html_rendered


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

    extraction_result = None
    if os.getenv("GEMINI_API_KEY"):
        try:
            from app.extraction import extract_project_data
            extraction_result = extract_project_data(project_id, t1_bytes, t2_bytes)
        except RuntimeError as e:
            err_msg = str(e)
            status_code = 429 if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) else 503
            raise HTTPException(
                status_code=status_code,
                detail=f"Gemini API error: {err_msg}"
            )
        except Exception as e:
            extraction_result = {"error": f"Extraction parsing failed: {str(e)}"}

    return {
        "status": "success",
        "message": f"Successfully uploaded template files for project '{project_id}'",
        "project_id": project_id,
        "files": [res1, res2],
        "extraction": extraction_result
    }


@app.get("/review", response_class=HTMLResponse)
def review_page_default():
    """
    Serves the Review screen with no project id in the URL (e.g. from the main nav's Review
    tab, which has no specific project in context). The client-side script resolves an active
    project from session state and redirects to /review/{id}, or renders an explicit empty
    state if no project has been reviewed or uploaded yet in this session -- it must never
    fall back to a hardcoded reference project.
    """
    html_path = os.path.join(os.path.dirname(__file__), "templates", "review.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Review Screen</h1><p>Template not found.</p></body></html>"


@app.get("/review/{project_id}", response_class=HTMLResponse)
def review_page(project_id: str):
    """
    Renders interactive Review UI for project input inspection & editing.
    """
    html_path = os.path.join(os.path.dirname(__file__), "templates", "review.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Review Screen</h1><p>Template not found.</p></body></html>"


@app.get("/api/projects/{project_id}")
def get_project_api(project_id: str) -> Dict[str, Any]:
    """
    Returns the stored project record from Cloud Firestore. If the project has been
    approved, the score is always recomputed fresh rather than served from the stored
    document -- a persisted score may predate engine fixes and would otherwise be
    served silently stale to the results screen's fetchAssessment() call, which only
    triggers a fresh /score POST when no score is present at all (same root cause
    as BUG 4 in get_results_page above).
    """
    from app.firestore import get_project_document
    from app.rationale.draft import draft_rationale

    doc = get_project_document(project_id)

    if doc.get("status") == "approved" and doc.get("approved_data"):
        project_data = doc["approved_data"]
        result = score_project(project_data)
        result["rationale"] = draft_rationale(project_data, result)
        doc["score"] = result
    else:
        # There is no currently-approved data to score against (project was never approved,
        # or approved_data is missing/null even though status still reads "approved"). Any
        # score field persisted from an earlier state no longer corresponds to this document's
        # current approved_data and must never be served as if it were current -- the client's
        # fetchAssessment() only re-scores when no score is present at all, so a stale cached
        # score here would otherwise be displayed unchanged and unvalidated.
        doc["score"] = None

    return doc


@app.post("/api/projects/{project_id}/approve")
def approve_project_api(project_id: str, approved_data: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Computes leaf field provenance, saves approved_data, field_provenance, and status = 'approved'
    to Cloud Firestore, and executes Phase 2 grounded assessment pipeline (Score -> Ground -> Draft -> QA -> Report).
    """
    if not approved_data or not isinstance(approved_data, dict):
        raise HTTPException(status_code=400, detail="Invalid request body: expected JSON object")
    from app.pipeline import run_approved_assessment_pipeline
    try:
        return run_approved_assessment_pipeline(project_id, approved_data)
    except jsonschema.ValidationError as err:
        raise HTTPException(status_code=422, detail=f"JSON Schema Validation Error: {err.message}")


@app.post("/api/projects/{project_id}/score")
def score_approved_project_api(project_id: str, include_rationale: bool = True) -> Dict[str, Any]:
    """
    Scores a project directly from its approved_data in Cloud Firestore.
    Enforces scoring approval gate (returns HTTP 400 if status != 'approved').
    Persists score output to Firestore under 'score' key.
    """
    from app.firestore import get_project_document, save_score_document
    from app.rationale.draft import draft_rationale

    doc = get_project_document(project_id)
    if doc.get("status") != "approved" or not doc.get("approved_data"):
        raise HTTPException(status_code=400, detail="Project inputs must be reviewed and approved before scoring")

    project_data = doc["approved_data"]
    result = score_project(project_data)

    # Always generate grounded rationale for full report persistence
    result["rationale"] = draft_rationale(project_data, result)

    # Persist score result to Cloud Firestore
    save_score_document(project_id, result)

    return result


@app.get("/api/projects/{project_id}/download-rationale")
def download_rationale_pdf(project_id: str):
    """
    Generates and streams a PDF credit rating rationale report for an approved and scored project.
    """
    from app.firestore import get_project_document, save_score_document
    from app.rationale.draft import draft_rationale
    from app.pdf import generate_rationale_pdf, build_rationale_filename

    doc = get_project_document(project_id)
    if doc.get("status") != "approved" or not doc.get("approved_data"):
        raise HTTPException(status_code=400, detail="Project inputs must be reviewed and approved before downloading rationale PDF")

    project_data = doc["approved_data"]

    # Always recompute: a stored score may predate engine fixes and would otherwise be
    # streamed into a PDF as silently stale data (same root cause as BUG 4).
    score_result = score_project(project_data)
    score_result["rationale"] = draft_rationale(project_data, score_result)
    save_score_document(project_id, score_result)

    pdf_bytes = generate_rationale_pdf(project_id, project_data, score_result)
    filename = build_rationale_filename(project_id, project_data)

    headers = {
        "Content-Disposition": f'inline; filename="{filename}"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


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
        from app.rationale.draft import draft_rationale
        result["rationale"] = draft_rationale(project, result)

    return result
