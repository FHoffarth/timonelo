"""
Truth Conflict Engine.

Governed by ADR-0002 §1, §5, §9.

When a new statement contradicts one that is already answerable, the store does
not overwrite, does not discard, and does not pick a winner. It records the
disagreement and hands it to a human.

    detect -> record -> mark both -> require review -> publish resolution

Three rules follow from ADR-0002 and are enforced here rather than by habit:

1. NOTHING DISAPPEARS. A losing statement becomes SUPERSEDED, never deleted and
   never REJECTED. Those are different claims: REJECTED means the reading was
   wrong; SUPERSEDED means it was right for its source and has been replaced by
   a better one. Collapsing them destroys the record of why the value changed.

2. DETECTION IS DELIBERATELY BLUNT. Any difference in value for the same entity
   and question is a conflict. Normalising values before comparing ("14" vs 14,
   "none" vs "none marked") would silently suppress real disagreements to save a
   curator some clicks. Over-detection costs a review; under-detection ships a
   contradiction to a passenger.

3. AGREEMENT IS NOT A CONFLICT, AND NOT CORROBORATION EITHER. Two sources
   stating the same value produce no conflict, and under min-propagation the
   agreement does not raise confidence (ADR-0002 §7.1). It is recorded as a
   concurrence so a curator can see the value was independently observed.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from timonelo.canonical import canonical_dump


class ConflictStatus(str, Enum):
    OPEN = "OPEN"                    # detected, awaiting a human
    RESOLVED = "RESOLVED"            # a winner was chosen and published
    BOTH_REJECTED = "BOTH_REJECTED"  # neither reading survived review


class ConflictError(ValueError):
    pass


@dataclass(frozen=True)
class Conflict:
    """A recorded disagreement between two statements about the same question."""
    conflict_id: str
    entity_id: str
    question_id: str
    statement_type: str
    incumbent_statement_id: str
    incumbent_value: Any
    challenger_statement_id: str
    challenger_value: Any
    detected_on: str
    status: str = ConflictStatus.OPEN.value
    resolved_statement_id: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_on: Optional[str] = None
    resolution_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)

    @property
    def is_open(self) -> bool:
        return self.status == ConflictStatus.OPEN.value

    def statement_ids(self) -> Sequence[str]:
        return (self.incumbent_statement_id, self.challenger_statement_id)


@dataclass(frozen=True)
class Concurrence:
    """Two statements agreeing. Recorded, but never treated as corroboration."""
    entity_id: str
    question_id: str
    value: Any
    statement_ids: Sequence[str]


class ConflictLog:
    """Append-only conflict record. Resolutions are appended, never overwritten
    in place — the resolution is a new revision of the entry, and the full
    history stays in the file."""

    ID_PREFIX = "CFL-"

    def __init__(self, path: str):
        self.path = path
        self._by_id: Dict[str, Conflict] = {}
        self._history: List[Dict[str, Any]] = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            self._history = raw.get("history", [])
            for cid, d in raw.get("conflicts", {}).items():
                self._by_id[cid] = Conflict(**d)

    def _next_id(self) -> str:
        n = 1 + max((int(k[len(self.ID_PREFIX):]) for k in self._by_id), default=0)
        return f"{self.ID_PREFIX}{n:04d}"

    def record(
        self,
        entity_id: str,
        question_id: str,
        statement_type: str,
        incumbent_statement_id: str,
        incumbent_value: Any,
        challenger_statement_id: str,
        challenger_value: Any,
        detected_on: str,
    ) -> Conflict:
        conflict = Conflict(
            conflict_id=self._next_id(),
            entity_id=entity_id,
            question_id=question_id,
            statement_type=statement_type,
            incumbent_statement_id=incumbent_statement_id,
            incumbent_value=incumbent_value,
            challenger_statement_id=challenger_statement_id,
            challenger_value=challenger_value,
            detected_on=detected_on,
        )
        self._by_id[conflict.conflict_id] = conflict
        self._history.append({
            "conflict_id": conflict.conflict_id,
            "event": "DETECTED",
            "on": detected_on,
            "incumbent": incumbent_statement_id,
            "challenger": challenger_statement_id,
        })
        self._flush()
        return conflict

    def resolve(
        self,
        conflict_id: str,
        winning_statement_id: Optional[str],
        actor: str,
        occurred_on: str,
        note: str,
    ) -> Conflict:
        c = self.get(conflict_id)
        if not c.is_open:
            raise ConflictError(
                f"{conflict_id} is already {c.status}. Reopening is not "
                "supported: record a new statement instead, which will be "
                "detected as a fresh conflict."
            )
        if not note:
            raise ConflictError(
                "A resolution must record WHY one reading was preferred. "
                "A winner without a reason is indistinguishable from a guess."
            )
        if winning_statement_id is not None and winning_statement_id not in c.statement_ids():
            raise ConflictError(
                f"{winning_statement_id} is not party to {conflict_id}."
            )
        status = (ConflictStatus.RESOLVED if winning_statement_id
                  else ConflictStatus.BOTH_REJECTED)
        updated = replace(
            c,
            status=status.value,
            resolved_statement_id=winning_statement_id,
            resolved_by=actor,
            resolved_on=occurred_on,
            resolution_note=note,
        )
        self._by_id[conflict_id] = updated
        self._history.append({
            "conflict_id": conflict_id,
            "event": status.value,
            "on": occurred_on,
            "actor": actor,
            "winner": winning_statement_id,
            "note": note,
        })
        self._flush()
        return updated

    def get(self, conflict_id: str) -> Conflict:
        if conflict_id not in self._by_id:
            raise ConflictError(f"No conflict {conflict_id!r}.")
        return self._by_id[conflict_id]

    def all(self) -> List[Conflict]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def open_conflicts(self) -> List[Conflict]:
        return [c for c in self.all() if c.is_open]

    def for_statement(self, statement_id: str) -> List[Conflict]:
        return [c for c in self.all() if statement_id in c.statement_ids()]

    def open_for_question(self, entity_id: str, question_id: str) -> List[Conflict]:
        return [
            c for c in self.all()
            if c.is_open and c.entity_id == entity_id and c.question_id == question_id
        ]

    def history(self, conflict_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if conflict_id is None:
            return list(self._history)
        return [h for h in self._history if h["conflict_id"] == conflict_id]

    def __len__(self) -> int:
        return len(self._by_id)

    def _flush(self) -> None:
        canonical_dump(
            {"conflicts": {k: v.to_dict() for k, v in self._by_id.items()},
             "history": self._history},
            self.path,
        )


def values_disagree(a: Any, b: Any) -> bool:
    """Blunt comparison. See rule 2 in the module docstring.

    Only exact equality counts as agreement. No trimming, no case folding, no
    numeric coercion: "14" and 14 are treated as a disagreement, because a
    curator should look at why two readings of the same cell were typed
    differently before the store decides they meant the same thing.
    """
    return a != b
