"""
src/timonelo/harvester/verifier.py

Raw byte-level verification, integrity checking, and metadata extraction for PDF artifacts.
"""

import io
import hashlib
from typing import Tuple, Dict, Any, Optional
import pypdf


def compute_bytes_sha256(data: bytes) -> str:
    """Computes deterministic SHA-256 digest over raw bytes."""
    return hashlib.sha256(data).hexdigest()


def verify_pdf_bytes(data: bytes) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies that raw bytes represent a valid, intact PDF document.
    Returns: (is_valid, error_reason, metadata_dict)
    """
    if not data:
        return False, "EMPTY_PAYLOAD", {}

    # 1. Magic Bytes Check
    if not data.startswith(b"%PDF-"):
        # Check if it looks like HTML masquerading as PDF
        if data.strip().startswith(b"<!DOCTYPE") or data.strip().startswith(b"<html") or b"<html" in data[:100].lower():
            return False, "HTML_MASQUERADING_AS_PDF", {}
        return False, "INVALID_MAGIC_BYTES_NOT_PDF", {}

    # 2. Parseability & Integrity Check
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        page_count = len(reader.pages)
        if page_count == 0:
            return False, "ZERO_PAGES", {}

        # Extract text from first page
        first_page_text = ""
        try:
            first_page_text = reader.pages[0].extract_text() or ""
            # If multi-page, also peek at page 2 for rich metadata (e.g. edition/legend)
            if page_count > 1:
                p2_text = reader.pages[1].extract_text() or ""
                first_page_text = f"{first_page_text}\n{p2_text}"
        except Exception:
            first_page_text = ""

        # Extract PDF metadata dict
        meta_info = {}
        if reader.metadata:
            meta_info = {k: str(v) for k, v in reader.metadata.items()}

        sha256 = compute_bytes_sha256(data)
        file_size_bytes = len(data)

        verification_data = {
            "sha256": sha256,
            "page_count": page_count,
            "file_size_bytes": file_size_bytes,
            "first_page_text": first_page_text,
            "pdf_title": meta_info.get("/Title") or meta_info.get("Title"),
            "pdf_creator": meta_info.get("/Creator") or meta_info.get("Creator"),
            "mime_type": "application/pdf"
        }

        return True, "VALID_PDF", verification_data

    except Exception as exc:
        return False, f"CORRUPT_PDF_PARSE_ERROR: {str(exc)}", {}
