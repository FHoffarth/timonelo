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
from dataclasses import dataclass, field, replace
from typing import Dict, Iterable, List, Optional, Tuple

from timonelo.canonical import canonical_dump

CHUNK = 1 << 20


def sha256_of_file(path: str) -> str:
    """Digest of bytes on disk. The only sanctioned way to produce a digest."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def _imo_check_digit_holds(seven_digits: str) -> bool:
    """IMO ship numbers carry a check digit; verify it rather than trust shape.

    The first six digits are weighted 7..2 and summed; the units digit of that
    sum is the seventh digit. A transposed or invented number fails this, so a
    typo cannot silently become a vessel identity.
    """
    total = sum(int(seven_digits[i]) * (7 - i) for i in range(6))
    return total % 10 == int(seven_digits[6])


def normalize_vessel_imo(value: str) -> str:
    """Return the canonical `IMO#######` form, or raise.

    Attribution is keyed on IMO because it is the one vessel identity that is
    stable across renames, reflags and operator changes, and the only one this
    registry can check arithmetically. Display names, slugs and filenames are
    deliberately not accepted: they are what the sister-ship confusion is made
    of.

    ENI numbers (inland/river vessels, e.g. MS Andorinha) are NOT accepted.
    They carry no check digit, and admitting a weaker identity scheme beside a
    verifiable one would let an unverifiable value ride the same code path.
    Extending to ENI is a deliberate future decision, not an oversight.
    """
    if not isinstance(value, str):
        raise RegistryError(f"Vessel identity must be a string, got {type(value).__name__}.")
    candidate = value.strip().upper().replace(" ", "")
    if candidate.startswith("IMO"):
        candidate = candidate[3:]
    # `isascii()` before `isdigit()`, deliberately. `str.isdigit()` alone is
    # true for characters `int()` then refuses -- superscripts such as "²" --
    # and true for characters `int()` accepts but which are not the digits an
    # IMO number is made of, such as Arabic-Indic "٩". The first leaks a
    # ValueError out of what must be a total gate; the second would persist a
    # non-ASCII identity into the canonical registry that can never match a
    # lookup. Restricting to ASCII rules out both, and makes the int()
    # conversion below unconditionally safe.
    if len(candidate) != 7 or not (candidate.isascii() and candidate.isdigit()):
        raise RegistryError(
            f"Invalid IMO identity {value!r}. Expected 'IMO' followed by seven "
            "ASCII digits."
        )
    if not _imo_check_digit_holds(candidate):
        raise RegistryError(
            f"IMO identity {value!r} fails its check digit and is not a real "
            "IMO number."
        )
    return f"IMO{candidate}"


def normalize_subject_vessels(values: Optional[Iterable[str]]) -> Tuple[str, ...]:
    """Validate, de-duplicate and order an attribution set deterministically."""
    if not values:
        return ()
    if isinstance(values, str):
        raise RegistryError(
            "subject_vessels must be a sequence of IMO identities, not a string."
        )
    return tuple(sorted({normalize_vessel_imo(v) for v in values}))


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
    private_source: bool = False

    #: Vessels whose facts this document is curated as establishing, by IMO.
    #:
    #: Registry-side on purpose. A caller assembling an EvidenceLink or a
    #: VesselSpatialOntology references an artifact by ID; it cannot alter what
    #: that artifact is attributed to. Empty means UNKNOWN, never "any vessel" —
    #: consumers must fail closed on it.
    subject_vessels: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "subject_vessels", normalize_subject_vessels(self.subject_vessels)
        )

    def establishes_vessel(self, vessel_imo: str) -> bool:
        """True only if this artifact is explicitly attributed to that vessel.

        Total by construction: any malformed identity answers False rather than
        raising. `RegistryError` subclasses `ValueError`, so catching the latter
        covers both the validator's own refusals and any parsing error it might
        let through. That breadth is deliberate — this is a trust gate, and its
        totality should not depend on the validator upstream staying correct.
        """
        if not self.subject_vessels:
            return False
        try:
            wanted = normalize_vessel_imo(vessel_imo)
        except ValueError:
            return False
        return wanted in self.subject_vessels

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = {
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
        if self.private_source:
            d["private_source"] = True
        if self.subject_vessels:
            # Omitted when empty so an unattributed artifact stays byte-identical
            # to its pre-attribution record. UNKNOWN is the absence of a claim,
            # and it should not appear in the index as an empty assertion.
            d["subject_vessels"] = list(self.subject_vessels)
        return d

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
        subject_vessels: Optional[Iterable[str]] = None,
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

        # Validate before the digest work so a malformed identity cannot leave
        # a blob copied with no index entry.
        attributed = normalize_subject_vessels(subject_vessels)

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
            subject_vessels=attributed,
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

    # -- subject attribution --------------------------------------------------

    def artifact_establishes_vessel(self, artifact_id: str, vessel_imo: str) -> bool:
        """Does this registered artifact establish facts for this vessel?

        The only sanctioned answer to "may this document speak for that ship?".
        It is deliberately the narrow, boring end of the trust chain:

            EvidenceLink -> artifact_id -> registry record -> held bytes
                         -> curated subject attribution

        True requires all of: the artifact is registered, it carries an explicit
        attribution, and the requested IMO is in it. Everything else is False —
        an unknown artifact, an unattributed one, a malformed identity, or a
        sister vessel. Nothing is inferred from filename, slug, source_id,
        publisher, notes, or from the ontology asking the question.
        """
        try:
            artifact = self.get(artifact_id)
        except RegistryError:
            # An unheld document cannot vouch for a vessel. Fail closed rather
            # than propagate: callers are trust gates, and a gate that must
            # catch an exception to stay closed eventually forgets to.
            return False
        return artifact.establishes_vessel(vessel_imo)

    def vessels_established_by(self, artifact_id: str) -> Tuple[str, ...]:
        """Attributed vessels for one artifact; empty for unknown/unattributed."""
        try:
            return self.get(artifact_id).subject_vessels
        except RegistryError:
            return ()

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
        For private_source artifacts, local private directories outside git are checked.
        """
        artifact = self.get(artifact_id)
        if not self._valid_digest(artifact.sha256):
            return None

        if artifact.private_source:
            # Check local private storage paths outside the public repository vault
            for private_dir in [
                os.path.join(self.root, "..", ".local", "private-evidence"),
                os.path.join(self.root, "..", ".private", "evidence"),
                os.environ.get("TIMONELO_PRIVATE_EVIDENCE_DIR", ""),
            ]:
                if private_dir and os.path.isdir(private_dir):
                    prefix = artifact.sha256[:2]
                    for candidate in [
                        os.path.join(private_dir, f"{artifact.sha256}.pdf"),
                        os.path.join(private_dir, prefix, f"{artifact.sha256}.pdf"),
                        os.path.join(private_dir, artifact.filename),
                    ]:
                        if os.path.isfile(candidate) and self._matches_identity(candidate, artifact):
                            return candidate
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
        """Resolve and re-hash stored bytes, failing closed on missing physical bytes."""
        return self.resolve_path(artifact_id) is not None

    def verification_status(self, artifact_id: str) -> str:
        """Explicit verification status distinguishing physical reverification from reference registration."""
        artifact = self.get(artifact_id)
        if self.resolve_path(artifact_id) is not None:
            if artifact.private_source:
                return "PRIVATE_ARTIFACT_SHA_VERIFIED"
            return "PUBLIC_ARTIFACT_SHA_VERIFIED"
        if artifact.private_source and self._valid_digest(artifact.sha256):
            return "PRIVATE_ARTIFACT_REFERENCE_REGISTERED"
        return "MISSING"

    def has_provenance_reference(self, artifact_id: str) -> bool:
        """Whether artifact metadata contains valid cryptographic digest and provenance."""
        artifact = self.get(artifact_id)
        return self._valid_digest(artifact.sha256) and bool(artifact.document_class) and bool(artifact.publisher)

    def verify_all(self, *, include_private: bool = True) -> List[str]:
        if include_private:
            return sorted(a for a in self._by_id if not self.verify(a))
        return sorted(a for a in self._by_id if not self.get(a).private_source and not self.verify(a))

    def list_all(self) -> List[Artifact]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)

    def _flush(self) -> None:
        canonical_dump(
            {k: v.to_dict() for k, v in self._by_id.items()}, self.index_path
        )
