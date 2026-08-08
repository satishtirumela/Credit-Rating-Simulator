"""
Shared enum-code and field-name display-label lookup.

Single source of truth: schemas/display_labels.json, keyed on the CORE Appendix A
enum codes and CORE Appendix B field paths defined in project.schema.json. Both this
module (used by app/rationale/draft.py and app/pdf.py) and the frontend (which fetches
GET /api/display-labels) read the exact same file, so a new enum code or field only
needs to be added in one place.

Codes/paths not yet in the table fall back to a mechanical humanization rather than
showing the raw code -- a readable-if-imperfect default until someone adds a proper
entry, never a raw schema code shown to a user.
"""

import json
import os
import re
from typing import Any, Dict

DISPLAY_LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "display_labels.json")

_ENUM_LABELS: Dict[str, str] = {}
_FIELD_LABELS: Dict[str, str] = {}
_loaded = False

_ARRAY_INDEX_RE = re.compile(r"\[\d+\]")


def _load() -> None:
    global _loaded, _ENUM_LABELS, _FIELD_LABELS
    if _loaded:
        return
    _loaded = True
    if os.path.exists(DISPLAY_LABELS_PATH):
        with open(DISPLAY_LABELS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _ENUM_LABELS = data.get("enum_labels", {})
        _FIELD_LABELS = data.get("field_labels", {})


def get_display_labels() -> Dict[str, Any]:
    """Returns the full {enum_labels, field_labels} dict, e.g. for serving via the API."""
    _load()
    return {"enum_labels": _ENUM_LABELS, "field_labels": _FIELD_LABELS}


def _humanize_enum_code(code: str) -> str:
    words = code.replace("-", "_").split("_")
    return " ".join(w.capitalize() for w in words if w)


def _humanize_field_path(path: str) -> str:
    normalized = _ARRAY_INDEX_RE.sub("", path)
    parts = re.split(r"[.\[\]_/]+", normalized)
    return " ".join(p.capitalize() for p in parts if p)


def label_for_enum(code: Any) -> str:
    """Human-readable label for a CORE Appendix A enum code, e.g. 'OFFTAKER_DISCOM' -> 'DISCOM'."""
    if not code:
        return ""
    _load()
    code_str = str(code)
    if code_str in _ENUM_LABELS:
        return _ENUM_LABELS[code_str]
    return _humanize_enum_code(code_str)


def label_for_field(path: Any) -> str:
    """
    Human-readable name for a CORE Appendix B field path, e.g. 'offtakers[2].rating_or_grade'
    -> 'Offtaker Rating'. Array indices are stripped before lookup so every instance of a
    repeated field (debt_instruments[], offtakers[]) shares one entry.
    """
    if not path:
        return ""
    _load()
    path_str = str(path)
    if path_str in _FIELD_LABELS:
        return _FIELD_LABELS[path_str]
    normalized = _ARRAY_INDEX_RE.sub("[]", path_str)
    if normalized in _FIELD_LABELS:
        return _FIELD_LABELS[normalized]
    return _humanize_field_path(path_str)
