"""
Evidence Gatekeeper — Canonical release verification and truth gating.

Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-A.5 Truth Model.

The Gatekeeper is a PURE EVALUATOR:
- It verifies artifact existence and cryptographic SHA-256 integrity on disk.
- It evaluates Statement evidence conditions, human review states, and publish status.
- It validates geometry provenance and conflict status.
- It NEVER mutates or promotes any statement, review state, or publish status.
- It rejects fail-open defaults and collapses zero orthogonal axes.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from timonelo.evidence.artifacts import sha256_of_file
from timonelo.evidence.engine import Statement
from timonelo.ontology.models import (
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    PublishStatus,
)


class ArtifactVerificationStatus(str, Enum):
    """Integrity status of a physical source artifact on disk."""
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    HASH_MISMATCH = "HASH_MISMATCH"


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

    def verify_physical_artifact(self) -> ArtifactVerificationStatus:
        """Computes real SHA-256 of file on disk and compares against expected hash."""
        if not os.path.exists(self.file_path):
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
    Pure evaluator checking physical artifact integrity, statement validity,
    geometry provenance, and conflict safety against canonical rules.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, SourceArtifactRecord] = {}
        self._statements: List[Statement] = []
        self._geometries: List[GeometryProvenanceRecord] = []
        self._conflict_result: ConflictGateResult = ConflictGateResult(executed=False)

    def register_source(self, source: SourceArtifactRecord) -> None:
        self._sources[source.source_id] = source

    def add_statement(self, statement: Statement) -> None:
        self._statements.append(statement)

    def add_geometry(self, geometry: GeometryProvenanceRecord) -> None:
        self._geometries.append(geometry)

    def set_conflict_result(self, result: ConflictGateResult) -> None:
        self._conflict_result = result

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

        # 2. Evaluate Statements against 4-Part Canonical Publication Firewall
        supported_count = 0
        approved_count = 0

        for stmt in self._statements:
            if stmt.evidence_condition == EvidenceCondition.SUPPORTED:
                supported_count += 1
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
