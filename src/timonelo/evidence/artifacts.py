"""
Artifact store — the floor beneath every trust property.

Governed by ADR-0002 §1, ADR-0003 §3.

An artifact is a source document we PHYSICALLY POSSESS. Its identity is the
SHA-256 of its bytes, computed here, never supplied by a caller.

This closes the defect that motivated the whole redesign: the knowledge base
contained 15,090 evidence links whose digests were hand-typed hex patterns, and
`hashlib` was never once used to hash a document. Content addressing requires
bytes you hold; a citation you never dereference is unverifiable.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional

from timonelo.canonical import canonical_dump, canonical_dumps

CHUNK = 1 << 20


def sha256_of_file(path: str) -> str:
    """Digest of the bytes on disk. The only way a digest may be produced."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Artifact:
    """A source document held in the store.

    `document_class` determines which claims this artifact is CAPABLE of
    supporting (see questions.py). A marketing deck plan cannot support a
    stateroom area; a shipyard general arrangement can. Recording the class at
    ingest is what stops the first evidence record from overreaching.
    """
    sha256: str
    filename: str
    document_class: str
    obtained_on: str
    obtained_from: str
    edition: Optional[str] = None
    published_on: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "sha256": self.sha256,
            "filename": self.filename,
            "document_class": self.document_class,
            "obtained_on": self.obtained_on,
            "obtained_from": self.obtained_from,
            "edition": self.edition,
            "published_on": self.published_on,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(d: Dict[str, object]) -> "Artifact":
        return Artifact(
            sha256=str(d["sha256"]),
            filename=str(d["filename"]),
            document_class=str(d["document_class"]),
            obtained_on=str(d["obtained_on"]),
            obtained_from=str(d["obtained_from"]),
            edition=d.get("edition"),          # type: ignore[arg-type]
            published_on=d.get("published_on"),  # type: ignore[arg-type]
            notes=str(d.get("notes", "")),
        )


class ArtifactStore:
    """Content-addressed store of possessed source documents.

    Empty by construction. Nothing may be registered without a file on disk.
    """

    def __init__(self, root: str):
        self.root = root
        self.blobs = os.path.join(root, "blobs")
        self.index_path = os.path.join(root, "index.json")
        os.makedirs(self.blobs, exist_ok=True)
        self._index: Dict[str, Artifact] = {}
        if os.path.exists(self.index_path):
            import json
            with open(self.index_path, encoding="utf-8") as f:
                for k, v in json.load(f).items():
                    self._index[k] = Artifact.from_dict(v)

    def add(
        self,
        path: str,
        document_class: str,
        obtained_on: str,
        obtained_from: str,
        edition: Optional[str] = None,
        published_on: Optional[str] = None,
        notes: str = "",
    ) -> Artifact:
        """Register a document. The file must exist; its digest is computed here."""
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"No artifact at {path!r}. An evidence chain cannot be started "
                "from a document that is not held."
            )
        if os.path.getsize(path) == 0:
            raise ValueError(f"Artifact at {path!r} is empty.")

        digest = sha256_of_file(path)
        if digest in self._index:
            return self._index[digest]

        shutil.copy2(path, os.path.join(self.blobs, digest))
        artifact = Artifact(
            sha256=digest,
            filename=os.path.basename(path),
            document_class=document_class,
            obtained_on=obtained_on,
            obtained_from=obtained_from,
            edition=edition,
            published_on=published_on,
            notes=notes,
        )
        self._index[digest] = artifact
        self._flush()
        return artifact

    def get(self, sha256: str) -> Artifact:
        if sha256 not in self._index:
            raise KeyError(
                f"No artifact {sha256[:12]}... in the store. Evidence may only "
                "reference documents actually held."
            )
        return self._index[sha256]

    def has(self, sha256: str) -> bool:
        return sha256 in self._index

    def verify(self, sha256: str) -> bool:
        """Re-hash the stored blob. Detects corruption or substitution."""
        blob = os.path.join(self.blobs, sha256)
        if not os.path.isfile(blob):
            return False
        return sha256_of_file(blob) == sha256

    def verify_all(self) -> List[str]:
        """Returns digests that failed verification. Empty list = store intact."""
        return sorted(d for d in self._index if not self.verify(d))

    def list_all(self) -> List[Artifact]:
        return [self._index[k] for k in sorted(self._index)]

    def __len__(self) -> int:
        return len(self._index)

    def _flush(self) -> None:
        canonical_dump({k: v.to_dict() for k, v in self._index.items()}, self.index_path)
