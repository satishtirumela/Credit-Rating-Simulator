"""
Unit Test Suite for Credit Rating Simulator Grounding Module (app/grounding.py).
"""

import pytest
from app.grounding import verify_methodology_citations


def test_verify_methodology_citations_passes_genuine_verbatim_claim():
    """
    Positive path: a citation whose claim genuinely is a verbatim substring of its named
    corpus PDF must come back with grounding_status = VERIFIED_VERBATIM and a display_claim,
    with the original claim/source_document/source_section fields preserved.

    This claim/PDF pairing is drawn directly from draft.py's get_grounded_methodology_citations()
    -- it is the one of the five hardcoded claims confirmed (by manual verification during this
    task) to actually be a verbatim substring of its named PDF.
    """
    citations = [{
        "claim": (
            "The financial risk profile is primarily driven by the DSCR over the loan life of "
            "the project. It can be driven by minimum DSCR, average DSCR or a combination of "
            "both depending on variability of cashflows. The calculation shall solely be based "
            "on project cash flows, without considering parent support or debt service reserve "
            "account (DSRA)."
        ),
        "source_document": "Crisil_Ratings_Criteria_for_Infrastructure_sectors.pdf",
        "source_section": "Section 6 — Projected Financial Performance & DSRA (Page 51)"
    }]

    verified = verify_methodology_citations(citations)

    assert len(verified) == 1
    v = verified[0]
    assert v["grounding_status"] == "VERIFIED_VERBATIM"
    assert v["claim"] == citations[0]["claim"]
    assert v["source_document"] == "Crisil_Ratings_Criteria_for_Infrastructure_sectors.pdf"
    assert v["source_section"] == citations[0]["source_section"]
    assert "display_claim" in v and v["display_claim"]


def test_verify_methodology_citations_empty_list_returns_empty_list():
    assert verify_methodology_citations([]) == []


def test_verify_methodology_citations_raises_on_non_verbatim_claim():
    """
    Negative path: a claim that is not a verbatim substring of its named PDF must raise
    RuntimeError rather than being silently dropped or downgraded.

    This claim/PDF pairing was previously the live claim in draft.py's
    get_grounded_methodology_citations() for the CARE_Criteria_for_Infrastructure_Sector_Ratings
    document -- confirmed by manual verification to NOT be a verbatim substring of the real PDF
    text (the real document continues "...DSCR is [running-header artifact] computed under base
    case scenarios and under stress scenarios", not "...DSCR is evaluated along with debt service
    protection metrics..." as this text states). draft.py has since been fixed to use a genuine
    verbatim claim for that document; this fabricated text is kept here only as a known-bad
    negative-path fixture, not as a description of draft.py's current content.
    """
    citations = [{
        "claim": (
            "In debt protection metrics, one of the key ratios to determine repayment capacity, "
            "DSCR is evaluated along with debt service protection metrics, reserve accounts such "
            "as debt service reserve account (DSRA), and financial flexibility."
        ),
        "source_document": "CARE_Criteria_for_Infrastructure_Sector_Ratings_Mar_2025.pdf",
        "source_section": "Section 4 — Cash Flow Adequacy & DSCR (Page 3)"
    }]

    with pytest.raises(RuntimeError, match="not a verbatim substring"):
        verify_methodology_citations(citations)


def test_verify_methodology_citations_raises_on_unknown_source_document():
    citations = [{
        "claim": "This document does not exist in the corpus.",
        "source_document": "Nonexistent_Document_That_Is_Not_In_Corpus.pdf",
        "source_section": "Section 1"
    }]

    with pytest.raises(RuntimeError, match="failed SHA-256 or manifest verification"):
        verify_methodology_citations(citations)
