"""
PDF importer.

Governed by ADR-0002 §5.

The importer's entire responsibility is to accept one real document and hand it
to the registry. It ENDS at successful registration.

It deliberately does not:
  * extract factual claims, tables or geometry;
  * create evidence events;
  * create statements.

That separation is structural, not stylistic. An importer that could also make
claims would be able to produce a statement whose provenance it invented in the
same breath — which is precisely how synthesized cabins came to carry evidence
links in the old engine.
"""

from __future__ import annotations

import os
import json
import hashlib
import re
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Optional

from timonelo.evidence.registry import (
    Artifact, ArtifactRegistry, RegistryError, normalize_subject_vessels, sha256_of_file,
)

PDF_MAGIC = b"%PDF-"


class ImportError_(RegistryError):
    """Raised when the input is not an acceptable source document."""


def _shared_document_decision(path, expected_sha256, source, subjects, pages):
    """Check a retained human decision supplied by a trusted local operator.

    The externally pinned physical record hash binds content, not identity.
    This library must not accept these arguments from an untrusted request.
    """
    if not path or not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ImportError_("Shared-document attribution requires a pinned governed exception.")
    try:
        raw = Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise ImportError_("Shared-document decision hash mismatch.")
        record = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise ImportError_("Shared-document decision could not be verified.") from exc
    if not isinstance(record, dict) or (
        record.get("schema") != "timonelo.shared-document-intake.v1"
        or record.get("decision") != "APPROVE"
        or not all(isinstance(record.get(key), str) and record[key].strip()
                   for key in ("actor", "occurred_on", "note"))
        or record.get("artifact_sha256") != sha256_of_file(source)
        or record.get("subject_vessels") != list(subjects)
        or not isinstance(record.get("source_identity_pages"), dict)
        or any(type(page) is not int for page in record["source_identity_pages"].values())
        or record.get("source_identity_pages") != pages
    ):
        raise ImportError_("Shared-document decision must approve the exact digest, vessel set and pages.")
    return expected_sha256


def _verify_source_identity(
    path: str, subjects: tuple[str, ...], pages: Optional[Mapping[str, int]],
) -> None:
    """Check the requested subject against the held PDF, before registration.

    Pages are one-based locators, not identity authority. The vessel name and
    IMO come from the repository identity catalog; at least one must occur in
    the page's extracted text. Filenames, notes and caller labels have no role.
    This verifies documentary identity only, not individual claims or approval.
    """
    if not subjects:
        if pages:
            raise ImportError_("Identity pages require explicit subject_vessels.")
        return
    if not isinstance(pages, Mapping) or set(pages) != set(subjects):
        raise ImportError_("source_identity_pages must locate every subject vessel.")
    if any(type(page) is not int or page < 1 for page in pages.values()):
        raise ImportError_("Source identity page must be a positive one-based integer.")

    catalog = Path(__file__).resolve().parents[3] / "knowledge" / "ships"
    from timonelo.evidence.vessel_ownership import canonical_vessel
    names = {subject: [] for subject in subjects}
    for identity in catalog.glob("*/identity.json"):
        try:
            data = json.loads(identity.read_text(encoding="utf-8"))
            # Documentary preparation is allowed while canonical admission is
            # quarantined. Publication/ownership gates retain the default
            # refusal; importing bytes cannot resolve an identity dispute.
            imo = canonical_vessel(identity.parent.name, allow_quarantined=True)
            if imo not in subjects:
                continue
            name = data.get("name", {})
            name = name.get("value") if isinstance(name, dict) else name
            if isinstance(name, str) and name.strip():
                names[imo].append(name)
        except (ValueError, TypeError, OSError):
            continue
    if any(len(values) != 1 for values in names.values()):
        raise ImportError_("Subject vessel must resolve uniquely in the canonical identity catalog.")
    try:
        import fitz
        with fitz.open(path) as document:
            if any(page > len(document) for page in pages.values()):
                raise ImportError_("Source identity page is outside the held PDF.")
            texts = {subject: document[pages[subject] - 1].get_text() for subject in subjects}
    except ImportError_:
        raise
    except Exception as exc:
        raise ImportError_("Held PDF text could not be verified for vessel identity.") from exc
    for subject, text in texts.items():
        normalized_text = " ".join(text.casefold().split())
        normalized_name = " ".join(names[subject][0].casefold().split())
        printed_imos = re.findall(r"(?<!\w)imo\s*([0-9]{7})(?!\w)", normalized_text)
        if any("IMO" + imo not in subjects for imo in printed_imos):
            raise ImportError_("Held identity page contains a conflicting IMO identity.")
        name_match = re.search(r"(?<!\w)" + re.escape(normalized_name) + r"(?!\w)", normalized_text)
        imo_match = re.search(r"(?<!\w)imo\s*" + re.escape(subject[3:]) + r"(?!\w)", normalized_text)
        if not (name_match or imo_match):
            raise ImportError_("Held source page does not establish the requested vessel identity.")


def import_pdf(
    registry: ArtifactRegistry,
    path: str,
    document_class: str,
    acquired_on: str,
    acquisition_method: str,
    publisher: Optional[str] = None,
    published_on: Optional[str] = None,
    version: Optional[str] = None,
    language: Optional[str] = None,
    notes: str = "",
    subject_vessels: Optional[Iterable[str]] = None,
    source_identity_pages: Optional[Mapping[str, int]] = None,
    shared_document_decision_path: Optional[str] = None,
    shared_document_decision_sha256: Optional[str] = None,
) -> Artifact:
    """Register one PDF with documentary identity and governed shared exceptions.

    Metadata is supplied by the acquirer, not read from the PDF's own fields:
    embedded /CreationDate and /Producer describe the file, not the document,
    and are routinely wrong or absent in operator publications. A recorded
    publication date must come from the person who obtained the document.
    """
    if not os.path.isfile(path):
        raise ImportError_(f"No file at {path!r}.")

    # Inspect and register one private snapshot. A caller replacing the source
    # after inspection must not cause different bytes to inherit its identity.
    with tempfile.TemporaryDirectory(prefix="timonelo-source-") as temporary:
        snapshot = os.path.join(temporary, os.path.basename(path))
        shutil.copyfile(path, snapshot)
        with open(snapshot, "rb") as f:
            head = f.read(len(PDF_MAGIC))
        if head != PDF_MAGIC:
            raise ImportError_(
                f"{path!r} is not a PDF (missing %PDF- header). The importer "
                "verifies the format rather than trusting the file extension."
            )

        attributed = normalize_subject_vessels(subject_vessels)
        if len(attributed) > 1:
            decision_hash = _shared_document_decision(
                shared_document_decision_path, shared_document_decision_sha256,
                snapshot, attributed, source_identity_pages,
            )
            notes = notes + ("\n" if notes else "") + "Shared-document intake decision SHA-256: " + decision_hash
        elif shared_document_decision_path is not None or shared_document_decision_sha256 is not None:
            raise ImportError_("Shared-document exception requires multiple explicit subjects.")
        _verify_source_identity(snapshot, attributed, source_identity_pages)
        return registry.register(
            path=snapshot,
            document_class=document_class,
            acquired_on=acquired_on,
            acquisition_method=acquisition_method,
            publisher=publisher,
            published_on=published_on,
            version=version,
            language=language,
            notes=notes,
            subject_vessels=attributed if subject_vessels is not None else None,
        )
