"""
Truth Engine — the read path.

Governed by ADR-0002 §8, §9.

The engine asks one thing: for this registered question about this entity,
which statements currently satisfy it?

  * Only APPROVED and PUBLISHED statements are consulted. DRAFT and
    UNDER_REVIEW are invisible here and can never appear in a passenger answer.
  * If none satisfy, the answer is UNKNOWN by construction. There is no
    UNKNOWN literal and no special case.
  * Confidence is computed from the artifact's document class at query time and
    is never stored.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from timonelo.evidence import authority
from timonelo.evidence.editor import Statement, StatementEditor
from timonelo.evidence.questions import QuestionRegistry
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus


@dataclass(frozen=True)
class Provenance:
    """Where an answer came from. Returned raw; renderers project from it."""
    statement_id: str
    artifact_id: str
    filename: str
    document_class: str
    page: Optional[int]
    locator: str
    read_by: str
    read_on: str
    publisher: Optional[str]
    published_on: Optional[str]
    version: Optional[str]


@dataclass(frozen=True)
class Answer:
    """Either a satisfied statement or UNKNOWN. There is no third outcome."""
    entity_id: str
    question_id: str
    known: bool
    value: Any = None
    confidence: Optional[float] = None
    provenance: Optional[Provenance] = None
    unknown_guidance: Optional[str] = None
    # An open conflict does not withdraw the published answer — the passenger
    # still sees what was last published. But serving a contested value as
    # though it were uncontested is the Language Layer strengthening a claim
    # (ADR-0002 9), so the contest travels with the answer and renderers must
    # disclose it.
    contested: bool = False
    conflict_ids: tuple = ()


class TruthEngine:
    def __init__(
        self,
        questions: QuestionRegistry,
        editor: StatementEditor,
        registry: ArtifactRegistry,
        conflict_log=None,
    ):
        self.questions = questions
        self.editor = editor
        self.registry = registry
        self.conflict_log = conflict_log

    def confidence(self, statement: Statement) -> float:
        """Computed from the document class. Never read from storage."""
        artifact = self.registry.get(statement.artifact_id)
        return authority.reliability_of(artifact.document_class)

    def _provenance(self, statement: Statement) -> Provenance:
        a = self.registry.get(statement.artifact_id)
        return Provenance(
            statement_id=statement.statement_id,
            artifact_id=a.artifact_id,
            filename=a.filename,
            document_class=a.document_class,
            page=statement.page,
            locator=statement.locator,
            read_by=statement.read_by,
            read_on=statement.read_on,
            publisher=a.publisher,
            published_on=a.published_on,
            version=a.version,
        )

    def _valid_at(self, s: Statement, as_of: Optional[str]) -> bool:
        if as_of is None:
            return True
        if s.valid_from and as_of < s.valid_from:
            return False
        if s.valid_until and as_of > s.valid_until:
            return False
        return True

    def answer(
        self, entity_id: str, question_id: str, as_of: Optional[str] = None
    ) -> Answer:
        question = self.questions.get(question_id)
        candidates = [
            s for s in self.editor.all()
            if s.entity_id == entity_id
            and s.question_id == question_id
            and s.publishing in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS)
            and s.state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
            and s.condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
            and self._valid_at(s, as_of)
        ]
        open_conflicts = ()
        if self.conflict_log is not None:
            open_conflicts = tuple(
                c.conflict_id
                for c in self.conflict_log.open_for_question(entity_id, question_id)
            )

        if not candidates:
            return Answer(
                entity_id=entity_id,
                question_id=question_id,
                known=False,
                unknown_guidance=question.unknown_guidance,
                contested=bool(open_conflicts),
                conflict_ids=open_conflicts,
            )
        best = max(
            candidates, key=lambda s: (self.confidence(s), s.statement_id)
        )
        return Answer(
            entity_id=entity_id,
            question_id=question_id,
            known=True,
            value=best.value,
            confidence=self.confidence(best),
            provenance=self._provenance(best),
            contested=bool(open_conflicts),
            conflict_ids=open_conflicts,
        )

    def coverage(
        self, entity_id: str, entity_type: str, as_of: Optional[str] = None
    ) -> Dict[str, Any]:
        qs = self.questions.for_entity_type(entity_type)
        answered = [
            q for q in qs if self.answer(entity_id, q.question_id, as_of).known
        ]
        return {
            "entity_id": entity_id,
            "questions_registered": len(qs),
            "questions_answerable": len(answered),
            "coverage": round(len(answered) / len(qs), 4) if qs else 0.0,
            "unknown_question_ids": sorted(
                q.question_id for q in qs if q not in answered
            ),
        }
