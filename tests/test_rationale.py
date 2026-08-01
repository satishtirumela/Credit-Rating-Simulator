"""
Unit Test Suite for Credit Rating Simulator Rationale Drafting Module (app/rationale/draft.py).
"""

import json
import os
import re
import pytest
from app.engine.scoring import score_project
from app.rationale.draft import (
    draft_rationale,
    filter_passages_by_tier,
    MANDATORY_DISCLAIMER,
    MANIFEST_TIERS
)

FIXTURES_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "reference_projects_v3_0.json"
)

def load_projects():
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["projects"]

PROJECTS = load_projects()


@pytest.mark.parametrize("project", PROJECTS, ids=[p["id"] for p in PROJECTS])
def test_rationale_reference_projects(project):
    pid = project["id"]
    inputs = project["inputs"]
    result = score_project(inputs)

    draft = draft_rationale(inputs, result)

    # 1. Unrated exit check for TP-7 and TP-8
    if pid in ["TP-7", "TP-8"]:
        assert draft["rationale_text"] == "Not rated — no rationale produced."
        assert len(draft["citations"]) == 0
        assert len(draft["uncited_claims"]) == 0
        return

    rationale_text = draft["rationale_text"]
    citations = draft["citations"]

    # 2. Scope disclaimer must be present verbatim
    assert MANDATORY_DISCLAIMER in rationale_text, f"[{pid}] Mandatory disclaimer missing from rationale text"

    # 3. No citation references a Tier 2 or Tier 3 document
    for c in citations:
        doc = c.get("source_document", "")
        tier = MANIFEST_TIERS.get(doc)
        assert tier != "Tier 3", f"[{pid}] Citation references Tier 3 document: {doc}"
        assert tier != "Tier 2", f"[{pid}] Citation references Tier 2 document: {doc}"

    # 4. Number Traceability: every numeric digit sequence in rationale_text must be traceable to result
    digit_sequences = re.findall(r"\b\d+(?:\.\d+)?\b", rationale_text)
    
    # Collect all numbers present in result dictionary
    result_numbers = set()
    for k, v in result.items():
        if isinstance(v, (int, float)):
            result_numbers.add(f"{v:.1f}")
            result_numbers.add(f"{v}")
            result_numbers.add(str(v))

    # Allowed fixed constants (block maxes, level numbers, section numbers)
    allowed_constants = {"35.0", "35", "25.0", "25", "20.0", "20", "115.0", "115", "1", "2", "3", "4", "5", "6", "7", "8", "90", "95", "100", "0"}

    for num_str in digit_sequences:
        is_in_result = any(num_str in str(v) for v in result.values() if v is not None)
        assert is_in_result or num_str in allowed_constants, f"[{pid}] Untraceable number '{num_str}' in rationale text"

    # 5. Moderate confidence surfacing for TP-2, TP-4, TP-6
    if pid in ["TP-2", "TP-4", "TP-6"]:
        conf_reason = result["confidence_reason"]
        assert result["confidence"] == "Moderate", f"[{pid}] Expected Moderate confidence"
        assert conf_reason in rationale_text, f"[{pid}] Confidence reason '{conf_reason}' missing from rationale text"


def test_rationale_poisoning_attack():
    """
    Poisoning Test: Directly injects a Tier 3 document passage (bypassing normal retrieval)
    and asserts that the structural guard filters it out completely.
    """
    project = PROJECTS[0]  # TP-1
    result = score_project(project["inputs"])

    # Malicious passage constructed from a Tier 3 rating rationale
    tier3_poison_passage = {
        "claim": "Adani Green Energy Twenty Five B Limited has outstanding debt of 450 crore.",
        "source_document": "Adani_Green_Energy_Twenty_Five_B_Limited_Wind__Solar.pdf",
        "source_section": "Section 1 — Debt Overview"
    }

    # Pass directly to filter_passages_by_tier
    filtered = filter_passages_by_tier([tier3_poison_passage])
    assert len(filtered) == 0, "Structural guard failed: Tier 3 poison passage was not stripped!"

    # Pass via extra_passages in draft_rationale
    draft = draft_rationale(project["inputs"], result, extra_passages=[tier3_poison_passage])
    
    # Assert no Tier 3 document or company name appears in citations or rationale_text
    for c in draft["citations"]:
        assert c["source_document"] != "Adani_Green_Energy_Twenty_Five_B_Limited_Wind__Solar.pdf"
        assert MANIFEST_TIERS.get(c["source_document"]) != "Tier 3"

    assert "Adani" not in draft["rationale_text"]
    assert "450" not in draft["rationale_text"]


def test_unrated_exit_tp7_tp8():
    """
    Explicitly test that unrated projects TP-7 and TP-8 produce no rationale text at all.
    """
    for pid in ["TP-7", "TP-8"]:
        p = next(proj for proj in PROJECTS if proj["id"] == pid)
        res = score_project(p["inputs"])
        draft = draft_rationale(p["inputs"], res)

        assert draft["rationale_text"] == "Not rated — no rationale produced."
        assert draft["citations"] == []
        assert draft["uncited_claims"] == []
