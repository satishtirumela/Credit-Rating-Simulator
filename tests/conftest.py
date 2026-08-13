import json
import os
import re

from app.engine.scoring import _normalize_inputs

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "project.schema.json")

with open(_SCHEMA_PATH, "r", encoding="utf-8") as _sf:
    _SCHEMA_PROPERTIES = set(json.load(_sf).get("properties", {}).keys())


def to_schema_conformant_inputs(raw_inputs):
    """
    Converts fixture-format (narrative-key) project inputs into a schema-conformant payload,
    via the same _normalize_inputs() + schema-property filter that
    tests/test_engine.py::test_schema_conformance uses to validate the fixture against
    schemas/project.schema.json. Used to build real `approved_data` payloads for API tests that
    exercise the live approve path (app.firestore.approve_project_document's schema-validation
    gate), since the fixture's own narrative-key inputs are not schema-conformant as-is.
    """
    norm = _normalize_inputs(raw_inputs)
    converted = {}
    for k, v in norm.items():
        if k in _SCHEMA_PROPERTIES and v is not None:
            if k == "discount_rate_as_of" and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(v)):
                continue
            converted[k] = v
    return converted
