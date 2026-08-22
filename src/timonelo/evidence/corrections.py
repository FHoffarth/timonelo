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


class PriorRepresentation(str, Enum):
    """What the corrected value REPLACED. Declared, never inferred.

    A null `prior_statement_id` is ambiguous on its own: it may mean the prior
    reading was a legacy artefact that was never a Statement, or it may mean the
    caller simply failed to supply it. Those are different claims, so the caller
    must say which one it is.
    """

    STATEMENT = "STATEMENT"                          # prior_statement_id required
    LEGACY_NON_STATEMENT = "LEGACY_NON_STATEMENT"    # prior_statement_id must be None


class ReferenceIntegrity(str, Enum):
    """Whether this record's ID references were checked against known IDs.

    LOCAL integrity metadata about the correction record itself. It is NOT a
    canonical truth or lifecycle axis: it says nothing about evidence condition,
    review state, or publication eligibility, and the TruthEngine never reads it.

    It replaces a boolean that could reach its strongest value in its weakest
    case: with no statement references at all, `not any(statement_ids)` was
    trivially true, so a record referencing nothing reported "validated".
    """

    VALIDATED = "VALIDATED"                      # references present and all checked
    UNVALIDATED = "UNVALIDATED"                  # no known-ID sets supplied; unchecked
    NOTHING_TO_VALIDATE = "NOTHING_TO_VALIDATE"  # checking requested, no references


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
    prior_representation: PriorRepresentation = PriorRepresentation.STATEMENT
    reference_integrity: ReferenceIntegrity = ReferenceIntegrity.UNVALIDATED

    def __post_init__(self) -> None:
        object.__setattr__(self, "correction_kind", CorrectionKind(self.correction_kind))
        object.__setattr__(self, "evidence_event_ids", tuple(self.evidence_event_ids))
        object.__setattr__(
            self, "prior_representation", PriorRepresentation(self.prior_representation)
        )
        object.__setattr__(
            self, "reference_integrity", ReferenceIntegrity(self.reference_integrity)
        )

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
            "prior_representation": self.prior_representation.value,
            "reference_integrity": self.reference_integrity.value,
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
                correction_id: self._record_from_dict(correction_id, record)
                for correction_id, record in raw.get("corrections", {}).items()
            }

    @staticmethod
    def _record_from_dict(correction_id: str, record: Dict[str, Any]) -> "HistoricalCorrectionRecord":
        """Load one persisted record, refusing the superseded boolean shape.

        Pre-tri-state files carry `references_validated: bool`. That value is not
        translatable: `true` could mean "every reference resolved" or "there were
        no references to check", and those map to different states now. Guessing
        would reintroduce exactly the ambiguity the tri-state removes, so this
        fails closed and asks for a regeneration instead.
        """
        if "references_validated" in record:
            raise ValueError(
                f"{correction_id} uses the superseded 'references_validated' boolean. "
                "It cannot be migrated automatically: 'true' was reachable both when "
                "all references resolved and when there were none to check. "
                "Regenerate the correction log."
            )
        return HistoricalCorrectionRecord(**record)

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
        prior_representation: PriorRepresentation,
        prior_statement_id: Optional[str] = None,
        replacement_statement_id: Optional[str] = None,
        note: str = "",
        recorded_by: Optional[str] = None,
        known_statement_ids: Optional[Collection[str]] = None,
        known_evidence_event_ids: Optional[Collection[str]] = None,
    ) -> HistoricalCorrectionRecord:
        if not basis:
            raise ValueError("A historical correction requires an auditable basis.")

        prior_representation = PriorRepresentation(prior_representation)
        correction_kind = CorrectionKind(correction_kind)

        # A corrected value must exist as answerable knowledge. Recording that a
        # value changed while proving no Statement carries the new one asserts a
        # correction nothing can answer.
        if correction_kind is CorrectionKind.VALUE_CORRECTED and not replacement_statement_id:
            raise ValueError(
                "CorrectionKind.VALUE_CORRECTED requires replacement_statement_id: "
                "the corrected value must exist as a Statement."
            )
        # The null prior must be a declaration, never an omission.
        if prior_representation is PriorRepresentation.STATEMENT and not prior_statement_id:
            raise ValueError(
                "prior_representation=STATEMENT requires prior_statement_id. "
                "If the prior reading was never a Statement, declare "
                "prior_representation=LEGACY_NON_STATEMENT."
            )
        if prior_representation is PriorRepresentation.LEGACY_NON_STATEMENT and prior_statement_id:
            raise ValueError(
                "prior_representation=LEGACY_NON_STATEMENT forbids prior_statement_id: "
                "a legacy representation is by definition not a Statement."
            )

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
        # Tri-state, so "nothing was checked" can never masquerade as "checked".
        # Dangling IDs already raised above, so reaching here with references
        # present and both known-ID sets supplied means every reference resolved.
        present_statement_ids = [sid for sid in statement_ids if sid is not None]
        checked_statements = known_statement_ids is not None
        checked_events = known_evidence_event_ids is not None
        if not checked_statements and not checked_events:
            reference_integrity = ReferenceIntegrity.UNVALIDATED
        elif (present_statement_ids and not checked_statements) or (
            evidence_event_ids and not checked_events
        ):
            reference_integrity = ReferenceIntegrity.UNVALIDATED
        elif not present_statement_ids and not evidence_event_ids:
            reference_integrity = ReferenceIntegrity.NOTHING_TO_VALIDATE
        else:
            reference_integrity = ReferenceIntegrity.VALIDATED
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
            prior_representation=prior_representation,
            reference_integrity=reference_integrity,
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
