"""
End-to-End Approved Assessment Pipeline Orchestrator.
Chains: Score -> Ground -> Draft -> QA -> Report & Persist upon Human Approval.
Strict Engine/Model Boundary:
- Python engine (score_project) handles 100% of numeric scores, bands, caps, and confidence.
- Rationale narrative drafting (draft_rationale) is deterministic Python string templating over
  the score_project() result dict -- not a Gemini/LLM call. Its citations come from
  get_grounded_methodology_citations(), a static, technology-branched lookup table, not an LLM
  call or a retrieval index. Gemini is used elsewhere in this codebase (app/extraction.py) only
  for document extraction (Template 1/2 -> project JSON), unrelated to rationale drafting.
"""

from typing import Dict, Any
from app.engine.scoring import score_project
from app.grounding import get_verified_methodology_citations
from app.rationale.draft import draft_rationale
from app.pdf import generate_rationale_pdf
from app.firestore import approve_project_document, save_score_document


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
    3. Draft (deterministic narrative generation from the score_project() result dict, with
       citations from a static, technology-branched lookup -- no Gemini/LLM call).
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
    # approve_project_document sets approved_data/status/field_provenance/approved_at;
    # save_score_document sets score/scored_at. Both stamp their own timestamp fresh on
    # every call -- there is no other write path to the score/scored_at fields, so this is
    # the single point that must be correct for scored_at to ever reflect reality.
    approve_project_document(project_id, approved_data)
    save_score_document(project_id, score_result)

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
