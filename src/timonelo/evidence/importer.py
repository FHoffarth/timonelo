"""
PDF importer.

Governed by ADR-0002 §5.

The importer's entire responsibility is to accept one real document and hand it
to the registry. It ENDS at successful registration.

It deliberately does not:
  * extract text, tables or geometry;
  * create evidence events;
  * create statements.

That separation is structural, not stylistic. An importer that could also make
claims would be able to produce a statement whose provenance it invented in the
same breath — which is precisely how synthesized cabins came to carry evidence
links in the old engine.
"""

from __future__ import annotations

import os
from typing import Optional

from timonelo.evidence.registry import Artifact, ArtifactRegistry, RegistryError

PDF_MAGIC = b"%PDF-"


class ImportError_(RegistryError):
    """Raised when the input is not an acceptable source document."""


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
) -> Artifact:
    """Register one PDF. Returns the Artifact. Does nothing else.

    Metadata is supplied by the acquirer, not read from the PDF's own fields:
    embedded /CreationDate and /Producer describe the file, not the document,
    and are routinely wrong or absent in operator publications. A recorded
    publication date must come from the person who obtained the document.
    """
    if not os.path.isfile(path):
        raise ImportError_(f"No file at {path!r}.")

    with open(path, "rb") as f:
        head = f.read(len(PDF_MAGIC))
    if head != PDF_MAGIC:
        raise ImportError_(
            f"{path!r} is not a PDF (missing %PDF- header). The importer "
            "verifies the format rather than trusting the file extension."
        )

    artifact = registry.register(
        path=path,
        document_class=document_class,
        acquired_on=acquired_on,
        acquisition_method=acquisition_method,
        publisher=publisher,
        published_on=published_on,
        version=version,
        language=language,
        notes=notes,
    )

    # The importer stops here. Nothing downstream is created.
    return artifact
