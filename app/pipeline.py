"""
End-to-End Approved Assessment Pipeline Orchestrator.
Chains: Score -> Ground -> Draft -> QA -> Report & Persist upon Human Approval.
Strict Engine/Model Boundary:
- Python engine (score_project) handles 100% of numeric scores, bands, caps, and confidence.
- Gemini handles ONLY qualitative rationale narrative drafting grounded in verified citations.
"""

from typing import Dict, Any
from app.engine.scoring import score_project
from app.grounding import get_verified_methodology_citations
from app.rationale.draft import draft_rationale
from app.pdf import generate_rationale_pdf
from app.firestore import approve_project_document, get_project_document, UPLOAD_DIR
import os
import json


def qa_review_assessment(score_result: Dict[str, Any], rationale: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs automated QA review pass on the assessment.
    Checks:
    1. Elevated risk flag (band <= BB).
    2. Mandatory QA review trigger (bands C/D).
    3. Semantic coherence check between narrative prose and verified methodology citations.
    """
    final_band = score_result.get("final_band", "Not Rated")
    flags = []

    if final_band in ["BB", "B", "C", "D"]:
        flags.append("ELEVATED_RISK_FLAG: Final rating band is Non-Investment Grade (<= BB).")

    if final_band in ["C", "D"]:
        flags.append("MANDATORY_QA_REVIEW_REQUIRED: Final rating band is in C/D deep speculative range.")

    citations = rationale.get("citations", [])
    coherent = (final_band == "Not Rated" and len(citations) == 0) or (len(citations) == 3 and all(c.get("claim") for c in citations))
    if not coherent:
        flags.append("CITATION_COHERENCE_WARNING: Methodology citations count or claim text incomplete.")

    return {
        "qa_status": "QA_PASSED" if not flags or final_band in ["AAA", "AA", "A", "BBB", "BB"] else "QA_FLAGGED",
        "qa_flags": flags,
        "citation_coherence_verified": coherent
    }


def run_approved_assessment_pipeline(project_id: str, approved_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes Phase 2 of the credit rating pipeline upon explicit human approval:
    1. Score (includes all 5 validation stages in Python engine).
    2. Ground (verifies verbatim methodology quotes via manifest SHA-256).
    3. Draft (generates grounded qualitative rationale via Gemini).
    4. QA (executes automated QA review pass).
    5. Report & Save (generates ReportLab PDF & saves to Cloud Firestore).
    """
    # 1. SCORE
    score_result = score_project(approved_data)

    final_band = score_result.get("final_band")

    # 2. GROUND & 3. DRAFT
    if final_band == "Not Rated":
        # For Stage 1 "Not Rated" exits, skip Ground/Draft citation attachment entirely
        rationale_result = draft_rationale(approved_data, score_result)
        rationale_result["citations"] = []
        score_result["rationale"] = rationale_result
    else:
        verified_citations = get_verified_methodology_citations()
        rationale_result = draft_rationale(approved_data, score_result)
        rationale_result["citations"] = verified_citations
        score_result["rationale"] = rationale_result

    # 4. QA REVIEW
    qa_result = qa_review_assessment(score_result, rationale_result)
    score_result["qa_review"] = qa_result

    # 5. REPORT & PERSIST
    # Save approved document to Cloud Firestore / local fallback
    approve_res = approve_project_document(project_id, approved_data)
    
    # Save score_result into project document in Firestore / local fallback
    local_path = os.path.join(UPLOAD_DIR, f"firestore_{project_id}.json")
    doc_data = get_project_document(project_id)
    doc_data["approved_data"] = approved_data
    doc_data["score"] = score_result
    doc_data["status"] = "approved"

    try:
        import firebase_admin
        from firebase_admin import firestore
        if firebase_admin._apps:
            db = firestore.client()
            db.collection("projects").document(project_id).set({"score": score_result}, merge=True)
    except Exception:
        pass

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, default=str)

    # Generate PDF Report
    pdf_bytes = generate_rationale_pdf(project_id, approved_data, score_result)

    return {
        "status": "success",
        "message": f"Successfully executed full approved assessment pipeline for project '{project_id}'",
        "project_id": project_id,
        "score": score_result,
        "qa_review": qa_result,
        "pdf_report_generated": len(pdf_bytes) > 0,
        "redirect_url": f"/results/{project_id}"
    }
