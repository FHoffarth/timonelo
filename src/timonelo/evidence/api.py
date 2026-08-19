"""
Inspection APIs — structured access to the evidence store.

Governed by ADR-0002 §8, §9.

These return data, not formatted text. `workspace.format_*` renders for a human
terminal; these are for programmatic callers, and both project from the same
underlying records so they cannot drift apart.

Nothing here can mutate the store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from timonelo.evidence import authority
from timonelo.evidence.editor import Statement
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus


@dataclass(frozen=True)
class StatementSummary:
    statement_id: str
    entity_id: str
    question_id: str
    statement_type: str
    value: Any
    review_state: str
    answerable: bool
    page: Optional[int]
    locator: str
    read_by: str
    read_on: str


@dataclass(frozen=True)
class ArtifactInspection:
    artifact_id: str
    sha256: str
    integrity_ok: bool
    filename: str
    byte_size: int
    document_class: str
    document_class_declared: bool
    reliability: Optional[float]
    validity_scope: Optional[str]
    acquisition: Optional[str]
    use_permission: Optional[str]
    publisher: Optional[str]
    published_on: Optional[str]
    version: Optional[str]
    language: Optional[str]
    acquired_on: str
    acquisition_method: str
    notes: str
    supported_statement_types: List[str]
    statements: List[StatementSummary]
    coverage: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.__dict__)
        d["statements"] = [dict(s.__dict__) for s in self.statements]
        return d


def _summarise(s: Statement) -> StatementSummary:
    answerable = (
        s.publishing in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS)
        and s.state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
        and s.condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
    )
    return StatementSummary(
        statement_id=s.statement_id,
        entity_id=s.entity_id,
        question_id=s.question_id,
        statement_type=s.statement_type,
        value=s.value,
        review_state=s.review_state,
        answerable=answerable,
        page=s.page,
        locator=s.locator,
        read_by=s.read_by,
        read_on=s.read_on,
    )


class ArtifactInspectionAPI:
    """Everything known about one artifact."""

    def __init__(self, workspace):
        self.ws = workspace

    def inspect(self, artifact_id: str) -> ArtifactInspection:
        a = self.ws.registry.get(artifact_id)
        cls = authority.DOCUMENT_CLASSES.get(a.document_class)
        supported = sorted(
            stype for stype, classes in authority.AUTHORITY.items()
            if a.document_class in classes
        )
        return ArtifactInspection(
            artifact_id=a.artifact_id,
            sha256=a.sha256,
            integrity_ok=self.ws.registry.verify(artifact_id),
            filename=a.filename,
            byte_size=a.byte_size,
            document_class=a.document_class,
            document_class_declared=cls is not None,
            reliability=cls.reliability if cls else None,
            validity_scope=cls.validity_scope.value if cls else None,
            acquisition=cls.acquisition.value if cls else None,
            use_permission=cls.use_permission.value if cls else None,
            publisher=a.publisher,
            published_on=a.published_on,
            version=a.version,
            language=a.language,
            acquired_on=a.acquired_on,
            acquisition_method=a.acquisition_method,
            notes=a.notes,
            supported_statement_types=supported,
            statements=[
                _summarise(s) for s in self.ws.statements_for_artifact(artifact_id)
            ],
            coverage=self.ws.document_coverage(artifact_id),
        )

    def list_all(self) -> List[ArtifactInspection]:
        return [self.inspect(a.artifact_id) for a in self.ws.registry.list_all()]

    def integrity_report(self) -> Dict[str, Any]:
        failed = self.ws.registry.verify_all()
        return {
            "artifacts": len(self.ws.registry),
            "failed": failed,
            "all_intact": not failed,
        }


class StatementRegistryAPI:
    """Query access to statements. Read-only by construction.

    Creation and state transitions stay with the StatementEditor; exposing them
    here would give callers a second route into the review workflow.
    """

    def __init__(self, workspace):
        self.ws = workspace

    def get(self, statement_id: str) -> StatementSummary:
        return _summarise(self.ws.editor.get(statement_id))

    def query(
        self,
        entity_id: Optional[str] = None,
        question_id: Optional[str] = None,
        statement_type: Optional[str] = None,
        artifact_id: Optional[str] = None,
        review_state: Optional[str] = None,
        answerable_only: bool = False,
    ) -> List[StatementSummary]:
        out = []
        for s in self.ws.editor.all():
            if entity_id and s.entity_id != entity_id:
                continue
            if question_id and s.question_id != question_id:
                continue
            if statement_type and s.statement_type != statement_type:
                continue
            if artifact_id and s.artifact_id != artifact_id:
                continue
            if review_state and s.review_state != review_state:
                continue
            is_answerable = (
                s.publishing in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS)
                and s.state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
                and s.condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
            )
            if answerable_only and not is_answerable:
                continue
            out.append(_summarise(s))
        return out

    def history(self, statement_id: str) -> List[Dict[str, str]]:
        return [e.to_dict() for e in self.ws.reviews.history(statement_id)]

    def counts_by_state(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in HumanReviewState}
        for s in self.ws.editor.all():
            counts[s.review_state] = counts.get(s.review_state, 0) + 1
        return counts

    def pending_review(self) -> List[StatementSummary]:
        """Statements waiting on a human. The curator's work queue."""
        return [
            _summarise(s) for s in self.ws.editor.all()
            if s.state in (HumanReviewState.DRAFT, HumanReviewState.UNDER_REVIEW)
        ]
