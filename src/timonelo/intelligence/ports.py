"""
Plane 6: Port Intelligence Evaluator (Stateless).
Resolves port logistics, gangway decks, tender operations, and shoreside walking routes
strictly through canonical TruthEngine and EvidenceGatekeeper delegation.

Governed by ADR-0002 §1, §4, §6, §7, §8, §9, §13.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from timonelo.evidence.gatekeeper import EvidenceGatekeeper
from timonelo.evidence.workspace import Workspace
from timonelo.intelligence.models import PortIntelligence
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    EvidenceLink,
    HumanReviewState,
    Method,
    PublishStatus,
)


@dataclass(frozen=True)
class PortFactProvenance:
    """Provenance details for an admissible port fact."""
    artifact_id: str
    document_class: str
    evidence_condition: EvidenceCondition
    human_review_state: HumanReviewState
    publish_status: PublishStatus
    locator: str
    statement_id: str
    artifact_sha256: Optional[str] = None
    evidence_event_id: Optional[str] = None
    publisher: Optional[str] = None
    version: Optional[str] = None
    method: Optional[Method] = None
    derivation: Optional[Derivation] = None


@dataclass(frozen=True)
class PortFactEvaluation:
    """Result of evaluating a specific port fact question against canonical truth gates."""
    entity_id: str
    question_id: str
    statement_type: str
    is_known: bool
    value: Any = None
    provenance: Optional[PortFactProvenance] = None
    refusal_reason: Optional[str] = None

    def to_evidence_link(self) -> Optional[EvidenceLink]:
        """Convert admissible fact provenance to an EvidenceLink."""
        if not self.is_known or not self.provenance:
            return None
        return EvidenceLink(
            source_id=self.provenance.artifact_id,
            locator=self.provenance.locator,
            sha256=self.provenance.artifact_sha256,
            method=self.provenance.method,
            derivation=self.provenance.derivation,
        )


class PortIntelligenceEvaluator:
    """Evaluates port logistics, berths, and terminals by delegating to canonical truth gates.

    Core Rule:
      Storage != Truth
      Authority compatibility != Review approval
      Evidence existence != Publishability

    All truth and admissibility decisions are delegated strictly to canonical owners:
      - Question validation ➔ QuestionRegistry
      - Candidate filtering, review/evidence condition/publish gates, validity ➔ TruthEngine.answer()
      - Physical artifact hash integrity, event closure & authority class ➔ EvidenceGatekeeper
      - Open conflict detection ➔ ConflictLog
    """

    @classmethod
    def evaluate_fact(
        cls,
        workspace: Workspace,
        entity_id: str,
        question_id: str,
        as_of: Optional[str] = None,
    ) -> PortFactEvaluation:
        """Evaluate a single factual question for a port entity by delegating to canonical truth gates."""
        # 1. Question existence check in canonical QuestionRegistry
        try:
            question = workspace.questions.get(question_id)
        except KeyError:
            return PortFactEvaluation(
                entity_id=entity_id,
                question_id=question_id,
                statement_type="unknown",
                is_known=False,
                refusal_reason="QUESTION_NOT_REGISTERED",
            )

        statement_type = question.statement_type or "unknown"

        # 2. Delegate candidate resolution, lifecycle gating, validity, and conflict check to TruthEngine
        answer = workspace.engine.answer(entity_id, question_id, as_of=as_of)

        # 3. If TruthEngine determines unknown or contested, fail closed with canonical refusal
        if not answer.known or answer.contested:
            refusal = "ACTIVE_CONFLICT_UNRESOLVED" if answer.contested else "TRUTH_NOT_ADMISSIBLE"
            return PortFactEvaluation(
                entity_id=entity_id,
                question_id=question_id,
                statement_type=statement_type,
                is_known=False,
                refusal_reason=refusal,
            )

        # 4. If TruthEngine surfaced an answer, verify physical cryptographic & event closure via EvidenceGatekeeper
        winning_stmt = workspace.editor.get(answer.provenance.statement_id)
        gk = EvidenceGatekeeper.from_workspace(workspace)
        gk.add_statement(winning_stmt)
        gate_res = gk.evaluate_publish_gate()

        if gate_res.status == PublishStatus.PUBLISH_BLOCKED:
            return PortFactEvaluation(
                entity_id=entity_id,
                question_id=question_id,
                statement_type=statement_type,
                is_known=False,
                refusal_reason=gate_res.reasons[0] if gate_res.reasons else "PUBLISH_BLOCKED",
            )

        # 5. Build PortFactProvenance from canonical Answer provenance and winning Statement
        artifact = workspace.registry.get(answer.provenance.artifact_id) if answer.provenance.artifact_id else None
        event_id = winning_stmt.evidence_event_ids[0] if winning_stmt.evidence_event_ids else None
        provenance = PortFactProvenance(
            artifact_id=answer.provenance.artifact_id,
            document_class=answer.provenance.document_class,
            evidence_condition=winning_stmt.evidence_condition,
            human_review_state=winning_stmt.human_review_state,
            publish_status=winning_stmt.publish_status,
            locator=answer.provenance.locator,
            statement_id=winning_stmt.statement_id,
            artifact_sha256=artifact.sha256 if artifact else None,
            evidence_event_id=event_id,
            publisher=answer.provenance.publisher,
            version=answer.provenance.version,
            method=winning_stmt.method,
            derivation=winning_stmt.derivation,
        )

        return PortFactEvaluation(
            entity_id=entity_id,
            question_id=question_id,
            statement_type=statement_type,
            is_known=True,
            value=answer.value,
            provenance=provenance,
            refusal_reason=None,
        )

    @classmethod
    def evaluate(
        cls,
        port_data: Optional[Dict[str, Any]] = None,
        workspace: Optional[Workspace] = None,
        port_entity_id: Optional[str] = None,
        as_of: Optional[str] = None,
    ) -> Optional[PortIntelligence]:
        """Briefing-level evaluator for shoreside logistics, gangway decks, and tender operations.

        Governed by ADR-0002 §1, §8, §9.
        Returns PortIntelligence ONLY when every required field is truth-backed by sourced records.
        Until all required briefing fields are backed by canonical evidence, returns None (UNKNOWN)
        to prevent fabricating passenger-facing defaults.
        """
        # Sourced port intelligence briefing fields are not yet complete in Slice 2/3.
        # Fail closed and return None (UNKNOWN).
        return None
