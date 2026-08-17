"""
Question Registry — the root of the read path.

Governed by ADR-0002 §8, §12.

UNKNOWN cannot be discovered by looking at answers. It is discovered by
comparing the set of registered questions against the statement graph. A gap
that no question anticipates is invisible: it does not render, the passenger
never learns it exists, and coverage cannot be measured.

Question identity is NEVER text (ADR-0002 §12). Question IDs leak into every
satisfaction record ever written; keying them by English strings would make the
eventual vocabulary layer a migration across the entire graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from typing import Dict, List, Optional, Tuple

from timonelo.canonical import canonical_dump


@dataclass(frozen=True)
class Question:
    """A question answerable about an entity type.

    `supportable_by` encodes the principle carried forward from the audit: a
    document may only support the claims it is actually capable of supporting.
    A public marketing deck plan can establish which side of the ship a cabin
    is on; it cannot establish the stateroom's area in square metres or a
    door's clear width in millimetres. Recording that per question stops the
    first evidence record from overreaching.
    """
    question_id: str          # opaque, stable, e.g. "Q-0007"
    entity_type: str          # "cabin", "deck", "venue", "vessel"
    statement_type: Optional[str] = None  # key into authority.AUTHORITY
    labels: Dict[str, str] = field(default_factory=dict)  # presentation only
    supportable_by: Tuple[str, ...] = ()   # derived from the matrix if unset
    unknown_guidance: Optional[str] = None  # what to tell the passenger instead

    def can_be_supported_by(self, document_class: str) -> bool:
        """Authority check. Delegates to the matrix when a statement_type is set.

        `supportable_by` remains as a per-question override for cases the
        matrix does not cover (fixtures, experiments). When statement_type is
        present the matrix governs, so authority is declared once centrally
        rather than copied into every question.
        """
        if self.statement_type is not None:
            from timonelo.evidence import authority
            return document_class in authority.authoritative_classes(self.statement_type)
        return document_class in self.supportable_by


class QuestionRegistry:
    """Versioned set of registered questions."""

    def __init__(self, version: str = "unversioned"):
        self.version = version
        self._by_id: Dict[str, Question] = {}

    def register(self, question: Question) -> None:
        if question.question_id in self._by_id:
            raise ValueError(f"Duplicate question id {question.question_id!r}")
        if not question.question_id.startswith("Q-"):
            raise ValueError(
                f"Question id {question.question_id!r} must be an opaque "
                "identifier of the form Q-NNNN, never English text."
            )
        self._by_id[question.question_id] = question

    def get(self, question_id: str) -> Question:
        return self._by_id[question_id]

    def for_entity_type(self, entity_type: str) -> List[Question]:
        return [
            self._by_id[k]
            for k in sorted(self._by_id)
            if self._by_id[k].entity_type == entity_type
        ]

    def all(self) -> List[Question]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)

    # -- persistence ----------------------------------------------------------

    def to_dict(self) -> Dict[str, object]:
        return {
            "version": self.version,
            "questions": {
                q.question_id: {
                    "question_id": q.question_id,
                    "entity_type": q.entity_type,
                    "statement_type": q.statement_type,
                    "labels": q.labels,
                    "supportable_by": list(q.supportable_by),
                    "unknown_guidance": q.unknown_guidance,
                }
                for q in self.all()
            },
        }

    def save(self, path: str) -> None:
        canonical_dump(self.to_dict(), path)

    @classmethod
    def load(cls, path: str) -> "QuestionRegistry":
        if not os.path.exists(path):
            return cls(version="empty")
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        registry = cls(version=raw.get("version", "unversioned"))
        for q in raw.get("questions", {}).values():
            registry.register(Question(
                question_id=q["question_id"],
                entity_type=q["entity_type"],
                statement_type=q.get("statement_type"),
                labels=q.get("labels", {}),
                supportable_by=tuple(q.get("supportable_by", ())),
                unknown_guidance=q.get("unknown_guidance"),
            ))
        return registry
