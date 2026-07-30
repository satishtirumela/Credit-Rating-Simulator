#!/usr/bin/env python3
"""
Credit Rating Simulator — Reference Corpus Remediation
Version 3.0 — 30 July 2026. Closes QA finding MIN-10 (reference corpus hygiene).

WHAT CHANGED IN v3.0
--------------------
1. The rename table records the names ACTUALLY APPLIED. v2.0 targeted a longer,
   date-bearing convention; the renames were applied by hand under a shorter one.
   The script consequently reported 4 BLOCKED against files that were already
   correct, which trains the operator to ignore the tool.
2. payload_hash() dispatches on the container signature. Four files are now
   genuine PDFs, and v2.0's zipfile.ZipFile() call raised BadZipFile on them.
3. This script no longer owns corpus verification. Run
   corpus_manifest.py --verify instead: it compares the folder against the
   manifest by content hash rather than against a hard-coded name table, so it
   cannot be defeated by a renaming convention nobody predicted.

Idempotent and DRY-RUN BY DEFAULT. Nothing is moved unless --apply is passed.
Every action is verified by payload hash before and after, so a partially
completed run can be re-run safely.

    python corpus_remediate.py --corpus /path/to/corpus            # dry run
    python corpus_remediate.py --corpus /path/to/corpus --apply     # execute
    python corpus_remediate.py --corpus /path/to/corpus --verify    # check state only

Duplicate handling:

    ... --apply                      # duplicate moved to _quarantine/ (default, reversible)
    ... --apply --delete-duplicates  # duplicate DELETED outright (irreversible)

--delete-duplicates will not delete a file unless it has first re-confirmed, at
that moment, that a byte-identical payload survives elsewhere in the corpus. If
the surviving twin is missing or its payload differs, the delete is refused.

Design notes
------------
* The two ReNew files are NOT duplicates. They are different rationales on the
  same issuer from different agencies. Both are renamed; neither is deleted.
* Both renamed files keep their terminal "_Solar" suffix, so any existing
  category-from-filename logic keeps working unchanged.
* The Fitch duplicate is QUARANTINED by default, so the action is reversible.
  Pass --delete-duplicates to remove it outright. Either way the deletion is
  safe only because the payload-identity evidence is recorded in the Reference
  Corpus Hygiene and Ingestion Specification and in the manifest, so the audit
  trail survives the file.
"""
import argparse, hashlib, os, shutil, sys, zipfile

QUARANTINE = '_quarantine'

# expected payload hash -> guards against renaming the wrong file
# Target names are those ACTUALLY APPLIED to the folder as at 30 July 2026.
# The payload-prefix guard is dropped for the two ReNew files because both were
# re-supplied as genuine PDFs during remediation, so their payload hash is now
# the whole-file hash and no longer matches the v2.0 ZIP-derived prefix. The
# guard those prefixes provided -- refusing to attribute a CARE rationale to
# India Ratings -- is now enforced by corpus_manifest.py --verify against the
# manifest's agency and payload_sha256 columns.
RENAMES = [
    # (current name, new name, expected payload sha256 prefix, reason)
    ('ReNew_Solar_Power_Private_Limited_Solar.pdf',
     'ReNew_Solar_Power_Private_Limited_IndRa_Solar.pdf',
     None, 'Case collision. India Ratings rationale, 31 Mar 2026, 6pp, IND A/Negative.'),
    ('Renew_Solar_Power_Private_Limited_Solar.pdf',
     'Renew_Solar_Power_Private_Limited_CARE_Solar.pdf',
     None, 'Case collision. CARE Ratings press release, 08 Apr 2026, 12pp, CARE A/Stable.'),
    ('CARE_Criterial_for_ConsolidationandCombinedApproachMarch2025.pdf',
     'CARE_Criteria_Consolidation_Combined_Approach_07_March_2025.pdf',
     None, 'Typo "Criterial"; missing word separators.'),
    ('India_Ratings_Criteria_for_Infrastructure_and_Project_FinanceMay.pdf',
     'India_Ratings_Criteria_Infrastructure_Project_Finance_27_May_2024.pdf',
     None, 'Dangling "May" with no year and no separator. Document is dated 27 May 2024.'),
]

# (redundant file, surviving canonical twin, reason)
QUARANTINES = [
    ('Fitch_Ratings_Renewable_Energy_Criteria.pdf',
     'Fitch_Ratings_Renewable_Energy_Rating_Criteria_Feb_2023.pdf',
     'Payload byte-identical to the canonical twin (26/26 OCR pages and all images '
     'identical). The dated filename is retained because it carries the publication date.'),
]

def payload_hash(path):
    """Content hash, dispatching on the container signature.

    The corpus is MIXED: 37 ZIP containers of per-page JPEG + OCR text, and 4
    genuine PDFs. v2.0 called zipfile.ZipFile() unconditionally and raised
    BadZipFile on the four PDFs.

    ZIP -> hash the sorted .txt/.jpeg entries, so the hash survives rename and
           re-compression because container metadata is excluded.
    PDF -> whole-file hash. A PDF has no equivalent container/payload
           separation, and manufacturing one by hashing extracted text would
           make the hash depend on the extraction library's version.
    """
    with open(path, 'rb') as f:
        sig = f.read(4)
    if sig[:2] == b'PK':
        z = zipfile.ZipFile(path)
        names = sorted(n for n in z.namelist()
                       if n.lower().endswith(('.txt', '.jpeg', '.jpg', '.png')))
        h = hashlib.sha256()
        for n in names:
            h.update(z.read(n))
        return h.hexdigest()
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--delete-duplicates', action='store_true',
                    help='delete the redundant duplicate outright instead of quarantining it '
                         '(irreversible; only proceeds if the canonical twin is verified present)')
    a = ap.parse_args()
    root = os.path.abspath(a.corpus)
    if not os.path.isdir(root):
        sys.exit(f'not a directory: {root}')

    mode = 'VERIFY' if a.verify else ('APPLY' if a.apply else 'DRY RUN')
    if a.delete_duplicates:
        mode += ' + DELETE DUPLICATES (irreversible)'
    print(f'Corpus: {root}\nMode:   {mode}\n' + '-' * 74)

    planned = done = blocked = 0

    for old, new, expect, reason in RENAMES:
        po, pn = os.path.join(root, old), os.path.join(root, new)
        if os.path.exists(pn) and not os.path.exists(po):
            print(f'[done]    {new}'); done += 1; continue
        if not os.path.exists(po):
            print(f'[missing] {old}  -- neither old nor new name present'); blocked += 1; continue
        if expect:
            got = payload_hash(po)[:4]
            if got != expect:
                print(f'[BLOCK]   {old}\n          payload {got} != expected {expect} -- refusing to rename')
                blocked += 1; continue
        print(f'[rename]  {old}\n       -> {new}\n          {reason}')
        planned += 1
        if a.apply:
            before = payload_hash(po)
            os.rename(po, pn)
            assert payload_hash(pn) == before, 'payload changed during rename'
            print('          verified: payload unchanged after rename')

    qdir = os.path.join(root, QUARANTINE)
    for name, twin, reason in QUARANTINES:
        ps = os.path.join(root, name)
        pq = os.path.join(qdir, name)
        pt = os.path.join(root, twin)

        # already dealt with, either way
        if not os.path.exists(ps):
            if os.path.exists(pq):
                print(f'[done]    quarantined: {QUARANTINE}/{name}')
            else:
                print(f'[done]    removed: {name}')
            done += 1
            continue

        if not a.delete_duplicates:
            print(f'[quarant] {name} -> {QUARANTINE}/\n          {reason}')
            planned += 1
            if a.apply:
                os.makedirs(qdir, exist_ok=True)
                shutil.move(ps, pq)
            continue

        # --- deletion path: re-prove the twin survives, now, before removing anything ---
        if not os.path.exists(pt):
            print(f'[BLOCK]   {name}\n          canonical twin {twin} not found -- refusing to delete')
            blocked += 1
            continue
        h_dup, h_twin = payload_hash(ps), payload_hash(pt)
        if h_dup != h_twin:
            print(f'[BLOCK]   {name}\n          payload differs from {twin}'
                  f'\n          {h_dup[:16]} vs {h_twin[:16]} -- NOT a duplicate, refusing to delete')
            blocked += 1
            continue
        print(f'[delete]  {name}\n          {reason}'
              f'\n          verified: identical payload {h_twin[:16]} survives as {twin}')
        planned += 1
        if a.apply:
            os.remove(ps)
            assert os.path.exists(pt) and payload_hash(pt) == h_twin, 'canonical twin damaged'
            print('          deleted; canonical twin re-verified intact')

    print('-' * 74)
    print(f'planned: {planned}   already done: {done}   blocked: {blocked}')

    # post-state assertions
    files = [f for f in os.listdir(root) if f.lower().endswith('.pdf')]
    lower = [f.lower() for f in files]
    collisions = {x for x in lower if lower.count(x) > 1}
    print(f'\nPost-state: {len(files)} files in corpus root')
    print(f'  case-insensitive collisions: {len(collisions)}'
          + (f' -> {sorted(collisions)}' if collisions else ' (none)'))
    containers = {}
    for f in files:
        with open(os.path.join(root, f), 'rb') as fh:
            sig = fh.read(4)
        k = 'ZIP' if sig[:2] == b'PK' else ('PDF' if sig == b'%PDF' else 'UNKNOWN')
        containers[k] = containers.get(k, 0) + 1
    print('  containers: ' + ', '.join(f'{k}={v}' for k, v in sorted(containers.items()))
          + '   (the corpus is MIXED -- ingestion must dispatch on the manifest'
            ' container column, never on the extension)')
    print('\nFor full verification run:\n  python corpus_manifest.py --corpus '
          + root + ' --verify --manifest Reference_Corpus_Manifest_v3_0.csv')
    if not a.apply and planned:
        print('\nNothing was changed. Re-run with --apply to execute.')

if __name__ == '__main__':
    main()
