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
    PublishStatus,
    Statement,
)
from timonelo.evidence import authority
from timonelo.evidence.registry import RegistryError, sha256_of_file

#: A rule hash is content-addressed, exactly like `EvidenceLink.sha256`: a
#: SHA-256 of the rule that produced the inference. Mirroring that model's
#: existing rule (64 hex, never the all-zero placeholder) keeps the two from
#: drifting. Truthiness is not a contract -- "x" is truthy and proves nothing.
_HEX = set("0123456789abcdef")


def is_valid_rule_hash(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    return len(v) == 64 and all(c in _HEX for c in v) and v != "0" * 64


#: Inference closure is walked iteratively, but a graph can still be absurdly
#: deep. Beyond this the answer is an explicit verdict, never a RecursionError.
MAX_INFERENCE_DEPTH = 64

#: Re-hashing an artifact is the expensive part of admission and the bytes do
#: not change between reads. Keyed on (path, size, mtime) so a replaced file is
#: re-hashed rather than trusted.
_DIGEST_CACHE: Dict[Tuple[str, int, float], str] = {}


def _cached_digest(path: str) -> str:
    import os

    stat = os.stat(path)
    key = (path, stat.st_size, stat.st_mtime)
    if key not in _DIGEST_CACHE:
        _DIGEST_CACHE[key] = sha256_of_file(path)
    return _DIGEST_CACHE[key]

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
    EVIDENCE_DOES_NOT_SUPPORT_CLAIM = "EVIDENCE_DOES_NOT_SUPPORT_CLAIM"
    NOT_PUBLISHABLE_BY_PERMISSION = "NOT_PUBLISHABLE_BY_PERMISSION"
    INFERRED_INVALID_RULE_HASH = "INFERRED_INVALID_RULE_HASH"
    INFERRED_RULE_PROVENANCE_UNRESOLVABLE = "INFERRED_RULE_PROVENANCE_UNRESOLVABLE"
    QUESTION_METADATA_UNRESOLVABLE = "QUESTION_METADATA_UNRESOLVABLE"
    NO_VALIDATION_CONTEXT = "NO_VALIDATION_CONTEXT"
    INFERRED_CLOSURE_TOO_DEEP = "INFERRED_CLOSURE_TOO_DEEP"
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


#: Resolving a rule hash to the rule it names.
#:
#: ADR-0003 §3 makes rules content-addressed: a derived statement cites the hash
#: of the rule version it consumed. Honouring that needs somewhere to look the
#: hash up, and this repository has none -- no rule store, no registry, no
#: resolver. `TruthEngine.rules` is a confidence-weight lookup, not rule
#: content.
#:
#: This seam exists so the limitation is visible and has one obvious place to be
#: fixed. Until something is wired in, it returns None for every hash and
#: authoritative INFERRED publication fails closed. Inventing a resolver inside
#: this boundary would be inventing provenance.
_RULE_RESOLVER = None


def set_rule_resolver(resolver) -> None:
    """Install a callable mapping a rule hash to its rule content, or None."""
    global _RULE_RESOLVER
    _RULE_RESOLVER = resolver


def resolve_rule(rule_hash: str):
    """The rule a hash identifies, or None when it cannot be established."""
    if _RULE_RESOLVER is None:
        return None
    return _RULE_RESOLVER(rule_hash)


def _index_events(events: Any) -> Dict[str, Any]:
    """Event id -> event, with superseded entries already folded out."""
    if events is None:
        return {}
    if hasattr(events, "all"):
        return {e.event_id: e for e in events.all()}
    if isinstance(events, dict):
        return dict(events)
    return {e.event_id: e for e in events}


def _values_agree(observed: Any, claimed: Any) -> bool:
    """Whether an observation records the value the statement asserts.

    Compared as stored first, then as text. The store round-trips values
    through JSON, so an integer deck number can come back as `14` from one
    path and `"14"` from another; treating those as disagreement would reject
    honest evidence for a serialization detail.
    """
    # Booleans first, because Python would otherwise settle this wrongly:
    # `1 == True`, so an observation of the number 1 would back a claim of
    # "yes", and `str(1) != str(True)` would not catch it either. A cabin
    # counted once is not a cabin confirmed to exist.
    if isinstance(observed, bool) != isinstance(claimed, bool):
        return False
    if observed == claimed:
        return True
    if observed is None or claimed is None:
        return False
    return str(observed).strip() == str(claimed).strip()


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
    # Question metadata is what establishes whether this document class may
    # answer this question. If it cannot be resolved, that capability is
    # unknown -- and unknown must never read as permitted.
    if questions is None:
        result.reasons.append((
            PublicationRejection.QUESTION_METADATA_UNRESOLVABLE,
            "no question registry was supplied, so document class capability "
            "cannot be established",
        ))
    else:
        try:
            question = questions.get(statement.question_id)
        except Exception:
            question = None
        if question is None:
            result.reasons.append((
                PublicationRejection.QUESTION_METADATA_UNRESOLVABLE,
                f"{statement.question_id} is not a registered question, so its "
                "document class capability cannot be established",
            ))
        elif not question.can_be_supported_by(document_class):
            result.reasons.append((
                PublicationRejection.INELIGIBLE_DOCUMENT_CLASS,
                f"{document_class} cannot support {statement.question_id}",
            ))
    # Permission to be SEEN. R1 removed this from `StatementEditor.publish`
    # and left no owner on that path, which was a regression: a statement type
    # that may not be shown could be published. This module is now the single
    # owner, and the writers delegate rather than each keeping a copy.
    try:
        ok, why = authority.is_publishable(statement.statement_type, document_class)
    except Exception as exc:
        # An unregistered document class cannot be shown to be publishable.
        ok, why = False, f"permission for {document_class!r} could not be determined: {exc}"
    if not ok:
        result.reasons.append((
            PublicationRejection.NOT_PUBLISHABLE_BY_PERMISSION,
            why or "not publishable",
        ))


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

    # The event must support THIS claim, not merely exist. `EvidenceEvent`
    # defines the correspondence itself -- entity_id, question_id and
    # observed_value are its own fields, and they mean the same things as the
    # statement's entity_id, question_id and value. Without this, the Barcelona
    # observation of "Port de Barcelona" would support a Tokyo statement
    # asserting something else entirely, which is exactly what R1 allowed.
    mismatches = []
    if getattr(event, "entity_id", None) != statement.entity_id:
        mismatches.append(
            f"entity {getattr(event, 'entity_id', None)!r} != {statement.entity_id!r}"
        )
    if getattr(event, "question_id", None) != statement.question_id:
        mismatches.append(
            f"question {getattr(event, 'question_id', None)!r} != {statement.question_id!r}"
        )
    if not _values_agree(getattr(event, "observed_value", None), statement.value):
        mismatches.append(
            f"observed {getattr(event, 'observed_value', None)!r} != claimed {statement.value!r}"
        )
    if mismatches:
        result.reasons.append((
            PublicationRejection.EVIDENCE_DOES_NOT_SUPPORT_CLAIM,
            f"{event_id} does not support this claim: " + "; ".join(mismatches),
        ))

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
            # R2 recorded these as publishable on the strength of a comparison
            # that was not actually made: `EvidenceGatekeeper.from_workspace`
            # registers sources and events but never statements, so the gate was
            # asked about an empty set and unsurprisingly found nothing wrong.
            # Adding the statement, the Gatekeeper refuses it outright with
            # PRIVATE_SOURCE_UNVERIFIED_FOR_PUBLICATION. That is the
            # repository's policy, and this boundary converges on it: bytes
            # nobody holds cannot be re-verified, and a claim that cannot be
            # re-verified cannot be published.
            result.reasons.append((
                PublicationRejection.EVENT_PRIVATE_SOURCE_NOT_REVERIFIABLE,
                f"{event_id} cites private source {artifact_ref}, whose bytes "
                "are not held for re-verification",
            ))
        else:
            result.reasons.append((
                PublicationRejection.EVENT_ARTIFACT_NOT_HELD,
                f"{event_id} cites {artifact_ref}, whose bytes are not held",
            ))
    elif _cached_digest(held_path) != artifact.sha256:
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
) -> None:
    """Walk the inference's dependency graph iteratively.

    Recursion here was unbounded: a 2000-deep chain raised RecursionError
    instead of returning a verdict, and a trust gate that crashes is a gate
    that stops answering. The walk is now an explicit stack with a depth
    bound, so malformed or absurd graphs fail with a reason.

    Every reachable input must itself be admitted. Cycles are reported rather
    than followed, and each statement is evaluated once however many paths
    reach it.
    """
    pending: List[Tuple[str, int, Tuple[str, ...]]] = [
        (input_id, 1, (statement.statement_id,))
        for input_id in statement.input_statement_ids
    ]
    settled: Set[str] = set()

    while pending:
        input_id, depth, path = pending.pop()
        if depth > MAX_INFERENCE_DEPTH:
            result.reasons.append((
                PublicationRejection.INFERRED_CLOSURE_TOO_DEEP,
                f"closure exceeds {MAX_INFERENCE_DEPTH} levels at {input_id}",
            ))
            return
        if input_id in path:
            result.reasons.append((
                PublicationRejection.INFERRED_CIRCULAR_CLOSURE,
                f"{input_id} participates in a derivation cycle",
            ))
            continue
        if input_id in settled:
            continue
        settled.add(input_id)

        parent = statements_by_id.get(input_id)
        if parent is None:
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                f"input {input_id} does not exist",
            ))
            continue

        # Each input is judged on its own terms: its own lifecycle axes, and
        # its own evidence or its own closure. Only its direct requirements are
        # checked here; its inputs are pushed onto the stack rather than
        # recursed into.
        parent_result = PublicationAdmissionResult(statement_id=parent.statement_id)
        _check_axes(parent, parent_result)
        if parent.method is Method.INFERRED:
            _check_inference_shape(parent, parent_result)
            if parent_result.admitted or not parent_result.reasons:
                pending.extend(
                    (next_id, depth + 1, path + (input_id,))
                    for next_id in parent.input_statement_ids
                )
        else:
            _check_events(parent, parent_result, events, registry, questions)

        if parent_result.reasons:
            codes = ", ".join(c.value for c in parent_result.reason_codes)
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                f"input {input_id} is not itself admitted ({codes})",
            ))
        else:
            result.inputs_verified += 1
            result.events_verified += parent_result.events_verified


def _check_axes(statement: Statement, result: PublicationAdmissionResult) -> None:
    """The lifecycle axes. Necessary, never sufficient."""
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


def _check_inference_shape(
    statement: Statement, result: PublicationAdmissionResult
) -> None:
    """An inference's own requirements, before its inputs are walked."""
    if not statement.input_statement_ids:
        result.reasons.append((
            PublicationRejection.INFERRED_INCOMPLETE_CLOSURE,
            "INFERRED statement cites no input statements",
        ))
    if not is_valid_rule_hash(statement.rule_hash):
        result.reasons.append((
            PublicationRejection.INFERRED_INVALID_RULE_HASH,
            f"rule_hash {statement.rule_hash!r} is not a SHA-256 content address",
        ))
    elif resolve_rule(statement.rule_hash) is None:
        # ADR-0003 §3 requires a derived statement to cite the hash of the rule
        # version it consumed, so that editing a rule invalidates its closure.
        # The repository stores no rules and offers no resolver, so a hash
        # cannot be shown to identify anything: any 64 hex characters look
        # exactly like a real citation. Shape is not provenance, and a
        # well-formed pointer to nothing is precisely the "fake hash in a new
        # costume" that ADR names. Authoritative inference therefore fails
        # closed until a rule store exists.
        result.reasons.append((
            PublicationRejection.INFERRED_RULE_PROVENANCE_UNRESOLVABLE,
            f"rule_hash {statement.rule_hash} cannot be resolved to any rule "
            "content: this repository holds no rule store (ADR-0003 §3)",
        ))


def _check_events(
    statement: Statement,
    result: PublicationAdmissionResult,
    events: Any,
    registry: Any,
    questions: Any,
) -> None:
    """A read statement's own evidence requirements."""
    if not statement.evidence_event_ids:
        result.reasons.append((
            PublicationRejection.ZERO_EVIDENCE_EVENTS,
            "statement cites no evidence events",
        ))
        return
    index = _index_events(events)
    for event_id in statement.evidence_event_ids:
        _verify_event(event_id, index, registry, questions, statement, result)


def evaluate_statement_publication_admission(
    statement: Statement,
    *,
    events: Any = None,
    registry: Any = None,
    questions: Any = None,
    statements_by_id: Optional[Dict[str, Statement]] = None,
) -> PublicationAdmissionResult:
    """Decide whether this statement may hold PUBLISH_ALLOWED.

    Never raises for inadmissible input, and never recurses: an unbacked or
    malformed statement is a verdict, not an error.
    `require_statement_publication_admission` is the raising form for call
    sites that are gates.
    """
    result = PublicationAdmissionResult(statement_id=statement.statement_id)
    _check_axes(statement, result)

    if statement.method is Method.INFERRED:
        _check_inference_shape(statement, result)
        if statements_by_id is None:
            result.reasons.append((
                PublicationRejection.INFERRED_INPUT_NOT_ADMITTED,
                "input statements were not supplied, so closure cannot be verified",
            ))
        elif statement.input_statement_ids:
            _verify_closure(
                statement, result, events, registry, questions, statements_by_id
            )
    else:
        _check_events(statement, result, events, registry, questions)

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


class PublicationAuthority:
    """Whether a statement is authoritative *now*.

    P1 and its first remediation both established that a statement must earn
    PUBLISH_ALLOWED against real evidence. Neither established that it keeps
    it. `PublishStatus` is written to disk, evidence is not frozen when it is
    written, and nothing re-asked the question afterwards: an event could be
    superseded, an artifact replaced, a question retired, and the persisted
    axes would go on reading as truth. Lifecycle state is a record that
    publication was once granted -- audit, not authority.

    So authority is computed, never loaded. Every truth-bearing consumer asks
    this object, and this object re-derives the verdict from the evidence as it
    stands at the moment of the question. There is deliberately no cache: a
    cached admission is a smaller version of the same defect, and the check is
    dict lookups over an already-cached digest.

    Being unable to check is not permission to skip the check. An authority
    missing any part of its validation context refuses everything, and says so.
    """

    def __init__(
        self,
        *,
        events: Any = None,
        registry: Any = None,
        questions: Any = None,
        statements: Any = None,
    ) -> None:
        self.events = events
        self.registry = registry
        self.questions = questions
        self._statements = statements

    @property
    def has_context(self) -> bool:
        """True only if every input the verdict depends on is present."""
        return not self.missing_context

    @property
    def missing_context(self) -> Tuple[str, ...]:
        missing = []
        if self.events is None:
            missing.append("events")
        if self.registry is None:
            missing.append("registry")
        if self.questions is None:
            missing.append("questions")
        if self._statements is None:
            missing.append("statements")
        return tuple(missing)

    def statements_by_id(self) -> Optional[Dict[str, Statement]]:
        """The live statement set, re-read per call so closures see the present."""
        src = self._statements
        if src is None:
            return None
        if callable(src):
            return src()
        if hasattr(src, "all"):
            return {s.statement_id: s for s in src.all()}
        return dict(src)

    def evaluate(self, statement: Statement) -> PublicationAdmissionResult:
        """The current admission verdict for one statement."""
        missing = self.missing_context
        if missing:
            result = PublicationAdmissionResult(statement_id=statement.statement_id)
            result.reasons.append((
                PublicationRejection.NO_VALIDATION_CONTEXT,
                "current publication admission cannot be established without "
                + ", ".join(missing),
            ))
            result.admitted = False
            return result
        return evaluate_statement_publication_admission(
            statement,
            events=self.events,
            registry=self.registry,
            questions=self.questions,
            statements_by_id=self.statements_by_id(),
        )

    def is_currently_authoritative(self, statement: Statement) -> bool:
        """The single question every truth-bearing consumer must ask.

        Persisted lifecycle state is necessary and not sufficient: the axes say
        publication was granted, this says it still holds.
        """
        if statement.publishing not in (
            PublishStatus.PUBLISH_ALLOWED,
            PublishStatus.PUBLISH_ALLOWED.value,
            PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS,
            PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value,
        ):
            return False
        return self.evaluate(statement).admitted


#: The authority used when a consumer was given none. It has no validation
#: context, so it refuses everything -- which is the right answer to "is this
#: authoritative?" asked by something that cannot check.
NO_AUTHORITY = PublicationAuthority()
