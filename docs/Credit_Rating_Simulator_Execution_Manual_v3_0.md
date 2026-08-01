**CREDIT RATING SIMULATOR**

Execution Manual

*A step-by-step guide to build and submit the project independently*

*ICAI AICA Level 2 —** ****Satish Tirumela**** Capstone*

| Prepared for | CA. Satish Tirumela |
| --- | --- |
| Reader profile | Finance Professionals |
| Project | Indicative Credit Rating decision-support tool |
| Nature | Academic |
| Manual version | 3.0 — 30 July 2026 (supersedes v2.0 and v1.0) |
| Aligned to | Core Rating Criteria v3.0; Key Input Template 1 v3.0; Key Input Template 2 v3.0 |
| Review cadence | On every CORE release |

*Guidance:** *

***Developer**** provides **finance** logic and judgement; Antigravity writes and deploys the code;*

*Gemini reads documents and drafts language;** *

*Claude is**** the**** co-pilot for prompts and troubleshooting.*

Table of Contents

How to read this manual 2

A. Project Overview 2

B. Project Objectives   3

C. Assumptions  3

D. Tools Required   4

Day 1 — Rating methodology and the Python engine    7

Day 2 — AI document reading and the validation screen   10

Day 3 — Grounding, rationale, and the PDF   12

Day 4 — Full application, agentic workflow, and hosting 15

Day 5 — Back-test, testing, documentation, and submission   17

G. Expected Deliverables    19

H. Quality Checks and Validation Steps  20

I. Risks and Mitigation 21

J. Final Project Completion Checklist   22

Final Readiness Assessment  23

Appendix — Ready-to-use prompts 23

# How to read this manual

This manual turns your 5-day plan into click-level instructions. It assumes you have never written or deployed software. Wherever a step is technical, you will not type code yourself — you will **tell Antigravity in plain English what to build**, then check the result using the validation tests provided.

Three tools do the heavy lifting, and it helps to keep their roles separate:

- **Claude** — For planning and troubleshooting co-pilot. Ask it to explain errors, refine prompts, and check logic. It does not build the app.

- **Google AI Studio (Gemini)** — reads financial documents, does the lightweight grounding, and drafts the rationale. Developer designs and tests the prompts here.

- **Antigravity** — builds the actual web application, the Python engine, and deploys everything. You direct it in plain English; it writes and runs the code.

**One rule for the project:** numbers are calculated by Python (fixed formulas, no AI), and only language and reading are done by Gemini. AI will not decide the Credit Rating.

# Reference architecture

The finance logic is anchored to three approved reference documents that Claude has ingested and that Gemini will draw on at build and run time:

- **Core Rating Criteria v3.0** — the fixed, engine-ready 115-point scorecard (Business/Operating 35, Cash-flow 35, Financial 25, Structural 20), notching rules, band map, band caps, required-inputs list, validation rules, and source-mapping table. Status: Approved for build. This is the single source of truth for every number the Python engine calculates.

- *v2.0 changed nine things the engine must implement differently from v1.0, and this manual has been amended throughout to match. In summary: the band table is now stated as half-open intervals; all quantitative tiers are single-sided thresholds with a stated evaluation precision; null handling and confidence have numeric definitions; the DSRA is permitted in the PLCR and LLCR numerators as a stated exception; offtaker credit and construction status are each scored in exactly one place; the offtaker-dependence threshold is 25% with a worst-tier rule; caps constrain the band rather than the score; Blocks A’s narrative factors are now enumerated inputs; and DSCR thresholds are technology-specific. See CORE §13 for the full change log and §13.4 for the Section 9 renumbering map.*

- **Crisil Intelligence Indian Renewable Energy Report (January 2026)** — used only to enrich the Business/Operating narrative and sector-context framing in the drafted rationale (capacity trends, tariff trajectory, policy/regulatory backdrop, DISCOM payment discipline, technology cost trends). It never feeds a score.

- **20 real-world rating rationales** (Wind 4, Solar 8, Wind-Solar Hybrid 6, BESS 1, Wind-Solar-BESS 1 — categorised by the terminal suffix of the file name, and authoritatively by the corpus manifest) — used as structural and style benchmarks only: how strengths/weaknesses are framed, how rating sensitivities are worded, how agencies sequence a rationale. Category-matched examples are selected per project (e.g. a solar assessment draws on the **8** solar rationales first). Numbers, conclusions, and issuer facts are never carried over from these documents into a new rationale — only structure and phrasing conventions.

# A. Project Overview

Credit Rating Simulator is a web application that gives a renewable-energy project an **indicative credit-rating band** (for example, BBB+) and a **written rationale** explaining why, before the developer ever approaches a rating agency. The user uploads **project information** in standardized templates; the application reads the uploaded information, scores the project against a transparent scorecard modelled on the published methodologies of Indian rating agencies (CRISIL, ICRA, CARE, India Ratings), and produces a rating with a plain-English explanation and a downloadable PDF.

A **back-testing** step runs projects whose real ratings are already public through the same scorecard, to show how close the tool’s output lands to reality. It is a **directional** check on whether the framework is sound, not a validation of its individual thresholds — with nine provisional calibrations and a sample in the high single digits, it cannot be the latter. Activity 5.1 states what the check can and cannot establish.

The result is deliberately labelled **indicative and academic** — it supports an internal view; it is not, and never claims to be, a SEBI-registered credit rating.

# B. Project Objectives

- Turn a **project information** into an **indicative rating band** using a transparent, methodology-aligned scorecard.

- Produce a **professionally written rationale** that cites the published criteria it relied on.

- **Read financial statements directly**, including scanned copies, so the user does not retype numbers.

- **Test reliability directionally** by back-testing against projects with known public ratings, reporting differences in rating categories and the sign of any systematic error.

- Keep every output **explainable, reproducible, and clearly positioned** as indicative decision-support.

# C. Assumptions

**About the way you will work as Developer**

- You will execute the project personally, directing Antigravity in plain English rather than hand-writing code.

- You have a Google account and can create free Google AI Studio and Firebase projects.

- All data used is public (published methodologies and rationales) or Developer’s own project data — so no confidential-data handling is required, and a cloud AI engine is acceptable.

**Built into the tool itself (shown on every result and PDF)**

- Uses publicly available rating methodologies.

- Intended for renewable-energy project finance only.

- Not a substitute for a SEBI-registered credit rating.

- Requires professional review before relying on the results.

- Assumes accurate user inputs and extracted financial data.

# D. Tools Required

| Tool | What it is for | How to get it / beginner note |
| --- | --- | --- |
| Google account | You Log in to AI Studio, Firebase, Gemini Notebook, Docs, Slides | Use an existing Gmail or create one at accounts.google.com |
| Google AI Studio | Gemini API key; design, test, extraction, grounding and rationale prompts | aistudio.google.com → sign in → Get API key. Free tier is enough |
| Antigravity | Builds the web app + Python engine and deploys them; your coding IDE | Install from the Antigravity site; sign in with Google. This is where Developer ‘talks to build’ |
| Python | Runs the scorecard maths | Developer does not install this — Antigravity sets it up and writes the code |
| Firebase / Google Cloud | Database (Firestore), file storage, hosting the web app, and running the Python engine (Cloud Run) | console.firebase.google.com → Add project. One project covers all of this |
| Gemini Notebook | Reads the methodology PDFs and helps you find the right sections | https://notebooklm.google.com/ → New notebook → upload PDFs |
| GitHub | Stores a copy of your project (version control) and holds the final code | github.com → sign up → create one empty repository |
| Google Apps Script | Turns the rationale into a formatted PDF | script.google.com — used on Day 3. (A Python PDF library is the alternative) |
| Screen recorder | Records the demonstration video (your face + screen) | Built-in (Windows Game Bar / Mac QuickTime) or Loom free |
| Project Presentation | Capstone presentation slides | Use the ICAI 4-slide template |
| Claude | Planning, prompt-writing and troubleshooting co-pilot throughout | claude.ai — keep it open beside Antigravity |

**Day 0 — Setup (do this before Day 1)**

This day is not in the original 5-day plan, but skipping it is the most common way a non-developer gets stuck. None of it is hard; it is mostly creating free accounts and confirming they work. Budget half a day.

**0.1 Create accounts**

**Tool — Web** browser

**Steps —**

- Sign in to a Google account (or create one).

- Open aistudio.google.com, sign in, click **Get API key**, create a key, and copy it into a private note. Treat it like a password.

- Create a Firebase project at console.firebase.google.com → **Add project**; accept defaults; when asked, enable the Blaze (pay-as-you-go) plan — the free monthly allowance covers a capstone, but Cloud Run needs Blaze enabled.

- Create a free GitHub account and one **new empty repository** named credit-rating-simulator.

- Install Antigravity and sign in with the same Google account.

**Validation —** you can open AI Studio, Firebase console, GitHub, and Antigravity while signed in, and you have your Gemini API key saved privately.

**0.2 Turn on the Firebase services you will use**

**Tool — Firebase** console

**Steps —**

- In the left menu open **Build → Firestore Database** → Create database → Start in test mode → pick a region close to you (e.g. asia-south1).

- Open **Build → Storage** → Get started (same region).

- Open **Build → Authentication** → Get started → enable **Email/Password** (you can keep auth minimal for a capstone).

- Leave the console open; you will return here when Antigravity asks for project details.

**Validation —** Firestore, Storage, and Authentication each show as enabled in the Firebase console.

**Common mistake —** forgetting to enable the Blaze plan. Cloud Run (which will host your Python engine on Day 4) will not deploy on the free Spark plan. Enabling Blaze does not mean you will be charged if you stay within the free allowance.

**0.3 Understand the hosting picture (read once, act on Day 4)**

**Tool — NA**

**Steps —**

- Your **web app / PWA** (the screens the user sees) will be hosted on **Firebase Hosting**.

- Your **Python engine** (the scorecard maths, exposed as a small FastAPI service) cannot run on Firebase Hosting — it needs **Google Cloud Run**. Antigravity will deploy it there for you.

- On Day 4 you will simply tell Antigravity: ‘deploy the Python engine to Cloud Run and the web app to Firebase Hosting and connect them.’ Knowing this now prevents a Day-5 surprise.

**Why this matters —** this single distinction (front-end on Hosting, Python engine on Cloud Run) is the one genuinely technical dependency in the whole project. Everything else is form-filling and prompt-writing.

**E. Day-wise Implementation Roadmap**

This keeps your five themed days and slots in the missing pieces (setup, wrapping the engine as an API early, the hosting decision, and back-test sourcing). If you have the full 10-day window, the ‘comfortable spread’ column shows where to add slack.

| Day | Focus | Main deliverable | If you have more time |
| --- | --- | --- | --- |
| Day 0 | Setup and accounts | All tools installed and verified | — |
| Day 1 | Rating methodology + Python engine + API | Working, tested scoring engine callable as an API | Split methodology and coding across two days |
| Day 2 | Document reading (Gemini) + validation screen | Upload → extract → editable JSON, saved to Firestore | Add a day to harden extraction on messy scans |
| Day 3 | Grounding + rationale + PDF | Cited rationale and a professional PDF | — |
| Day 4 | Full app + agentic workflow + QA + hosting | Deployed, end-to-end working web app | Give hosting/integration its own half-day |
| Day 5 | Back-test + testing + docs + package + submit | Submission package on the ICAI AI Hub | Split testing/docs from packaging/video |

**Critical path (protect these first):** the Python scoring engine (Day 1), the grounded rationale (Day 3), and the back-test (Day 5). If time runs short, thin the dashboard polish, make authentication minimal, and skip continuous integration — never cut the engine, the rationale grounding, or the back-test.

**F. Step-by-Step Activities**

Each activity below states its purpose, the tool, exact steps, the output you should see, how to confirm it worked, and the mistake to avoid. Work through them in order.

## Day 1 — Rating methodology and the Python engine

**1.1 Adopt the rating methodology and weights (Core Rating Criteria v3.0)**

**Purpose —**The finance logic — blocks, factors, points, scoring rules, band map, caps, and notching rules — is finalised in Core Rating Criteria v3.0 (v2.0, status: Approved for build), synthesised from **20** distinct published CRA methodology documents (CRISIL, ICRA, CARE, India Ratings, Fitch, Moody’s, Brickwork). *v2.0 of this manual said 21. The reference folder held 21 methodology files as assembled, but two were the same Fitch document under different filenames; the redundant copy is quarantined and the distinct count is 20 (QA finding m4). Of the 20, thirteen ground a factor in Section 12; the other seven sit within the Criteria Extension scope and ground nothing in the v1 engine.*. Your task on Day 1 is to read it, confirm it, and hand it to Antigravity — not to design it from a blank page.

**Tool — Claude** (to walk through the CORE document with you), Antigravity (to implement)

**Steps —**

- Open Core Rating Criteria v3.0 and confirm the four risk blocks and maxima: Business/Operating 35, Cash-flow Adequacy 35, Financial Strength 25, Structural Protections 20 (total 115) — Section 2.

- Confirm each block’s factors and points (e.g. Cash-flow: Minimum DSCR 15, Average DSCR 8, PLCR 6, LLCR 6, all on a P90 basis) — Sections 3–6.

- Confirm that Cash-flow thresholds are **technology-specific** from v2.0 — Set W for wind, Set S for solar, Set H for hybrid, selected from the technology type at Template 1 §A.1 — and that a **merchant adjustment** of +0.20x applies to every DSCR **tier** threshold in the selected set where merchant exposure exceeds **0.2500** (CORE §4.0). Sets S and H are Developer calibrations and are flagged as such.

- **The coverage floor at 1.00x is absolute and is NEVER shifted by the merchant adjustment** (CORE §4.1). v2.0 of this manual said the adjustment applies to "every threshold in the selected set", which reads as including the floor. It does not. The difference is decisive: on the adjusted reading a merchant-exposed project with Minimum DSCR between 1.00x and 1.20x scores 0 points **and** trips the BB band cap; on the correct reading it scores 0 points and does **not** trip the cap. Merchant exposure is stated as a **decimal fraction** and the comparison is **strict** — exactly 0.2500 does not trigger the adjustment. Validation rule V8a warns wherever the resulting combination arises, so it is visible rather than silent (QA finding M1).

- **Read CORE Appendices A and B before writing the schema.** Appendix A is the normative list of every enumeration with a **stable code**; Appendix B is the normative field dictionary giving every field's name, type, unit, criticality and governing template. The schema uses those names and codes and no others, and the engine matches on **code**, never on display text. *v2.0 of this manual gave four illustrative field names in prose and left the remaining ninety-odd to be invented at build time, while making Template 1's option strings authoritative for the schema at the same time as CORE claimed to be the single source of truth (QA findings M8, M10).*

- **Every percentage in the schema is a decimal fraction** — 0.9700 for 97%. No field carries a value out of 100 (CORE §9.6). Appendix B marks these `frac`.

- Confirm the score-to-band map (Section 8.2) and the notching mechanics — 1 notch = a fixed 7-point deduction, downward-only, additive, floored at zero (Section 7). Note that the band table is stated as **half-open intervals**, so every reachable score including every half-point value maps to exactly one band.

- Confirm the **order of operations** at CORE §8.1 and implement it exactly in that sequence: score → sum → notch → map to band → apply caps → compute confidence → apply flags. Reordering any step changes results.

- Confirm the **cap-the-band** mechanic at CORE §8.3. A cap constrains the band, not the score. Three caps exist: offtaker tier Weak caps at BB; offtaker tier Poor/Unrated caps at B; and a **coverage floor** caps at BB where Minimum DSCR is below 1.00x. Where several apply, the lowest governs.

- Confirm the **non-overlap map** at CORE §2. Offtaker credit quality is scored only at §7.1; construction and ramp-up status only at §7.3; liquidity only at §5.3. v1.0 breached this twice and the engine must not reintroduce either breach.

- Note the items explicitly flagged as illustrative/provisional pending back-test (e.g. PLCR/LLCR thresholds, Section 11) — these are fair targets to revisit once back-test data (Day 5) is available, but should not be silently changed before then. In v2.0 each such item is marked **[Developer calibration — provisional]** at its point of use and all of them are listed together at Section 11 — the PLCR/LLCR thresholds, the solar and hybrid DSCR sets, the 25% offtaker-dominance threshold, the bullet-share definitions, the contingency threshold, the reinvestment bands, the operator and sponsor thresholds, and the N = 3.0-point confidence window.

- Ask Claude to sanity-check the CORE document against your own judgement for gaps or double counting — the document states its own non-double-counting rule at **Section 9.7** (renumbered from 9.5 in v1.0; see the map at CORE §13.4) and its non-overlap map at Section 2, so this is a confirmation pass, not a redesign.

**Expected output — A** confirmed understanding of the CORE scorecard: blocks, factors, points, scoring rules, precision convention, band map, caps, order of operations, and notching rules — with no open questions before Antigravity encodes it.

**Validation — Every** factor in CORE Section 2 has a maximum and a clear rule; the block maxima add to 115; every quantitative tier is a single-sided threshold with no gap to the next; and a colleague could apply the document by hand and get the same score, band **and confidence level** you do. This last test is CORE’s own determinism standard at §0.2 — on the v1.0 draft it failed, and it is the acceptance test for the revision.

**Common mistake — Re-deriving** thresholds that CORE already fixes. If a number is in CORE, use it as-is; only the items Section 11 explicitly flags as provisional are open for revision.

**1.2 Design the data model (JSON schema)**

**Purpose — Define** the exact list of inputs the app will hold for each project, so extraction, scoring and storage all speak the same language.

**Tool — Claude** (to draft), Antigravity (to implement later)

**Steps —**

- **Start from CORE Appendix B (Section 15), not Section 10.2.** Section 10.2 describes the required inputs in prose, block by block; **Appendix B is the normative field dictionary** and gives every field's name, type, unit, criticality and governing template. Section 10.2.1 says so explicitly. Generate the schema from Appendix B rather than transcribing it — transcription is how a schema and its criteria drift apart, which is the defect class behind QA findings M8 and M10.

- **Every percentage in the schema is a decimal fraction** — 0.9700 for 97%. No field carries a value out of 100 (CORE §9.6); Appendix B marks these `frac`. Note that `frac` does **not** imply an upper bound of 1: a share cannot exceed 1, but `actual_gen_vs_p90_*` legitimately exceeds 1.0000 whenever a project outperforms its P90 estimate.

- **Take every field name from CORE Appendix B. Do not invent, abbreviate or paraphrase one.** *v2.0 of this manual offered `min_dscr, avg_dscr, gearing, offtaker_type, offtaker_rating` as examples and left the other ninety-odd names to be chosen at build time — which is QA finding M8. Worse, four of those five are **wrong** against Appendix B: the canonical names are `minimum_dscr`, `average_dscr`, `offtakers[].type` and `offtakers[].rating_or_grade`, and gearing is not an input at all but a value derived from `total_debt` and `tangible_net_worth`. `avg_dscr` is expressly recorded at Appendix B as an informal abbreviation and not a field name.* If a field you need is not in Appendix B, stop and raise it — do not coin one.

- **Implement every enumeration in CORE Appendix A — twenty-seven of them — and no others.** *v2.0 of this manual named five and said "and no others". Two things are wrong with that. **`TIER_4` is withdrawn** in v3.0 (QA finding m6): it was declared as applying to Sections 3.3.1 and 3.4, neither of which carries a tier label, so it had no site of use and would have become a dead type in the schema. And the five named were **output vocabularies only** — the twenty-odd **input** enumerations that actually constrain what a user may submit (`TECH_3`, `COMP_POS_5`, `PERMIT_3`, `ALMM_5`, `YNNA_3`, `TREATMENT_2` and the rest) were not mentioned at all, so a schema built to that bullet would have left every scored input as free text.* The output vocabularies are at Appendix A §14.2; the input enumerations are at §14.1. Both are normative.

- **Type every enumerated input as a strict enum of Appendix A CODES.** These fields carry 25 of the 115 points and were free-form narrative in v1.0; the schema must reject an unmatched value rather than accept it, and an input that does not resolve to a listed code is a **null**, not a coerced nearest match. *v2.0 of this manual said to match "the exact option strings in Template 1". That bullet **is** QA finding M10: display strings differed between CORE and Template 1 for the same option, the Manual made Template 1 authoritative while CORE claimed to be the single source of truth, and any later rewording of a display string would have silently broken the schema. Match on `TECH_SOLAR`, never on "Solar PV".*

- Model the offtaker array as **up to four individual counterparties plus one aggregated line** (Template 1 §N.2–N.6), each with type (C&I vs DISCOM), contracted revenue share, and current published rating or grade with edition and date. A missing or superseded edition/date is flagged stale per CORE §9.9, not silently applied.

- Model **Total Debt at instrument level** with an equity-treatment classification per instrument (CORE §9.3). The treatment of subordinated sponsor loans and CCDs moves Sections 5.1 and 5.2 by whole tiers, so it must be an explicit stored field, not an assumption inside a formula.

- Model the DSRA as **total balance plus encumbered portion** as two separate fields, so the partial-encumbrance rule at CORE §5.3 can exclude the encumbered part and score the remainder.

- **Add a P90 attestation object carrying all four fields** — `p90_plf`, `p90_attestation_basis` (the single permitted value `ATTESTED_P90`), `p90_resource_study` and `p90_preparer`. All four are critical: a blank in any one makes `p90_plf` a null critical input, and the pipeline stops at Stage 1 with "Insufficient Input — Not Rated". *v2.0 of this manual offered "either the derivation inputs or the preparer attestation". **The derivation route is withdrawn** (QA finding B5): Template 2 never implemented it, no formula ever linked the entered P90 PLF to the CFADS schedule, and the workbook's status cell returned "Satisfied" for any string at all. Attestation is now the only route.*

- Add the **Null Register** as a first-class output structure (CORE §9.8.2): field name, sub-factor affected, points forgone.

- **Encode the thirteen input validation rules V1–V14 at CORE §10.1** — there is no V4, V5 or V10, which became engine assertions — each carrying its classification, positioned per §10.1.1 Stage 3. **There are four outcomes, not two: Pass, Warn, Block and `Not Evaluated`.** A rule runs only where every operand it needs is populated; otherwise it returns `Not Evaluated`, does not block, and does not itself reduce confidence, because the underlying null already does.

- **A Block does not stop the other rules from running.** All thirteen are evaluated and the complete report is returned; only then does the pipeline stop without scoring (CORE §10.1.1 Stage 3, as clarified at §13.0.5). The review screen therefore shows every problem at once, so a preparer corrects one submission rather than discovering failures one at a time.

- **Keep the four engine assertions A1–A4 out of the schema and off the user-facing validation screen.** They test the engine's own arithmetic rather than the submitted data, so a failure is an implementation defect that must halt the response, not appear as something a user could correct. *v2.0 of this manual said "twelve validation rules… Block-or-Warn" with A1–A3 mixed in among them (QA finding m7).*

- **A Block failure stops the pipeline before scoring — and critical nulls stop it earlier still.** Stage 1 resolves critical nulls and returns "Insufficient Input — Not Rated" before any validation rule runs at all (§10.1.1, QA finding B6).

- Save the schema alongside CORE, not as a replacement for it.

**Expected output — A** master JSON schema covering project info, financials, and qualitative inputs, field-for-field matched to CORE Section 10.2, with the canonical enums, the validation rules, and the Null Register structure included.

**Validation — Every** factor in CORE Sections 2–7 has a matching field in the schema — no factor is unscorable for lack of an input. A missing critical field (CORE §9.8.1) returns “Insufficient Input — Not Rated”; a missing non-critical field registers as null, scores zero, and appears in the Null Register. Feed the schema a project with a deliberately mismatched enum string and confirm it is rejected rather than coerced.

**Common mistake — Inventing** new field names later. Fix the schema now and reuse the exact names everywhere.

**1.3 Build the Python scoring engine**

**Purpose — Turn** your scorecard into fixed formulas that always give the same score for the same inputs.

**Tool — Antigravity** (it writes the Python; you direct and check)

**Steps —**

- Open Antigravity, create a new project, and connect it to your GitHub repository when prompted.

- In plain English, instruct it: ‘Create a Python module that takes a project JSON matching this schema [paste schema] and executes **the five-stage pipeline at Core Rating Criteria v3.0 Section 10.1.1** — (1) resolve critical nulls and stop with "Insufficient Input — Not Rated" if any is absent; (2) resolve non-critical nulls to 0 and populate the Null Register; (3) run validation rules V1–V14, evaluating a rule only where every operand is populated and returning `Not Evaluated` otherwise, **evaluating every rule before stopping** — a Block does not halt the remaining checks; (4) score; (5) run engine assertions A1–A4. Stage 4 executes the order of operations at Section 8.1 exactly in that sequence: (1) score every sub-factor using Sections 3–6, applying the null rules at Section 9.8 and the precision convention at Section 9.6; (2) sum to a raw score out of 115 with no rounding at any level; (3) apply the notching rules in Section 7 — 1 notch = 7-point deduction, downward-only, additive, floored at zero; (4) map the post-notching score to an indicative band using the half-open intervals in Section 8.2; (5) apply the band caps in Section 8.3, where the final band is the lower of the indicative band and the lowest applicable cap, and the score itself is never altered by a cap; (6) compute confidence per Section 9.8.3; (7) return the band flags per Section 8.4. Return the post-notching score, the indicative band, the final band, the cap trigger where they differ, the four sub-scores, the notches applied with their sources, the confidence level, the Null Register, the drivers, and the constraints.’

- Instruct it explicitly on the **three implementation traps** that would otherwise reproduce v1.0’s defects: thresholds are single-sided and evaluated at the precision in CORE §9.6 with no tolerance band; a cap constrains the **band** and never the score; and the DSCR threshold set is **selected by technology** with a +0.20x adjustment to the **tier** thresholds, and only those, above **0.2500** merchant exposure — the 1.00x coverage floor is absolute.

- Ask it to compute the **confidence level from CORE §9.8.3, not from a judgment**: let *d* be the absolute distance in points between the post-notching score and the nearest band edge, and let *N* = 3.0. Not Rated if any critical input at §9.8.1 is null. Low if four or more non-critical nulls, or any input stale by more than one publication cycle, or an ALMM parameter more than 90 days past its “as at” date. Moderate if one to three non-critical nulls, or *d* < 3.0, or a **binding** cap has been applied, or any input is flagged stale. High only if there are no nulls, *d* ≥ 3.0, no **binding** cap is applied, and nothing is stale. **A cap that is triggered but does not lower the band is not binding and does not reduce confidence.** *Resolved in v3.0 (QA finding M3): v2.0 of this manual dropped the word "binding" from CORE §9.8.3 in both places. The distinction is not academic — reference project TP-3 trips two caps, neither of which lowers its band because the indicative band is already D, and the published expected result is **High** confidence. An engine built to this manual’s v2.0 wording would return Moderate and fail its own acceptance test.* Where more than one level’s conditions are met, the lowest governs. *This replaces the v1.0 formulation, which turned on the words** **“**comfortably**”** **and** **“**near**”** **and was the only definition of confidence anywhere in the project — neither word is implementable.*

- Ask it to add a **sensitivity** function: re-run the score with minimum DSCR set to 1.20 and report the resulting band. Note that on a technology-specific threshold set the same 1.20x sensitivity lands in different tiers for wind, solar and hybrid, so the function must re-select the set rather than assume one.

- Ask it to implement the twelve **validation rules** at CORE §10.1 as a pre-scoring gate. A Block failure raises and stops; a Warn failure proceeds and is returned for display.

**Expected output — A** Python scoring module that returns the post-notching score, indicative band, final band, cap trigger, sub-scores, notches with sources, confidence, Null Register, drivers, constraints, validation results, and a sensitivity result.

**Validation — Give** it the three hand-calculated test projects on the ‘Test Projects’ sheet of Key Input Template 2 v3.0; the engine’s score, band, cap status and confidence level match that sheet exactly for all three. Then confirm the two defects that v1.0 would have produced are absent: a project scoring 77.5 maps to BB (not to nothing), and a project with a Weak offtaker displays its uncapped score alongside the capped BB band.

**Common mistake — Letting** the engine ‘estimate’ anything. It must only apply your fixed rules. If a rule is missing it should flag it, not guess.

**1.4 Wrap the engine as an API (do this now, not on Day 4)**

**Purpose — Make** the engine callable by the web app later, so Day 4 integration is plug-in rather than rebuild.

**Tool — Antigravity** (FastAPI)

**Steps —**

- Instruct Antigravity: ‘Wrap the scoring module in a FastAPI service with endpoints /score, /extract, /rationale, /assess and /backtest, each accepting and returning JSON.’

- Ask it to run the service locally and show you a test call to /score with your sample project.

**Expected output — A** FastAPI service exposing the engine; a successful local /score response.

**Validation — A** test call to /score returns the same band as 1.3 for the same input.

**Common mistake — Postponing** this to Day 4. Building the API alongside the engine avoids a rushed integration later.

**1.5 Unit-test the engine**

**Purpose — Confirm** the maths is correct across normal and edge cases before anything is built on top of it.

**Tool — Antigravity** (it writes and runs the tests)

**Steps —**

- Use the **eight** hand-calculated reference projects in **Credit Rating Simulator Test Fixtures v3.0** — a separate workbook from Key Input Template 2, which is a blank form and deliberately holds no invented figures. The **"Test Project Inputs"** sheet carries the full input set for each, keyed on the CORE Appendix B field names, and the **"Test Projects"** sheet carries every expected output — intermediate sub-scores, raw score, notches, post-notching score, indicative band, cap status and whether it binds, final band, distance to the nearest band edge, null count and confidence level. The expected result is the whole result object, not a single band.

*v2.0 of this manual asserted that the three projects on the Test Projects sheet each carried "its full input set". They did not — the sheet held sub-scores and a handful of parameters, so the acceptance test could not be executed from it and a developer would have had to reverse-engineer inputs that happened to produce the stated scores (QA finding B3). The inputs sheet is new in v3.0, and every figure on the outputs sheet is derived from it rather than asserted alongside it.*

*Keep the fixtures workbook with the source code, not with the assessment paperwork, and do not place it in the same searchable knowledge base as a live assessment. Every figure in it is invented, and a retrieval for a field such as `p90_plf` or `total_debt` that returns a fixture value reads exactly like a fact about the project being rated.*

| Project | What it exists to test |
| --- | --- |
| TP-1 Strong Solar | Upper bound: raw 115, AAA, no notching, d = 7.0, High |
| TP-2 Mid Wind | Band-edge proximity: post 77.5, d = 0.5 → Moderate |
| TP-3 Weak Hybrid | Lower bound and **non-binding** caps: merchant adjustment, coverage floor, post 0 after the floor, two caps neither of which lowers the band, **High** confidence |
| TP-4 Capped AA Solar | **Binding cap.** Identical to TP-1 in every input except the offtaker rating: indicative AA, final BB, score unaltered, confidence Moderate. Directly tests assertion A4. |
| TP-5 Pre-COD Blend Wind | **Blended-tier fallback** — five counterparties, none at or above 0.2500, so the dominance test does not fire; the aggregated line counts as one counterparty. Plus §7.3 row 3 (all four pre-COD conditions met) and §7.2 partial bullet with **no** mitigant. |
| TP-6 Ramp-up Solar | **Ramp-up state**; §7.2 large bullet **with** a mitigant, satisfied via `NOT_APPLICABLE_FIXED_RATE`; partial DSRA encumbrance; a CCD that **fails** the §9.3 equity test; two non-critical nulls → Moderate |
| TP-7 Not Rated | **Critical null** — `technology_type` absent. Pipeline stops at Stage 1: no score, no band, no validation results, no partial output. |
| TP-8 Validation Block | **V1 Block** — Average DSCR 1.1000 below Minimum DSCR 1.2000. Pipeline stops at Stage 3; validation report returned, no band. |

- Instruct Antigravity: ‘Write unit tests checking the engine returns the expected sub-scores, raw score, notches, post-notching score, indicative band, final band and confidence level for these three projects, plus the edge cases below.’

- Require these edge cases specifically, each of which corresponds to a defect that existed in the v1.0 criteria:

- **Half-point score on a boundary** — a post-notching score of exactly 77.5 and of exactly 78.0. Both must map to a band, and 78.0 must be BBB while 77.5 must be BB.

- **Every quantitative boundary value** — 1.4999x and 1.5000x minimum DSCR on Set W; 24.99% and 25.00% CFO/Adjusted Debt; 11.9 and 12.0 months of DSRA cover; 1.8570x and 1.8571x gearing. Each must land in exactly one tier.

- **Cap-versus-score separation** — a project with a raw score in the AA range and a Weak offtaker. The result must show the uncapped post-notching score, an indicative band of AA, a final band of BB, and a cap notice.

- **Coverage floor** — a project with minimum DSCR of 0.98x and otherwise strong inputs. Final band must be capped at BB.

- **Critical null** — a project with technology type absent. Must return “Insufficient Input — Not Rated”, not a band.

- **Non-critical null** — a project with the covenant schedule absent. Must score zero for §6.2, populate the Null Register, and downgrade confidence.

- **Technology-set selection** — the same cash-flow profile submitted as wind, as solar and as hybrid. The three must produce different Block B scores.

- **Merchant adjustment** — merchant exposure of **0.2499**, **0.2500** and **0.2501** on identical cash flows. Only the third applies the +0.20x shift: the comparison is strict, so exactly 0.2500 does not trigger it. In all three the coverage floor stays at 1.00x.

- **Validation gate** — a project where average DSCR is below minimum DSCR. Must stop before scoring, not produce a flagged score.

- **Extreme gearing** and **nil tangible net worth**. The second must score §5.2 at zero and warn.

- Run the tests and fix any rule until all pass.

**Expected output — A** passing test suite covering the three reference projects and all ten edge-case families.

**Validation — All** tests pass. In particular, no input value anywhere in the suite fails to map to a tier, and no cap alters a reported score.

**Common mistake — Testing** only ‘nice’ projects. Every blocking defect found in the v1.0 criteria would have survived a suite of three well-formed projects and surfaced only in production — the boundary and null cases are the ones that matter.

## Day 2 — AI document reading and the validation screen

**2.1 Build a simple upload module**

**Purpose — Let** the user add the project’s documents (financials, IM, PPA, others).

**Tool — Antigravity** (front-end) + Firebase Storage

**Steps —**

- Instruct Antigravity: ‘Add an upload screen that accepts PDF and image files for Financial Statements, Information Memorandum, PPA, and Other, and stores them in Firebase Storage.’

- Keep this screen plain for now — the polished dashboard comes on Day 4.

**Expected output — A** working upload screen that stores files in Firebase Storage.

**Validation — You** upload a test PDF and can see it in the Firebase Storage console.

**Common mistake — Trying** to make it look finished today. Function first; styling on Day 4.

**2.2 Design and test the extraction prompt**

**Purpose — Get** Gemini to read a financial statement and return clean, structured numbers matching your schema.

**Tool — Google** AI Studio (Gemini)

**Steps —**

- Open aistudio.google.com → create a new prompt → attach a sample financial statement (a scanned PDF is a good test).

- Paste the extraction prompt from the ‘Ready-to-use prompts’ section (Appendix) and your JSON schema.

- Set temperature low (around 0.1). Run it and inspect the JSON.

- Adjust wording until the numbers are correct and anything absent is returned as null, never guessed.

**Expected output — A** tested extraction prompt that reliably returns schema-shaped JSON from a statement.

**Validation — For** a document whose figures you know, every extracted number is correct and missing items are null.

**Common mistake — Accepting** invented numbers. The prompt must say: return null for anything not present; never infer a figure.

**2.3 Wire extraction into the app**

**Purpose — Connect** the upload to Gemini so an uploaded document becomes structured JSON automatically.

**Tool — Antigravity** + Gemini API

**Steps —**

- In Antigravity: ‘When a document is uploaded, call Gemini with the extraction prompt and save the returned JSON to Firestore under the project.’

- Ask Antigravity to store the Gemini API key as a **server-side secret**, never in the browser code.

**Expected output — Uploading** a document produces JSON saved in Firestore.

**Validation — After** an upload, the extracted JSON appears in the Firestore console under the project.

**Common mistake — Pasting** the API key into front-end code. Anyone could read it. It must live server-side only.

**2.4 Build the validation screen**

**Purpose — Let** the user review and correct extracted numbers before scoring — this is your main defence against extraction errors.

**Tool — Antigravity**

**Steps —**

- Instruct Antigravity: ‘Show the extracted fields in an editable form; let the user fix any value and click Approve; mark each field as extracted or user corrected.’

- On Approve, save the confirmed JSON as the project’s inputs.

**Expected output — An** editable review screen; approved inputs saved.

**Validation — You** change a value, approve, and the saved input reflects your edit and is tagged user-corrected.

**Common mistake — Auto**-scoring straight from extraction with no human check. Always route through this screen.

## Day 3 — Grounding, rationale, and the PDF

**3.1 Organise the methodology corpus (largely already collected)**

**Purpose — Give** the tool the published criteria it will cite, so the rationale is grounded in real methodology. Most of this collection work is already done — this step is now about loading and structuring what you have, in three tiers.

**Tool — Google** AI Studio / Gemini Notebook

**Steps —**

- **Before loading anything, apply the ingestion contract below.** **All 41 files are genuine PDFs with a text layer** — verified at 660 of 661 pages carrying extractable text. Read them with an ordinary PDF library. No container dispatch is required.

- *This is simpler than it was earlier in v3.0, and the history is worth knowing because it explains why the tooling looks defensive. As originally assembled the corpus was **mixed**: 37 ZIP archives of per-page images and OCR text wearing a `.pdf` extension, and 4 genuine PDFs. A pipeline written against either assumption failed silently on the other set, reading as file corruption. On re-download the archives came back as real PDFs, which removed the problem — but only because the text layer survived, and that was **checked rather than assumed**.*

- **Still resolve documents through the manifest, never by filename.** Filenames in this corpus have proven unstable four separate ways: two collided on case alone, one methodology appeared twice, two carried malformed dates, and a re-download rewrote 37 of them. The manifest keys on content hash. Run `corpus_manifest.py --verify` before the grounding step; it fails loudly and names the problem.

- Two rules still apply and both fail *silently* rather than raising:

- **Open each file as a ZIP, not with a PDF library.** pypdf, pdfplumber and PyMuPDF all fail on every file in the corpus, and the failure reads as a corrupt-file error rather than a format mismatch. This one at least fails loudly.

- **For text, read the per-page**** ****.txt**** ****entries.** There is no PDF text layer to extract.

- **Sort page entries numerically, not lexicographically.** ZIP entry names sort as strings, so 10.txt comes before 2.txt. Sort on the integer stem or the pages assemble out of order — every page present, silently scrambled, and any grounding citation then points at the wrong page.

- **Never declare these files as**** ****application/pdf** to any API. A Gemini file upload so declared is rejected or mis-parsed.

- **Treat the text as OCR output.** It carries recognition errors, hard line breaks mid-sentence, and carriage returns rather than newlines. Normalise whitespace before matching, and do not treat a failed exact-string match as evidence that a passage is absent from the source.

- **Read the**** ****.jpeg**** ****entries only where a figure or table image is needed** — which includes the DSCR guidance table in the Fitch renewable criteria and the liquidity tiers in the CARE liquidity criteria, both of which live inside table images that OCR may not render usefully.

- **Identify documents by content hash, never by filename.** Reference_Corpus_Manifest_v2.0.csv is the authoritative index; resolve every grounding lookup through its payload_sha256 column. Filenames in this corpus have already proven unstable in three separate ways — two collided on capitalisation alone, one methodology was present twice under different names, and two carried malformed dates. The payload hash is stable across renames and re-compression because it hashes only the OCR text and page images. Run python corpus_remediate.py --corpus <folder> --verify after any clone, re-download or unzip and before this step; a non-zero collision count means a file has been lost and the corpus must be restored, not worked around.

- Tier 1 — Scoring criteria (grounds every number): Core Rating Criteria v3.0. Its Section 12 (Reference Mapping Table) already links each scored factor to its primary source document(s) — e.g. P90 DSCR basis to Crisil’s infrastructure criteria, PLCR/LLCR definitions to Fitch’s Global Infrastructure & Project Finance Criteria. Load this table as-is rather than re-deriving it.

- Tier 2 — Sector narrative (grounds the Business/Operating write-up only): Crisil Intelligence Indian Renewable Energy Report (January 2026). Use this for capacity-addition trends, tariff trajectory, RPO/policy backdrop, DISCOM payment discipline, and technology cost trends — never for scored numbers.

- Tier 3 — Style and structure benchmarks (never a source of numbers): the 20 collected rating rationales, already categorised by project type — Wind (4), Solar (8), Wind-Solar Hybrid (6), BESS (1), Wind-Solar-BESS (1). Use these to calibrate how the drafted rationale sequences strengths/weaknesses, phrases rating sensitivities, and matches agency tone — matched by category to the project being assessed.

- Create a notebook in Gemini Notebook (or equivalent grounding context in AI Studio), upload all three tiers, and confirm Gemini can distinguish which tier it is drawing from for a given statement.

**Expected output — A** structured three-tier corpus (CORE criteria, sector report, category-tagged benchmark rationales) loaded and ready for grounding.

**Validation — For** every scorecard factor you can point to the exact CORE-cited methodology section behind it (Section 12); for every sector-context sentence you can point to the Crisil report; for every stylistic choice you can point to a category-matched benchmark rationale — and none of these three ever cross-contaminate (no benchmark-rationale number ends up in a new draft). Additionally: the **Reference Corpus Manifest v3.0** lists 41 files, of which 20 are Tier 1 methodology documents, 1 is the Tier 2 sector report and 20 are Tier 3 benchmark rationales; the Tier-3 category counts read 8 solar, 4 wind, 6 hybrid, 1 BESS and 1 wind-solar-BESS; the `container` column reads **PDF on all 41 rows**; no two filenames collide when compared case-insensitively; and `corpus_manifest.py --verify` returns PASS, meaning every file on disk resolves to a manifest row and every payload hash matches. **A non-zero collision count, a container mismatch, or a hash mismatch means the corpus must be restored or the manifest deliberately regenerated — never worked around.**

**Common mistake — Letting** Tier 3 (benchmark rationales) leak numbers or issuer-specific facts into a new draft. It supplies structure and phrasing only.

**3.2 Adopt the factor-to-section mapping (CORE Section 12)**

**Purpose — Tell** the app which methodology passage to cite for each factor, so citations are precise. This table already exists — Core Rating Criteria v3.0 Section 12 maps every core factor (overall architecture, P90 DSCR basis, PLCR/LLCR definitions, liquidity tiers, structural checklist, each notching factor) to its primary source document(s).

**Tool — Claude** (to organise) + CORE Section 12

**Steps —**

- Copy CORE Section 12’s Reference Mapping Table directly into your grounding notebook — factor name → primary source document(s).

- Confirm every factor scored in CORE Sections 3–7 has a row in Section 12; flag and fill any gap before Day 3 proceeds.

- Keep the sector-report citations (Tier 2, from 3.1) in a separate column so the app can distinguish “this is a scoring citation” from “this is sector-context colour.”

**Expected output — A** factor-to-section mapping table sourced from CORE Section 12, plus a separate sector-narrative citation list.

**Validation — Each** material factor maps to one governing section already documented in CORE; no factor is left uncited.

**Common mistake — Vague** citations (‘as per CRISIL’). Cite the specific section CORE Section 12 already names.

**3.3 Set up lightweight grounding in Gemini (three-tier)**

**Purpose — Let** Gemini answer from your reference corpus without building a database, while keeping the three tiers (scoring criteria, sector narrative, style benchmarks) distinct.

**Tool — Google** AI Studio (Gemini long context + file grounding)

**Steps —**

- In AI Studio, attach CORE (Tier 1) and the CRISIL sector report (Tier 2) to the prompt context for factual/citation grounding.

- Separately, attach the category-relevant subset of the 20 benchmark rationales (Tier 3) — e.g. for a solar project, the **8** solar rationales — for style grounding only.

- Test: ask Gemini to return the passage that governs a given factor (should come from Tier 1, per CORE Section 12); ask it separately to describe how a benchmark rationale phrases a rating sensitivity (Tier 3) without pulling any of that document’s numbers.

**Expected output — Gemini** reliably returns the correct CORE-cited passage per factor, and separately can describe benchmark phrasing conventions without leaking benchmark numbers.

**Validation — For** three test factors, the passage returned matches CORE Section 12 (3.2); for a style check, no figure from a Tier 3 document appears in the response.

**Common mistake — Mixing** tiers in one undifferentiated corpus. Keep Tier 3 (benchmark rationales) clearly separated so its role stays “style only,” never “source of facts.”

**3.4 Generate the rating rationale**

**Purpose — Produce** the written explanation — summary, strengths, concerns, drivers, constraints — using only the scorecard result, CORE-cited passages, sector-report context, and category-matched style conventions.

**Tool — Google** AI Studio (Gemini), then wired via Antigravity

**Steps —**

- Determine the project’s category (Wind, Solar, Wind-Solar Hybrid, BESS, or Wind-Solar-BESS) from the intake form; this selects which subset of the 20 benchmark rationales Gemini should reference for structure and phrasing.

- Use the rationale prompt from the Appendix. Feed it the scorecard output (from the engine), the CORE-cited passages (Tier 1), relevant Crisil sector-report context (Tier 2), and the category-matched benchmark rationale excerpts (Tier 3, style only).

- Confirm it writes in agency style, cites CORE sections for every scored claim, attributes sector-context statements to the Crisil report, invents no numbers, draws no numbers or issuer facts from the benchmark rationales, and includes the indicative/academic disclaimer.

- In Antigravity: ‘After scoring, call Gemini with the rationale prompt, the project’s category, and the three-tier grounding context, then save the rationale and its citations to Firestore.’

**Expected output — A** drafted rationale with citations, sector context, and category-appropriate style — saved per assessment.

**Validation — Every** factual claim traces to a scorecard number or a CORE-cited passage; every sector-context sentence traces to the Crisil report; no number or issuer fact traces to a benchmark rationale; the disclaimer is present.

**Common mistake — Letting** the rationale mention figures that are not in the scorecard, or letting a benchmark rationale’s numbers/facts bleed into the new draft. The prompt must forbid both.

**3.5 Generate the PDF report**

**Purpose — Produce** a clean, shareable report containing the rating, scores, explanation, citations, and disclaimer.

**Tool — Google** Apps Script (or a Python PDF library via Antigravity)

**Steps —**

- Create a Google Doc template with placeholders for rating, sub-scores, rationale, citations and disclaimer.

- In script.google.com, write (with Claude’s help) a short Apps Script that fills the template and exports a PDF — or ask Antigravity to generate the PDF in Python.

- Wire a ‘Download PDF’ action in the app.

**Expected output — A** one-click PDF containing all result elements.

**Validation — The** PDF shows the band, the four sub-scores out of their maxima, the rationale, citations, and the disclaimer.

**Common mistake —**** **A PDF that omits the disclaimer or the citations. Both must appear on every report.

## Day 4 — Full application, agentic workflow, and hosting

This is the heaviest day. If you can, give it extra time. Do the hosting step (4.5) in the morning, not at the end.

**4.1 Build the dashboard screens**

**Purpose — Assemble** the user journey into a clean set of screens.

**Tool — Antigravity**

**Steps —**

- Instruct Antigravity to create: Home / New Assessment, Upload, Review (validation), Results, and a Back-Test tab.

- For the Results screen, implement the display requirements at CORE §8.4 in full. Because a cap can separate the numeric score from the band, the screen must show **both** and must never present either alone:

- **Post-notching score** out of 115, displayed unchanged whether or not a cap applies.

- **Indicative band** implied by that score.

- **Final band** after caps.

- Where the two bands differ, a **mandatory cap notice** naming the trigger, in the form: *“**Band capped at [band] — [trigger]. Score-implied band was [band].**”*

- **Confidence badge** — High / Moderate / Low / Not Rated.

- The four block sub-scores against their maxima, and each notch applied with its source section.

- An explicit **“****Non-Investment Grade / Elevated Risk****”** flag on any band at or below BB.

- A **mandatory QA-agent review flag** on any band in the C or D range.

- The **BBB/BB boundary at 78 points visually distinguished** — it is the single most operationally important line in the band table.

- The **Null Register** wherever it is non-empty — field name, sub-factor affected, points forgone.

- Rating Drivers (ticks) and Rating Constraints (bullets); a Sensitivity line; the rationale with expandable citations; the Assumptions and Limitations block; and any Warn-level validation results from CORE §10.1.

- Where the engine returns “Insufficient Input — Not Rated”, the Results screen shows the named missing critical fields and **no band** — not a band with a low-confidence badge.

**Expected output — A** connected set of screens following the user journey.

**Validation — You** can move Home → Upload → Review → Results without dead ends.

**Common mistake — Over**-designing. Clean and legible beats elaborate.

**4.2 Assemble the agentic workflow**

**Purpose — Chain** the steps so one action runs the whole pipeline: extract → validate → score → ground → draft → QA → report.

**Tool — Antigravity** + Gemini API

**Steps —**

- Instruct Antigravity to orchestrate the sequence as one flow triggered by ‘Assess project’.

- Ensure the Python engine does the scoring step and Gemini only does extraction, grounding and drafting.

**Expected output — A** single ‘Assess’ action that runs end to end and shows progress states.

**Validation — Pressing** Assess on a test project produces a band, rationale and PDF without manual hand-offs.

**Common mistake — Letting** the workflow call an AI for the score. Route scoring through the Python engine only.

**4.3 Add the QA agent**

**Purpose — Automatically** catch problems before the user sees the result — missing values, maths that does not add up, claims with no citation.

**Tool — Antigravity** + Gemini API

**Steps —**

- Instruct Antigravity: ‘Before showing results, run the **thirteen input validation rules** at Core Rating Criteria v3.0 Section 10.1, in the pipeline position fixed by Section 10.1.1, plus checks for AI statements without a citation, and flag anything failing.’ The thirteen are: **V1** average DSCR not below minimum DSCR; **V2** PLCR not below LLCR; **V3** offtaker shares summing to 1.0000 ± 0.0100 across the four individual lines and the aggregated line; **V6** the two CFADS routes agreeing within 2% **in every period, tested period by period**; **V7** encumbered DSRA not exceeding total DSRA; **V7a** encumbered other cash not exceeding total other cash; **V8** minimum DSCR below 1.00x with PLCR at or above 2.00x; **V8a** minimum DSCR scoring 0 without the coverage floor triggering; **V9** nil or negative tangible net worth; **V11** an operating project’s COD not later than the calculation date; **V12** any stale offtaker rating, discount rate or ALMM parameter; **V13** technology type and calculation date agreeing across the two templates; **V14** every instrument with an amount carrying a Debt or Equity treatment.

- **Four engine assertions (A1–A4) are separate and must not appear on this screen.** They test the engine’s own arithmetic — sub-scores summing to the raw score, no block exceeding its maximum, the merchant shift actually present in the lookups used, and a binding cap leaving the score unaltered. A failure is an implementation defect and must halt the response, not be shown to the user as a data problem they could correct. *v2.0 of this manual listed twelve rules with these three mixed in, which implied a user could clear them by editing inputs. They cannot (QA finding m7).*

- **A rule runs only where every operand it needs is populated.** Otherwise it returns **`Not Evaluated`**, which is the fourth validation outcome alongside Pass, Warn and Block, and which does **not** itself reduce confidence — the underlying null already does (CORE §10.1.1).

- Distinguish **Block** from **Warn** in the display. A Block failure means the pipeline stopped before scoring and there is no result to show; a Warn failure accompanies a result.

- Show any flags on the Results screen.

**Expected output —**** **A QA step that flags issues on each assessment.

**Validation — Feed** it a project with a deliberately missing input; the QA agent flags it.

**Common mistake — Treating** QA as optional. It is your automated reviewer and a strong point for evaluators.

**4.4 Wire in confidence and sensitivity display**

**Purpose — Show** the confidence level and the sensitivity line computed by the engine on Day 1.

**Tool — Antigravity**

**Steps —**

- Display the engine’s confidence output as a badge — High / Moderate / Low / **Not Rated**. The fourth state is new in v2.0 and arises where a critical input is null (CORE §9.8.1).

- Display the sensitivity result as a line, e.g. ‘DSCR below 1.20x → rating may reduce to BBB’.

- Where confidence is Moderate or Low, display the **reason** alongside the badge, drawn from the engine’s own determination: proximity to a band edge (with the distance in points), the count of nulls, a **binding** cap, or a stale input. A badge without a reason invites the user to discount it.

**Expected output — Confidence** badge with its reason, and the sensitivity line, on the Results screen.

**Validation — Feed** the engine a project whose post-notching score sits 2.0 points from a band edge; it must return Moderate, with proximity named as the reason, because CORE §9.8.3 sets N = 3.0 points. Feed it the same project moved to 4.0 points from the edge; it must return High. Feed it a project with a Weak offtaker **whose indicative band is above BB** — reference project TP-4 is exactly this case; it must return Moderate on account of the **binding** cap, regardless of distance. Then feed it TP-3, which trips two caps that do **not** lower its band because the indicative band is already D: it must return **High**. A cap that is triggered but not binding must not reduce confidence (QA finding M3).

**Common mistake — Hard**-coding ‘High’, or treating confidence as a presentational nicety. Confidence is a computed output of the rule at CORE §9.8.3 with a stated numeric window, and it is user-visible — Template 1 promises the user that a blank field will affect it, so it cannot be quietly dropped.

**4.5 Deploy (front-end and Python engine)**

**Purpose — Put** the app online so it can be demonstrated and submitted.

**Tool — Antigravity** → Firebase Hosting + Google Cloud Run

**Steps —**

- Instruct Antigravity: ‘Deploy the Python FastAPI engine to Google Cloud Run, deploy the web app as a PWA to Firebase Hosting, and connect the app to the Cloud Run URL.’

- Ask it to set the Gemini key as a server-side secret and to allow the app’s web address to call the engine (CORS).

- Open the live web address and run one full assessment.

**Expected output — A** live web address where the full app works end to end.

**Validation — On** the live site you complete Upload → Review → Results → PDF successfully.

**Common mistake — Trying** to host the Python engine on Firebase Hosting. It must go to Cloud Run; the front-end goes to Hosting.

## Day 5 — Back-test, testing, documentation, and submission

**5.1 Back-test against known ratings**

**Purpose — Establish whether the tool is DIRECTIONALLY sound** by comparing its output to real published ratings.

*Reframed in v3.0 (QA finding m16). v2.0 of this manual described this activity as the project's "proof that it works" and set a target of "most cases within about one notch". A back-test on 8 to 10 projects cannot bear that weight. CORE Section 11 lists **nine** Developer calibrations — the PLCR/LLCR thresholds, the solar and hybrid DSCR sets, the 25% dominance threshold, the bullet-share definitions, the contingency threshold, the reinvestment bands, the operator and sponsor thresholds, and the N = 3.0-point confidence window — and nine parameters cannot be fitted to ten observations without overfitting. **Those calibrations remain provisional after the back-test, and the back-test must say so.**

What a set this size can establish is worth having, and it is what to report: whether the framework lands in the **right region** of the scale; whether its errors are **systematically** in one direction, which would indicate a calibration bias rather than noise; and whether any single project is off by more than one **rating category**, which would indicate a mechanic that is wrong rather than merely untuned. Report those three things. Do not report a headline accuracy percentage, and do not adjust a calibration on the strength of this evidence.*

**Tool — The** app + published agency rationales

**Steps —**

- Pick **8 to 10** renewable projects whose ratings are public, drawn from the Tier 3 rationales in the reference corpus. *v2.0 said 3–5. With nine provisional calibrations, three observations cannot distinguish a systematic bias from a single unusual project, and the corpus holds twenty rationales, so the larger set costs nothing but time.*

- **Keep the set disjoint from the eight reference projects** in Key Input Template 2. Those are hand-built fixtures for unit-testing the mechanics; using them here would test the engine against its own specification rather than against the market.

- Enter each into the simulator and record its indicative band.

- Compare with the published rating and record the difference in **rating categories** — that is, steps on the AAA-to-D band scale of CORE §8.2, such as A to BBB. **Do not report the difference in "notches".** In this framework a notch is a fixed 7-point deduction (CORE §7); in conventional rating usage it is one step on the alphanumeric scale. They are different units: a CORE band spans between 8 and 22 points and covers roughly three conventional notches, so a −2-notch deduction here is about one and a half **bands**. A back-test reporting "within one notch" without saying which unit it means is not interpretable (QA finding m5).

- Summarise as **three** findings, not one: (a) the distribution of differences in **rating categories** — how many exact, how many one category out, how many two or more; (b) the **signed mean** difference, which tests for systematic optimism or pessimism; and (c) any project off by two or more categories, examined individually for the mechanic responsible.

**Expected output — A** back-test table: project, published rating, agency and date, indicative band, final band, whether a cap was **binding**, and the difference in **rating categories** (signed). Plus the three findings above, and an explicit statement that the nine CORE Section 11 calibrations remain provisional.

**Validation — Most** cases land within one **rating category**, the signed mean is close to zero rather than consistently one-sided, and every case two or more categories out has a named cause. A one-sided mean is the interesting result, not a failure: it says the scale is offset, which is a calibration finding worth recording in Section 11 even though this sample is too small to act on.

**Common mistake — Two,** and the second is the more tempting. First, using the same projects you used to tune the weights, or the eight reference fixtures — keep the back-test set disjoint. Second, **tuning a calibration to close a gap the back-test reveals.** With nine free parameters and ten observations, any gap can be closed, and closing it proves nothing. Record the gap; leave the parameter.

**5.2 End-to-end and prompt refinement**

**Purpose — Confirm** the whole journey works and tighten the prompts.

**Tool — The** live app + Google AI Studio

**Steps —**

- Run several projects through the live app end to end.

- Where extraction, grounding, rationale or QA underperforms, refine that prompt in AI Studio and redeploy.

- Re-run identical inputs to confirm results are stable.

**Expected output — A** stable, working end-to-end app and refined prompts.

**Validation — The** same input gives the same result on repeat runs.

**Common mistake — Endless** prompt tweaking. Stop when outputs are correct and stable.

**5.3 Write the documentation**

**Purpose — Prepare** the written materials the submission requires.

**Tool — Google** Docs / Markdown (Claude to help draft)

**Steps —**

- Prepare: a short User Guide, the Technical Architecture, the AI Workflow diagram, the Assumptions and Limitations, and Future Enhancements.

- Keep the Project Summary Document concise: problem, solution, how it works, impact, and the disclaimer.

**Expected output — A** documentation set including the Project Summary Document.

**Validation — A** reader who has never seen the tool understands what it does and its limits.

**Common mistake — Skipping** the summary document — it is part of the required ZIP.

**5.4 Package, record, and submit**

**Purpose — Assemble** the ICAI submission exactly as required.

**Tool — File** manager, screen recorder, ICAI AI Hub

**Steps —**

- Assemble a single ZIP (under 200 MB) containing: the Project Summary Document, the prompt files, example files and sample data, and the executable/code.

- Record a demonstration video showing your face and your screen walking through the tool; upload it unlisted to YouTube or Google Drive and keep the link accessible.

- Prepare the 4-slide capstone deck (Problem, Technology Solution, Implementation Plan, Conclusion).

- Push the final code to GitHub.

- Upload the ZIP to the ICAI AI Hub (ai.icai.org/ai_hub.php) and confirm you receive the upload confirmation.

**Expected output — A** submitted capstone: ZIP on the AI Hub, video link, slides, GitHub repo.

**Validation — The** AI Hub shows your upload confirmation, and the video link opens.

**Common mistake — A** ZIP over 200 MB, or a video without your face — both fail the ICAI requirements.

# G. Expected Deliverables

| Day | Deliverables |
| --- | --- |
| Day 0 | All accounts created; tools installed; Firestore, Storage, Auth enabled; Blaze plan on |
| Day 1 | Scorecard document (CORE v2.0); JSON schema with canonical enums, validation rules and Null Register; tested Python engine implementing the CORE §8.1 order of operations; engine exposed as an API |
| Day 2 | Upload module; tested extraction prompt; extraction wired to Firestore; validation screen |
| Day 3 | Three-tier corpus loaded (CORE criteria, Crisil sector report, category-tagged benchmark rationales); factor-to-section mapping adopted from CORE Section 12; grounding; cited, sector-contextualised, category-styled rationale; PDF report |
| Day 4 | Full dashboard; agentic workflow; QA agent; confidence and sensitivity; deployed live app |
| Day 5 | Back-test results; end-to-end tested app; documentation; ZIP, video, slides; AI Hub submission |

# H. Quality Checks and Validation Steps

Run these confirmations as you go. If any fails, fix it before moving on.

- **Engine correctness:** each of the three hand-calculated projects on Template 2’s ‘Test Projects’ sheet matches the engine’s sub-scores, raw score, notches, post-notching score, indicative band, final band and confidence level exactly.

- **Determinism standard (CORE §0.2):** a competent reviewer working from CORE v2.0 alone reaches the same score, band **and confidence level** as the engine. This is the acceptance test for the criteria document, not just for the code.

- **Boundary completeness:** no reachable value of any scored input fails to map to a tier, and no reachable score fails to map to a band. Test the half-point scores and every threshold value in Sections 4 and 5.

- **Cap independence (CORE assertion A4):** where a cap **binds**, the reported numeric score is identical to the score reported for the same project without the cap. A cap must never move the number. Reference projects TP-1 and TP-4 are identical in every input except the offtaker rating, so this assertion is directly testable: both must report a post-notching score computed the same way, with TP-4 differing only by the −14-point offtaker notch and the cap notice.

- **Technology-set selection:** the same cash-flow profile submitted as wind, solar and hybrid produces three different Block B scores.

- **Non-overlap:** a weak offtaker is penalised once, at §7.1. A pre-COD project is penalised once, at §7.3. Change one offtaker rating and confirm only the notch moves, not any Block A sub-score.

- **Edge cases:** missing critical input, missing non-critical input, extreme gearing, nil tangible net worth, and an on-the-boundary score all behave as CORE specifies.

- **Extraction accuracy:** for a document with known figures, every extracted number is right and missing items are null.

- **Human check present:** every assessment passes through the editable validation screen before scoring.

- **Grounding precision:** each cited passage genuinely governs the factor it is attached to, per CORE Section 12 — and where Section 12 records a **[Developer calibration]** rather than a published source, the rationale says so rather than implying agency authority. CORE v2.0 withdrew one attribution outright (the offtaker-dependence threshold) because the threshold was changed on the Developer’s own judgment; the drafted rationale must not reinstate it.

- **Rationale integrity:** no number appears in the rationale that is not in the scorecard; every sector-context statement is attributed to the Crisil report; no number or issuer-specific fact from a benchmark rationale appears in the draft; the disclaimer is always present.

- **QA agent works:** a deliberately flawed project is flagged.

- **Confidence is derived:** a project within 3.0 points of a band edge shows Moderate, not High, per CORE §9.8.3; a project missing a critical input shows Not Rated and no band.

- **Live end-to-end:** on the deployed site, Upload → Review → Results → PDF completes without error.

- **Back-test:** most known-rated projects land within about one notch, and exceptions are explainable.

- **Reproducibility:** identical inputs produce identical results on repeat runs.

# I. Risks and Mitigation

| Risk | Why it matters for you | Mitigation |
| --- | --- | --- |
| Skipping setup (Day 0) | Day 1 stalls on missing keys/accounts | Complete Day 0 fully; verify each service before Day 1 |
| Hosting the Python engine wrongly | Firebase Hosting cannot run FastAPI; deploy fails on Day 5 | Engine to Cloud Run, front-end to Hosting; do this on Day 4 morning; enable Blaze on Day 0 |
| 5-day compression | Day 4 and 5 are overloaded for one non-developer | Use the 10-day window if possible; protect the critical path; make auth minimal, skip CI |
| API key exposed in the browser | Anyone could use your key and run up cost | Store the key as a server-side secret; never in front-end code |
| Billing surprise | Unexpected cloud charges | Stay within free allowances; set a Firebase budget alert; the capstone load is tiny |
| Extraction errors on scans | Wrong numbers → wrong rating | Editable validation screen; null-not-guess prompt; correct before scoring |
| Criteria drift between CORE and the templates | The engine scores a field the template no longer collects, or vice versa | CORE §0.1 lists the three downstream documents that must move in step; re-run the cross-document check at H whenever any one of the four changes |
| Implementer discretion filling a criteria gap | Two builds of the same document produce different ratings | Every tier in CORE v2.0 is a single-sided threshold at a stated precision; if a rule still needs a judgment call, that is a defect in CORE, not a decision for Antigravity — raise it and amend the document |
| Stale regulatory parameter scored silently | An ALMM-driven score computed on a superseded notification | CORE §3.3.3 holds ALMM as a dated configuration table with a 90-day staleness rule that downgrades confidence; never hard-code the values into engine logic |
| Corpus file lost to a filename collision | Two rationales in the folder differed only in capitalisation, and on a case-insensitive filesystem one silently overwrote the other. This had already happened once — it is why this manual said “7 solar rationales” in two places and “Solar (8)” in a third | Both files renamed to encode agency and date (applied 30 July 2026); corpus keyed by content hash in Reference_Corpus_Manifest_v2.0.csv; run corpus_remediate.py --verify after any clone or re-download, since restoring from the original source reintroduces the collision |
| Corpus opened with a PDF library | Every .pdf in the folder is a ZIP of per-page JPEGs and OCR text; a PDF parser fails on all 41 | Follow the six-rule ingestion contract at Activity 3.1; validate with the manifest’s container column before ingesting |
| AI inventing numbers in the rationale | Undermines credibility | Numbers only from the Python engine; rationale prompt forbids new figures; QA agent checks citations |
| Back-test set reused from tuning | Looks accurate but is not a fair test | Keep back-test projects separate from the ones used to set weights |
| Over-claiming vs a real agency | Governance/ethics issue | Indicative/academic disclaimer on every result and PDF; positioned as pre-agency |
| Submission format errors | Certificate not generated | ZIP under 200 MB with all required files; video shows your face; confirm AI Hub upload |

# J. Final Project Completion Checklist

- All accounts and tools set up and verified (Day 0); Blaze plan enabled

- Scorecard, weights, band map and notching documented

- JSON schema covers every scored factor

- Python engine returns post-notching score, indicative band, final band, cap trigger, sub-scores, notches with sources, confidence, Null Register, drivers, constraints, sensitivity

- Engine exposed as a FastAPI service; unit tests pass (including edge cases)

- Upload module stores files in Firebase Storage

- Extraction prompt tested; returns null for missing items; wired to Firestore

- Editable validation screen in place and used before scoring

- Methodology corpus collected, deduplicated and collision-free (corpus_remediate.py --verify reports zero collisions); corpus manifest present and content hashes verified; factor-to-section mapping done; grounding tested

- Rationale generated with citations and disclaimer; no invented numbers

- PDF report includes band, sub-scores, rationale, citations, disclaimer

- Dashboard screens connected; agentic ‘Assess’ workflow runs end to end

- QA agent flags missing/inconsistent/uncited items

- Confidence badge (High / Moderate / Low / Not Rated) with its reason, and the sensitivity line, derived by the engine and displayed

- Results screen shows post-notching score, indicative band, final band and — where they differ — the mandatory cap notice

- Null Register displayed wherever non-empty; the 78-point investment-grade line visually distinguished

- All twelve CORE §10.1 validation rules implemented, with Block failures stopping the pipeline before scoring

- Python engine deployed to Cloud Run; web app deployed to Firebase Hosting; connected; Gemini key server-side; CORS set

- Back-test on 3–5 known-rated projects with an accuracy summary

- End-to-end tested on the live site; results reproducible

- Documentation set prepared, including the Project Summary Document

- Single ZIP (<200 MB): summary, prompts, examples, sample data, code

- Demonstration video (face + screen) recorded and uploaded unlisted; link works

- 4-slide capstone deck prepared; final code pushed to GitHub

- ZIP uploaded to ICAI AI Hub; upload confirmation received

# Final Readiness Assessment

**Overall verdict:** the plan and your 5-day timeline are coherent and closely aligned, and the project is executable by a non-developer using Antigravity — provided three things are fixed before you start. With those in place, this is a realistic, well-scoped capstone.

**Green — ready as designed**

- The overall approach is sound: deterministic Python for the numbers, Gemini for reading and drafting, lightweight grounding instead of a database.

- Your timeline faithfully implements the plan and adds two genuine improvements: an explicit QA agent and a governance-oriented explainability screen.

- The critical path (engine, grounded rationale, back-test) is clear and defensible.

**Amber — fix before you start**

- **Adopt CORE v2.0, not v1.0.** The v1.0 criteria carried nine blocking defects that would have produced either a crash, a silently wrong band, or a band no two implementers would agree on. They are resolved in v2.0 (CORE Section 13), and the templates and this manual have been amended in step. Build from v2.0 and confirm all four documents carry the 30 July 2026 issue date before Antigravity encodes anything.

- **Add Day 0 setup.** Accounts, keys, and Firebase services are prerequisites the original timeline omits.

- **Correct the hosting path.** The Python engine goes to Cloud Run, not Firebase Hosting; enable the Blaze plan on Day 0 so this works.

- **Wrap the engine as an API on Day 1–2**, and specify how confidence and sensitivity are computed — otherwise Day 4 has gaps to improvise.

**Red — the main risk to manage**

- **The 5-day compression.** Day 4 (full app + workflow + QA + hosting) and Day 5 (back-test + testing + docs + deploy + video + slides) are each overloaded for one non-developer. You have a 10-day ICAI window — use it if you can, and if time runs short, thin the dashboard, keep authentication minimal, and skip continuous integration, but never cut the engine, the grounding, or the back-test.

**Bottom line:** proceed. Insert Day 0, fix the hosting path, build the API early, and give yourself more than five days if the window allows. Judgement on the finance logic is yours; let Antigravity handle the code and deployment and keep Claude open for prompts and troubleshooting.

# Change Log — v2.0 to v3.0

*This manual is reissued at v3.0 alongside Core Rating Criteria v3.0, Key Input Template 1 v3.0, Key Input Template 2 v3.0, Reference Corpus Manifest v3.0 and the Reference Corpus Hygiene and Ingestion Specification v3.0. All six documents carry a single date, 30 July 2026, so the alignment set is unambiguous — the version breach at QA finding M16, where a v2.0 workbook carried a v3.0 change log inside it and neither document acknowledged the other, is closed by reissuing the whole set rather than by patching one member of it.*

| Ref | Change | Activity |
| --- | --- | --- |
| **M3** | "Binding" restored to the confidence rule in both places, and to the Results screen and the cap-independence assertion. v2.0 of this manual dropped the word from CORE §9.8.3, which is not academic: reference project TP-3 trips two caps, neither of which lowers its band, and its published expected confidence is **High**. An engine built to the v2.0 wording would return Moderate and fail its own acceptance test. | 1.3, 4.4, 4.7, H |
| **M15, B3** | The reference-project set is extended from three to eight, with a table stating what each exists to test, and Activity 1.5's false claim that the three projects "each carr[y] its full input set" is corrected — they did not, so the acceptance test could not be executed from the sheet. The new **Test Project Inputs** sheet carries the input sets; every expected output is derived from them. | 1.5, 2.4 |
| **Ingestion** | *(Superseded 31 July 2026 — the corpus is now uniformly PDF; see Activity 3.1. The entry below records the position as first issued.)* The contract is rewritten for a **mixed-format corpus**: 37 ZIP containers and 4 genuine PDFs. v2.0 stated that all 41 files were ZIP archives and none was a PDF. That was true of the corpus as assembled, but the four files renamed during remediation were re-supplied in PDF form, so a pipeline built on the v2.0 contract fails on exactly those four — silently, reading as corruption, which is the failure mode the contract exists to prevent. Code must now **dispatch on the manifest's `container` column** and must never sniff or assume. | 3.1 |
| **m4** | Methodology count corrected from 21 to **20 distinct** documents, with the Fitch duplication and the seven Criteria Extension-scope documents explained. | 1.1 |
| **m5, m16** | The back-test is restated in **rating categories**, not "notches". In this framework a notch is a fixed 7-point deduction; conventionally it is one step on the alphanumeric scale. A CORE band spans 8 to 22 points and covers roughly three conventional notches, so the two units differ by more than a factor of three and a back-test reporting "within one notch" is not interpretable. The back-test is also reframed as a **directional** accuracy check: nine Developer calibrations cannot be fitted to eight or ten observations without overfitting, so it validates direction and the sign of systematic error, not any specific threshold. | 5.1 |
| **B6** | The Day-2 engine instruction now opens with the **five-stage pipeline at CORE §10.1.1** — critical nulls, non-critical nulls, validation with `Not Evaluated`, scoring, engine assertions — rather than starting at the §8.1 order of operations, which is only Stage 4. v2.0 of this manual and CORE gave contradictory orderings for null resolution and validation. | 2.2 |
| **M8, M10** | Activity 1.2 now directs the developer to **CORE Appendices A and B** before writing the schema, and states that the engine matches on **code**, never on display text. v2.0 gave four illustrative field names in prose, left the other ninety-odd to be invented at build time, and simultaneously made Template 1's option strings authoritative while CORE claimed to be the single source of truth. | 1.2 |
| **B7** | The schema convention is stated explicitly: **every percentage is a decimal fraction**, 0.9700 for 97%, no field out of 100. | 1.2 |
| **m1** | Corpus counts stated consistently — 42 files as assembled, 41 after the Fitch duplicate is quarantined — and Activity 3.1's validation criteria extended to require that `corpus_manifest.py --verify` returns PASS, so a container mismatch or a hash mismatch stops the build rather than being discovered during grounding. | 3.1 |
| **1.2 sweep** | Six further bullets in Activity 1.2 corrected against v3.0: start from **Appendix B**, not §10.2 prose; take field names from Appendix B rather than the four wrong examples v2.0 offered (`avg_dscr` is not a field name); implement **all 27** Appendix A enumerations, not five, and `TIER_4` is withdrawn; match on **code**, not Template 1 display strings; the P90 **derivation route is withdrawn**; and there are **thirteen** V-rules plus four assertions with **four** outcomes, not twelve rules with two. Every one of these would have put a defect into the schema on Day 1. | 1.2 |
| **m11** | Companion documents are cited by **title and version** throughout, never by filename. Section 12 of CORE records why filenames in this project are not stable identifiers; that rule now applies to this manual's own cross-references. | throughout |

# Appendix — Ready-to-use prompts

Copy these into Google AI Studio and adapt the bracketed parts. Keep temperature low (around 0.1) for extraction and QA; a little higher (around 0.4) for the rationale. All three prompts below are updated for the three-tier reference architecture: Core Rating Criteria v3.0 **v2.0** (scoring), the Crisil Intelligence Indian Renewable Energy Report, Jan 2026 (sector narrative), and the 20 category-tagged benchmark rationales (style only). Section references in the prompts point to v2.0 numbering — note in particular that the non-double-counting rule moved from §9.5 to §9.7 and that §9.3, §9.6 and §9.8 are new (CORE §13.4).

**Extraction prompt**

| You are a financial-statement extraction engine. Read the attached document and return ONLY JSON matching this schema, which mirrors Core Rating Criteria v3.0 Section 10.2 (Required Inputs by Block): [paste your JSON schema]. Rules: Return null for any field not present. Never infer or estimate a number. Do not add fields that are not in the schema. Where a field is an enumerated selection, return the exact option string from Key Input Template 1 v3.0 or null — never a paraphrase. For each offtaker (up to four individually, plus an aggregated line), extract the type (C&I or DISCOM), the contracted revenue share, and the published rating or grade with its modifier, edition and date; if no date is present, still return the value but flag it as undated, and if a more recent edition is referenced anywhere in the document, flag the value as stale. For debt, itemise each instrument separately and return its stated terms — do not aggregate subordinated sponsor loans or compulsorily convertible debentures into a single total, since their equity treatment is decided by rule at CORE Section 9.3 and not by the extractor. For the DSRA, return the total balance and the encumbered portion as two separate fields. Return the P90 PLF and, separately, any statement in the document as to whether the cash-flow schedule was built on a P90 or P50 basis. Output JSON only, with no commentary. |
| --- |

**Rationale prompt**

| You are drafting an INDICATIVE, academic credit-rating rationale in the style of an Indian rating agency, for a project in this category: [Wind / Solar / Wind-Solar Hybrid / BESS / Wind-Solar-BESS]. Use the following four sources, and do not blend their roles: (1) SCORECARD — the engine’s output below is your only source of numbers, sub-scores, score, band, caps, and notching; never introduce a number not present here. Where the final band differs from the score-implied band because a cap was applied, state the cap and its trigger explicitly — do not present the capped band as though the score produced it, and do not present the score as though no cap applied. Where the confidence level is Moderate, Low or Not Rated, state the level and the engine’s stated reason. (2) METHODOLOGY CITATIONS — the passages below, each already mapped to a scored factor via Core Rating Criteria v3.0 Section 12; cite the specific section for every material scored point. Where Section 12 records a factor as a [Developer calibration] rather than a published source, describe it as an internal calibration and do not attribute it to any agency. Where a threshold set is a Developer calibration — the solar and hybrid DSCR sets in particular — say so. (3) SECTOR CONTEXT — the Crisil Intelligence Indian Renewable Energy Report passages below; use these only to frame the Business/Operating narrative (capacity trends, tariff trajectory, policy backdrop, DISCOM payment discipline), and attribute each such statement to the Crisil report. (4) STYLE REFERENCE — the category-matched benchmark rationale excerpts below are for structure and tone only; never copy a number, ratio, or issuer-specific fact from them into this draft. Structure: Rating summary; Key strengths; Key concerns; Rating drivers; Rating constraints; Rating sensitivities. Cite the CORE methodology section for each material scored point and the Crisil report for each sector-context statement. End with: ‘Indicative and academic. Not a substitute for a SEBI-registered credit rating.’ Scorecard: [paste engine output]. Methodology passages: [paste CORE-grounded passages]. Sector context: [paste Crisil report excerpts]. Style reference: [paste category-matched benchmark excerpts]. |
| --- |

**QA prompt**

| You are a QA reviewer. Given the scorecard output and the drafted rationale, list any problems: missing required inputs; sub-scores that do not sum to the overall score; a band inconsistent with the score after notching; any statement in the rationale that has no supporting number or CORE-cited passage; any factor described as agency-sourced where CORE Section 12 records it as a Developer calibration; any case where a band cap was applied but the rationale presents the final band as score-implied, or presents the score without noting the cap; any case where the confidence level is not High and the rationale does not say so; any sector-context statement not attributed to the Crisil report; any number, ratio, or issuer-specific fact that appears to have been drawn from a benchmark/style-reference rationale rather than this project’s own scorecard or inputs; missing rating sensitivities; a missing or altered disclaimer. Return a short list of flags, or ‘No issues found.’ |
| --- |

Credit Rating Simulator is an indicative, academic decision-support tool for internal pre-assessment. It does not reproduce or replace a rating agency’s opinion, and every output states this.