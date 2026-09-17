"""
Applying a staged human geometry adjudication to the repository.

The review workspace produces a `timonelo.deck-review.staged-record.v1` file: a
human looked at a polygon against the source drawing and said what they thought
of it. Until now nothing could turn that into repository truth, which was the
honest state of affairs -- a downloaded JSON file is a proposal, not a fact.

This is the governed path that makes one durable, and the whole design follows
from two sentences in ADR-0002 §5: *the log is append-only*, and *promotion from
hypothesis to ground truth requires an evidence event; there is no automatic
path*.

WHAT IS AND IS NOT WRITTEN

The proof is not touched. Rewriting `deck14.proof.json` to stamp APPROVED into
an object would change the proof digest -- the very thing the staged record
binds itself to -- and would be destructive replacement of an extraction record
by a review outcome. Instead an entry is appended to a review log, and the
review state of a proof object becomes a projection of (extracted object) +
(adjudication log), computed at read time. That is the same lesson the statement
side learned: authority is derived from current records, not stamped into them.

WHAT A REVIEW ACT CAN ESTABLISH

The review axis, and nothing else. `human_review_state` moves. `evidence_condition`
does not, because looking at a drawing is not an observation recorded against an
artifact, and SUPPORTED is what an evidence event earns. `publish_status` does
not, because publication needs evidence this act did not create. No evidence
event is written. No cabin identity statement is written. An applied ACCEPT
therefore leaves passenger admission exactly where it was: false.

WHY THIS IS NOT THE STATEMENT REVIEW LOG

`evidence.review.ReviewLog` is append-only and does almost the right thing, but
it is keyed on `statement_id` and enforces the statement workflow
DRAFT -> UNDER_REVIEW -> APPROVED. A proof object is not a statement and has no
statement id, and forcing one in would put geometry rows into the log that
answers "who approved this statement". Separate store, same discipline.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from timonelo.canonical import canonical_dump
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus
from timonelo.spatial.review import BANNED_PHANTOM_REVIEWERS

SUPPORTED_RECORD_TYPE = "timonelo.deck-review.staged-record.v1"
SUPPORTED_APPLICATION_STATUS = "STAGED_NOT_APPLIED"

#: Decisions a human may record on a geometry envelope, and the review state
#: each one establishes. UNREVIEWED is absent on purpose: it is the absence of a
#: decision, not a decision, and must never be applied.
DECISION_TO_REVIEW_STATE: Dict[str, HumanReviewState] = {
    "ACCEPT": HumanReviewState.APPROVED,
    "REJECT": HumanReviewState.REJECTED,
    "NEEDS_CORRECTION": HumanReviewState.UNDER_REVIEW,
}

#: Transitions permitted on the geometry review axis.
#:
#: This table is declared here rather than borrowed from
#: `evidence.review.ALLOWED`, and it differs from it in one way that matters:
#: DRAFT -> APPROVED is permitted. The statement workflow inserts UNDER_REVIEW
#: because authoring and reviewing a statement are separate human acts. A proof
#: object arrives in DRAFT from an extractor and is judged by a human, so the two
#: parties are already distinct and an UNDER_REVIEW step would be a formality
#: with nobody on either side of it.
#:
#: This is a policy choice and is flagged as one. Everything else stays closed:
#: an approved or rejected object cannot be re-decided here, and a second,
#: different decision needs an explicit supersession mechanism that does not yet
#: exist.
ALLOWED_GEOMETRY_TRANSITIONS: Dict[HumanReviewState, frozenset] = {
    HumanReviewState.DRAFT: frozenset({
        HumanReviewState.APPROVED,
        HumanReviewState.REJECTED,
        HumanReviewState.UNDER_REVIEW,
    }),
    HumanReviewState.UNDER_REVIEW: frozenset({
        HumanReviewState.APPROVED,
        HumanReviewState.REJECTED,
    }),
    HumanReviewState.APPROVED: frozenset(),
    HumanReviewState.REJECTED: frozenset(),
    HumanReviewState.SUPERSEDED: frozenset(),
}

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVIEW_STATE_VALUES = frozenset(st.value for st in HumanReviewState)


class ApplyRefusal(str, Enum):
    """Every reason a staged record is not applied. One is enough to refuse."""

    MALFORMED_RECORD = "MALFORMED_RECORD"
    UNSUPPORTED_RECORD_TYPE = "UNSUPPORTED_RECORD_TYPE"
    NOT_STAGED = "NOT_STAGED"
    ALREADY_MARKED_APPLIED = "ALREADY_MARKED_APPLIED"
    PROOF_NOT_FOUND = "PROOF_NOT_FOUND"
    PROOF_DIGEST_MISMATCH = "PROOF_DIGEST_MISMATCH"
    ARTIFACT_NOT_FOUND = "ARTIFACT_NOT_FOUND"
    ARTIFACT_DIGEST_MISMATCH = "ARTIFACT_DIGEST_MISMATCH"
    RASTER_NOT_FOUND = "RASTER_NOT_FOUND"
    RASTER_DIGEST_MISMATCH = "RASTER_DIGEST_MISMATCH"
    OBJECT_NOT_IN_PROOF = "OBJECT_NOT_IN_PROOF"
    OBJECT_IDENTITY_DRIFT = "OBJECT_IDENTITY_DRIFT"
    PRE_STATE_DRIFT = "PRE_STATE_DRIFT"
    REVIEWER_MISSING_OR_PLACEHOLDER = "REVIEWER_MISSING_OR_PLACEHOLDER"
    UNSUPPORTED_DECISION = "UNSUPPORTED_DECISION"
    REVIEW_TRANSITION_NOT_PERMITTED = "REVIEW_TRANSITION_NOT_PERMITTED"
    CONFLICTING_ADJUDICATION_EXISTS = "CONFLICTING_ADJUDICATION_EXISTS"
    REVIEW_ACT_WOULD_CHANGE_EVIDENCE = "REVIEW_ACT_WOULD_CHANGE_EVIDENCE"
    REVIEW_ACT_WOULD_CHANGE_PUBLICATION = "REVIEW_ACT_WOULD_CHANGE_PUBLICATION"


class StagedRecordError(RuntimeError):
    """Raised by the applying form when a record is refused."""


@dataclass(frozen=True)
class PlannedMutation:
    """Exactly what would be appended, stated before anything is written."""

    object_id: str
    deck_number: int
    proof_sha256: str
    from_review_state: str
    to_review_state: str
    geometry_judgement: str
    #: Carried through untouched. Present so a reader can see they do not move.
    evidence_condition: str
    publish_status: str
    reviewer: str
    reviewed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class ApplyResult:
    dry_run: bool
    applied: bool
    already_applied: bool = False
    refusals: List[Tuple[ApplyRefusal, str]] = field(default_factory=list)
    planned: List[PlannedMutation] = field(default_factory=list)
    log_path: Optional[str] = None

    @property
    def refusal_codes(self) -> List[ApplyRefusal]:
        return [code for code, _ in self.refusals]

    def summary(self) -> str:
        if self.already_applied:
            return "ALREADY_APPLIED: this record is already in the adjudication log"
        if self.refusals:
            return "REFUSED: " + "; ".join(f"{c.value}: {d}" for c, d in self.refusals)
        verb = "WOULD APPLY" if self.dry_run else "APPLIED"
        return f"{verb}: " + "; ".join(
            f"{m.object_id} {m.from_review_state} -> {m.to_review_state}" for m in self.planned
        )


def _sha256_file(path: str) -> Optional[str]:
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class SpatialAdjudicationLog:
    """Append-only record of applied human geometry adjudications.

    Same discipline as `evidence.review.ReviewLog`: entries are appended, never
    edited, and a correction is a new entry rather than a rewrite. Keyed on
    `(object_id, proof_sha256)`, because a decision is about one object as it
    existed in one proof; regenerate the proof and the old decision is history,
    not a verdict on the new geometry.
    """

    def __init__(self, path: str):
        self.path = path
        self._entries: List[Dict[str, Any]] = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                text = fh.read().strip()
            if text:
                loaded = json.loads(text)
                self._entries = loaded.get("entries", []) if isinstance(loaded, dict) else list(loaded)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def for_object(self, object_id: str, proof_sha256: Optional[str] = None) -> List[Dict[str, Any]]:
        """Entries for one object, optionally bound to one proof.

        Non-object rows are skipped rather than raising. A log that somebody
        hand-edited into nonsense should make the projection fall back to the
        proof, not take the process down.
        """
        return [
            e for e in self._entries
            if isinstance(e, dict)
            and e.get("object_id") == object_id
            and (proof_sha256 is None or e.get("proof_sha256") == proof_sha256)
        ]

    def append(self, entry: Dict[str, Any]) -> None:
        self._entries.append(entry)
        self._flush()

    def _flush(self) -> None:
        canonical_dump(
            {
                "record_type": "timonelo.spatial.adjudication-log.v1",
                "note": (
                    "Append-only. Each entry is one applied human geometry "
                    "adjudication. Corrections are new entries, never edits. "
                    "No entry here establishes evidence or publication."
                ),
                "entries": self._entries,
            },
            self.path,
        )


def current_geometry_review_state(
    obj: Dict[str, Any],
    proof_sha256: str,
    log: SpatialAdjudicationLog,
) -> str:
    """The review state of a proof object now: extracted state plus adjudications.

    THE canonical projection. Computed rather than read off the object, because
    the object is an extraction record and the decision lives in the log. Every
    governed consumer of a proof object's review state goes through here; a
    second implementation somewhere else is how a review log becomes a log
    nothing reads.

    Only the review axis is projected. An APPROVED entry never becomes SUPPORTED
    evidence, PUBLISH_ALLOWED, or an admitted identity, because none of those is
    a thing a human looking at a drawing established.

    Binding is on `(object_id, proof_sha256)` together. Matching on object id
    alone would let a decision taken against one geometry vouch for whatever
    later took the same id, which is exactly the fake-provenance shape this
    repository keeps removing. A decision against a superseded proof is history;
    the new proof's own governed state stands until somebody reviews it again.

    No entry means no change: the proof's stored state is returned untouched, so
    a repository with no adjudication log behaves exactly as it did before this
    mechanism existed.
    """
    object_id = str(obj.get("object_id") or "")
    stored = str(obj.get("human_review_state", HumanReviewState.DRAFT.value))
    if not object_id or not _SHA256.match(str(proof_sha256 or "")):
        # Nothing to bind to. Fail closed onto the extraction record.
        return stored

    entries = [e for e in log.for_object(object_id, str(proof_sha256))
               if isinstance(e, dict) and e.get("to_review_state")]
    if not entries:
        return stored

    projected = str(entries[-1].get("to_review_state"))
    if projected not in _REVIEW_STATE_VALUES:
        # A log entry naming a state that does not exist projects nothing.
        return stored
    return projected


def duplicate_object_ids(proof: Dict[str, Any]) -> frozenset:
    """Object ids that appear more than once in one proof.

    Not hypothetical: `deck07.proof.json` carries
    `bellissima-deck07-venue-champagne-bar` twice. An id that names two objects
    cannot carry a decision about one of them, so the projection refuses to
    project onto any of them.
    """
    seen: Dict[str, int] = {}
    for o in proof.get("objects", []):
        if isinstance(o, dict):
            oid = str(o.get("object_id") or "")
            seen[oid] = seen.get(oid, 0) + 1
    return frozenset(oid for oid, n in seen.items() if n > 1)


def project_proof_review_states(
    proof: Dict[str, Any],
    proof_sha256: str,
    log: Optional[SpatialAdjudicationLog] = None,
    *,
    repo_root: str = ".",
) -> Dict[str, str]:
    """Effective review state for every object in one proof, keyed by object id.

    An id that appears twice in the proof is returned at its stored state and
    never projected: a decision recorded against that id cannot be attributed to
    one of the two objects wearing it, and projecting onto both would let one
    human review vouch for geometry nobody looked at.
    """
    log = log if log is not None else SpatialAdjudicationLog(
        os.path.join(repo_root, "evidence", "reviews", "spatial_adjudications.json")
    )
    ambiguous = duplicate_object_ids(proof)
    projected: Dict[str, str] = {}
    for o in proof.get("objects", []):
        if not isinstance(o, dict):
            continue
        oid = str(o.get("object_id") or "")
        if oid in ambiguous:
            projected[oid] = str(o.get("human_review_state", HumanReviewState.DRAFT.value))
            continue
        projected[oid] = current_geometry_review_state(o, proof_sha256, log)
    return projected


def _entry_fingerprint(record: Dict[str, Any], entry: Dict[str, Any]) -> str:
    """Identifies one decision from one staged record, for replay detection."""
    basis = "|".join([
        str(record.get("proof_sha256", "")),
        str(entry.get("objectId", "")),
        str(entry.get("decision", "")),
        str(entry.get("reviewer", "")),
        str(entry.get("timestamp", "")),
    ])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _load_proof(repo_root: str, proof_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
    full = os.path.join(repo_root, proof_path.replace("/", os.sep))
    digest = _sha256_file(full)
    if digest is None:
        return None, None, full
    with open(full, encoding="utf-8") as fh:
        return json.load(fh), digest, full


def evaluate_staged_record(
    record: Any,
    *,
    repo_root: str = ".",
    log: Optional[SpatialAdjudicationLog] = None,
    artifact_path: Optional[str] = None,
    raster_path: Optional[str] = None,
) -> ApplyResult:
    """Decide whether a staged record may be applied. Never writes.

    Collects every reason to refuse rather than stopping at the first, so a
    curator sees the whole picture. An empty refusal list is the only thing that
    admits, and a partial apply is never produced: it is all entries or none.
    """
    result = ApplyResult(dry_run=True, applied=False)
    log = log if log is not None else SpatialAdjudicationLog(
        os.path.join(repo_root, "evidence", "reviews", "spatial_adjudications.json")
    )
    result.log_path = log.path

    if not isinstance(record, dict):
        result.refusals.append((ApplyRefusal.MALFORMED_RECORD, f"record is {type(record).__name__}, not an object"))
        return result

    if record.get("record_type") != SUPPORTED_RECORD_TYPE:
        result.refusals.append((
            ApplyRefusal.UNSUPPORTED_RECORD_TYPE,
            f"record_type {record.get('record_type')!r} is not {SUPPORTED_RECORD_TYPE}",
        ))
    if record.get("application_status") != SUPPORTED_APPLICATION_STATUS:
        result.refusals.append((
            ApplyRefusal.NOT_STAGED,
            f"application_status is {record.get('application_status')!r}",
        ))
    if record.get("applied_to_repository") is not False:
        result.refusals.append((
            ApplyRefusal.ALREADY_MARKED_APPLIED,
            f"applied_to_repository is {record.get('applied_to_repository')!r}, not false",
        ))

    entries = record.get("entries")
    if not isinstance(entries, list) or not entries:
        result.refusals.append((ApplyRefusal.MALFORMED_RECORD, "record carries no entries"))
        return result

    source = record.get("source") or {}
    proof_path = record.get("proof_path")
    claimed_proof_sha = record.get("proof_sha256")
    if not isinstance(proof_path, str) or not _SHA256.match(str(claimed_proof_sha)):
        result.refusals.append((ApplyRefusal.MALFORMED_RECORD, "record has no usable proof path or digest"))
        return result

    proof, actual_proof_sha, full_proof_path = _load_proof(repo_root, proof_path)
    if proof is None:
        result.refusals.append((ApplyRefusal.PROOF_NOT_FOUND, f"{full_proof_path} does not exist"))
        return result
    if actual_proof_sha != claimed_proof_sha:
        result.refusals.append((
            ApplyRefusal.PROOF_DIGEST_MISMATCH,
            f"record cites proof {claimed_proof_sha[:12]}, repository holds {actual_proof_sha[:12]}",
        ))

    # The source artifact the proof was read from.
    claimed_artifact_sha = source.get("artifact_sha256")
    resolved_artifact = artifact_path or (
        proof.get("source", {}).get("physical_pdf_path") if isinstance(proof.get("source"), dict) else None
    )
    if not resolved_artifact:
        result.refusals.append((ApplyRefusal.ARTIFACT_NOT_FOUND, "no artifact path could be resolved"))
    else:
        full_artifact = os.path.join(repo_root, str(resolved_artifact).replace("/", os.sep))
        actual_artifact_sha = _sha256_file(full_artifact)
        if actual_artifact_sha is None:
            result.refusals.append((ApplyRefusal.ARTIFACT_NOT_FOUND, f"{full_artifact} does not exist"))
        elif actual_artifact_sha != claimed_artifact_sha:
            result.refusals.append((
                ApplyRefusal.ARTIFACT_DIGEST_MISMATCH,
                f"record cites artifact {str(claimed_artifact_sha)[:12]}, repository holds {actual_artifact_sha[:12]}",
            ))

    # The raster the human actually looked at.
    claimed_raster_sha = source.get("review_image_sha256")
    resolved_raster = raster_path or _raster_path_for(source)
    if claimed_raster_sha is None:
        result.refusals.append((ApplyRefusal.RASTER_DIGEST_MISMATCH, "record records no review image digest"))
    elif not resolved_raster:
        result.refusals.append((ApplyRefusal.RASTER_NOT_FOUND, "no review raster path could be resolved"))
    else:
        full_raster = os.path.join(repo_root, resolved_raster.replace("/", os.sep))
        actual_raster_sha = _sha256_file(full_raster)
        if actual_raster_sha is None:
            result.refusals.append((ApplyRefusal.RASTER_NOT_FOUND, f"{full_raster} does not exist"))
        elif actual_raster_sha != claimed_raster_sha:
            result.refusals.append((
                ApplyRefusal.RASTER_DIGEST_MISMATCH,
                f"record cites raster {str(claimed_raster_sha)[:12]}, repository holds {actual_raster_sha[:12]}",
            ))

    objects = {o.get("object_id"): o for o in proof.get("objects", []) if isinstance(o, dict)}
    deck_number = record.get("deck_number")

    planned: List[PlannedMutation] = []
    already = 0
    for entry in entries:
        if not isinstance(entry, dict):
            result.refusals.append((ApplyRefusal.MALFORMED_RECORD, "an entry is not an object"))
            continue
        oid = entry.get("objectId")
        obj = objects.get(oid)
        if obj is None:
            result.refusals.append((ApplyRefusal.OBJECT_NOT_IN_PROOF, f"{oid} is not in {proof_path}"))
            continue

        # Replay is settled before anything else is checked. Applying this entry
        # is what moved the repository past the state the record describes, so
        # running the drift checks on a second pass would report the first apply
        # as tampering and turn an idempotent replay into an accusation.
        fingerprint = _entry_fingerprint(record, entry)
        prior = log.for_object(str(oid), str(actual_proof_sha))
        if any(pr.get("staged_entry_fingerprint") == fingerprint for pr in prior):
            already += 1
            continue
        if prior:
            last = prior[-1]
            result.refusals.append((
                ApplyRefusal.CONFLICTING_ADJUDICATION_EXISTS,
                f"{oid}: already adjudicated {last.get('decision')} by {last.get('reviewer')} "
                f"on {last.get('reviewed_at')}; a different decision needs an explicit supersession",
            ))
            continue

        # The object must still be the one that was reviewed, not merely an id
        # that survived. Geometry provenance and semantic type are what the
        # human was looking at.
        pre = entry.get("preReviewState") or {}
        drift: List[str] = []
        if entry.get("deckNumber") not in (None, deck_number):
            drift.append(f"entry deck {entry.get('deckNumber')} != record deck {deck_number}")
        if proof.get("deck", {}).get("number") != deck_number:
            drift.append(f"proof deck {proof.get('deck', {}).get('number')} != record deck {deck_number}")
        if drift:
            result.refusals.append((ApplyRefusal.OBJECT_IDENTITY_DRIFT, f"{oid}: " + "; ".join(drift)))

        current = {
            "humanReviewState": str(obj.get("human_review_state")),
            "publishStatus": str(obj.get("publish_status")),
            "evidenceCondition": str(obj.get("evidence_condition")),
        }
        # The stored object plus any adjudication already applied is the real
        # current state; a record made against a stale view must not apply.
        current["humanReviewState"] = current_geometry_review_state(obj, str(actual_proof_sha), log)
        if any(str(pre.get(k)) != v for k, v in current.items()):
            result.refusals.append((
                ApplyRefusal.PRE_STATE_DRIFT,
                f"{oid}: record saw {json.dumps(pre, sort_keys=True)}, repository holds {json.dumps(current, sort_keys=True)}",
            ))

        reviewer = str(entry.get("reviewer") or record.get("reviewer") or "").strip()
        if not reviewer or reviewer.lower() in BANNED_PHANTOM_REVIEWERS:
            result.refusals.append((
                ApplyRefusal.REVIEWER_MISSING_OR_PLACEHOLDER,
                f"{oid}: reviewer {reviewer!r} is empty or a placeholder identity",
            ))

        decision = str(entry.get("decision") or "")
        to_state = DECISION_TO_REVIEW_STATE.get(decision)
        if to_state is None:
            result.refusals.append((
                ApplyRefusal.UNSUPPORTED_DECISION,
                f"{oid}: decision {decision!r} is not one a human may apply",
            ))
        else:
            try:
                from_state = HumanReviewState(current["humanReviewState"])
            except ValueError:
                from_state = None
            if from_state is None:
                result.refusals.append((
                    ApplyRefusal.PRE_STATE_DRIFT,
                    f"{oid}: current review state {current['humanReviewState']!r} is not a known state",
                ))
            elif to_state not in ALLOWED_GEOMETRY_TRANSITIONS.get(from_state, frozenset()):
                result.refusals.append((
                    ApplyRefusal.REVIEW_TRANSITION_NOT_PERMITTED,
                    f"{oid}: {from_state.value} -> {to_state.value} is not a permitted geometry review transition",
                ))

        # A review act may not move the evidence or publication axes. The record
        # itself is checked, so a record built by some other tool cannot smuggle
        # a promotion through this path.
        post = entry.get("postReviewState") or {}
        if str(post.get("evidenceCondition")) != current["evidenceCondition"]:
            result.refusals.append((
                ApplyRefusal.REVIEW_ACT_WOULD_CHANGE_EVIDENCE,
                f"{oid}: record would move evidence_condition "
                f"{current['evidenceCondition']} -> {post.get('evidenceCondition')}; "
                "a review decision is not an evidence event",
            ))
        if str(post.get("publishStatus")) != current["publishStatus"]:
            result.refusals.append((
                ApplyRefusal.REVIEW_ACT_WOULD_CHANGE_PUBLICATION,
                f"{oid}: record would move publish_status "
                f"{current['publishStatus']} -> {post.get('publishStatus')}; "
                "publication is not granted by review",
            ))

        if to_state is not None:
            planned.append(PlannedMutation(
                object_id=str(oid),
                deck_number=int(deck_number) if isinstance(deck_number, int) else -1,
                proof_sha256=str(actual_proof_sha),
                from_review_state=current["humanReviewState"],
                to_review_state=to_state.value,
                geometry_judgement=str(entry.get("geometryJudgement") or ""),
                evidence_condition=current["evidenceCondition"],
                publish_status=current["publishStatus"],
                reviewer=reviewer,
                reviewed_at=str(entry.get("timestamp") or record.get("generated_at") or ""),
            ))

    if result.refusals:
        # All-or-nothing, in the report as well as in the writing: a plan shown
        # next to a refusal would read as a partial apply.
        result.planned = []
        return result

    result.planned = planned
    if already and not planned:
        result.already_applied = True
    return result


def _raster_path_for(source: Dict[str, Any]) -> Optional[str]:
    """Where the review raster lives, from the record's own provenance pointer."""
    record_path = source.get("review_image_provenance_record")
    if isinstance(record_path, str) and record_path.endswith(".provenance.json"):
        # The raster sits beside its provenance record.
        asset = str(source.get("review_image_uri") or "").rsplit("/", 1)[-1]
        if asset:
            return os.path.dirname(record_path) + "/" + asset
    return None


def apply_staged_record(
    record: Any,
    *,
    repo_root: str = ".",
    dry_run: bool = True,
    log: Optional[SpatialAdjudicationLog] = None,
    artifact_path: Optional[str] = None,
    raster_path: Optional[str] = None,
) -> ApplyResult:
    """Apply a staged record, or explain why it will not be applied.

    `dry_run=True` is the default because applying a human decision is the kind
    of thing that should be typed out on purpose. A dry run reports the exact
    entries it would append and writes nothing.

    Refusals are all-or-nothing: if any entry in the record is refused, no entry
    is applied. A record is one human sitting down once, and half of that is not
    a smaller version of it.
    """
    log = log if log is not None else SpatialAdjudicationLog(
        os.path.join(repo_root, "evidence", "reviews", "spatial_adjudications.json")
    )
    result = evaluate_staged_record(
        record, repo_root=repo_root, log=log, artifact_path=artifact_path, raster_path=raster_path
    )
    result.dry_run = dry_run

    if result.refusals or result.already_applied or not result.planned:
        return result
    if dry_run:
        return result

    entries = record.get("entries", [])
    by_object = {str(e.get("objectId")): e for e in entries if isinstance(e, dict)}
    for mutation in result.planned:
        staged_entry = by_object.get(mutation.object_id, {})
        log.append({
            "object_id": mutation.object_id,
            "deck_number": mutation.deck_number,
            "proof_path": record.get("proof_path"),
            "proof_sha256": mutation.proof_sha256,
            "source_artifact_id": (record.get("source") or {}).get("artifact_id"),
            "source_artifact_sha256": (record.get("source") or {}).get("artifact_sha256"),
            "review_image_sha256": (record.get("source") or {}).get("review_image_sha256"),
            "decision": str(staged_entry.get("decision")),
            "geometry_judgement": mutation.geometry_judgement,
            "from_review_state": mutation.from_review_state,
            "to_review_state": mutation.to_review_state,
            # Recorded so a reader can see these did not move, and so a later
            # change to either is visibly not attributable to this review.
            "evidence_condition_unchanged": mutation.evidence_condition,
            "publish_status_unchanged": mutation.publish_status,
            "reviewer": mutation.reviewer,
            "reviewed_at": mutation.reviewed_at,
            "note": str(staged_entry.get("note") or ""),
            "staged_record_generated_at": record.get("generated_at"),
            "staged_entry_fingerprint": _entry_fingerprint(record, staged_entry),
        })
    result.applied = True
    return result


def require_apply(record: Any, **kwargs: Any) -> ApplyResult:
    """Apply or raise. For callers that are gates rather than reporters."""
    result = apply_staged_record(record, **kwargs)
    if result.refusals:
        raise StagedRecordError(result.summary())
    return result
