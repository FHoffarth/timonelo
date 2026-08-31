"""
The positive admission boundary for governed spatial state.

One question is asked before any spatial ontology reaches a canonical or public
sink: can every fact in it be *proved* admissible? Not "does it look like the
right class", not "is it structurally coherent" — proved, from evidence the
repository actually holds.

Why the type check was not enough
---------------------------------
`ShipPatchEngine` produces sister-ship hypotheses wrapped in
`QuarantinedVesselSpatialOntology`. The previous gate rejected that wrapper by
`isinstance`. A caller who copies the fields into a plain
`VesselSpatialOntology` drops the wrapper and the gate opens — the geometry is
unchanged, the quarantine marker is gone, and nothing downstream can tell. A
marker a caller can drop is not a boundary.

So nothing here reads the class. Admission is computed from the evidence each
fact carries, which survives copying, deep-copying, re-wrapping and
reconstruction because it *is* the fact. Laundering fails not because the
wrapper is recognised but because copying a fact copies its inadmissible
evidence along with it.

The predicate
-------------
An ontology is ADMITTED when it declares a vessel identity the registry can
resolve, it carries at least one governed fact, and **every** governed fact
(each cabin, each venue) carries at least one `EvidenceLink`, and **every**
link on **every** fact independently satisfies all of:

  1. it names a registered evidence artifact
  2. it is content-addressed (a digest is present)
  3. that digest re-verifies against bytes the repository holds
  4. its `method` and `derivation` are both classified
  5. its derivation is acceptable for canonical first-party evidence
  6. its `evidence_condition` is SUPPORTED
  7. its `human_review_state` is APPROVED
  8. the registered artifact explicitly establishes THIS vessel, through
     `ArtifactRegistry.artifact_establishes_vessel`

Universal quantification on 1-8 is the point. Requiring "some link qualifies"
would let one good citation launder a generated, unheld or wrong-vessel one
sitting beside it. Every link must stand on its own, so adding evidence can
never subtract scrutiny.

Requirement 8 is the only sanctioned vessel binding, and it is registry-side:
a caller chooses which artifact to cite but cannot change what that artifact is
attributed to. Vessel authority is never inferred from `source_id` text,
filenames, publishers, notes, slugs, an existing canonical path, or the
identity the ontology claims for itself.

What it refuses to guess
------------------------
Where the model cannot mechanically establish a requirement, the answer is
rejection, not assumption. An unclassified `derivation` is not read as LOCAL;
an absent digest is not treated as "probably fine"; a vessel identity the
registry cannot parse is not matched by name. UNKNOWN fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

from timonelo.evidence.registry import (
    ArtifactRegistry,
    RegistryError,
    normalize_vessel_imo,
    sha256_of_file,
)
from timonelo.ontology.models import Derivation, EvidenceCondition, HumanReviewState


class AdmissionRejection(str, Enum):
    """Why a governed spatial fact could not be admitted."""

    NO_VESSEL_IDENTITY = "NO_VESSEL_IDENTITY"
    UNRESOLVABLE_VESSEL_IDENTITY = "UNRESOLVABLE_VESSEL_IDENTITY"
    NO_GOVERNED_FACTS = "NO_GOVERNED_FACTS"
    NO_EVIDENCE_LINK = "NO_EVIDENCE_LINK"
    ARTIFACT_NOT_REGISTERED = "ARTIFACT_NOT_REGISTERED"
    NOT_CONTENT_ADDRESSED = "NOT_CONTENT_ADDRESSED"
    ARTIFACT_NOT_HELD = "ARTIFACT_NOT_HELD"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    UNCLASSIFIED_PROVENANCE = "UNCLASSIFIED_PROVENANCE"
    DERIVATION_NOT_CANONICAL = "DERIVATION_NOT_CANONICAL"
    EVIDENCE_NOT_SUPPORTED = "EVIDENCE_NOT_SUPPORTED"
    REVIEW_NOT_APPROVED = "REVIEW_NOT_APPROVED"
    ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL = "ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL"


#: Derivations acceptable for canonical first-party spatial evidence.
#:
#: An allowlist, not a denylist of GENERATED. The distinction matters: the
#: Bellissima ontology's links are *unclassified* (`derivation is None`), which
#: a GENERATED-scan would wave through. Requiring a positive, canonical
#: derivation refuses generated, sister-ship, reference-model and unclassified
#: evidence alike, without enumerating what to fear.
CANONICAL_DERIVATIONS: Tuple[Derivation, ...] = (Derivation.LOCAL,)


@dataclass(frozen=True)
class LinkRejection:
    """One link that could not be admitted, and why."""

    fact_id: str
    source_id: str
    reasons: Tuple[AdmissionRejection, ...]


@dataclass
class AdmissionResult:
    """The verdict, plus enough detail to explain a refusal without guessing."""

    vessel_imo: str
    admitted: bool = False
    facts_examined: int = 0
    facts_admitted: int = 0
    links_examined: int = 0
    rejections: List[LinkRejection] = field(default_factory=list)
    vessel_rejection: Optional[AdmissionRejection] = None

    @property
    def reason_codes(self) -> Tuple[AdmissionRejection, ...]:
        codes: List[AdmissionRejection] = []
        if self.vessel_rejection is not None:
            codes.append(self.vessel_rejection)
        for rejection in self.rejections:
            codes.extend(rejection.reasons)
        return tuple(dict.fromkeys(codes))

    def summary(self) -> str:
        if self.admitted:
            return (
                f"ADMITTED {self.vessel_imo}: {self.facts_admitted} governed facts, "
                f"{self.links_examined} evidence links verified."
            )
        codes = ", ".join(code.value for code in self.reason_codes) or "UNKNOWN"
        if self.vessel_rejection is AdmissionRejection.UNRESOLVABLE_VESSEL_IDENTITY:
            # Say plainly that nothing was weighed. Reporting this as an
            # evidence failure would imply the evidence was examined and found
            # wanting, when the identity gate stopped it before that.
            return (
                f"NOT ADMITTED ({self.vessel_imo}): vessel identity is not "
                f"resolvable under the registry's identity scheme, so no "
                f"evidence was evaluated. Reasons: {codes}"
            )
        failed_facts = self.facts_examined - self.facts_admitted
        return (
            f"NOT ADMITTED ({self.vessel_imo or 'no vessel identity'}): "
            f"{failed_facts} of {self.facts_examined} governed facts failed "
            f"across {len(self.rejections)} rejected evidence link(s). "
            f"Reasons: {codes}"
        )


class SpatialAdmissionError(RuntimeError):
    """Raised when non-admitted spatial state is offered to a governed sink."""


def _governed_facts(ontology: Any) -> List[Tuple[str, Sequence[Any]]]:
    """Every fact that participates in published spatial state, with its links.

    Read structurally rather than by type, so a re-wrapped or reconstructed
    ontology is examined exactly like any other.
    """
    facts: List[Tuple[str, Sequence[Any]]] = []
    for deck_number, deck in sorted(getattr(ontology, "decks", {}).items()):
        for cabin_number, cabin in sorted(getattr(deck, "cabins", {}).items()):
            facts.append(
                (f"deck{deck_number}:cabin:{cabin_number}", getattr(cabin, "evidence_links", []) or [])
            )
        for venue_id, venue in sorted(getattr(deck, "venues", {}).items()):
            facts.append(
                (f"deck{deck_number}:venue:{venue_id}", getattr(venue, "evidence_links", []) or [])
            )
    return facts


def _link_rejections(
    link: Any,
    vessel_imo: str,
    registry: ArtifactRegistry,
) -> Tuple[AdmissionRejection, ...]:
    """Every reason this one link cannot support admitted state for this vessel."""
    reasons: List[AdmissionRejection] = []

    source_id = getattr(link, "source_id", "") or ""
    try:
        artifact = registry.get(source_id)
    except RegistryError:
        # Not a registered artifact. Nothing further can be established about
        # it -- possession, digest and attribution are all registry facts -- so
        # report that alone rather than inferring more from the string.
        return (AdmissionRejection.ARTIFACT_NOT_REGISTERED,)

    digest = getattr(link, "sha256", None)
    if not digest:
        reasons.append(AdmissionRejection.NOT_CONTENT_ADDRESSED)
    else:
        held_path = registry.resolve_path(artifact.artifact_id)
        if held_path is None:
            reasons.append(AdmissionRejection.ARTIFACT_NOT_HELD)
        elif sha256_of_file(held_path) != digest:
            # Recomputed from the bytes, not compared to the index. A digest
            # that only matches a record proves the record, not the document.
            reasons.append(AdmissionRejection.DIGEST_MISMATCH)

    method = getattr(link, "method", None)
    derivation = getattr(link, "derivation", None)
    if method is None or derivation is None:
        reasons.append(AdmissionRejection.UNCLASSIFIED_PROVENANCE)
    elif derivation not in CANONICAL_DERIVATIONS:
        reasons.append(AdmissionRejection.DERIVATION_NOT_CANONICAL)

    if getattr(link, "evidence_condition", None) is not EvidenceCondition.SUPPORTED:
        reasons.append(AdmissionRejection.EVIDENCE_NOT_SUPPORTED)

    if getattr(link, "human_review_state", None) is not HumanReviewState.APPROVED:
        reasons.append(AdmissionRejection.REVIEW_NOT_APPROVED)

    if not registry.artifact_establishes_vessel(artifact.artifact_id, vessel_imo):
        reasons.append(AdmissionRejection.ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL)

    return tuple(reasons)


def evaluate_admission(
    ontology: Any,
    *,
    registry: ArtifactRegistry,
) -> AdmissionResult:
    """Decide whether this spatial state may be persisted to a governed sink.

    Never raises for inadmissible input: an unusable ontology is a verdict, not
    an error. `require_admission` is the raising form for call sites that are
    gates.
    """
    raw_identity = getattr(ontology, "imo_number", "") or ""
    if not str(raw_identity).strip():
        return AdmissionResult(vessel_imo="", vessel_rejection=AdmissionRejection.NO_VESSEL_IDENTITY)
    try:
        vessel_imo = normalize_vessel_imo(str(raw_identity))
    except (RegistryError, ValueError):
        # The identity scheme itself is unsupported or malformed. Evidence is
        # not examined at all -- there is no vessel to attribute it to -- and
        # the result says so rather than implying the evidence was weighed.
        return AdmissionResult(
            vessel_imo=str(raw_identity),
            vessel_rejection=AdmissionRejection.UNRESOLVABLE_VESSEL_IDENTITY,
        )

    result = AdmissionResult(vessel_imo=vessel_imo)
    facts = _governed_facts(ontology)
    result.facts_examined = len(facts)
    if not facts:
        # Admitting an empty ontology would let a sink be created on the
        # strength of having nothing to prove.
        result.vessel_rejection = AdmissionRejection.NO_GOVERNED_FACTS
        return result

    for fact_id, links in facts:
        if not links:
            result.rejections.append(
                LinkRejection(fact_id, "", (AdmissionRejection.NO_EVIDENCE_LINK,))
            )
            continue
        fact_ok = True
        for link in links:
            result.links_examined += 1
            reasons = _link_rejections(link, vessel_imo, registry)
            if reasons:
                fact_ok = False
                result.rejections.append(
                    LinkRejection(fact_id, getattr(link, "source_id", "") or "", reasons)
                )
        if fact_ok:
            result.facts_admitted += 1

    result.admitted = not result.rejections
    return result


def require_admission(ontology: Any, *, registry: ArtifactRegistry) -> AdmissionResult:
    """Admit or raise. The gate governed writers call before any persistence."""
    result = evaluate_admission(ontology, registry=registry)
    if not result.admitted:
        raise SpatialAdmissionError(result.summary())
    return result
