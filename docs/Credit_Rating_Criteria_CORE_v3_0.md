Credit Rating Simulator — Core Rating Criteria (v3.0)

Table of Contents

# CREDIT RATING SIMULATOR

## RATING CRITERIA — CORE SCORECARD (ENGINE-READY)

*115-Point Scale · Indian Long-Term Rating Bands (AAA–D) · Renewable-Energy Project Finance (Solar, Wind, Hybrid)*

**Version 3.0 — 30 July 2026**

*STATUS: Approved for build. This document is the fixed rule set the Python scoring engine (Execution Manual, Activities 1.2–1.3) implements for this academic capstone.*

*This document is a synthesized, harmonized framework built from** ****twenty**** **distinct published CRA methodology documents (CRISIL, ICRA, CARE, India Ratings, Fitch, Moody’s, Brickwork). The count was stated as twenty-one in v1.0. The reference folder held twenty-one methodology files as originally assembled, but two of them were the same Fitch document under different filenames; the redundant copy has been quarantined and the folder now holds twenty. Of those twenty, thirteen ground a factor in this document — see Section 12 — and seven sit within the Extension scope at Section 0.4 and ground nothing in the v1 engine. See the Reference Corpus Hygiene and Ingestion Specification v3.0 for the audit. No provision below reproduces any single agency’s text verbatim. Section 12 records, for each factor, the published methodology whose reasoning or numeric guidance informed it; that mapping is a transparency record and does not imply sourcing, endorsement, or licensing from any CRA. Where a publicly available but superseded scorecard architecture was used as a structural reference for organizing weighted factors and notching, this is disclosed for transparency only.*

# 0. Document Control and Purpose

## 0.1 Document control

| Attribute | Value |
| --- | --- |
| Version | 3.0 |
| Issue date | 30 July 2026 |
| Supersedes | v2.0 (30 July 2026); v1.0 (undated) |
| Owner | Developer (CA. Satish Tirumela) — Credit Rating Simulator capstone |
| Status | Approved for build |
| Review cadence | Reviewed on every engine release, and in any event not less than every six months. Section 3.3.2 (regulatory sourcing parameters) is reviewed whenever MNRE issues a notification affecting ALMM. |
| Change log | Section 13 |
| Downstream documents that must move in step | Key Input Template 1 v3.0; Key Input Template 2 v3.0; **Credit Rating Simulator Test Fixtures v3.0**; Credit Rating Simulator Execution Manual v3.0; Reference Corpus Manifest v3.0; Reference Corpus Hygiene and Ingestion Specification v3.0 |
| Reference data for validation | **Credit Rating Simulator Test Fixtures v3.0** (eight reference projects, inputs and expected outputs); **reference_projects_v3_0.json** (the same eight in engine input format, for the Day-1 and Day-2 acceptance tests); and one matched worked pair — **Worked Example TP-2 Template 1** and **Worked Example TP-2 Template 2** — for validating the application end to end. None of these belongs in the same searchable knowledge base as a live assessment. |
| Format convention | Key Input Template 1 is issued as a genuine **.docx** because it is a data-entry form that users type into. This document and the Execution Manual are issued as **.md** because they are reference texts that are read, searched and diffed, not filled in. QA finding m12 was that the v2.0 files were Markdown wearing a .docx extension; the resolution is to match each file's format to its actual use, not to move every file to one extension. |
| Reference convention | Companion documents are cited by **title and version**, never by filename. Section 12 records why filenames in this project are not stable identifiers, and that rule applies to this document's own cross-references. |

## 0.2 Purpose

This document is the Core Rating Criteria for the Credit Rating Simulator. It defines every scored factor, numeric threshold, notching rule, cap, and band mapping the Python engine applies deterministically, with no AI-assisted judgment in the scoring path (per the Execution Manual’s founding rule: “numbers are calculated by Python… AI will not decide the score”).

**Determinism standard.** Every rule below must be applicable by hand. The acceptance test is the one the Execution Manual sets at its Activity 1.1: *a competent reviewer working from this document alone must reach the same score, band, and confidence level as the engine.* Any provision that cannot meet that test is a defect in this document, not a matter for implementer discretion.

## 0.3 Scope

Applies to Indian renewable-energy project-finance special purpose vehicles (SPVs) — solar, wind, and solar+wind hybrid — financed substantially on a non-recourse or limited-recourse basis.

**Technology-specific thresholds.** From v2.0, the Cash-flow Adequacy block (Section 4) applies **technology-specific DSCR threshold sets** for solar, wind, and hybrid projects, selected from the technology type captured at Key Input Template 1 §A.1. This replaces v1.0’s single cross-technology set. Technology-specific *qualitative* risk continues to be captured in Section 3.3.

**SPV perimeter.** The scored entity is the project SPV on a standalone basis. Group, sponsor, and consolidation effects are out of scope for the v1 engine (see Section 0.4).

## 0.4 Companion document

A separate document, the **Credit Rating Simulator — Criteria Extension**, sets out modules that are methodologically designed but intentionally not encoded in the v1 engine: Environmental, Social & Governance (ESG) assessment, Corporate Governance, Sponsor/Group-Linkage & Consolidation, Default Recognition, Hybrid & Storage-Linked structures, and Short-Term Instrument mapping.

*Resolved in v3.0 (QA finding B1). v2.0 carried an unverified cross-reference to a numbered section of a document not held in the project folder, and offered two permitted resolutions. Resolution (b) has been applied: the Extension is now cited **by title only**, here and at Section 11, with no section number. No internal cross-reference in this document now points at a document outside the project folder. Seven methodology documents in the reference corpus — short-term instruments, consolidation (CARE and CRISIL), default recognition, complexity indicator, corporate governance, and basics of ratings — sit within this Extension scope and are correctly recorded in Section 12 as grounding no v1 factor.*

# 1. Rating Philosophy

The Credit Rating Simulator expresses an indicative view of a renewable-energy project SPV’s relative capacity to service its rated debt obligations in full and on time, over the term of that debt. The view is built bottom-up from four weighted risk blocks — Business/Operating, Cash-flow Adequacy, Financial Strength, and Structural Protections — combined additively into a 115-point raw score; then adjusted by downward-only notching factors that capture risks a raw additive score cannot represent well (counterparty concentration, refinancing risk, construction and ramp-up risk); then mapped to an indicative rating band; then, where a cap is triggered, limited to that capped band.

Every quantitative threshold is either (a) grounded in a specific published CRA methodology, cited in Section 12, or (b) an explicitly flagged Developer calibration built on standard Indian project-finance convention where no agency in the reviewed corpus publishes a directly comparable numeric threshold. Category (b) items are marked **[Developer calibration — provisional]** at the point of use and are the first candidates for revision once back-test data is available.

The output is explicitly indicative and academic. It supports an internal, pre-agency view; it is not a SEBI-registered credit rating and does not represent the opinion of any credit rating agency named in this document.

# 2. Scorecard Architecture Overview

| **Block** | **Sub-Factor** | **Max Points** |
| --- | --- | --- |
| A. Business / Operating (35) | 3.1 Market Position (competition, permitting, regulatory) | **12** |
|  | 3.2 Predictability of Net Cash Flows (contractedness, price/volume risk) | **13** |
|  | 3.3 Technology (maturity, plant complexity, sourcing compliance) | **3** |
|  | 3.4 Capital Reinvestment | **3** |
|  | 3.5 Generation Performance Evidence | **2** |
|  | 3.6 Operator and Sponsor Quality | **2** |
| B. Cash-flow Adequacy (35) | 4.1 Minimum DSCR (P90 basis, technology-specific) | **15** |
|  | 4.2 Average DSCR (P90 basis, technology-specific) | **8** |
|  | 4.3 PLCR — Project Life Coverage Ratio | **6** |
|  | 4.4 LLCR — Loan Life Coverage Ratio | **6** |
| C. Financial Strength (25) | 5.1 Project CFO / Adjusted Debt | **10** |
|  | 5.2 Gearing (Total Debt / Tangible Net Worth) | **8** |
|  | 5.3 Liquidity — DSRA / Reserve Cover | **7** |
| D. Structural Protections (20) | 6.1 Security and Cash-flow Waterfall | **8** |
|  | 6.2 Debt and Investment Covenants | **6** |
|  | 6.3 Reporting, Hedging and Insurance | **6** |
| TOTAL |  | **115** |

*Applied after the 115-point score (Section 7 — not part of the 115): Offtaker/Counterparty Risk (graded notch plus band cap), Refinancing Risk, Construction and Ramp-up Risk. Band caps, including the coverage floor, are applied per Section 8.2.*

**Non-overlap map.** Each of the following risks is scored in exactly one place, **except where this table states otherwise and gives the reason**. A stated exception is a design decision; an unstated overlap is a defect.

| Risk | Scored at | Single place? |
| --- | --- | --- |
| Offtaker / counterparty credit quality | Section 7.1 | Yes — and nowhere in Block A |
| Construction and ramp-up status | Section 7.3 | Yes — and nowhere in Block A |
| Refinancing / bullet exposure | Section 7.2 | Yes |
| Liquidity and reserve cover | Section 5.3 | **No — stated exception**, see Section 9.7 |
| Merchant / uncontracted revenue exposure | Section 3.2.1 **and** the Section 4.0 merchant adjustment | **No — stated exception**, see below |
| Interest-rate / FX hedging | Section 6.3 **and** Section 7.2 mitigant 3 | **No — stated exception**, see below |

*Corrected in v3.0. The v2.0 map opened "scored in exactly one place, and nowhere else" and then gave two places on its final row, so it broke its own rule in its own last line. Two further overlaps were not listed at all. The map now distinguishes genuine single-placement from declared exceptions, and every exception carries its reasoning.*

**Stated exception — merchant exposure at Section 3.2.1 and Section 4.0.** These ask different questions about the same fact. Section 3.2.1 scores **how much** revenue is contracted and for how long: a business-risk measure, worth up to 8 points. Section 4.0 does not score anything; it **raises the coverage bar** the cash flow must clear, by 0.20x on every DSCR tier threshold, because a given DSCR built on merchant revenue is less reliable than the same DSCR built on contracted revenue. One measures the quantity of contracted revenue; the other adjusts the confidence attached to a coverage ratio. A project with heavy merchant exposure is therefore affected twice, and that is intended: the exposure is both a weaker business position and a reason to demand more headroom.

**Stated exception — hedging at Section 6.3 and Section 7.2.** Section 6.3 asks whether an interest-rate/FX hedging **policy exists**, as one of three structural-protection items. Section 7.2 mitigant 3 asks whether a hedge **covers at least 75% of floating-rate exposure to final maturity**, as one of four possible mitigants against refinancing risk. The second is a materially higher test than the first: a project can have a policy and still fail the 75%-to-maturity test. The two are recorded as separate fields — `hedging_policy` and `mitigant_ir_hedge` — precisely so that the engine cannot infer one from the other, and Section 7.2 requires only **one** of four mitigants, so the hedge answer is frequently not decisive there. The overlap is narrow and deliberate, but it is an overlap and is declared here rather than left for an implementer to discover.

# 3. Block A — Business / Operating Risk (35 points)

## 3.1 Market Position (12 points)

Scored as the sum of three independent enumerated sub-dimensions. Each is answered by a single enumerated selection in Key Input Template 1; none requires narrative interpretation.

### 3.1.1 Competitive and essentiality position (4 points)

| Code (Appendix A, `COMP_POS_5`) | Enumerated selection (Template 1 §A.2) | Points |
| --- | --- | --- |
| `COMP_POS_5` | No economically viable substitute source available to the offtaker for this volume (e.g. must-run or RPO-driven procurement obligation), and project tariff at or below the most recent comparable central/state auction benchmark | **4** |
| `COMP_POS_4` | Substitutes exist but switching is costly or slow; project tariff at or below the comparable auction benchmark | **3** |
| `COMP_POS_3` | Substitutes readily available; project tariff within 10% above the comparable auction benchmark | **2** |
| `COMP_POS_2` | Substitutes readily available; project tariff more than 10% above the comparable auction benchmark | **1** |
| `COMP_POS_1` | Offtake position expected to erode within the remaining debt tenor (contract expiry without renewal path, or notified re-tendering of the volume) | **0** |

### 3.1.2 Permitting completeness (4 points)

Derived deterministically from the three permitting statuses at Template 1 §A.3 (land acquisition, transmission connectivity, statutory clearances).

| Combination of the three statuses | Points |
| --- | --- |
| All three Complete | **4** |
| Two Complete, one In Progress | **3** |
| One Complete and two In Progress; or all three In Progress | **2** |
| Exactly one status is Not Started | **1** |
| Two or three statuses are Not Started | **0** |

*Operating-project rule: for a project past COD, each of the three statuses is deemed Complete unless a live dispute or a lapsed consent is recorded at Template 1 §A.3, in which case the affected item is treated as In Progress.*

### 3.1.3 Regulatory and tariff-policy stability (4 points)

| Enumerated selection (Template 1 §A.4) | Points |
| --- | --- |
| Stable — no PPA renegotiation attempt, retrospective charge, or contested tariff order in the offtake state in the last five years, and the applicable RPO trajectory is notified | **4** |
| Stable — a routine tariff or true-up order is pending with no adverse precedent in the state | **3** |
| Some uncertainty — a pending RPO revision or tariff order is material to project revenue | **2** |
| Unstable — a live PPA renegotiation attempt or contested tariff order affects this project or its offtaker | **1** |
| Adverse — a retrospective charge has been levied, or a renegotiation affecting this project is unresolved | **0** |

## 3.2 Predictability of Net Cash Flows (13 points)

**Offtaker credit quality is not scored here.** It is scored once, at Section 7.1. This section grades only (a) how much of the revenue is contracted and for how long, and (b) the price and volume risk carried within the contracted portion. See the non-overlap map at Section 2.

### 3.2.1 Contracted revenue share (8 points)

**Three distinct quantities are used here, and v2.0 conflated two of them.** They are separate fields in Appendix B and separate cells in Template 1 §A.2.

| Field | Definition |
| --- | --- |
| `contracted_revenue_share` | Revenue under executed PPAs or offtake agreements as a fraction of total projected revenue, measured over the remaining tenor of the rated debt. This is a **revenue-weighted average across the tenor**. It drives the merchant test at Section 4.0 and **nothing in the table below**. |
| `contracted_share_full_tenor` | The fraction of projected revenue contracted **all the way to final maturity of the rated debt**. This drives rows 1, 3, 4 and 5 below. |
| `contracted_share_75pc_tenor` | The fraction of projected revenue contracted for **at least 75% of the remaining debt tenor**. This drives the second limb of row 2 below, and nothing else. |

**Merchant exposure** = 1 − `contracted_revenue_share`. It is computed by the engine and is not a separate input (Section 10.1, V13).

*Resolved in v3.0 (QA finding M11). v2.0 defined contracted revenue share as a revenue-weighted average and then wrote every tier in terms of "X% contracted for the full remaining debt tenor" — a different quantity — while row 2's second limb required a ≥ 75%-of-tenor figure that Template 1 did not collect at all. Row 2 was therefore unreachable through its second limb, and rows 1, 3, 4 and 5 could be evaluated against either of two numbers with different results.*

| Row | Criteria | Points |
| --- | --- | --- |
| 1 | `contracted_share_full_tenor` ≥ 0.95 | **8** |
| 2 | `contracted_share_full_tenor` ≥ 0.85; **or** `contracted_share_75pc_tenor` ≥ 0.95 | **6** |
| 3 | `contracted_share_full_tenor` ≥ 0.70 | **4** |
| 4 | `contracted_share_full_tenor` ≥ 0.50 | **2** |
| 5 | `contracted_share_full_tenor` < 0.50 **and** row 2 not satisfied | **0** |

*Where more than one row is satisfied, the highest applicable points apply. Where `contracted_share_full_tenor` is null but `contracted_revenue_share` is populated, the sub-factor is a non-critical null and scores 0 (Section 9.8.2); the engine does not substitute one field for the other.*

### 3.2.2 Price and volume risk within the contracted portion (5 points)

| Enumerated selection (Template 1 §A.2) | Points |
| --- | --- |
| Fixed or pre-defined escalating tariff, with a take-or-pay or deemed-generation provision **and** a defined termination payment | **5** |
| Fixed or pre-defined escalating tariff, with either a take-or-pay/deemed-generation provision **or** a defined termination payment, but not both | **3.5** |
| Fixed or pre-defined escalating tariff, with neither a take-or-pay/deemed-generation provision nor a defined termination payment | **2** |
| Tariff partly indexed to a merchant or market reference | **1** |
| Tariff wholly merchant or market-linked | **0** |

## 3.3 Technology (3 points)

Split into two independent dimensions, resolving the v1.0 conflation of technology maturity with regulatory sourcing compliance.

### 3.3.1 Technology maturity and plant complexity (2 points)

Scored deterministically from the **two independent enumerated inputs** at Template 1 §A.5 — `technology_maturity` (`TECH_MAT_3`) and `bop_grid_complexity` (`BOP_3`). All nine combinations are enumerated below.

*Resolved in v3.0 (QA finding m6). v2.0 stated four prose rows combining both dimensions, while Template 1 collected them as a 3 × 3 grid, and gave no derivation. The mapping was inferable but was nowhere stated — the same defect Section 3.1.2 avoids by tabulating its combinations explicitly.*

| `technology_maturity` | `bop_grid_complexity` | Points |
| --- | --- | --- |
| `TECH_MAT_STANDARD` | `BOP_CONVENTIONAL` | **2** |
| `TECH_MAT_STANDARD` | `BOP_MODERATE` | **1.5** |
| `TECH_MAT_STANDARD` | `BOP_HIGH` | **1** |
| `TECH_MAT_NEWER` | `BOP_CONVENTIONAL` | **1** |
| `TECH_MAT_NEWER` | `BOP_MODERATE` | **1** |
| `TECH_MAT_NEWER` | `BOP_HIGH` | **1** |
| `TECH_MAT_UNTESTED` | any | **0** |

*`TECH_MAT_UNTESTED` governs regardless of balance-of-plant complexity: an untested generating technology is the binding constraint and the framework does not compound it.*

### 3.3.2 Regulatory sourcing compliance (1 point)

Scored from the single enumerated input `almm_status` (`ALMM_5`) at Template 1 §A.5. All five codes are enumerated.

*Resolved in v3.0 (QA finding m6). v2.0 stated three prose tiers while Template 1 offered five options, and Section 10.3 assigned this factor neither a canonical enumeration nor a place on the list of factors that carry no tier label.*

| `almm_status` | Points |
| --- | --- |
| `ALMM_COMPLIANT` | **1** |
| `ALMM_NOT_APPLICABLE` | **1** |
| `ALMM_EXEMPT_OPEN` | **0.5** |
| `ALMM_NON_COMPLIANT` | **0** |
| `ALMM_EXEMPT_CLOSED` | **0** |

*Technology asymmetry, disclosed. `ALMM_NOT_APPLICABLE` scores the full point, so a wind-only project cannot lose this point and a solar or hybrid project can. The factor is worth 1 of 115. It is retained rather than rebased because ALMM compliance is a real and currently live risk for solar procurement and no equivalent binding sourcing mandate applies to wind, but the asymmetry is now recorded at Section 11 rather than left implicit (QA finding m14).*

### 3.3.3 ALMM parameter table — configurable, not prose

The ALMM regime is a live regulatory parameter and is held as configuration, not as narrative text. The engine reads the table below; the table is versioned and dated independently of this document.

| Parameter | Value as recorded | As at |
| --- | --- | --- |
| Regime | ALMM List-II (solar PV cells) | 30 July 2026 |
| Base applicability | Projects commissioned on or after 1 June 2026 | 30 July 2026 |
| Segment governed by the deadline and its extension | Net-metering and open-access projects | 30 July 2026 |
| Extended compliance date for that segment | 31 December 2026 | 30 July 2026 |
| Case-by-case exemption route | MNRE office memorandum of 25 May 2026 — Category I (modules fully installed on site before 1 June 2026); Category II (substantial implementation steps demonstrated) | 30 July 2026 |
| Exemption claim channel and cut-off | NISE portal; claims by 30 June 2026 | 30 July 2026 |
| Most recent superseding instrument identified | MNRE memorandum of 18 July 2026 | 30 July 2026 |

**Mandatory verification rule.** These values were recorded on the issue date of this document and MNRE has issued instruments at least monthly through 2026. The engine must display the “as at” date alongside any ALMM-driven score, and the values must be re-verified against MNRE’s current notifications before each engine release. A parameter more than 90 days old is treated as stale and downgrades confidence per Section 9.8. Do not hard-code these values into engine logic.

## 3.4 Capital Reinvestment (3 points)

Reinvestment ratio = NPV of planned major-maintenance and replacement capital expenditure over the remaining debt tenor, divided by NPV of CFADS over the same period, both discounted at the Section 9.4 rate.

| Criteria | Points |
| --- | --- |
| Reinvestment ratio ≤ 5%, and fundable wholly from operating cash flow or a funded major-maintenance reserve account (MMRA) | **3** |
| Reinvestment ratio ≤ 12%, and fundable from operating cash flow or a funded MMRA | **2** |
| Reinvestment ratio ≤ 20%; or requires incremental debt or sponsor support | **1** |
| Reinvestment ratio > 20%; or funding source not identified | **0** |

*[Developer calibration — provisional. No agency in the reviewed corpus publishes a numeric reinvestment threshold for renewable SPVs.]*

## 3.5 Generation Performance Evidence (2 points)

*Renamed from** **“**Operating Track Record**”** **in v1.0. The v1.0 tiers awarded a pre-COD project 1.5 of 2 points by reference to its construction status, which Section 7.3 then notched for the same fact. This section now grades the** ****quality of the evidence base supporting the P90 assumption****, which is a genuinely separate question from construction status and is assessable for operating and pre-COD projects alike.*

**Two independent assessments, and the lower governs.** This section is scored by evaluating the project on a **performance limb** and an **evidence limb**, taking the highest row each limb reaches, and awarding the **lower of the two results**.

*Resolved in v3.0 (QA finding M4). v2.0 stated two mutually exclusive tie-break rules in consecutive sentences — "the highest applicable points apply" and "the lower governs" — which gave different answers on the same operating project. It also opened row 3 with "< 1 full operating year", which awarded a point for construction status alone; that is precisely the double-count that BL-5 removed from this section in v2.0, re-admitted through the tie-break. The limb construction below states one rule, and the construction-status limb is deleted.*

**Performance limb** — assessed only where `operating_years_completed` ≥ 1.00. Where the project has under one full operating year, the performance limb is **not assessed** and the evidence limb alone governs.

| Performance | Row |
| --- | --- |
| ≥ 3 full operating years, and actual generation ≥ 100% of P90 in **each** of the last three years | 1 |
| ≥ 1 full operating year, and actual generation ≥ 95% of P90 over the period | 2 |
| ≥ 1 full operating year, and actual generation ≥ 85% of P90 over the period | 3 |
| Actual generation < 85% of P90 | 4 |

**Evidence limb** — assessed for every project, operating or pre-COD.

| Evidence base | Row |
| --- | --- |
| Independent resource assessment **and** LTA-verified P90 **and** an EPC or O&M performance guarantee covering generation | 1 |
| Independent resource assessment **and** LTA-verified P90 | 2 |
| Independent resource assessment, with no independent verification of P90 | 3 |
| No independent resource assessment | 4 |

**Points from the governing row** — the higher-numbered (worse) of the two limb results:

| Governing row | Points |
| --- | --- |
| 1 | **2** |
| 2 | **1.5** |
| 3 | **1** |
| 4 | **0** |

*Worked consequence: a pre-COD project with no independent resource assessment reaches row 4 on the evidence limb, its performance limb is not assessed, and it scores **0** — not the 1 point v2.0's table awarded it for having no operating history. A three-year operating project generating at 105% of P90 but holding no resource assessment reaches row 1 on performance and row 4 on evidence, and scores **0**: the framework does not credit unverifiable outperformance.*

## 3.6 Operator and Sponsor Quality (2 points)

Scored on an **operator limb** and a **sponsor limb**, each taking the highest row it reaches, with the **lower of the two** governing. The two limbs are evaluated against disjoint, exhaustive conditions so that no input falls into two rows.

*Resolved in v3.0 (QA findings M11 and m18). v2.0's tier 3 sponsor limb required "documented committed support to **this** project", but Template 1 collected only support to a **comparable** project, so tier 3's sponsor limb was not scoreable from the collected inputs. Separately, an operator with zero years and zero MW satisfied both tier 3 ("< 3 years' experience or < 200 MW") and tier 4 ("No relevant operating experience"), with no precedence stated. Template 1 §A.8 now collects `sponsor_support_this_project` as a discrete flag, and the row conditions below are mutually exclusive.*

**Operator limb**

| Condition | Row |
| --- | --- |
| `operator_years` ≥ 5.0 **and** `operator_mw_under_om` ≥ 500 | 1 |
| `operator_years` ≥ 3.0 **and** `operator_mw_under_om` ≥ 200 | 2 |
| `operator_years` > 0 **and** not row 1 or 2 | 3 |
| `operator_years` = 0 **or** `operator_mw_under_om` = 0 | 4 |

**Sponsor limb**

| Condition | Row |
| --- | --- |
| `sponsor_projects_at_cod` ≥ 3 **and** `sponsor_support_comparable_count` ≥ 1 | 1 |
| `sponsor_projects_at_cod` ≥ 1 | 2 |
| `sponsor_projects_at_cod` = 0 **and** `sponsor_support_this_project` = `YES` | 3 |
| `sponsor_projects_at_cod` = 0 **and** `sponsor_support_this_project` = `NO` **and** `sponsor_support_comparable_count` = 0 | 4 |

**Points from the governing row** — the higher-numbered (worse) of the two limb results: row 1 → **2**; row 2 → **1.5**; row 3 → **1**; row 4 → **0**.

*[Developer calibration — provisional: the MW and year thresholds above.]*

# 4. Block B — Cash-flow Adequacy (35 points)

All ratios in this block are computed on cash flow available for debt service (CFADS), defined at Section 9.1, on the P90 generation basis defined at Section 9.5, and evaluated at the precision defined at Section 9.6.

## 4.0 Threshold-set selection and the merchant adjustment

**Technology-specific sets.** v1.0 applied a single set of DSCR thresholds derived from Fitch’s published guidance for **fully-contracted wind** projects to solar, wind, and hybrid projects alike, on the stated basis that this was “the only explicit numeric DSCR/rating correspondence found across the twenty-one reference documents.” That statement was incorrect: the source publishes distinct guidance by contracting status, and differentiates renewable technologies on resource-variability grounds. v2.0 therefore adopts three threshold sets, selected from the technology type at Template 1 §A.1:

| Technology type (Template 1 §A.1) | Threshold set applied |
| --- | --- |
| Wind | Set W |
| Solar PV | Set S |
| Solar + Wind Hybrid | Set H |

Set W is grounded in the published wind guidance. Sets S and H are **[Developer calibration — provisional]**, positioned below Set W to reflect the lower inter-annual variability of the solar resource, and are first-order candidates for revision after back-test.

**Merchant adjustment.** Where merchant exposure — computed by the engine as 1 − `contracted_revenue_share` (Section 3.2.1) — exceeds **0.2500**, **add 0.20x to every DSCR **tier** threshold in the applicable set** before tier lookup. The comparison is strict: an exposure of exactly 0.2500 does not trigger the adjustment. This mirrors the source guidance, under which a fully-merchant wind project requires materially higher coverage than a fully-contracted one for the same rating category. The adjustment applies to Sections 4.1 and 4.2 only.

**Basis disclosure.** The published anchors underlying Set W are stated on the source agency’s own rating case. This document applies them to a **P90** basis adopted from a different agency’s infrastructure criteria. These are two different calculation bases and are not interchangeable. Applying rating-case anchors to a P90 cash flow is a **deliberate conservatism**, since P90 is the more stressed basis; it is disclosed here rather than presented as an equivalence, and is recorded as a limitation at Section 11. This document does not adopt the source’s separate one-year P99 break-even test for investment grade.

## 4.1 Minimum DSCR — P90 Basis (15 points)

DSCR = CFADS ÷ (Interest + Scheduled Principal Repayment) for the period, computed on project cash flows only. A DSRA drawdown or sponsor contribution is not a CFADS inflow for this purpose (Section 9.7). Minimum DSCR is the lowest annual DSCR across the measurement set defined at Section 9.2.1.

| Tier | Set W (Wind) | Set S (Solar) | Set H (Hybrid) | Points |
| --- | --- | --- | --- | --- |
| Full | ≥ 1.50x | ≥ 1.40x | ≥ 1.45x | **15** |
| Strong | ≥ 1.30x | ≥ 1.25x | ≥ 1.28x | **11** |
| Adequate | ≥ 1.15x | ≥ 1.12x | ≥ 1.14x | **7** |
| Weak | ≥ 1.00x | ≥ 1.00x | ≥ 1.00x | **3** |
| Deficient | < 1.00x | < 1.00x | < 1.00x | **0** |

*Tiers are half-open: a value is assigned to the highest tier whose threshold it meets or exceeds. Add 0.20x to every **tier** threshold in the selected column where the merchant adjustment at Section 4.0 applies.*

**Coverage floor — an absolute test at 1.00x, never adjusted.** A Minimum DSCR below **1.00x** means the project cannot service its debt from its own cash flow in at least one period. This triggers a band cap at BB per Section 8.3, independent of the raw score, of the technology threshold set, and **of the merchant adjustment**.

*Resolved in v3.0 (QA finding M1). v2.0's Section 4.0 said the merchant adjustment applies to "every DSCR threshold in the applicable set", while Section 4.1 stated the coverage floor at a flat 1.00x, and Template 2 shifted the Weak tier to 1.20x but left the floor at 1.00x. The two readings diverge in a specific and consequential way: on the adjusted reading a merchant-exposed project between 1.00x and 1.20x scores **0 points** on Minimum DSCR **and** trips the cap; on the unadjusted reading it scores 0 points and does **not** trip the cap, which reopens exactly the asymmetry the coverage floor was introduced to close. The floor is now stated as absolute, and the merchant adjustment is expressly confined to the five **tier** thresholds. The rationale: the tier thresholds grade how much headroom a project has above self-sufficiency, and merchant volatility properly demands more of it; the floor tests whether the project is self-sufficient at all, which is a fact about the project and not about the basis on which it is graded.*

*Consequence, stated so no implementer has to derive it: where the merchant adjustment applies, a Minimum DSCR of, say, 1.10x scores 0 points (below the adjusted Weak threshold of 1.20x) but does **not** trigger the coverage floor, because 1.10x ≥ 1.00x. That combination — zero points on the 15-point factor without a band cap — is intended. Validation rule V8a warns on it so it is visible rather than silent.*

## 4.2 Average DSCR — P90 Basis (8 points)

Average DSCR is the **arithmetic mean of the annual DSCRs** across the measurement set at Section 9.2.1. It is not total CFADS divided by total debt service; on a sculpted amortisation profile the two diverge materially, and the arithmetic mean is specified.

| Tier | Set W (Wind) | Set S (Solar) | Set H (Hybrid) | Points |
| --- | --- | --- | --- | --- |
| Full | ≥ 1.70x | ≥ 1.60x | ≥ 1.65x | **8** |
| Strong | ≥ 1.50x | ≥ 1.42x | ≥ 1.46x | **6** |
| Adequate | ≥ 1.30x | ≥ 1.25x | ≥ 1.28x | **4** |
| Weak | ≥ 1.15x | ≥ 1.12x | ≥ 1.14x | **2** |
| Deficient | < 1.15x | < 1.12x | < 1.14x | **0** |

## 4.3 PLCR — Project Life Coverage Ratio (6 points)

*[Developer calibration — provisional: no agency in the reviewed corpus publishes a numeric PLCR tier table.]*

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | ≥ 2.00x | **6** |
| Strong | ≥ 1.60x | **4.5** |
| Adequate | ≥ 1.30x | **3** |
| Weak | ≥ 1.10x | **1.5** |
| Deficient | < 1.10x | **0** |

## 4.4 LLCR — Loan Life Coverage Ratio (6 points)

*[Developer calibration — provisional.]*

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | ≥ 1.80x | **6** |
| Strong | ≥ 1.50x | **4.5** |
| Adequate | ≥ 1.20x | **3** |
| Weak | ≥ 1.05x | **1.5** |
| Deficient | < 1.05x | **0** |

# 5. Block C — Financial Strength (25 points)

## 5.1 Project CFO / Adjusted Debt (10 points)

Adjusted Debt is defined at Section 9.3. Evaluated as a fraction to four decimal places.

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | ≥ 25.00% | **10** |
| Strong | ≥ 15.00% | **7.5** |
| Adequate | ≥ 8.00% | **5** |
| Weak | ≥ 3.00% | **2.5** |
| Deficient | < 3.00% | **0** |

## 5.2 Gearing — Total Debt / Tangible Net Worth (8 points)

*Retitled in v2.0. v1.0 titled this factor** **“**Gearing — Debt: Equity**”** **while Section 9.2 defined it as Total Debt / Tangible Net Worth. These are different ratios.** ****Total Debt / Tangible Net Worth is the governing definition****, per Section 9.3. The Debt:Equity equivalents shown below hold only where tangible net worth equals book equity, and are retained for orientation only — they are not the operative test.*

Gearing is a lower-is-better metric, so its tiers use **≤** thresholds.

| Tier | Criteria | Debt:Equity equivalent where TNW = equity | Points |
| --- | --- | --- | --- |
| Full | ≤ 1.8570x | ≈ 65:35 or lower | **8** |
| Strong | ≤ 2.3330x | ≈ 65:35 to 70:30 | **6** |
| Adequate | ≤ 3.0000x | ≈ 70:30 to 75:25 | **4** |
| Weak | ≤ 4.0000x | ≈ 75:25 to 80:20 | **2** |
| Deficient | > 4.0000x | ≈ beyond 80:20 | **0** |

*A value is assigned to the first tier, reading down, whose threshold it satisfies.*

**Where tangible net worth is nil or negative, this factor scores 0 points and validation rule V9 raises a Warn.** This is a **scored zero, not a null**: the field is present and its value is known, so it does not enter the Null Register and it does not reduce confidence through the null count at Section 9.8.3. *Resolved in v3.0 (QA finding M13): Template 2 v2.0 returned blank rather than 0 in this case, so a negative-net-worth project presented as a non-critical null — the same 8-point loss, but a Null Register entry and a confidence downgrade the criteria never called for.*

## 5.3 Liquidity — DSRA / Reserve Cover (7 points)

*v1.0’s text announced** **“**the four-tier liquidity classification convention**”** **above a five-row table. v2.0 states plainly that this is a** ****five-tier extension**** **of the published four-tier convention, adopted to give the 7-point factor sufficient granularity, with the additional tier disclosed rather than concealed inside a four-tier label.*

Measured as months of scheduled debt service covered by the **unencumbered portion** of the Debt Service Reserve Account or equivalent reserve, divided by average monthly debt service.

**Partial encumbrance rule.** Only the unencumbered portion counts. Where part of a reserve is pledged, margined, or earmarked for another purpose, **exclude that portion and score the remainder** — do not zero the factor. Template 2 collects the total reserve and the encumbered amount separately for this purpose.

**Scope of the numerator — DSRA only.** Months of cover is computed as `(dsra_total − dsra_encumbered) ÷ avg_monthly_debt_service`. **`other_cash_total` does not enter this calculation.** Other available cash is a general corporate balance, not a reserve dedicated to debt service, and a liquidity tier built on it would not survive a working-capital swing. Other unencumbered cash **does** enter the PLCR and LLCR numerators at Section 9.2, where the measure is deliberately a stock-versus-stock test of all available resources against outstanding principal.

*Resolved in v3.0 (QA finding m8). v2.0 was silent on the point. Template 2 excluded other cash from months of cover and included it in the PLCR/LLCR numerator — the right treatment, but an undocumented one, so a reviewer working from the criteria alone could include it and land a tier higher, failing the Section 0.2 determinism test.*

| Liquidity classification | DSRA / reserve cover | Points |
| --- | --- | --- |
| Superior | ≥ 12.0 months of debt service funded | **7** |
| Strong | ≥ 9.0 months | **5.5** |
| Adequate | ≥ 6.0 months | **4** |
| Stretched | ≥ 3.0 months | **2** |
| Poor | < 3.0 months | **0** |

# 6. Block D — Structural Protections (20 points)

Scored on the **count of named protections present**, not on a graded quality assessment. Every tier below is a count, so the block is encodable as a fixed checklist and no tier requires the implementer to judge whether gaps are “minor”.

## 6.1 Security and Cash-flow Waterfall (8 points)

Three elements are assessed:

- A trustee- or escrow-administered payment waterfall is in place.

- A comprehensive security package is in place — satisfied where **at least three of the four** following are present: charge over project assets; assignment of project contracts (PPA, EPC, O&M); charge over project bank accounts; pledge of sponsor shares in the SPV.

- A distribution lock-up tied to a stated minimum DSCR test is in place.

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | All three elements present | **8** |
| Partial | Exactly two elements present | **5** |
| Minimal | Exactly one element present | **2** |
| Absent | No element present | **0** |

## 6.2 Debt and Investment Covenants (6 points)

Four covenants are assessed: restriction on additional indebtedness; restriction on asset sales; restriction on change of control; lender step-in rights.

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | All four present | **6** |
| Partial | Exactly three present | **3.5** |
| Minimal | One or two present | **1.5** |
| Absent | None present | **0** |

## 6.3 Reporting, Hedging and Insurance (6 points)

Three items are assessed: a regular compliance and financial reporting covenant; an interest-rate/FX hedging policy; an insurance package including business-interruption cover.

| Tier | Criteria | Points |
| --- | --- | --- |
| Full | All three present | **6** |
| Partial | Exactly two present | **3.5** |
| Minimal | Exactly one present | **1.5** |
| Absent | None present | **0** |

*Hedging counts as present where the facility is a fully fixed-rate rupee facility with no FX exposure, so that a hedging policy is not applicable. This is recorded as** **“**Not Applicable**”** **at Template 1 §D.3 and scored as present.*

# 7. Notching Factors (Applied After the 115-Point Score)

Notching factors are **downward-only** adjustments layered on top of — not blended into — the weighted 115-point score. One notch is a fixed deduction of 7 points from the raw score before the Section 8 band mapping. Multiple notching factors are additive. The post-notching score is floored at zero.

**Terminology warning — two different meanings of "notch".** In this framework a *notch* is a 7-point deduction. In conventional rating usage a *notch* is one step on the alphanumeric scale, such as AA to AA−. **These are not the same unit and must never be compared as though they were.** A band in the Section 8.2 table spans between 8 and 22 points and covers roughly three conventional notches, so a −2-notch deduction here (−14 points) is approximately one and a half **bands**, not two conventional notches.

Where this document, the Execution Manual, or any output uses "notch" in the conventional sense — most importantly in the back-test, which compares this framework's output band against a published agency rating — it must say **"rating category"** or **"agency notch"** explicitly. The Execution Manual v3.0 has been amended accordingly. A back-test that reports "within one notch" without stating which unit it means is not interpretable.

*Resolved in v3.0 (QA finding m5). The mechanic keeps the name "notch" because "post-notching score" is embedded in the order of operations, the Results screen specification and the engine's return object, and renaming it would cost more clarity than it bought. The ambiguity is resolved where it actually caused harm — at the point of comparison.*

A risk already scored inside Blocks A–D is not also notched here, and vice versa, **save for the exceptions declared in the non-overlap map at Section 2**. One such exception falls in this section: hedging is assessed both at Section 6.3, as the existence of a policy, and at Section 7.2 mitigant 3, at the materially higher test of 75% coverage to maturity. See Section 2 for the reasoning and Section 9.7 for the liquidity exception.

## 7.1 Offtaker / Counterparty Risk — Graded Notch and Band Cap

### Step 1 — Crosswalk to a common internal risk tier

The C&I column below enumerates the full national long-term scale **including modifiers**, so that no rating falls between two tiers. The scale is the SEBI-standardised long-term scale — AAA, AA, A, BBB, BB, B, C and D, with "+" and "−" modifiers applicable to the categories AA through C — giving twenty symbols, all twenty of which appear in the table.

*Resolved in v3.0 (QA finding m3). v2.0's Poor/Unrated row read "CCC+ and below, C, D, or unrated". "CCC+" is not a symbol on the Indian national long-term scale at all; it is S&P/Fitch international-scale notation. The effect was that **C+ and C− were enumerated nowhere**, and the residual tier was anchored on a symbol that cannot occur — so the row's own claim to leave no rating between two tiers was false. The DISCOM column required no change: A+, A, B, B−, C, C− and D are the seven grades the Ministry of Power framework actually issues, and all seven were already enumerated.* The BBB−/BB+ step is the sharpest discontinuity in this framework — it converts a one-notch deduction into a two-notch deduction plus a BB band cap — so its placement is stated explicitly rather than left to inference.

| Internal risk tier | Tier value (for blending) | C&I customer — CRA long-term rating | DISCOM — MoP Integrated Rating |
| --- | --- | --- | --- |
| Strong | 4 | AAA, AA+, AA, AA− | A+, A |
| Adequate | 3 | A+, A, A−, BBB+, BBB, **BBB−** | B, B− |
| Weak | 2 | **BB+**, BB, BB−, B+, B, B− | C, C− |
| Poor / Unrated | 1 | C+, C, C−, D, or unrated | D, or not yet rated |

### Step 2 — Apply the notch and band cap by tier

*v1.0 assigned Weak and Poor/Unrated the same −2 notches, which collapsed a four-tier crosswalk into three tiers for scoring purposes. v2.0 differentiates them.*

| Risk tier | Notch adjustment | Band cap (Section 8.2) |
| --- | --- | --- |
| Strong | No adjustment | None |
| Adequate | −1 notch (−7 points) | None |
| Weak | −2 notches (−14 points) | Capped at **BB** — cannot be shown as investment grade |
| Poor / Unrated | −3 notches (−21 points) | Capped at **B** |

### Step 3 — Multiple offtakers

*v1.0 directed the engine to** **“**apply the weighted-average tier by contracted revenue share.**”** **Tiers are ordinal labels and cannot be averaged without assigned numeric values; none were given. v1.0 also set the single-offtaker dominance threshold at 10% of contracted revenue, which every project in the reference corpus exceeds — making the weighted average unreachable dead logic. Both are corrected below.*

**Dominance test (primary).** Where any single offtaker accounts for **≥ 25%** of contracted project revenue, the **worst tier among all offtakers meeting that threshold** governs, and its notch and cap apply. This is the operative test for the great majority of Indian renewable SPVs.

**Blended tier (fallback).** Only where **no** offtaker reaches 25% is a blend computed, using the tier values in the Step 1 table:

Blended tier value = Σ (tier value × contracted revenue share) ÷ Σ (contracted revenue shares)

The result is rounded to the nearest integer; a result of exactly x.5 rounds **down**, to the worse tier. The integer maps back to the tier of that value.

**The aggregated line is a single counterparty for both tests.** Template 1 provides fields for up to **four** offtakers individually. Where a project has more than four, the four largest by contracted revenue share are entered individually and the remainder is aggregated into a fifth "Other offtakers" line (`other_offtakers_share`, `other_offtakers_worst_tier`).

**For the dominance test and for the blend, the aggregated line is treated as one counterparty**, carrying `other_offtakers_share` and `other_offtakers_worst_tier`. So where the aggregated share reaches 0.25, the dominance test fires on it and its worst tier governs.

*Resolved in v3.0 (QA finding M7). v2.0 left this unstated, and the omission was structural rather than cosmetic: four individual offtakers each below 25% cannot sum to 100%, so **the aggregated line is the only route by which the blended-tier fallback is reachable at all**. Whether the fallback existed therefore depended on an unwritten rule. It is now written.*

*Note on the aggregated tier being user-supplied. `other_offtakers_worst_tier` is the one place in this framework where the user performs a crosswalk the engine performs everywhere else. It is retained because collecting full rating detail for a tail of small offtakers is disproportionate, but it is a declared exception: the engine records the field as user-derived in the Null Register metadata, the Results screen labels it as such, and Template 1 §N.6 requires the naming of the offtaker and rating the tier rests on.*

**Share summation.** Contracted revenue shares across the individual offtakers and the aggregated line must sum to 1.0000 ± 0.0100 (Section 10.1, V3).

*The 25% dominance threshold is a** ****[Developer calibration — provisional]****. It replaces v1.0’s 10% figure, which was attributed in Section 12 to a published methodology; because the threshold has been changed on the Developer’s own judgment, that attribution has been withdrawn in Section 12 and the row now records the calibration honestly.*

## 7.2 Refinancing Risk

*v1.0’s table populated only two of the four common combinations of refinancing size and mitigants, leaving** **“**large bullet with mitigants**”** **and** **“**partial bullet without mitigants**”** **unscored. Both are added, and** **“**partial**”** **and** **“**large**”** **are given numeric definitions.*

**Bullet share** = principal falling due in the final twelve months of the rated debt, as a percentage of original principal.

**Mitigants** are present where **at least one** of the following applies:

| Mitigant | Field | Test |
| --- | --- | --- |
| 1 | `mitigant_cash_sweep` | A contractual cash sweep applying ≥ 50% of surplus cash to prepayment |
| 2 | `mitigant_committed_refi` | A committed refinancing facility from a scheduled bank or NBFC |
| 3 | `mitigant_ir_hedge` | An interest-rate hedge covering ≥ 75% of floating-rate exposure to maturity |
| 4 | `mitigant_residual_ppa` | Residual contracted PPA tenor after final debt maturity of ≥ 5 years |

**Mitigant 3 and the fixed-rate case.** Where the rated debt is a fully fixed-rate rupee facility with no floating-rate exposure, there is nothing to hedge and the test does not arise. `mitigant_ir_hedge` = `NOT_APPLICABLE_FIXED_RATE` is **scored as present**, exactly as Section 6.3 treats the equivalent answer for the hedging policy at Template 1 §D.3. It is a different answer from `NO`, which asserts that floating-rate exposure exists and is unhedged.

*Resolved in v3.0 (QA finding M6). v2.0 was silent on this, and the silence was flagged inside Template 1 itself, which instructed the user to "confirm the scoring treatment against CORE §7.2 before relying on it" and noted that "§7.2 is presently silent". An open specification question had been shipped inside a template rather than closed in the criteria. It is not always immaterial: because Section 7.2 requires only one mitigant, the answer is harmless where another mitigant is `YES` and decisive where none is.*

| Bullet share | Mitigants | Adjustment |
| --- | --- | --- |
| ≤ 10% (fully amortising) | Either | No adjustment |
| > 10% and ≤ 25% (partial bullet) | Present | No adjustment |
| > 10% and ≤ 25% (partial bullet) | Absent | −1 notch |
| > 25% (large bullet) | Present | −1 notch |
| > 25% (large bullet) | Absent | −2 notches |

## 7.3 Construction and Ramp-up Risk

*v1.0’s table was titled** **“**Construction and Ramp-up Risk**”** **but contained no ramp-up row: row 1 required an established performance history, rows 2 and 3 required the project to be under construction, and a project three months past COD matched none of them. The ramp-up state is added.*

Scored from `project_state` and, where pre-COD, from `epc_structure`, `contractor_standing`, `contingency_share` and `execution_complexity`.

| # | Condition | Adjustment |
| --- | --- | --- |
| 1 | `project_state` = `STATE_OPERATING_MATURE` | No adjustment |
| 2 | `project_state` = `STATE_OPERATING_RAMPUP` | −1 notch |
| 3 | `project_state` = `STATE_PRECOD`, **and** `epc_structure` = `EPC_TURNKEY`, **and** `contractor_standing` = `CONTR_ADEQUATE`, **and** `contingency_share` ≥ 0.0500, **and** `execution_complexity` = `EXEC_STANDARD` | −1 notch |
| 4 | `project_state` = `STATE_PRECOD`, and row 3 not fully satisfied | −2 notches |

*Where more than one adverse condition in row 4 applies, the adjustment remains −2 notches; this factor does not stack within itself.*

*Resolved in v3.0 (QA finding M5). v2.0's row 1 turned on the phrase "with an established performance history", which was defined nowhere in the document — the last undefined qualitative term in the notching tables, sitting on a 7-point step — and Template 1 bundled it into a single option string, so **no state existed for a project operating twelve months or more without one**. The phrase is deleted. Row 1 now turns on the 12-month test alone, which is objective and already collected. The quality of the generation record it would have gestured at is graded where it belongs, at Section 3.5, on evidence the template actually captures.*

*Row 3 also now states `execution_complexity` explicitly. v2.0 listed elevated execution complexity among row 4's disqualifying conditions but omitted it from row 3's qualifying set, so a project with a turnkey EPC, an adequate contractor, 6% contingency and elevated complexity matched both rows.*

# 8. Score-to-Band Mapping, Caps, and Order of Operations

## 8.1 Order of operations

The engine executes these steps in this order. No step may be reordered.

*These are the scoring steps. They are Stage 4 of the five-stage pipeline at **Section 10.1.1**, which states when null resolution and validation run relative to scoring. Section 10.1.1 governs; this list expands its Stage 4.*

- Score every sub-factor in Sections 3–6, on the input set already resolved for nulls at Section 10.1.1 Stage 2.

- Sum to the raw score (maximum 115). No rounding at sub-factor, block, or total level.

- Apply all applicable notches from Section 7 (7 points each, additive, downward only). Floor the result at 0. This is the **post-notching score**.

- Map the post-notching score to an **indicative band** using the table at Section 8.2.

- Determine the applicable band caps (Section 8.3). The **final band** is the lower of the indicative band and the lowest applicable cap.

- Compute the confidence level (Section 9.8).

- Apply the display flags at Section 8.4.

## 8.2 Band table — half-open intervals

*v1.0 stated this table as closed integer ranges (108–115, 100–107, 90–99, 78–89, 64–77, 43–63, 22–42, 0–21). Because sub-factor points include half-point values, seven reachable scores — including 77.5, which sits exactly on the investment-grade boundary — fell into no band at all. Restating the table as half-open intervals eliminates the entire class of defect rather than patching the seven instances.*

| Post-notching score | Indicative rating band | Investment grade? |
| --- | --- | --- |
| ≥ 108 | AAA | Yes |
| ≥ 100 and < 108 | AA (AA− to AA+) | Yes |
| ≥ 90 and < 100 | A (A− to A+) | Yes |
| ≥ 78 and < 90 | BBB (BBB− to BBB+) — lowest investment-grade band | Yes |
| ≥ 64 and < 78 | BB (BB− to BB+) — highest non-investment-grade band | No |
| ≥ 43 and < 64 | B (High Risk) | No |
| ≥ 22 and < 43 | C (Very High Risk) | No |
| ≥ 0 and < 22 | D (Substantial Risk / Default Profile) | No |

The intervals are exhaustive and mutually exclusive across the full reachable range [0, 115]. Every reachable score, including every half-point value, maps to exactly one band.

**AAA and notching.** The engine does **not** block an AAA result on account of notching having been applied. A project scoring 115 that takes one notch lands at 108 and is mapped to AAA. AAA remains rare because the raw score required is near-perfect, but rarity is a consequence of the arithmetic, not a separate rule. The only band-limiting mechanisms in this framework are the caps at Section 8.3.

## 8.3 Band caps — cap-the-band, not cap-the-score

*v1.0 specified a** **“**hard cap on final band**”** **but never defined how it interacts with the score-driven table, leaving the implementer to choose between capping the score and capping the band, with different results. v2.0 specifies** ****cap-the-band****.*

**Mechanic.** A cap constrains the **band**, not the score. The post-notching score is not altered by a cap. Where a cap applies, the final band is the capped band and the numeric score is reported unchanged.

| Cap trigger | Source | Capped band |
| --- | --- | --- |
| Offtaker/counterparty tier = Weak | Section 7.1 | BB |
| Offtaker/counterparty tier = Poor / Unrated | Section 7.1 | B |
| Minimum DSCR < 1.00x (coverage floor) — **absolute, never shifted by the merchant adjustment** (Section 4.1) | Section 4.1 | BB |

Where more than one cap applies, the **lowest** capped band governs.

**Coverage floor rationale.** v1.0 provided a hard cap for offtaker risk but no equivalent override for coverage. A project scoring zero across the entire Cash-flow Adequacy block could still reach 80 points and be shown as BBB; a project with Minimum DSCR alone at zero — meaning it cannot service debt from its own cash flow — could reach 100 and be shown as ‘A’. Coverage is the more fundamental credit fact, and the floor at Section 4.1 corrects the asymmetry.

## 8.4 Results screen display requirements

Because a cap can separate the numeric score from the band, the Results screen must display both, and must not present either alone:

- **Post-notching score**, out of 115, as computed at step 3 — displayed unchanged, whether or not a cap applies.

- **Indicative band** from the score (step 4).

- **Final band** after caps (step 5).

- Where the final band differs from the indicative band, a **mandatory cap notice** naming the trigger, in the form: *“**Band capped at [band] — [trigger]. Score-implied band was [band].**”*

- **Confidence badge** (High / Moderate / Low / Not Rated) per Section 9.8.

- The four block sub-scores against their maxima, and the notches applied with their sources.

- Any band at or below BB carries an explicit **“****Non-Investment Grade / Elevated Risk****”** flag.

- Any band in the C or D range triggers a **mandatory QA-agent review flag** rather than a routine result.

- The BBB/BB boundary (the 78-point line) is visually distinguished, being the single most operationally important line in the table.

- The **Null Register** (Section 9.8) is displayed wherever it is non-empty.

# 9. Formula and Definitions Appendix

## 9.1 Cash Flow Available for Debt Service (CFADS)

**Primary construction (governing).**

CFADS = Project revenue − cash operating expenses − maintenance and lifecycle costs (or contractual MMRA deposits) − increase in working capital − cash taxes ± interest received on operating cash balances

**Exclusions, stated explicitly.** Interest expense and scheduled principal repayment are **excluded** from CFADS — they are the denominator of DSCR and cannot also reduce the numerator. A DSRA drawdown, an equity or sponsor contribution, and a debt drawdown are **not** CFADS inflows.

**Cash taxes convention.** Cash taxes are computed after the deductibility of interest on the rated debt, consistent with the project’s actual tax position; the resulting figure is the cash tax outflow for the period. Where a tax holiday or MAT position applies, it is applied as it actually falls.

**Permitted reconciliation route.** v1.0’s Section 10 required “PAT, depreciation, interest, principal schedule” as Block B inputs — the net-cash-accrual construction, a different formula giving different answers from Section 9.1’s build. Where a financial model produces CFADS by that route, it is permitted, provided it reconciles to the primary construction:

CFADS = PAT + depreciation and amortisation + interest expense − increase in working capital − maintenance capex or MMRA deposits ± non-cash adjustments

The two routes must agree within **2%** for every period. A larger divergence is a validation failure (Section 10.1) and blocks scoring.

## 9.2 Coverage Ratio Formulas

- **DSCR** = CFADS ÷ (Interest + Scheduled Principal Repayment) for the period, on project cash flows only, excluding DSRA drawdown and sponsor support.

- **PLCR** = [NPV of CFADS over the remaining project or asset life, **plus** the unencumbered DSRA **and** other available unencumbered cash] ÷ principal outstanding on the rated debt plus equally- or more-senior debt, at the calculation date. *Other unencumbered cash enters here and, per Section 5.3, does **not** enter the liquidity months-of-cover calculation.*

- **LLCR** = [NPV of CFADS over the remaining loan life to final maturity, **plus** the unencumbered initial DSRA and other available unencumbered cash] ÷ principal outstanding on the rated debt **plus equally- or more-senior debt**, at the calculation date.

*The pari passu and senior addition is now stated in both denominators. v1.0 included it in PLCR but omitted it from LLCR, which was an omission rather than a distinction — Template 2 already assumed the inclusive definition for both.*

- **Gearing** = Total Debt ÷ Tangible Net Worth (Section 9.3).

- **Project CFO / Adjusted Debt** = Project cash flow from operations ÷ Adjusted Debt (Section 9.3).

### 9.2.1 DSCR measurement period

- **Period.** Annual periods, from the calculation date to the final maturity of the **rated debt**.

- **Stub period.** A first period shorter than twelve months is annualised for DSCR purposes; its DSCR is included in both the minimum and the average.

- **Construction-period years.** A year in which no scheduled debt service falls due yields an undefined DSCR and is **excluded** from both the minimum and the average. A year in which debt service falls due before COD **is included**, on the cash flow actually available in that year.

- **Pre-COD projects.** Minimum DSCR is computed over the post-COD scheduled service years, plus any pre-COD year carrying scheduled service.

- **Averaging.** Arithmetic mean of the annual DSCRs across the included set (Section 4.2).

## 9.3 Debt, Adjusted Debt, and Tangible Net Worth

*v1.0 defined Adjusted Debt circularly —** **“**total project debt (adjusted for any non-recourse or off-balance-sheet items as applicable)**”** **— which is unhelpful for an SPV that is non-recourse by construction, and left Total Debt and Tangible Net Worth undefined altogether. For Indian renewable SPVs the treatment of subordinated sponsor loans, working-capital lines, and compulsorily convertible debentures moves Sections 5.1 and 5.2 by whole tiers, so each is now specified.*

**Total Debt** comprises all interest-bearing liabilities of the SPV at the calculation date:

- Rupee and foreign-currency term loans, and non-convertible debentures

- Drawn working-capital borrowings, including cash credit and drawn letters of credit

- Finance and capital lease liabilities

- **Subordinated sponsor loans — included**, unless they meet the equity-treatment test below

- **Compulsorily convertible debentures — included**, unless they meet the equity-treatment test below

**The default classification is `TREATMENT_DEBT` for every instrument, including sponsor loans and CCDs.** `TREATMENT_EQUITY` requires affirmative satisfaction of all three conditions below and is recorded per instrument. **A blank treatment is a null, not a default**, and validation rule V14 blocks it. *Resolved in v3.0 (QA finding B4): Template 2 v2.0 shipped with CCDs pre-classified as Equity, inverting this rule on the very field this section says moves Sections 5.1 and 5.2 by whole tiers, and an instrument with a blank treatment was silently excluded from both Total Debt and Tangible Net Worth.*

**Adjusted Debt** = Total Debt as defined above. For the standalone SPV perimeter at Section 0.3 there is no further adjustment; the term is retained for continuity with Section 5.1’s title, and the identity is stated so no implementer has to infer it.

**Tangible Net Worth (TNW)** = paid-up equity share capital + securities premium + free reserves + instruments meeting the equity-treatment test, **less** intangible assets, **less** revaluation reserves, **less** accumulated losses, **less** deferred revenue expenditure not written off.

**Equity-treatment test.** A subordinated sponsor loan or CCD is treated as equity — excluded from Total Debt and included in TNW — only where **all three** conditions hold:

- It is mandatorily and fully convertible into equity, or not repayable, before the final maturity of the rated debt.

- No coupon or interest is payable in cash ahead of scheduled debt service on the rated debt.

- It is contractually subordinated to the rated debt in right of payment and on enforcement.

An instrument failing any condition is Total Debt. The classification applied must be recorded per instrument at Template 2, so the treatment is auditable rather than assumed.

## 9.4 Discount Rate for PLCR and LLCR

The weighted-average effective interest rate actually contracted on the rated debt facility or facilities, as stated in the loan agreement or sanction letter at the calculation date — not a rate implied by the project’s output rating. For a facility with multiple tranches or a floating-rate structure, use the blended effective rate at the calculation date; where hedged, use the hedged or capped rate. Record the rate with its “as of” date, consistent with the staleness convention at Section 9.9.

## 9.5 P90 Generation Basis

All DSCR calculations in Section 4 use the project’s P90 annual Plant Load Factor — the generation level the asset is expected to exceed in 90% of years — rather than the P50 design estimate. P50 and P90 estimates are expected to derive from an independent resource-assessment study (solar irradiance or wind-speed data combined with the relevant equipment power curve).

**P90 attestation requirement — attestation is the only route.** *v1.0 mandated a P90 basis, and Template 2 collected a P90 PLF figure, but nothing in the engine used or verified it: CFADS was entered directly, and a user pasting a P50 CFADS obtained a P50 score labelled P90.*

Before Block B can be scored, **all four** of the following must be populated:

| Field | Requirement |
| --- | --- |
| `p90_plf` | The P90 annual plant load factor, as a decimal fraction |
| `p90_attestation_basis` | Must equal the single permitted value `ATTESTED_P90`. There is no other permitted value. |
| `p90_resource_study` | The resource-assessment study relied on, and its date |
| `p90_preparer` | The name of the attesting preparer, and the date of attestation |

Absent any of the four, `p90_plf` is treated as a **null critical input**, no band is issued, and the engine returns "Insufficient Input — Not Rated" naming the missing field (Section 9.8.1).

*Resolved in v3.0 (QA finding B5). v2.0 offered a derivation route — "(a) CFADS is derived within Template 2 from the entered P90 PLF, so the basis is arithmetically enforced" — and Template 2 did not implement it. No formula linked the entered P90 PLF to the CFADS schedule; CFADS remained a hardcoded input. Route (a) was therefore an unenforced self-declaration wearing the language of arithmetic enforcement, which is worse than no route at all, because it invited reliance. Worse, Template 2's status formula returned "Satisfied" for any string other than blank or the attestation value, so selecting the derivation option passed the gate with no derivation and no attestation.*

*Route (a) is **withdrawn**. Attestation is now the only route, `p90_attestation_basis` is a constant rather than an enumeration, and all four fields are critical. Deriving CFADS from a PLF requires net capacity, tariff, escalation, opex and working-capital inputs that this framework deliberately does not collect — Template 2 captures the outputs of the project's financial model, not the model itself (Section 0.3) — so building the derivation properly would have meant expanding the template into a cash-flow model. Naming the study and the preparer, and making the omission of either a critical null, places the accountability where it belongs and is enforceable.*

**Operating assets.** For an asset with at least three full years of history, actual generation may **inform** but not automatically override the P90 assumption. A sustained record materially above or below the original P90 is reflected in Section 3.5 and flagged for input-level review before the DSCR calculation basis itself is reset.

## 9.6 Precision, Rounding, and Boundary Convention

*v1.0 stated every quantitative tier as a closed range with a gap to the next —** **“**1.30x – 1.49x**”** **then** **“**≥ 1.50x**”** **— so a Minimum DSCR of 1.495x belonged to no tier. The same hole existed at every boundary in every quantitative table, and at Section 5.1 an entire percentage point was unclassified at each of three boundaries on a 10-point factor. Template 2 resolved it with a ≥ cascade, which was the sensible reading but was the workbook’s reading and not this document’s, and was undocumented. The convention is now stated here and governs.*

**Threshold form.** Every quantitative tier in this document is stated as a single-sided threshold:

- Higher-is-better metrics (DSCR, PLCR, LLCR, CFO/Adjusted Debt, DSRA cover, contracted share) use **≥**.

- Lower-is-better metrics (Gearing, reinvestment ratio, bullet share) use **≤**, except the residual bottom tier, which uses **>**.

- A value is assigned to the **highest** qualifying tier for higher-is-better metrics, and to the **first qualifying tier reading down** for lower-is-better metrics. There are no gaps and no overlaps.

**Percentage representation — decimal fractions only.**

> **All percentage inputs are transmitted and stored as decimal fractions; no field carries a value out of 100.**

97% is `0.9700`. A 25% merchant-exposure threshold is `0.2500`. A 5% contingency is `0.0500`. This applies to every percentage field in the framework without exception: `contracted_revenue_share`, `contracted_share_full_tenor`, `contracted_share_75pc_tenor`, `reinvestment_ratio`, `p90_plf`, all four `actual_gen_vs_p90_*` fields, `bullet_share`, `contingency_share`, `discount_rate`, every `offtakers[].contracted_share`, `other_offtakers_share`, and the derived merchant exposure and CFO/Adjusted Debt ratios.

*Resolved in v3.0 (QA finding B7). v2.0 stated this convention here and Template 2 implemented it, but Template 1 asked for "%… to two decimal places" on six fields and the Test Projects sheet stated its percentages out of 100. Nothing anywhere stated the conversion. The failure mode is silent rather than loud: a contracted revenue share arriving as 0.97 where 97 is expected scores 0 instead of 8 at Section 3.2.1 and computes merchant exposure at 99.03%, firing the merchant adjustment on a 97%-contracted project. Both templates and the Test Projects sheets are restated as fractions in v3.0, and every percentage field in Appendix B carries the unit `frac`.*

**Evaluation precision.**

| Input class | Precision | Rounding |
| --- | --- | --- |
| Coverage ratios (DSCR, PLCR, LLCR) and gearing | 4 decimal places | Round half up at the 4th decimal place |
| Percentages (CFO/Adjusted Debt, contracted share, contingency, bullet share) | Stored as fractions, 4 decimal places (0.01 percentage point) | Round half up at the 4th decimal place |
| Months of cover | 1 decimal place | Round half up at the 1st decimal place |
| Years of operating history | 2 decimal places | Round half up at the 2nd decimal place |

**No tolerance band.** The stated comparison operator is applied strictly at the stated precision. A Minimum DSCR of 1.4999x does not reach a ≥ 1.50x tier.

**Points and score.** Points are exact values as tabulated, in increments of 0.5. No rounding is applied at sub-factor, block, or total level. Notches are exact multiples of 7. The band lookup at Section 8.2 is performed on the exact post-notching score.

## 9.7 Non-Double-Counting Rule

An asset counted within the Liquidity sub-factor (Section 5.3) **may not** also be counted within CFADS as a cash inflow for **DSCR** purposes (Sections 4.1, 4.2, and 9.1).

**Stated exception — DSRA in the PLCR and LLCR numerators.** The same reserve **may** be counted in the PLCR and LLCR numerators at Section 9.2. This is the conventional treatment in project finance: PLCR and LLCR are stock-versus-stock coverage measures at a point in time, and available cash properly forms part of the resources measured against outstanding principal, whereas DSCR is a flow measure of a single period’s self-sufficiency. v1.0’s Section 9.5 named Section 9.2 in its prohibition while Section 9.2 required the same balance in the numerator, so the two sections gave opposite instructions on the same cash balance, and Template 2 implemented the contradiction while describing itself as compliant. **The exception is now explicit and is the governing rule.** Template 2’s note has been corrected accordingly.

The remaining consequence is disclosed rather than concealed: one DSRA balance influences up to 7 points at Section 5.3 and up to 12 points at Sections 4.3 and 4.4. That is a deliberate design choice reflecting standard practice, not an oversight.

*v1.0’s third clause — prohibiting liquidity from justifying a more favourable offtaker notch — has been removed. Section 7.1’s notch derives solely from an external published rating, so no mechanism existed through which liquidity could influence it; the clause implied a pathway that does not exist.*

**Companion prohibitions.** Offtaker credit quality is scored only at Section 7.1 and nowhere in Block A. Construction and ramp-up status is scored only at Section 7.3 and nowhere in Block A. See the non-overlap map at Section 2.

## 9.8 Missing Inputs, Null Scoring, and Confidence

*v1.0 stated that a missing field** **“**should register as** **‘**null, not guessed**’** **… and should reduce the engine’s confidence output**”** **— a data-capture rule, not a scoring rule. What a null sub-factor** ****scored**** **was never stated, and three plausible readings (null scores zero; the block re-weights pro rata; the rating is suppressed) give three different ratings for the same project.** **“**Confidence output**”** **appeared nowhere else in this document; the only definition in the project sat in the Execution Manual and turned on the words** **“**comfortably**”** **and** **“**near**”**, neither of which is numeric. Both gaps are closed here, and this section is the single governing definition for the whole project.*

### 9.8.1 Critical inputs — null suppresses the rating

Where any of the following is null, the engine returns **“****Insufficient Input — Not Rated****”**, issues no band, and names the missing fields. It does not score them as zero.

- `technology_type` (Template 1 §A.1) — required to select the Section 4 threshold set

- `project_status` and, where operating, `cod_date` (Template 1 §A.1) — required for Section 7.3

- `calculation_date` (Template 1 §A.1) — required for V11 and for every remaining-tenor and as-of-date computation. *Added in v3.0 (QA finding m19): v2.0 omitted it, although V11 is a Block rule that cannot run without it.*

- `dscr_schedule[]`, **or** a directly entered `minimum_dscr` (Template 2). Either route satisfies the requirement; see Appendix B note 1 for how the two interact.

- `p90_plf`, **together with all three attestation fields** — `p90_attestation_basis`, `p90_resource_study`, `p90_preparer` — per Section 9.5

- `total_debt` and `tangible_net_worth` (Template 2), and a `treatment` on every instrument carrying an amount (Section 9.3, V14)

- `contracted_revenue_share` (Template 1 §A.2)

- `offtakers[].type` and `offtakers[].rating_or_grade`, for **any** offtaker whose `contracted_share` is ≥ **0.2500** (Template 1 §N.2–N.6), including the aggregated line

### 9.8.2 Non-critical inputs — null scores zero and is registered

Any other null input scores **0 points** for its sub-factor. Null is not re-weighted pro rata across the block, and the block maximum is not reduced: re-weighting would silently reward incomplete submissions, and a 115-point denominator that varies by project is not comparable across projects or against the band table.

Every null is recorded in a **Null Register** — field name, sub-factor affected, points forgone — which is returned with the result and displayed on the Results screen per Section 8.4. A “Not Applicable” answer is a deliberate answer, not a null, and is scored per the relevant table.

### 9.8.3 Confidence — numeric definition

Let **d** = the absolute distance, in points, between the post-notching score and the nearest band edge. Let **N = 3.0 points**.

**Band edges are the seven interior thresholds: 22, 43, 64, 78, 90, 100 and 108.** The endpoints of the reachable range, **0 and 115, are not band edges** and are excluded from the calculation of *d*.

*Resolved in v3.0 (QA finding M2). v2.0 said only "the nearest band edge in the Section 8.2 table", and the table's first row is stated as "≥ 0 and < 22", so 0 reads as an edge of the D band on the plain wording. That reading breaks two of the three reference projects: TP-3 has a post-notching score of exactly 0 and TP-1 exactly 115, and the Test Projects sheet gives them d = 22.0 and d = 7.0 with **High** confidence — figures that are only reachable if 0 and 115 are not edges. A reviewer applying the v2.0 wording literally gets d = 0 for both and **Moderate** confidence, failing the Section 0.2 determinism standard on the document's own worked examples. The exclusion is correct on the merits as well as necessary for consistency: 0 and 115 are the arithmetic limits of the scale, not boundaries between adjacent opinions, and a score sitting at either is maximally far from any reclassification rather than adjacent to one.*

| Confidence | Conditions (all must hold for High; any one suffices for the lower levels) |
| --- | --- |
| **Not Rated** | Any critical input at Section 9.8.1 is null |
| **Low** | Four or more non-critical nulls; or any input stale by more than one publication cycle (Section 9.9); or an ALMM parameter more than 90 days past its “as at” date (Section 3.3.3) |
| **Moderate** | One to three non-critical nulls; or **d ****<**** 3.0**; or a **binding** band cap has been applied (Section 8.3); or any input flagged stale |
| **High** | No nulls; **d ≥ 3.0**; no binding cap; no input flagged stale |

Where more than one row’s conditions are met, the **lowest** applicable confidence governs. Confidence is computed by the engine from this rule; it is never set by hand and never defaults to High.

**“****Binding****”**** ****cap.** A cap counts as applied for confidence purposes only where it **binds** — that is, where the final band differs from the indicative band. A cap that triggers but does not bind, because the score-implied band already sits at or below the capped band, does not reduce confidence. The distinction matters: a project whose raw score already puts it in D loses nothing in certainty from an offtaker cap at BB.

**Confidence measures the assessment, not the credit.** A complete, unambiguous, well-inside-the-band D is a High-confidence result. Confidence answers “how much should the reader trust that this band is the band this framework produces for these inputs” — not “how creditworthy is this project”. The engine must not conflate a weak rating with an uncertain one, and the Results screen must not imply that it does.

## 9.9 Offtaker / Counterparty Rating Sources

**C****&****I customers:** the offtaker’s own published long-term credit rating from a SEBI-registered CRA. **DISCOMs:** the Integrated Rating and Ranking of Power Distribution Utilities, published annually by Power Finance Corporation Limited under the framework approved by the Ministry of Power, Government of India — a 100-point composite (Financial Sustainability, Performance Excellence, External Environment, with Red-Card penalty deductions) converted to a letter grade from A+ down to D.

**Staleness convention.** The engine records the rating or ranking edition and date used for each assessment. An input is **stale** where a more recent edition has been published and not used, or where a C&I rating is more than twelve months old. A stale input downgrades confidence per Section 9.8.3 and is flagged on the Results screen; it is never silently applied.

# 10. Required Inputs Summary and Validation Rules

## 10.1 Internal-consistency validation rules

*v1.0 specified no validation rules, so an arithmetically impossible input set would score silently. Section 10.1.1 states when these checks run relative to null resolution and scoring. A** ****Block**** **result prevents scoring — every remaining rule is still evaluated first, so the report is complete (Section 10.1.1 Stage 3); a** ****Warn**** **result proceeds and is displayed on the Results screen; a** ****Not Evaluated**** **result means at least one operand was null.*

**Input validations.** These test the submitted input set. Each runs only where every operand it needs is populated; otherwise it returns **Not Evaluated** (Section 10.1.1).

| # | Check | Result if failed |
| --- | --- | --- |
| V1 | Average DSCR ≥ Minimum DSCR | Block |
| V2 | PLCR ≥ LLCR (remaining project life ≥ remaining loan life) | Block |
| V3 | Contracted revenue shares across the individual offtakers and the aggregated line sum to 1.0000 ± 0.0100 | Block |
| V6 | Where a net-cash-accrual CFADS series is supplied (Section 9.1), it agrees with the direct build within 2% **in every period, tested period by period** | Block |
| V7 | `dsra_encumbered` ≤ `dsra_total` | Block |
| V7a | `other_cash_encumbered` ≤ `other_cash_total` | Block |
| V8 | Minimum DSCR < 1.00x coexisting with PLCR ≥ 2.00x — close to incoherent | Warn |
| V8a | Minimum DSCR scores 0 points but the coverage floor has not triggered — reachable only where the merchant adjustment applies (Section 4.1) | Warn |
| V9 | Tangible net worth nil or negative | Warn (Section 5.2 scores 0) |
| V11 | `project_status` = `STATUS_OPERATING` with `cod_date` later than `calculation_date` | Block |
| V12 | Any offtaker rating, discount rate, or ALMM parameter flagged stale | Warn |
| V13 | Fields captured in both templates agree: `technology_type`, `calculation_date`. Merchant exposure is derived, never entered, so no comparison arises. | Block |
| V14 | Every instrument in `debt_instruments[]` with a non-zero `amount` carries a `treatment` of `TREATMENT_DEBT` or `TREATMENT_EQUITY` | Block |

**Engine assertions.** These test the engine's own arithmetic, not the user's input. They cannot be evaluated before scoring and are not affected by nulls. A failure is a defect in the implementation and must halt the response rather than be displayed as a data problem.

| # | Assertion | Result if failed |
| --- | --- | --- |
| A1 (was V4) | Sum of the four block sub-scores equals the raw score | Halt — implementation defect |
| A2 (was V5) | Raw score ≤ 115, and each block sub-score ≤ its maximum (35 / 35 / 25 / 20) | Halt — implementation defect |
| A3 (was V10) | Where derived merchant exposure > 0.2500, the +0.20x adjustment is present in the Section 4.1 and 4.2 threshold lookups actually used | Halt — implementation defect |
| A4 | Where a cap binds, `post_notching_score` is byte-identical to the score the same inputs produce with the cap suppressed | Halt — implementation defect |

*Resolved in v3.0 (QA findings m7, M8, M9, M14). v2.0 listed twelve rules of two different kinds under one heading. V4, V5 and V10 do not test input at all — they test whether the engine added up correctly and whether it applied its own adjustment — so classifying them as "Block" implied a user could clear them by correcting data, which is false. They are now assertions. V6 is restated to say period by period, which is what it always required and not what Template 2 implemented. V3 and V7 are restated in fraction terms. V7a, V8a, V13 and V14 are new: V7a closes the gap that only DSRA encumbrance was checked; V8a surfaces the Section 4.1 merchant consequence; V13 closes the unreconciled cross-template duplication; V14 catches an instrument carrying an amount with no equity treatment, which v2.0 silently excluded from both Total Debt and Tangible Net Worth.*

## 10.1.1 Pipeline order — null resolution, validation, scoring

*New in v3.0. Resolves QA finding B6. v2.0 said at Section 10.1 that the engine "must apply every check below **before scoring**" and at Section 8.1 step 1 that null rules are applied **during** scoring. The two orderings give different answers on the same project, and the case is not exotic: Average DSCR is a non-critical input, so under Section 9.8.2 a null Average DSCR scores 0 and registers — but V1 (Average DSCR ≥ Minimum DSCR) is a **Block**. A project with Minimum DSCR supplied and Average DSCR null therefore had two lawful outcomes, which is exactly the implementer discretion Section 0.2 forbids. The same pattern arose at V2 with a null PLCR or LLCR and at V7 with a null DSRA. Template 2 had quietly invented a third behaviour, returning "Not evaluated" strings that appeared in neither document.*

**The engine executes these stages in this order. No stage may be reordered or interleaved.**

- **Stage 1 — Critical null resolution.** Test every critical input at Section 9.8.1. If any is null, return **"Insufficient Input — Not Rated"**, name every missing critical field, set confidence to **Not Rated**, and **stop**. No score, no band, no validation results, no partial output.

- **Stage 2 — Non-critical null resolution.** Resolve every remaining null to 0 points for its sub-factor and record it in the Null Register (Section 9.8.2). The block maximum is not reduced. A `NOT_APPLICABLE_*` code is a deliberate answer, not a null.

- **Stage 3 — Input validation.** Run V1 to V14. **A rule runs only where every operand it requires is populated.** Where any operand is null, the rule returns **Not Evaluated** and does not block. If any rule returns **Block**, the engine still **evaluates every remaining rule** and returns the complete validation report, then stops without scoring — it does not halt on the first Block. *Stated in v3.0 because the wording was silent and both readings are defensible. Running on is the better of the two: the rules are mutually independent, so a Block in one tells you nothing about the others, and a user who is shown one failure at a time must correct and resubmit once per failure. The validation screen exists so that a preparer can see everything wrong with a submission in a single pass.* **Warn** and **Not Evaluated** results proceed to Stage 4 and are carried into the output.

- **Stage 4 — Scoring.** Execute Section 8.1 steps 1 to 7 on the resolved input set.

- **Stage 5 — Engine assertions.** Run A1 to A4. Any failure halts the response as an implementation defect.

**`Not Evaluated` is the fourth validation outcome**, alongside Pass, Warn and Block (`VALIDATION_4`, Appendix A).

**Not Evaluated does not itself reduce confidence.** The null that caused it already reduces confidence through Section 9.8.3's null count, and counting the same missing field twice would double-penalise it. A Not Evaluated result is displayed on the Results screen alongside the Null Register entry that explains it, so the reader can see which check was not performed and why.

*Worked example. A project supplies Minimum DSCR but not Average DSCR. Stage 1 passes — the DSCR schedule is present, so the critical input is satisfied. Stage 2 scores Section 4.2 at 0 and registers `average_dscr` in the Null Register, 8 points forgone. Stage 3 returns V1 = **Not Evaluated**. Stage 4 scores the project, 8 points short. Confidence is at most **Moderate**, on the single non-critical null. The project receives a band, the reader can see exactly what was missing and what it cost, and no implementer had to choose between two readings.*

## 10.2 Required inputs by block

| Block | Required inputs |
| --- | --- |
| A — Business/Operating | Technology type; project status and COD date; enumerated competitive and essentiality position; contracted revenue share (%) and remaining contracted tenor; enumerated tariff structure, take-or-pay and termination-payment provisions; three permitting statuses plus any live dispute; enumerated regulatory stability; enumerated technology maturity; enumerated balance-of-plant and grid complexity; ALMM compliance status (solar) or WTG Indian operating history (wind); reinvestment ratio and funding source; operating years and actual generation as % of P90, or the pre-COD evidence set (independent resource assessment, LTA-verified P90, performance guarantee); operator years and MW operated; sponsor projects at COD and documented support history. |
| B — Cash-flow | P90 annual PLF **plus the full attestation set per Section 9.5** (basis, resource study, preparer); the annual CFADS figure per period, with annual interest and scheduled principal to final maturity; optionally the net-cash-accrual CFADS series for the V6 reconciliation; remaining project life; remaining loan life; principal outstanding on rated debt plus pari passu and senior debt; unencumbered DSRA and other unencumbered cash; effective contracted interest rate on the rated debt with its as-of date. |
| C — Financial | Project cash flow from operations; Total Debt itemised by instrument with its equity-treatment classification (Section 9.3); Tangible Net Worth build; total DSRA balance and the encumbered portion; average monthly debt service. |
| D — Structural | Presence or absence of: trustee-administered waterfall; each of the four security elements; distribution lock-up with its DSCR threshold; each of the four covenants; reporting covenant; hedging policy or fixed-rate confirmation; insurance including business-interruption cover. |
| Notching | For each of up to four offtakers (plus an aggregated "Other" line): name, type, contracted revenue share, and current published rating or grade with agency, edition and date. Bullet share and each of the four mitigants discretely. Project state, EPC structure, contractor standing, contingency share, and execution complexity per Section 7.3. |

**CFADS components are deliberately not collected.** Section 9.1 defines CFADS by its primary construction, and Section 10.2 above requires only the resulting annual figure. This is a scope decision, not an omission: Template 2 captures the *outputs* of the project's financial model rather than reproducing the model (Section 0.3), and collecting revenue, cash opex, maintenance, working-capital movement and cash taxes per period for thirty years would make the template a cash-flow model. The consequence is disclosed rather than concealed — **the engine cannot verify that an entered CFADS figure was built to the Section 9.1 definition.** The controls against that are the Section 9.5 attestation, the optional V6 reconciliation against the net-cash-accrual route, and the editable validation screen. This limitation is recorded at Section 11.

*Resolved in v3.0 (QA finding M9). v2.0's Section 10.2 required "the CFADS build (revenue, cash opex, maintenance/MMRA, ΔWC, cash taxes)" while Template 2 collected only the annual total, so a stated required input was not collected anywhere and Section 9.1's governing construction was unverifiable without this being acknowledged. Either the template had to expand or the requirement had to be withdrawn and the gap disclosed. The requirement is withdrawn and the gap disclosed.*

## 10.2.1 Field-level requirements

Every input above resolves to a named field in **Appendix B**, with its type, unit, criticality and governing template. Appendix B is normative: the JSON schema, both templates, the extraction prompt and the test-fixture input sheets use those names and no others.

**Fixtures are held separately from the blank template.** The eight reference projects and the worked Blocks B and C example live in **Credit Rating Simulator Test Fixtures v3.0**, not in Key Input Template 2. The separation is deliberate: Key Input Template 2 is the form a preparer fills in for a live assessment, and it must contain **no invented figure of any kind**. A fixture value sitting in the same workbook — or in the same searchable knowledge base — can be retrieved and read as a fact about the project under assessment. This is the same hazard the Tier-3 rule guards against in the reference corpus, where rating rationales are a permitted source of style and never of numbers (Section 12).

## 10.3 Canonical tier vocabularies

*v1.0 used six different tier vocabularies across its tables, each of which becomes a separate enumeration in the data model. v2.0 harmonised them to five. v3.0 moves the definitive list to **Appendix A**, which covers both the output tier vocabularies and — new in v3.0 — every **input** enumeration with a stable code.*

**Appendix A is the single normative enumeration list for this project.** The engine must implement exactly those enumerations and no others, and must match on **code**, never on display text.

Output tier vocabularies: `TIER_5`, `LIQUIDITY_5`, `PRESENCE_4`, `COUNTERPARTY_4`, `BAND_8`, `CONFIDENCE_4`, `VALIDATION_4` (Appendix A §14.2).

*v2.0's `TIER_4` is withdrawn. It was declared as applying to Sections 3.3.1 and 3.4, but neither of those tables carries a tier label — both are now scored from explicit derivation tables — so the enumeration had no site of use and would have become a dead type in the schema.*

Sections 3.1, 3.2, 3.3.1, 3.3.2, 3.5 and 3.6 are scored from enumerated input selections or derivation tables mapped directly to points, and do not carry an output tier label.

# 11. Limitations, Assumptions, and Disclaimers

- This is an indicative, academic decision-support output, not a SEBI-registered credit rating, and does not represent the opinion of any credit rating agency named in this document.

- **DSCR basis mismatch.** The Set W anchors at Section 4.1 derive from published guidance stated on the source agency’s own rating case, applied here to a P90 basis adopted from a different agency’s criteria. This is a deliberate conservatism, disclosed at Section 4.0, not an equivalence. The source’s separate one-year P99 break-even test for investment grade is not adopted.

- **Sets S and H are Developer calibrations**, not published thresholds. They are the highest-priority items for revision after back-test.

- PLCR and LLCR thresholds (Sections 4.3–4.4) are Developer calibrations, not grounded in a published agency table, and are provisional pending back-test validation.

- Further Developer calibrations, all provisional: the 25% offtaker-dominance threshold (7.1); the bullet-share definitions (7.2); the 5% contingency threshold (7.3); the reinvestment ratio bands (3.4); the operator and sponsor MW and year thresholds (3.6); the N = 3.0-point confidence window (9.8.3).

- Accuracy for hybrid and storage-linked structures specifically is untested. See the companion **Credit Rating Simulator — Criteria Extension**, cited by title.

- **CFADS composition is not verified by the engine.** Only the annual CFADS figure is collected, not its components, so the engine cannot confirm that an entered figure was built to the Section 9.1 definition. The controls are the Section 9.5 attestation, the optional V6 reconciliation, and the validation screen. See Section 10.2.

- **Section 3.3.2 carries a technology asymmetry.** A wind-only project scores the full sourcing-compliance point by definition; a solar or hybrid project can lose up to 1 point. The asymmetry is real and deliberate — no binding ALMM-equivalent sourcing mandate applies to wind — but it means the 115-point scale is not perfectly technology-neutral.

- **The back-test validates direction, not calibration.** A back-test on the 8 to 10 projects available cannot recalibrate the nine Developer calibrations listed above; nine parameters cannot be fitted to ten observations without overfitting. Those calibrations remain provisional after the back-test, and the back-test should be reported as a directional accuracy check — how often the framework lands in the right region, and whether its errors are systematic in one direction — not as a validation of any specific threshold.

- The engine assumes accurate user inputs and extracted financial data; an editable validation screen sits between extraction and scoring, and every field traces to Section 10.2.

- The Offtaker/Counterparty mechanic depends on the currency of the published C&I rating or DISCOM Integrated Rating; a stale rating is flagged, not silently applied (Section 9.9).

- The ALMM parameters at Section 3.3.3 were current as at 30 July 2026 and require re-verification before each engine release.

- Requires professional review before being relied upon for any real transaction, investment, or lending decision.

# 12. Reference Mapping Table

**Corpus integrity.** The source documents named in this table are identified by title, not by filename. Filenames in the reference folder are not stable identifiers: two collided on case alone until remediated, one methodology was present twice under different names, and two carried malformed dates. The authoritative index is the **Reference Corpus Manifest v3.0**, which keys each document by content hash and records its tier, category, agency, publication date, container format and page count. Grounding lookups must resolve through the manifest rather than by matching filenames.

**The corpus is uniformly PDF.** All 41 files are genuine PDFs carrying a text layer, and every page of every document yields extractable text. Ingestion reads them with an ordinary PDF library; no container dispatch is required.

*This is a change from earlier in v3.0, and it simplified rather than complicated the contract. As originally assembled, 37 of the 41 files were ZIP archives of per-page images and OCR text wearing a `.pdf` extension, and only 4 were genuine PDFs — so the contract had to dispatch on a `container` column and could assume neither format. On re-download the archives were served as real PDFs. Verification confirmed a text layer on 660 of 661 pages across all 41 documents, so nothing was lost and the mixed-format handling is no longer needed. The `container` column is retained in the manifest because it costs nothing and would catch a future divergence; it currently reads `PDF` on every row.*

**Two sources named in this table are not in the corpus** and cannot be resolved through the manifest: the Ministry of Power / Power Finance Corporation Integrated Rating and Ranking of Power Distribution Utilities (cited at Section 7.1), and the MNRE notifications and office memoranda behind Section 3.3.3. Both are live reference data rather than methodology documents, they are re-verified on the cadence at Section 0.1 rather than ingested once, and the rows below mark them **external**. The grounding step must not attempt a manifest lookup for either (QA finding m13).

*Every factor scored in Sections 3–7 now has a row, and every row states whether it rests on a published methodology or on a Developer calibration. Where v2.0 changed a threshold away from the published figure that v1.0 cited, the attribution has been withdrawn rather than retained over a number the source does not support.*

| Core factor | Basis | Primary source document(s) or calibration note |
| --- | --- | --- |
| Overall architecture (blocks, notching, cap concept) | Published | Moody’s General Project Finance Methodology, June 2021 (structural reference only; publicly available, superseded methodology; not branded as source) |
| 3.1.1 Competitive and essentiality position | Published | CARE Methodology — Solar Power Projects; CARE Ratings Methodology — Wind Power Projects |
| 3.1.2 Permitting completeness | Published | CARE Methodology — Solar / Wind Power Projects; ICRA Power (Solar & Wind) Rating Methodology |
| 3.1.3 Regulatory and tariff-policy stability (RPO, tariff) | Published | CARE Methodology — Solar / Wind Power Projects; ICRA Power (Solar & Wind) Rating Methodology |
| 3.2.1 Contracted revenue share | Published | Fitch Ratings Renewable Energy Rating Criteria (contracted vs merchant revenue treatment) |
| 3.2.2 Price and volume risk within contracted revenue | Published | Fitch Ratings Global Infrastructure & Project Finance Criteria (Revenue Risk); India Ratings Criteria for Infrastructure and Project Finance |
| 3.3.1 Technology maturity and plant complexity | Published | ICRA Power (Solar & Wind) Rating Methodology; CARE Methodology — Solar / Wind Power Projects |
| 3.3.2 Regulatory sourcing compliance (ALMM) | Published | ICRA Power (Solar & Wind) Rating Methodology, July 2025 |
| 3.3.3 ALMM parameter values | Published, dated — **external, not in corpus** | MNRE notifications and office memoranda as recorded at Section 3.3.3, all as at 30 July 2026; re-verification mandatory |
| 3.4 Capital reinvestment bands | **Developer calibration** | No numeric reinvestment threshold published in the reviewed corpus. Provisional. |
| 3.5 Generation performance evidence | Published | Crisil Ratings Criteria for Infrastructure Sectors (P90 basis); ICRA Project Finance Rating Methodology (independent resource assessment) |
| 3.6 Operator and sponsor quality — qualitative construct | Published | ICRA Project Finance Rating Methodology; India Ratings Criteria for Infrastructure and Project Finance |
| 3.6 Operator and sponsor MW / year thresholds | **Developer calibration** | Provisional. |
| 4.0 P90 DSCR basis | Published | Crisil Ratings Criteria for Infrastructure Sectors (“Why use P90 PLF levels to calculate DSCR”) |
| 4.1 / 4.2 Set W — wind DSCR thresholds | Published | Fitch Ratings Renewable Energy Rating Criteria (Indicative Coverage Ratios Guidance — Wind Projects) |
| 4.1 / 4.2 Sets S and H — solar and hybrid DSCR thresholds | **Developer calibration** | Positioned below Set W on resource-variability grounds. Provisional; first priority for back-test revision. |
| 4.0 Merchant adjustment (+0.20x above 25% merchant exposure) | Published (direction and magnitude) | Fitch Ratings Renewable Energy Rating Criteria (fully-merchant vs fully-contracted coverage guidance) |
| 4.3 / 4.4 PLCR and LLCR definitions | Published | Fitch Ratings Global Infrastructure & Project Finance Criteria (Appendix B); India Ratings Criteria for Infrastructure and Project Finance |
| 4.3 / 4.4 PLCR and LLCR tier thresholds | **Developer calibration** | No numeric PLCR/LLCR tier table published in the reviewed corpus. Provisional. |
| 5.1 Project CFO / Adjusted Debt thresholds | **Developer calibration** | Standard Indian project-finance convention. Provisional. |
| 5.2 Gearing definition and thresholds | Published (construct) | Brickworks Approach to Financial Ratios; CARE Financial Ratios — Non-Financial Sector. Thresholds are Developer calibration. |
| 5.3 Liquidity classification | Published (four-tier), extended | CARE Liquidity Analysis of Non-Financial Sector Entities. Five-tier extension is Developer calibration, disclosed at Section 5.3. |
| 6.1–6.3 Structural protections checklist | Published | Fitch Ratings Global Infrastructure & Project Finance Criteria (Debt Structure key rating driver) |
| 7.1 Offtaker crosswalk — C&I rating input and modifier placement | Published | SEBI-standardised national long-term rating scale (AAA to D, modifiers on AA to C), as applied by CRISIL / ICRA / CARE / India Ratings |
| 7.1 Offtaker crosswalk — DISCOM input | Published — **external, not in corpus** | Integrated Rating & Ranking of Power Distribution Utilities, Ministry of Power, published by Power Finance Corporation Limited, 14th edition (FY25). Seven grades: A+, A, B, B−, C, C−, D — all seven enumerated at Section 7.1. |
| 7.1 Offtaker-dependence threshold (25%) and worst-tier rule | **Developer calibration** | v1.0 cited Moody’s General Project Finance Methodology (Off-taker Risk, Appendix C) for a 10% threshold. That threshold fires on effectively every project in the reference corpus, rendering the blended-tier logic unreachable. The threshold has been raised on the Developer’s own judgment and **the attribution is withdrawn**. Provisional. |
| 7.1 Tier values for blending (4/3/2/1) | **Developer calibration** | Provisional. |
| 7.2 Refinancing risk notch — construct | Published | Crisil Ratings Criteria for Infrastructure Sectors (Assessment of refinancing risk in power projects) |
| 7.2 Bullet-share definitions and mitigant list | **Developer calibration** | Provisional. |
| 7.3 Construction and ramp-up risk notch — construct | Published | ICRA Power (Solar & Wind) Rating Methodology; ICRA Project Finance Rating Methodology; Fitch Ratings Global Infrastructure & Project Finance Criteria (Completion Risk) |
| 7.3 12-month ramp-up window and 5% contingency threshold | **Developer calibration** | Provisional. |
| 8.2 Band table and investment-grade distinction | Published (convention) | Standard Indian long-term rating-scale convention (CRISIL / ICRA / CARE / India Ratings), and the Execution Manual’s disclaimer requirement. Band widths are Developer calibration. |
| 8.3 Cap-the-band mechanic and coverage floor | **Developer calibration** | Cap concept from the Moody’s structural reference; the cap-the-band resolution, the coverage floor, and their interaction are the Developer’s specification. Provisional. |
| 9.1 CFADS definition | Published | Fitch Ratings Global Infrastructure & Project Finance Criteria (Appendix B) |
| 9.3 Debt, Adjusted Debt and TNW definitions; equity-treatment test | Published (construct) | Brickworks Approach to Financial Ratios; CARE Financial Ratios — Non-Financial Sector; CARE Criteria for Consolidation and Combined Approach. Instrument-level treatment is Developer specification. |
| 9.6 Precision and boundary convention | **Developer calibration** | Engine-determinism requirement. Not a methodology question. |
| 9.8 Null scoring and confidence definition | **Developer calibration** | Engine-determinism requirement. N = 3.0 points is provisional. |

# 13. Change Log

## 13.0 v2.0 to v3.0 — pre-build QA remediation

*v3.0 closes the findings of the final pre-build QA review. v2.0 was assessed **Requires Further Revision Before Build** on seven blocking defects; all seven are closed below, together with sixteen major and nineteen minor findings. Section numbering is unchanged from v2.0 except for two additions — Section 10.1.1 (pipeline order) and Appendices A and B at Sections 14 and 15 — so no downstream reference built against v2.0 numbering breaks.*

### 13.0.1 Blocking defects resolved

| Ref | Defect | Resolution | Sections |
| --- | --- | --- | --- |
| B1 | Three artefacts declared mandatory did not exist: the corpus manifest, the remediation script, the ingestion specification. The Extension cross-reference was unverified. | All three artefacts now issued at v3.0. Extension cited **by title only**, resolution (b) of v2.0's own two options. Seven Extension-scope corpus documents identified in Section 12. | preamble, 0.1, 0.4, 11, 12 |
| B2 | Corpus renames documented as applied on 30 July 2026 had not been applied; two filenames still collided on case alone. | Renames applied and verified: 41 files, 0 case-insensitive collisions, 41 distinct payload hashes, every hash matching the manifest. | 12 |
| B3 | The Test Projects sheet did not carry the input set the unit tests are built against. | Full input sets added for all reference projects, keyed on the Appendix B field names. | 15, Template 2 |
| B4 | Template 2 shipped with defaults that inverted a criteria rule — CCDs pre-classified as Equity against Section 9.3. | `TREATMENT_DEBT` is now the stated default for every instrument including sponsor loans and CCDs; a blank treatment is a null, not a default; V14 blocks an unclassified instrument. All pre-set input values cleared. | 9.3, 10.1, 14.1, Template 2 |
| B5 | Section 9.5's derivation route claimed arithmetic enforcement that Template 2 did not implement. | Route (a) **withdrawn**. Attestation is the only route; all four attestation fields are critical. | 9.5, 9.8.1 |
| B6 | Null resolution and validation gave two lawful outcomes for the same project. | New Section 10.1.1 states the five-stage pipeline order; `Not Evaluated` defined as the fourth validation outcome and excluded from the confidence penalty. | 10.1, 10.1.1, 14.2 |
| B7 | Percentages were fractions in this document and Template 2, and out of 100 in Template 1 and the Test Projects sheet, with no stated conversion. | Single normative line at Section 9.6; every percentage field carries unit `frac` in Appendix B; both templates and all reference projects restated. | 9.6, 15, Templates 1 and 2 |

### 13.0.2 Major findings resolved

| Ref | Resolution | Sections |
| --- | --- | --- |
| M1 | Coverage floor stated as **absolute at 1.00x**, never shifted by the merchant adjustment, which is confined to the five tier thresholds. Consequence stated; V8a warns on it. | 4.0, 4.1, 8.3, 10.1 |
| M2 | Band edges defined as the seven interior thresholds; 0 and 115 expressly excluded from *d*. | 9.8.3 |
| M3 | "Binding" restored to the confidence rule wherever the Execution Manual had dropped it. | 9.8.3, Manual 1.3 and 4.4 |
| M4 | Section 3.5 restated as a performance limb and an evidence limb with the lower governing; the "< 1 full operating year" limb deleted. | 3.5 |
| M5 | "Established performance history" deleted; row 1 turns on the 12-month test alone. | 7.3 |
| M6 | `NOT_APPLICABLE_FIXED_RATE` scored as present at Section 7.2, mirroring Section 6.3. | 7.2, 14.1 |
| M7 | The aggregated offtaker line is a single counterparty for the dominance test and the blend; the user-derived tier is declared as an exception. | 7.1 |
| M8 | Duplicated fields reduced to a governing source in Appendix B; merchant exposure derived rather than entered; V13 added. | 10.1, 15 |
| M9 | CFADS component collection withdrawn and the limitation disclosed; V6 restated as period by period. | 10.1, 10.2, 11 |
| M10 | Appendix A issued: every enumeration with a stable code, matched on code and never on display text. | 14 |
| M11 | `contracted_share_75pc_tenor` and `sponsor_support_this_project` added; Section 3.2.1's three distinct quantities separated. | 3.2.1, 3.6, 15 |
| M12 | Actual-generation evidence split into three typed annual fields plus a period field. | 3.5, 15 |
| M13 | Nil or negative tangible net worth **scores 0** with a V9 Warn, rather than returning blank and presenting as a null. | 5.2, 10.1, Template 2 |
| M14 | The vacuous Total Debt reconciliation replaced; V14 catches an instrument with an amount and no treatment. | 10.1, Template 2 |
| M15 | Reference projects extended from three to seven, covering the binding cap, the ramp-up state, the two unexercised refinancing rows, multi-offtaker logic, the blend, nulls, and Block failures. | Template 2 |
| M16 | Version breach closed: all documents issued at **v3.0** on a single date, and the `Data Input` sheet added to the extraction contract. | 0.1, throughout |

### 13.0.3 Minor findings resolved

| Ref | Resolution |
| --- | --- |
| m1 | File counts stated as 42 as assembled / 41 after quarantine; the methodology count restated in the past tense. |
| m2 | Stale row and cell references corrected; named ranges introduced in Template 2 so row insertion cannot break them again. |
| m3 | Poor/Unrated row restated as C+, C, C−, D or unrated; "CCC+" removed as not being a symbol on the Indian scale. |
| m4 | Methodology count corrected to twenty in the Execution Manual. |
| m5 | Two meanings of "notch" disambiguated at Section 7; the Execution Manual's back-test restated in rating categories. |
| m6 | Derivation tables added for Sections 3.3.1 and 3.3.2; `TIER_4` withdrawn as having no site of use. |
| m7 | Section 10.1 split into input validations (V) and engine assertions (A). |
| m8 | Other unencumbered cash expressly excluded from the liquidity numerator and included in the PLCR/LLCR numerator. |
| m9 | Calculated cells protected; legacy dropdowns removed from formula cells; named ranges added. |
| m10 | Template 1 enumerated fields restated against Appendix A codes; Template 2 critical fields marked. |
| m11 | Companion documents cited by title and version, never by filename. |
| m12 | Documents issued with extensions matching their actual format. |
| m13 | Two external sources marked **external, not in corpus**; the seven Extension-scope corpus documents identified. |
| m14 | Section 3.3.2's technology asymmetry disclosed at Section 11. |
| m15 | The self-certified share-summation field deleted; V3 performs the test arithmetically. |
| m16 | Back-test reframed as directional validation; the limits of fitting nine calibrations stated at Section 11. |
| m17 | `execution_complexity` added to Section 7.3 row 3's qualifying conditions. |
| m18 | Section 3.6 limb conditions made mutually exclusive and exhaustive. |
| m19 | `calculation_date` marked critical and added to Section 9.8.1. |

### 13.0.4 Post-issue sanity check, 30 July 2026 (within v3.0)

*A structural self-check was run over this document after issue: block and sub-factor arithmetic, cross-reference resolution, enumeration and field-dictionary completeness, and a search for undeclared double counting. Arithmetic and cross-references passed unchanged — sub-factors sum to 35 / 35 / 25 / 20 and 115, and all 62 cited sections resolve to real headings. Four defects were found and are corrected within v3.0. None alters a score.*

| # | Defect | Correction |
| --- | --- | --- |
| S1 | The **non-overlap map contradicted itself**: it opened "scored in exactly one place, and nowhere else" and its own final row then named two places. Two further overlaps — liquidity, and hedging — were not listed at all. | The map now distinguishes single placement from **declared exceptions**, lists all three overlaps, and gives the reasoning for each. An unstated overlap is a defect; a stated one is a design decision. |
| S2 | Section 7's blanket claim that "a risk already scored inside Blocks A–D is not also notched here" was **false for hedging**, which is assessed at Section 6.3 as the existence of a policy and at Section 7.2 as 75% coverage to maturity. | The claim is qualified by reference to the map, and the exception is stated where it arises. |
| S3 | **`ATTESTED_P90` was not declared in Appendix A**, although Section 9.5 requires the engine to match on it and Appendix A claims to be the complete normative list. | Declared as `P90_BASIS_1`, a deliberately single-member enumeration, with the reason recorded. |
| S4 | **`minimum_dscr` and `average_dscr` were absent from Appendix B**, although Section 9.8.1 names a directly entered Minimum DSCR as an alternative critical input and Section 10.1.1's worked example registered `avg_dscr` in the Null Register. The alternative route could not be represented in the JSON schema at all, and the worked example named a field nothing defined. | Both fields added, with criticality and a note governing how the schedule route and the direct-entry route interact. `avg_dscr` is recorded as an informal abbreviation, not a field name. |

*S4 is the same class as QA finding M11 — a criteria rule depending on a field no template collects — and would have surfaced on Day 1, when the JSON schema is written from Appendix B.*

### 13.0.5 Findings surfaced during implementation, 31 July 2026 (within v3.0)

*Section 13.0.4 records defects found by reading this document. This section records defects found by **building from it** — which is a different test, and a harder one to pass. A specification can be internally consistent, arithmetically sound and fully cross-referenced, and still leave an implementer with a choice the author never realised they were delegating.*

| # | Gap | Resolution |
| --- | --- | --- |
| S5 | **Section 10.1.1 Stage 3 was silent on whether a Block halts evaluation of the remaining rules.** Both readings were defensible, so the implementer had to choose — and chose to halt on the first Block, which returns an incomplete validation report. | **All rules are evaluated, then the pipeline stops without scoring.** The rules are mutually independent, so a Block in one says nothing about the others, and a preparer shown one failure at a time must correct and resubmit once per failure. TP-8's expected output is restated as the full thirteen-rule report. |

# 13.1 Change Log — v1.0 to v2.0


## 13.1.1 Blocking defects resolved (v1.0 to v2.0)

| Ref | Defect | Resolution | Sections changed |
| --- | --- | --- | --- |
| BL-1 | Seven reachable scores fell into no band | Band table restated as half-open intervals, exhaustive over [0, 115] | 8.2 |
| BL-2 | No rounding or boundary convention anywhere | All quantitative tiers restated as single-sided thresholds; precision and rounding stated per input class | 9.6, and every table in 3–7 |
| BL-3 | Missing-input handling and “confidence” undefined | Critical/non-critical null rules, Null Register, and a numeric confidence definition with N = 3.0 points | 9.8 |
| BL-4 | §9.2 and §9.5 gave opposite instructions on the same DSRA | DSRA permitted in the PLCR/LLCR numerators as a stated exception; prohibition narrowed to CFADS and DSCR | 9.2, 9.7 |
| BL-5 | Non-double-counting rule violated twice | Offtaker credit stripped from Block A; Operating Track Record re-anchored on evidence quality and renamed | 2, 3.2, 3.5, 9.7 |
| BL-6 | 10% offtaker-dependence rule fired on every project | Dominance threshold raised to 25%; worst-tier rule stated; tier values assigned for blending; Section 12 attribution withdrawn | 7.1, 12 |
| BL-7 | Hard cap had no defined interaction with the band table | Cap-the-band specified; Results screen display requirements stated | 8.1, 8.3, 8.4 |
| BL-8 | 25 of 115 points not deterministically scoreable | Sections 3.1 and 3.2 decomposed into enumerated sub-dimensions; numeric anchors added to 3.5 and 3.6 | 3.1, 3.2, 3.5, 3.6 |
| BL-9 | Wind DSCR thresholds applied to solar on a false premise | Three technology-specific threshold sets; merchant adjustment; basis mismatch disclosed; the “only explicit correspondence” claim corrected | 4.0, 4.1, 4.2, 11 |

## 13.1.2 Major findings resolved (v1.0 to v2.0)

| Ref | Resolution | Sections |
| --- | --- | --- |
| MAJ-1 | Gearing defined once, as Total Debt / Tangible Net Worth; Section 5.2 retitled and its Debt:Equity labels demoted to orientation only | 5.2, 9.2, 9.3 |
| MAJ-2 | Total Debt, Adjusted Debt and Tangible Net Worth defined at instrument level, with an equity-treatment test for sponsor loans and CCDs | 9.3 |
| MAJ-3 | CFADS primary construction made governing; interest exclusion and cash-tax convention stated; net-cash-accrual route permitted with a 2% reconciliation tolerance | 9.1, 10.1 (V6) |
| MAJ-4 | DSCR measurement period, stub-period, construction-year and pre-COD treatment specified; Average DSCR defined as the arithmetic mean | 9.2.1, 4.2 |
| MAJ-5 | P90 derivation-or-attestation made mandatory before Block B scores | 9.5, 9.8.1 |
| MAJ-6 | Twelve internal-consistency validation rules added, each classified Block or Warn | 10.1 |
| MAJ-7 | Coverage floor added: Minimum DSCR < 1.00x caps the band at BB | 4.1, 8.3 |
| MAJ-8 | Section 5.3 restated as a disclosed five-tier extension of the published four-tier convention | 5.3, 10.3 |
| MAJ-9, MAJ-10, MAJ-17 | Technology split into independent maturity/complexity and sourcing-compliance dimensions; balance-of-plant and grid complexity given its own input | 3.3.1, 3.3.2 |
| MAJ-11 | Refinancing table completed to all bullet-share × mitigant combinations, with numeric definitions of partial and large | 7.2 |
| MAJ-12 | Ramp-up state added to the construction table | 7.3 |
| MAJ-13 | C&I crosswalk enumerated with full modifiers; BBB− placed in Adequate and BB+ in Weak explicitly | 7.1 |
| MAJ-14 | Weak and Poor/Unrated differentiated: −2 notches and −3 notches respectively | 7.1 |
| MAJ-15 | Tier values assigned; blending formula, rounding rule and dominance test stated; Template 1 extended to four offtakers plus an aggregated line | 7.1, 10.2 |
| MAJ-16 | Partial encumbrance: exclude the encumbered portion and score the remainder; Template 2 collects the encumbered amount separately | 5.3 |
| MAJ-18 to MAJ-22 | Block D tiers restated as counts; Section 3.4 given numeric anchors; tier vocabularies harmonised into five canonical enumerations | 6.1–6.3, 3.4, 10.3 |
| MAJ-23 | Section 12 completed — every scored factor has a row, and every row declares published basis or Developer calibration | 12 |
| MAJ-24 | Template 2’s Sample sheet rebuilt to be internally reproducible; three hand-calculated end-to-end test projects added | Template 2 |
| MAJ-25 | Document control block added (version, date, owner, review cadence, change log); ALMM converted from prose to a dated, configurable parameter table with a mandatory verification rule | 0.1, 3.3.3 |

## 13.1.3 Minor findings resolved (v1.0 to v2.0)

| Ref | Resolution | Sections |
| --- | --- | --- |
| MIN-1 | Six tier vocabularies harmonised to five canonical enumerations | 10.3 |
| MIN-2 | All cross-references swept and corrected; the non-double-counting rule is now Section 9.7 and every reference to it updated across all four documents | throughout; see 13.4 |
| MIN-3 | Formatting artifacts removed — stray ampersand entities, trailing whitespace, inconsistent heading capitalisation, dangling page markers | throughout |
| MIN-4 | Section 7’s self-contradictory general definition of notching trimmed; the framework is stated as downward-only from the outset | 7 |
| MIN-5 | AAA parenthetical resolved: the engine does not block AAA after notching, and the only band-limiting mechanisms are the Section 8.3 caps | 8.2 |
| MIN-6 | Vestigial third clause of the non-double-counting rule removed | 9.7 |
| MIN-7 | Pari passu and senior debt now stated in both the PLCR and the LLCR denominators | 9.2 |
| MIN-8 | Section 0 disclaimer softened to match what Section 12 actually does — a transparency record of informing methodologies, not a claim of no attribution | preamble |
| MIN-9 | Extension-document dependency flagged explicitly, with two permitted resolutions before handover | 0.4, 11 |
| MIN-10 | **Now closed in full.** All four elements resolved. (a) Container format: every file carrying a .pdf extension is in fact a ZIP of per-page JPEGs plus per-page OCR text — confirmed across all 42 files as assembled (41 after quarantine) — and the ingestion contract is now specified rather than assumed. (b) The two Fitch files are payload-identical and one has been quarantined; this is why the methodology count in the preamble falls from twenty-one to twenty. (c) The two ReNew files are **not** duplicates — they are different rationales from different agencies whose names collide only in capitalisation — so both have been renamed rather than either deleted. (d) Template 2’s hard-ranged MIN and AVERAGE formulas were fixed in the first pass. A machine-readable corpus manifest and an idempotent remediation script now accompany the document set. | 12 |

## 13.1.4 Section renumbering map — Section 9 (v1.0 to v2.0)

Downstream references to Section 9 must be updated. The engine, both templates, and the Execution Manual have been swept; any external note built against v1.0 should use this map.

| v1.0 | v2.0 | Topic |
| --- | --- | --- |
| 9.1 | 9.1 | CFADS |
| 9.2 | 9.2 | Coverage ratio formulas (9.2.1 added — measurement period) |
| 9.3 | 9.4 | Discount rate for PLCR/LLCR NPV |
| 9.4 | 9.5 | P90 generation basis |
| 9.5 | **9.7** | Non-double-counting rule |
| 9.6 | 9.9 | Offtaker/counterparty rating sources |
| — | 9.3 | **New** — Debt, Adjusted Debt and Tangible Net Worth |
| — | 9.6 | **New** — Precision, rounding and boundary convention |
| — | 9.8 | **New** — Missing inputs, null scoring and confidence |

*Note for implementers: v1.0’s own headings carried bolded digits at 9.4, 9.5 and 9.6, and Template 2 cited** **“**Section 9.4**”** **for the liquidity non-double-counting rule, which was in fact Section 9.5. That was an unpropagated renumbering from the late insertion of Section 9.3. Both references are corrected in v2.0, and the map above exists so the same failure does not recur.*

# 14. Appendix A — Canonical Enumerations (normative)

*New in v3.0. Resolves QA findings M10, M6 and m6. In v2.0 the same enumerated option appeared with different wording in this document and in Key Input Template 1 — Section 3.1.1's first option ran to 34 words here and 12 words there — while Execution Manual Activity 1.2 made Template 1's strings authoritative for the JSON schema and this document simultaneously claimed to be the single source of truth. There was no canonical list anywhere. This appendix is that list.*

**Rule of construction.** Every enumerated input in this framework is identified by a **stable code**. The code is what the JSON schema stores, what the engine matches on, and what Template 1 and Template 2 record. The display string is presentational and may be reworded without a version bump; **the code may not**. No component may match on display text.

**Rule of completeness.** The engine must implement exactly the enumerations below and no others. An input that does not resolve to a listed code is a null (Section 9.8), not a coerced nearest match.

## 14.1 Scoring enumerations

### TECH_3 — Technology type (Template 1 §A.1) → selects the Section 4 threshold set

| Code | Display string | Threshold set |
| --- | --- | --- |
| `TECH_SOLAR` | Solar PV | Set S |
| `TECH_WIND` | Wind | Set W |
| `TECH_HYBRID` | Solar + Wind Hybrid | Set H |

### STATUS_2 — Project status (Template 1 §A.1)

| Code | Display string |
| --- | --- |
| `STATUS_OPERATING` | Operating |
| `STATUS_PRECOD` | Under Construction (Pre-COD) |

### COMP_POS_5 — Competitive and essentiality position (§3.1.1)

| Code | Display string | Points |
| --- | --- | --- |
| `COMP_POS_5` | No economically viable substitute for the offtaker for this volume; tariff at or below the comparable auction benchmark | 4 |
| `COMP_POS_4` | Substitutes exist but switching is costly or slow; tariff at or below the comparable auction benchmark | 3 |
| `COMP_POS_3` | Substitutes readily available; tariff within 10% above the comparable auction benchmark | 2 |
| `COMP_POS_2` | Substitutes readily available; tariff more than 10% above the comparable auction benchmark | 1 |
| `COMP_POS_1` | Offtake position expected to erode within the remaining debt tenor | 0 |

### PERMIT_3 — Individual permitting status (§3.1.2, three instances)

| Code | Display string |
| --- | --- |
| `PERMIT_COMPLETE` | Complete |
| `PERMIT_IN_PROGRESS` | In Progress |
| `PERMIT_NOT_STARTED` | Not Started |

### DISPUTE_5 — Live permitting dispute or lapsed consent (§3.1.2)

| Code | Display string |
| --- | --- |
| `DISPUTE_NONE` | None |
| `DISPUTE_LAND` | Land |
| `DISPUTE_TRANSMISSION` | Transmission connectivity |
| `DISPUTE_STATUTORY` | Statutory clearances |
| `DISPUTE_MULTIPLE` | More than one — specify in notes |

### REG_STAB_5 — Regulatory and tariff-policy stability (§3.1.3)

| Code | Display string | Points |
| --- | --- | --- |
| `REG_STAB_5` | Stable — no renegotiation attempt, retrospective charge or contested tariff order in the offtake state in five years, and the applicable RPO trajectory is notified | 4 |
| `REG_STAB_4` | Stable — a routine tariff or true-up order is pending, with no adverse precedent in the state | 3 |
| `REG_STAB_3` | Some uncertainty — a pending RPO revision or tariff order is material to project revenue | 2 |
| `REG_STAB_2` | Unstable — a live PPA renegotiation attempt or contested tariff order affects this project or its offtaker | 1 |
| `REG_STAB_1` | Adverse — a retrospective charge has been levied, or a renegotiation affecting this project is unresolved | 0 |

### PRICE_VOL_5 — Price and volume risk within the contracted portion (§3.2.2)

| Code | Display string | Points |
| --- | --- | --- |
| `PRICE_VOL_5` | Fixed or pre-defined escalating tariff, with a take-or-pay or deemed-generation provision **and** a defined termination payment | 5 |
| `PRICE_VOL_4` | Fixed or pre-defined escalating tariff, with a take-or-pay/deemed-generation provision **or** a defined termination payment, but not both | 3.5 |
| `PRICE_VOL_3` | Fixed or pre-defined escalating tariff, with neither a take-or-pay/deemed-generation provision nor a defined termination payment | 2 |
| `PRICE_VOL_2` | Tariff partly indexed to a merchant or market reference | 1 |
| `PRICE_VOL_1` | Tariff wholly merchant or market-linked | 0 |

### TECH_MAT_3 — Generating technology maturity (§3.3.1, dimension 1)

| Code | Display string |
| --- | --- |
| `TECH_MAT_STANDARD` | Standard, widely deployed — conventional crystalline-silicon PV, or an onshore WTG platform with 3+ years of utility-scale Indian operating history |
| `TECH_MAT_NEWER` | Newer or less-established technology or configuration, under 3 years of utility-scale Indian operating history |
| `TECH_MAT_UNTESTED` | Largely untested at this scale or in this application |

### BOP_3 — Balance-of-plant and grid-integration complexity (§3.3.1, dimension 2)

| Code | Display string |
| --- | --- |
| `BOP_CONVENTIONAL` | Conventional — dedicated substation, evacuation line under 25 km, no shared infrastructure, no storage coupling |
| `BOP_MODERATE` | Moderately complex — shared pooling substation, or evacuation line over 25 km, or hybrid dispatch controller, or storage-coupled dispatch obligation |
| `BOP_HIGH` | High complexity — more than one of the above, or a first-of-kind configuration at this site |

### ALMM_5 — Regulatory sourcing compliance (§3.3.2)

| Code | Display string | Points |
| --- | --- | --- |
| `ALMM_COMPLIANT` | Fully compliant with the applicable ALMM requirement | 1 |
| `ALMM_NOT_APPLICABLE` | Not Applicable — wind-only project | 1 |
| `ALMM_EXEMPT_OPEN` | Relying on a documented exemption or approved case-by-case route, within its window | 0.5 |
| `ALMM_NON_COMPLIANT` | Non-compliant with a currently binding requirement | 0 |
| `ALMM_EXEMPT_CLOSED` | Exemption window closed without a confirmed compliant sourcing plan | 0 |

### FUND_SRC_5 — Reinvestment funding source (§3.4)

| Code | Display string | Counts as internally fundable? |
| --- | --- | --- |
| `FUND_OCF` | Operating cash flow | Yes |
| `FUND_MMRA` | Funded major-maintenance reserve account (MMRA) | Yes |
| `FUND_INCREMENTAL_DEBT` | Incremental debt | No |
| `FUND_SPONSOR` | Sponsor support | No |
| `FUND_NOT_IDENTIFIED` | Not identified | No |

### YN_2 and YNNA_3 — Boolean and boolean-with-exemption

| Enumeration | Codes | Used at |
| --- | --- | --- |
| `YN_2` | `YES`, `NO` | All Block D presence questions except hedging; §3.5 evidence flags; §7.2 mitigants 1, 2 and 4 |
| `YNNA_3` | `YES`, `NO`, `NOT_APPLICABLE_FIXED_RATE` | §6.3 hedging policy (Template 1 §D.3); §7.2 mitigant 3 (Template 1 §N.7) |

`NOT_APPLICABLE_FIXED_RATE` means the rated debt carries no floating-rate or FX exposure, so the test does not arise. **It is scored as present** at both §6.3 and §7.2 (see §7.2, resolving QA finding M6). It is not the same answer as `NO`.

### PROJ_STATE_3 — Project state for construction and ramp-up (§7.3)

| Code | Display string |
| --- | --- |
| `STATE_OPERATING_MATURE` | Operating, 12 or more months since COD |
| `STATE_OPERATING_RAMPUP` | Operating, under 12 months since COD (ramp-up) |
| `STATE_PRECOD` | Under construction / pre-COD |

### EPC_3, CONTR_3, EXEC_3 — Pre-COD execution inputs (§7.3)

| Enumeration | Codes |
| --- | --- |
| `EPC_3` | `EPC_TURNKEY` (single fixed-price turnkey) · `EPC_MULTI` (multi-contract) · `EPC_NOT_APPLICABLE` (operating) |
| `CONTR_3` | `CONTR_ADEQUATE` · `CONTR_WEAK` · `CONTR_NOT_APPLICABLE` (operating) |
| `EXEC_3` | `EXEC_STANDARD` · `EXEC_ELEVATED` · `EXEC_NOT_APPLICABLE` (operating) |

### OFFTAKER_TYPE_2 and COUNTERPARTY_4

| Enumeration | Codes |
| --- | --- |
| `OFFTAKER_TYPE_2` | `OFFTAKER_CI` (Commercial & Industrial) · `OFFTAKER_DISCOM` |
| `COUNTERPARTY_4` | `CP_STRONG` · `CP_ADEQUATE` · `CP_WEAK` · `CP_POOR_UNRATED` |

### P90_BASIS_1 — Basis of the CFADS schedule (§9.5)

| Code | Display string |
| --- | --- |
| `ATTESTED_P90` | Attested as P90 |

**A single-member enumeration, deliberately.** v2.0 offered a second option — derivation of CFADS from the entered P90 PLF — which Template 2 never implemented (QA finding B5). Route (a) is withdrawn, so exactly one value is permitted, and `p90_attestation_basis` is in effect a constant. It is declared here rather than left in Section 9.5 prose because Appendix A is the list the engine matches on, and a value the engine must match on belongs in it. Any other value, including a blank, makes `p90_plf` a null critical input (Section 9.8.1).

### TREATMENT_2 — Instrument equity-treatment classification (§9.3)

| Code | Display string |
| --- | --- |
| `TREATMENT_DEBT` | Debt |
| `TREATMENT_EQUITY` | Equity — all three §9.3 conditions satisfied |

**Default is `TREATMENT_DEBT`** for every instrument, including subordinated sponsor loans and compulsorily convertible debentures. `TREATMENT_EQUITY` requires affirmative satisfaction of all three §9.3 conditions and is recorded per instrument. A blank treatment is a null, not a default (resolving QA findings B4 and M14).

## 14.2 Output enumerations

*Where an enumeration appears in both §14.1 and this table, §14.1 governs and this table is a cross-reference only. `COUNTERPARTY_4` was declared twice with different member sets — codes at §14.1, display words here — in an appendix that requires matching on code. Corrected: one name, one member set.*

| Enumeration | Members | Used at |
| --- | --- | --- |
| `TIER_5` | Full, Strong, Adequate, Weak, Deficient | 4.1, 4.2, 4.3, 4.4, 5.1, 5.2 |
| `LIQUIDITY_5` | Superior, Strong, Adequate, Stretched, Poor | 5.3 |
| `PRESENCE_4` | Full, Partial, Minimal, Absent | 6.1, 6.2, 6.3 |
| `COUNTERPARTY_4` | **Declared at §14.1 above** — `CP_STRONG` · `CP_ADEQUATE` · `CP_WEAK` · `CP_POOR_UNRATED`. It is both an input enumeration (Template 1 §N.6, the user-supplied aggregated tier) and an output vocabulary (§7.1 Step 1). **One enumeration, one member set.** | 7.1 |
| `BAND_8` | AAA, AA, A, BBB, BB, B, C, D | 8.2 |
| `CONFIDENCE_4` | High, Moderate, Low, Not Rated | 9.8.3 |
| `VALIDATION_4` | Pass, Warn, Block, Not Evaluated | 10.1, 10.1.1 |

*v2.0's `TIER_4` enumeration is withdrawn. It was declared at §10.3 as applying to §3.3.1 and §3.4, but neither of those tables carries a tier label — both are scored from derivation tables — so the enumeration had no site of use. Sections 3.1, 3.2, 3.3.2, 3.5 and 3.6 are scored from enumerated input selections mapped directly to points and carry no output tier label.*

---

# 15. Appendix B — Canonical Field Dictionary (normative)

*New in v3.0. Resolves QA findings B3 and M8. Execution Manual Activity 1.2 requires field names to be fixed once and reused everywhere; v2.0 gave four illustrative names in prose and left the remaining ninety-odd to be invented at build time, and three inputs were collected in both templates with no rule as to which governed.*

**Naming.** `snake_case`. The name in the `Field` column is the JSON schema property name, the Template 1 or Template 2 storage location, and the key the Test Projects input sheets use. It is not a display label.

**Units.** `frac` means a decimal fraction — 0.9700 for 97%. No field in this framework carries a percentage out of 100 (Section 9.6). `x` means a ratio multiple. `date` means ISO 8601 `YYYY-MM-DD` in transport, however the template renders it for entry.

**Source of truth.** Where a field is captured in both templates, the `Source` column names the governing template. The other template displays it read-only. Validation rule V13 requires them to agree.

## 15.1 Project identification and parameters

| Field | Type | Unit | Critical? | Source | Feeds |
| --- | --- | --- | --- | --- | --- |
| `project_name` | string | — | | T1 §A.1 | audit |
| `technology_type` | `TECH_3` | — | **Yes** | **T1 §A.1** | §4.0 threshold set |
| `project_status` | `STATUS_2` | — | **Yes** | T1 §A.1 | §7.3 |
| `cod_date` | date | — | **Yes** | T1 §A.1 | §7.3, V11 |
| `calculation_date` | date | — | **Yes** | **T1 §A.1** | V11, all tenors |
| `installed_capacity_mw_ac` | number | MW | | T1 §A.1 | audit |
| `currency_unit` | string | — | | T2 | display |

## 15.2 Block A — Business / Operating

| Field | Type | Unit | Critical? | Source | Feeds |
| --- | --- | --- | --- | --- | --- |
| `competitive_position` | `COMP_POS_5` | — | | T1 §A.2 | §3.1.1 |
| `auction_benchmark_note` | string | — | | T1 §A.2 | audit |
| `contracted_revenue_share` | number | frac | **Yes** | **T1 §A.2** | §3.2.1, §4.0 merchant test |
| `contracted_share_full_tenor` | number | frac | | T1 §A.2 | §3.2.1 rows 1, 3, 4, 5 |
| `contracted_share_75pc_tenor` | number | frac | | T1 §A.2 | §3.2.1 row 2, second limb |
| `remaining_contracted_tenor_years` | number | years | | T1 §A.2 | §3.2.1, audit |
| `remaining_debt_tenor_years` | number | years | | T1 §A.2 | §3.2.1, §7.2 |
| `price_volume_risk` | `PRICE_VOL_5` | — | | T1 §A.2 | §3.2.2 |
| `land_acquisition_status` | `PERMIT_3` | — | | T1 §A.3 | §3.1.2 |
| `transmission_connectivity_status` | `PERMIT_3` | — | | T1 §A.3 | §3.1.2 |
| `statutory_clearances_status` | `PERMIT_3` | — | | T1 §A.3 | §3.1.2 |
| `permitting_dispute` | `DISPUTE_5` | — | | T1 §A.3 | §3.1.2 operating rule |
| `regulatory_stability` | `REG_STAB_5` | — | | T1 §A.4 | §3.1.3 |
| `offtake_states` | string | — | | T1 §A.4 | audit |
| `technology_maturity` | `TECH_MAT_3` | — | | T1 §A.5 | §3.3.1 |
| `bop_grid_complexity` | `BOP_3` | — | | T1 §A.5 | §3.3.1 |
| `almm_status` | `ALMM_5` | — | | T1 §A.5 | §3.3.2 |
| `almm_basis_reference` | string | — | | T1 §A.5 | audit, V12 |
| `wtg_oem_indian_years` | number | years | | T1 §A.5 | §3.3.1 evidence |
| `reinvestment_ratio` | number | frac | | T1 §A.6 | §3.4 |
| `reinvestment_funding_source` | `FUND_SRC_5` | — | | T1 §A.6 | §3.4 |
| `operating_years_completed` | number | years (2 dp) | | T1 §A.7 | §3.5 |
| `actual_gen_vs_p90_y1` | number | frac | | T1 §A.7 | §3.5 row 1 (legitimately null for projects with fewer than 3 years of operating history) |
| `actual_gen_vs_p90_y2` | number | frac | | T1 §A.7 | §3.5 row 1 (legitimately null for projects with fewer than 3 years of operating history) |
| `actual_gen_vs_p90_y3` | number | frac | | T1 §A.7 | §3.5 row 1 (legitimately null for projects with fewer than 3 years of operating history) |
| `actual_gen_vs_p90_period` | number | frac | | T1 §A.7 | §3.5 rows 2, 3, 4 |
| `independent_resource_assessment` | `YN_2` | — | | T1 §A.7 | §3.5 |
| `p90_verified_by_lta` | `YN_2` | — | | T1 §A.7 | §3.5 |
| `generation_performance_guarantee` | `YN_2` | — | | T1 §A.7 | §3.5 row 1 |
| `operator_years` | number | years (1 dp) | | T1 §A.8 | §3.6 |
| `operator_mw_under_om` | number | MW | | T1 §A.8 | §3.6 |
| `sponsor_projects_at_cod` | integer | count | | T1 §A.8 | §3.6 |
| `sponsor_support_comparable_count` | integer | count | | T1 §A.8 | §3.6 tiers 1, 4 |
| `sponsor_support_this_project` | `YN_2` | — | | T1 §A.8 | §3.6 tiers 3, 4 |

## 15.3 Block B — Cash-flow Adequacy

| Field | Type | Unit | Critical? | Source | Feeds |
| --- | --- | --- | --- | --- | --- |
| `p90_plf` | number | frac | **Yes** | T2 §B3 | §9.5 |
| `p90_attestation_basis` | const `ATTESTED_P90` | — | **Yes** | T2 §B3 | §9.5 |
| `p90_resource_study` | string | — | **Yes** | T2 §B3 | §9.5 |
| `p90_preparer` | string | — | **Yes** | T2 §B3 | §9.5 |
| `dscr_schedule[]` | array | — | **Yes**¹ | T2 §B1 | §4.1, §4.2, §9.2.1 |
| `minimum_dscr` | number | x | **Yes**¹ | T2 §B2 | §4.1, §8.3 coverage floor, V1, V8, V8a (legitimately null when dscr_schedule is supplied instead — CORE Section 9.8.1 permits this as an alternative) |
| `average_dscr` | number | x | | T2 §B2 | §4.2, V1 (legitimately null when dscr_schedule is supplied instead — CORE Section 9.8.1 permits this as an alternative) |
| `dscr_schedule[].debt_year` | integer | — | | T2 §B1 | ordering |
| `dscr_schedule[].cfads` | number | currency | | T2 §B1 | §9.1 |
| `dscr_schedule[].interest` | number | currency | | T2 §B1 | DSCR denominator |
| `dscr_schedule[].principal` | number | currency | | T2 §B1 | DSCR denominator |
| `cfads_nca_by_period[]` | array | currency | | T2 §B4 | V6 |
| `npv_cfads_project_life` | number | currency | | T2 §B5 | §4.3 |
| `npv_cfads_loan_life` | number | currency | | T2 §B5 | §4.4 |
| `discount_rate` | number | frac | | T2 §B5 | §9.4 |
| `discount_rate_as_of` | date | — | | T2 §B5 | §9.4, V12 |
| `remaining_project_life_years` | number | years | | T2 §B5 | V2 |
| `remaining_loan_life_years` | number | years | | T2 §B5 | V2 |
| `principal_outstanding_senior` | number | currency | | T2 §B5 | §4.3, §4.4 denominator |

¹ **The critical requirement is satisfied by either route, not both.** Section 9.8.1 requires `dscr_schedule[]` **or** a directly entered `minimum_dscr`. Where the schedule is supplied, `minimum_dscr` and `average_dscr` are **derived** from it and must not also be entered — validation rule V13's principle applies, and a supplied value that disagrees with the schedule is a Block. Where only `minimum_dscr` is entered, Section 4.2 has no operand, `average_dscr` is a non-critical null scoring 0 with a Null Register entry, and V1 returns `Not Evaluated` (Section 10.1.1).

*Added in v3.0. Section 9.8.1 named the direct-entry route as an alternative critical input and Section 10.1.1's worked example registered `avg_dscr` in the Null Register, but neither field appeared in this dictionary — so the alternative route could not be represented in the JSON schema at all, and the worked example named a field nothing defined. Note the canonical names are `minimum_dscr` and `average_dscr`; `avg_dscr` was an informal abbreviation and is not a field name.*

## 15.4 Block C — Financial Strength

| Field | Type | Unit | Critical? | Source | Feeds |
| --- | --- | --- | --- | --- | --- |
| `debt_instruments[]` | array | — | **Yes** | T2 §C1 | §9.3 |
| `debt_instruments[].label` | string | — | | T2 §C1 | audit |
| `debt_instruments[].amount` | number | currency | | T2 §C1 | §9.3 |
| `debt_instruments[].treatment` | `TREATMENT_2` | — | **Yes** | T2 §C1 | §9.3, V14 |
| `total_debt` | derived | currency | **Yes** | T2 §C1 | §5.1, §5.2 |
| `paid_up_equity` | number | currency | | T2 §C2 | §9.3 |
| `securities_premium` | number | currency | | T2 §C2 | §9.3 |
| `free_reserves` | number | currency | | T2 §C2 | §9.3 |
| `intangible_assets` | number | currency | | T2 §C2 | §9.3 |
| `revaluation_reserves` | number | currency | | T2 §C2 | §9.3 |
| `accumulated_losses` | number | currency | | T2 §C2 | §9.3 |
| `deferred_revenue_expenditure` | number | currency | | T2 §C2 | §9.3 |
| `tangible_net_worth` | derived | currency | **Yes** | T2 §C2 | §5.2, V9 |
| `project_cfo` | number | currency | | T2 §C3 | §5.1 |
| `dsra_total` | number | currency | | T2 §C4 | §5.3 |
| `dsra_encumbered` | number | currency | | T2 §C4 | §5.3, V7 |
| `other_cash_total` | number | currency | | T2 §C4 | §9.2 numerator |
| `other_cash_encumbered` | number | currency | | T2 §C4 | §9.2, V7a |
| `avg_monthly_debt_service` | number | currency | | T2 §C4 | §5.3 |

## 15.5 Block D — Structural Protections

| Field | Type | Source | Feeds |
| --- | --- | --- | --- |
| `waterfall_trustee` | `YN_2` | T1 §D.1 | §6.1 element 1 |
| `security_charge_assets` | `YN_2` | T1 §D.1 | §6.1 element 2 |
| `security_assignment_contracts` | `YN_2` | T1 §D.1 | §6.1 element 2 |
| `security_charge_accounts` | `YN_2` | T1 §D.1 | §6.1 element 2 |
| `security_pledge_shares` | `YN_2` | T1 §D.1 | §6.1 element 2 |
| `distribution_lockup` | `YN_2` | T1 §D.1 | §6.1 element 3 |
| `lockup_dscr_threshold` | number (x) | T1 §D.1 | audit (legitimately null unless distribution_lockup == "YES") |
| `cov_additional_indebtedness` | `YN_2` | T1 §D.2 | §6.2 |
| `cov_asset_sales` | `YN_2` | T1 §D.2 | §6.2 |
| `cov_change_of_control` | `YN_2` | T1 §D.2 | §6.2 |
| `cov_lender_stepin` | `YN_2` | T1 §D.2 | §6.2 |
| `reporting_covenant` | `YN_2` | T1 §D.3 | §6.3 |
| `hedging_policy` | `YNNA_3` | T1 §D.3 | §6.3 |
| `insurance_business_interruption` | `YN_2` | T1 §D.3 | §6.3 |

## 15.6 Notching inputs

| Field | Type | Unit | Critical? | Source | Feeds |
| --- | --- | --- | --- | --- | --- |
| `offtakers[]` | array (max 4) | — | | T1 §N.2–N.5 | §7.1 |
| `offtakers[].name` | string | — | | T1 | audit |
| `offtakers[].type` | `OFFTAKER_TYPE_2` | — | Yes if share ≥ 0.25 | T1 | §7.1 Step 1 |
| `offtakers[].contracted_share` | number | frac | Yes if share ≥ 0.25 | T1 | §7.1 Step 3, V3 |
| `offtakers[].rating_or_grade` | string | — | Yes if share ≥ 0.25 | T1 | §7.1 Step 1 |
| `offtakers[].rating_agency` | string | — | | T1 | §9.9 |
| `offtakers[].rating_date` | date | — | | T1 | §9.9 staleness |
| `offtakers[].edition` | string | — | | T1 | §9.9 staleness |
| `offtakers[].more_recent_published` | `YN_2` | — | | T1 | §9.9, V12 |
| `other_offtakers_count` | integer | count | | T1 §N.6 | §7.1 Step 3 |
| `other_offtakers_share` | number | frac | | T1 §N.6 | §7.1 Step 3, V3 |
| `other_offtakers_worst_tier` | `COUNTERPARTY_4` | — | | T1 §N.6 | §7.1 Step 3 (legitimately null when not applicable) |
| `bullet_share` | number | frac | | T1 §N.7 | §7.2 |
| `mitigant_cash_sweep` | `YN_2` | — | | T1 §N.7 | §7.2 |
| `mitigant_committed_refi` | `YN_2` | — | | T1 §N.7 | §7.2 |
| `mitigant_ir_hedge` | `YNNA_3` | — | | T1 §N.7 | §7.2 |
| `mitigant_residual_ppa` | `YN_2` | — | | T1 §N.7 | §7.2 |
| `project_state` | `PROJ_STATE_3` | — | | T1 §N.8 | §7.3 |
| `epc_structure` | `EPC_3` | — | | T1 §N.8 | §7.3 |
| `contractor_standing` | `CONTR_3` | — | | T1 §N.8 | §7.3 |
| `contingency_share` | number | frac | | T1 §N.8 | §7.3 (legitimately null: only relevant pre-COD — CORE Section 3.3.1 row 3; the engine treats a missing value as 0.0) |
| `execution_complexity` | `EXEC_3` | — | | T1 §N.8 | §7.3 |

## 15.7 Engine outputs

| Field | Type | Notes |
| --- | --- | --- |
| `block_a_score` … `block_d_score` | number | Against maxima 35 / 35 / 25 / 20 |
| `raw_score` | number | Maximum 115, no rounding at any level |
| `notches_applied[]` | array | `{source_section, notches, points}` |
| `post_notching_score` | number | Floored at 0. **Never altered by a cap.** |
| `indicative_band` | `BAND_8` | From §8.2 |
| `final_band` | `BAND_8` | Lower of indicative band and lowest applicable cap |
| `cap_triggers[]` | array | `{trigger, capped_band, binding}` |
| `cap_notice` | string | Populated only where `final_band != indicative_band` |
| `distance_to_band_edge` | number | *d* per §9.8.3 |
| `confidence` | `CONFIDENCE_4` | Per §9.8.3 |
| `confidence_reason` | string | Mandatory where confidence is not High |
| `null_register[]` | array | `{field, sub_factor, points_forgone}` |
| `validation_results[]` | array | `{rule, outcome ∈ VALIDATION_4, detail}` |
| `sensitivity_result` | object | Band at Minimum DSCR = 1.20x, threshold set re-selected |
| `drivers[]`, `constraints[]` | array | For the rationale step |
