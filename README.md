# Credit Rating Simulator

**Live app:** https://credit-rating-simulator.web.app/

Gives an Indian renewable-energy project SPV (solar, wind or hybrid) an
**indicative** credit-rating band on an AAA–D scale, with a written rationale
grounded in published rating-agency methodology.

> "This is an indicative, academic assessment produced for an ICAI AICA Level 2
> capstone project. It is not a credit rating issued by a registered credit
> rating agency and must not be relied upon as one."
> — `MANDATORY_DISCLAIMER`, `app/rationale/draft.py`, attached to every scored
> result.

**Founding rule: numbers are computed by Python, never by a language model.**
Every score, band, notch and cap comes from the deterministic engine in
`app/engine/scoring.py`. The written rationale is also deterministic Python
string templating (`app/rationale/draft.py`) over that engine's output, not a
language-model call. Gemini's only role in this codebase is document
extraction — turning the uploaded Template 1 (`.docx`) / Template 2 (`.xlsx`)
pair into structured project JSON (`app/extraction.py`) — confirmed by grep:
`google.genai`/Gemini references exist only in `app/extraction.py` (plus the
upload endpoint in `app/main.py` that conditionally invokes it) and are
absent from both `app/engine/scoring.py` and `app/rationale/draft.py`.

## Status

Built and operational, not pre-build. The engine, the deterministic rationale
drafter, the Firestore persistence layer, and the review/approve/score/results
web flow are all written and exercised end to end. The codebase has been
through a runtime remediation and hardening pass on top of the initial v3.0
build — among other fixes: removal of fabricated placeholder values from the
rationale narrative, real citation verification against the source PDF corpus
(replacing several previously non-verbatim claims), a JSON-schema validation
gate on the real approval write path, and a Firestore write-path bug fix
(a `merge=True` write was silently leaving stale data behind on
re-approval). See `docs/Remediation_Log_v2_0_to_v3_0.md` (Section G) for the
full record.

Test suite: **62 passed** (`pytest -v`, run fresh against a live dev server,
2026-08-14).

## Method

A 115-point scorecard across four blocks — Business/Operating 35, Cash-flow 35,
Financial Strength 25, Structural Protections 20 — then downward-only notching,
a band map, and band caps. Criteria are synthesised from 20 distinct published
methodologies (CRISIL, ICRA, CARE, India Ratings, Fitch, Moody's, Brickwork).

## Layout

- `app/` — the FastAPI application.
  - `engine/scoring.py` — the deterministic scoring engine: block scores,
    notching, band mapping, caps, confidence.
  - `rationale/draft.py` — deterministic narrative drafting and methodology
    citation lookup for the scored result; no LLM call.
  - `extraction.py` — Gemini-based extraction of Template 1/2 into structured
    project JSON. The only place in the app that calls an LLM.
  - `grounding.py` — mechanically verifies rationale citations are genuine
    verbatim excerpts of the source PDFs in `corpus/`.
  - `pipeline.py` — orchestrates Score → Draft → Ground → QA → Report/Persist
    on approval.
  - `firestore.py` — Cloud Firestore persistence (with a local-JSON-file
    fallback), field provenance, and the schema-validation gate on approval.
  - `main.py`, `pdf.py`, `storage.py`, `labels.py` — HTTP routes, PDF report
    generation, file storage, display-label formatting.
  - `templates/` — the four HTML screens (upload, review, results, home).
- `public/` — generated static mirror of `app/templates/` for PWA hosting
  (regenerated via `scratch/prepare_pwa.py`), plus the manifest, service
  worker, and icons.
- `corpus/` — the reference PDF methodology corpus that citations are
  verified against, its manifest CSVs, and maintenance scripts
  (`corpus_manifest.py`, `corpus_textcheck.py`, etc.).
- `docs/` — the governing CORE Rating Criteria document, the input template
  files, the execution manual, and the remediation log.
- `schemas/` — `project.schema.json` (the JSON Schema all approved project
  data is validated against) and `display_labels.json`.
- `tests/` — `pytest` suite (unit, API, and Playwright browser tests) plus
  `tests/conftest.py` and the reference-project fixture set.
- `scratch/` — small ad-hoc maintenance/diagnostic scripts, not part of the
  application itself.

## Testing

```
pip install -r requirements.txt
playwright install chromium
```

`pip install -r requirements.txt` installs `playwright`, but the browser
binary itself is a separate one-time step (`playwright install chromium`).
Run without it and the Playwright-based tests in `tests/test_api.py` will
fail to launch a browser.

No Firebase or Gemini credentials are required to run the suite: `pytest`
automatically sets `PYTEST_CURRENT_TEST`, which `app/firestore.py` checks
before touching real Firestore and routes both reads and writes to a local
JSON fallback instead — a test run never touches production data, with or
without real credentials configured. (`CRS_FORCE_LOCAL_FIRESTORE` is the same
guard for ad-hoc scripts run outside `pytest`.)

A handful of tests (e.g. `test_results_screen_rendered_playwright`) drive a
headless browser against a live server at `http://127.0.0.1:8000`, so start
the app in a separate terminal first:

```
uvicorn app.main:app --reload
```

Then run the suite:

```
pytest -v
```
