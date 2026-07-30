#!/usr/bin/env python3
"""
Credit Rating Simulator — Reference Corpus Manifest Generator / Verifier
Version 3.0 — supersedes the hard-coded rename table in corpus_remediate.py v2.0.

    python corpus_manifest.py --corpus <folder> --generate --out manifest.csv
    python corpus_manifest.py --corpus <folder> --verify --manifest manifest.csv

WHY THIS REPLACES THE v2.0 APPROACH
-----------------------------------
corpus_remediate.py v2.0 keyed its work on a hard-coded table of old and new
filenames. When the renames were applied by hand under a different naming
convention, the script reported four BLOCKED actions against files that were in
fact already correct, and the manifest -- which carried the script's intended
names -- no longer matched the folder. A tool whose job is to protect against
unstable filenames must not itself depend on them.

This tool derives everything from the folder as it stands, dispatches on the
container signature rather than assuming one, and treats the manifest as a
regenerable artefact rather than a hand-maintained one.

CONTAINER HANDLING
------------------
The corpus is MIXED. Files beginning PK\\x03\\x04 are ZIP containers of per-page
JPEG + OCR text plus manifest.json. Files beginning %PDF are genuine PDFs.
Any ingestion code must dispatch on the manifest's `container` column and must
not assume either format.

  container = ZIP  ->  payload_sha256 hashes the sorted .txt/.jpeg entries only,
                       so it is stable across rename and re-compression.
  container = PDF  ->  payload_sha256 = file_sha256. A PDF has no container /
                       payload separation of the kind the ZIP archives have, so
                       the two hashes are declared equal rather than a spurious
                       distinction being manufactured. `payload_basis` records
                       which rule was applied.

DATE RESOLUTION
---------------
v2.0 resolved publication_date to the LATEST date found in page-1 text. On
methodology documents that is usually right. On rating rationales it is usually
wrong, because a rationale cites PPA expiries and debt maturities decades ahead.
v2.0's manifest consequently dated three rationales to December 2038, March 2027
and June 2045.

The rule here: publication_date is the latest date on page 1 that is NOT later
than the audit date. This is regenerable, states its own logic, and fixes all
three without hand-editing a generated column. Residual known-wrong values are
recorded in `date_flag` rather than silently corrected.
"""
import argparse, csv, hashlib, io, json, os, re, sys, zipfile
from datetime import date

AUDIT_DATE = date(2026, 7, 30)

FIELDS = ['filename', 'tier', 'category', 'agency', 'publication_date',
          'date_resolution', 'date_flag', 'dates_on_page1', 'container',
          'payload_basis', 'pages', 'ocr_text_pages', 'inner_manifest',
          'bytes', 'flags', 'duplicate_group', 'payload_sha256', 'file_sha256']

MONTHS = {m.lower(): i for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July',
     'August', 'September', 'October', 'November', 'December'], 1)}
for _m, _i in list(MONTHS.items()):
    MONTHS[_m[:3]] = _i

DATE_RES = [
    re.compile(r'\b(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\b'),
    re.compile(r'\b([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\b'),
    re.compile(r'\b([A-Za-z]{3,9})\.?,?\s+(\d{4})\b'),
]

# Documents whose page 1 carries a revision history, so that the latest past
# date is a cross-reference rather than the publication date. The resolved value
# is left as the heuristic produced it and the dispute is declared, because a
# hand-corrected value inside a generated column survives regeneration
# invisibly and misleads the next reader into trusting the whole column.
DATE_DISPUTED = {
    'Fitch_Ratings_Global_Infra__Project_Finance_Criteria.pdf':
        'HEURISTIC-DISPUTED: page-1 revision history. Criteria report is dated '
        '17 May 2023; resolved value is a later cross-reference.',
    'Moodys_General_Project_Finance_Methodology.pdf':
        'HEURISTIC-DISPUTED: page-1 revision history. CORE Section 12 cites this '
        'methodology as June 2021; resolved value is a later cross-reference.',
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def container_of(path):
    with open(path, 'rb') as f:
        sig = f.read(4)
    if sig[:2] == b'PK':
        return 'ZIP'
    if sig == b'%PDF':
        return 'PDF'
    return 'UNKNOWN'


def payload_sha256(path, container):
    """Content hash. See CONTAINER HANDLING above."""
    if container == 'ZIP':
        z = zipfile.ZipFile(path)
        names = sorted(n for n in z.namelist()
                       if n.lower().endswith(('.txt', '.jpeg', '.jpg', '.png')))
        h = hashlib.sha256()
        for n in names:
            h.update(z.read(n))
        return h.hexdigest(), 'zip-entries'
    return sha256_file(path), 'file'


def page1_text(path, container):
    if container == 'ZIP':
        z = zipfile.ZipFile(path)
        for cand in ('1.txt', '01.txt', '0.txt'):
            if cand in z.namelist():
                return z.read(cand).decode('utf-8', 'ignore')
        txts = sorted((n for n in z.namelist() if n.lower().endswith('.txt')),
                      key=lambda n: int(re.sub(r'\D', '', n) or 0))
        return z.read(txts[0]).decode('utf-8', 'ignore') if txts else ''
    try:
        from pypdf import PdfReader
        return PdfReader(path).pages[0].extract_text() or ''
    except Exception:
        return ''


def page_count(path, container):
    if container == 'ZIP':
        z = zipfile.ZipFile(path)
        names = z.namelist()
        if 'manifest.json' in names:
            try:
                return int(json.loads(z.read('manifest.json'))['num_pages'])
            except Exception:
                pass
        return sum(1 for n in names if n.lower().endswith(('.jpeg', '.jpg', '.png')))
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages)
    except Exception:
        return 0


def ocr_text_pages(path, container):
    if container == 'ZIP':
        z = zipfile.ZipFile(path)
        return sum(1 for n in z.namelist() if n.lower().endswith('.txt'))
    return 0


def has_inner_manifest(path, container):
    if container == 'ZIP':
        return 'manifest.json' in zipfile.ZipFile(path).namelist()
    return False


def find_dates(text):
    """Return (label, date) pairs in order of appearance, de-duplicated."""
    out, seen = [], set()
    for rx in DATE_RES:
        for m in rx.finditer(text):
            g = m.groups()
            try:
                if len(g) == 3 and g[0].isdigit():
                    d, mo, y = int(g[0]), MONTHS.get(g[1].lower()), int(g[2])
                elif len(g) == 3:
                    mo, d, y = MONTHS.get(g[0].lower()), int(g[1]), int(g[2])
                else:
                    mo, d, y = MONTHS.get(g[0].lower()), 1, int(g[1])
                if not mo or not (1900 < y < 2100) or not (1 <= d <= 31):
                    continue
                dt = date(y, mo, d)
            except Exception:
                continue
            label = m.group(0).strip()
            if label.lower() in seen:
                continue
            seen.add(label.lower())
            out.append((label, dt))
    return out


def resolve_date(dates):
    """Latest date not later than the audit date. See DATE RESOLUTION above."""
    past = [(l, d) for l, d in dates if d <= AUDIT_DATE]
    if not past:
        return '', 'unresolved', 'NO-PAST-DATE-ON-PAGE1'
    label, dt = max(past, key=lambda t: t[1])
    future = [l for l, d in dates if d > AUDIT_DATE]
    flag = f'FUTURE-DATES-IGNORED: {len(future)}' if future else ''
    return label, 'latest-not-future', flag


def build_row(path, classify):
    name = os.path.basename(path)
    cont = container_of(path)
    ph, basis = payload_sha256(path, cont)
    txt = page1_text(path, cont)
    dates = find_dates(txt)
    pub, method, flag = resolve_date(dates)
    if name in DATE_DISPUTED:
        flag = (flag + '; ' if flag else '') + DATE_DISPUTED[name]
    tier, cat, agency = classify(name, txt)
    flags = [] if cont == 'PDF' else ['CONTAINER-NOT-PDF']
    if cont == 'UNKNOWN':
        flags = ['CONTAINER-UNKNOWN']
    return {
        'filename': name, 'tier': tier, 'category': cat, 'agency': agency,
        'publication_date': pub, 'date_resolution': method, 'date_flag': flag,
        'dates_on_page1': '; '.join(l for l, _ in dates),
        'container': cont, 'payload_basis': basis,
        'pages': page_count(path, cont),
        'ocr_text_pages': ocr_text_pages(path, cont),
        'inner_manifest': 'yes' if has_inner_manifest(path, cont) else 'no',
        'bytes': os.path.getsize(path), 'flags': '; '.join(flags),
        'duplicate_group': '', 'payload_sha256': ph, 'file_sha256': sha256_file(path),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--manifest')
    ap.add_argument('--out')
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--classifier', help='optional JSON: {filename: [tier, category, agency]}')
    a = ap.parse_args()

    lookup = json.load(open(a.classifier)) if a.classifier else {}

    def classify(name, txt):
        if name in lookup:
            return tuple(lookup[name])
        return ('', '', '')

    files = sorted(f for f in os.listdir(a.corpus) if f.lower().endswith('.pdf'))
    paths = [os.path.join(a.corpus, f) for f in files]

    if a.generate:
        rows = [build_row(p, classify) for p in paths]
        by_payload = {}
        for r in rows:
            by_payload.setdefault(r['payload_sha256'], []).append(r)
        g = 0
        for grp in by_payload.values():
            if len(grp) > 1:
                g += 1
                for r in grp:
                    r['duplicate_group'] = f'DUP-{g}'
        out = a.out or 'Reference_Corpus_Manifest.csv'
        with open(out, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f'Wrote {out}: {len(rows)} rows')
        print(f'  containers: ' + ', '.join(
            f'{k}={sum(1 for r in rows if r["container"] == k)}'
            for k in sorted({r['container'] for r in rows})))
        print(f'  duplicate payload groups: {g}')
        return

    if a.verify:
        if not a.manifest:
            sys.exit('--verify requires --manifest')
        man = {r['filename']: r for r in csv.DictReader(open(a.manifest, encoding='utf-8'))}
        errs = []
        low = [f.lower() for f in files]
        coll = sorted({x for x in low if low.count(x) > 1})
        if coll:
            errs.append(f'case-insensitive filename collisions: {coll}')
        for f in files:
            if f not in man:
                errs.append(f'on disk but not in manifest: {f}')
        for f in man:
            if f not in files:
                errs.append(f'in manifest but not on disk: {f}')
        for f in files:
            if f not in man:
                continue
            p = os.path.join(a.corpus, f)
            cont = container_of(p)
            if cont != man[f]['container']:
                errs.append(f'container mismatch {f}: disk={cont} manifest={man[f]["container"]}')
                continue
            ph, _ = payload_sha256(p, cont)
            if ph != man[f]['payload_sha256']:
                errs.append(f'payload_sha256 mismatch: {f}')
        print(f'Corpus:   {os.path.abspath(a.corpus)}')
        print(f'Manifest: {a.manifest}')
        print(f'Files on disk: {len(files)}   Manifest rows: {len(man)}')
        print(f'Case-insensitive collisions: {len(coll)}')
        if errs:
            print('\nFAIL — ' + str(len(errs)) + ' problem(s):')
            for e in errs:
                print('  ' + e)
            sys.exit(1)
        print('\nPASS — every file resolves, every payload hash matches, no collisions.')
        return

    sys.exit('specify --generate or --verify')


if __name__ == '__main__':
    main()
