"""
Artifact Registry — the sole issuer of Artifact IDs.

Governed by ADR-0002 §5.

Two identities, deliberately:

  * `artifact_id` (ART-NNNN) is the stable reference handle. Only this registry
    may create one. It is immutable and is never reused, even if the artifact
    is later superseded.
  * `sha256` is the integrity anchor, computed from the bytes on disk. It
    answers "are these still the same bytes?", which an ID cannot.

Statements and events reference artifacts by ID. Integrity is verified through
the digest. Neither substitutes for the other.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass, replace
from typing import Dict, List, Optional

from timonelo.canonical import canonical_dump

CHUNK = 1 << 20


def sha256_of_file(path: str) -> str:
    """Digest of bytes on disk. The only sanctioned way to produce a digest."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Artifact:
    """A source document physically held.

    Every field is either computed from the file or supplied by the acquirer at
    registration. Nothing defaults to a plausible value: unknown metadata stays
    None, because a guessed publication date is indistinguishable from a
    recorded one once it is in the store.
    """
    artifact_id: str            # issued by the registry, immutable
    sha256: str                 # computed from the bytes
    filename: str
    document_class: str
    acquired_on: str            # ISO date the copy was obtained
    acquisition_method: str     # how: "download", "operator request", "onboard"
    publisher: Optional[str] = None
    published_on: Optional[str] = None
    version: Optional[str] = None       # edition / revision as printed
    language: Optional[str] = None      # BCP-47, e.g. "en", "de"
    byte_size: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "sha256": self.sha256,
            "filename": self.filename,
            "document_class": self.document_class,
            "acquired_on": self.acquired_on,
            "acquisition_method": self.acquisition_method,
            "publisher": self.publisher,
            "published_on": self.published_on,
            "version": self.version,
            "language": self.language,
            "byte_size": self.byte_size,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(d: Dict[str, object]) -> "Artifact":
        return Artifact(**d)  # type: ignore[arg-type]


class RegistryError(ValueError):
    pass


class ArtifactRegistry:
    """Content-addressed store plus the ID authority.

    Empty by construction. The only mutation is registration; artifacts are
    never edited in place, because a registry entry that can change is a
    provenance record that can drift from what was actually observed.
    """

    ID_PREFIX = "ART-"

    def __init__(self, root: str):
        self.root = root
        self.blobs = os.path.join(root, "blobs")
        self.index_path = os.path.join(root, "index.json")
        os.makedirs(self.blobs, exist_ok=True)
        self._by_id: Dict[str, Artifact] = {}
        self._id_by_sha: Dict[str, str] = {}
        if os.path.exists(self.index_path):
            import json
            with open(self.index_path, encoding="utf-8") as f:
                for aid, raw in json.load(f).items():
                    art = Artifact.from_dict(raw)
                    self._by_id[aid] = art
                    self._id_by_sha[art.sha256] = aid

    # -- ID authority ---------------------------------------------------------

    def _next_id(self) -> str:
        n = 1 + max(
            (int(k[len(self.ID_PREFIX):]) for k in self._by_id), default=0
        )
        return f"{self.ID_PREFIX}{n:04d}"

    # -- registration ---------------------------------------------------------

    def register(
        self,
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
        """Register a held document. Digest and size are computed, never given."""
        if not os.path.isfile(path):
            raise RegistryError(
                f"No file at {path!r}. An evidence chain cannot begin with a "
                "document that is not held."
            )
        size = os.path.getsize(path)
        if size == 0:
            raise RegistryError(f"File at {path!r} is empty.")

        from timonelo.evidence import authority
        if document_class not in authority.DOCUMENT_CLASSES:
            raise RegistryError(
                f"Unregistered document class {document_class!r}. Declare it in "
                "authority.DOCUMENT_CLASSES first, so its reliability, validity "
                "scope and use permission are known before it carries evidence."
            )
        for field_name, value in (
            ("acquired_on", acquired_on),
            ("acquisition_method", acquisition_method),
        ):
            if not value:
                raise RegistryError(f"{field_name} is required at registration.")

        digest = sha256_of_file(path)
        if digest in self._id_by_sha:
            # Same bytes already held. Return the existing entry rather than
            # issuing a second ID for one document.
            return self._by_id[self._id_by_sha[digest]]

        artifact = Artifact(
            artifact_id=self._next_id(),
            sha256=digest,
            filename=os.path.basename(path),
            document_class=document_class,
            acquired_on=acquired_on,
            acquisition_method=acquisition_method,
            publisher=publisher,
            published_on=published_on,
            version=version,
            language=language,
            byte_size=size,
            notes=notes,
        )
        shutil.copy2(path, os.path.join(self.blobs, digest))
        self._by_id[artifact.artifact_id] = artifact
        self._id_by_sha[digest] = artifact.artifact_id
        self._flush()
        return artifact

    # -- lookup ---------------------------------------------------------------

    def get(self, identifier: str) -> Artifact:
        if identifier in self._by_id:
            return self._by_id[identifier]
        if identifier in self._id_by_sha:
            return self._by_id[self._id_by_sha[identifier]]
        raise RegistryError(
            f"No artifact {identifier!r}. Evidence may only reference "
            "documents actually held and registered."
        )

    def has(self, identifier: str) -> bool:
        return identifier in self._by_id or identifier in self._id_by_sha

    def blob_path(self, artifact_id: str) -> str:
        """Return the legacy extensionless blob path used by registration."""
        return os.path.join(self.blobs, self.get(artifact_id).sha256)

    @staticmethod
    def _valid_digest(digest: str) -> bool:
        return len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)

    @staticmethod
    def _matches_identity(path: str, artifact: Artifact) -> bool:
        if not os.path.isfile(path) or os.path.islink(path):
            return False
        if artifact.byte_size and os.path.getsize(path) != artifact.byte_size:
            return False
        return sha256_of_file(path) == artifact.sha256

    def _vault_candidates(self, artifact: Artifact) -> List[str]:
        """Return exact-digest files from the sibling SHA vault.

        Extensions are intentionally not guessed from the human filename. The
        digest directory may contain an extensionless file or one typed by its
        real media suffix; exactly one candidate is required.
        """
        digest = artifact.sha256
        if not self._valid_digest(digest):
            return []
        vault_dir = os.path.join(
            os.path.dirname(os.path.abspath(self.root)),
            "raw",
            "sha256",
            digest[:2],
        )
        if not os.path.isdir(vault_dir):
            return []
        candidates = []
        for entry in os.scandir(vault_dir):
            if not entry.is_file(follow_symlinks=False):
                continue
            if entry.name == digest or entry.name.startswith(f"{digest}."):
                candidates.append(entry.path)
        return sorted(candidates)

    def resolve_path(self, artifact_id: str) -> Optional[str]:
        """Resolve one verified physical representation of an artifact.

        The canonical SHA vault has authority when it contains a candidate.
        Multiple candidates or an invalid canonical candidate fail closed; a
        legacy blob is considered only when the canonical vault has none.
        """
        artifact = self.get(artifact_id)
        if not self._valid_digest(artifact.sha256):
            return None
        candidates = self._vault_candidates(artifact)
        if candidates:
            if len(candidates) != 1:
                return None
            candidate = candidates[0]
            return candidate if self._matches_identity(candidate, artifact) else None

        legacy = self.blob_path(artifact_id)
        return legacy if self._matches_identity(legacy, artifact) else None

    def verify(self, artifact_id: str) -> bool:
        """Resolve and re-hash stored bytes, failing closed on ambiguity."""
        return self.resolve_path(artifact_id) is not None

    def verify_all(self) -> List[str]:
        return sorted(a for a in self._by_id if not self.verify(a))

    def list_all(self) -> List[Artifact]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)

    def _flush(self) -> None:
        canonical_dump(
            {k: v.to_dict() for k, v in self._by_id.items()}, self.index_path
        )
