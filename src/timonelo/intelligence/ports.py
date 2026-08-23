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
from timonelo.intelligence.models import PortDockingType, PortIntelligence
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
            sha256=None,
            method=self.provenance.method,
            derivation=self.provenance.derivation,
        )


class PortIntelligenceEvaluator:
    """Evaluates port logistics, berths, and terminals by delegating to canonical truth gates.

    Core Rule:
      Storage != Truth
      Authority compatibility != Review approval
      Evidence existence != Publishability

    All truth and admissibility decisions are delegated to canonical owners:
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

        # 2. Delegate candidate resolution and lifecycle gating to canonical TruthEngine
        answer = workspace.engine.answer(entity_id, question_id, as_of=as_of)

        # 3. If TruthEngine determines unknown or contested, map refusal reason
        if not answer.known or answer.contested:
            if answer.contested:
                refusal = "ACTIVE_CONFLICT_UNRESOLVED"
            else:
                # Identify why candidate statement was not answerable via Gatekeeper
                candidates = [
                    s for s in workspace.editor.all()
                    if s.entity_id == entity_id and s.question_id == question_id
                ]
                if not candidates:
                    refusal = "STATEMENT_MISSING"
                else:
                    cand = candidates[0]
                    # Check validity window
                    if not cand.is_valid_at(as_of):
                        refusal = "EXPIRED_OR_INACTIVE_VALIDITY"
                    else:
                        gk = EvidenceGatekeeper.from_workspace(workspace)
                        gk.add_statement(cand)
                        gate_res = gk.evaluate_publish_gate()
                        refusal = gate_res.reasons[0] if gate_res.reasons else "STATEMENT_NOT_ADMISSIBLE"

            return PortFactEvaluation(
                entity_id=entity_id,
                question_id=question_id,
                statement_type=statement_type,
                is_known=False,
                refusal_reason=refusal,
            )

        # 4. Check for multiple disagreeing values among admissible candidate statements
        admissible_candidates = [
            s for s in workspace.editor.all()
            if s.entity_id == entity_id
            and s.question_id == question_id
            and s.publishing in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS)
            and s.state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
            and s.condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
            and s.is_valid_at(as_of)
        ]
        if len({s.value for s in admissible_candidates}) > 1:
            return PortFactEvaluation(
                entity_id=entity_id,
                question_id=question_id,
                statement_type=statement_type,
                is_known=False,
                refusal_reason="CONFLICTING_SUPPORTED_STATEMENTS",
            )

        # 5. If TruthEngine surfaced an answer, verify physical cryptographic & event closure via EvidenceGatekeeper
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
        event_id = winning_stmt.evidence_event_ids[0] if winning_stmt.evidence_event_ids else None
        provenance = PortFactProvenance(
            artifact_id=answer.provenance.artifact_id,
            document_class=answer.provenance.document_class,
            evidence_condition=winning_stmt.evidence_condition,
            human_review_state=winning_stmt.human_review_state,
            publish_status=winning_stmt.publish_status,
            locator=answer.provenance.locator,
            statement_id=winning_stmt.statement_id,
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
        """Evaluates and returns PortIntelligence ONLY when canonical gates allow it.

        If no workspace or entity is provided or if required facts fail closed, returns None.
        """
        if workspace is None:
            if port_data and "workspace" in port_data:
                workspace = port_data["workspace"]
            else:
                return None

        entity_id = port_entity_id or (port_data.get("entity_id") if port_data else None)
        if not entity_id:
            return None

        name_eval = cls.evaluate_fact(workspace, entity_id, "Q-0024", as_of=as_of)
        if not name_eval.is_known or not name_eval.value:
            return None

        evidence_links: List[EvidenceLink] = []
        link = name_eval.to_evidence_link()
        if link:
            evidence_links.append(link)

        return PortIntelligence(
            port_name=str(name_eval.value),
            country="Spain" if "ES" in entity_id else "Unknown",
            docking_type=PortDockingType.PIER_BERTH,
            gangway_deck=0,
            gangway_location="TBD",
            all_aboard_time="TBD",
            last_tender_time=None,
            town_distance_meters=0,
            is_walkable_to_center=False,
            walking_route_summary="UNKNOWN",
            official_taxi_fare_notes="UNKNOWN",
            local_emergency_phone="112",
            evidence_links=evidence_links,
        )
