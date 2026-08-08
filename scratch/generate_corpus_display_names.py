"""
Generates corpus/Corpus_Display_Names_v3_0.csv from corpus/Reference_Corpus_Manifest_v3_0.csv.

Mechanical transform: strip the file extension, collapse a run of 2+ underscores
(multi-technology filenames like "Wind__Solar") into a single space, then replace any
remaining single underscore with a space. A small manual-correction table fixes tokens
the mechanical pass would otherwise mangle -- agency acronym casing, apostrophes, and
ampersands encoded as underscores.

Re-run this script whenever new files are added to the corpus manifest.
"""

import csv
import os
import re

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")
MANIFEST_PATH = os.path.join(CORPUS_DIR, "Reference_Corpus_Manifest_v3_0.csv")
OUT_PATH = os.path.join(CORPUS_DIR, "Corpus_Display_Names_v3_0.csv")

TOKEN_CORRECTIONS = {
    "Crisil": "CRISIL",
    "Moodys": "Moody's",
    "H_G": "H&G",
}


def humanize(filename: str) -> str:
    name = re.sub(r"\.[A-Za-z0-9]+$", "", filename)
    for token, replacement in TOKEN_CORRECTIONS.items():
        name = name.replace(token, replacement)
    name = re.sub(r"_{2,}", " ", name)
    name = name.replace("_", " ")
    return re.sub(r"\s+", " ", name).strip()


def main():
    rows = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row.get("filename", "").strip()
            if fname:
                rows.append((fname, humanize(fname)))

    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "display_name"])
        for fname, disp in rows:
            writer.writerow([fname, disp])

    print(f"Wrote {len(rows)} display names to {OUT_PATH}")
    for fname, disp in rows:
        print(f"  {fname} -> {disp}")


if __name__ == "__main__":
    main()
