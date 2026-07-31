#!/usr/bin/env python3
"""
Restore corpus filenames from the manifest, matching on CONTENT.

Why this exists
---------------
Downloading the corpus through a web interface can rewrite the filenames --
underscores become spaces, dots become underscores, and so on. The bytes are
untouched, so every document is still the right document; only the labels are
wrong. corpus_manifest.py --verify then reports each file twice, once as
unexpected and once as missing, which looks far more alarming than it is.

This tool does not guess at names. It hashes each file on disk exactly as the
manifest does, finds the manifest row with the same hash, and renames the file
to the name that row carries. A file whose hash matches nothing is left alone
and reported, because that is a real problem rather than a cosmetic one.

    python corpus_restore_names.py --corpus corpus \
           --manifest corpus/Reference_Corpus_Manifest_v3_0.csv          # preview
    python corpus_restore_names.py --corpus corpus \
           --manifest corpus/Reference_Corpus_Manifest_v3_0.csv --apply  # do it
"""
import argparse, csv, hashlib, os, sys, zipfile


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


def payload_sha256(path):
    """Identical rule to corpus_manifest.py, so the hashes are comparable."""
    if container_of(path) == 'ZIP':
        z = zipfile.ZipFile(path)
        names = sorted(n for n in z.namelist()
                       if n.lower().endswith(('.txt', '.jpeg', '.jpg', '.png')))
        h = hashlib.sha256()
        for n in names:
            h.update(z.read(n))
        return h.hexdigest()
    return sha256_file(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--apply', action='store_true',
                    help='actually rename; without this the run is a preview')
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.manifest, encoding='utf-8')))
    by_hash = {r['payload_sha256']: r['filename'] for r in rows}
    if len(by_hash) != len(rows):
        sys.exit('Manifest contains duplicate payload hashes; cannot match unambiguously.')

    files = sorted(f for f in os.listdir(a.corpus) if f.lower().endswith('.pdf'))
    print(f'Corpus:   {os.path.abspath(a.corpus)}')
    print(f'Manifest: {a.manifest}  ({len(rows)} rows)')
    print(f'Files on disk: {len(files)}')
    print(f'Mode:     {"APPLY" if a.apply else "PREVIEW — nothing will be changed"}')
    print('-' * 74)

    correct = planned = unmatched = 0
    problems = []
    for f in files:
        src = os.path.join(a.corpus, f)
        try:
            h = payload_sha256(src)
        except Exception as e:
            problems.append(f'{f}: could not read ({e})')
            unmatched += 1
            continue
        want = by_hash.get(h)
        if want is None:
            problems.append(f'{f}: content matches no manifest row')
            unmatched += 1
            continue
        if want == f:
            correct += 1
            continue
        dst = os.path.join(a.corpus, want)
        if os.path.exists(dst):
            problems.append(f'{f}: target {want} already exists')
            unmatched += 1
            continue
        print(f'  {f}')
        print(f'      -> {want}')
        planned += 1
        if a.apply:
            os.rename(src, dst)

    print('-' * 74)
    print(f'already correct: {correct}   '
          f'{"renamed" if a.apply else "to rename"}: {planned}   '
          f'unmatched: {unmatched}')

    if problems:
        print('\nPROBLEMS — these are real, not cosmetic:')
        for p in problems:
            print('  ' + p)
        print('\nA file whose content matches no manifest row is either not part of '
              'the corpus or has been altered. Do not rename it; find out why.')

    missing = set(by_hash.values()) - set(os.listdir(a.corpus))
    if a.apply and missing:
        print(f'\nStill missing after rename: {len(missing)}')
        for m in sorted(missing):
            print('  ' + m)

    if not a.apply and planned:
        print('\nThis was a preview. Re-run with --apply to perform the renames.')
    elif a.apply and not problems and not missing:
        print('\nAll filenames now match the manifest. Re-run corpus_manifest.py '
              '--verify to confirm.')


if __name__ == '__main__':
    main()
