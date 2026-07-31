#!/usr/bin/env python3
"""
Rebuild the corpus: restore filenames, then regenerate the manifest.

Use this when the corpus has been re-downloaded and the files came back with
altered names or in a different container format. It does two things:

  1. Renames every file to its canonical name, matching on a NORMALISED name
     (spaces, underscores, dots and case all ignored) rather than on content.
     Content matching is safer and is what corpus_restore_names.py does, but it
     only works when the bytes are unchanged. After a format conversion the
     bytes differ by design, so name matching is the only route left.

  2. Regenerates the manifest against the restored files, carrying forward each
     document's tier, category and agency from the table below.

    python corpus_rebuild.py --corpus corpus            # preview
    python corpus_rebuild.py --corpus corpus --apply    # do it

WHAT A REGENERATED MANIFEST DOES AND DOES NOT PROVE
---------------------------------------------------
It guarantees integrity FROM NOW ON: any later change to any file will be
caught. It proves nothing about what happened BEFORE it was generated. That is
an honest limitation and it is why the tier and category assignments below are
carried forward from the original audit rather than re-derived -- those were
established by reading the documents, and re-deriving them automatically would
be guesswork wearing the appearance of rigour.
"""
CLASSIFICATION = {
 "adanigreenenergytwentyfiveblimitedwindsolar": [
  "Adani_Green_Energy_Twenty_Five_B_Limited_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "CARE"
 ],
 "adanisolarenergyapsixprivatelimitedsolar": [
  "Adani_Solar_Energy_AP_Six_Private_Limited_Solar.pdf",
  "Tier 3",
  "Solar",
  "CARE"
 ],
 "brickworksapproachtofinancialratios": [
  "Brickworks_Approach_to_Financial_Ratios.pdf",
  "Tier 1",
  "Methodology",
  "Brickwork"
 ],
 "carecriteriaconsolidationcombinedapproach07march2025": [
  "CARE_Criteria_Consolidation_Combined_Approach_07_March_2025.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "carecriteriaforinfrastructuresectorratingsmar2025": [
  "CARE_Criteria_for_Infrastructure_Sector_Ratings_Mar_2025.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "carecriteriaforshortterminstrumentsfeb2025": [
  "CARE_Criteria_for_Short_Term_Instruments_Feb_2025.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "carefinancialratiosnonfinancialsectormarch2025": [
  "CARE_Financial_Ratios_Non_Financial_Sector_March_2025.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "careliquidityanalysisofnonfinancialsectorentities20sept2024": [
  "CARE_Liquidity_Analysis_of_NonFinancial_Sector_Entities_20Sept_2024.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "caremethodologysolarpowerprojectsdecember2024": [
  "CARE_Methodology_Solar_Power_Projects_December_2024.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "carepolicyondefaultrecognitionjan2025": [
  "CARE_Policy_on_Default_Recognition_Jan_2025.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "careratingsmethodologywindpowerprojectsdecember2024": [
  "CARE_Ratings_Methodology_Wind_Power_Projects_December_2024.pdf",
  "Tier 1",
  "Methodology",
  "CARE"
 ],
 "cleanwindpowerdevgarhprivatelimitedwind": [
  "Clean_Wind_Power_Devgarh_Private_Limited_Wind.pdf",
  "Tier 3",
  "Wind",
  "India Ratings"
 ],
 "crisilintelligenceindianrenewableenergyreportjanuary2026": [
  "Crisil_Intelligence_Indian_Renewable_Energy_Report_January_2026.pdf",
  "Tier 2",
  "Sector report",
  ""
 ],
 "crisilratingsbasicsofratings": [
  "Crisil_Ratings_Basics_of_Ratings.pdf",
  "Tier 1",
  "Methodology",
  "CRISIL"
 ],
 "crisilratingscriteriaforconsolidation": [
  "Crisil_Ratings_Criteria_for_Consolidation.pdf",
  "Tier 1",
  "Methodology",
  "CRISIL"
 ],
 "crisilratingscriteriaforinfrastructuresectors": [
  "Crisil_Ratings_Criteria_for_Infrastructure_sectors.pdf",
  "Tier 1",
  "Methodology",
  "CRISIL"
 ],
 "fitchratingsglobalinfraprojectfinancecriteria": [
  "Fitch_Ratings_Global_Infra__Project_Finance_Criteria.pdf",
  "Tier 1",
  "Methodology",
  "Fitch"
 ],
 "fitchratingsrenewableenergyratingcriteriafeb2023": [
  "Fitch_Ratings_Renewable_Energy_Rating_Criteria_Feb_2023.pdf",
  "Tier 1",
  "Methodology",
  "Fitch"
 ],
 "greeninfrawindenergygenerationlimitedwind": [
  "Green_Infra_Wind_Energy_Generation_Limited_Wind.pdf",
  "Tier 3",
  "Wind",
  "CRISIL"
 ],
 "greenkosironjwindpowerprivatelimitedwind": [
  "Greenko_Sironj_Wind_Power_Private_Limited_Wind.pdf",
  "Tier 3",
  "Wind",
  "CARE"
 ],
 "hgbanaskanthabessprivatelimitedbess": [
  "H_G__Banaskantha_Bess_Private_Limited_BESS.pdf",
  "Tier 3",
  "BESS",
  "CARE"
 ],
 "icracomplexityindicatordec2025": [
  "ICRA_Complexity_Indicator_Dec_2025.pdf",
  "Tier 1",
  "Methodology",
  "ICRA"
 ],
 "icrapowersolarandwindratingmethodologyjuly2025": [
  "ICRA_Power_Solar_and_Wind_Rating_Methodology_July_2025.pdf",
  "Tier 1",
  "Methodology",
  "ICRA"
 ],
 "icraprojectfinanceratingmethodologynov2022": [
  "ICRA_Project_Finance_Rating_Methodology_Nov_2022.pdf",
  "Tier 1",
  "Methodology",
  "ICRA"
 ],
 "indiaratingscriteriainfrastructureprojectfinance27may2024": [
  "India_Ratings_Criteria_Infrastructure_Project_Finance_27_May_2024.pdf",
  "Tier 1",
  "Methodology",
  "India Ratings"
 ],
 "indiaratingsevaluatingcorporategovernance": [
  "India_Ratings_Evaluating_Corporate_Governance.pdf",
  "Tier 1",
  "Methodology",
  "India Ratings"
 ],
 "inoxwindlimitedwind": [
  "Inox_Wind_Limited_Wind.pdf",
  "Tier 3",
  "Wind",
  "CARE"
 ],
 "jaksonpowerprivatelimitedsolar": [
  "Jakson_Power_Private_Limited_Solar.pdf",
  "Tier 3",
  "Solar",
  "CRISIL"
 ],
 "junipergreenbesszetaprivatelimitedwindsolarbess": [
  "Juniper_Green_Bess_Zeta_Private_Limited_Wind__Solar__BESS.pdf",
  "Tier 3",
  "Wind-Solar-BESS",
  "ICRA"
 ],
 "loomsolarsolar": [
  "LoomSolar_Solar.pdf",
  "Tier 3",
  "Solar",
  "Brickwork"
 ],
 "moodysgeneralprojectfinancemethodology": [
  "Moodys_General_Project_Finance_Methodology.pdf",
  "Tier 1",
  "Methodology",
  "Moodys"
 ],
 "morjarrenewablesprivatelimitedwindsolar": [
  "Morjar_Renewables_Private_Limited_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "CARE"
 ],
 "purvahgreenpowerprivatelimitedwindsolar": [
  "Purvah_Green_Power_Private_Limited_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "CARE"
 ],
 "renewpowerwindsolar": [
  "ReNew_Power_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "Brickwork"
 ],
 "renewsandurgreenenergyprivatelimitedwindsolar": [
  "ReNew_Sandur_Green_Energy_Private_Limited_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "India Ratings"
 ],
 "renewsolarpowerprivatelimitedcaresolar": [
  "Renew_Solar_Power_Private_Limited_CARE_Solar.pdf",
  "Tier 3",
  "Solar",
  "CARE"
 ],
 "renewsolarpowerprivatelimitedindrasolar": [
  "ReNew_Solar_Power_Private_Limited_IndRa_Solar.pdf",
  "Tier 3",
  "Solar",
  "India Ratings"
 ],
 "seisitaraprivatelimitedsolar": [
  "SEI_Sitara_Private_Limited_Solar.pdf",
  "Tier 3",
  "Solar",
  "CRISIL"
 ],
 "solairepowerprivatelimitedsolar": [
  "Solaire_Power_Private_Limited_Solar.pdf",
  "Tier 3",
  "Solar",
  "CRISIL"
 ],
 "upkoraunurjaprivatelimitedsolar": [
  "UP_Koraun_Urja_Private_Limited_Solar.pdf",
  "Tier 3",
  "Solar",
  "India Ratings"
 ],
 "zenatarisrenewableenergyprivatelimitedwindsolar": [
  "Zenataris_Renewable_Energy_Private_Limited_Wind__Solar.pdf",
  "Tier 3",
  "Wind-Solar Hybrid",
  "ICRA"
 ]
}

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


def _norm(n):
    n = n.lower()
    n = n[:-4] if n.endswith('.pdf') else n
    return re.sub(r'[\s_\.\-]+', '', n)


def restore_names(corpus, apply):
    """Rename each file to its canonical name, matched on normalised name."""
    files = sorted(f for f in os.listdir(corpus) if f.lower().endswith('.pdf'))
    ok = planned = unknown = 0
    problems = []
    for f in files:
        row = CLASSIFICATION.get(_norm(f))
        if row is None:
            unknown += 1
            problems.append(f'{f}: name matches no known document')
            continue
        want = row[0]
        if want == f:
            ok += 1
            continue
        dst = os.path.join(corpus, want)
        if os.path.exists(dst):
            problems.append(f'{f}: target {want} already exists')
            unknown += 1
            continue
        print(f'  {f}')
        print(f'      -> {want}')
        planned += 1
        if apply:
            os.rename(os.path.join(corpus, f), dst)
    return ok, planned, unknown, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--manifest')
    ap.add_argument('--out')
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--classifier', help='optional JSON: {filename: [tier, category, agency]}')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    if not (a.generate or a.verify):
        print(f'Corpus: {os.path.abspath(a.corpus)}')
        print(f'Mode:   {"APPLY" if a.apply else "PREVIEW - nothing will be changed"}')
        print('-' * 74)
        ok, planned, unknown, problems = restore_names(a.corpus, a.apply)
        print('-' * 74)
        print(f'already correct: {ok}   {"renamed" if a.apply else "to rename"}: {planned}   unrecognised: {unknown}')
        if problems:
            print('\nPROBLEMS:')
            for p in problems:
                print('  ' + p)
        if not a.apply:
            print('\nPreview only. Re-run with --apply to rename, then again with')
            print('--apply --generate --out corpus/Reference_Corpus_Manifest_v3_0.csv')
            return
        if problems:
            print('\nNot regenerating the manifest while problems remain.')
            return
        a.generate = True
        a.out = a.out or os.path.join(a.corpus, 'Reference_Corpus_Manifest_v3_0.csv')
        print()

    lookup = json.load(open(a.classifier)) if a.classifier else {}

    def classify(name, txt):
        if name in lookup:
            return tuple(lookup[name])
        row = CLASSIFICATION.get(_norm(name))
        return tuple(row[1:]) if row else ('', '', '')

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
