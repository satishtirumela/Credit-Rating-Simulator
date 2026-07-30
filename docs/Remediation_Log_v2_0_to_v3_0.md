# Credit Rating Simulator — Remediation Log, v2.0 → v3.0

**30 July 2026 · CA. Satish Tirumela · ICAI AICA Level 2 capstone**

Every finding in the final pre-build QA review, mapped to the change that closes it and the artefact it was made in. **7 blocking · 16 major · 19 minor · 3 newly discovered = 45 findings, all closed.**

| Artefact | v3.0 file |
| --- | --- |
| Core Rating Criteria | `Credit_Rating_Criteria_CORE_v3_0.md` |
| Execution Manual | `Credit_Rating_Simulator_Execution_Manual_v3_0.md` |
| Key Input Template 1 | `Key_Input_Template_1_v3_0.md` |
| Key Input Template 2 | `Key_Input_Template_2_v3_0.xlsx` |
| Corpus manifest | `Reference_Corpus_Manifest_v3_0.csv` |
| Manifest generator / verifier | `corpus_manifest.py` (new) |
| Remediation script | `corpus_remediate.py` (v3.0) |
| Hygiene specification | `Reference_Corpus_Hygiene_and_Ingestion_Specification_v3_0.md` |

---

## A. Three defects discovered during verification of your B1/B2 work

These were not in the original review. They were introduced by the remediation itself, and each one broke a contract that the remediation existed to establish.

| Ref | Defect | Resolution |
| --- | --- | --- |
| **N1** | **The corpus became mixed-format.** The four renamed files were re-supplied as genuine `%PDF` files; the other 37 remain ZIP containers. The Hygiene Spec's central claim — *"All 42 files… begin with PK\x03\x04. None begins with %PDF"* — was false for four files, and the six-rule contract ("Open each file as a ZIP") failed on exactly those four, silently, reading as corruption. | Hygiene Spec §2 rewritten: MIXED, 37 ZIP / 4 PDF. Ingestion contract rewritten to **dispatch on the manifest's `container` column**. `payload_basis` column added to record which hashing rule applies. `corpus_remediate.py` `payload_hash()` made container-aware (it raised `BadZipFile` on the four PDFs). CORE §12 and Execution Manual 3.1 updated. |
| **N2** | **The manifest stopped matching the folder.** Renames were applied under a shorter convention than the script targeted, so the manifest listed four filenames that did not exist and omitted four that did. `corpus_remediate.py --verify` reported **4 BLOCKED** against files that were already correct — worse than no tooling, because it trains the operator to ignore it. | Treated **disk as authoritative**. New `corpus_manifest.py` regenerates the manifest from the folder as it stands; `RENAMES` in `corpus_remediate.py` updated to the applied names. `--verify` now reports **0 blocked, 5 done**; `corpus_manifest.py --verify` returns **PASS** on 41/41 files and 41/41 payload hashes. |
| **N3** | **Three impossible publication dates.** Banaskantha *December 23, 2038*; Juniper Green *March 2027*; ReNew Sandur *30 June 2045*. The "latest date on page 1" heuristic picks up PPA expiries on rating rationales. Spec §6.4 asserted exactly one date was wrong. | Rule changed to **latest date not later than the audit date** — regenerable, self-documenting, no hand-editing. Six dates corrected. `date_flag` column added, recording discarded future dates. Two revision-history documents (Fitch, Moody's) flagged `HEURISTIC-DISPUTED` with the competing date named, rather than patched. Hygiene Spec §5.2–5.3. |

---

## B. Blocking defects

| Ref | Defect | Resolution | Where |
| --- | --- | --- | --- |
| **B1** | Three mandatory artefacts did not exist; the Extension cross-reference was unverified. | All three now issued at v3.0. Extension cited **by title only** — v2.0's own resolution (b). The seven Extension-scope corpus documents identified so their absence from §12 is explained rather than looking like an omission. | CORE preamble, §0.1, §0.4, §11, §12 |
| **B2** | Renames documented as applied 30-07-2026 had not been applied; two filenames still collided on case alone. | Applied and verified: 41 files, **0** case-insensitive collisions, 41 distinct payload hashes, all matching. | Corpus + Hygiene Spec §1, §6 |
| **B3** | The Test Projects sheet did not carry the input set Execution Manual 1.5 claimed it did, so the acceptance test could not be run from it. | New **"Test Project Inputs"** sheet, 113 rows, full input set for all 8 reference projects, keyed on the Appendix B field names. Manual 1.5's false claim corrected. Held in a **separate fixtures workbook** so the blank template carries no invented figures — see §G. | Test Fixtures v3.0; CORE §10.2.1, §15; EM 1.5 |
| **B4** | Template 2 shipped with CCDs pre-classified as **Equity**, inverting CORE §9.3 on the field CORE says moves §5.1 and §5.2 by whole tiers. Also pre-filled technology, P90 PLF 0.28, the attestation, and merchant exposure. | Every pre-set input cleared (7 values + all 8 treatments). **`TREATMENT_DEBT` is the stated default** for every instrument including sponsor loans and CCDs, in the cell note. Dropdowns kept. A blank treatment is a null, not a default, and new rule **V14** blocks it. | T2 Data Input; CORE §9.3, §14.1 |
| **B5** | §9.5's derivation route claimed arithmetic enforcement Template 2 never implemented; `B58` returned "Satisfied" for any non-blank string. | **Route (a) withdrawn.** Attestation is the only route. `p90_attestation_basis` is now a constant (`ATTESTED_P90`), not an enumeration; all four attestation fields are critical. `B58` hardened; the dropdown reduced to the single permitted value. | CORE §9.5, §9.8.1; T2 |
| **B6** | Null resolution and validation gave two lawful outcomes on the same project (a null Average DSCR is a non-critical null *and* a V1 Block). Template 2 had invented a third behaviour. | New **§10.1.1**: five-stage pipeline — critical nulls → non-critical nulls → validation (operands-populated only) → scoring → engine assertions. **`Not Evaluated`** defined as the fourth validation outcome and **excluded from the confidence penalty**, since the underlying null already counts. Worked example included. | CORE §10.1.1, §8.1, §14.2; EM 2.2; T2 Validation |
| **B7** | Percentages were fractions in CORE and T2, out of 100 in T1 and the Test Projects sheet, with no stated conversion. Silent failure: 97 where 0.9700 is expected scores 0 instead of 8 *and* fires the merchant adjustment. | **Single normative line at §9.6**: *all percentage inputs are transmitted and stored as decimal fractions; no field carries a value out of 100.* Every T1 percentage restated with worked examples; T2 `(%)` captions relabelled; all reference projects restated; every percentage field marked `frac` in Appendix B. | CORE §9.6, §15; T1 throughout; T2; EM 1.2 |

---

## C. Major findings

| Ref | Resolution | Where |
| --- | --- | --- |
| **M1** | Coverage floor stated **absolute at 1.00x**, never shifted by the merchant adjustment, which is confined to the five **tier** thresholds. The reasoning is given: tier thresholds grade headroom above self-sufficiency and merchant volatility properly demands more of it; the floor tests whether the project is self-sufficient at all. The consequence — 0 of 15 points without a cap — is stated rather than left to be derived, and new rule **V8a** surfaces it. | CORE §4.0, §4.1, §8.3, §10.1; T2 |
| **M2** | Band edges defined as the **seven interior thresholds** 22/43/64/78/90/100/108; **0 and 115 expressly excluded**. Verified: this definition reproduces TP-1 (d=7.0, High) and TP-3 (d=22.0, High) exactly as published in v2.0. The literal v2.0 reading gives d=0 for both and downgrades both to Moderate. | CORE §9.8.3 |
| **M3** | "Binding" restored in both places, plus the Results screen and the cap-independence assertion. TP-3 trips two non-binding caps and must return **High** — an engine built to the v2.0 manual wording fails its own acceptance test. New test pairs TP-3 against TP-4. | EM 1.3, 4.4, 4.7, H |
| **M4** | §3.5 restated as a **performance limb** and an **evidence limb** with the lower governing — one rule, not two contradictory ones. The "< 1 full operating year" limb deleted, closing the BL-5 double-count it re-admitted. Two worked consequences stated. | CORE §3.5 |
| **M5** | "Established performance history" **deleted**. Row 1 turns on the 12-month test alone. Generation-record quality is graded at §3.5, on evidence §A.7 actually collects. | CORE §7.3; T1 N.8 |
| **M6** | `NOT_APPLICABLE_FIXED_RATE` **scored as present** at §7.2, mirroring §6.3. Mitigants tabulated with field names. T1's open instruction to the user to "confirm the treatment before relying on it" removed — the question is closed in the criteria, not shipped in a template. | CORE §7.2, §14.1; T1 N.7 |
| **M7** | The aggregated offtaker line is **a single counterparty** for the dominance test and the blend. Stated because it is structural: four individual offtakers each below 25% cannot sum to 100%, so this line is the **only** route to the blended-tier fallback. The user-derived tier is declared as an exception with a mandatory evidence field. | CORE §7.1; T1 N.6 |
| **M8** | Appendix B names one **governing template** per duplicated field; T1 governs `technology_type` and `calculation_date`, T2 shows them read-only. Merchant exposure is **derived**, never entered. New rule **V13** blocks a mismatch. | CORE §10.1, §15; T1 A.1–A.2; T2 |
| **M9** | CFADS-component collection **withdrawn** and the verification gap **disclosed** — the alternative was expanding T2 into a cash-flow model, which §0.3 forbids. **V6 restated as period-by-period** and rebuilt in T2 with an NCA series in column H and per-period variance in column I; v2.0 compared schedule totals, which passes while periods diverge in offsetting directions. | CORE §10.1, §10.2, §11; T2 |
| **M10** | **Appendix A** issued: 26 enumerations, every option carrying a **stable code**. The engine matches on code, never display text, so wording can improve without a schema break. | CORE §14; T1 throughout; EM 1.2 |
| **M11** | `contracted_share_75pc_tenor` added (row 2's second limb at §3.2.1 was unreachable without it) and `sponsor_support_this_project` added (§3.6 row 3 was not scoreable without it). §3.2.1's **three distinct quantities** separated with a table. | CORE §3.2.1, §3.6, §15; T1 A.2, A.8 |
| **M12** | Generation evidence split into **four typed numeric cells** — three annual plus a period figure — replacing one free-text cell that asked for three years "lowest first" and could not be typed, validated or extracted. | CORE §3.5, §15; T1 A.7 |
| **M13** | Nil or negative TNW **scores 0** with a V9 Warn. Stated as a **scored zero, not a null**: it does not enter the Null Register and does not reduce confidence. v2.0's blank return presented it as a non-critical null — the same 8-point loss plus a confidence downgrade the criteria never called for. | CORE §5.2, §10.1; T2 both sheets |
| **M14** | The vacuous reconciliation replaced. v2.0 compared Total Debt to its own defining formula, so it always passed; the real risk — an instrument with an amount and a blank treatment, silently excluded from **both** Total Debt and TNW — was unguarded. New **V14** catches it. | CORE §10.1; T2 Validation |
| **M15** | Reference projects extended **3 → 8**, closing every gap: binding cap (TP-4), ramp-up (TP-6), both unexercised §7.2 rows (TP-5, TP-6), multi-offtaker and blended tier (TP-5), nulls (TP-6), critical null (TP-7), Block failure (TP-8). Manual 1.5 gains a table stating what each tests. | Test Fixtures v3.0; EM 1.5 |
| **M16** | Version breach closed by reissuing **all six documents at v3.0 on one date**, rather than patching one member of an inconsistent set. `Data Input` added to the extraction contract. | All artefacts |

---

## D. Minor findings

| Ref | Resolution |
| --- | --- |
| **m1** | Counts stated consistently: **42 as assembled, 41 after quarantine**; methodology count restated in the past tense so the arithmetic is followable. |
| **m2** | Read Me row references corrected (v2.0's "rows 9–38" and "rows 40–44" were **both** stale). Nine **named ranges** added so row insertion cannot silently break the pipeline again — treating the cause, not the symptom. |
| **m3** | Poor/Unrated restated as **C+, C, C−, D or unrated**. "CCC+" removed: it is S&P/Fitch international notation, not an Indian national-scale symbol, so v2.0 anchored the residual tier on an impossible value and left C+ and C− enumerated nowhere — falsifying the row's own claim to leave no rating between two tiers. |
| **m4** | Methodology count corrected 21 → **20 distinct**, with the Fitch duplication explained. |
| **m5** | Two meanings of "notch" disambiguated with a warning block: a CORE notch is 7 points; a conventional notch is one scale step; a CORE band spans 8–22 points and covers roughly three conventional notches. The back-test restated in **rating categories**. The mechanic keeps its name — "post-notching score" is embedded in the order of operations, the Results screen and the return object — and the ambiguity is resolved at the point of comparison, where it caused harm. |
| **m6** | Derivation tables added: **nine rows** for §3.3.1's 3×3 grid, **five codes** for §3.3.2. `TIER_4` **withdrawn** — declared at §10.3 but with no site of use, so it would have become a dead type in the schema. |
| **m7** | §10.1 split into **input validations (V1–V14)** and **engine assertions (A1–A4)**. V4/V5/V10 test the engine's arithmetic, not the user's data; calling them "Block" implied a user could clear them by correcting inputs. New **A4** added for cap independence. |
| **m8** | Other unencumbered cash **excluded** from the liquidity numerator and **included** in the PLCR/LLCR numerator, with the reasoning. v2.0 implemented this correctly in T2 and documented it nowhere, so a reviewer working from the criteria could land a tier higher. |
| **m9** | All sheets protected with **164 input cells unlocked** — what the Read Me asked for and nothing enforced. Legacy dropdowns stripped from formula cells. Named ranges added. |
| **m10** | T1 enums restated against Appendix A codes; every field labelled with its Appendix B name; six T2 critical fields marked `[CRITICAL]`; free-text "Not Applicable" replaced by explicit codes or "leave blank", so a deliberate answer is never confusable with a null. |
| **m11** | Companion documents cited by **title and version**, never filename — CORE §12's own reasoning about filename instability applied to its cross-references. |
| **m12** | Documents issued as `.md`, matching their actual format, rather than Markdown inside a `.docx` extension. |
| **m13** | Two external sources marked **external, not in corpus** so the grounding step does not attempt a manifest lookup; the seven Extension-scope documents identified. |
| **m14** | §3.3.2's technology asymmetry disclosed at §11: a wind-only project scores the sourcing point by definition, so the 115-point scale is not perfectly technology-neutral. Retained on the merits — no ALMM-equivalent mandate applies to wind — but recorded rather than implicit. |
| **m15** | The self-certified share-summation field **deleted**. It asked the user to assert what V3 computes, with no rule for a disagreement. |
| **m16** | Back-test reframed as **directional**: sample raised to 8–10, three findings reported instead of a headline accuracy figure, and an explicit statement that nine calibrations cannot be fitted to ten observations, so they remain provisional afterwards. A second common mistake added — tuning a parameter to close a gap the back-test reveals. |
| **m17** | `execution_complexity` added to §7.3 row 3's qualifying set. v2.0 listed elevated complexity as disqualifying in row 4 but omitted it from row 3, so a turnkey/adequate/6%/elevated project matched **both** rows. |
| **m18** | §3.6 limb conditions made **mutually exclusive and exhaustive**. An operator with zero years and zero MW previously satisfied both tier 3 and tier 4 with no precedence stated. |
| **m19** | `calculation_date` marked **critical** and added to §9.8.1. V11 is a blocking rule that cannot run without it. |

---

## E. Verification performed

Nothing above is asserted without a check.

| Check | Result |
| --- | --- |
| `corpus_manifest.py --verify` | **PASS** — 41/41 files resolve, 41/41 payload hashes match, 0 collisions |
| `corpus_remediate.py --verify` | **0 blocked, 5 done** (was 4 blocked) |
| Manifest containers vs disk | 37 ZIP + 4 PDF, matching on all 41 rows |
| Manifest tier / category counts | 20 / 1 / 20; Solar 8, Wind 4, Hybrid 6, BESS 1, Wind-Solar-BESS 1 |
| Duplicate payload groups | 0 |
| Every CORE / T1 / EM edit | Applied by script with a per-edit assertion that the target string occurred **exactly once**; every miss investigated and fixed, not skipped |
| Block maxima | 12+13+3+3+2+2 = 35 · 15+8+6+6 = 35 · 10+8+7 = 25 · 8+6+6 = 20 · total **115** |
| TP-1 to TP-6 recomputation | Block B and Block C **derived from the input sheet** and reconciled against intended scores — 6 of 6 exact |
| TP-1 / TP-2 / TP-3 against v2.0 | Reproduced **exactly** (115/AAA/d=7.0/High · 77.5/BB/d=0.5/Moderate · 0/D/d=22.0/High), independently validating the M2 band-edge definition |
| Formatting sweep | Non-breaking spaces and trailing whitespace removed from all three Markdown documents |
| Workbook reopened after build | 8 sheets, 9 named ranges, protection active, 3 dropdowns retained |

---

## F. Two things to check before you build

**1. The corpus format divergence is a decision, not just a fix.** I resolved N1 by accepting the mixed corpus and making ingestion dispatch on the manifest. The alternative was converting the four PDFs back to ZIP containers so the corpus is uniform and the original six-rule contract holds unchanged. Dispatching is more robust and handles whatever arrives next; uniformity is simpler to implement. If you prefer uniformity, the manifest regenerates in one command and the Hygiene Spec §2 and §4.1 are the only sections that change.

**2. The nine Developer calibrations are still provisional, and now say so.** m16's resolution means the back-test will no longer produce a headline accuracy figure to put in the submission. That is the honest position — nine free parameters against ten observations — but it is a weaker-sounding claim than v2.0 promised, and worth deciding on deliberately rather than discovering at the write-up stage. The three findings the back-test *can* support are specified at Manual 5.1.
