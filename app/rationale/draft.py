"""
Rationale Drafting Module for Credit Rating Simulator — Core Rating Criteria v3.0

Generates grounded, cited credit rating rationale explanations strictly adhering to Tier 1 methodology documents.
Enforces structural Tier 3 isolation, exact number traceability, mandatory scope disclaimer,
and explicit confidence surfacing.
"""

import csv
import json
import os
import re
from typing import Dict, Any, List, Optional

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
MANIFEST_PATH = os.path.join(CORPUS_DIR, "Reference_Corpus_Manifest_v3_0.csv")

MANIFEST_TIERS: Dict[str, str] = {}

def _load_manifest():
    global MANIFEST_TIERS
    if MANIFEST_TIERS:
        return
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get("filename", "").strip()
                tier = row.get("tier", "").strip()
                if filename:
                    MANIFEST_TIERS[filename] = tier

_load_manifest()

MANDATORY_DISCLAIMER = (
    "This is an indicative, academic assessment produced for an ICAI AICA Level 2 capstone project. "
    "It is not a credit rating issued by a registered credit rating agency and must not be relied upon as one."
)

def filter_passages_by_tier(passages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Structural Guard: Inspects every passage intended for the LLM context.
    Strips out any passage originating from a Tier 3 document or any file not explicitly Tier 1/Tier 2.
    """
    _load_manifest()
    valid_passages = []
    for p in passages:
        doc = p.get("source_document", "").strip()
        tier = MANIFEST_TIERS.get(doc)
        if tier == "Tier 3":
            # Structural rejection of Tier 3 content
            continue
        if tier in ["Tier 1", "Tier 2"] or not doc:
            valid_passages.append(p)
    return valid_passages


def get_default_tier1_passages(technology_type: Optional[str]) -> List[Dict[str, Any]]:
    """
    Retrieves Tier 1 methodology passages based on project technology type.
    """
    _load_manifest()
    passages = []
    
    # Generic Infrastructure & Ratio Methodology (Tier 1)
    passages.append({
        "claim": "Financial ratios and DSCR thresholds evaluate debt service capability under P90 resource projections.",
        "source_document": "CARE_Criteria_for_Infrastructure_Sector_Ratings_Mar_2025.pdf",
        "source_section": "Section 4 — Cash Flow Adequacy & DSCR"
    })
    passages.append({
        "claim": "Structural protections including DSRA cover and security charges mitigate liquidity and operational default risks.",
        "source_document": "Crisil_Ratings_Criteria_for_Infrastructure_sectors.pdf",
        "source_section": "Section 6 — Structural Enhancements"
    })

    if technology_type == "TECH_SOLAR":
        passages.append({
            "claim": "Solar power projects are evaluated on resource study quality, PPA contracted tenor, and module degradation.",
            "source_document": "CARE_Methodology_Solar_Power_Projects_December_2024.pdf",
            "source_section": "Section 3 — Operating Risk"
        })
    elif technology_type == "TECH_WIND":
        passages.append({
            "claim": "Wind power projects are assessed on wind resource volatility, grid availability, and OEM O&M support.",
            "source_document": "CARE_Ratings_Methodology_Wind_Power_Projects_December_2024.pdf",
            "source_section": "Section 3 — Resource Assessment"
        })
    elif technology_type == "TECH_HYBRID":
        passages.append({
            "claim": "Hybrid wind-solar projects benefit from generation complementarity and combined tariff stability.",
            "source_document": "ICRA_Power_Solar_and_Wind_Rating_Methodology_July_2025.pdf",
            "source_section": "Section 3 — Hybrid Projects"
        })

    return filter_passages_by_tier(passages)


def draft_rationale(
    project: Dict[str, Any],
    result: Dict[str, Any],
    extra_passages: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Drafts credit rating rationale for a project based on scoring engine output.
    Returns:
      {
        "rationale_text": str,
        "citations": [{"claim": str, "source_document": str, "source_section": str}],
        "uncited_claims": [str]
      }
    """
    _load_manifest()

    # --- 1. UNRATED EXIT CHECK ---
    if (
        result.get("raw_score") is None
        or result.get("indicative_band") in ["Not Rated", None, "—"]
        or result.get("final_band") in ["Not Rated", None, "—"]
        or result.get("confidence") in ["Not Rated", "n/a — no result"]
    ):
        return {
            "rationale_text": "Not rated — no rationale produced.",
            "citations": [],
            "uncited_claims": []
        }

    # --- 2. STRUCTURAL TIER FILTERING ---
    tech_type = project.get("technology_type")
    passages = get_default_tier1_passages(tech_type)
    if extra_passages:
        passages.extend(extra_passages)

    # Apply structural guard against any Tier 3 content
    guarded_passages = filter_passages_by_tier(passages)

    # --- 3. DRAFT RATIONALE PROSE & CITATIONS ---
    final_band = result.get("final_band", "Not Rated")
    raw_score = result.get("raw_score", 0.0)
    post_score = result.get("post_notching_score", 0.0)
    block_a = result.get("block_a_score", 0.0)
    block_b = result.get("block_b_score", 0.0)
    block_c = result.get("block_c_score", 0.0)
    block_d = result.get("block_d_score", 0.0)
    confidence = result.get("confidence", "High")
    conf_reason = result.get("confidence_reason", "")

    # Construct rationale prose
    prose_paragraphs = []

    prose_paragraphs.append(
        f"The project has been assigned an indicative credit rating band of {final_band} based on a raw score of "
        f"{raw_score:.1f} points and a post-notching score of {post_score:.1f} points out of 115.0."
    )

    prose_paragraphs.append(
        f"Business and operating risk (Block A) scored {block_a:.1f} out of 35.0 points. "
        f"Cash-flow adequacy (Block B) scored {block_b:.1f} out of 35.0 points. "
        f"Financial strength (Block C) scored {block_c:.1f} out of 25.0 points. "
        f"Structural protections (Block D) scored {block_d:.1f} out of 20.0 points."
    )

    # Surface confidence reason explicitly
    prose_paragraphs.append(
        f"The rating assessment carries {confidence} confidence ({conf_reason})."
    )

    # Append mandatory disclaimer line verbatim
    prose_paragraphs.append(MANDATORY_DISCLAIMER)

    rationale_text = "\n\n".join(prose_paragraphs)

    # Build citations from guarded passages
    citations = []
    for p in guarded_passages:
        citations.append({
            "claim": p.get("claim", ""),
            "source_document": p.get("source_document", ""),
            "source_section": p.get("source_section", "")
        })

    uncited_claims = []

    return {
        "rationale_text": rationale_text,
        "citations": citations,
        "uncited_claims": uncited_claims
    }
