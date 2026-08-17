"""
Statement Editor — the sole creator of Statements.

Governed by ADR-0002 §1, §6.

Statements are authored here and nowhere else. Every statement is created in
DRAFT and must be carried through the review workflow by a named actor before
it can answer a passenger's question.

A statement created here always cites:
  * the Artifact ID it came from (never a digest typed by hand),
  * the page and locator within that artifact,
  * the human who read it,
  * the date they read it.

If any of those is missing the statement cannot be created. That is the whole
point: a claim whose reader, page and date are unrecorded is indistinguishable
from a claim someone invented.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Optional

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.conflicts import ConflictLog, values_disagree
from timonelo.evidence.review import ANSWERABLE, ReviewError, ReviewLog, ReviewState


class EditorError(ValueError):
    pass


@dataclass(frozen=True)
class Statement:
    """One manually authored claim, tied to one artifact.

    Carries no confidence field (ADR-0002 I1). Confidence is computed from the
    artifact's document class at query time.
    """
    statement_id: str
    entity_id: str
    question_id: str
    statement_type: str
    value: Any
    artifact_id: str
    page: Optional[int]
    locator: str
    read_by: str
    read_on: str
    # ADR-0002 6.1. Manual curation is almost always DIRECT: a human read the
    # value off the page. CALCULATED covers deductions from two or more printed
    # facts (e.g. a legend colour shared by two category codes, disambiguated by
    # the printed deck range). derivation_note must state the reasoning.
    method: str = "DIRECT"
    derivation_note: str = ""
    review_state: str = ReviewState.DRAFT.value
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement_id": self.statement_id,
            "entity_id": self.entity_id,
            "question_id": self.question_id,
            "statement_type": self.statement_type,
            "value": self.value,
            "artifact_id": self.artifact_id,
            "page": self.page,
            "locator": self.locator,
            "read_by": self.read_by,
            "read_on": self.read_on,
            "method": self.method,
            "derivation_note": self.derivation_note,
            "review_state": self.review_state,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "note": self.note,
        }

    @property
    def state(self) -> ReviewState:
        return ReviewState(self.review_state)


class StatementEditor:
    """Authors statements and moves them through review."""

    ID_PREFIX = "STM-"

    def __init__(self, path: str, registry: ArtifactRegistry, review_log: ReviewLog,
                 conflict_log: Optional[ConflictLog] = None):
        self.path = path
        self.registry = registry
        self.review_log = review_log
        self.conflict_log = conflict_log
        self._by_id: Dict[str, Statement] = {}
        if os.path.exists(path):
            import json
            with open(path, encoding="utf-8") as f:
                for sid, raw in json.load(f).items():
                    self._by_id[sid] = Statement(**raw)

    def _next_id(self) -> str:
        n = 1 + max(
            (int(k[len(self.ID_PREFIX):]) for k in self._by_id), default=0
        )
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
    ) -> Statement:
        """Author one statement in DRAFT."""
        artifact = self.registry.get(artifact_id)  # raises if not held

        if not locator:
            raise EditorError(
                "A statement requires a locator: WHERE in the artifact the "
                "value was read."
            )
        if method not in ("DIRECT", "CALCULATED", "INFERRED"):
            raise EditorError(f"Unknown method {method!r}.")
        if method != "DIRECT" and not derivation_note:
            raise EditorError(
                f"A {method} statement must record its derivation_note: which "
                "printed facts were combined, and how."
            )
        if not read_by or not read_on:
            raise EditorError(
                "A statement requires the reader's name and the date read."
            )

        # Statement Authority Matrix: does this class have authority here?
        authority.check(statement_type, artifact.document_class)

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
            method=method,
            derivation_note=derivation_note,
            review_state=ReviewState.DRAFT.value,
            valid_from=valid_from,
            valid_until=valid_until,
            note=note,
        )
        self._by_id[statement.statement_id] = statement
        self._flush()

        # Conflict detection. Runs against statements a passenger could already
        # be seeing; a disagreement with a DRAFT is not yet a contradiction in
        # the published record.
        if self.conflict_log is not None:
            for existing in self._by_id.values():
                if existing.statement_id == statement.statement_id:
                    continue
                if existing.entity_id != entity_id or existing.question_id != question_id:
                    continue
                if existing.state not in ANSWERABLE:
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

    def transition(
        self,
        statement_id: str,
        to_state: ReviewState,
        actor: str,
        occurred_on: str,
        note: str = "",
    ) -> Statement:
        """Advance a statement. The ReviewLog validates the transition."""
        current = self._by_id[statement_id]

        if to_state is ReviewState.PUBLISHED:
            artifact = self.registry.get(current.artifact_id)
            ok, reason = authority.is_publishable(
                current.statement_type, artifact.document_class
            )
            if not ok:
                raise EditorError(
                    f"{statement_id} may not be published: {reason}"
                )
            if actor == current.read_by:
                raise EditorError(
                    f"{actor} read this statement and cannot also publish it. "
                    "Review is only meaningful with a second pair of eyes."
                )

        self.review_log.transition(
            statement_id, current.state, to_state, actor, occurred_on, note
        )
        updated = replace(current, review_state=to_state.value)
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
        """Resolve a conflict and move both statements to their end states.

        The winner is carried to PUBLISHED; the loser becomes SUPERSEDED, not
        REJECTED and never deleted. If neither reading survives, both are
        REJECTED and the question returns to UNKNOWN — which is the correct
        outcome when two sources disagree and neither can be trusted.
        """
        if self.conflict_log is None:
            raise EditorError("No conflict log is attached to this editor.")
        conflict = self.conflict_log.get(conflict_id)

        if winning_statement_id is None:
            for sid in conflict.statement_ids():
                self._force_state(sid, ReviewState.REJECTED, actor, occurred_on,
                                  f"both readings rejected ({conflict_id})")
        else:
            loser = next(s for s in conflict.statement_ids() if s != winning_statement_id)
            winner = self.get(winning_statement_id)
            if winner.state is ReviewState.DRAFT:
                self.transition(winning_statement_id, ReviewState.UNDER_REVIEW,
                                actor, occurred_on, f"conflict {conflict_id}")
            if self.get(winning_statement_id).state is ReviewState.UNDER_REVIEW:
                self.transition(winning_statement_id, ReviewState.APPROVED,
                                actor, occurred_on, f"conflict {conflict_id}")
            if self.get(winning_statement_id).state is ReviewState.APPROVED:
                self.transition(winning_statement_id, ReviewState.PUBLISHED,
                                actor, occurred_on, f"resolves {conflict_id}")
            # The loser always reaches a terminal state, whatever it was in.
            # Leaving a losing DRAFT alive lets it be published later and
            # recreate the same conflict.
            if self.get(loser).state not in (ReviewState.SUPERSEDED,
                                             ReviewState.REJECTED):
                self._force_state(loser, ReviewState.SUPERSEDED, actor, occurred_on,
                                  f"superseded by {winning_statement_id} ({conflict_id})")
        return self.conflict_log.resolve(
            conflict_id, winning_statement_id, actor, occurred_on, note)

    def _force_state(self, statement_id: str, to_state: ReviewState,
                     actor: str, occurred_on: str, note: str) -> None:
        current = self._by_id[statement_id]
        self.review_log.transition(statement_id, current.state, to_state,
                                   actor, occurred_on, note)
        self._by_id[statement_id] = replace(current, review_state=to_state.value)
        self._flush()
