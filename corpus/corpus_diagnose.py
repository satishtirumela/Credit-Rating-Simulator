#!/usr/bin/env python3
"""
Diagnose how the files on disk differ from what the manifest expects.

Run this when corpus_restore_names.py reports unmatched files. It does not
change anything. It answers one question: were the documents altered in
transit, and if so, how?

    python corpus_diagnose.py --corpus corpus \
           --manifest corpus/Reference_Corpus_Manifest_v3_0.csv
"""
import argparse, csv, os, re, zipfile


def norm(name):
    """Reduce a filename to a comparable key: spaces, underscores and dots all
    collapse, and case is ignored. Enough to pair a renamed file with its row."""
    n = name.lower()
    n = n[:-4] if n.endswith('.pdf') else n
    n = re.sub(r'[\s_\.\-]+', '', n)
    return n


def container_of(path):
    with open(path, 'rb') as f:
        sig = f.read(5)
    if sig[:2] == b'PK':
        return 'ZIP'
    if sig[:4] == b'%PDF':
        return 'PDF'
    return 'OTHER:' + repr(sig[:4])


def zip_shape(path):
    try:
        z = zipfile.ZipFile(path)
        names = z.namelist()
        txt = sum(1 for n in names if n.lower().endswith('.txt'))
        img = sum(1 for n in names if n.lower().endswith(('.jpeg', '.jpg', '.png')))
        return f'{len(names)} entries ({img} images, {txt} text, ' \
               f'{"manifest.json" if "manifest.json" in names else "no inner manifest"})'
    except Exception as e:
        return f'unreadable as zip: {e}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--manifest', required=True)
    a = ap.parse_args()

    rows = {norm(r['filename']): r for r in csv.DictReader(open(a.manifest, encoding='utf-8'))}
    files = sorted(f for f in os.listdir(a.corpus) if f.lower().endswith('.pdf'))

    print(f'Files on disk: {len(files)}   Manifest rows: {len(rows)}')
    print('=' * 78)

    paired = unpaired = 0
    same_container = changed_container = 0
    size_same = size_diff = 0
    examples = []

    for f in files:
        k = norm(f)
        r = rows.get(k)
        p = os.path.join(a.corpus, f)
        disk_c = container_of(p)
        disk_b = os.path.getsize(p)
        if r is None:
            unpaired += 1
            examples.append(('NO MATCHING ROW', f, f'{disk_c}, {disk_b:,} bytes', ''))
            continue
        paired += 1
        man_c, man_b = r['container'], int(r['bytes'])
        if disk_c == man_c:
            same_container += 1
        else:
            changed_container += 1
        if disk_b == man_b:
            size_same += 1
        else:
            size_diff += 1
        if len(examples) < 6 and (disk_c != man_c or disk_b != man_b):
            extra = zip_shape(p) if disk_c == 'ZIP' else ''
            examples.append((
                'ALTERED', f,
                f'disk: {disk_c}, {disk_b:,} bytes',
                f'manifest: {man_c}, {man_b:,} bytes   {extra}'))

    print(f'paired with a manifest row by name : {paired}')
    print(f'no matching row at all             : {unpaired}')
    print('-' * 78)
    print(f'container UNCHANGED                : {same_container}')
    print(f'container CHANGED                  : {changed_container}   '
          f'<-- if high, the download converted the files')
    print(f'byte size identical                : {size_same}')
    print(f'byte size different                : {size_diff}')
    print('=' * 78)

    if examples:
        print('EXAMPLES\n')
        for tag, name, a1, a2 in examples:
            print(f'  [{tag}] {name}')
            print(f'      {a1}')
            if a2:
                print(f'      {a2}')
            print()

    print('WHAT THIS MEANS')
    if changed_container and same_container == 0:
        print('  Every paired file changed container format. The download did not')
        print('  hand back the original bytes -- it re-rendered the documents.')
        print('  The manifest cannot verify these, because they are not the same files.')
    elif size_diff and not changed_container:
        print('  Same container, different size: the files were re-compressed or')
        print('  re-packaged in transit. Content may or may not be intact.')
    elif size_same and changed_container == 0 and size_diff == 0:
        print('  Files look byte-identical. If hashes still failed, the mismatch is')
        print('  inside the payload rather than the container -- report back.')
    print()
    print('  Either way: the safe fix is to locate the ORIGINAL local copies of')
    print('  these 41 files. If they cannot be found, the manifest can be')
    print('  regenerated against whatever set you do have -- but read the note')
    print('  the assistant gives you before doing that, because a regenerated')
    print('  manifest verifies integrity going forward and proves nothing about')
    print('  what happened in the past.')


if __name__ == '__main__':
    main()
