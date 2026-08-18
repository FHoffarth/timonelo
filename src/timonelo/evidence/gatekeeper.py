"""
src/timonelo/evidence/gatekeeper.py

Evidence Gatekeeper v1 — The Absolute Trust Infrastructure for Timonelo.
Governed by:
- Principle: No evidence -> no canonical truth.
- Principle: Unverified does not mean false; it means unverified.
- Epistemic Ceiling: A derived layer cannot be more trusted than its weakest source.

Components:
1. SourceArtifactModel & Verification
2. Fact-Level Evidence Model
3. Geometry Provenance Model
4. Epistemic Ceiling Computer
5. Deterministic Coverage Engine
6. Conflict Gate
7. Central Publish Gatekeeper
8. Report Language Guard
"""

from __future__ import annotations

import os
import re
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple


# =========================================================================
# 1. SOURCE ARTIFACT MODEL
# =========================================================================

class SourceType(str, Enum):
    OFFICIAL_PDF = "OFFICIAL_PDF"
    BUILDER_DOC = "BUILDER_DOC"
    REGISTER = "REGISTER"
    OFFICIAL_WEB = "OFFICIAL_WEB"
    OTHER = "OTHER"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    MISSING = "MISSING"
    HASH_MISMATCH = "HASH_MISMATCH"


def compute_file_sha256(path: str) -> Optional[str]:
    """Computes SHA-256 of real physical bytes on disk."""
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class SourceArtifact:
    source_id: str
    title: str
    publisher: str
    source_type: SourceType
    file_path: Optional[str] = None
    source_url: Optional[str] = None
    edition: Optional[str] = None
    publication_date: Optional[str] = None
    retrieved_at: Optional[str] = None
    sha256: Optional[str] = None
    page_count: int = 0
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

    def verify_physical_artifact(self) -> VerificationStatus:
        """Verifies the physical presence and SHA-256 hash of the artifact file."""
        if not self.file_path or not os.path.isfile(self.file_path):
            self.verification_status = VerificationStatus.MISSING
            return self.verification_status

        actual_sha256 = compute_file_sha256(self.file_path)
        if self.sha256:
            if actual_sha256.lower() != self.sha256.lower():
                self.verification_status = VerificationStatus.HASH_MISMATCH
                return self.verification_status
        else:
            self.sha256 = actual_sha256

        self.verification_status = VerificationStatus.VERIFIED
        return self.verification_status

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["source_type"] = self.source_type.value
        d["verification_status"] = self.verification_status.value
        return d


# =========================================================================
# 2. FACT-LEVEL EVIDENCE MODEL
# =========================================================================

class EpistemicStatus(str, Enum):
    DIRECT = "DIRECT"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTED = "CONFLICTED"


@dataclass
class EvidenceLocator:
    source_id: str
    page: Optional[int] = None
    section: Optional[str] = None
    evidence_type: str = "TEXT"  # TEXT | TABLE | VISUAL | GEOMETRY
    locator: Optional[str] = None  # e.g. "P.3/Deck6/Musica"


@dataclass
class FactEvidenceRecord:
    fact_id: str
    entity_id: str
    attribute: str
    value: Any
    epistemic_status: EpistemicStatus
    evidence: List[EvidenceLocator] = field(default_factory=list)
    parent_fact_ids: List[str] = field(default_factory=list)

    def validate_epistemic_consistency(self, source_registry: Dict[str, SourceArtifact]) -> Tuple[bool, Optional[str]]:
        """Ensures that epistemic status strictly satisfies evidence rules."""
        if self.epistemic_status == EpistemicStatus.DIRECT:
            if not self.evidence:
                return False, f"Fact '{self.fact_id}' declared DIRECT but contains no evidence locators."
            for ev in self.evidence:
                src = source_registry.get(ev.source_id)
                if not src or src.verification_status != VerificationStatus.VERIFIED:
                    return False, f"Fact '{self.fact_id}' declared DIRECT but source '{ev.source_id}' is not VERIFIED."
                if ev.page is None and not ev.locator:
                    return False, f"Fact '{self.fact_id}' declared DIRECT but missing page/locator citation."

        elif self.epistemic_status == EpistemicStatus.DERIVED:
            if not self.parent_fact_ids:
                return False, f"Fact '{self.fact_id}' declared DERIVED but specifies no parent_fact_ids."

        elif self.epistemic_status == EpistemicStatus.CONFLICTED:
            if len(self.evidence) < 2:
                return False, f"Fact '{self.fact_id}' declared CONFLICTED but contains fewer than 2 evidence sources."

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["epistemic_status"] = self.epistemic_status.value
        return d


# =========================================================================
# 3. GEOMETRY PROVENANCE MODEL
# =========================================================================

class GeometryProvenanceType(str, Enum):
    DIRECT_SOURCE_GEOMETRY = "DIRECT_SOURCE_GEOMETRY"
    TRANSFORMED_SOURCE_GEOMETRY = "TRANSFORMED_SOURCE_GEOMETRY"
    DERIVED_GEOMETRY = "DERIVED_GEOMETRY"
    SYNTHETIC_GEOMETRY = "SYNTHETIC_GEOMETRY"
    UNKNOWN_PROVENANCE = "UNKNOWN_PROVENANCE"


@dataclass
class GeometryProvenanceRecord:
    object_id: str
    deck_number: int
    geometry_type: GeometryProvenanceType
    source_id: Optional[str] = None
    extraction_method: Optional[str] = None
    transform_parameters: Optional[Dict[str, Any]] = None
    confidence: float = 0.5

    def validate_geometry_provenance(self, source_registry: Dict[str, SourceArtifact]) -> Tuple[bool, Optional[str]]:
        """Ensures that geometry is not deceptively classified."""
        if self.geometry_type == GeometryProvenanceType.DIRECT_SOURCE_GEOMETRY:
            if not self.source_id:
                return False, f"Geometry '{self.object_id}' is DIRECT_SOURCE_GEOMETRY but has no source_id."
            src = source_registry.get(self.source_id)
            if not src or src.verification_status != VerificationStatus.VERIFIED:
                return False, f"Geometry '{self.object_id}' is DIRECT_SOURCE_GEOMETRY but source '{self.source_id}' is not VERIFIED."

        elif self.geometry_type == GeometryProvenanceType.TRANSFORMED_SOURCE_GEOMETRY:
            if not self.source_id or not self.transform_parameters:
                return False, f"Geometry '{self.object_id}' is TRANSFORMED_SOURCE_GEOMETRY but lacks transform parameters."

        elif self.geometry_type == GeometryProvenanceType.SYNTHETIC_GEOMETRY:
            if self.confidence > 0.60:
                return False, f"Geometry '{self.object_id}' is SYNTHETIC_GEOMETRY but carries unjustified confidence {self.confidence} > 0.60."

        return True, None


# =========================================================================
# 4. EPISTEMIC CEILING COMPUTER
# =========================================================================

def compute_epistemic_ceiling(
    upstream_statuses: List[EpistemicStatus],
    source_status: Optional[VerificationStatus] = None,
    geometry_type: Optional[GeometryProvenanceType] = None
) -> EpistemicStatus:
    """
    Central Epistemic Ceiling Rule:
    A downstream/derived layer can never be more trusted than the weakest link in its dependency chain.
    """
    # 1. Source availability ceiling
    if source_status in [VerificationStatus.MISSING, VerificationStatus.HASH_MISMATCH, VerificationStatus.UNVERIFIED]:
        return EpistemicStatus.UNVERIFIED

    # 2. Geometry type ceiling
    if geometry_type in [GeometryProvenanceType.SYNTHETIC_GEOMETRY, GeometryProvenanceType.UNKNOWN_PROVENANCE]:
        return EpistemicStatus.INFERRED

    # 3. Upstream dependency ceiling
    if not upstream_statuses:
        return EpistemicStatus.UNVERIFIED

    if any(s == EpistemicStatus.CONFLICTED for s in upstream_statuses):
        return EpistemicStatus.CONFLICTED
    if any(s == EpistemicStatus.UNVERIFIED for s in upstream_statuses):
        return EpistemicStatus.UNVERIFIED
    if any(s == EpistemicStatus.INFERRED for s in upstream_statuses):
        return EpistemicStatus.INFERRED
    if any(s == EpistemicStatus.DERIVED for s in upstream_statuses):
        return EpistemicStatus.DERIVED

    if all(s == EpistemicStatus.DIRECT for s in upstream_statuses):
        return EpistemicStatus.DIRECT

    return EpistemicStatus.UNVERIFIED


# =========================================================================
# 5. DETERMINISTIC COVERAGE ENGINE
# =========================================================================

@dataclass
class EpistemicCoverageMetrics:
    total_sources: int = 0
    verified_sources: int = 0
    source_coverage_pct: float = 0.0

    total_facts: int = 0
    direct_facts: int = 0
    derived_facts: int = 0
    inferred_facts: int = 0
    unverified_facts: int = 0
    fact_evidence_coverage_pct: float = 0.0
    direct_evidence_coverage_pct: float = 0.0

    total_geometry_objects: int = 0
    direct_geometry_objects: int = 0
    synthetic_geometry_objects: int = 0
    geometry_provenance_coverage_pct: float = 0.0

    total_graph_relations: int = 0
    grounded_graph_relations: int = 0
    graph_provenance_coverage_pct: float = 0.0

    conflicts_total: int = 0
    conflicts_resolved: int = 0
    conflict_resolution_coverage_pct: float = 0.0

    global_epistemic_score: float = 0.0

    def compute_all_metrics(self) -> None:
        """Computes deterministic percentages and weighted global epistemic score."""
        self.source_coverage_pct = round((self.verified_sources / max(1, self.total_sources)) * 100.0, 2)
        
        grounded_facts = self.direct_facts + self.derived_facts
        self.fact_evidence_coverage_pct = round((grounded_facts / max(1, self.total_facts)) * 100.0, 2)
        self.direct_evidence_coverage_pct = round((self.direct_facts / max(1, self.total_facts)) * 100.0, 2)

        self.geometry_provenance_coverage_pct = round((self.direct_geometry_objects / max(1, self.total_geometry_objects)) * 100.0, 2)
        self.graph_provenance_coverage_pct = round((self.grounded_graph_relations / max(1, self.total_graph_relations)) * 100.0, 2)

        if self.conflicts_total > 0:
            self.conflict_resolution_coverage_pct = round((self.conflicts_resolved / self.conflicts_total) * 100.0, 2)
        else:
            self.conflict_resolution_coverage_pct = 100.0

        # Weighted Composite Epistemic Formula:
        # 30% Source + 30% Fact Evidence + 20% Geometry + 20% Graph
        self.global_epistemic_score = round(
            (0.30 * self.source_coverage_pct) +
            (0.30 * self.fact_evidence_coverage_pct) +
            (0.20 * self.geometry_provenance_coverage_pct) +
            (0.20 * self.graph_provenance_coverage_pct),
            2
        )


# =========================================================================
# 6. CONFLICT GATE
# =========================================================================

@dataclass
class ConflictGateResult:
    executed: bool = False
    resolver_version: str = "ConflictResolver_v1.0"
    checked_entities: int = 0
    conflicts_found: int = 0
    unresolved_conflicts: int = 0
    conflicts_log: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def status_summary(self) -> str:
        if not self.executed:
            return "CONFLICT STATUS UNKNOWN (Conflict Detection not executed)"
        if self.unresolved_conflicts == 0:
            return f"0 Unresolved Conflicts ({self.conflicts_found} detected & resolved)"
        return f"{self.unresolved_conflicts} UNRESOLVED CONFLICTS"


# =========================================================================
# 7. PUBLISH GATEKEEPER
# =========================================================================

class PublishStatus(str, Enum):
    PUBLISH_ALLOWED = "PUBLISH_ALLOWED"
    PUBLISH_ALLOWED_WITH_WARNINGS = "PUBLISH_ALLOWED_WITH_WARNINGS"
    PUBLISH_BLOCKED = "PUBLISH_BLOCKED"


@dataclass
class PublishGateResult:
    status: PublishStatus
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Optional[EpistemicCoverageMetrics] = None
    conflict_gate: Optional[ConflictGateResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "publish_status": self.status.value,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "global_epistemic_score": self.metrics.global_epistemic_score if self.metrics else 0.0,
            "conflict_status": self.conflict_gate.status_summary if self.conflict_gate else "UNKNOWN"
        }


class EvidenceGatekeeper:
    """
    Central Gatekeeper orchestrating canonical release verification.
    """

    def __init__(self):
        self.sources: Dict[str, SourceArtifact] = {}
        self.facts: List[FactEvidenceRecord] = []
        self.geometries: List[GeometryProvenanceRecord] = []
        self.graph_relations: List[Dict[str, Any]] = []
        self.conflict_gate = ConflictGateResult()

    def register_source(self, source: SourceArtifact) -> None:
        source.verify_physical_artifact()
        self.sources[source.source_id] = source

    def add_fact(self, fact: FactEvidenceRecord) -> None:
        self.facts.append(fact)

    def add_geometry(self, geom: GeometryProvenanceRecord) -> None:
        self.geometries.append(geom)

    def set_conflict_result(self, result: ConflictGateResult) -> None:
        self.conflict_gate = result

    def evaluate_publish_gate(self) -> PublishGateResult:
        reasons: List[str] = []
        warnings: List[str] = []

        # 1. Check Primary Sources
        if not self.sources:
            reasons.append("NO_SOURCES_REGISTERED")
        else:
            missing_sources = [s.source_id for s in self.sources.values() if s.verification_status == VerificationStatus.MISSING]
            if missing_sources:
                reasons.append(f"PRIMARY_SOURCE_MISSING: {', '.join(missing_sources)}")

            mismatched_sources = [s.source_id for s in self.sources.values() if s.verification_status == VerificationStatus.HASH_MISMATCH]
            if mismatched_sources:
                reasons.append(f"SOURCE_HASH_MISMATCH: {', '.join(mismatched_sources)}")

        # 2. Validate Fact-Level Epistemic Integrity
        for fact in self.facts:
            valid, err = fact.validate_epistemic_consistency(self.sources)
            if not valid:
                reasons.append(f"INVALID_FACT_EPISTEMIC_STATUS: {err}")

        # 3. Check Geometry Provenance Truth
        for geom in self.geometries:
            valid, err = geom.validate_geometry_provenance(self.sources)
            if not valid:
                reasons.append(f"GEOMETRY_PROVENANCE_VIOLATION: {err}")

        # 4. Check Conflict Detection Execution
        if not self.conflict_gate.executed:
            reasons.append("CONFLICT_DETECTION_NOT_EXECUTED")
        elif self.conflict_gate.unresolved_conflicts > 0:
            reasons.append(f"UNRESOLVED_CRITICAL_CONFLICTS ({self.conflict_gate.unresolved_conflicts})")

        # 5. Compute Coverage Metrics
        metrics = EpistemicCoverageMetrics(
            total_sources=len(self.sources),
            verified_sources=sum(1 for s in self.sources.values() if s.verification_status == VerificationStatus.VERIFIED),
            total_facts=len(self.facts),
            direct_facts=sum(1 for f in self.facts if f.epistemic_status == EpistemicStatus.DIRECT),
            derived_facts=sum(1 for f in self.facts if f.epistemic_status == EpistemicStatus.DERIVED),
            inferred_facts=sum(1 for f in self.facts if f.epistemic_status == EpistemicStatus.INFERRED),
            unverified_facts=sum(1 for f in self.facts if f.epistemic_status == EpistemicStatus.UNVERIFIED),
            total_geometry_objects=len(self.geometries),
            direct_geometry_objects=sum(1 for g in self.geometries if g.geometry_type in [GeometryProvenanceType.DIRECT_SOURCE_GEOMETRY, GeometryProvenanceType.TRANSFORMED_SOURCE_GEOMETRY]),
            synthetic_geometry_objects=sum(1 for g in self.geometries if g.geometry_type == GeometryProvenanceType.SYNTHETIC_GEOMETRY),
            total_graph_relations=len(self.graph_relations),
            grounded_graph_relations=sum(1 for r in self.graph_relations if r.get("grounded", False)),
            conflicts_total=self.conflict_gate.conflicts_found,
            conflicts_resolved=self.conflict_gate.conflicts_found - self.conflict_gate.unresolved_conflicts
        )
        metrics.compute_all_metrics()

        if metrics.global_epistemic_score < 70.0:
            warnings.append(f"LOW_GLOBAL_EPISTEMIC_SCORE ({metrics.global_epistemic_score}%)")

        if reasons:
            return PublishGateResult(status=PublishStatus.PUBLISH_BLOCKED, reasons=reasons, warnings=warnings, metrics=metrics, conflict_gate=self.conflict_gate)
        elif warnings:
            return PublishGateResult(status=PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS, reasons=[], warnings=warnings, metrics=metrics, conflict_gate=self.conflict_gate)
        else:
            return PublishGateResult(status=PublishStatus.PUBLISH_ALLOWED, reasons=[], warnings=[], metrics=metrics, conflict_gate=self.conflict_gate)


# =========================================================================
# 8. REPORT LANGUAGE GUARD
# =========================================================================

BANNED_UNGROUNDED_CLAIMS = [
    r"100%\s+verified",
    r"all\s+facts\s+directly\s+verified",
    r"0\s+conflicts(?!\s+detected\s+&\s+resolved)",
    r"canonical\s+truth\s+guaranteed"
]

def sanitize_report_content(report_text: str, gate_result: PublishGateResult) -> str:
    """
    Ensures that report documents do not contain fraudulent claims if publish gate is not fully allowed.
    """
    if gate_result.status == PublishStatus.PUBLISH_BLOCKED:
        for pattern in BANNED_UNGROUNDED_CLAIMS:
            report_text = re.sub(pattern, "[UNVERIFIED / BLOCKED]", report_text, flags=re.IGNORECASE)
    return report_text
