"""
Acceptance Test Suite for Credit Rating Simulator Scoring Engine.
Parametritised pytest suite testing field-by-field equality against all 8 reference project fixtures in reference_projects_v3_0.json.
"""

import json
import os
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
        assert computed["confidence"] == "n/a — no result", f"[TP-8] Confidence expected 'n/a — no result', got '{computed['confidence']}'"
        assert len(computed["validation_results"]) == 1, f"[TP-8] Expected exactly 1 validation result (V1 Block), got {len(computed['validation_results'])}"
        assert computed["validation_results"][0]["rule"] == "V1", f"[TP-8] Expected V1 rule, got '{computed['validation_results'][0]['rule']}'"
        assert computed["validation_results"][0]["outcome"] == "Block", f"[TP-8] Expected Block outcome, got '{computed['validation_results'][0]['outcome']}'"
    else:
        exp_conf = _get_exp_key(expected, "CONFIDENCE")
        comp_conf = computed["confidence"]
        if exp_conf is not None:
            assert comp_conf == str(exp_conf).strip(), f"[{pid}] Confidence mismatch: computed '{comp_conf}' != expected '{exp_conf}'"


def test_schema_conformance():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as sf:
        schema = json.load(sf)

    valid_ids = ["TP-1", "TP-2", "TP-3", "TP-4", "TP-5", "TP-6", "TP-8"]
    for project in PROJECTS:
        pid = project["id"]
        inputs = project["inputs"]
        if pid in valid_ids:
            jsonschema.validate(instance=inputs, schema=schema)
        elif pid == "TP-7":
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(instance=inputs, schema=schema)
