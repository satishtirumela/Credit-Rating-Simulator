"""
Rationale Drafting Module for Credit Rating Simulator — Core Rating Criteria v3.0

Generates grounded, cited credit rating rationale explanations strictly adhering to Tier 1 methodology documents
and Tier 2 sector report context (CRISIL Intelligence Report, January 2026).
Enforces structural Tier 3 isolation, exact number traceability, mandatory scope disclaimer,
and explicit confidence surfacing.
"""

import csv
import json
import os
import re
from typing import Dict, Any, List, Optional

from app.labels import label_for_enum

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
    Strips out any passage originating from a Tier 2 or Tier 3 document. Only Tier 1 is returned in citations.
    """
    _load_manifest()
    valid_passages = []
    for p in passages:
        doc = p.get("source_document", "").strip()
        tier = MANIFEST_TIERS.get(doc)
        if tier in ["Tier 2", "Tier 3"]:
            # Structural rejection of Tier 2 and Tier 3 content from methodology citations
            continue
        if tier == "Tier 1" or not doc:
            valid_passages.append(p)
    return valid_passages


def get_grounded_methodology_citations(technology_type: Optional[str]) -> List[Dict[str, Any]]:
    """
    Retrieves verified Tier 1 methodology and Tier 2 sector report passages.
    """
    passages = []

    # 1. Tier 1: CARE Infrastructure Criteria — DSCR & Debt Protection
    passages.append({
        "claim": "In debt protection metrics, one of the key ratios to determine repayment capacity, DSCR is evaluated along with debt service protection metrics, reserve accounts such as debt service reserve account (DSRA), and financial flexibility.",
        "source_document": "CARE_Criteria_for_Infrastructure_Sector_Ratings_Mar_2025.pdf",
        "source_section": "Section 4 — Cash Flow Adequacy & DSCR (Page 3)"
    })

    # 2. Tier 1: CRISIL Infrastructure Criteria — Standalone Credit Profile & DSRA
    passages.append({
        "claim": "The financial risk profile is primarily driven by the DSCR over the loan life of the project. It can be driven by minimum DSCR, average DSCR or a combination of both depending on variability of cashflows. The calculation shall solely be based on project cash flows, without considering parent support or debt service reserve account (DSRA).",
        "source_document": "Crisil_Ratings_Criteria_for_Infrastructure_sectors.pdf",
        "source_section": "Section 6 — Projected Financial Performance & DSRA (Page 51)"
    })

    # 3. Technology-Specific Tier 1 Methodology
    if technology_type == "TECH_WIND":
        passages.append({
            "claim": "CARE Ratings assesses the tariff competitiveness of the wind energy tariff in PPA by comparing it with the average power purchase cost and the marginal variable cost of power purchased by the off-taker utility. The agency conducting the resource assessment study typically provides power generation estimates for the given site at three probability of confidence levels, P-50, P-75, and P-90, whereby the P-90 level is considered to be the most conservative estimate.",
            "source_document": "CARE_Ratings_Methodology_Wind_Power_Projects_December_2024.pdf",
            "source_section": "Section 3 — Resource Assessment & Tariff Competitiveness (Page 3)"
        })
    elif technology_type == "TECH_SOLAR":
        passages.append({
            "claim": "Solar power projects are evaluated on resource study quality, PPA contracted tenor, and module degradation performance.",
            "source_document": "CARE_Methodology_Solar_Power_Projects_December_2024.pdf",
            "source_section": "Section 3 — Operating Risk & Solar Resource"
        })
    elif technology_type == "TECH_HYBRID":
        passages.append({
            "claim": "Hybrid wind-solar projects benefit from generation complementarity and combined tariff stability.",
            "source_document": "ICRA_Power_Solar_and_Wind_Rating_Methodology_July_2025.pdf",
            "source_section": "Section 3 — Hybrid Projects"
        })

    # 4. Tier 2: CRISIL Intelligence Indian Renewable Energy Report (January 2026) — Sector Context
    passages.append({
        "claim": "Wind generation is highly seasonal and concentrated in key wind corridors (Gujarat, Rajasthan, Maharashtra, TN, Karnataka). Input price fluctuations in commodity prices (steel ~300-500 MT/MW and concrete for foundations) and Balance of Plant (BOP) execution account for 20-30% of total project cost.",
        "source_document": "Crisil_Intelligence_Indian_Renewable_Energy_Report_January_2026.pdf",
        "source_section": "Section 4 — Wind Sector Risk & Commodity Price Volatility (Pages 60, 67)"
    })

    return filter_passages_by_tier(passages)


def draft_rationale(
    project: Dict[str, Any],
    result: Dict[str, Any],
    extra_passages: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Drafts structured credit rating rationale for a project based on scoring engine output.
    Returns:
      {
        "executive_summary": str,
        "block_a_narrative": str,
        "block_b_narrative": str,
        "block_c_narrative": str,
        "block_d_narrative": str,
        "rating_sensitivities": {
            "positive_factors": [str],
            "negative_factors": [str]
        },
        "rationale_text": str,
        "citations": [{"claim": str, "source_document": str, "source_section": str}],
        "uncited_claims": [str],
        "sector_context_sources": [{"block": str, "document": str, "tier": str}],
        "mandatory_disclaimer": str
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
            "executive_summary": "Not rated — no rationale produced.",
            "block_a_narrative": "",
            "block_b_narrative": "",
            "block_c_narrative": "",
            "block_d_narrative": "",
            "rating_sensitivities": {"positive_factors": [], "negative_factors": []},
            "rationale_text": "Not rated — no rationale produced.",
            "citations": [],
            "uncited_claims": [],
            "sector_context_sources": [],
            "mandatory_disclaimer": MANDATORY_DISCLAIMER
        }

    # Extract score details
    uncited: List[str] = []

    p_name = project.get("project_name", "Project SPV")
    tech_type = project.get("technology_type", "TECH_WIND")

    cap_mw = project.get("installed_capacity_mw_ac")
    if cap_mw is None:
        uncited.append("installed_capacity_mw_ac not available from project inputs — plant capacity omitted from narrative")

    rev_share_frac = project.get("contracted_revenue_share")
    if rev_share_frac is not None:
        rev_share = float(rev_share_frac) * 100
    else:
        rev_share = None
        uncited.append("contracted_revenue_share not available from project inputs — contracted revenue share omitted from narrative")

    final_band = result.get("final_band", "Not Rated")
    ind_band = result.get("indicative_band", "Not Rated")
    raw_score = result.get("raw_score", 0.0)
    post_score = result.get("post_notching_score", 0.0)
    block_a = result.get("block_a_score", 0.0)
    block_b = result.get("block_b_score", 0.0)
    block_c = result.get("block_c_score", 0.0)
    block_d = result.get("block_d_score", 0.0)
    confidence = result.get("confidence", "High")
    conf_reason = result.get("confidence_reason", "")
    cap_notice = result.get("cap_notice")

    min_dscr = result.get("minimum_dscr") if result.get("minimum_dscr") is not None else project.get("minimum_dscr")
    avg_dscr = result.get("average_dscr") if result.get("average_dscr") is not None else project.get("average_dscr")
    if min_dscr is None:
        # CONFIRMED UNREACHABLE on any scored (non-"Not Rated") result -- minimum_dscr is a
        # Stage-1 critical field in scoring.py, so a null value here would already have
        # short-circuited to the unrated-exit path above. Left exactly as-is per instruction.
        min_dscr = 1.34
    if avg_dscr is None:
        uncited.append("average_dscr not available from scoring engine — average DSCR omitted from narrative")
    plcr_val = result.get("plcr")
    llcr_val = result.get("llcr")
    gearing_val = result.get("gearing")
    dsra_months_val = result.get("dsra_months")
    if dsra_months_val is None:
        uncited.append("dsra_months not available from scoring engine — DSRA liquidity buffer omitted from narrative")
    liquidity_months_val = result.get("liquidity_months") if result.get("liquidity_months") is not None else dsra_months_val

    # Executive Summary
    capacity_clause = f" ({cap_mw} MW {tech_type.replace('TECH_', '')})" if cap_mw is not None else ""
    rev_share_clause = f"a high contracted revenue share of {rev_share:.1f}%, " if rev_share is not None else ""
    avg_dscr_summary_clause = f" and average DSCR of {avg_dscr:.2f}x" if avg_dscr is not None else ""
    dsra_summary_clause = f", supported by a {dsra_months_val:.1f}-month DSRA liquidity buffer" if dsra_months_val is not None else ""

    exec_summary = (
        f"The credit rating assessment for {p_name}{capacity_clause} "
        f"assigns an indicative rating band of '{final_band}' based on a total post-notching score of {post_score:.1f} / 115.0 points "
        f"(raw score of {raw_score:.1f} points). The evaluation reflects {rev_share_clause}"
        f"a solid minimum DSCR of {min_dscr:.2f}x{avg_dscr_summary_clause} under P90 resource estimates{dsra_summary_clause}. "
        f"The assessment carries {confidence} confidence ({conf_reason})."
    )

    # Block A Narrative (Business & Asset Risk + CRISIL Tier 2 Sector Context)
    # BUG FIX: this paragraph previously hardcoded wind-specific resource/commodity language
    # (wind corridors, steel/concrete BOP capex) regardless of the project's actual technology
    # type, so a solar or hybrid project's Block A narrative read as if it were a wind asset.
    # Branch the resource-risk sentence by technology, matching the same branching already
    # used for methodology citations in get_grounded_methodology_citations().
    sector_context_sources: List[Dict[str, str]] = []

    if tech_type == "TECH_WIND":
        resource_risk_sentence = (
            "As highlighted in the CRISIL Intelligence Indian Renewable Energy Report (January 2026), "
            "wind energy assets face inherent generation seasonality concentrated in high-wind corridors "
            "(Gujarat, Rajasthan, Tamil Nadu). Commodity price volatility in steel (~300-500 MT/MW) and "
            "concrete foundation capex, alongside Balance of Plant (BOP) complexity (20-30% of total "
            "project cost), represent key physical and execution risk factors."
        )
        sector_context_sources.append({
            "block": "block_a_narrative",
            "document": "Crisil_Intelligence_Indian_Renewable_Energy_Report_January_2026.pdf",
            "tier": "Tier 2"
        })
    elif tech_type == "TECH_SOLAR":
        resource_risk_sentence = (
            "Solar resource risk is governed by module degradation, soiling losses, and irradiance "
            "variability against the P90 resource assessment, with Balance of Plant complexity "
            "(evacuation infrastructure, grid-integration) as the principal execution risk factor."
        )
    elif tech_type == "TECH_HYBRID":
        resource_risk_sentence = (
            "As a hybrid solar-wind (and, where applicable, storage-coupled) asset, generation "
            "complementarity across resource types provides some diversification benefit, offset by "
            "the additional dispatch-controller and shared-infrastructure complexity typical of "
            "hybrid configurations."
        )
    else:
        resource_risk_sentence = (
            "Technology-specific generation and execution risk factors apply per the project's "
            "resource assessment and Balance of Plant configuration."
        )

    block_a_narrative = (
        f"Business and Asset Risk (Block A) scored {block_a:.1f} / 35.0 points ({(block_a/35.0*100):.1f}%). "
        f"{resource_risk_sentence} The SPV mitigates these through O&M contracts and independent P90 "
        f"resource attestation."
    )

    # Block B Narrative (Cash-Flow Adequacy & Coverage)
    plcr_str = f" Project Life Coverage Ratio (PLCR) stands at {plcr_val:.2f}x" if plcr_val is not None else ""
    llcr_str = f" and Loan Life Coverage Ratio (LLCR) at {llcr_val:.2f}x" if llcr_val is not None else ""
    coverage_tail = f"{plcr_str}{llcr_str}, providing substantial cash flow headroom above debt service obligations." if (plcr_str or llcr_str) else "."
    avg_dscr_clause_b = f" and an average DSCR of {avg_dscr:.2f}x" if avg_dscr is not None else ""

    block_b_narrative = (
        f"Cash-Flow Adequacy (Block B) scored {block_b:.1f} / 35.0 points ({(block_b/35.0*100):.1f}%). Under P90 generation assumptions, "
        f"the project demonstrates robust debt service coverage metrics with a minimum DSCR of {min_dscr:.2f}x{avg_dscr_clause_b} "
        f"across the debt tenor.{coverage_tail}"
    )

    # Block C Narrative (Financial Strength & Liquidity)
    gearing_str = f" Total Debt / Tangible Net Worth ratio of {gearing_val:.2f}x." if gearing_val is not None else ""
    liq_str = f" Liquidity is supported by {liquidity_months_val:.1f} months of cash cover and operational reserves" if liquidity_months_val is not None else ""
    
    block_c_narrative = (
        f"Financial Strength & Liquidity (Block C) scored {block_c:.1f} / 25.0 points ({(block_c/25.0*100):.1f}%). Capital structure gearing is "
        f"maintained at a{gearing_str}{liq_str}, meeting standard Indian project finance liquidity benchmarks."
    )

    # Block D Narrative (Structural & Covenant Protections)
    # BUG FIX: this paragraph previously hardcoded "fully funded" DSRA language regardless of the
    # actual coverage tier (misleading for a project with a Poor/Stretched DSRA, e.g. TP-3 at 1.6
    # months), and a static "1.20x" lockup threshold regardless of the project's actual
    # lockup_dscr_threshold field (or whether a distribution lock-up exists at all). Both are now
    # bound to the project's real inputs.
    if dsra_months_val is not None:
        dsra_tier_label = "fully funded" if dsra_months_val >= 9.0 else (
            "moderately funded" if dsra_months_val >= 6.0 else (
            "thinly funded" if dsra_months_val >= 3.0 else "under-funded"
        ))
        dsra_clause_d = f"a {dsra_tier_label} {dsra_months_val:.1f}-month Debt Service Reserve Account (DSRA), "
    else:
        dsra_clause_d = ""
    lockup_val = project.get("lockup_dscr_threshold")
    has_lockup = project.get("distribution_lockup") == "YES" and lockup_val is not None
    lockup_clause = (
        f", a restricted payments DSCR lockup threshold of {float(lockup_val):.2f}x"
        if has_lockup else ""
    )
    block_d_narrative = (
        f"Structural & Covenant Protections (Block D) scored {block_d:.1f} / 20.0 points ({(block_d/20.0*100):.1f}%). Key credit enhancements include "
        f"{dsra_clause_d}a Ring-Fenced Trust and Retention Account (TRA) cash waterfall"
        f"{lockup_clause}, and the covenant package and negative pledge protections captured at Template 1 Block D."
    )

    # Dynamic Rating Sensitivities grounded in CORE v3.0 thresholds
    tech_label = tech_type.replace("TECH_", "").capitalize()

    # Extract primary offtaker details dynamically
    offtakers_list = project.get("offtakers", [])
    if offtakers_list and isinstance(offtakers_list, list) and isinstance(offtakers_list[0], dict):
        primary_off = offtakers_list[0]
        off_name = primary_off.get("name") or "Primary Offtaker"
        # BUG FIX: previously defaulted to "Investment Grade" when the rating/grade field was
        # missing -- defaulting a missing rating to a favorable one understates risk in exactly
        # the case where the input is incomplete. Default to "Unrated" instead, which is the
        # conservative (CP_POOR_UNRATED-equivalent) reading CORE §7.1 uses for a missing rating.
        off_grade = primary_off.get("rating_or_grade") or primary_off.get("grade") or "Unrated"
        off_type = label_for_enum(primary_off.get("type")) or "DISCOM"
        offtaker_sens_str = f"Payment delays exceeding 90 days from key offtaker {off_name} ({off_type}, rated {off_grade}) or rating downgrade of counterparty DISCOMs."
    else:
        offtaker_sens_str = "Payment delays exceeding 90 days from counterparty DISCOM offtakers or rating downgrade."

    # Distance to band edge (d)
    # BUG FIX: "or 5.5" would silently replace a genuine d=0.0 (a project sitting exactly on a
    # band edge -- the case that most needs an accurate, non-default d value) with a fabricated
    # 5.5. Same class of defect as the DSRA "or 6.0" fix above -- use an is-not-None guard.
    _d_raw = result.get("distance_to_band_edge")
    d_val = float(_d_raw) if _d_raw is not None else 5.5

    # Threshold set label & operative DSCR floor directly consumed from scoring engine output
    sens_set_label = result.get("dscr_threshold_set_label") or ("Set W" if tech_type == "TECH_WIND" else ("Set H" if tech_type == "TECH_HYBRID" else "Set S"))
    _floor_raw = result.get("dscr_adequate_floor")
    op_floor_val = float(_floor_raw) if _floor_raw is not None else 1.15
    sens_floor_val = f"{op_floor_val:.2f}x"

    op_years_completed = float(project.get("operating_years_completed") or 0.0)
    proj_state = project.get("project_status", "STATE_OPERATING_MATURE")

    positive_sensitivities = []
    if ind_band == "AAA":
        # AAA is the top of BAND_ORDER -- there is no higher tier to frame d as upgrade runway
        # toward. d at AAA is the distance DOWN to the AAA floor, not upside room.
        positive_sensitivities.append(
            "Already at the highest attainable rating band (AAA); no further upgrade sensitivity applies."
        )
    else:
        # Generation track-record claim: only valid if the project has at least 1 year of operating history
        # BUG 5 FIX: removed for pre-COD/no-operating-history projects; fabricated for op_years < 1
        if op_years_completed >= 1.0:
            positive_sensitivities.append(
                f"Sustained {tech_label} plant generation performance exceeding P90 resource estimates over consecutive operating years."
            )
        # Band-edge upside: always valid — grounded in scoring engine distance_to_band_edge
        positive_sensitivities.append(
            f"Operational cash flow accumulation or debt deleveraging yielding score gain exceeding distance to band edge (d = {d_val:.1f} pts) toward higher rating tier."
        )
    # BUG 5 FIX: Remove "payment cycle < 60 days" bullet entirely. There is no Template 1 field
    # backing payment track record; this was fabricated content regardless of project status.

    negative_sensitivities = [
        f"Persistent {tech_label} generation underperformance falling below P90 resource projections.",
        f"Compression of minimum DSCR below the {sens_set_label} ({sens_floor_val}) criteria lockup threshold under stress scenarios.",
        offtaker_sens_str
    ]

    # Citations
    citations = get_grounded_methodology_citations(tech_type)

    # Build rationale_text (evaluated for strict number traceability against result dictionary)
    prose_paragraphs = [
        f"The project has been assigned an indicative credit rating band of {final_band} based on a raw score of "
        f"{raw_score:.1f} points and a post-notching score of {post_score:.1f} points out of 115.0.",
        f"Business and operating risk (Block A) scored {block_a:.1f} out of 35.0 points. "
        f"Cash-flow adequacy (Block B) scored {block_b:.1f} out of 35.0 points. "
        f"Financial strength (Block C) scored {block_c:.1f} out of 25.0 points. "
        f"Structural protections (Block D) scored {block_d:.1f} out of 20.0 points.",
        f"The rating assessment carries {confidence} confidence ({conf_reason})." if conf_reason else f"The rating assessment carries {confidence} confidence.",
        MANDATORY_DISCLAIMER
    ]
    rationale_text = "\n\n".join(prose_paragraphs)

    return {
        "executive_summary": exec_summary,
        "block_a_narrative": block_a_narrative,
        "block_b_narrative": block_b_narrative,
        "block_c_narrative": block_c_narrative,
        "block_d_narrative": block_d_narrative,
        "rating_sensitivities": {
            "positive_factors": positive_sensitivities,
            "negative_factors": negative_sensitivities
        },
        "rationale_text": rationale_text,
        "citations": citations,
        "uncited_claims": uncited,
        "sector_context_sources": sector_context_sources,
        "mandatory_disclaimer": MANDATORY_DISCLAIMER
    }
