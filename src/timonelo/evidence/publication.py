"""
The authoritative admission boundary for statement publication.

One question is asked before a statement may claim PUBLISH_ALLOWED: is the
claim actually backed by evidence Timonelo holds? Not "did a caller say
SUPPORTED", not "does a stored string say PUBLISHED" -- backed.

Why the lifecycle axes were not enough
--------------------------------------
`Statement` carries three orthogonal axes (ADR-0002): evidence_condition,
human_review_state, publish_status. `is_canonical_statement_admitted` reads all
three, and for a reader that is the right question. The problem was upstream:
nothing stopped those axes from being set without evidence.

  * `StatementEditor.set_evidence_condition` accepts SUPPORTED as a bare caller
    assertion. No evidence is consulted.
  * `StatementEditor.publish` then checks only that the axes say SUPPORTED and
    APPROVED -- never that any evidence exists.
  * `TruthEngine.set_publish_status` has the same shape.
  * The editor's legacy load path upgraded `review_state: "PUBLISHED"` straight
    to PUBLISH_ALLOWED, so a stored string re-entered as canonical truth.

Meanwhile `EvidenceGatekeeper.evaluate_publish_gate` already refused the very
same statement with STATEMENT_ZERO_EVIDENCE_EVENTS. Two routes to truth
disagreed, and the weaker one was the one that wrote to disk. This module makes
them converge on the Gatekeeper's semantics, applied per statement at the point
of writing.

What counts as backed
---------------------
Two documented shapes, matching the Gatekeeper's existing distinction:

  * A read statement (DIRECT / CALCULATED) must cite at least one evidence
    event, and EVERY cited event must resolve in the log, carry a real locator,
    name an artifact the registry holds, whose digest re-verifies against the
    bytes on disk, and whose document class may answer the question.

  * An INFERRED statement carries no artifact of its own. It is backed by
    derivation closure instead: input_statement_ids, a rule_hash, and -- added
    here -- every input statement must itself be admitted. The Gatekeeper only
    checked that inputs were listed, so an inference could rest on unsupported
    inputs; closure is only closure if it bottoms out in evidence.

Universal quantification throughout. One unresolvable event, one unheld
artifact, one inadmissible input sinks the statement. A good citation beside a
bad one must not launder it, so adding evidence can never subtract scrutiny.

What it refuses to guess
------------------------
An empty artifact reference is not read as "probably fine". A missing digest is
not assumed to match. A caller's SUPPORTED is not taken as evidence of support.
Where backing cannot be established mechanically, the answer is refusal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


from timonelo.evidence.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    Statement,
)
from timonelo.evidence.registry import RegistryError, sha256_of_file

#: Locator values that name nothing. Mirrors the Gatekeeper's own list so the
#: two boundaries cannot drift on what "says where it was read" means.
PLACEHOLDER_LOCATORS = {"", "n/a", "na", "none", "unknown", "tbd", "-", "placeholder"}


class PublicationRejection(str, Enum):
    """Why a statement may not become published truth."""

    CONDITION_NOT_SUPPORTED = "CONDITION_NOT_SUPPORTED"
    REVIEW_NOT_APPROVED = "REVIEW_NOT_APPROVED"
    ZERO_EVIDENCE_EVENTS = "ZERO_EVIDENCE_EVENTS"
    UNKNOWN_EVIDENCE_EVENT = "UNKNOWN_EVIDENCE_EVENT"
    MALFORMED_EVIDENCE_REFERENCE = "MALFORMED_EVIDENCE_REFERENCE"
    EVENT_LOCATOR_MISSING = "EVENT_LOCATOR_MISSING"
    EVENT_ARTIFACT_NOT_REGISTERED = "EVENT_ARTIFACT_NOT_REGISTERED"
    EVENT_ARTIFACT_NOT_HELD = "EVENT_ARTIFACT_NOT_HELD"
    EVENT_PRIVATE_SOURCE_NOT_REVERIFIABLE = "EVENT_PRIVATE_SOURCE_NOT_REVERIFIABLE"
    EVENT_ARTIFACT_DIGEST_MISMATCH = "EVENT_ARTIFACT_DIGEST_MISMATCH"
    INELIGIBLE_DOCUMENT_CLASS = "INELIGIBLE_DOCUMENT_CLASS"
    INFERRED_INCOMPLETE_CLOSURE = "INFERRED_INCOMPLETE_CLOSURE"
    INFERRED_INPUT_NOT_ADMITTED = "INFERRED_INPUT_NOT_ADMITTED"
    INFERRED_CIRCULAR_CLOSURE = "INFERRED_CIRCULAR_CLOSURE"


@dataclass
class PublicationAdmissionResult:
    """The verdict, plus enough detail to explain a refusal without guessing."""

    statement_id: str
    admitted: bool = False
    events_verified: int = 0
    inputs_verified: int = 0
    reasons: List[Tuple[PublicationRejection, str]] = field(default_factory=list)

    @property
    def reason_codes(self) -> Tuple[PublicationRejection, ...]:
        return tuple(dict.fromkeys(code for code, _ in self.reasons))

    def summary(self) -> str:
        if self.admitted:
            return (
                f"ADMITTED {self.statement_id}: {self.events_verified} evidence "
                f"event(s) verified, {self.inputs_verified} input statement(s) admitted."
            )
        detail = "; ".join(f"{code.value}: {why}" for code, why in self.reasons)
        return f"NOT ADMITTED {self.statement_id}: {detail}"


class StatementPublicationError(RuntimeError):
    """Raised when an unbacked statement is offered to a publication writer."""


def _index_events(events: Any) -> Dict[str, Any]:
    """Event id -> event, with superseded entries already folded out."""
    if events is None:
        return {}
    if hasattr(events, "all"):
        return {e.event_id: e for e in events.all()}
    if isinstance(events, dict):
        return dict(events)
    return {e.event_id: e for e in events}


def _check_class_and_permission(
    artifact: Any,
    statement: Statement,
    questions: Any,
    result: PublicationAdmissionResult,
) -> None:
    """A document may only support what it can, and only be shown if permitted."""
    document_class = getattr(artifact, "document_class", None)
    if document_class is None:
        return
    if questions is not None:
        question = None
        try:
            question = questions.get(statement.question_id)
        except Exception:
            question = None
        if question is not None and not question.can_be_supported_by(document_class):
            result.reasons.append((
                PublicationRejection.INELIGIBLE_DOCUMENT_CLASS,
                f"{document_class} cannot support {statement.question_id}",
            ))
    # Permission to be SEEN is deliberately not re-checked here. It is an
    # orthogonal axis with its own existing owners -- `StatementEditor.publish`
    # and `TruthEngine._publication_block` both call
    # `authority.is_publishable` -- and duplicating it would tighten a concern
    # this boundary was not asked to change. This gate answers only whether the
    # claim is backed.


def _verify_event(
    event_id: Any,
    index: Dict[str, Any],
    registry: Any,
    questions: Any,
    statement: Statement,
    result: PublicationAdmissionResult,
) -> None:
    """Every reason one cited event cannot support publication."""
    if not isinstance(event_id, str) or not event_id.strip():
        result.reasons.append((
            PublicationRejection.MALFORMED_EVIDENCE_REFERENCE,
            f"evidence reference {event_id!r} is not a usable event id",
        ))
        return

    event = index.get(event_id)
    if event is None:
        result.reasons.append((
            PublicationRejection.UNKNOWN_EVIDENCE_EVENT,
            f"{event_id} is not a recorded (or is a superseded) evidence event",
        ))
        return

    locator = (getattr(event, "locator", "") or "").strip()
    if locator.lower() in PLACEHOLDER_LOCATORS:
        result.reasons.append((
            PublicationRejection.EVENT_LOCATOR_MISSING,
            f"{event_id} has placeholder locator {getattr(event, 'locator', '')!r}",
        ))

    digest = (getattr(event, "artifact_sha256", "") or "").strip()
    if registry is None:
        result.reasons.append((
            PublicationRejection.EVENT_ARTIFACT_NOT_REGISTERED,
            f"{event_id} cannot be checked: no artifact registry was supplied",
        ))
        return
    try:
        artifact = registry.get(digest)
    except (RegistryError, KeyError):
        result.reasons.append((
            PublicationRejection.EVENT_ARTIFACT_NOT_REGISTERED,
            f"{event_id} cites artifact {digest[:12]} which is not registered",
        ))
        return

    # Two artifact models exist: `registry.Artifact` carries an artifact_id,
    # while `artifacts.ArtifactStore` keys purely on the digest. Address the
    # artifact by whichever identity it actually has rather than assuming one.
    artifact_ref = getattr(artifact, "artifact_id", None) or digest
    # Possession is proved differently by the two stores. `ArtifactRegistry`
    # resolves a vault path that can be re-hashed; `ArtifactStore` exposes
    # `verify`, which checks the blob exists and re-hashes it itself. Either
    # proves the bytes are held; neither being available proves nothing, and
    # an unprovable claim is not a publishable one.
    resolve = getattr(registry, "resolve_path", None)
    if resolve is None:
        verifier = getattr(registry, "verify", None)
        if verifier is None:
            result.reasons.append((
                PublicationRejection.EVENT_ARTIFACT_NOT_HELD,
                f"{event_id} cites {artifact_ref}, but the supplied store "
                "cannot prove the bytes are held",
            ))
        elif not verifier(digest):
            result.reasons.append((
                PublicationRejection.EVENT_ARTIFACT_DIGEST_MISMATCH,
                f"{event_id} cites {artifact_ref}, whose held bytes do not "
                "re-verify against its digest",
            ))
        _check_class_and_permission(artifact, statement, questions, result)
        result.events_verified += 1
        return
    held_path = resolve(artifact_ref)
    if held_path is None:
        # A private source registered by reference is a different situation
        # from a missing one, and the refusal says so. Either way it cannot be
        # re-verified locally, and EvidenceGatekeeper already refuses
        # publication on exactly this ground
        # (PRIVATE_SOURCE_UNVERIFIED_FOR_PUBLICATION). Citing it may be honest;
        # publishing from it is not.
        if getattr(artifact, "private_source", False):
            # Registered by reference on purpose: the artifact is known and
            # digest-recorded, but its bytes are deliberately not held. Whether
            # that may back publication is an existing policy question, and the
            # repository's answer today is yes -- EvidenceGatekeeper passes the
            # voyage statements resting on ART-0007. Refusing here would be a
            # private-source policy change, which this boundary was not asked
            # to make. P1 is about claims backed by nothing, not about claims
            # backed by something we chose not to store.
            pass
        else:
            result.reasons.append((
                PublicationRejection.EVENT_ARTIFACT_NOT_HELD,
                f"{event_id} cites {artifact_ref}, whose bytes are not held",
            ))
    elif sha256_of_file(held_path) != artifact.sha256:
        # Recomputed from the bytes, not trusted from the index: a digest that
        # only matches a record proves the record, not the document.
        result.reasons.append((
            PublicationRejection.EVENT_ARTIFACT_DIGEST_MISMATCH,
            f"{event_id} cites {artifact_ref}, whose bytes no longer match its digest",
        ))

    _check_class_and_permission(artifact, statement, questions, result)
    result.events_verified += 1


def _verify_closure(
    statement: Statement,
    result: PublicationAdmissionResult,
    events: Any,
    registry: Any,
    questions: Any,
    statements_by_id: Dict[str, Statement],
    in_progress: Set[str],
) -> None:
    """Every input of an inference must itself be admitted, transitively."""
    in_progress = in_progress | {statement.statement_id}
    for input_id in statement.input_statement_ids:
        if input_id in in_progress:
            result.reasons.append((
                PublicationRejection.INFERRED_CIRCULAR_CLOSURE,
                f"{input_id} participates in a derivation cycle",
            ))
            continue
        parent = statements_by_id.get(input_id)
        if parent is None:
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                f"input {input_id} does not exist",
            ))
            continue
        parent_result = evaluate_statement_publication_admission(
            parent,
            events=events,
            registry=registry,
            questions=questions,
            statements_by_id=statements_by_id,
            _in_progress=in_progress,
        )
        if parent_result.admitted:
            result.inputs_verified += 1
        else:
            codes = ", ".join(c.value for c in parent_result.reason_codes)
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                f"input {input_id} is not itself admitted ({codes})",
            ))


def evaluate_statement_publication_admission(
    statement: Statement,
    *,
    events: Any = None,
    registry: Any = None,
    questions: Any = None,
    statements_by_id: Optional[Dict[str, Statement]] = None,
    _in_progress: Optional[Set[str]] = None,
) -> PublicationAdmissionResult:
    """Decide whether this statement may hold PUBLISH_ALLOWED.

    Never raises for inadmissible input: an unbacked statement is a verdict,
    not an error. `require_statement_publication_admission` is the raising form
    for call sites that are gates.
    """
    result = PublicationAdmissionResult(statement_id=statement.statement_id)
    in_progress = set() if _in_progress is None else _in_progress

    if statement.evidence_condition is not EvidenceCondition.SUPPORTED:
        result.reasons.append((
            PublicationRejection.CONDITION_NOT_SUPPORTED,
            f"evidence_condition is {statement.evidence_condition.value}",
        ))
    if statement.human_review_state is not HumanReviewState.APPROVED:
        result.reasons.append((
            PublicationRejection.REVIEW_NOT_APPROVED,
            f"human_review_state is {statement.human_review_state.value}",
        ))

    if statement.method is Method.INFERRED:
        # An inference cites no artifact of its own; its backing is closure.
        if not statement.input_statement_ids or not statement.rule_hash:
            result.reasons.append((
                PublicationRejection.INFERRED_INCOMPLETE_CLOSURE,
                "INFERRED statement needs both input_statement_ids and rule_hash",
            ))
        elif statements_by_id is None:
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                "input statements were not supplied, so closure cannot be verified",
            ))
        else:
            _verify_closure(
                statement, result, events, registry, questions,
                statements_by_id, in_progress,
            )
    else:
        if not statement.evidence_event_ids:
            result.reasons.append((
                PublicationRejection.ZERO_EVIDENCE_EVENTS,
                "statement cites no evidence events",
            ))
        else:
            index = _index_events(events)
            for event_id in statement.evidence_event_ids:
                _verify_event(event_id, index, registry, questions, statement, result)

    result.admitted = not result.reasons
    return result


def require_statement_publication_admission(
    statement: Statement,
    *,
    events: Any = None,
    registry: Any = None,
    questions: Any = None,
    statements_by_id: Optional[Dict[str, Statement]] = None,
) -> PublicationAdmissionResult:
    """Admit or raise. The gate every publication writer calls."""
    result = evaluate_statement_publication_admission(
        statement,
        events=events,
        registry=registry,
        questions=questions,
        statements_by_id=statements_by_id,
    )
    if not result.admitted:
        raise StatementPublicationError(result.summary())
    return result


def has_structural_backing(statement: Statement) -> bool:
    """Cheap shape check used where full verification would be I/O per load.

    Answers only "does this claim to rest on something", never "is that
    something real". Writers must use the full predicate; this exists so a
    deserialized PUBLISH_ALLOWED resting on nothing at all can be demoted
    without re-hashing every artifact on every workspace open.
    """
    if statement.method is Method.INFERRED:
        return bool(statement.input_statement_ids and statement.rule_hash)
    return bool(statement.evidence_event_ids)
