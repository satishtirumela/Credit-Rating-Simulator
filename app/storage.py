"""
Firebase Storage integration helper for uploading and retrieving project files (.docx / .xlsx).
Falls back to local file storage if Firebase credentials / bucket are not initialized.
"""

import os
import shutil
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "storage_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

_firebase_initialized = False

try:
    import firebase_admin
    from firebase_admin import credentials, storage

    if not firebase_admin._apps:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
            firebase_admin.initialize_app(cred, {"storageBucket": bucket_name} if bucket_name else {})
            _firebase_initialized = True
        else:
            # Check default app initialization
            try:
                firebase_admin.initialize_app()
                _firebase_initialized = True
            except Exception:
                _firebase_initialized = False
except Exception:
    _firebase_initialized = False


def save_project_file(project_id: str, filename: str, content_bytes: bytes) -> Dict[str, Any]:
    """
    Saves a project file (.docx / .xlsx) under projects/{project_id}/{filename} in Firebase Storage,
    or stores it locally under storage_uploads/projects/{project_id}/{filename}.
    """
    safe_pid = project_id.strip() or "default_project"
    rel_path = f"projects/{safe_pid}/{filename}"

    # Always write to local storage backup
    local_proj_dir = os.path.join(UPLOAD_DIR, "projects", safe_pid)
    os.makedirs(local_proj_dir, exist_ok=True)
    local_file_path = os.path.join(local_proj_dir, filename)

    with open(local_file_path, "wb") as f:
        f.write(content_bytes)

    storage_provider = "local"
    remote_url = None

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".docx":
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext == ".xlsx":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        content_type = "application/octet-stream"

    if _firebase_initialized:
        try:
            b_name = os.getenv("FIREBASE_STORAGE_BUCKET")
            bucket = storage.bucket(name=b_name) if b_name else storage.bucket()
            blob = bucket.blob(rel_path)
            blob.upload_from_string(content_bytes, content_type=content_type)
            remote_url = blob.public_url or f"gs://{bucket.name}/{rel_path}"
            storage_provider = "firebase_storage"
        except Exception as e:
            storage_provider = f"local (firebase upload deferred: {str(e)})"

    return {
        "project_id": safe_pid,
        "filename": filename,
        "path": rel_path,
        "local_path": local_file_path,
        "storage_provider": storage_provider,
        "remote_url": remote_url,
        "size_bytes": len(content_bytes)
    }


def get_project_file_bytes(project_id: str, filename: str) -> bytes:
    """
    Downloads file bytes directly from Firebase Storage bucket at projects/{project_id}/{filename}.
    Falls back to local file storage if Firebase Storage fails or is unavailable.
    """
    safe_pid = project_id.strip() or "default_project"
    rel_path = f"projects/{safe_pid}/{filename}"

    if _firebase_initialized:
        try:
            b_name = os.getenv("FIREBASE_STORAGE_BUCKET")
            bucket = storage.bucket(name=b_name) if b_name else storage.bucket()
            blob = bucket.blob(rel_path)
            if blob.exists():
                return blob.download_as_bytes()
        except Exception as e:
            print(f"[STORAGE WARNING] Failed to download '{rel_path}' from Firebase Storage: {str(e)}. Falling back to local storage.")

    local_file_path = os.path.join(UPLOAD_DIR, "projects", safe_pid, filename)
    if os.path.exists(local_file_path):
        with open(local_file_path, "rb") as f:
            return f.read()

    raise FileNotFoundError(f"File '{rel_path}' not found in Firebase Storage or local uploads")
