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
| Container format | **Uniform PDF, all 41 files.** Text layer verified on 660 of 661 pages. See Section 2. |
| Owner | Developer (CA. Satish Tirumela) |

---

# 0. What changed in v3.0, and why it matters

v2.0 of this specification described a remediation that had been designed but not applied. The remediation has since been applied — by hand, under a different naming convention from the one the script targeted, and with four documents re-supplied in a different file format. Three consequences followed, none of them visible from any single document, and all three are corrected here.

**(a) The container format changed twice, and now it is uniform.** v2.0's central factual claim was that *all 42 files carrying a .pdf extension begin with the byte signature 50 4B 03 04, and none begins with %PDF.* That became false for four files during remediation, making the corpus **mixed**: 37 ZIP archives and 4 genuine PDFs. A pipeline built on either assumption failed silently on the other set, reading as file corruption rather than as a format mismatch.

That is no longer the state. On re-download, the 37 archives were served as **real PDFs**. All 41 files now begin `%PDF`, and the mixed-format dispatch this specification introduced is no longer required. **Crucially, that was verified rather than assumed:** a text-layer check found extractable text on **660 of 661 pages** across all 41 documents, with samples confirming they read as the genuine agency publications. Had the conversion produced image-only PDFs, the grounding step would have failed silently and the corpus would have needed rebuilding from original copies. See Section 2.

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

# 2. Element (a) — container format: now uniformly PDF

**All 41 files are genuine PDFs.**

| Container | Count | Signature | Text layer |
| --- | --- | --- | --- |
| PDF | **41** | `25 50 44 46` (`%PDF`) | 660 of 661 pages carry extractable text |
| ZIP | 0 | — | — |

**This has changed twice, and the history matters because it explains why the tooling is defensive.**

*As originally assembled*, every file was a ZIP container holding one JPEG and one OCR text file per page plus a `manifest.json` index, all wearing a `.pdf` extension. A pipeline built on any PDF library — pypdf, pdfplumber, PyMuPDF, or a Gemini upload declared as `application/pdf` — failed on all 41.

*After the first remediation*, four files were re-supplied as genuine PDFs, making the corpus **mixed**: 37 ZIP, 4 PDF. Neither assumption worked, so this specification introduced dispatch on the manifest's `container` column.

*After re-download*, all 37 archives came back as real PDFs. The corpus is uniform and the dispatch is unnecessary.

**The lesson is not about formats.** It is that the corpus changed underneath the project three times without anyone intending it, and each time the manifest caught it immediately with a precise list. Filenames and container formats are not stable properties of this corpus; content hashes are. That is why Section 4.1 still requires resolution through the manifest even though the format question has resolved itself.

## 2.1 What was checked before accepting the conversion

A format conversion is only harmless if the content survives. Two things were verified, and neither was taken on trust:

| Check | Result |
| --- | --- |
| Does every document still pair with a manifest row? | 41 of 41 paired by name; 0 unrecognised |
| Does every document still yield text? | 41 of 41 have a text layer on 80%+ of pages; 660 of 661 pages overall |

Text samples were read from three documents and confirmed to be the genuine publications — a CARE press release, a second CARE press release, and the Brickwork financial-ratios approach — rather than headers, boilerplate or OCR noise.

**Had the conversion produced image-only PDFs**, the pages would have been pictures of words. Extraction would have returned empty strings, the grounding step would have found nothing, and the failure would have looked like an absent threshold in the source rather than an unreadable file. That is precisely the class of silent failure this specification exists to prevent, and it is why the check was run before the manifest was regenerated rather than after.

## 2.2 The `container` and `payload_basis` columns are retained

Both columns now read the same value on every row — `PDF` and `file` respectively. They are kept rather than dropped because they cost nothing, they document the rule by which each hash was computed, and they would catch a future divergence of exactly the kind that has now happened three times.

**For a PDF, `payload_sha256` equals `file_sha256`.** A PDF has no container/payload separation of the kind the ZIP archives had. Manufacturing one — extracting text and hashing that — would make the hash depend on the extraction library's version, which is worse than no abstraction. The property given up is stability across PDF re-compression; nothing in this project re-compresses PDFs.

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

## 4.1 Resolve through the manifest, and read the `container` column

**Read `Reference_Corpus_Manifest_v3_0.csv` first.** All 41 rows currently read `container = PDF`, so ingestion opens each file with an ordinary PDF library and uses the text layer. **Read the column rather than hard-coding the answer** — it has changed three times, and a pipeline that assumes a format will fail silently the next time it changes.

**Key documents on `payload_sha256`, not on filename.** Filenames in this corpus have proven unstable **five** separate ways: two collided on case alone, one methodology appeared twice under different names, two carried malformed dates, four were renamed by hand under a convention no tool predicted, and a re-download rewrote 37 of them by replacing underscores with spaces. The payload hash is the stable identifier; the filename is a label.

## 4.2 Declaring `application/pdf` is now correct — but check the manifest, not the extension

All 41 files are genuine PDFs, so a Gemini file upload declared as `application/pdf` is correct today. **That was not true a week ago and may not be true again.** When 37 of these files were ZIP archives, the same declaration caused rejection or mis-parsing on 37 of 41 documents. Read the `container` column; do not infer from the `.pdf` extension, which was misleading for most of this corpus's life.

## 4.3 Text comes from the PDF text layer, and its presence is verifiable

Extraction is an ordinary `extract_text()` per page. **Confirm the text layer before relying on it**: `corpus_textcheck.py` reports, per document, how many pages yield extractable text. The current state is 660 of 661 pages across all 41 documents.

A PDF that is a scan with no text layer extracts as empty strings. That does not raise an error — it looks exactly like a document that does not mention the thing you searched for. If a grounding lookup returns nothing, run the text check before concluding the source is silent.

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
| 7 | Restore filenames after a re-download rewrote 37 of them, and regenerate the manifest against the converted files | `corpus_rebuild.py` | Applied 31 July 2026 |
| 8 | Verify a text layer survived the conversion before accepting it | `corpus_textcheck.py` | Applied — 660 of 661 pages |

**Post-state, verified 30 July 2026:**

| Check | Result |
| --- | --- |
| Files in corpus root | 41 |
| Quarantined | 1 |
| Case-insensitive collisions | **0** |
| Manifest rows | 41 |
| Files on disk resolving to a manifest row | **41 of 41** |
| Payload hashes matching the manifest | **41 of 41** |
| Container declarations matching disk | **41 of 41** (PDF on every row) |
| Distinct payload hashes | 41 — no duplicate group |
| Tier counts | 20 / 1 / 20 |
| Tier-3 category counts | Solar 8, Wind 4, Hybrid 6, BESS 1, Wind-Solar-BESS 1 |
| `corpus_manifest.py --verify` | **PASS** |

---

# 6.1 Revision within v3.0 — 31 July 2026

*The corpus was re-downloaded and came back materially changed. This section records what happened, because the sequence is the clearest evidence in the project that the manifest is doing real work.*

| Step | What happened |
| --- | --- |
| 1 | 41 files copied into the repository. `corpus_manifest.py --verify` returned **FAIL — 74 problems** |
| 2 | 74 resolved as 37 + 37: thirty-seven files reported both as unexpected and as missing. The download had replaced underscores with spaces |
| 3 | `corpus_restore_names.py` matched on content hash and found **37 unmatched** — so the bytes had changed too, not just the labels |
| 4 | `corpus_diagnose.py` found **37 container changes**: the ZIP archives had been served as real PDFs |
| 5 | `corpus_textcheck.py` confirmed a text layer on **660 of 661 pages**, with samples read from three documents to confirm they were the genuine publications |
| 6 | `corpus_rebuild.py` restored the canonical filenames by normalised-name matching and regenerated the manifest, carrying tier and category forward from the original audit |
| 7 | `corpus_manifest.py --verify` returned **PASS** |

**What this cost and what it bought.** Six steps and about half an hour. Without the manifest, the outcome would have been 41 correctly-named-looking files, no error message anywhere, and a grounding step quietly retrieving nothing — discovered, if at all, as an unexplained gap in the rationale output days later.

**The judgement that mattered was step 5, not step 6.** Renaming files and regenerating a manifest is mechanical. Deciding whether a format conversion had destroyed the content is not, and it is the step that could have been skipped by anyone in a hurry. Had the conversion produced image-only PDFs, regenerating the manifest would have produced a confident **PASS** over an unreadable corpus.

# 7. Limitations

**7.1 The corpus will re-collide if restored from an unremediated source.** The remediation is applied to files, not to the source they came from. Anyone re-downloading the original set gets the collision back. This is why the verification step at Section 4.4 belongs in the build routine rather than in a one-time checklist.

**7.2 OCR quality has not been assessed.** This audit established what the files are, not how well they were recognised. Page-1 text was legible in all 42, which is a reasonable signal but not a measurement. If a grounding lookup for a specific threshold comes back empty, suspect OCR before concluding the threshold is absent from the source — particularly for numbers inside table images, which is where the DSCR guidance in the Fitch criteria and the liquidity tiers in the CARE criteria both live.

**7.3 Two publication dates are disputed.** See Section 5.3. Both are declared in `date_flag`. Neither has been hand-corrected, for the reason at Section 4.5.

**7.4 Seven Tier-1 methodology documents ground nothing in the v1 engine.** Short-term instruments, consolidation (CARE and CRISIL), default recognition, the complexity indicator, corporate governance, and basics of ratings all sit within the scope of the companion Criteria Extension and are correctly absent from Core Rating Criteria Section 12's mapping. They are retained in the corpus because the Extension modules are designed against them.

**7.5 Two sources cited in Core Rating Criteria Section 12 are not in the corpus at all** and cannot be resolved through the manifest: the Ministry of Power / Power Finance Corporation Integrated Rating and Ranking of Power Distribution Utilities, and the MNRE notifications behind the ALMM parameter table. Both are live reference data re-verified on a cadence rather than ingested once. Section 12 marks them **external, not in corpus**, and the grounding step must not attempt a manifest lookup for either.

**7.6 Every file now has the weaker content-identity guarantee.** With the corpus uniformly PDF, `payload_sha256` equals `file_sha256` on all 41 rows, so the hash would change on any re-compression even if the words were untouched. When the corpus was ZIP-based, the payload hash excluded container metadata and so survived re-compression. Nothing in this project re-compresses PDFs, and the trade is worth it for a uniform contract — but it is a real reduction in what the hash guarantees, and it is recorded here rather than left for someone to discover.

**7.7 The current manifest was regenerated after the re-download, and that limits what it proves.** It guarantees integrity **from this point forward**: any later change to any file will be caught. It proves nothing about what happened before it was generated. The tier, category and agency assignments were **carried forward from the original audit** rather than re-derived, because those were established by reading the documents; re-deriving them automatically would have been guesswork wearing the appearance of rigour. The publication dates were re-derived by the Section 5.2 rule and the disputes at Section 5.3 still stand.
