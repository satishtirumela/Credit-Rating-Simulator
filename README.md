# Credit Rating Simulator

Gives an Indian renewable-energy project-finance SPV (solar, wind or hybrid) an
**indicative** credit-rating band on an AAA–D scale, with a written rationale
grounded in published rating-agency methodology.

> **Indicative and academic. Not a substitute for a SEBI-registered credit rating.**
> This is an ICAI AICA Level 2 capstone. It is not a credit-rating agency, it is not
> registered with SEBI, and nothing it outputs is a credit opinion.

**Founding rule: numbers are computed by Python, never by a language model.**
Gemini extracts fields and drafts prose. Every score, band, notch and cap comes
from the deterministic engine in `app/engine/`.

## Status

Pre-build. The v3.0 governing document set is approved and frozen; the engine is
not yet written.

## Method

A 115-point scorecard across four blocks — Business/Operating 35, Cash-flow 35,
Financial Strength 25, Structural Protections 20 — then downward-only notching,
a band map, and band caps. Criteria are synthesised from 20 distinct published
methodologies (CRISIL, ICRA, CARE, India Ratings, Fitch, Moody's, Brickwork).

## Layout
