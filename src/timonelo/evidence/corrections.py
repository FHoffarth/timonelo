"""Append-only audit history for corrected historical representations."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Collection, Dict, List, Optional, Tuple

from timonelo.canonical import canonical_dump


class CorrectionKind(str, Enum):
    """Why the recorded representation changed; never a trust or lifecycle axis."""

    VALUE_CORRECTED = "VALUE_CORRECTED"


@dataclass(frozen=True)
class HistoricalCorrectionRecord:
    correction_id: str
    entity_id: str
    question_id: str
    correction_kind: CorrectionKind
    basis: str
    evidence_event_ids: Tuple[str, ...]
    recorded_at: str
    prior_statement_id: Optional[str] = None
    replacement_statement_id: Optional[str] = None
    note: str = ""
    recorded_by: Optional[str] = None
    references_validated: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "correction_kind", CorrectionKind(self.correction_kind))
        object.__setattr__(self, "evidence_event_ids", tuple(self.evidence_event_ids))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correction_id": self.correction_id,
            "entity_id": self.entity_id,
            "question_id": self.question_id,
            "prior_statement_id": self.prior_statement_id,
            "replacement_statement_id": self.replacement_statement_id,
            "correction_kind": self.correction_kind.value,
            "basis": self.basis,
            "evidence_event_ids": list(self.evidence_event_ids),
            "note": self.note,
            "recorded_at": self.recorded_at,
            "recorded_by": self.recorded_by,
            "references_validated": self.references_validated,
        }


class HistoricalCorrectionLog:
    """Persistent correction history, independent from live conflict state."""

    ID_PREFIX = "COR-"

    def __init__(self, path: str):
        self.path = path
        self._by_id: Dict[str, HistoricalCorrectionRecord] = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            self._by_id = {
                correction_id: HistoricalCorrectionRecord(**record)
                for correction_id, record in raw.get("corrections", {}).items()
            }

    def _next_id(self) -> str:
        number = 1 + max(
            (int(key[len(self.ID_PREFIX):]) for key in self._by_id), default=0
        )
        return f"{self.ID_PREFIX}{number:04d}"

    def record(
        self,
        entity_id: str,
        question_id: str,
        correction_kind: CorrectionKind,
        basis: str,
        evidence_event_ids: Tuple[str, ...],
        recorded_at: str,
        prior_statement_id: Optional[str] = None,
        replacement_statement_id: Optional[str] = None,
        note: str = "",
        recorded_by: Optional[str] = None,
        known_statement_ids: Optional[Collection[str]] = None,
        known_evidence_event_ids: Optional[Collection[str]] = None,
    ) -> HistoricalCorrectionRecord:
        if not basis:
            raise ValueError("A historical correction requires an auditable basis.")
        statement_ids = (prior_statement_id, replacement_statement_id)
        if known_statement_ids is not None:
            dangling_statements = [
                statement_id
                for statement_id in statement_ids
                if statement_id is not None and statement_id not in known_statement_ids
            ]
            if dangling_statements:
                raise ValueError(
                    f"Historical correction references unknown Statement IDs: "
                    f"{dangling_statements}"
                )
        if known_evidence_event_ids is not None:
            dangling_events = [
                event_id
                for event_id in evidence_event_ids
                if event_id not in known_evidence_event_ids
            ]
            if dangling_events:
                raise ValueError(
                    f"Historical correction references unknown EvidenceEvent IDs: "
                    f"{dangling_events}"
                )
        validation_requested = (
            known_statement_ids is not None or known_evidence_event_ids is not None
        )
        statement_references_validated = (
            not any(statement_ids) or known_statement_ids is not None
        )
        evidence_references_validated = (
            not evidence_event_ids or known_evidence_event_ids is not None
        )
        references_validated = (
            validation_requested
            and statement_references_validated
            and evidence_references_validated
        )
        record = HistoricalCorrectionRecord(
            correction_id=self._next_id(),
            entity_id=entity_id,
            question_id=question_id,
            prior_statement_id=prior_statement_id,
            replacement_statement_id=replacement_statement_id,
            correction_kind=correction_kind,
            basis=basis,
            evidence_event_ids=evidence_event_ids,
            note=note,
            recorded_at=recorded_at,
            recorded_by=recorded_by,
            references_validated=references_validated,
        )
        self._by_id[record.correction_id] = record
        self._flush()
        return record

    def all(self) -> List[HistoricalCorrectionRecord]:
        return [self._by_id[key] for key in sorted(self._by_id)]

    def get(self, correction_id: str) -> HistoricalCorrectionRecord:
        return self._by_id[correction_id]

    def __len__(self) -> int:
        return len(self._by_id)

    def _flush(self) -> None:
        canonical_dump(
            {"corrections": {key: value.to_dict() for key, value in self._by_id.items()}},
            self.path,
        )
