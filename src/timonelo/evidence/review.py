"""
Review workflow.

Governed by ADR-0002 §5, ADR-0003 §7.

    DRAFT -> UNDER_REVIEW -> APPROVED -> PUBLISHED
                          \\-> REJECTED

Every transition is recorded with actor and date in an append-only history, so
"who approved this and when" is answerable for any statement a passenger saw.

Nothing bypasses the workflow: a statement is created in DRAFT and can only
advance one step at a time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from timonelo.canonical import canonical_dump


class ReviewState(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    # Was a correct reading of its source, and has been replaced by a better
    # one through conflict resolution. Distinct from REJECTED, which means the
    # reading was wrong. Collapsing the two would destroy the record of why a
    # published value changed.
    SUPERSEDED = "SUPERSEDED"


# Exactly which transitions exist. Anything absent is forbidden.
ALLOWED: Dict[ReviewState, frozenset] = {
    ReviewState.DRAFT:        frozenset({ReviewState.UNDER_REVIEW,
                                         ReviewState.REJECTED,
                                         ReviewState.SUPERSEDED}),
    ReviewState.UNDER_REVIEW: frozenset({ReviewState.APPROVED, ReviewState.REJECTED,
                                         ReviewState.SUPERSEDED}),
    ReviewState.APPROVED:     frozenset({ReviewState.PUBLISHED, ReviewState.REJECTED,
                                         ReviewState.SUPERSEDED}),
    ReviewState.PUBLISHED:    frozenset({ReviewState.REJECTED, ReviewState.SUPERSEDED}),
    ReviewState.REJECTED:     frozenset(),
    ReviewState.SUPERSEDED:   frozenset(),
}

# States whose statements may reach a passenger.
ANSWERABLE = frozenset({ReviewState.APPROVED, ReviewState.PUBLISHED})


class ReviewError(ValueError):
    pass


@dataclass(frozen=True)
class ReviewEntry:
    statement_id: str
    from_state: str
    to_state: str
    actor: str
    occurred_on: str
    note: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "statement_id": self.statement_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "actor": self.actor,
            "occurred_on": self.occurred_on,
            "note": self.note,
        }


class ReviewLog:
    """Append-only record of every state transition."""

    def __init__(self, path: str):
        self.path = path
        self._entries: List[ReviewEntry] = []
        if os.path.exists(path):
            import json
            with open(path, encoding="utf-8") as f:
                self._entries = [ReviewEntry(**e) for e in json.load(f)]

    def transition(
        self,
        statement_id: str,
        from_state: ReviewState,
        to_state: ReviewState,
        actor: str,
        occurred_on: str,
        note: str = "",
    ) -> ReviewEntry:
        if to_state not in ALLOWED[from_state]:
            raise ReviewError(
                f"{from_state.value} -> {to_state.value} is not an allowed "
                f"transition. From {from_state.value}, allowed: "
                f"{sorted(s.value for s in ALLOWED[from_state]) or 'none'}."
            )
        if not actor:
            raise ReviewError("A review transition requires a named actor.")
        entry = ReviewEntry(
            statement_id=statement_id,
            from_state=from_state.value,
            to_state=to_state.value,
            actor=actor,
            occurred_on=occurred_on,
            note=note,
        )
        self._entries.append(entry)
        self._flush()
        return entry

    def history(self, statement_id: str) -> List[ReviewEntry]:
        return [e for e in self._entries if e.statement_id == statement_id]

    def all(self) -> List[ReviewEntry]:
        return list(self._entries)

    def _flush(self) -> None:
        canonical_dump([e.to_dict() for e in self._entries], self.path)
