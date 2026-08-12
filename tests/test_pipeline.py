"""
Unit Test Suite for Credit Rating Simulator Pipeline Orchestrator (app/pipeline.py).
"""

from app.pipeline import qa_review_assessment


def _verified_citation(n=1):
    return {
        "claim": f"Sample verified claim {n}.",
        "source_document": f"Sample_Document_{n}.pdf",
        "source_section": f"Section {n}",
        "grounding_status": "VERIFIED_VERBATIM"
    }


def test_qa_coherence_true_for_two_item_technology_citation_set():
    """
    The old check hardcoded len(citations) == 3, matching only the static catalog's fixed size.
    Citation count now varies by technology_type (e.g. 2 items for an unrecognized/default tech
    branch in get_grounded_methodology_citations()) -- coherence must not depend on a specific count.
    """
    score_result = {"final_band": "A"}
    rationale = {"citations": [_verified_citation(1), _verified_citation(2)]}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is True
    assert not any("CITATION_COHERENCE_WARNING" in f for f in result["qa_flags"])


def test_qa_coherence_true_for_three_item_technology_citation_set():
    score_result = {"final_band": "AAA"}
    rationale = {"citations": [_verified_citation(1), _verified_citation(2), _verified_citation(3)]}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is True


def test_qa_coherence_true_for_not_rated_with_empty_citations():
    score_result = {"final_band": "Not Rated"}
    rationale = {"citations": []}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is True


def test_qa_coherence_false_for_empty_citations_on_rated_band():
    score_result = {"final_band": "BBB"}
    rationale = {"citations": []}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is False
    assert any("CITATION_COHERENCE_WARNING" in f for f in result["qa_flags"])


def test_qa_coherence_false_when_citation_missing_grounding_status():
    """
    A citation dict with claim/source_document but no grounding_status (i.e. never actually
    verified) must not read as coherent -- coherence means genuinely verified, not just present.
    """
    score_result = {"final_band": "A"}
    unverified = {"claim": "Some claim.", "source_document": "Some_Doc.pdf", "source_section": "S1"}
    rationale = {"citations": [unverified]}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is False


def test_qa_coherence_false_when_citation_missing_claim_or_source_document():
    score_result = {"final_band": "A"}
    no_claim = {"claim": "", "source_document": "Some_Doc.pdf", "grounding_status": "VERIFIED_VERBATIM"}
    rationale = {"citations": [no_claim]}

    result = qa_review_assessment(score_result, rationale)

    assert result["citation_coherence_verified"] is False
