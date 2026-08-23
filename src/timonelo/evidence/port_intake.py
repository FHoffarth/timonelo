"""
Port Evidence Intake Module (ADR-0002).

Generic, port-agnostic intake mechanism for port authorities, UN/LOCODE registries,
and terminal operator specifications.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from timonelo.evidence import authority
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.models import Statement
from timonelo.evidence.registry import Artifact, ArtifactRegistry, sha256_of_file
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)


@dataclass(frozen=True)
class PortSourceDescriptor:
    """Metadata describing a physical port source document."""
    path: str
    document_class: str
    acquired_on: str
    acquisition_method: str
    publisher: Optional[str] = None
    published_on: Optional[str] = None
    version: Optional[str] = None
    language: Optional[str] = None
    notes: str = ""


@dataclass(frozen=True)
class PortClaimDraft:
    """A single factual claim extracted from an authoritative port source."""
    entity_id: str
    question_id: str
    statement_type: str
    value: Any
    locator: str
    read_by: str
    read_on: str
    page: Optional[int] = None
    method: Method = Method.DIRECT
    derivation: Derivation = Derivation.LOCAL
    derivation_note: str = ""
    note: str = ""


def ingest_port_source(
    workspace: Workspace,
    source: PortSourceDescriptor,
    claims: List[PortClaimDraft],
) -> Tuple[Artifact, List[EvidenceEvent], List[Statement]]:
    """Port-agnostic intake function.
    
    Accepts any authoritative port source document, registers it with the
    underlying ArtifactRegistry, records EvidenceEvents in the EvidenceEventLog,
    checks question and authority compatibility, and authors conservative
    Statement records (UNKNOWN / DRAFT / PUBLISH_BLOCKED) linked to their events.
    """
    if not os.path.isfile(source.path):
        raise FileNotFoundError(f"Source file not found at {source.path!r}")

    # 1. Register or retrieve artifact by digest
    artifact = workspace.registry.register(
        path=source.path,
        document_class=source.document_class,
        acquired_on=source.acquired_on,
        acquisition_method=source.acquisition_method,
        publisher=source.publisher,
        published_on=source.published_on,
        version=source.version,
        language=source.language,
        notes=source.notes,
    )

    # 2. Also ensure raw copy exists in SHA vault for long-term audit
    digest = artifact.sha256
    vault_dir = os.path.join(workspace.root, "raw", "sha256", digest[:2])
    os.makedirs(vault_dir, exist_ok=True)
    ext = os.path.splitext(source.path)[1]
    vault_target = os.path.join(vault_dir, f"{digest}{ext}")
    if not os.path.isfile(vault_target):
        shutil.copy2(source.path, vault_target)

    # Clean legacy blobs folder to maintain vault purity
    blob_file = os.path.join(workspace.registry.blobs, digest)
    if os.path.isfile(blob_file):
        try:
            os.remove(blob_file)
        except OSError:
            pass

    # 3. Create EvidenceEvents and Statements with strict authority and question validation
    created_events: List[EvidenceEvent] = []
    created_statements: List[Statement] = []
    for claim in claims:
        # Validate question in registry
        q = workspace.questions.get(claim.question_id)
        if q.statement_type != claim.statement_type:
            raise ValueError(
                f"Question {claim.question_id} statement type mismatch: "
                f"expected {q.statement_type!r}, got {claim.statement_type!r}"
            )

        # Authority check
        authority.check(claim.statement_type, artifact.document_class)

        # Create and record EvidenceEvent
        event_num = len(workspace.events) + 1
        event_id = f"EVT-PORT-{event_num:04d}"
        event = EvidenceEvent(
            event_id=event_id,
            artifact_sha256=artifact.sha256,
            locator=claim.locator,
            entity_id=claim.entity_id,
            question_id=claim.question_id,
            observed_value=claim.value,
            observed_by=claim.read_by,
            observed_on=claim.read_on,
            notes=claim.note,
        )
        workspace.events.append(event)
        created_events.append(event)

        # Author statement through StatementEditor with explicit event linkage
        stmt = workspace.editor.create(
            entity_id=claim.entity_id,
            question_id=claim.question_id,
            statement_type=claim.statement_type,
            value=claim.value,
            artifact_id=artifact.artifact_id,
            locator=claim.locator,
            read_by=claim.read_by,
            read_on=claim.read_on,
            page=claim.page,
            method=claim.method.value if isinstance(claim.method, Method) else claim.method,
            derivation_note=claim.derivation_note,
            evidence_event_ids=(event.event_id,),
            note=claim.note,
        )
        created_statements.append(stmt)

    return artifact, created_events, created_statements
