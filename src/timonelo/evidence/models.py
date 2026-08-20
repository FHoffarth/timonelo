"""Canonical evidence-domain models shared by authoring and evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)


@dataclass(frozen=True)
class Statement:
    """A provenance-bearing claim and its complete derivation closure.

    Confidence is deliberately absent: it is computed from evidence during
    traversal and is never persisted on a statement.
    """

    statement_id: str
    entity_id: str
    question_id: str
    value: Any
    statement_type: str = ""
    artifact_id: str = ""
    page: Optional[int] = None
    locator: str = ""
    read_by: str = ""
    read_on: str = ""
    method: Method = Method.DIRECT
    derivation: Derivation = Derivation.LOCAL
    derivation_note: str = ""
    evidence_event_ids: Tuple[str, ...] = ()
    input_statement_ids: Tuple[str, ...] = ()
    rule_hash: Optional[str] = None
    evidence_condition: EvidenceCondition = EvidenceCondition.UNKNOWN
    human_review_state: HumanReviewState = HumanReviewState.DRAFT
    publish_status: PublishStatus = PublishStatus.PUBLISH_BLOCKED
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    note: str = ""

    def __post_init__(self) -> None:
        """Normalize persisted legacy values to the canonical enum/tuple types."""
        object.__setattr__(self, "method", Method(self.method))
        object.__setattr__(self, "derivation", Derivation(self.derivation))
        object.__setattr__(
            self, "evidence_condition", EvidenceCondition(self.evidence_condition)
        )
        object.__setattr__(
            self, "human_review_state", HumanReviewState(self.human_review_state)
        )
        object.__setattr__(self, "publish_status", PublishStatus(self.publish_status))
        object.__setattr__(self, "evidence_event_ids", tuple(self.evidence_event_ids))
        object.__setattr__(self, "input_statement_ids", tuple(self.input_statement_ids))

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete canonical, JSON-serializable representation."""
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
            "method": self.method.value,
            "derivation": self.derivation.value,
            "derivation_note": self.derivation_note,
            "evidence_event_ids": list(self.evidence_event_ids),
            "input_statement_ids": list(self.input_statement_ids),
            "rule_hash": self.rule_hash,
            "evidence_condition": self.evidence_condition.value,
            "human_review_state": self.human_review_state.value,
            "publish_status": self.publish_status.value,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "note": self.note,
        }

    def is_valid_at(self, as_of: Optional[str]) -> bool:
        """Return whether the statement exists within its validity window."""
        if as_of is None:
            return True
        if self.valid_from and as_of < self.valid_from:
            return False
        if self.valid_until and as_of > self.valid_until:
            return False
        return True

    @property
    def state(self) -> HumanReviewState:
        return self.human_review_state

    @property
    def review_state(self) -> str:
        return self.human_review_state.value

    @property
    def condition(self) -> EvidenceCondition:
        return self.evidence_condition

    @property
    def publishing(self) -> PublishStatus:
        return self.publish_status
