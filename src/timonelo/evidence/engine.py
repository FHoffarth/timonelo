"""
Truth Engine — statements, propagation, review, publication.

Governed by ADR-0002 §4, §6, §7, §8, §9.

The engine never asks "what do we know?" It asks, for a registered question:
which statements currently satisfy it? If none do, the answer is UNKNOWN by
construction — no special case, no literal.

Confidence is NEVER stored. It is computed on traversal, every time.
Human review state, evidence condition, and publication status are distinct axes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from timonelo.evidence.artifacts import ArtifactStore
from timonelo.evidence.events import EvidenceEventLog
from timonelo.evidence.questions import QuestionRegistry
from timonelo.ontology.models import (
    Method,
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)


# Source reliability for DIRECT statements (ADR-0002 §7).
# Capped at 0.97: deck plans are undated marketing artifacts revised at refit.
# 1.0 is reserved for tautologies and is deliberately unreachable here.
SOURCE_RELIABILITY: Dict[str, float] = {
    "shipyard_general_arrangement": 0.97,
    "classification_society_record": 0.95,
    "cruise_line_deck_plan": 0.80,
    "onboard_survey": 0.90,
    "cruise_line_marketing": 0.55,
}


@dataclass(frozen=True)
class Statement:
    """A claim, with the record of how it came into existence.

    Deliberately carries no confidence field (ADR-0002 I1). It carries the IDs
    of every input it consumed, so the derivation closure is inspectable and
    the blast-radius criterion (ADR-0003 §6) is verifiable.
    """
    statement_id: str
    entity_id: str
    question_id: str
    value: Any
    method: Method
    derivation: Derivation
    evidence_event_ids: Tuple[str, ...] = ()
    input_statement_ids: Tuple[str, ...] = ()
    rule_hash: Optional[str] = None
    evidence_condition: EvidenceCondition = EvidenceCondition.UNKNOWN
    human_review_state: HumanReviewState = HumanReviewState.DRAFT
    publish_status: PublishStatus = PublishStatus.PUBLISH_BLOCKED
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None

    def is_valid_at(self, as_of: Optional[str]) -> bool:
        """Outside its window a statement does not degrade — it ceases to be one."""
        if as_of is None:
            return True
        if self.valid_from and as_of < self.valid_from:
            return False
        if self.valid_until and as_of > self.valid_until:
            return False
        return True


@dataclass(frozen=True)
class DerivationNode:
    """One step in an explanation. Renderable, but never composed independently."""
    statement_id: str
    question_id: str
    value: Any
    method: str
    derivation: str
    confidence: float
    sources: Tuple[str, ...]
    inputs: Tuple["DerivationNode", ...] = ()


@dataclass(frozen=True)
class Answer:
    """Either a satisfied statement or UNKNOWN. There is no third outcome."""
    question_id: str
    entity_id: str
    known: bool
    value: Any = None
    confidence: Optional[float] = None
    derivation: Optional[DerivationNode] = None
    unknown_guidance: Optional[str] = None


class TruthEngine:
    """Answers registered questions from published statements."""

    def __init__(
        self,
        registry: QuestionRegistry,
        log: EvidenceEventLog,
        store: ArtifactStore,
        rules: Optional[Dict[str, float]] = None,
    ):
        self.registry = registry
        self.log = log
        self.store = store
        self.rules = rules or {}
        self._statements: Dict[str, Statement] = {}

    # -- statement management -------------------------------------------------

    def add_statement(self, statement: Statement) -> Statement:
        if statement.statement_id in self._statements:
            raise ValueError(f"Duplicate statement_id {statement.statement_id!r}")
        if statement.method is Method.DIRECT and not statement.evidence_event_ids:
            raise ValueError(
                f"Statement {statement.statement_id!r} claims DIRECT observation "
                "but cites no evidence event."
            )
        if statement.method is not Method.DIRECT and not (
            statement.input_statement_ids or statement.evidence_event_ids
        ):
            raise ValueError(
                f"Statement {statement.statement_id!r} is {statement.method.value} "
                "but consumes no inputs. A derived statement must cite its premises."
            )
        if statement.method is Method.INFERRED and statement.rule_hash is None:
            raise ValueError(
                f"Statement {statement.statement_id!r} is INFERRED but cites no "
                "rule hash. Rules are content-addressed (ADR-0003 §3)."
            )
        for sid in statement.input_statement_ids:
            if sid not in self._statements:
                raise ValueError(f"Unknown input statement {sid!r}")
        self._statements[statement.statement_id] = statement
        return statement

    def set_human_review_state(self, statement_id: str, state: HumanReviewState) -> Statement:
        """Transitions the human review workflow state."""
        s = self._statements[statement_id]
        updated = Statement(**{**s.__dict__, "human_review_state": state})
        self._statements[statement_id] = updated
        return updated

    def set_evidence_condition(self, statement_id: str, condition: EvidenceCondition) -> Statement:
        """Sets the evidence condition of a statement."""
        s = self._statements[statement_id]
        pub_status = s.publish_status
        if condition != EvidenceCondition.SUPPORTED and condition != EvidenceCondition.SUPPORTED.value:
            pub_status = PublishStatus.PUBLISH_BLOCKED
        updated = Statement(**{**s.__dict__, "evidence_condition": condition, "publish_status": pub_status})
        self._statements[statement_id] = updated
        return updated

    def set_publish_status(self, statement_id: str, status: PublishStatus) -> Statement:
        """Sets the publication gate status. Only APPROVED and SUPPORTED items may become PUBLISH_ALLOWED."""
        s = self._statements[statement_id]
        if status in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS, PublishStatus.PUBLISH_ALLOWED.value, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value):
            if s.human_review_state != HumanReviewState.APPROVED and s.human_review_state != HumanReviewState.APPROVED.value:
                raise ValueError(
                    f"Statement {statement_id!r} cannot be publish-allowed while in "
                    f"human review state {s.human_review_state}. It must be APPROVED first."
                )
            if s.evidence_condition != EvidenceCondition.SUPPORTED and s.evidence_condition != EvidenceCondition.SUPPORTED.value:
                raise ValueError(
                    f"Statement {statement_id!r} cannot be publish-allowed with evidence condition "
                    f"{s.evidence_condition}. It must be SUPPORTED first."
                )
            blocked = self._publication_block(s)
            if blocked:
                raise ValueError(
                    f"Statement {statement_id!r} may not be published: {blocked}"
                )
        updated = Statement(**{**s.__dict__, "publish_status": status})
        self._statements[statement_id] = updated
        return updated

    def publish(self, statement_id: str) -> Statement:
        """Convenience method to advance an approved statement to PUBLISH_ALLOWED."""
        return self.set_publish_status(statement_id, PublishStatus.PUBLISH_ALLOWED)

    def _publication_block(self, s: Statement) -> Optional[str]:
        """Authority governs whether a statement may EXIST; permission governs
        whether it may be SEEN. A statement can be perfectly evidenced and
        still not publishable."""
        from timonelo.evidence import authority
        question = self.registry.get(s.question_id)
        if question.statement_type is None:
            return None
        for eid in s.evidence_event_ids:
            event = next((e for e in self.log.all() if e.event_id == eid), None)
            if event is None:
                continue
            class_id = self.store.get(event.artifact_sha256).document_class
            ok, reason = authority.is_publishable(question.statement_type, class_id)
            if not ok:
                return reason
        return None

    # -- confidence propagation (ADR-0002 §7) ---------------------------------

    def confidence(self, statement_id: str) -> float:
        """Computed on traversal. Never read from storage."""
        s = self._statements[statement_id]

        if s.method is Method.DIRECT:
            classes = set()
            for eid in s.evidence_event_ids:
                event = next(e for e in self.log.all() if e.event_id == eid)
                classes.add(self.store.get(event.artifact_sha256).document_class)
            if not classes:
                return 0.0
            from timonelo.evidence import authority
            unknown = sorted(
                c for c in classes
                if c not in SOURCE_RELIABILITY and c not in authority.DOCUMENT_CLASSES
            )
            if unknown:
                # Silently returning 0.0 would make an unregistered document
                # class indistinguishable from an unsupported claim. Reliability
                # must be declared before a class can carry weight.
                raise ValueError(
                    f"No declared reliability for document class(es) {unknown}. "
                    "Register the class in SOURCE_RELIABILITY before using it "
                    "as evidence."
                )
            # Corroboration does not raise confidence under min-propagation
            # (ADR-0002 §7.1). The best single source governs.
            def _rel(c: str) -> float:
                if c in authority.DOCUMENT_CLASSES:
                    return authority.DOCUMENT_CLASSES[c].reliability
                return SOURCE_RELIABILITY[c]
            return max(_rel(c) for c in classes)

        premises = [self.confidence(i) for i in s.input_statement_ids]
        if not premises:
            return 0.0
        base = min(premises)   # truth-preserving: cannot exceed its premises
        if s.method is Method.CALCULATED:
            return base
        return round(base * self.rules.get(s.rule_hash or "", 0.0), 6)

    def derivation_of(self, statement_id: str) -> DerivationNode:
        """The canonical explanation artifact (ADR-0002 §9.1).

        Returned raw. Any human-readable explanation must be rendered FROM this,
        never composed alongside it.
        """
        s = self._statements[statement_id]
        sources: List[str] = []
        for eid in s.evidence_event_ids:
            event = next(e for e in self.log.all() if e.event_id == eid)
            artifact = self.store.get(event.artifact_sha256)
            sources.append(f"{artifact.filename}@{event.locator}")
        return DerivationNode(
            statement_id=s.statement_id,
            question_id=s.question_id,
            value=s.value,
            method=s.method.value,
            derivation=s.derivation.value,
            confidence=self.confidence(s.statement_id),
            sources=tuple(sorted(sources)),
            inputs=tuple(self.derivation_of(i) for i in s.input_statement_ids),
        )

    # -- the read path (ADR-0002 §8) ------------------------------------------

    def answer(self, entity_id: str, question_id: str, as_of: Optional[str] = None) -> Answer:
        """Which published statements satisfy this question? None => UNKNOWN."""
        question = self.registry.get(question_id)
        candidates = [
            s for s in self._statements.values()
            if s.entity_id == entity_id
            and s.question_id == question_id
            and s.publish_status in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS, PublishStatus.PUBLISH_ALLOWED.value, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value)
            and s.human_review_state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
            and s.evidence_condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
            and s.is_valid_at(as_of)
        ]
        if not candidates:
            return Answer(
                question_id=question_id,
                entity_id=entity_id,
                known=False,
                unknown_guidance=question.unknown_guidance,
            )
        best = max(candidates, key=lambda s: (self.confidence(s.statement_id), s.statement_id))
        return Answer(
            question_id=question_id,
            entity_id=entity_id,
            known=True,
            value=best.value,
            confidence=self.confidence(best.statement_id),
            derivation=self.derivation_of(best.statement_id),
        )

    def coverage(self, entity_id: str, entity_type: str, as_of: Optional[str] = None) -> Dict[str, Any]:
        """How many registered questions can this entity answer? (ADR-0002 §8.1)"""
        questions = self.registry.for_entity_type(entity_type)
        answered = [
            q for q in questions
            if self.answer(entity_id, q.question_id, as_of).known
        ]
        return {
            "entity_id": entity_id,
            "questions_registered": len(questions),
            "questions_answerable": len(answered),
            "coverage": round(len(answered) / len(questions), 4) if questions else 0.0,
            "unknown_question_ids": sorted(
                q.question_id for q in questions if q not in answered
            ),
        }
