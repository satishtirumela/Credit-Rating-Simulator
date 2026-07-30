# Reference Corpus Hygiene and Ingestion Specification

**Version 3.0 — 30 July 2026**

*Supersedes v2.0 (30 July 2026) and v1.0. Aligned to Core Rating Criteria v3.0, Key Input Template 1 v3.0, Key Input Template 2 v3.0, Credit Rating Simulator Execution Manual v3.0, and Reference Corpus Manifest v3.0.*

| Attribute | Value |
| --- | --- |
| Purpose | To state what the reference corpus actually is, what was wrong with it, what was done, and the contract any ingestion code must honour |
| Audit basis | All 42 files in the reference folder as originally assembled were opened and inspected; content hashed at payload level; publication dates and issuing agencies extracted from page-1 text. Re-audited on 30 July 2026 against the folder as remediated: 41 files |
| Authoritative index | Reference Corpus Manifest v3.0 (`Reference_Corpus_Manifest_v3_0.csv`), 41 rows, 18 columns |
| Generator and verifier | `corpus_manifest.py` v3.0 |
| Verification state | `corpus_manifest.py --verify` returns **PASS**: 41 of 41 files resolve to a manifest row, 41 of 41 payload hashes match, 0 case-insensitive collisions |
| Owner | Developer (CA. Satish Tirumela) |

---

# 0. What changed in v3.0, and why it matters

v2.0 of this specification described a remediation that had been designed but not applied. The remediation has since been applied — by hand, under a different naming convention from the one the script targeted, and with four documents re-supplied in a different file format. Three consequences followed, none of them visible from any single document, and all three are corrected here.

**(a) The corpus is no longer uniformly ZIP.** v2.0's central factual claim was that *all 42 files carrying a .pdf extension begin with the byte signature 50 4B 03 04, and none begins with %PDF.* As at 30 July 2026 that is **false for four files**. Those four are genuine PDFs. Any pipeline built on the v2.0 contract — "Open each file as a ZIP archive" — now fails on exactly those four, and fails in the way the contract was written to prevent: silently, reading as file corruption rather than as a format mismatch.

**(b) The manifest no longer matched the folder.** The four renames were applied under a shorter naming convention (`ReNew_Solar_Power_Private_Limited_IndRa_Solar.pdf`) than the script's targets (`ReNew_Solar_Power_Private_Limited_IndiaRatings_2026-03_Solar.pdf`). The v2.0 manifest carried the script's intended names. The result: `corpus_remediate.py --verify` reported **4 BLOCKED**, the manifest listed four filenames that did not exist and omitted four that did, and only 37 of 41 files verified by hash. The remediation had in substance succeeded — the case collision was gone, the typos were fixed — and the verification tooling reported failure anyway, which is worse than no tooling, because it trains the operator to ignore it.

**(c) Three publication dates in the manifest were impossible.** v2.0 §6.4 stated that exactly one publication date was known to be wrong (the Fitch global criteria document, where a page-1 revision history defeats the heuristic). In fact the manifest also carried **December 23, 2038**, **March 2027** and **30 June 2045**. The cause is structural rather than incidental and is set out at Section 5.2.

**The design lesson, recorded because it generalises.** A tool whose purpose is to protect against unstable filenames must not itself depend on them. v2.0's script keyed its work on a hard-coded table of old and new names, so the moment a human applied the same substantive change under different names, the tool could not recognise its own success. v3.0 replaces that design: the folder as it stands is the input, the manifest is a **regenerated** artefact rather than a hand-maintained one, and verification compares content hashes rather than names.

---

# 1. Element (c) — the case-collision filenames

The most consequential defect, and the one that had already destroyed data.

| Filename as assembled | Agency | Date | Pages | Rating action |
| --- | --- | --- | --- | --- |
| `ReNew_Solar_Power_Private_Limited_Solar.pdf` | India Ratings (Ind-Ra) | 31 March 2026 | 6 | Downgrade to IND A, Outlook Negative |
| `Renew_Solar_Power_Private_Limited_Solar.pdf` | CARE Ratings | 8 April 2026 | 12 | CARE A; Stable — assigned and reaffirmed |

Two different agencies, two different dates, two different rating actions, one capital letter apart. On any case-insensitive filesystem — Windows, and macOS in its default configuration — a clone, a re-download, or an unzip silently keeps one and destroys the other. The loss is invisible: no error, no warning, just nineteen rationales where there were twenty.

**This had already happened.** The Execution Manual v2.0 stated the Tier-3 corpus as "Solar (8)" in its Activity 3.1 breakdown and as "the 7 solar rationales" in its reference-architecture section and again in Activity 3.3. Eight is the count on a case-sensitive listing. Seven is the count after a case-insensitive checkout has eaten one file. The two numbers were written at different times from different views of the same folder.

**Resolved.** The files now stand as:

| Current filename | Agency | Container |
| --- | --- | --- |
| `ReNew_Solar_Power_Private_Limited_IndRa_Solar.pdf` | India Ratings | PDF |
| `Renew_Solar_Power_Private_Limited_CARE_Solar.pdf` | CARE Ratings | PDF |

They differ by five characters, not one. `corpus_manifest.py --verify` confirms **0 case-insensitive collisions** across the folder.

*A note on the residual cosmetic inconsistency: one file begins `ReNew` and the other `Renew`. This is untidy but no longer dangerous, and it is deliberately left alone. Renaming a third time to harmonise the capitalisation would invalidate the manifest again for no gain in safety, and the manifest keys on content hash rather than filename precisely so that cosmetic naming does not matter.*

---

# 2. Element (a) — container format: the corpus is MIXED

**Confirmed, and the finding has changed since v2.0.**

| Container | Count | Signature | Structure |
| --- | --- | --- | --- |
| ZIP | **37** | `50 4B 03 04` (`PK\x03\x04`) | One JPEG and one `.txt` OCR file per page, plus `manifest.json` carrying `num_pages` |
| PDF | **4** | `25 50 44 46` (`%PDF`) | Ordinary PDF with a text layer |

The four PDFs are the four files touched by the remediation: the two ReNew rationales above, `CARE_Criteria_Consolidation_Combined_Approach_07_March_2025.pdf`, and `India_Ratings_Criteria_Infrastructure_Project_Finance_27_May_2024.pdf`.

**Consequence if unaddressed, in both directions.** A pipeline built on any PDF library — pypdf, pdfplumber, PyMuPDF, or a Gemini file upload declared as `application/pdf` — fails on 37 of 41 files. A pipeline built on the v2.0 ZIP-only contract fails on the other 4. Neither failure raises a clean error; both read as file corruption. The Execution Manual's Day 3 grounding step is on the critical path and would meet one or the other on the first pass.

**The contract is therefore dispatch, not assumption.** See Section 4.

**Why the payload hash needed redefining.** For a ZIP container, hashing the sorted `.txt` and image entries gives a content identity that survives rename, filesystem move and ZIP re-compression, because container metadata is excluded. A PDF has no equivalent container/payload separation. Manufacturing one — extracting text and hashing that — would produce a hash dependent on the extraction library's version, which is worse than no abstraction at all. So for `container = PDF`, `payload_sha256` is **declared equal to** `file_sha256`, and the new `payload_basis` column records which rule was applied (`zip-entries` or `file`). The property being given up is stability across PDF re-compression; nothing in this project re-compresses PDFs, and the manifest says plainly which files have the weaker guarantee.

---

# 3. Element (b) — the duplicate methodology

| Filename | Payload hash | Status |
| --- | --- | --- |
| `Fitch_Ratings_Renewable_Energy_Rating_Criteria_Feb_2023.pdf` | identical | **Retained** — the dated filename carries the publication date |
| `Fitch_Ratings_Renewable_Energy_Criteria.pdf` | identical | **Quarantined** |

The two files were the same document: 26 of 26 OCR pages and every image byte-identical. The file-level checksum difference was ZIP container metadata only and carried no content. The document is Fitch's Renewable Energy Project Rating Criteria dated 7 February 2023 — which the longer filename says and the shorter one does not.

**This is why the distinct methodology count is 20, not 21.** Core Rating Criteria and the Execution Manual are both corrected at v3.0 to state 20. The folder as assembled held 21 methodology *files*; it held 20 methodology *documents*.

The quarantine is reversible by default. `corpus_remediate.py --delete-duplicates` removes the file outright, and refuses to do so unless it has re-proved, at that moment, that a byte-identical payload survives elsewhere in the folder.

---

# 4. The ingestion contract

**These rules are binding on every component that reads the corpus.** Four of them fail silently rather than raising, which is why they are stated as rules rather than left to be discovered.

## 4.1 Resolve through the manifest, and dispatch on `container`

**Read `Reference_Corpus_Manifest_v3_0.csv` first. Branch on the `container` column. Do not sniff the file, do not infer from the extension, do not assume either format.**

```
container == 'ZIP'  ->  open as zipfile; read per-page .txt entries for text,
                        per-page .jpeg entries for images, manifest.json for num_pages
container == 'PDF'  ->  open with a PDF library; use the text layer
```

**Key documents on `payload_sha256`, not on filename.** Filenames in this corpus have already proven unstable four separate ways: two collided on case alone, one methodology appeared twice under different names, two carried malformed dates, and four were renamed by hand under a convention no tool predicted. The payload hash is the stable identifier.

## 4.2 Do not declare a corpus file as `application/pdf` to any API

For the 37 ZIP files, a Gemini file upload so declared will be rejected or mis-parsed. Send the extracted per-page text, or the per-page images, not the container. For the 4 genuine PDFs the declaration is correct.

## 4.3 Text comes from the OCR entries, not from a PDF text layer

For ZIP files there is no text layer. Extraction means reading the `.txt` entries in page order. Page order requires numeric sorting of the entry names — a lexicographic sort puts page 10 before page 2.

## 4.4 Verify before the grounding step

Run:

```
python corpus_manifest.py --corpus <folder> --verify --manifest Reference_Corpus_Manifest_v3_0.csv
```

after any clone, re-download or unzip of the corpus, and before the Day 3 grounding step. It exits non-zero and names the problem if any file is missing, extra, changed in container, changed in payload, or in case-collision with another.

**A non-zero collision count means a file has been lost and the corpus must be restored, not worked around.** A container mismatch means a file has been re-supplied in a different format and the manifest must be regenerated, not edited. A payload mismatch means the content has changed and the reason must be established before proceeding.

## 4.5 Do not hand-edit the manifest

It is generated. Regenerate it:

```
python corpus_manifest.py --corpus <folder> --generate --out Reference_Corpus_Manifest_v3_0.csv --classifier classify.json
```

A hand-corrected value inside a generated column survives regeneration invisibly and misleads the next reader into trusting the whole column. Where a generated value is known to be wrong, it is **flagged** rather than corrected — see Section 5.2.

## 4.6 Tier discipline

| Tier | Count | Role | Rule |
| --- | --- | --- | --- |
| 1 | 20 | Methodology documents | The only source of criteria citations |
| 2 | 1 | CRISIL Intelligence sector report | Sector context only — capacity, tariff, policy, DISCOM discipline |
| 3 | 20 | Rating rationales | **Style and structure only. Never a source of numbers.** |

The Tier-3 rule is the one that will be broken accidentally. A benchmark rationale contains real ratios for a real issuer, and a rationale-drafting prompt that is shown one will reproduce its numbers if not explicitly forbidden. Core Rating Criteria Section 12 records that no Tier-3 document grounds any scored factor.

Tier 3 by category: Solar 8, Wind 4, Wind-Solar Hybrid 6, BESS 1, Wind-Solar-BESS 1.

---

# 5. The manifest

## 5.1 Columns

| Column | Meaning |
| --- | --- |
| `filename` | As on disk. **Not** a stable identifier. |
| `tier`, `category`, `agency` | Classification, carried forward through `--classifier` |
| `publication_date` | Resolved per Section 5.2 |
| `date_resolution` | The rule that produced it: `latest-not-future` or `unresolved` |
| `date_flag` | **New in v3.0.** Declares a known or suspected problem with the resolved date |
| `dates_on_page1` | Every date found on page 1, in order of appearance — the evidence for the resolution |
| `container` | `ZIP` or `PDF`. **The dispatch key.** New meaning in v3.0. |
| `payload_basis` | **New in v3.0.** `zip-entries` or `file` — which hashing rule was applied |
| `pages`, `ocr_text_pages`, `inner_manifest`, `bytes` | Structure and size |
| `flags` | `CONTAINER-NOT-PDF` for ZIP files; empty for genuine PDFs |
| `duplicate_group` | Populated where two files share a payload hash. **Currently empty for all 41 rows.** |
| `payload_sha256` | Content identity. The key to resolve documents on. |
| `file_sha256` | Whole-file hash |

## 5.2 Date resolution, and the three impossible dates

**v2.0's rule was: take the latest date found on page 1.** On a methodology document that is usually right — a criteria report's page 1 carries its own publication date and little else, and where it carries an earlier version's date too, the later one is correct. `CARE_Criteria_Consolidation_Combined_Approach_07_March_2025.pdf` shows both August 2022 and March 2025; taking the first would date a 2025 criteria document to 2022.

**On a rating rationale it is usually wrong**, because a rationale cites the PPA expiry and the final debt maturity, and those are decades ahead. v2.0's manifest consequently recorded:

| File | v2.0 resolved date | Why it was wrong |
| --- | --- | --- |
| `H_G__Banaskantha_Bess_Private_Limited_BESS.pdf` | December 23, 2038 | A contractual end date |
| `Juniper_Green_Bess_Zeta_Private_Limited_Wind__Solar__BESS.pdf` | March 2027 | A forward-looking reference |
| `ReNew_Sandur_Green_Energy_Private_Limited_Wind__Solar.pdf` | 30 June 2045 | A PPA expiry |

A 2045 publication date on a document in a folder audited in 2026 is not a subtle error, and v2.0 §6.4 asserted that exactly one date was known to be wrong. Three were impossible and a fourth was disputed.

**The v3.0 rule: `publication_date` is the latest date on page 1 that is not later than the audit date (30 July 2026).** It is regenerable, it states its own logic, and it fixes all three without hand-editing. Where future dates were discarded, `date_flag` records how many, so the discarding is visible rather than silent.

**Six dates changed as a result:**

| File | v2.0 | v3.0 |
| --- | --- | --- |
| `H_G__Banaskantha_Bess_Private_Limited_BESS.pdf` | December 23, 2038 | March 05, 2026 |
| `Juniper_Green_Bess_Zeta_Private_Limited_Wind__Solar__BESS.pdf` | March 2027 | May 29, 2025 |
| `ReNew_Sandur_Green_Energy_Private_Limited_Wind__Solar.pdf` | 30 June 2045 | Jun 19, 2025 |
| `Adani_Green_Energy_Twenty_Five_B_Limited_Wind__Solar.pdf` | December 2026 | June 2026 |
| `ICRA_Power_Solar_and_Wind_Rating_Methodology_July_2025.pdf` | March 31, 2025 | JULY 2025 |
| `Moodys_General_Project_Finance_Methodology.pdf` | June 2021 | JANUARY 12, 2022 |

The ICRA change is a straightforward improvement: the new value agrees with the filename, the old one did not.

## 5.3 The disputed-date register

Two documents carry a **revision history** on page 1, so the latest past date is a cross-reference rather than the publication date. The heuristic cannot distinguish these, and the correct response is to declare the dispute, not to patch the value:

| File | Resolved | Disputed because |
| --- | --- | --- |
| `Fitch_Ratings_Global_Infra__Project_Finance_Criteria.pdf` | 8 January 2025 | The criteria report itself is dated 17 May 2023 |
| `Moodys_General_Project_Finance_Methodology.pdf` | JANUARY 12, 2022 | Core Rating Criteria Section 12 cites this methodology as June 2021 |

Both carry `HEURISTIC-DISPUTED` in `date_flag`, naming the competing date. The `dates_on_page1` column exposes the full list in both cases. **Anything relying on the publication date of either document must read `date_flag` first.**

---

# 6. Remediation actions and their verification

| # | Action | Target | State |
| --- | --- | --- | --- |
| 1 | Rename | `ReNew_Solar_Power_Private_Limited_Solar.pdf` → `..._IndRa_Solar.pdf` | Applied |
| 2 | Rename | `Renew_Solar_Power_Private_Limited_Solar.pdf` → `..._CARE_Solar.pdf` | Applied |
| 3 | Rename | `CARE_Criterial_for_ConsolidationandCombinedApproachMarch2025.pdf` → `CARE_Criteria_Consolidation_Combined_Approach_07_March_2025.pdf` | Applied — typo "Criterial" and missing separators |
| 4 | Rename | `India_Ratings_Criteria_for_Infrastructure_and_Project_FinanceMay.pdf` → `India_Ratings_Criteria_Infrastructure_Project_Finance_27_May_2024.pdf` | Applied — dangling "May" with no year |
| 5 | Quarantine | `Fitch_Ratings_Renewable_Energy_Criteria.pdf` | Applied |
| 6 | Regenerate manifest against the folder as it stands | — | Applied at v3.0 |

**Post-state, verified 30 July 2026:**

| Check | Result |
| --- | --- |
| Files in corpus root | 41 |
| Quarantined | 1 |
| Case-insensitive collisions | **0** |
| Manifest rows | 41 |
| Files on disk resolving to a manifest row | **41 of 41** |
| Payload hashes matching the manifest | **41 of 41** |
| Container declarations matching disk | **41 of 41** (37 ZIP, 4 PDF) |
| Distinct payload hashes | 41 — no duplicate group |
| Tier counts | 20 / 1 / 20 |
| Tier-3 category counts | Solar 8, Wind 4, Hybrid 6, BESS 1, Wind-Solar-BESS 1 |
| `corpus_manifest.py --verify` | **PASS** |

---

# 7. Limitations

**7.1 The corpus will re-collide if restored from an unremediated source.** The remediation is applied to files, not to the source they came from. Anyone re-downloading the original set gets the collision back. This is why the verification step at Section 4.4 belongs in the build routine rather than in a one-time checklist.

**7.2 OCR quality has not been assessed.** This audit established what the files are, not how well they were recognised. Page-1 text was legible in all 42, which is a reasonable signal but not a measurement. If a grounding lookup for a specific threshold comes back empty, suspect OCR before concluding the threshold is absent from the source — particularly for numbers inside table images, which is where the DSCR guidance in the Fitch criteria and the liquidity tiers in the CARE criteria both live.

**7.3 Two publication dates are disputed.** See Section 5.3. Both are declared in `date_flag`. Neither has been hand-corrected, for the reason at Section 4.5.

**7.4 Seven Tier-1 methodology documents ground nothing in the v1 engine.** Short-term instruments, consolidation (CARE and CRISIL), default recognition, the complexity indicator, corporate governance, and basics of ratings all sit within the scope of the companion Criteria Extension and are correctly absent from Core Rating Criteria Section 12's mapping. They are retained in the corpus because the Extension modules are designed against them.

**7.5 Two sources cited in Core Rating Criteria Section 12 are not in the corpus at all** and cannot be resolved through the manifest: the Ministry of Power / Power Finance Corporation Integrated Rating and Ranking of Power Distribution Utilities, and the MNRE notifications behind the ALMM parameter table. Both are live reference data re-verified on a cadence rather than ingested once. Section 12 marks them **external, not in corpus**, and the grounding step must not attempt a manifest lookup for either.

**7.6 The four genuine PDFs have a weaker content-identity guarantee** than the 37 ZIP containers, because their payload hash is the whole-file hash and would change on PDF re-compression. Nothing in this project re-compresses PDFs. The `payload_basis` column states which files are affected.
