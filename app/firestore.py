"""
Firestore project management and field provenance engine.
Manages project document persistence, leaf-level field provenance calculation,
type normalization, and approval workflow state.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from dotenv import load_dotenv
import jsonschema

load_dotenv()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "storage_uploads")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "project.schema.json")


def _get_project_schema() -> Dict[str, Any]:
    """Loads schemas/project.schema.json fresh on each call (no caching), matching the same
    pattern app/main.py's _get_schema() already uses for the /score endpoint's validate_schema
    flag."""
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_guard_logged = False


def _firestore_guard_reason() -> Optional[str]:
    """
    Returns the trigger reason if the test/diagnostic guard should force the local JSON
    fallback instead of real Firestore, else None. Checked before any real Firestore
    initialization is attempted, so a guarded process never touches production data.
    """
    if os.getenv("PYTEST_CURRENT_TEST"):
        return "PYTEST_CURRENT_TEST detected"
    if os.getenv("CRS_FORCE_LOCAL_FIRESTORE", "").strip().lower() in ("1", "true", "yes", "on"):
        return "CRS_FORCE_LOCAL_FIRESTORE set"
    return None


def get_firestore_client_or_none():
    """
    Centralized Firestore client resolution used by every read/write function in this module
    and by app.extraction.save_to_firestore. Returns a real firebase_admin firestore client when
    genuine credentials are configured and no guard condition is active; returns None otherwise,
    signaling every caller to use the local JSON fallback for both reads and writes -- a guarded
    process never talks to real Firestore at all, for either direction.

    Guard conditions (checked first, before any real Firestore initialization is attempted):
    1. PYTEST_CURRENT_TEST is set -- pytest sets this automatically for every test, zero config.
    2. CRS_FORCE_LOCAL_FIRESTORE is set to a truthy value -- explicit opt-in for ad-hoc diagnostic
       scripts that must not risk touching real production data. Deliberately not named around
       "diagnostic mode" -- some diagnostic scripts (e.g. a Firestore staleness audit) legitimately
       need to read real Firestore, so the flag name describes the protection applied, not the
       general activity being performed.
    """
    global _guard_logged
    reason = _firestore_guard_reason()
    if reason:
        if not _guard_logged:
            print(f"[CRS] Firestore guard active — routing to local fallback (reason: {reason})")
            _guard_logged = True
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()

        return firestore.client()
    except Exception:
        return None


def normalize_value(val: Any) -> Any:
    """
    Normalizes scalar values for strict equivalence checks.
    Converts numeric strings ("150", "0.88") to floats, normalizes empty strings "" / None to None,
    and strips whitespace from strings.
    """
    if val is None or val == "":
        return None

    if isinstance(val, bool):
        return val

    if isinstance(val, (int, float)):
        # Normalize float representation
        return float(val)

    if isinstance(val, str):
        cleaned = val.strip()
        if not cleaned:
            return None
        # Try numeric conversion
        try:
            return float(cleaned)
        except ValueError:
            return cleaned.upper() if cleaned.startswith("TECH_") or cleaned.startswith("STATUS_") or cleaned.startswith("PERMIT_") else cleaned

    return val


def compute_field_provenance(extracted: Any, approved: Any, path: str = "") -> Dict[str, str]:
    """
    Recursively compares raw extracted_data against human approved_data to calculate
    leaf-level field provenance ("extracted" vs "user-corrected").
    """
    provenance: Dict[str, str] = {}

    if isinstance(approved, dict) and isinstance(extracted, dict):
        all_keys = set(approved.keys()).union(set(extracted.keys()))
        for k in sorted(all_keys):
            field_path = f"{path}.{k}" if path else k
            sub_ext = extracted.get(k)
            sub_app = approved.get(k)
            provenance.update(compute_field_provenance(sub_ext, sub_app, field_path))
    elif isinstance(approved, list) and isinstance(extracted, list):
        max_len = max(len(approved), len(extracted))
        for idx in range(max_len):
            field_path = f"{path}[{idx}]"
            sub_ext = extracted[idx] if idx < len(extracted) else None
            sub_app = approved[idx] if idx < len(approved) else None
            provenance.update(compute_field_provenance(sub_ext, sub_app, field_path))
    else:
        # Leaf level scalar comparison
        norm_ext = normalize_value(extracted)
        norm_app = normalize_value(approved)
        leaf_key = path if path else "value"
        if norm_ext == norm_app:
            provenance[leaf_key] = "extracted"
        else:
            provenance[leaf_key] = "user-corrected"

    return provenance


def get_project_document(project_id: str) -> Dict[str, Any]:
    """
    Retrieves project document from Firestore (or local file fallback).
    """
    safe_pid = project_id.strip() or "default_project"

    db = get_firestore_client_or_none()
    if db is not None:
        try:
            doc = db.collection("projects").document(safe_pid).get()
            if doc.exists:
                data = doc.to_dict()
                data["_id"] = doc.id
                return data
        except Exception as err:
            print(f"[FIRESTORE WARNING] Failed to query Firestore document for '{safe_pid}': {err}. Trying local fallback.")

    # Local fallback file
    local_path = os.path.join(UPLOAD_DIR, f"firestore_{safe_pid}.json")
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "project_id": safe_pid,
        "status": "draft",
        "extracted_data": {},
        "approved_data": None,
        "field_provenance": {}
    }


def get_all_projects_from_firestore() -> List[Dict[str, Any]]:
    """
    Returns a list of all project documents stored in Cloud Firestore (or local file fallback).
    """
    projects = []
    db = get_firestore_client_or_none()
    if db is not None:
        try:
            docs = db.collection("projects").stream()
            for doc in docs:
                p_data = doc.to_dict()
                p_data["project_id"] = doc.id
                projects.append(p_data)
            if projects:
                return projects
        except Exception:
            pass

    # Local fallback
    if os.path.exists(UPLOAD_DIR):
        for fname in os.listdir(UPLOAD_DIR):
            if fname.startswith("firestore_") and fname.endswith(".json"):
                fpath = os.path.join(UPLOAD_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        projects.append(json.load(f))
                except Exception:
                    pass

    return projects


def approve_project_document(project_id: str, approved_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates approved_data against schemas/project.schema.json, computes leaf field
    provenance, and saves approved_data, field_provenance, and status = "approved" to Cloud
    Firestore under projects/{project_id}.

    Raises jsonschema.ValidationError if approved_data does not conform to the schema. This
    check runs before any Firestore read or write (including the local-fallback write path)
    -- placed here, ahead of the try/except around the Firestore call below, so a validation
    failure is never caught by that except and silently downgraded into a "successful" local
    fallback write.
    """
    schema = _get_project_schema()
    if schema:
        jsonschema.validate(instance=approved_data, schema=schema)

    safe_pid = project_id.strip() or "default_project"
    doc_data = get_project_document(safe_pid)

    extracted_data = doc_data.get("extracted_data", {})
    provenance = compute_field_provenance(extracted_data, approved_data)

    db = get_firestore_client_or_none()
    if db is not None:
        try:
            from firebase_admin import firestore
            doc_ref = db.collection("projects").document(safe_pid)

            update_payload = {
                "project_id": safe_pid,
                "approved_data": approved_data,
                "field_provenance": provenance,
                "status": "approved",
                "approved_at": firestore.SERVER_TIMESTAMP
            }
            doc_ref.set(update_payload, merge=True)
            return {
                "status": "success",
                "message": f"Successfully approved project '{safe_pid}'",
                "project_id": safe_pid,
                "field_provenance": provenance,
                "approved_data": approved_data
            }
        except Exception:
            pass  # fall through to local fallback below

    # Local fallback update
    local_path = os.path.join(UPLOAD_DIR, f"firestore_{safe_pid}.json")
    doc_data["approved_data"] = approved_data
    doc_data["field_provenance"] = provenance
    doc_data["status"] = "approved"
    doc_data["approved_at"] = "local_timestamp"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, default=str)
    return {
        "status": "success",
        "message": f"Successfully approved project '{safe_pid}' (local fallback)",
        "project_id": safe_pid,
        "field_provenance": provenance,
        "approved_data": approved_data
    }


def save_score_document(project_id: str, score_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves the completed score_project() output object under 'score' key in Cloud Firestore
    document projects/{project_id}.
    """
    safe_pid = project_id.strip() or "default_project"
    doc_data = get_project_document(safe_pid)

    db = get_firestore_client_or_none()
    if db is not None:
        try:
            from firebase_admin import firestore
            doc_ref = db.collection("projects").document(safe_pid)

            update_payload = {
                "score": score_data,
                "scored_at": firestore.SERVER_TIMESTAMP
            }
            doc_ref.set(update_payload, merge=True)
            return {"status": "success", "project_id": safe_pid}
        except Exception:
            pass  # fall through to local fallback below

    local_path = os.path.join(UPLOAD_DIR, f"firestore_{safe_pid}.json")
    doc_data["score"] = score_data
    doc_data["scored_at"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, default=str)
    return {"status": "success", "project_id": safe_pid}
