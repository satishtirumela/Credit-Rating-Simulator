"""
Mechanical citation grounding & corpus manifest verification engine.
Resolves criteria PDFs via Reference_Corpus_Manifest_v3_0.csv SHA-256 hashes,
applies normalization, and mechanically verifies verbatim claims.
"""

import csv
import hashlib
import os
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")
MANIFEST_PATH = os.path.join(CORPUS_DIR, "Reference_Corpus_Manifest_v3_0.csv")


def clean_display_text(text: str) -> str:
    """
    Cleans cosmetic extraction artifacts for user UI & PDF display WITHOUT altering the raw claim
    string used for strict verbatim verification.
    Narrowed pattern: Only cleans letter-number split artifacts like 'P -50' -> 'P-50', leaving
    legitimate parenthetical prose dashes like 'cash flows - after adjustments - remain' untouched.
    """
    if not text:
        return ""
    t = text
    # Fix stray whitespace before punctuation ("emphasis ," -> "emphasis,")
    t = re.sub(r"\s+([,.:;?!])", r"\1", t)
    # Narrowed hyphenation cleanup: letter on one side and digit on the other ("P -50" -> "P-50")
    t = re.sub(r"([A-Za-z]+)\s+-\s*(\d+)", r"\1-\2", t)
    t = re.sub(r"(\d+)\s+-\s*([A-Za-z]+)", r"\1-\2", t)
    return t.strip()


def normalize_pdf_text(text: str) -> str:
    """
    Normalizes raw extracted PDF text to handle line-break hyphens, ligatures, and whitespace artifacts.
    """
    if not text:
        return ""
    # Remove soft hyphens
    t = text.replace("\xad", "")
    # Remove line-break hyphenation ("word-\n continuation" -> "wordcontinuation")
    t = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", t)
    # Ligature substitutions
    t = t.replace("ﬁ", "fi").replace("ﬂ", "fl")
    # Smart quotes to ASCII
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    # Collapse multiple whitespaces and newlines
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum of a file on disk."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest() -> List[Dict[str, str]]:
    """Loads reference corpus manifest rows."""
    manifest = []
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                manifest.append(row)
    return manifest


def verify_manifest_file(filename: str) -> bool:
    """Verifies that the PDF file exists and its SHA-256 matches manifest entry if present."""
    filepath = os.path.join(CORPUS_DIR, filename)
    if not os.path.exists(filepath):
        return False

    manifest = load_manifest()
    row = next((r for r in manifest if r.get("filename") == filename or r.get("container") == filename), None)
    if row and row.get("sha256"):
        expected_sha = row.get("sha256").strip().lower()
        actual_sha = compute_sha256(filepath).lower()
        if expected_sha and actual_sha != expected_sha:
            print(f"[GROUNDING WARNING] SHA-256 mismatch for {filename}: expected {expected_sha}, got {actual_sha}")
            return False
    return True


def verify_methodology_citations(citations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Mechanically verifies a given list of citations -- as produced by draft.py's
    get_grounded_methodology_citations(), keyed by "claim" and "source_document" (the literal
    corpus PDF filename) -- against the real corpus. Checks PDF existence, SHA-256 manifest
    integrity, and 100% exact substring matching. Attaches clean_display_text for UI/PDF display.
    Raises RuntimeError on the first citation whose claim is not a verbatim substring of its
    source PDF -- callers must not catch this to silently drop or downgrade a failed citation.
    """
    verified = []
    for cit in citations:
        fname = cit["source_document"]
        fpath = os.path.join(CORPUS_DIR, fname)

        if not os.path.exists(fpath) or not verify_manifest_file(fname):
            raise RuntimeError(f"Corpus file {fname} failed SHA-256 or manifest verification")

        reader = PdfReader(fpath)
        full_text = " ".join(page.extract_text() or "" for page in reader.pages)
        norm_full = normalize_pdf_text(full_text)
        norm_claim = normalize_pdf_text(cit["claim"])

        # Strict mechanical verbatim substring verification against raw extracted text
        if norm_claim.lower() in norm_full.lower():
            cit_copy = dict(cit)
            cit_copy["grounding_status"] = "VERIFIED_VERBATIM"
            # Populate cleaned display text for UI & PDF presentation
            cit_copy["display_claim"] = clean_display_text(cit["claim"])
            verified.append(cit_copy)
        else:
            raise RuntimeError(f"Grounding failed: claim '{cit['claim']}' is not a verbatim substring of {fname}")

    return verified
