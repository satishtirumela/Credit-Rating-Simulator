#!/usr/bin/env python3
"""
Can the grounding step actually read these documents?

The 37 converted files are now real PDFs instead of ZIP archives of OCR text.
That is only a problem if the conversion dropped the text layer, leaving pages
that are pictures of words. This script settles that question and nothing else.

    pip install pypdf
    python corpus_textcheck.py --corpus corpus

Read the VERDICT at the bottom.
"""
import argparse, os, sys

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit('pypdf is not installed. Run:  pip install pypdf')


def container_of(path):
    with open(path, 'rb') as f:
        sig = f.read(5)
    return 'ZIP' if sig[:2] == b'PK' else ('PDF' if sig[:4] == b'%PDF' else 'OTHER')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--sample', type=int, default=3,
                    help='how many documents to print a text sample from')
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.corpus) if f.lower().endswith('.pdf'))
    pdfs = [f for f in files if container_of(os.path.join(a.corpus, f)) == 'PDF']
    zips = [f for f in files if container_of(os.path.join(a.corpus, f)) == 'ZIP']

    print(f'Files: {len(files)}   real PDFs: {len(pdfs)}   ZIP archives: {len(zips)}')
    print('=' * 74)

    good = poor = broken = 0
    total_pages = pages_with_text = 0
    worst = []
    samples = []

    for f in pdfs:
        p = os.path.join(a.corpus, f)
        try:
            r = PdfReader(p)
        except Exception as e:
            broken += 1
            worst.append((f, f'cannot open: {e}'))
            continue
        n = len(r.pages)
        withtext = 0
        firsttext = ''
        for i, pg in enumerate(r.pages):
            try:
                t = (pg.extract_text() or '').strip()
            except Exception:
                t = ''
            if len(t) > 40:
                withtext += 1
                if not firsttext:
                    firsttext = ' '.join(t.split())[:220]
        total_pages += n
        pages_with_text += withtext
        ratio = withtext / n if n else 0
        if ratio >= 0.8:
            good += 1
            if len(samples) < a.sample and firsttext:
                samples.append((f, n, firsttext))
        elif ratio >= 0.3:
            poor += 1
            worst.append((f, f'only {withtext} of {n} pages carry text'))
        else:
            broken += 1
            worst.append((f, f'only {withtext} of {n} pages carry text — image-only'))

    print(f'documents with a good text layer (80%+ of pages) : {good}')
    print(f'documents with a partial text layer (30-80%)     : {poor}')
    print(f'documents with little or no text (under 30%)     : {broken}')
    print(f'pages carrying text: {pages_with_text} of {total_pages}'
          + (f'  ({100*pages_with_text/total_pages:.0f}%)' if total_pages else ''))
    print('=' * 74)

    if samples:
        print('TEXT SAMPLES — confirm these read like the real documents\n')
        for f, n, t in samples:
            print(f'  {f}  ({n} pages)')
            print(f'    "{t}..."\n')

    if worst:
        print('DOCUMENTS WITH WEAK OR NO TEXT\n')
        for f, why in worst[:12]:
            print(f'  {f}\n      {why}')
        if len(worst) > 12:
            print(f'  ... and {len(worst)-12} more')
        print()

    print('VERDICT')
    if broken == 0 and poor == 0:
        print('  Every document has a solid text layer. The conversion LOST NOTHING that')
        print('  matters. Regenerate the manifest and carry on -- and note that the corpus')
        print('  is now uniformly PDF, which makes the ingestion contract simpler than the')
        print('  mixed-format one it replaces.')
    elif broken == 0:
        print('  Text is present throughout, though a few documents have gaps. Usable.')
        print('  Regenerate the manifest, and if a grounding lookup later comes back empty,')
        print('  check the partial documents above before concluding the source is silent.')
    else:
        print(f'  {broken} document(s) have little or no extractable text. Those pages are')
        print('  pictures of words, and the grounding step cannot read them. Find the')
        print('  ORIGINAL copies of at least those documents before relying on the corpus.')


if __name__ == '__main__':
    main()
