"""
Evidence Gatekeeper — Canonical release verification and truth gating.

Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-A.5 / P0-B Truth Model.

The Gatekeeper is a PURE EVALUATOR:
- It verifies artifact existence and cryptographic SHA-256 integrity on disk.
- It validates the statement-specific evidence closure:
    Statement -> evidence_event_ids -> EvidenceEvent -> Artifact -> Disk Bytes & Hash.
- It verifies document class eligibility against the question/claim.
- It evaluates Statement evidence conditions, human review states, and publish status.
- It validates geometry provenance and conflict status.
- It NEVER mutates or promotes any statement, review state, or publish status.
- It rejects fail-open defaults and collapses zero orthogonal axes.

SCOPE & GUARANTEE BOUNDARY:
- The Gatekeeper guarantees traceability, cryptographic integrity, locator presence,
  authority eligibility, and publication firewall conjunctions.
- It does NOT independently verify that the artifact text semantically equals the statement
  value; semantic extraction correctness is the upstream responsibility of curators and ingestion pipelines.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from timonelo.evidence.artifacts import Artifact, sha256_of_file
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.models import Statement
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.ontology.models import (
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)


class ArtifactVerificationStatus(str, Enum):
    """
    Gate evaluation status of a physical source artifact on disk.
    NOTE (ADR-0002): This is strictly a gate evaluation/result type and
    is NOT a canonical ontology model enum.
    """
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    HASH_MISMATCH = "HASH_MISMATCH"
    PRIVATE_SOURCE_NOT_LOCALLY_REVERIFIABLE = "PRIVATE_SOURCE_NOT_LOCALLY_REVERIFIABLE"


PLACEHOLDER_LOCATORS = frozenset({
    "",
    "unknown",
    "n/a",
    "na",
    "source",
    "document",
    "none",
    "null",
    "undefined",
    "unspecified",
})


@dataclass(frozen=True)
class SourceArtifactRecord:
    """A registered source document artifact for verification."""
    source_id: str
    title: str
    expected_sha256: str
    file_path: str
    document_class: str
    publisher: Optional[str] = None
    edition: Optional[str] = None
    private_source: bool = False

    def verify_physical_artifact(self) -> ArtifactVerificationStatus:
        """Computes real SHA-256 of file on disk and compares against expected hash."""
        if not os.path.exists(self.file_path):
            if self.private_source and len(self.expected_sha256) == 64:
                return ArtifactVerificationStatus.PRIVATE_SOURCE_NOT_LOCALLY_REVERIFIABLE
            return ArtifactVerificationStatus.MISSING
        actual_sha = sha256_of_file(self.file_path)
        if actual_sha.lower() != self.expected_sha256.lower():
            return ArtifactVerificationStatus.HASH_MISMATCH
        return ArtifactVerificationStatus.PRESENT


@dataclass(frozen=True)
class GeometryProvenanceRecord:
    """Geometry provenance tracking for spatial objects."""
    object_id: str
    deck_number: int
    geometry_provenance: GeometryProvenance
    source_id: Optional[str] = None
    transformation_record: Optional[str] = None

    def validate_geometry_provenance(
        self, sources: Dict[str, Tuple[SourceArtifactRecord, ArtifactVerificationStatus]]
    ) -> Tuple[bool, Optional[str]]:
        """Validates that geometry claims match possessed artifacts."""
        if self.geometry_provenance == GeometryProvenance.SYNTHETIC_GEOMETRY:
            # Synthetic geometry is valid as synthetic, but cannot claim direct derivation
            return True, None

        if self.geometry_provenance in (
            GeometryProvenance.DIRECT_SOURCE_GEOMETRY,
            GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY,
            GeometryProvenance.DERIVED_GEOMETRY,
        ):
            if not self.source_id or self.source_id not in sources:
                return False, f"Geometry {self.object_id} references unknown source {self.source_id}"
            _, status = sources[self.source_id]
            if status != ArtifactVerificationStatus.PRESENT:
                return False, f"Geometry {self.object_id} source {self.source_id} is {status.value}"

        return True, None


@dataclass(frozen=True)
class ConflictGateResult:
    """Result of conflict detection and resolution checks."""
    executed: bool = False
    checked_entities: int = 0
    conflicts_found: int = 0
    unresolved_conflicts: int = 0
    conflicts_log: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_conflict_log(
        cls, conflict_log: "ConflictLog"
    ) -> "ConflictGateResult":
        conflicts = conflict_log.all()
        return cls(
            executed=conflict_log.detection_executed,
            checked_entities=conflict_log.detection_run_count,
            conflicts_found=len(conflicts),
            unresolved_conflicts=len(conflict_log.open_conflicts()),
            conflicts_log=[conflict.to_dict() for conflict in conflicts],
        )

    @property
    def status_summary(self) -> str:
        if not self.executed:
            return "CONFLICT STATUS UNKNOWN (Conflict detection not executed)"
        if self.unresolved_conflicts == 0:
            return f"0 Unresolved Conflicts ({self.conflicts_found} detected & resolved)"
        return f"{self.unresolved_conflicts} UNRESOLVED CONFLICTS"


@dataclass(frozen=True)
class GateResult:
    """Orthogonal multi-axial result of the Evidence Gatekeeper evaluation."""
    status: PublishStatus
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    artifact_statuses: Dict[str, ArtifactVerificationStatus] = field(default_factory=dict)
    conflict_gate: ConflictGateResult = field(default_factory=ConflictGateResult)
    evaluated_statement_count: int = 0
    supported_statement_count: int = 0
    approved_statement_count: int = 0
    synthetic_geometry_count: int = 0
    direct_geometry_count: int = 0

    @property
    def is_publishable(self) -> bool:
        return self.status in (
            PublishStatus.PUBLISH_ALLOWED,
            PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "publish_status": self.status.value,
            "is_publishable": self.is_publishable,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "artifact_statuses": {k: v.value for k, v in self.artifact_statuses.items()},
            "conflict_status": self.conflict_gate.status_summary,
            "metrics": {
                "evaluated_statements": self.evaluated_statement_count,
                "supported_statements": self.supported_statement_count,
                "approved_statements": self.approved_statement_count,
                "synthetic_geometries": self.synthetic_geometry_count,
                "direct_geometries": self.direct_geometry_count,
            },
        }


class EvidenceGatekeeper:
    """
    Pure evaluator checking physical artifact integrity, statement evidence closure,
    document class authority, geometry provenance, and conflict safety against canonical rules.
    """

    def __init__(self, question_registry: Optional[QuestionRegistry] = None) -> None:
        self._sources: Dict[str, SourceArtifactRecord] = {}
        self._sources_by_sha: Dict[str, SourceArtifactRecord] = {}
        self._events: Dict[str, EvidenceEvent] = {}
        self._statements: List[Statement] = []
        self._geometries: List[GeometryProvenanceRecord] = []
        self._conflict_result: ConflictGateResult = ConflictGateResult(executed=False)
        self._question_registry: Optional[QuestionRegistry] = question_registry

    def register_source(self, source: SourceArtifactRecord) -> None:
        self._sources[source.source_id] = source
        self._sources_by_sha[source.expected_sha256.lower()] = source

    def register_event(self, event: EvidenceEvent) -> None:
        self._events[event.event_id] = event

    def add_statement(self, statement: Statement) -> None:
        self._statements.append(statement)

    def add_geometry(self, geometry: GeometryProvenanceRecord) -> None:
        self._geometries.append(geometry)

    def set_conflict_result(self, result: ConflictGateResult) -> None:
        """Legacy non-canonical injection seam; production paths use ConflictLog."""
        self._conflict_result = result

    def use_conflict_log(self, conflict_log: "ConflictLog") -> None:
        """Derive detector status from canonical log provenance."""
        self._conflict_result = ConflictGateResult.from_conflict_log(conflict_log)

    @classmethod
    def from_workspace(cls, workspace: Any) -> EvidenceGatekeeper:
        """Construct an EvidenceGatekeeper populated from a canonical Workspace."""
        gatekeeper = cls(question_registry=workspace.questions)
        if hasattr(workspace, "registry") and workspace.registry is not None:
            for artifact in workspace.registry.list_all():
                vault_path = workspace.registry.resolve_path(artifact.artifact_id)
                if not vault_path:
                    candidates = workspace.registry._vault_candidates(artifact)
                    vault_path = candidates[0] if candidates else workspace.registry.blob_path(artifact.artifact_id)
                gatekeeper.register_source(
                    SourceArtifactRecord(
                        source_id=artifact.artifact_id,
                        title=artifact.filename,
                        expected_sha256=artifact.sha256,
                        file_path=vault_path,
                        document_class=artifact.document_class,
                        publisher=artifact.publisher,
                        edition=artifact.version,
                        private_source=getattr(artifact, "private_source", False),
                    )
                )
        if hasattr(workspace, "events") and workspace.events is not None:
            for event in workspace.events.all():
                gatekeeper.register_event(event)
        if hasattr(workspace, "conflicts") and workspace.conflicts is not None:
            gatekeeper.use_conflict_log(workspace.conflicts)
        return gatekeeper

    def evaluate_publish_gate(self) -> GateResult:
        reasons: List[str] = []
        warnings: List[str] = []
        artifact_statuses: Dict[str, ArtifactVerificationStatus] = {}

        # 1. Verify physical artifacts on disk
        if not self._sources:
            reasons.append("NO_SOURCES_REGISTERED")
        else:
            for source_id, source in self._sources.items():
                status = source.verify_physical_artifact()
                artifact_statuses[source_id] = status
                if status == ArtifactVerificationStatus.MISSING:
                    reasons.append(f"PRIMARY_SOURCE_MISSING: {source_id} at {source.file_path}")
                elif status == ArtifactVerificationStatus.HASH_MISMATCH:
                    reasons.append(f"SOURCE_HASH_MISMATCH: {source_id}")

        # 2. Evaluate Statements against 4-Part Canonical Publication Firewall & Evidence Closure
        supported_count = 0
        approved_count = 0

        for stmt in self._statements:
            if stmt.evidence_condition == EvidenceCondition.SUPPORTED:
                supported_count += 1

                # Statement-Specific Evidence Closure Verification
                if stmt.method == Method.INFERRED:
                    if not stmt.input_statement_ids or not stmt.rule_hash:
                        reasons.append(
                            f"INFERRED_STATEMENT_INCOMPLETE_CLOSURE: {stmt.statement_id} is marked INFERRED but missing input_statement_ids or rule_hash"
                        )
                elif not stmt.evidence_event_ids:
                    reasons.append(
                        f"STATEMENT_ZERO_EVIDENCE_EVENTS: {stmt.statement_id} is marked SUPPORTED but has no evidence_event_ids"
                    )
                else:
                    for event_id in stmt.evidence_event_ids:
                        if event_id not in self._events:
                            reasons.append(
                                f"UNKNOWN_EVIDENCE_EVENT: Statement {stmt.statement_id} references unrecorded event {event_id}"
                            )
                            continue

                        event = self._events[event_id]

                        # Check locator
                        locator = event.locator.strip() if event.locator else ""
                        if not locator or locator.lower() in PLACEHOLDER_LOCATORS:
                            reasons.append(
                                f"INVALID_EVENT_LOCATOR: Event {event_id} for statement {stmt.statement_id} has placeholder locator '{event.locator}'"
                            )

                        # Check artifact referenced by event
                        artifact_sha = event.artifact_sha256.lower()
                        if artifact_sha not in self._sources_by_sha:
                            reasons.append(
                                f"EVENT_ARTIFACT_NOT_REGISTERED: Event {event_id} references artifact SHA {event.artifact_sha256[:12]} not in registered sources"
                            )
                            continue

                        source = self._sources_by_sha[artifact_sha]
                        source_status = artifact_statuses.get(source.source_id, ArtifactVerificationStatus.MISSING)
                        if source_status == ArtifactVerificationStatus.MISSING:
                            reasons.append(
                                f"EVENT_ARTIFACT_MISSING: Event {event_id} cites missing artifact {source.source_id}"
                            )
                        elif source_status == ArtifactVerificationStatus.HASH_MISMATCH:
                            reasons.append(
                                f"EVENT_ARTIFACT_HASH_MISMATCH: Event {event_id} cites hash-mismatched artifact {source.source_id}"
                            )
                        elif source_status == ArtifactVerificationStatus.PRIVATE_SOURCE_NOT_LOCALLY_REVERIFIABLE:
                            if stmt.publish_status in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS):
                                reasons.append(
                                    f"PRIVATE_SOURCE_UNVERIFIED_FOR_PUBLICATION: Statement {stmt.statement_id} depends on private source {source.source_id} whose bytes are not locally held for reverification"
                                )

                        # Document Class Eligibility Check
                        if self._question_registry is not None:
                            try:
                                question = self._question_registry.get(stmt.question_id)
                                if not question.can_be_supported_by(source.document_class):
                                    reasons.append(
                                        f"INELIGIBLE_DOCUMENT_CLASS: Artifact class '{source.document_class}' cannot support question '{stmt.question_id}'"
                                    )
                            except KeyError:
                                reasons.append(
                                    f"UNREGISTERED_QUESTION: Statement {stmt.statement_id} references unregistered question {stmt.question_id}"
                                )
                        else:
                            # Fallback check against authority matrix if question registry is absent
                            if source.document_class == "cruise_line_deck_plan":
                                technical_prefixes = ("ship.imo", "ship.gross_tonnage", "ship.length", "ship.engine", "ship.propulsion", "ship.crew")
                                if any(stmt.question_id.startswith(p) for p in technical_prefixes):
                                    reasons.append(
                                        f"INELIGIBLE_DOCUMENT_CLASS: cruise_line_deck_plan cannot support technical spec question '{stmt.question_id}'"
                                    )

            else:
                reasons.append(
                    f"STATEMENT_NOT_SUPPORTED: {stmt.statement_id} has evidence_condition={stmt.evidence_condition.value}"
                )

            if stmt.human_review_state == HumanReviewState.APPROVED:
                approved_count += 1
            else:
                reasons.append(
                    f"STATEMENT_NOT_APPROVED: {stmt.statement_id} has human_review_state={stmt.human_review_state.value}"
                )

            if stmt.publish_status == PublishStatus.PUBLISH_BLOCKED:
                reasons.append(
                    f"STATEMENT_PUBLISH_BLOCKED: {stmt.statement_id} publish_status=PUBLISH_BLOCKED"
                )

        # 3. Evaluate Geometry Provenance
        synthetic_geom_count = 0
        direct_geom_count = 0
        sources_with_status = {
            s_id: (self._sources[s_id], artifact_statuses.get(s_id, ArtifactVerificationStatus.MISSING))
            for s_id in self._sources
        }

        for geom in self._geometries:
            if geom.geometry_provenance == GeometryProvenance.SYNTHETIC_GEOMETRY:
                synthetic_geom_count += 1
            else:
                direct_geom_count += 1

            valid, err = geom.validate_geometry_provenance(sources_with_status)
            if not valid:
                reasons.append(f"GEOMETRY_PROVENANCE_VIOLATION: {err}")

        # 4. Check Conflict Detection Execution
        if not self._conflict_result.executed:
            reasons.append("CONFLICT_DETECTION_NOT_EXECUTED")
        elif self._conflict_result.unresolved_conflicts > 0:
            reasons.append(f"UNRESOLVED_CRITICAL_CONFLICTS ({self._conflict_result.unresolved_conflicts})")

        # 5. Determine overall gate status
        if reasons:
            final_status = PublishStatus.PUBLISH_BLOCKED
        elif warnings:
            final_status = PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS
        else:
            final_status = PublishStatus.PUBLISH_ALLOWED

        return GateResult(
            status=final_status,
            reasons=reasons,
            warnings=warnings,
            artifact_statuses=artifact_statuses,
            conflict_gate=self._conflict_result,
            evaluated_statement_count=len(self._statements),
            supported_statement_count=supported_count,
            approved_statement_count=approved_count,
            synthetic_geometry_count=synthetic_geom_count,
            direct_geometry_count=direct_geom_count,
        )


BANNED_UNGROUNDED_CLAIMS = [
    r"100%\s+verified",
    r"all\s+facts\s+directly\s+verified",
    r"0\s+conflicts(?!\s+detected\s+&\s+resolved)",
    r"canonical\s+truth\s+guaranteed",
]


def sanitize_report_content(report_text: str, gate_result: GateResult) -> str:
    """Replaces ungrounded claims in generated reports if publication is blocked."""
    if gate_result.status == PublishStatus.PUBLISH_BLOCKED:
        for pattern in BANNED_UNGROUNDED_CLAIMS:
            report_text = re.sub(pattern, "[UNVERIFIED / BLOCKED]", report_text, flags=re.IGNORECASE)
    return report_text


def is_canonical_statement_admitted(statement: Union[Statement, Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Shared canonical predicate for statement publication admission (ADR-0002 §8, ADR-0003 §7).
    A statement participates in published truth if and only if all three lifecycle axes pass:
      1. evidence_condition == EvidenceCondition.SUPPORTED
      2. human_review_state == HumanReviewState.APPROVED
      3. publish_status in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS)
    """
    if isinstance(statement, Statement):
        cond = statement.evidence_condition
        rev = statement.human_review_state
        pub = statement.publish_status
        sid = statement.statement_id
    elif isinstance(statement, dict):
        cond_val = statement.get("evidence_condition")
        rev_val = statement.get("human_review_state")
        pub_val = statement.get("publish_status")
        try:
            cond = EvidenceCondition(cond_val) if isinstance(cond_val, str) else cond_val
            rev = HumanReviewState(rev_val) if isinstance(rev_val, str) else rev_val
            pub = PublishStatus(pub_val) if isinstance(pub_val, str) else pub_val
        except (ValueError, TypeError):
            return False, f"Invalid enum values in statement: cond={cond_val}, rev={rev_val}, pub={pub_val}"
        sid = statement.get("statement_id", "dict_statement")
    else:
        return False, f"Invalid statement type: {type(statement)}"

    if cond != EvidenceCondition.SUPPORTED:
        return False, f"Statement {sid} evidence_condition is {cond.value if hasattr(cond, 'value') else cond} (must be SUPPORTED)"
    if rev != HumanReviewState.APPROVED:
        return False, f"Statement {sid} human_review_state is {rev.value if hasattr(rev, 'value') else rev} (must be APPROVED)"
    if pub not in (PublishStatus.PUBLISH_ALLOWED, PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS):
        return False, f"Statement {sid} publish_status is {pub.value if hasattr(pub, 'value') else pub} (must be PUBLISH_ALLOWED)"

    return True, "Canonical publication criteria satisfied"
