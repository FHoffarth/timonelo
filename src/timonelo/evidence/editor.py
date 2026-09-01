"""
Statement Editor — the sole creator of Statements.

Governed by ADR-0002 §1, §6.

Statements are authored here and nowhere else. Every statement is created in
DRAFT with UNKNOWN evidence condition, and must be carried through the human review
workflow and evidence support verification before it can be considered for publication.

A statement created here always cites:
  * the Artifact ID it came from (never a digest typed by hand),
  * the page and locator within that artifact,
  * the human who read it,
  * the date they read it.

If any of those is missing the statement cannot be created.
"""

from __future__ import annotations

import os
from dataclasses import replace
from typing import Any, Dict, List, Optional, Tuple

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.publication import (
    StatementPublicationError,
    evaluate_statement_publication_admission,
    has_structural_backing,
    require_statement_publication_admission,
)
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.conflicts import (
    ConflictError,
    ConflictLog,
    validity_overlaps,
    values_disagree,
)
from timonelo.evidence.models import Statement
from timonelo.evidence.review import ReviewLog
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)


class EditorError(ValueError):
    pass


class StatementEditor:
    """Authors statements and moves them through review, verification, and publication."""

    ID_PREFIX = "STM-"

    def __init__(self, path: str, registry: ArtifactRegistry, review_log: ReviewLog,
                 conflict_log: Optional[ConflictLog] = None,
                 events=None, questions=None):
        self.path = path
        self.registry = registry
        self.review_log = review_log
        self.conflict_log = conflict_log
        # Publication admission needs the evidence log and the question
        # registry. Both default to None and the gate fails closed without
        # them: an editor that cannot resolve an event cannot prove backing,
        # so it must not publish. `Workspace` wires the real ones.
        self.events = events
        self.questions = questions
        #: Statements whose stored PUBLISH_ALLOWED rested on nothing at all and
        #: were demoted while loading. Recorded rather than silently dropped.
        self.demoted_on_load: List[str] = []
        self._by_id: Dict[str, Statement] = {}
        if os.path.exists(path):
            import json
            with open(path, encoding="utf-8") as f:
                for sid, raw in json.load(f).items():
                    # Handle backward compatible dict format if older keys present
                    if "review_state" in raw and "human_review_state" not in raw:
                        old_s = raw.pop("review_state")
                        if old_s == "PUBLISHED":
                            # A stored string is not evidence. The legacy value
                            # records that a human once approved the record; it
                            # cannot re-confer publication, because nothing in
                            # the file proves the claim is backed. Re-publishing
                            # goes through `publish()`, which checks.
                            raw["human_review_state"] = HumanReviewState.APPROVED.value
                            raw["publish_status"] = PublishStatus.PUBLISH_BLOCKED.value
                        elif old_s in HumanReviewState._value2member_map_:
                            raw["human_review_state"] = old_s
                            raw["publish_status"] = PublishStatus.PUBLISH_BLOCKED.value
                        else:
                            raw["human_review_state"] = HumanReviewState.DRAFT.value
                            raw["publish_status"] = PublishStatus.PUBLISH_BLOCKED.value
                    if "evidence_condition" not in raw:
                        raw["evidence_condition"] = EvidenceCondition.UNKNOWN.value
                    if "publish_status" not in raw:
                        raw["publish_status"] = PublishStatus.PUBLISH_BLOCKED.value
                    self._by_id[sid] = Statement(**raw)
        # Restoration is a publication boundary too. A persisted statement can
        # claim PUBLISH_ALLOWED while citing an event that does not exist, and
        # R1 only checked that it cited *something* -- so the claim survived
        # load and every reader downstream served it as truth. Readers must not
        # each re-derive admission, so the invariant is established here
        # instead: after load, no statement in memory holds authoritative state
        # its evidence cannot currently support.
        self._revalidate_published()

    def _revalidate_published(self) -> None:
        """Demote any loaded statement whose publication is not currently valid.

        Full admission where the evidence log and question registry are
        available, and the cheap structural check where they are not -- an
        editor constructed without them cannot resolve events, and demoting
        every published statement on that basis would be wrong rather than
        safe. Digest work is cached, so repeat loads are inexpensive.

        Only `publish_status` is touched. The record's content, its evidence
        condition and its review history are left exactly as stored: the claim
        is preserved, only its unsupported authority is withdrawn.
        """
        for sid, statement in list(self._by_id.items()):
            if statement.publish_status is PublishStatus.PUBLISH_BLOCKED:
                continue
            if self.events is not None and self.questions is not None:
                admitted = evaluate_statement_publication_admission(
                    statement,
                    events=self.events,
                    registry=self.registry,
                    questions=self.questions,
                    statements_by_id=self._by_id,
                ).admitted
            else:
                admitted = has_structural_backing(statement)
            if not admitted:
                self._by_id[sid] = replace(
                    statement, publish_status=PublishStatus.PUBLISH_BLOCKED
                )
                self.demoted_on_load.append(sid)

    def _next_id(self) -> str:
        nums = []
        for k in self._by_id:
            if k.startswith(self.ID_PREFIX):
                suffix = k[len(self.ID_PREFIX):]
                if suffix.isdigit():
                    nums.append(int(suffix))
        n = 1 + max(nums, default=0)
        return f"{self.ID_PREFIX}{n:04d}"

    def create(
        self,
        entity_id: str,
        question_id: str,
        statement_type: str,
        value: Any,
        artifact_id: str,
        locator: str,
        read_by: str,
        read_on: str,
        page: Optional[int] = None,
        method: str = "DIRECT",
        derivation_note: str = "",
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        note: str = "",
        evidence_event_ids: Tuple[str, ...] = (),
        input_statement_ids: Tuple[str, ...] = (),
        rule_hash: Optional[str] = None,
    ) -> Statement:
        """Author one statement in DRAFT with UNKNOWN evidence condition."""
        try:
            canonical_method = Method(method)
        except ValueError:
            raise EditorError(f"Unknown method {method!r}.")

        if canonical_method == Method.INFERRED:
            if not derivation_note:
                raise EditorError("An INFERRED statement must record its derivation_note.")
            if not input_statement_ids:
                raise EditorError("An INFERRED statement requires input_statement_ids.")
        else:
            artifact = self.registry.get(artifact_id)  # raises if not held
            if not locator:
                raise EditorError(
                    "A statement requires a locator: WHERE in the artifact the "
                    "value was read."
                )
            if canonical_method is not Method.DIRECT and not derivation_note:
                raise EditorError(
                    f"A {method} statement must record its derivation_note: which "
                    "printed facts were combined, and how."
                )
            # Statement Authority Matrix: does this class have authority here?
            authority.check(statement_type, artifact.document_class)

        if not read_by or not read_on:
            raise EditorError(
                "A statement requires the reader's name and the date read."
            )

        statement = Statement(
            statement_id=self._next_id(),
            entity_id=entity_id,
            question_id=question_id,
            statement_type=statement_type,
            value=value,
            artifact_id=artifact_id,
            page=page,
            locator=locator,
            read_by=read_by,
            read_on=read_on,
            method=canonical_method,
            derivation_note=derivation_note,
            evidence_event_ids=evidence_event_ids,
            input_statement_ids=input_statement_ids,
            rule_hash=rule_hash,
            evidence_condition=EvidenceCondition.UNKNOWN,
            human_review_state=HumanReviewState.DRAFT,
            publish_status=PublishStatus.PUBLISH_BLOCKED,
            valid_from=valid_from,
            valid_until=valid_until,
            note=note,
        )
        self._by_id[statement.statement_id] = statement
        self._flush()

        # Conflict existence is independent from evidence, review, and publish axes.
        if self.conflict_log is not None:
            self.conflict_log._record_detection_run(
                candidate_statement_id=statement.statement_id,
                checked_statement_count=len(self._by_id) - 1,
                executed_on=read_on,
            )
            for existing in self._by_id.values():
                if existing.statement_id == statement.statement_id:
                    continue
                if existing.entity_id != entity_id or existing.question_id != question_id:
                    continue
                if existing.statement_type != statement_type:
                    continue
                if not validity_overlaps(
                    existing.valid_from,
                    existing.valid_until,
                    statement.valid_from,
                    statement.valid_until,
                ):
                    continue
                if values_disagree(existing.value, value):
                    self.conflict_log.record(
                        entity_id=entity_id,
                        question_id=question_id,
                        statement_type=statement_type,
                        incumbent_statement_id=existing.statement_id,
                        incumbent_value=existing.value,
                        challenger_statement_id=statement.statement_id,
                        challenger_value=value,
                        detected_on=read_on,
                    )
        return statement

    def set_evidence_condition(
        self,
        statement_id: str,
        condition: EvidenceCondition,
        actor: str,
        occurred_on: str,
        note: str = "",
    ) -> Statement:
        """Explicitly set or update the evidence condition of a statement with full audit trail."""
        if not actor:
            raise EditorError("Setting evidence condition requires a named actor.")
        if not occurred_on:
            raise EditorError("Setting evidence condition requires an occurred_on timestamp.")
        current = self._by_id[statement_id]
        from_cond = current.condition
        to_cond = condition if isinstance(condition, EvidenceCondition) else EvidenceCondition(condition)

        # Record in review log for audit trail
        if self.review_log is not None:
            self.review_log.record_condition_transition(
                statement_id, from_cond, to_cond, actor, occurred_on, note
            )

        pub_status = current.publish_status
        if to_cond is not EvidenceCondition.SUPPORTED:
            pub_status = PublishStatus.PUBLISH_BLOCKED
        updated = replace(current, evidence_condition=to_cond, publish_status=pub_status)
        self._by_id[statement_id] = updated
        self._flush()
        return updated

    def transition(
        self,
        statement_id: str,
        to_state: HumanReviewState,
        actor: str,
        occurred_on: str,
        note: str = "",
    ) -> Statement:
        """Advance a statement through human review workflow."""
        current = self._by_id[statement_id]

        self.review_log.transition(
            statement_id, current.state, to_state, actor, occurred_on, note
        )
        # If rejected or superseded, ensure publish status is BLOCKED
        pub_status = current.publish_status
        if to_state in (HumanReviewState.REJECTED, HumanReviewState.SUPERSEDED):
            pub_status = PublishStatus.PUBLISH_BLOCKED

        updated = replace(current, human_review_state=to_state, publish_status=pub_status)
        self._by_id[statement_id] = updated
        self._flush()
        return updated

    def publish(
        self,
        statement_id: str,
        actor: str,
        occurred_on: str,
        note: str = "",
    ) -> Statement:
        """Publish an approved and supported statement so it can answer passenger queries."""
        current = self._by_id[statement_id]

        if current.state != HumanReviewState.APPROVED and current.state != HumanReviewState.APPROVED.value:
            raise EditorError(
                f"{statement_id} is in state {current.human_review_state} and cannot be "
                "published. Human review state must be APPROVED first."
            )
        if current.condition != EvidenceCondition.SUPPORTED and current.condition != EvidenceCondition.SUPPORTED.value:
            raise EditorError(
                f"{statement_id} has evidence condition {current.evidence_condition} and cannot be "
                "published. Evidence condition must be SUPPORTED first."
            )
        if actor == current.read_by:
            raise EditorError(
                f"{actor} read this statement and cannot also publish it. "
                "Review is only meaningful with a second pair of eyes."
            )

        # Evidence admission. The axes checked above are caller-set:
        # `set_evidence_condition` accepts SUPPORTED as a bare assertion, so
        # SUPPORTED + APPROVED proves only that somebody said so. This is where
        # the claim is checked against evidence actually held, converging with
        # EvidenceGatekeeper rather than disagreeing with it.
        try:
            require_statement_publication_admission(
                current,
                events=self.events,
                registry=self.registry,
                questions=self.questions,
                statements_by_id=self._by_id,
            )
        except StatementPublicationError as exc:
            raise EditorError(str(exc)) from exc

        updated = replace(current, publish_status=PublishStatus.PUBLISH_ALLOWED)
        self._by_id[statement_id] = updated
        self._flush()
        return updated

    def get(self, statement_id: str) -> Statement:
        return self._by_id[statement_id]

    def all(self) -> List[Statement]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)

    def _flush(self) -> None:
        canonical_dump({k: v.to_dict() for k, v in self._by_id.items()}, self.path)

    def resolve_conflict(
        self,
        conflict_id: str,
        winning_statement_id: Optional[str],
        actor: str,
        occurred_on: str,
        note: str,
    ):
        """Record a conflict decision without changing any lifecycle axis."""
        if self.conflict_log is None:
            raise EditorError("No conflict log is attached to this editor.")
        conflict = self.conflict_log.get(conflict_id)

        if winning_statement_id is not None and winning_statement_id not in conflict.statement_ids():
            raise ConflictError(f"{winning_statement_id} is not part of conflict {conflict_id}")
        return self.conflict_log.resolve(
            conflict_id, winning_statement_id, actor, occurred_on, note)
