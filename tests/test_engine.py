"""
Acceptance Test Suite for Credit Rating Simulator Scoring Engine.
Parametritised pytest suite testing field-by-field equality against all 8 reference project fixtures in reference_projects_v3_0.json.
"""

import json
import os
import re
import pytest
import jsonschema
from app.engine.scoring import score_project

FIXTURES_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "reference_projects_v3_0.json"
)
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "project.schema.json"
)

def load_projects():
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["projects"]

PROJECTS = load_projects()

def _parse_float(val):
    if val is None:
        return None
    try:
        return float(str(val).strip())
    except ValueError:
        return None

def _get_exp_key(expected_dict, key_substring):
    for k, v in expected_dict.items():
        if key_substring in k:
            return v
    return None

@pytest.mark.parametrize("project", PROJECTS, ids=[p["id"] for p in PROJECTS])
def test_reference_project(project):
    pid = project["id"]
    inputs = project["inputs"]
    expected = project["expected_outputs"]

    computed = score_project(inputs)

    # 1. Block A Score
    exp_a = _parse_float(_get_exp_key(expected, "Block A"))
    comp_a = computed["block_a_score"]
    if exp_a is not None:
        assert comp_a == exp_a, f"[{pid}] Block A mismatch: computed {comp_a} != expected {exp_a}"
    else:
        assert comp_a is None, f"[{pid}] Block A expected None, got {comp_a}"

    # 2. Block B Score
    exp_b = _parse_float(_get_exp_key(expected, "Block B"))
    comp_b = computed["block_b_score"]
    if exp_b is not None:
        assert comp_b == exp_b, f"[{pid}] Block B mismatch: computed {comp_b} != expected {exp_b}"
    else:
        assert comp_b is None, f"[{pid}] Block B expected None, got {comp_b}"

    # 3. Block C Score
    exp_c = _parse_float(_get_exp_key(expected, "Block C"))
    comp_c = computed["block_c_score"]
    if exp_c is not None:
        assert comp_c == exp_c, f"[{pid}] Block C mismatch: computed {comp_c} != expected {exp_c}"
    else:
        assert comp_c is None, f"[{pid}] Block C expected None, got {comp_c}"

    # 4. Block D Score
    exp_d = _parse_float(_get_exp_key(expected, "Block D"))
    comp_d = computed["block_d_score"]
    if exp_d is not None:
        assert comp_d == exp_d, f"[{pid}] Block D mismatch: computed {comp_d} != expected {exp_d}"
    else:
        assert comp_d is None, f"[{pid}] Block D expected None, got {comp_d}"

    # 5. Raw Score
    exp_raw = _parse_float(_get_exp_key(expected, "Raw score"))
    comp_raw = computed["raw_score"]
    if exp_raw is not None:
        assert comp_raw == exp_raw, f"[{pid}] Raw score mismatch: computed {comp_raw} != expected {exp_raw}"
    else:
        assert comp_raw is None, f"[{pid}] Raw score expected None, got {comp_raw}"

    # 6. Post-Notching Score
    exp_post = _parse_float(_get_exp_key(expected, "Post-notching score"))
    comp_post = computed["post_notching_score"]
    if exp_post is not None:
        assert comp_post == exp_post, f"[{pid}] Post-notching score mismatch: computed {comp_post} != expected {exp_post}"
    else:
        assert comp_post is None, f"[{pid}] Post-notching score expected None, got {comp_post}"

    # 7. Indicative Band
    exp_ind = _get_exp_key(expected, "Indicative band")
    comp_ind = computed["indicative_band"]
    if exp_ind is not None and _parse_float(exp_ind) is None and not str(exp_ind).startswith("—"):
        assert comp_ind == str(exp_ind).strip(), f"[{pid}] Indicative band mismatch: computed '{comp_ind}' != expected '{exp_ind}'"
    elif pid in ["TP-7", "TP-8"]:
        assert comp_ind == "Not Rated", f"[{pid}] Indicative band expected 'Not Rated', got '{comp_ind}'"

    # 8. Final Band
    exp_final = _get_exp_key(expected, "FINAL BAND")
    comp_final = computed["final_band"]
    if exp_final is not None and _parse_float(exp_final) is None and not str(exp_final).startswith("—"):
        assert comp_final == str(exp_final).strip(), f"[{pid}] Final band mismatch: computed '{comp_final}' != expected '{exp_final}'"
    elif pid in ["TP-7", "TP-8"]:
        assert comp_final == "Not Rated", f"[{pid}] Final band expected 'Not Rated', got '{comp_final}'"

    # 9. Distance to Edge
    exp_d_edge = _parse_float(_get_exp_key(expected, "Distance to nearest band edge"))
    comp_d_edge = computed["distance_to_band_edge"]
    if exp_d_edge is not None:
        assert comp_d_edge == exp_d_edge, f"[{pid}] Distance to edge mismatch: computed {comp_d_edge} != expected {exp_d_edge}"
    else:
        assert comp_d_edge is None, f"[{pid}] Distance to edge expected None, got {comp_d_edge}"

    # 10. Confidence & Specific Pipeline Termination Assertions
    if pid == "TP-7":
        assert computed["confidence"] == "Not Rated", f"[TP-7] Confidence expected 'Not Rated', got '{computed['confidence']}'"
        assert "technology_type" in computed["confidence_reason"], f"[TP-7] Expected technology_type named in confidence_reason, got '{computed['confidence_reason']}'"
        assert len(computed["validation_results"]) == 0, f"[TP-7] Expected 0 validation results, got {len(computed['validation_results'])}"
    elif pid == "TP-8":
        assert computed["confidence"] == "Not Rated", f"[TP-8] Confidence expected 'Not Rated', got '{computed['confidence']}'"
        val_results = computed["validation_results"]
        assert len(val_results) == 13, f"[TP-8] Expected full validation report with 13 rules evaluated, got {len(val_results)}"
        
        blocks = [r for r in val_results if r["outcome"] == "Block"]
        not_evals = [r for r in val_results if r["outcome"] == "Not Evaluated"]
        passes = [r for r in val_results if r["outcome"] == "Pass"]
        warns = [r for r in val_results if r["outcome"] == "Warn"]

        assert len(blocks) == 1, f"[TP-8] Expected exactly 1 Block, got {len(blocks)}"
        assert blocks[0]["rule"] == "V1", f"[TP-8] Expected V1 Block, got {blocks[0]['rule']}"
        assert len(not_evals) == 1, f"[TP-8] Expected exactly 1 Not Evaluated, got {len(not_evals)}"
        assert not_evals[0]["rule"] == "V6", f"[TP-8] Expected V6 Not Evaluated, got {not_evals[0]['rule']}"
        assert len(passes) == 11, f"[TP-8] Expected 11 Pass outcomes, got {len(passes)}"
        assert len(warns) == 0, f"[TP-8] Expected 0 Warn outcomes, got {len(warns)}"
    else:
        exp_conf = _get_exp_key(expected, "CONFIDENCE")
        comp_conf = computed["confidence"]
        if exp_conf is not None:
            assert comp_conf == str(exp_conf).strip(), f"[{pid}] Confidence mismatch: computed '{comp_conf}' != expected '{exp_conf}'"


from app.engine.scoring import score_project, _normalize_inputs, _get_offtaker_tier

def test_schema_conformance():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as sf:
        schema = json.load(sf)

    schema_properties = set(schema.get("properties", {}).keys())
    valid_ids = ["TP-1", "TP-2", "TP-3", "TP-4", "TP-5", "TP-6", "TP-8"]
    for project in PROJECTS:
        pid = project["id"]
        norm = _normalize_inputs(project["inputs"])
        inputs = {}
        for k, v in norm.items():
            if k in schema_properties and v is not None:
                if k == "discount_rate_as_of" and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(v)):
                    continue
                inputs[k] = v

        if pid in valid_ids:
            jsonschema.validate(instance=inputs, schema=schema)
        elif pid == "TP-7":
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(instance=inputs, schema=schema)


def test_rule_v12_positive_trigger_stale_rating():
    project = PROJECTS[0]
    inputs = dict(project["inputs"])
    inputs["offtakers"] = [
        {
            "name": "Discom 1",
            "type": "OFFTAKER_DISCOM",
            "contracted_share": 1.0,
            "rating_or_grade": "A",
            "rating_date": "2025-05-01"
        }
    ]
    computed = score_project(inputs)
    v12_results = [r for r in computed["validation_results"] if r["rule"] == "V12"]
    assert len(v12_results) == 1, "Expected V12 result"
    assert v12_results[0]["outcome"] == "Warn", f"Expected V12 Warn, got {v12_results[0]['outcome']}"


def test_rule_v6_positive_trigger_nca_disagreement():
    project = PROJECTS[0]
    inputs = dict(project["inputs"])
    inputs["dscr_schedule"] = [
        {"debt_year": 1, "cfads": 5000.0, "interest": 1000.0, "principal": 2000.0}
    ]
    inputs["cfads_nca_by_period"] = [6000.0]
    computed = score_project(inputs)
    v6_results = [r for r in computed["validation_results"] if r["rule"] == "V6"]
    assert len(v6_results) == 1, "Expected V6 result"
    assert v6_results[0]["outcome"] == "Block", f"Expected V6 Block, got {v6_results[0]['outcome']}"


def test_rule_v13_positive_trigger_template_mismatch():
    project = PROJECTS[0]
    inputs = dict(project["inputs"])
    inputs["technology_type_t2"] = "TECH_WIND"
    computed = score_project(inputs)
    v13_results = [r for r in computed["validation_results"] if r["rule"] == "V13"]
    assert len(v13_results) == 1, "Expected V13 result"
    assert v13_results[0]["outcome"] == "Block", f"Expected V13 Block, got {v13_results[0]['outcome']}"


def test_offtaker_tier_crosswalk_returns_none_on_unresolvable_rating():
    """
    _get_offtaker_tier() must return None -- a null, not a tier -- for any rating string that
    doesn't exactly match a CORE Appendix A code, including a compound value like the
    "AA, CRISIL, 12-03-2026" string that triggered this fix. It must never silently fall back
    to CP_POOR_UNRATED for a lookup miss, since that's indistinguishable downstream from a
    genuinely resolved Poor/Unrated determination.
    """
    assert _get_offtaker_tier("OFFTAKER_CI", "AA, CRISIL, 12-03-2026") is None
    assert _get_offtaker_tier("OFFTAKER_CI", "AAX") is None
    assert _get_offtaker_tier("OFFTAKER_CI", "") is None
    assert _get_offtaker_tier("OFFTAKER_CI", None) is None
    # Well-formed input must still resolve correctly -- this fix must not regress real ratings,
    # including case/whitespace normalization the crosswalk already applied before this fix.
    assert _get_offtaker_tier("OFFTAKER_CI", "AA") == "CP_STRONG"
    assert _get_offtaker_tier("OFFTAKER_CI", "Aa") == "CP_STRONG"
    assert _get_offtaker_tier("OFFTAKER_CI", "aa ") == "CP_STRONG"
    assert _get_offtaker_tier("OFFTAKER_CI", "D") == "CP_POOR_UNRATED"


def test_dominant_offtaker_unresolvable_rating_halts_as_insufficient_input():
    """
    A dominant offtaker (share >= 0.2500) with an unresolvable rating_or_grade must be treated
    identically to a MISSING critical field (CORE Section 9.8.1) -- the engine halts to
    "Insufficient Input -- Not Rated" with the field flagged in the null register, rather than
    silently computing a Poor/Unrated determination (the -21 pt notch / B-band cap this fix
    addresses).
    """
    project = PROJECTS[0]  # TP-1: single offtaker at 100% share
    inputs = dict(project["inputs"])
    inputs["offtakers"] = [
        {
            "name": "Vaidehi Alloys Limited",
            "type": "OFFTAKER_CI",
            "contracted_share": 1.0,
            "rating_or_grade": "AA, CRISIL, 12-03-2026",
        }
    ]
    computed = score_project(inputs)

    assert computed["final_band"] == "Not Rated", f"Expected halt to Not Rated, got {computed['final_band']}"
    assert computed["raw_score"] is None
    assert computed["notches_applied"] == [], "No notch should be computed for an unresolved rating"

    flagged = [n for n in computed["null_register"] if n["field"] == "offtakers[0].rating_or_grade"]
    assert len(flagged) == 1, f"Expected offtakers[0].rating_or_grade in null_register, got {computed['null_register']}"


def test_dominant_offtaker_wellformed_rating_resolves_to_strong_with_no_notch():
    """
    Regression guard for the exact reported scenario: a correctly-parsed bare rating symbol
    ("AA" for an OFFTAKER_CI counterparty) must resolve to CP_STRONG with a zero-point §7.1
    notch and no band cap from this factor.
    """
    project = PROJECTS[0]
    inputs = dict(project["inputs"])
    inputs["offtakers"] = [
        {
            "name": "Vaidehi Alloys Limited",
            "type": "OFFTAKER_CI",
            "contracted_share": 1.0,
            "rating_or_grade": "AA",
        }
    ]
    computed = score_project(inputs)

    offtaker_notches = [n for n in computed["notches_applied"] if n["source_section"] == "7.1 Offtaker"]
    assert len(offtaker_notches) == 1
    assert offtaker_notches[0]["points"] == 0.0, f"Expected 0 pt notch for Strong tier, got {offtaker_notches[0]}"

    offtaker_caps = [t for t in computed["cap_triggers"] if "Offtaker" in t["trigger"]]
    assert offtaker_caps == [], f"Expected no offtaker-tier band cap, got {offtaker_caps}"


def test_strong_metric_in_weak_block_appears_as_driver_not_constraint():
    """
    Regression guard: whether the Block A revenue-contractedness bullet and the Block B
    minimum-DSCR bullet render as a "driver" or a "constraint" must be decided by that
    specific metric's own threshold, not by the aggregate Block A/B percentage. Block A and
    B each fold in other, unrelated sub-factors (permitting/regulatory for A; PLCR/LLCR for
    B), so a project can legitimately have a low Block A/B score while its contracted revenue
    share and minimum DSCR are individually excellent -- previously this rendered the literal
    inverse ("Uncontracted merchant revenue exposure of 0.0%", "Minimum DSCR of 1.65x ...
    falls below ... target threshold") as a downward constraint.
    """
    project = PROJECTS[0]  # TP-1
    inputs = dict(project["inputs"])
    # Degrade unrelated Block A/B sub-factors so both aggregates drop well below 70%, while
    # leaving contracted_revenue_share and the DSCR-driving fields untouched (still strong).
    inputs["land_acquisition_status"] = "PERMIT_PENDING"
    inputs["transmission_connectivity_status"] = "PERMIT_PENDING"
    inputs["regulatory_stability"] = "REG_STAB_1"
    inputs["competitive_position"] = "COMP_POS_1"
    inputs["npv_cfads_project_life"] = 100
    inputs["npv_cfads_loan_life"] = 100

    computed = score_project(inputs)
    assert computed["block_a_score"] / 35.0 < 0.70, "Test setup must actually drop Block A below 70%"
    assert computed["block_b_score"] / 35.0 < 0.70, "Test setup must actually drop Block B below 70%"

    drivers = " | ".join(computed["drivers"])
    constraints = " | ".join(computed["constraints"])
    assert "High contracted revenue share" in drivers, f"Expected high contracted share as a driver, got drivers={computed['drivers']!r} constraints={computed['constraints']!r}"
    assert "Uncontracted merchant revenue exposure" not in constraints
    assert "comfortably exceeds" in drivers and "Minimum DSCR" in drivers
    assert "falls below" not in constraints or "Minimum DSCR" not in constraints


def test_zero_merchant_exposure_never_appears_as_constraint():
    """
    Regression guard for the exact vacuous-bullet report: 100% contracted revenue share
    (0.0% merchant exposure) must never render as "Uncontracted merchant revenue exposure of
    0.0%" under Rating Constraints, even when every other Block A sub-factor is weak enough
    to keep Block A's own aggregate well below 70%.
    """
    project = next(p for p in PROJECTS if p["id"] == "TP-3")
    inputs = dict(project["inputs"])
    inputs["contracted_revenue_share"] = 1.0

    computed = score_project(inputs)
    assert computed["block_a_score"] / 35.0 < 0.70, "Test setup must actually keep Block A below 70%"

    drivers = " | ".join(computed["drivers"])
    constraints = " | ".join(computed["constraints"])
    assert "High contracted revenue share of 100.0%" in drivers
    assert "merchant revenue exposure" not in constraints
