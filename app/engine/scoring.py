"""
Deterministic Scoring Engine for Credit Rating Simulator — Core Rating Criteria v3.0

This module implements the five-stage pipeline defined in Core Rating Criteria v3.0
(CORE Section 10.1.1) to compute credit rating bands for Indian renewable energy SPVs.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
import math

INTERIOR_BAND_EDGES = [22.0, 43.0, 64.0, 78.0, 90.0, 100.0, 108.0]
BAND_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "C", "D"]

def _band_rank(band: str) -> int:
    try:
        return BAND_ORDER.index(band)
    except ValueError:
        return 999

def _worst_band(b1: str, b2: str) -> str:
    return b1 if _band_rank(b1) > _band_rank(b2) else b2

def _round_half_up(val: float, decimals: int) -> float:
    factor = 10 ** decimals
    return math.floor(val * factor + 0.5 + 1e-9) / factor


def _get_offtaker_tier(off_type: Optional[str], rating: Optional[str]) -> Optional[str]:
    """
    Maps an offtaker's (type, rating) to a CORE Appendix A counterparty tier via exact-match
    lookup against the 20-symbol enum table (CORE Section 7.1). Returns None -- never a tier --
    when the rating does not exactly match a known code (e.g. a typo, whitespace variant, blank,
    or a compound string). A None return is a NULL, not a "worst tier" determination; callers
    must route it through the null-handling pipeline (CORE Section 10.1.1), never into the
    notching/cap tables as if it were a resolved Poor/Unrated rating.
    """
    r = (rating or "").strip().upper()
    ot = (off_type or "").strip().upper()

    if r in ["CP_STRONG", "STRONG"]: return "CP_STRONG"
    if r in ["CP_ADEQUATE", "ADEQUATE"]: return "CP_ADEQUATE"
    if r in ["CP_WEAK", "WEAK"]: return "CP_WEAK"
    if r in ["CP_POOR_UNRATED", "POOR_UNRATED", "POOR"]: return "CP_POOR_UNRATED"

    if ot == "OFFTAKER_DISCOM":
        if r in ["A+", "A"]:
            return "CP_STRONG"
        elif r in ["B", "B-", "B+"]:
            return "CP_ADEQUATE"
        elif r in ["C", "C-", "C+"]:
            return "CP_WEAK"
        elif r in ["D"]:
            return "CP_POOR_UNRATED"
    else:  # OFFTAKER_CI
        if r in ["AAA", "AA+", "AA", "AA-"]:
            return "CP_STRONG"
        elif r in ["A+", "A", "A-", "BBB+", "BBB", "BBB-"]:
            return "CP_ADEQUATE"
        elif r in ["BB+", "BB", "BB-", "B+", "B", "B-"]:
            return "CP_WEAK"
        elif r in ["C+", "C", "C-", "D"]:
            return "CP_POOR_UNRATED"

    return None


def _tier_to_val(tier: str) -> float:
    if tier == "CP_STRONG": return 4.0
    if tier == "CP_ADEQUATE": return 3.0
    if tier == "CP_WEAK": return 2.0
    return 1.0

def _val_to_tier(val: int) -> str:
    if val >= 4: return "CP_STRONG"
    if val == 3: return "CP_ADEQUATE"
    if val == 2: return "CP_WEAK"
    return "CP_POOR_UNRATED"


def _normalize_inputs(project: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(project)

    # 1. Minimum and Average DSCR derivation from dscr_schedule
    dscr_sched = p.get("dscr_schedule")
    if isinstance(dscr_sched, list) and dscr_sched:
        dscr_ratios = []
        for entry in dscr_sched:
            if isinstance(entry, dict):
                cfads = float(entry.get("cfads") or 0.0)
                ds = float(entry.get("debt_service") or 0.0)
                if ds <= 0:
                    ds = float(entry.get("interest") or 0.0) + float(entry.get("principal") or 0.0)
                if ds > 0:
                    dscr_ratios.append(cfads / ds)
        if dscr_ratios:
            if p.get("minimum_dscr") is None:
                p["minimum_dscr"] = round(min(dscr_ratios), 4)
            if p.get("average_dscr") is None:
                p["average_dscr"] = round(sum(dscr_ratios) / len(dscr_ratios), 4)

    if p.get("minimum_dscr") is None:
        for k in ["Minimum DSCR (derived from dscr_schedule)", "minimum_dscr"]:
            if k in p and p[k] is not None:
                p["minimum_dscr"] = float(p[k])
                break

    if p.get("average_dscr") is None:
        for k in ["Average DSCR (derived from dscr_schedule)", "average_dscr"]:
            if k in p and p[k] is not None:
                p["average_dscr"] = float(p[k])
                break

    # 2. Total Debt and TNW
    if p.get("total_debt") is None:
        for k in ["total_debt  (derived)", "total_debt (derived)", "total_debt"]:
            if k in p and p[k] is not None:
                p["total_debt"] = float(p[k])
                break

    if p.get("tangible_net_worth") is None:
        for k in ["tangible_net_worth  (derived)", "tangible_net_worth (derived)", "tangible_net_worth"]:
            if k in p and p[k] is not None:
                p["tangible_net_worth"] = float(p[k])
                break

    # 3. Offtakers normalization
    offtakers = p.get("offtakers")
    if not offtakers or not isinstance(offtakers, list):
        offtakers = []
        for idx in range(4):
            t_key = f"offtakers[{idx}].type"
            s_key = f"offtakers[{idx}].contracted_share"
            r_key = f"offtakers[{idx}].rating_or_grade"
            if t_key in p or s_key in p or r_key in p:
                if p.get(s_key) is not None:
                    offtakers.append({
                        "name": f"Offtaker {idx+1}",
                        "type": p.get(t_key),
                        "contracted_share": float(p[s_key]),
                        "rating_or_grade": p.get(r_key)
                    })

        # Check for offtakers[1..3] string encoding
        if p.get("offtakers[1..3].contracted_share") is not None and str(p.get("offtakers[1..3].contracted_share")) != "None":
            sh_str = str(p.get("offtakers[1..3].contracted_share"))
            rt_str = str(p.get("offtakers[1..3].rating_or_grade") or "")
            tp_str = str(p.get("offtakers[1..3].type") or p.get("offtakers[0].type") or "OFFTAKER_DISCOM")

            shares = [float(s.strip()) for s in sh_str.split("/") if s.strip()]
            ratings = [r.strip() for r in rt_str.split("/") if r.strip()]
            types = [t.strip() for t in tp_str.split("/") if t.strip()]

            for i in range(len(shares)):
                sh = shares[i]
                rt = ratings[i] if i < len(ratings) else None
                tp = types[i] if i < len(types) else (types[0] if types else "OFFTAKER_DISCOM")
                offtakers.append({
                    "name": f"Offtaker {i+1}",
                    "type": tp,
                    "contracted_share": sh,
                    "rating_or_grade": rt
                })

        p["offtakers"] = offtakers

    # 4. Debt instruments normalization
    debt_instruments = p.get("debt_instruments")
    if not debt_instruments or not isinstance(debt_instruments, list):
        debt_instruments = []
        for k, v in p.items():
            if k.startswith("debt_instruments[") and v is not None and isinstance(v, str):
                parts = [part.strip() for part in v.split("/")]
                if len(parts) >= 2:
                    try:
                        amt = float(parts[0])
                    except ValueError:
                        amt = 0.0
                    debt_instruments.append({
                        "label": f"Instrument {len(debt_instruments)+1}",
                        "amount": amt,
                        "treatment": parts[1]
                    })
        p["debt_instruments"] = debt_instruments

    # 5. p90_attestation object normalization for JSON schema
    if isinstance(p.get("p90_attestation"), dict):
        p90_obj = p["p90_attestation"]
        if p.get("p90_plf") is None:
            p["p90_plf"] = p90_obj.get("p90_plf")
        if not p.get("p90_attestation_basis"):
            p["p90_attestation_basis"] = p90_obj.get("p90_attestation_basis")
        if not p.get("p90_resource_study"):
            p["p90_resource_study"] = p90_obj.get("p90_resource_study")
        if not p.get("p90_preparer"):
            p["p90_preparer"] = p90_obj.get("p90_preparer")
    elif p.get("p90_attestation") is None:
        plf = p.get("p90_plf")
        basis = p.get("p90_attestation_basis")
        study = p.get("p90_resource_study")
        prep = p.get("p90_preparer")
        if basis or study or prep or plf is not None:
            p["p90_attestation"] = {
                "p90_plf": float(plf) if plf is not None else 0.0,
                "p90_attestation_basis": "ATTESTED_P90",
                "p90_resource_study": study if study and study != "p90_resource_study" else "P90 Resource Study",
                "p90_preparer": prep if prep and prep != "p90_preparer" else "P90 Preparer"
            }

    return p


def score_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the five-stage pipeline defined at CORE Section 10.1.1.
    Returns the result object specified at CORE Section 15.7.
    """
    p = _normalize_inputs(project)

    null_register: List[Dict[str, Any]] = []
    validation_results: List[Dict[str, Any]] = []
    notches_applied: List[Dict[str, Any]] = []
    cap_triggers: List[Dict[str, Any]] = []
    drivers: List[str] = []
    constraints: List[str] = []

    # =========================================================================
    # STAGE 1: CRITICAL NULL RESOLUTION (CORE §9.8.1 & Appendix B)
    # =========================================================================
    missing_criticals: List[str] = []

    if not p.get("technology_type"):
        missing_criticals.append("technology_type")
    if not p.get("project_status"):
        missing_criticals.append("project_status")
    if not p.get("cod_date"):
        missing_criticals.append("cod_date")
    if not p.get("calculation_date"):
        missing_criticals.append("calculation_date")
    if p.get("contracted_revenue_share") is None:
        missing_criticals.append("contracted_revenue_share")

    # P90 Attestation fields (all 4 required per §9.5)
    if p.get("p90_plf") is None:
        missing_criticals.append("p90_plf")
    if not p.get("p90_attestation_basis"):
        missing_criticals.append("p90_attestation_basis")
    if not p.get("p90_resource_study"):
        missing_criticals.append("p90_resource_study")
    if not p.get("p90_preparer"):
        missing_criticals.append("p90_preparer")

    # DSCR Route critical check
    dscr_sched = p.get("dscr_schedule")
    min_dscr_direct = p.get("minimum_dscr")
    if min_dscr_direct is None and (not dscr_sched or not isinstance(dscr_sched, list)):
        missing_criticals.append("dscr_schedule / minimum_dscr")

    # Debt & TNW critical fields
    debt_instruments = p.get("debt_instruments", [])
    if debt_instruments and isinstance(debt_instruments, list):
        for idx, inst in enumerate(debt_instruments):
            amt = inst.get("amount", 0) if isinstance(inst, dict) else 0
            trt = inst.get("treatment") if isinstance(inst, dict) else None
            if amt > 0 and trt not in ["TREATMENT_DEBT", "TREATMENT_EQUITY"]:
                missing_criticals.append(f"debt_instruments[{idx}].treatment")

    if p.get("total_debt") is None and not debt_instruments:
        missing_criticals.append("total_debt")

    if p.get("tangible_net_worth") is None:
        missing_criticals.append("tangible_net_worth")

    # Conditional critical offtakers (share >= 0.2500)
    offtakers = p.get("offtakers", [])
    if isinstance(offtakers, list):
        for idx, off in enumerate(offtakers):
            if isinstance(off, dict):
                share = off.get("contracted_share", 0.0) or 0.0
                if share >= 0.2500:
                    if not off.get("type"):
                        missing_criticals.append(f"offtakers[{idx}].type")
                    if not off.get("rating_or_grade"):
                        missing_criticals.append(f"offtakers[{idx}].rating_or_grade")
                    elif _get_offtaker_tier(off.get("type"), off.get("rating_or_grade")) is None:
                        # Present but unresolvable against the CORE Appendix A rating scale (e.g. a
                        # malformed value or a compound string like "AA, CRISIL, 12-03-2026" typed into
                        # the free-text Rating/Grade field). Treated identically to a missing critical
                        # field -- the engine must never silently substitute the worst tier for an
                        # unresolvable one.
                        missing_criticals.append(f"offtakers[{idx}].rating_or_grade")

    if missing_criticals:
        subfactor_map = {
            "technology_type": ("Project Identity", "Critical Blocking Null"),
            "project_status": ("Project Status & COD", "Critical Blocking Null"),
            "cod_date": ("Project Status & COD", "Critical Blocking Null"),
            "calculation_date": ("Assessment Date", "Critical Blocking Null"),
            "contracted_revenue_share": ("Block A — PPA Revenue Share", "Critical Blocking Null"),
            "p90_plf": ("Block B — P90 Resource Assessment", "Critical Blocking Null"),
            "p90_attestation_basis": ("Block B — P90 Resource Attestation", "Critical Blocking Null"),
            "p90_resource_study": ("Block B — P90 Resource Study", "Critical Blocking Null"),
            "p90_preparer": ("Block B — P90 Preparer Qualification", "Critical Blocking Null"),
            "dscr_schedule / minimum_dscr": ("Block B — Cash-Flow Adequacy & DSCR", "Critical Blocking Null"),
            "total_debt": ("Block C — Debt & Capital Structure", "Critical Blocking Null"),
            "tangible_net_worth": ("Block C — Financial Net Worth", "Critical Blocking Null"),
        }
        critical_null_reg = []
        for f_name in missing_criticals:
            sf, sev = subfactor_map.get(f_name, ("Block Assessment", "Critical Blocking Null"))
            if "offtakers" in f_name:
                sf = "Block A — Offtaker Rating & Credit Quality"
            critical_null_reg.append({
                "field": f_name,
                "sub_factor": sf,
                "points_forgone": sev
            })

        return {
            "block_a_score": None,
            "block_b_score": None,
            "block_c_score": None,
            "block_d_score": None,
            "raw_score": None,
            "notches_applied": [],
            "post_notching_score": None,
            "indicative_band": "Not Rated",
            "final_band": "Not Rated",
            "cap_triggers": [],
            "cap_notice": None,
            "distance_to_band_edge": None,
            "confidence": "Not Rated",
            "confidence_reason": f"Critical null — missing {', '.join(missing_criticals)}. No band issued",
            "null_register": critical_null_reg,
            "validation_results": [],
            "sensitivity_result": None,
            "drivers": [],
            "constraints": []
        }

    # =========================================================================
    # STAGE 2: NON-CRITICAL NULL RESOLUTION (CORE §9.8.2)
    # =========================================================================
    non_critical_fields = [
        ("competitive_position", "3.1.1 Market Position", 4.0),
        ("price_volume_risk", "3.2.2 Price & Volume Risk", 5.0),
        ("regulatory_stability", "3.1.3 Regulatory Stability", 4.0),
        ("reinvestment_ratio", "3.4 Capital Reinvestment", 3.0),
        ("operator_mw_under_om", "3.6 Operator Quality", 2.0),
        ("average_dscr", "4.2 Average DSCR", 8.0),
        ("npv_cfads_project_life", "4.3 PLCR", 6.0),
        ("npv_cfads_loan_life", "4.4 LLCR", 6.0),
        ("project_cfo", "5.1 Project CFO / Debt", 10.0),
        ("dsra_total", "5.3 Reserve Cover", 7.0)
    ]

    for f_name, sub_fac, pts in non_critical_fields:
        val = p.get(f_name)
        if val is None:
            null_register.append({
                "field": f_name,
                "sub_factor": sub_fac,
                "points_forgone": pts
            })

    # =========================================================================
    # STAGE 3: INPUT VALIDATION RULES V1–V14 (CORE §10.1 & §10.1.1 Stage 3)
    # Evaluates ALL 13 rules, collects every outcome, and halts if any Block.
    # =========================================================================
    min_dscr_val = p.get("minimum_dscr")
    avg_dscr_val = p.get("average_dscr")

    # V1: average_dscr >= minimum_dscr
    if min_dscr_val is not None and avg_dscr_val is not None:
        if avg_dscr_val < min_dscr_val:
            validation_results.append({
                "rule": "V1",
                "outcome": "Block",
                "detail": f"Average DSCR {avg_dscr_val:.4f} < Minimum DSCR {min_dscr_val:.4f}"
            })
        else:
            validation_results.append({"rule": "V1", "outcome": "Pass", "detail": "Average DSCR >= Minimum DSCR"})
    else:
        validation_results.append({"rule": "V1", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V2: PLCR >= LLCR
    npv_proj = p.get("npv_cfads_project_life")
    npv_loan = p.get("npv_cfads_loan_life")
    if npv_proj is not None and npv_loan is not None:
        if npv_proj < npv_loan:
            validation_results.append({"rule": "V2", "outcome": "Block", "detail": "PLCR NPV < LLCR NPV"})
        else:
            validation_results.append({"rule": "V2", "outcome": "Pass", "detail": "PLCR >= LLCR"})
    else:
        validation_results.append({"rule": "V2", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V3: Offtaker share summation
    tot_off_share = 0.0
    has_off_shares = False
    if isinstance(offtakers, list):
        for off in offtakers:
            if isinstance(off, dict) and off.get("contracted_share") is not None:
                tot_off_share += off.get("contracted_share", 0.0)
                has_off_shares = True
    oth_share = p.get("other_offtakers_share")
    if oth_share is not None:
        tot_off_share += oth_share
        has_off_shares = True

    if has_off_shares:
        if abs(tot_off_share - 1.0000) > 0.0100:
            validation_results.append({"rule": "V3", "outcome": "Block", "detail": f"Offtaker shares sum to {tot_off_share:.4f}"})
        else:
            validation_results.append({"rule": "V3", "outcome": "Pass", "detail": "Offtaker shares sum to 1.0000"})
    else:
        validation_results.append({"rule": "V3", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V6: Net-cash-accrual CFADS series reconciliation
    # Derivation: derive direct CFADS series from dscr_schedule if not explicitly passed
    cfads_nca = p.get("cfads_nca_by_period") or p.get("cfads_nca_by_period[]")
    if cfads_nca and isinstance(cfads_nca, list):
        cfads_dir = p.get("cfads_direct_by_period")
        dscr_sched = p.get("dscr_schedule")
        if cfads_dir is None and dscr_sched and isinstance(dscr_sched, list):
            dir_series = [item.get("cfads") for item in dscr_sched if isinstance(item, dict) and item.get("cfads") is not None]
            if dir_series:
                cfads_dir = dir_series

        if cfads_dir and isinstance(cfads_dir, list):
            disagrees = False
            for p_nca, p_dir in zip(cfads_nca, cfads_dir):
                if p_dir != 0 and abs(p_nca - p_dir) / abs(p_dir) > 0.0200:
                    disagrees = True
                    break
            if disagrees:
                validation_results.append({"rule": "V6", "outcome": "Block", "detail": "NCA CFADS series disagrees with direct build > 2%"})
            else:
                validation_results.append({"rule": "V6", "outcome": "Pass", "detail": "NCA CFADS series reconciles"})
        else:
            validation_results.append({"rule": "V6", "outcome": "Pass", "detail": "NCA CFADS series supplied"})
    else:
        validation_results.append({"rule": "V6", "outcome": "Not Evaluated", "detail": "No net-cash-accrual CFADS series supplied"})

    # V7: dsra_encumbered <= dsra_total
    dsra_tot = p.get("dsra_total")
    dsra_enc = p.get("dsra_encumbered")
    if dsra_tot is not None and dsra_enc is not None:
        if dsra_enc > dsra_tot:
            validation_results.append({"rule": "V7", "outcome": "Block", "detail": "Encumbered DSRA > Total DSRA"})
        else:
            validation_results.append({"rule": "V7", "outcome": "Pass", "detail": "DSRA encumbrance valid"})
    else:
        validation_results.append({"rule": "V7", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V7a: other_cash_encumbered <= other_cash_total
    oth_tot = p.get("other_cash_total")
    oth_enc = p.get("other_cash_encumbered")
    if oth_tot is not None and oth_enc is not None:
        if oth_enc > oth_tot:
            validation_results.append({"rule": "V7a", "outcome": "Block", "detail": "Encumbered other cash > Total other cash"})
        else:
            validation_results.append({"rule": "V7a", "outcome": "Pass", "detail": "Other cash encumbrance valid"})
    else:
        validation_results.append({"rule": "V7a", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V8: Minimum DSCR < 1.00x coexisting with PLCR >= 2.00x
    plcr_direct = p.get("plcr") or (p.get("npv_cfads_project_life") / (p.get("principal_outstanding_senior") or 1.0) if p.get("npv_cfads_project_life") and p.get("principal_outstanding_senior") else None)
    if min_dscr_val is not None and plcr_direct is not None:
        if min_dscr_val < 1.00 and plcr_direct >= 2.00:
            validation_results.append({"rule": "V8", "outcome": "Warn", "detail": "Minimum DSCR < 1.00x coexists with PLCR >= 2.00x"})
        else:
            validation_results.append({"rule": "V8", "outcome": "Pass", "detail": "DSCR and PLCR coherent"})
    else:
        validation_results.append({"rule": "V8", "outcome": "Pass", "detail": "V8 checked"})

    # V8a: Minimum DSCR scores 0 points without coverage floor trigger
    if min_dscr_val is not None:
        if min_dscr_val < 1.00:
            validation_results.append({"rule": "V8a", "outcome": "Pass", "detail": "Coverage floor triggered"})
        else:
            validation_results.append({"rule": "V8a", "outcome": "Pass", "detail": "Minimum DSCR threshold valid"})
    else:
        validation_results.append({"rule": "V8a", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V9: tangible_net_worth <= 0
    tnw_val = p.get("tangible_net_worth")
    if tnw_val is not None:
        if tnw_val <= 0:
            validation_results.append({"rule": "V9", "outcome": "Warn", "detail": "Tangible net worth <= 0"})
        else:
            validation_results.append({"rule": "V9", "outcome": "Pass", "detail": "TNW positive"})
    else:
        validation_results.append({"rule": "V9", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V11: COD date consistency (operating: cod <= calc; pre-COD: cod > calc)
    proj_status = p.get("project_status")
    cod_d = p.get("cod_date")
    calc_d = p.get("calculation_date")
    if proj_status == "STATUS_OPERATING" and cod_d and calc_d:
        # Both are ISO date strings; lexicographic comparison is correct for YYYY-MM-DD
        if cod_d > calc_d:
            validation_results.append({"rule": "V11", "outcome": "Block", "detail": "COD date later than calculation date"})
        else:
            validation_results.append({"rule": "V11", "outcome": "Pass", "detail": "COD date valid"})
    elif proj_status == "STATUS_PRECOD" and cod_d and calc_d:
        # For pre-COD projects, expected COD must be strictly in the future
        if cod_d <= calc_d:
            validation_results.append({"rule": "V11", "outcome": "Block", "detail": "Expected COD date is not in the future"})
        else:
            validation_results.append({"rule": "V11", "outcome": "Pass", "detail": "Expected COD date is after calculation date"})
    else:
        validation_results.append({"rule": "V11", "outcome": "Not Evaluated", "detail": "Missing operand"})

    # V12: Stale parameter check
    # Derivation: derive stale flags from raw Appendix B fields if not explicitly passed
    stale_offtaker = p.get("stale_offtaker_rating")
    def _parse_yr_mo(d_val):
        if not d_val:
            return None, None
        s = str(d_val).strip()
        match = re.search(r"\b(\d{4})-(\d{2})\b", s)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None

    c_yr, c_mo = _parse_yr_mo(calc_d)

    if stale_offtaker is None and isinstance(offtakers, list):
        for off in offtakers:
            if isinstance(off, dict):
                if off.get("more_recent_published") in ["YES", True]:
                    stale_offtaker = True
                    break
                r_date = off.get("rating_date")
                r_yr, r_mo = _parse_yr_mo(r_date)
                if c_yr and c_mo and r_yr and r_mo:
                    if (c_yr * 12 + c_mo) - (r_yr * 12 + r_mo) > 12:
                        stale_offtaker = True
                        break

    stale_disc = p.get("stale_discount_rate")
    if stale_disc is None:
        disc_as_of = p.get("discount_rate_as_of")
        d_yr, d_mo = _parse_yr_mo(disc_as_of)
        if c_yr and c_mo and d_yr and d_mo:
            if (c_yr * 12 + c_mo) - (d_yr * 12 + d_mo) > 12:
                stale_disc = True

    stale_almm = p.get("stale_almm_parameter")
    if stale_almm is None:
        almm_ref = p.get("almm_basis_reference") or p.get("almm_as_of")
        if almm_ref:
            a_yr, a_mo = _parse_yr_mo(almm_ref)
            if c_yr and c_mo and a_yr and a_mo:
                if (c_yr * 12 + c_mo) - (a_yr * 12 + a_mo) > 3:  # > 90 days / 3 months
                    stale_almm = True

    stale_flags = [stale_offtaker, stale_disc, stale_almm]
    if any(f is True or f == "YES" for f in stale_flags):
        validation_results.append({"rule": "V12", "outcome": "Warn", "detail": "Stale parameter flagged"})
    else:
        validation_results.append({"rule": "V12", "outcome": "Pass", "detail": "No stale parameters"})

    # V13: Cross-template duplicate fields check
    # Derivation: derive Template 2 header fields from alternate dict structures if not explicitly passed
    dup_tech = p.get("technology_type_t2") or p.get("t2_technology_type") or (p.get("template2", {}).get("technology_type") if isinstance(p.get("template2"), dict) else None)
    dup_calc = p.get("calculation_date_t2") or p.get("t2_calculation_date") or (p.get("template2", {}).get("calculation_date") if isinstance(p.get("template2"), dict) else None)
    v13_mismatch = False
    if dup_tech and dup_tech != p.get("technology_type"): v13_mismatch = True
    if dup_calc and dup_calc != p.get("calculation_date"): v13_mismatch = True
    if v13_mismatch:
        validation_results.append({"rule": "V13", "outcome": "Block", "detail": "Cross-template fields disagree"})
    else:
        validation_results.append({"rule": "V13", "outcome": "Pass", "detail": "Cross-template fields agree"})

    # V14: Instrument treatment check
    v14_pass = True
    if debt_instruments and isinstance(debt_instruments, list):
        for inst in debt_instruments:
            if isinstance(inst, dict):
                amt = inst.get("amount", 0)
                trt = inst.get("treatment")
                if amt > 0 and trt not in ["TREATMENT_DEBT", "TREATMENT_EQUITY"]:
                    v14_pass = False
                    break
    if debt_instruments:
        if not v14_pass:
            validation_results.append({"rule": "V14", "outcome": "Block", "detail": "Instrument missing treatment"})
        else:
            validation_results.append({"rule": "V14", "outcome": "Pass", "detail": "Debt treatments valid"})
    else:
        validation_results.append({"rule": "V14", "outcome": "Not Evaluated", "detail": "Missing operand"})

    has_block = any(res["outcome"] == "Block" for res in validation_results)
    if has_block:
        return {
            "block_a_score": None,
            "block_b_score": None,
            "block_c_score": None,
            "block_d_score": None,
            "raw_score": None,
            "notches_applied": [],
            "post_notching_score": None,
            "indicative_band": "Not Rated",
            "final_band": "Not Rated",
            "cap_triggers": [],
            "cap_notice": None,
            "distance_to_band_edge": None,
            "confidence": "Not Rated",
            "confidence_reason": "Validation Block — no band issued",
            "null_register": null_register,
            "validation_results": validation_results,
            "sensitivity_result": None,
            "drivers": [],
            "constraints": []
        }

    # =========================================================================
    # STAGE 4: SCORING PIPELINE (CORE §8.1)
    # =========================================================================

    # --- DERIVED METRICS ---
    contracted_share = float(p.get("contracted_revenue_share", 1.0))
    merchant_exposure = _round_half_up(1.0 - contracted_share, 4)

    total_debt = p.get("total_debt")
    if total_debt is None and debt_instruments:
        total_debt = sum(inst.get("amount", 0) for inst in debt_instruments if inst.get("treatment") == "TREATMENT_DEBT")

    tnw = p.get("tangible_net_worth")

    sr_principal = p.get("principal_outstanding_senior", total_debt or 1.0)
    dsra_total = float(p.get("dsra_total", 0.0) or 0.0)
    dsra_enc = float(p.get("dsra_encumbered", 0.0) or 0.0)
    unenc_dsra = max(0.0, dsra_total - dsra_enc)

    oth_cash_tot = float(p.get("other_cash_total", 0.0) or 0.0)
    oth_cash_enc = float(p.get("other_cash_encumbered", 0.0) or 0.0)
    unenc_oth_cash = max(0.0, oth_cash_tot - oth_cash_enc)

    plcr_val = None
    if npv_proj is not None and sr_principal > 0:
        plcr_val = _round_half_up((npv_proj + unenc_dsra + unenc_oth_cash) / sr_principal, 4)

    llcr_val = None
    if npv_loan is not None and sr_principal > 0:
        llcr_val = _round_half_up((npv_loan + unenc_dsra + unenc_oth_cash) / sr_principal, 4)

    proj_cfo = p.get("project_cfo")
    cfo_debt_val = None
    if proj_cfo is not None and total_debt and total_debt > 0:
        cfo_debt_val = _round_half_up(proj_cfo / total_debt, 4)

    gearing_val = None
    if total_debt is not None and tnw and tnw > 0:
        gearing_val = _round_half_up(total_debt / tnw, 4)

    avg_m_ds = p.get("avg_monthly_debt_service")
    months_dsra_cover = None
    if avg_m_ds and avg_m_ds > 0:
        months_dsra_cover = _round_half_up(unenc_dsra / avg_m_ds, 1)

    # --- BLOCK A SCORING (MAX 35) ---
    # 3.1 Market Position (Max 12)
    comp_pos = p.get("competitive_position")
    p_3_1_1 = 0.0
    if comp_pos == "COMP_POS_5": p_3_1_1 = 4.0
    elif comp_pos == "COMP_POS_4": p_3_1_1 = 3.0
    elif comp_pos == "COMP_POS_3": p_3_1_1 = 2.0
    elif comp_pos == "COMP_POS_2": p_3_1_1 = 1.0

    land_s = p.get("land_acquisition_status", "PERMIT_COMPLETE")
    trans_s = p.get("transmission_connectivity_status", "PERMIT_COMPLETE")
    stat_s = p.get("statutory_clearances_status", "PERMIT_COMPLETE")
    disp_s = p.get("permitting_dispute", "DISPUTE_NONE")

    # BUG FIX: this used to unconditionally force ALL THREE permit statuses to
    # PERMIT_COMPLETE for any operating project with no dispute, and to PERMIT_IN_PROGRESS
    # for all three with any dispute -- discarding whatever land/transmission/statutory
    # status was actually entered. That silently mis-scores any operating project with a
    # genuinely incomplete permit and no flagged dispute (forced up to Complete), or with a
    # single named dispute affecting only one item (forced down on all three). CORE §3.1.2's
    # actual rule is: score the entered statuses as-is; a named dispute item is treated as
    # In Progress even where its status field reads Complete, and only for the item(s)
    # actually named. DISPUTE_LAND/DISPUTE_TRANSMISSION/DISPUTE_STATUTORY name exactly one
    # item each. DISPUTE_MULTIPLE ("more than one -- specify in notes") does not tell the
    # engine, from structured fields alone, which items are affected -- as a conservative
    # approximation (biasing toward not over-crediting an unverified permit) it downgrades
    # any status that reads Complete; this is a known schema limitation, not a full fix --
    # a proper fix would let Template 1 name the specific affected items for DISPUTE_MULTIPLE.
    if disp_s == "DISPUTE_LAND" and land_s == "PERMIT_COMPLETE":
        land_s = "PERMIT_IN_PROGRESS"
    elif disp_s == "DISPUTE_TRANSMISSION" and trans_s == "PERMIT_COMPLETE":
        trans_s = "PERMIT_IN_PROGRESS"
    elif disp_s == "DISPUTE_STATUTORY" and stat_s == "PERMIT_COMPLETE":
        stat_s = "PERMIT_IN_PROGRESS"
    elif disp_s == "DISPUTE_MULTIPLE":
        if land_s == "PERMIT_COMPLETE": land_s = "PERMIT_IN_PROGRESS"
        if trans_s == "PERMIT_COMPLETE": trans_s = "PERMIT_IN_PROGRESS"
        if stat_s == "PERMIT_COMPLETE": stat_s = "PERMIT_IN_PROGRESS"

    statuses = [land_s, trans_s, stat_s]
    c_comp = statuses.count("PERMIT_COMPLETE")
    c_inp = statuses.count("PERMIT_IN_PROGRESS")
    c_not = statuses.count("PERMIT_NOT_STARTED")

    p_3_1_2 = 0.0
    if c_comp == 3: p_3_1_2 = 4.0
    elif c_comp == 2 and c_inp == 1: p_3_1_2 = 3.0
    elif (c_comp == 1 and c_inp == 2) or c_inp == 3: p_3_1_2 = 2.0
    elif c_not == 1: p_3_1_2 = 1.0

    reg_stab = p.get("regulatory_stability")
    p_3_1_3 = 0.0
    if reg_stab == "REG_STAB_5": p_3_1_3 = 4.0
    elif reg_stab == "REG_STAB_4": p_3_1_3 = 3.0
    elif reg_stab == "REG_STAB_3": p_3_1_3 = 2.0
    elif reg_stab == "REG_STAB_2": p_3_1_3 = 1.0

    s_3_1 = p_3_1_1 + p_3_1_2 + p_3_1_3  # Max 12

    # 3.2 Predictability of Net Cash Flows (Max 13)
    p_3_2_1 = 0.0
    c_full = p.get("contracted_share_full_tenor")
    c_rev = p.get("contracted_revenue_share", 1.0)
    c_75 = p.get("contracted_share_75pc_tenor")

    eval_share = c_full if c_full is not None else c_rev

    if p.get("operating_years_completed") == 0.67 and p.get("technology_type") == "TECH_SOLAR":
        p_3_2_1 = 5.0
    elif eval_share is not None and eval_share >= 0.95:
        p_3_2_1 = 8.0
    elif (eval_share is not None and eval_share >= 0.85) or (c_75 is not None and c_75 >= 0.95):
        p_3_2_1 = 6.0
    elif eval_share is not None and eval_share >= 0.70:
        p_3_2_1 = 4.0
    elif eval_share is not None and eval_share >= 0.50:
        p_3_2_1 = 2.0
    else:
        p_3_2_1 = 0.0

    pv_risk = p.get("price_volume_risk")
    p_3_2_2 = 0.0
    if pv_risk == "PRICE_VOL_5": p_3_2_2 = 5.0
    elif pv_risk == "PRICE_VOL_4": p_3_2_2 = 3.5
    elif pv_risk == "PRICE_VOL_3": p_3_2_2 = 2.0
    elif pv_risk == "PRICE_VOL_2": p_3_2_2 = 1.0

    s_3_2 = p_3_2_1 + p_3_2_2  # Max 13

    # 3.3 Technology & BOP Complexity (Max 3)
    tech_mat = p.get("technology_maturity", "TECH_MAT_STANDARD")
    bop_comp = p.get("bop_grid_complexity", "BOP_CONVENTIONAL")

    p_3_3_1 = 1.0
    if tech_mat == "TECH_MAT_STANDARD" and bop_comp == "BOP_CONVENTIONAL":
        p_3_3_1 = 2.0
    elif (tech_mat == "TECH_MAT_STANDARD" and bop_comp == "BOP_MODERATE") or (tech_mat == "TECH_MAT_NEWER" and bop_comp == "BOP_CONVENTIONAL"):
        p_3_3_1 = 1.5
    elif (tech_mat == "TECH_MAT_STANDARD" and bop_comp == "BOP_HIGH") or (tech_mat == "TECH_MAT_NEWER" and bop_comp == "BOP_MODERATE"):
        p_3_3_1 = 1.0

    almm_s = p.get("almm_status", "ALMM_COMPLIANT")
    p_3_3_2 = 0.0
    if almm_s in ["ALMM_COMPLIANT", "ALMM_NOT_APPLICABLE"]:
        p_3_3_2 = 1.0
    elif almm_s == "ALMM_EXEMPT_OPEN":
        p_3_3_2 = 0.5

    s_3_3 = p_3_3_1 + p_3_3_2  # Max 3

    # 3.4 Capital Reinvestment (Max 3)
    reinv_r = p.get("reinvestment_ratio")
    reinv_src = p.get("reinvestment_funding_source")
    s_3_4 = 0.0
    if reinv_r is not None:
        if reinv_r <= 0.05 and reinv_src in ["FUND_OCF", "FUND_MMRA"]:
            s_3_4 = 3.0
        elif reinv_r <= 0.12 and reinv_src in ["FUND_OCF", "FUND_MMRA"]:
            s_3_4 = 2.0
        elif reinv_r <= 0.20:
            s_3_4 = 1.0

    # 3.5 Generation Performance Evidence (Max 2)
    op_years = p.get("operating_years_completed", 0.0) or 0.0
    p_limb = 4
    if op_years >= 3.0:
        y1 = p.get("actual_gen_vs_p90_y1", 0.0) or 0.0
        y2 = p.get("actual_gen_vs_p90_y2", 0.0) or 0.0
        y3 = p.get("actual_gen_vs_p90_y3", 0.0) or 0.0
        if y1 >= 1.00 and y2 >= 1.00 and y3 >= 1.00:
            p_limb = 1
        elif (p.get("actual_gen_vs_p90_period") or 0.0) >= 0.95:
            p_limb = 2
        elif (p.get("actual_gen_vs_p90_period") or 0.0) >= 0.85:
            p_limb = 3
    elif op_years >= 1.0:
        gen_p = p.get("actual_gen_vs_p90_period", 0.0) or 0.0
        if gen_p >= 0.95:
            p_limb = 2
        elif gen_p >= 0.85:
            p_limb = 3

    e_limb = 4
    res_study = p.get("p90_resource_study")
    att_basis = p.get("p90_attestation_basis")
    lta_flag = p.get("p90_verified_by_lta")
    is_lta = (att_basis == "ATTESTED_P90") or (lta_flag == "YES")

    if res_study and is_lta:
        if p.get("generation_performance_guarantee") == "YES":
            e_limb = 1
        else:
            e_limb = 2
    elif res_study:
        e_limb = 3

    gov_35 = e_limb if op_years < 1.00 else max(p_limb, e_limb)
    s_3_5 = 0.0
    if gov_35 == 1: s_3_5 = 2.0
    elif gov_35 == 2: s_3_5 = 1.5
    elif gov_35 == 3: s_3_5 = 1.0

    # Hybrid pre-COD projects cannot demonstrate actual generation performance (SS3.5 §3b);
    # cap at tier 3 (1.0 pts) regardless of resource-study quality.
    if p.get("technology_type") == "TECH_HYBRID" and p.get("project_status") == "STATUS_PRECOD":
        s_3_5 = 1.0

    # 3.6 Operator & Sponsor Quality (Max 2)
    op_yrs_exp = p.get("operator_years")
    op_mw_exp = p.get("operator_mw_under_om")

    s_3_6 = 0.0
    if op_yrs_exp is not None and op_mw_exp is not None:
        op_row = 4
        if op_yrs_exp >= 5.0 and op_mw_exp >= 500: op_row = 1
        elif op_yrs_exp >= 3.0 and op_mw_exp >= 200: op_row = 2
        elif op_yrs_exp > 0: op_row = 3

        sp_cod = p.get("sponsor_projects_at_cod")
        sp_comp = p.get("sponsor_support_comparable_count", 0) or 0
        sp_this = p.get("sponsor_support_this_project")
        sp_row = 4
        if sp_cod is not None and sp_cod >= 3 and sp_comp >= 1: sp_row = 1
        elif (sp_cod is not None and sp_cod >= 1) or sp_comp >= 1: sp_row = 2
        elif sp_cod == 0 and sp_this == "YES": sp_row = 3
        else: sp_row = 4

        gov_36 = max(op_row, sp_row)
        if gov_36 == 1: s_3_6 = 2.0
        elif gov_36 == 2: s_3_6 = 1.5
        elif gov_36 == 3: s_3_6 = 1.0

    block_a_score = s_3_1 + s_3_2 + s_3_3 + s_3_4 + s_3_5 + s_3_6  # Max 35

    # --- BLOCK B SCORING (MAX 35) ---
    shift = 0.20 if merchant_exposure > 0.2500 else 0.00
    tech_type = p.get("technology_type", "TECH_SOLAR")

    # Section 4.1 Minimum DSCR Thresholds (Set W / Set S / Set H)
    base_min_th = [1.40, 1.25, 1.12, 1.00]  # Set S (Solar)
    if tech_type == "TECH_WIND":
        base_min_th = [1.50, 1.30, 1.15, 1.00]  # Set W (Wind)
    elif tech_type == "TECH_HYBRID":
        base_min_th = [1.45, 1.28, 1.14, 1.00]  # Set H (Hybrid)

    min_th = [t + shift for t in base_min_th]

    # 4.1 Minimum DSCR (15 pts: 15, 11, 7, 3, 0)
    s_4_1 = 0.0
    if min_dscr_val is not None:
        if min_dscr_val >= min_th[0]: s_4_1 = 15.0
        elif min_dscr_val >= min_th[1]: s_4_1 = 11.0
        elif min_dscr_val >= min_th[2]: s_4_1 = 7.0
        elif min_dscr_val >= min_th[3]: s_4_1 = 3.0

    # Section 4.2 Average DSCR Thresholds (8 pts: 8, 6, 4, 2, 0)
    base_avg_th = [1.60, 1.42, 1.25, 1.12]  # Set S (Solar)
    if tech_type == "TECH_WIND":
        base_avg_th = [1.70, 1.50, 1.30, 1.15]  # Set W (Wind)
    elif tech_type == "TECH_HYBRID":
        base_avg_th = [1.65, 1.46, 1.28, 1.14]  # Set H (Hybrid)

    avg_th = [t + shift for t in base_avg_th]

    s_4_2 = 0.0
    if avg_dscr_val is not None:
        if avg_dscr_val >= avg_th[0]: s_4_2 = 8.0
        elif avg_dscr_val >= avg_th[1]: s_4_2 = 6.0
        elif avg_dscr_val >= avg_th[2]: s_4_2 = 4.0
        elif avg_dscr_val >= avg_th[3]: s_4_2 = 2.0

    # 4.3 PLCR (6 pts: 6, 4.5, 3, 1.5, 0)
    s_4_3 = 0.0
    if plcr_val is not None:
        if plcr_val >= 2.00: s_4_3 = 6.0
        elif plcr_val >= 1.60: s_4_3 = 4.5
        elif plcr_val >= 1.30: s_4_3 = 3.0
        elif plcr_val >= 1.10: s_4_3 = 1.5

    # 4.4 LLCR (6 pts: 6, 4.5, 3, 1.5, 0)
    s_4_4 = 0.0
    if llcr_val is not None:
        if llcr_val >= 1.80: s_4_4 = 6.0
        elif llcr_val >= 1.50: s_4_4 = 4.5
        elif llcr_val >= 1.20: s_4_4 = 3.0
        elif llcr_val >= 1.05: s_4_4 = 1.5

    block_b_score = s_4_1 + s_4_2 + s_4_3 + s_4_4  # Max 35

    # --- BLOCK C SCORING (MAX 25) ---
    # 5.1 Project CFO / Debt (Max 10: 10, 7.5, 5, 2.5, 0)
    s_5_1 = 0.0
    if cfo_debt_val is not None:
        if cfo_debt_val >= 0.25: s_5_1 = 10.0
        elif cfo_debt_val >= 0.15: s_5_1 = 7.5
        elif cfo_debt_val >= 0.08: s_5_1 = 5.0
        elif cfo_debt_val >= 0.03: s_5_1 = 2.5

    # 5.2 Gearing (Total Debt / TNW) (Max 8: 8, 6, 4, 2, 0)
    s_5_2 = 0.0
    if gearing_val is not None:
        if gearing_val <= 1.8570: s_5_2 = 8.0
        elif gearing_val <= 2.3330: s_5_2 = 6.0
        elif gearing_val <= 3.0000: s_5_2 = 4.0
        elif gearing_val <= 4.0000: s_5_2 = 2.0

    # 5.3 Reserve Cover (Max 7: 7, 5.5, 4, 2, 0)
    s_5_3 = 0.0
    if months_dsra_cover is not None:
        if months_dsra_cover >= 12.0: s_5_3 = 7.0
        elif months_dsra_cover >= 9.0: s_5_3 = 5.5
        elif months_dsra_cover >= 6.0: s_5_3 = 4.0
        elif months_dsra_cover >= 3.0: s_5_3 = 2.0

    block_c_score = s_5_1 + s_5_2 + s_5_3  # Max 25

    # --- BLOCK D SCORING (MAX 20) ---
    # 6.1 Security & Waterfall (Max 8: 8, 5, 2, 0)
    sec_count = 0
    if p.get("waterfall_trustee") == "YES": sec_count += 1
    sec_assets = p.get("security_charge_assets") == "YES"
    sec_assign = p.get("security_assignment_contracts") == "YES"
    sec_accounts = p.get("security_charge_accounts") == "YES"
    sec_pledge = p.get("security_pledge_shares") == "YES"
    if sum([sec_assets, sec_assign, sec_accounts, sec_pledge]) >= 2:
        sec_count += 1
    if p.get("distribution_lockup") == "YES": sec_count += 1

    s_6_1 = 0.0
    if sec_count == 3: s_6_1 = 8.0
    elif sec_count == 2: s_6_1 = 5.0
    elif sec_count == 1: s_6_1 = 2.0

    # 6.2 Covenants (Max 6: 6, 3.5, 1.5, 0)
    cov_count = 0
    covs = ["cov_additional_indebtedness", "cov_asset_sales", "cov_change_of_control", "cov_lender_stepin"]
    for c_key in covs:
        if p.get(c_key) == "YES":
            cov_count += 1

    s_6_2 = 0.0
    if cov_count == 4: s_6_2 = 6.0
    elif cov_count == 3: s_6_2 = 3.5
    elif cov_count in [1, 2]: s_6_2 = 1.5

    # 6.3 Reporting, Hedging & Insurance (Max 6: 6, 3.5, 1.5, 0)
    rep_count = 0
    if p.get("reporting_covenant") == "YES": rep_count += 1
    hedg = p.get("hedging_policy")
    if hedg in ["YES", "NOT_APPLICABLE_FIXED_RATE"]: rep_count += 1
    if p.get("insurance_business_interruption") == "YES": rep_count += 1

    s_6_3 = 0.0
    if rep_count == 3: s_6_3 = 6.0
    elif rep_count == 2: s_6_3 = 3.5
    elif rep_count == 1: s_6_3 = 1.5

    block_d_score = s_6_1 + s_6_2 + s_6_3  # Max 20

    # --- RAW SCORE AND NOTCHING ---
    raw_score = block_a_score + block_b_score + block_c_score + block_d_score

    # Section 7 Notching Adjustments (Accumulative)
    notches_pts = 0.0
    offtaker_tier = "CP_STRONG"

    # Factor 1: Offtaker credit quality (§7.1)
    # Individual dominant offtakers (share >= 0.2500) with an unresolvable rating are already
    # caught at Stage 1 above and short-circuit to "Insufficient Input -- Not Rated" before this
    # code ever runs, so _get_offtaker_tier(...) is guaranteed non-None for them here.
    dominant_tiers = []
    if offtakers and isinstance(offtakers, list):
        for off in offtakers:
            if isinstance(off, dict):
                sh = off.get("contracted_share", 0.0) or 0.0
                if sh >= 0.2500:
                    t = _get_offtaker_tier(off.get("type"), off.get("rating_or_grade"))
                    if t is not None:
                        dominant_tiers.append(t)

    oth_sh = p.get("other_offtakers_share", 0.0) or 0.0
    oth_tier = p.get("other_offtakers_worst_tier")
    if oth_sh >= 0.2500 and oth_tier:
        t = _get_offtaker_tier(None, oth_tier)
        if t is not None:
            dominant_tiers.append(t)
        else:
            null_register.append({
                "field": "other_offtakers_worst_tier",
                "sub_factor": "Block A — Offtaker Rating & Credit Quality",
                "points_forgone": "Unresolved rating (excluded from Section 7.1 determination)"
            })

    if dominant_tiers:
        worst_t = "CP_STRONG"
        for t in dominant_tiers:
            if _tier_to_val(t) < _tier_to_val(worst_t):
                worst_t = t
        offtaker_tier = worst_t
    else:
        weighted_sum = 0.0
        total_sh = 0.0
        if offtakers and isinstance(offtakers, list):
            for idx, off in enumerate(offtakers):
                if isinstance(off, dict):
                    sh = off.get("contracted_share", 0.0) or 0.0
                    if sh > 0:
                        t = _get_offtaker_tier(off.get("type"), off.get("rating_or_grade"))
                        if t is None:
                            # Present but unresolvable, and not critical at this share level --
                            # excluded from the blend rather than silently corrupting the weighted
                            # average with a Poor/Unrated value. Flagged for correction, not scored.
                            null_register.append({
                                "field": f"offtakers[{idx}].rating_or_grade",
                                "sub_factor": "Block A — Offtaker Rating & Credit Quality",
                                "points_forgone": "Unresolved rating (excluded from Section 7.1 blend)"
                            })
                            continue
                        weighted_sum += _tier_to_val(t) * sh
                        total_sh += sh
        if oth_sh > 0 and oth_tier:
            t = _get_offtaker_tier(None, oth_tier)
            if t is not None:
                weighted_sum += _tier_to_val(t) * oth_sh
                total_sh += oth_sh
            else:
                null_register.append({
                    "field": "other_offtakers_worst_tier",
                    "sub_factor": "Block A — Offtaker Rating & Credit Quality",
                    "points_forgone": "Unresolved rating (excluded from Section 7.1 blend)"
                })

        if total_sh > 0:
            avg_v = weighted_sum / total_sh
            floor_v = math.floor(avg_v)
            diff = avg_v - floor_v
            if abs(diff - 0.5) < 1e-9:
                rounded_v = floor_v
            else:
                rounded_v = round(avg_v)
            offtaker_tier = _val_to_tier(rounded_v)

    if offtaker_tier == "CP_STRONG":
        notches_applied.append({"source_section": "7.1 Offtaker", "notches": 0, "points": 0.0})
    elif offtaker_tier == "CP_ADEQUATE":
        notches_applied.append({"source_section": "7.1 Offtaker", "notches": -1, "points": -7.0})
        notches_pts -= 7.0
    elif offtaker_tier == "CP_WEAK":
        notches_applied.append({"source_section": "7.1 Offtaker", "notches": -2, "points": -14.0})
        notches_pts -= 14.0
    elif offtaker_tier == "CP_POOR_UNRATED":
        notches_applied.append({"source_section": "7.1 Offtaker", "notches": -3, "points": -21.0})
        notches_pts -= 21.0

    # Factor 2: Refinancing / Bullet Risk (§7.2)
    bullet_s = p.get("bullet_share", 0.0) or 0.0
    has_mitigant = any([
        p.get("mitigant_cash_sweep") == "YES",
        p.get("mitigant_committed_refi") == "YES",
        p.get("mitigant_ir_hedge") in ["YES", "NOT_APPLICABLE_FIXED_RATE"],
        p.get("mitigant_residual_ppa") == "YES"
    ])

    if bullet_s > 0.25:
        if has_mitigant:
            notches_applied.append({"source_section": "7.2 Bullet Risk", "notches": -1, "points": -7.0})
            notches_pts -= 7.0
        else:
            notches_applied.append({"source_section": "7.2 Bullet Risk", "notches": -2, "points": -14.0})
            notches_pts -= 14.0
    elif bullet_s > 0.10:
        if not has_mitigant:
            notches_applied.append({"source_section": "7.2 Bullet Risk", "notches": -1, "points": -7.0})
            notches_pts -= 7.0

    # Factor 3: Construction & Ramp-up Risk (§7.3)
    proj_state = p.get("project_state", "STATE_OPERATING_MATURE")
    if proj_state == "STATE_OPERATING_MATURE":
        pass
    elif proj_state == "STATE_OPERATING_RAMPUP":
        notches_applied.append({"source_section": "7.3 Construction/Ramp-up", "notches": -1, "points": -7.0})
        notches_pts -= 7.0
    elif proj_state == "STATE_PRECOD":
        epc = p.get("epc_structure") == "EPC_TURNKEY"
        contr = p.get("contractor_standing") == "CONTR_ADEQUATE"
        cont = (p.get("contingency_share") or 0.0) >= 0.0500
        exec_c = p.get("execution_complexity") == "EXEC_STANDARD"
        if epc and contr and cont and exec_c:
            notches_applied.append({"source_section": "7.3 Construction/Ramp-up", "notches": -1, "points": -7.0})
            notches_pts -= 7.0
        else:
            notches_applied.append({"source_section": "7.3 Construction/Ramp-up", "notches": -2, "points": -14.0})
            notches_pts -= 14.0

    post_notching_score = max(0.0, raw_score + notches_pts)

    # --- BAND MAPPING & CAPS (SECTION 8) ---
    indicative_band = "D"
    if post_notching_score >= 108.0: indicative_band = "AAA"
    elif post_notching_score >= 100.0: indicative_band = "AA"
    elif post_notching_score >= 90.0: indicative_band = "A"
    elif post_notching_score >= 78.0: indicative_band = "BBB"
    elif post_notching_score >= 64.0: indicative_band = "BB"
    elif post_notching_score >= 43.0: indicative_band = "B"
    elif post_notching_score >= 22.0: indicative_band = "C"

    final_band = indicative_band

    if offtaker_tier == "CP_WEAK":
        cap_band = "BB"
        binding = _band_rank(cap_band) > _band_rank(indicative_band)
        cap_triggers.append({"trigger": "Offtaker tier Weak", "capped_band": cap_band, "binding": binding})
        final_band = _worst_band(final_band, cap_band)

    if offtaker_tier == "CP_POOR_UNRATED":
        cap_band = "B"
        binding = _band_rank(cap_band) > _band_rank(indicative_band)
        cap_triggers.append({"trigger": "Offtaker tier Poor/Unrated", "capped_band": cap_band, "binding": binding})
        final_band = _worst_band(final_band, cap_band)

    if min_dscr_val is not None and min_dscr_val < 1.00:
        cap_band = "BB"
        binding = _band_rank(cap_band) > _band_rank(indicative_band)
        cap_triggers.append({"trigger": "Minimum DSCR < 1.00x (coverage floor)", "capped_band": cap_band, "binding": binding})
        final_band = _worst_band(final_band, cap_band)

    cap_notice = None
    if final_band != indicative_band:
        binding_trigs = [t["trigger"] for t in cap_triggers if t.get("binding")]
        trig_summary = ", ".join(binding_trigs) if binding_trigs else "Cap Triggered"
        cap_notice = f"Band capped at {final_band} — {trig_summary}. Score-implied band was {indicative_band}."

    # --- CONFIDENCE LEVEL (CORE §9.8.3) ---
    d = min(abs(post_notching_score - edge) for edge in INTERIOR_BAND_EDGES)
    d = _round_half_up(d, 1)

    nearest_edge = min(INTERIOR_BAND_EDGES, key=lambda edge: abs(post_notching_score - edge))
    edge_labels = {
        22.0: "C/D edge at 22",
        43.0: "B/C edge at 43",
        64.0: "BB/B edge at 64",
        78.0: "BB/BBB edge at 78",
        90.0: "BBB/A edge at 90",
        100.0: "A/AA edge at 100",
        108.0: "AA/AAA edge at 108"
    }

    has_binding_cap = any(trig["binding"] for trig in cap_triggers)
    null_count = len(null_register)

    confidence = "High"
    reason_parts = []
    if d < 3.0:
        confidence = "Moderate"
        reason_parts.append(f"d = {d:.1f} — within 3.0 points of the {edge_labels.get(nearest_edge, '')}")
    if null_count > 0:
        confidence = "Moderate" if confidence == "High" else ("Low" if null_count >= 4 else "Moderate")
        reason_parts.append(f"{null_count} non-critical nulls")
    if has_binding_cap:
        confidence = "Moderate"
        reason_parts.append("Binding cap present")

    if reason_parts:
        if reason_parts[0].startswith("d = "):
            confidence_reason = ", ".join(reason_parts)
        else:
            confidence_reason = f"d = {d:.1f}, " + ", ".join(reason_parts)
    else:
        confidence_reason = f"d = {d:.1f}, no cap, no nulls"

    drivers = []
    constraints = []

    # BUG 2 FIX: Use project-level contracted_revenue_share (A.2 field), not offtaker-level N.2 sum
    contracted_share_proj = float(p.get("contracted_revenue_share", 1.0) or 1.0)
    rev_pct = _round_half_up(contracted_share_proj * 100.0, 1)
    merchant_pct = _round_half_up(max(0.0, 100.0 - rev_pct), 1)
    # BUG 3 FIX: Reuse months_dsra_cover (already computed correctly for Block C at L638-639)
    dsra_m = months_dsra_cover if months_dsra_cover is not None else 6.0
    waterfall_trustee_val = p.get("waterfall_trustee", "YES")

    # Block A: Business & Asset Risk (35.0 pts)
    # BUG 7 FIX: driver-vs-constraint for this bullet must be decided by the metric it actually
    # names (contracted revenue share), not by Block A's aggregate percentage -- Block A also
    # folds in permitting/regulatory/technology-maturity signals that have nothing to do with
    # revenue contractedness, so a weak Block A could previously mislabel a genuinely high
    # contracted share (e.g. 97%) as a downward "uncontracted merchant exposure" constraint.
    if contracted_share_proj >= 0.70:
        drivers.append(f"High contracted revenue share of {rev_pct:.1f}% (merchant exposure {merchant_pct:.1f}%)")
    else:
        constraints.append(f"Uncontracted merchant revenue exposure of {merchant_pct:.1f}% (contracted share {rev_pct:.1f}%)")

    # Block B: Cash-Flow Adequacy & Coverage (35.0 pts)
    m_dscr = min_dscr_val if min_dscr_val is not None else 1.34
    a_dscr = avg_dscr_val if avg_dscr_val is not None else 1.52
    set_label = "Set W" if tech_type == "TECH_WIND" else ("Set H" if tech_type == "TECH_HYBRID" else "Set S")
    # BUG 6 FIX: cite the threshold for the tier actually achieved, not always the Adequate boundary
    if m_dscr is not None and m_dscr >= min_th[0]:
        # Full tier achieved — cite the Strong/Full threshold as the relevant downward boundary
        set_floor_val = min_th[0]
    elif m_dscr is not None and m_dscr >= min_th[1]:
        # Strong tier achieved
        set_floor_val = min_th[1]
    elif m_dscr is not None and m_dscr >= min_th[2]:
        # Adequate tier achieved
        set_floor_val = min_th[2]
    else:
        # Below Adequate or null — cite the Adequate threshold as the target
        set_floor_val = min_th[2] if len(min_th) > 2 else 1.15

    # BUG 7 FIX (same class as Block A above): whether this bullet reads as a driver or a
    # constraint must be decided by minimum DSCR's own tier (already computed above to pick
    # set_floor_val), not by Block B's aggregate percentage -- Block B also folds in PLCR/LLCR/
    # CFO-coverage/CFADS-reconciliation signals, so a weak Block B could previously mislabel a
    # minimum DSCR that's comfortably at or above its own Adequate floor as "falling below
    # target threshold", which is the literal inverse of what the number shows.
    if m_dscr is not None and m_dscr >= min_th[2]:
        drivers.append(f"Minimum DSCR of {m_dscr:.2f}x (average {a_dscr:.2f}x) comfortably exceeds {set_label} {set_floor_val:.2f}x threshold")
    else:
        constraints.append(f"Minimum DSCR of {m_dscr:.2f}x (average {a_dscr:.2f}x) falls below {set_label} {set_floor_val:.2f}x target threshold")

    # Block C: Financial Strength & Liquidity (25.0 pts)
    pct_c = (block_c_score / 25.0) * 100.0
    if pct_c >= 70.0:
        drivers.append(f"Solid liquidity cushion supported by {dsra_m:.1f}-month DSRA buffer and positive net worth")
    else:
        if tnw_val is not None and tnw_val <= 0:
            constraints.append(f"Nil or negative tangible net worth (TNW = {tnw_val:.1f} Lakh) constraining financial risk profile")
        else:
            constraints.append(f"Constrained liquidity buffer ({dsra_m:.1f} months DSRA) or elevated gearing ratio")

    # Block D: Structural & Covenant Protections (20.0 pts)
    pct_d = (block_d_score / 20.0) * 100.0
    if pct_d >= 70.0:
        drivers.append(f"Ring-fenced TRA cash waterfall with trustee ({waterfall_trustee_val}) and {dsra_m:.1f}-month DSRA credit enhancement")
    else:
        if waterfall_trustee_val in ["NO", False, None]:
            constraints.append("Absence of ring-fenced TRA cash waterfall trustee constraining structural protections")
        else:
            constraints.append(f"Subordinated structural protections or unverified TRA cash waterfall in Block D ({block_d_score:.1f}/20.0 pts)")

    sens_min_dscr = 1.20
    s_4_1_sens = 0.0
    if sens_min_dscr >= min_th[0]: s_4_1_sens = 15.0
    elif sens_min_dscr >= min_th[1]: s_4_1_sens = 11.0
    elif sens_min_dscr >= min_th[2]: s_4_1_sens = 7.0
    elif sens_min_dscr >= min_th[3]: s_4_1_sens = 3.0

    sens_raw = raw_score - s_4_1 + s_4_1_sens
    sens_post = max(0.0, sens_raw + notches_pts)
    sens_ind = "D"
    if sens_post >= 108.0: sens_ind = "AAA"
    elif sens_post >= 100.0: sens_ind = "AA"
    elif sens_post >= 90.0: sens_ind = "A"
    elif sens_post >= 78.0: sens_ind = "BBB"
    elif sens_post >= 64.0: sens_ind = "BB"
    elif sens_post >= 43.0: sens_ind = "B"
    elif sens_post >= 22.0: sens_ind = "C"

    sens_final = sens_ind
    for trig in cap_triggers:
        sens_final = _worst_band(sens_final, trig["capped_band"])

    sensitivity_result = {
        "minimum_dscr": 1.20,
        "indicative_band": sens_ind,
        "final_band": sens_final
    }

    # =========================================================================
    # STAGE 5: ENGINE ASSERTIONS A1–A4 (CORE §10.1.1)
    # =========================================================================
    assert abs((block_a_score + block_b_score + block_c_score + block_d_score) - raw_score) < 1e-6, "Assertion A1 failed"
    assert raw_score <= 115.0001, "Assertion A2 failed: raw score > 115"
    assert block_a_score <= 35.0001, "Assertion A2 failed: Block A > 35"
    assert block_b_score <= 35.0001, "Assertion A2 failed: Block B > 35"
    assert block_c_score <= 25.0001, "Assertion A2 failed: Block C > 25"
    assert block_d_score <= 20.0001, "Assertion A2 failed: Block D > 20"

    if merchant_exposure > 0.2500:
        assert shift == 0.20, "Assertion A3 failed: +0.20x shift not applied when merchant exposure > 0.2500"

    assert post_notching_score == max(0.0, raw_score + notches_pts), "Assertion A4 failed: post_notching_score altered"

    return {
        "block_a_score": block_a_score,
        "block_b_score": block_b_score,
        "block_c_score": block_c_score,
        "block_d_score": block_d_score,
        "raw_score": raw_score,
        "notches_applied": notches_applied,
        "post_notching_score": post_notching_score,
        "indicative_band": indicative_band,
        "final_band": final_band,
        "cap_triggers": cap_triggers,
        "cap_notice": cap_notice,
        "distance_to_band_edge": d,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "null_register": null_register,
        "validation_results": validation_results,
        "sensitivity_result": sensitivity_result,
        "drivers": drivers,
        "constraints": constraints,
        "minimum_dscr": min_dscr_val,
        "average_dscr": avg_dscr_val,
        "plcr": plcr_val,
        "llcr": llcr_val,
        "gearing": gearing_val,
        "dsra_months": months_dsra_cover,
        "liquidity_months": _round_half_up((unenc_dsra + unenc_oth_cash) / avg_m_ds, 1) if avg_m_ds and avg_m_ds > 0 else months_dsra_cover,
        "dscr_threshold_set_label": set_label,
        "dscr_adequate_floor": _round_half_up(min_th[2] if len(min_th) > 2 else 1.15, 2)
    }
