# Knowledge Factory Protocol & Interface Definitions
### Python Structural Typing Architecture for the Compilation Pipeline

```python
"""
factory/interfaces.py (Specification Blueprint)
Core protocols for the 8-stage Timonelo Knowledge Factory.
"""

from typing import Protocol, runtime_checkable, Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    VERIFIED = "VERIFIED"
    EXPERIENCE_READY = "EXPERIENCE_READY"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class PipelineContext:
    vessel_imo: str
    target_version: str
    execution_id: str
    rule_version: str


@dataclass(frozen=True)
class StageResult:
    stage_name: str
    success: bool
    output_payload: Dict[str, Any]
    error_manifest: Optional[List[Dict[str, Any]]] = None


@runtime_checkable
class PipelineStage(Protocol):
    """Base protocol implemented by all factory pipeline stages."""
    
    @property
    def stage_id(self) -> str:
        ...

    def execute(self, context: PipelineContext, input_payload: Dict[str, Any]) -> StageResult:
        """Execute stage transformations and emit validated output payload."""
        ...


# --- STAGE-SPECIFIC PROTOCOLS ---

class IEvidenceIntakeStage(PipelineStage, Protocol):
    """Stage 01: Ingests, hashes, and registers raw GA blueprints and manifests."""
    def ingest_sources(self, context: PipelineContext, source_manifest: Dict[str, Any]) -> StageResult:
        ...


class INormalizationStage(PipelineStage, Protocol):
    """Stage 02: Calibrates and normalizes geometries into Cartesian unit space."""
    def normalize_geometry(self, context: PipelineContext, evidence_batch: Dict[str, Any]) -> StageResult:
        ...


class IArchetypeMatcherStage(PipelineStage, Protocol):
    """Stage 03: Matches vessel to master archetype and inherits baseline geometry."""
    def bind_archetype(self, context: PipelineContext, normalized_draft: Dict[str, Any]) -> StageResult:
        ...


class IShipDeltaDetectorStage(PipelineStage, Protocol):
    """Stage 04: Isolates vessel-specific physical modifications and mutations."""
    def detect_deltas(self, context: PipelineContext, archetype_bound: Dict[str, Any]) -> StageResult:
        ...


class IPackGeneratorStage(PipelineStage, Protocol):
    """Stage 05: Compiles reconciled model into canonical knowledge-pack.json."""
    def generate_pack(self, context: PipelineContext, reconciled_model: Dict[str, Any]) -> StageResult:
        ...


class ISpatialValidatorStage(PipelineStage, Protocol):
    """Stage 06: Performs polygon collision and corridor connectivity audits."""
    def validate_spatial_integrity(self, context: PipelineContext, candidate_pack: Dict[str, Any]) -> StageResult:
        ...


class IExperienceValidatorStage(PipelineStage, Protocol):
    """Stage 07: Audits overhead sandwich, sightline raycasts, and socket counts."""
    def validate_experience_rules(self, context: PipelineContext, spatial_pack: Dict[str, Any]) -> StageResult:
        ...


class IPublicationStage(PipelineStage, Protocol):
    """Stage 08: Digitally signs, seals, and distributes production Knowledge Pack."""
    def publish_pack(self, context: PipelineContext, audited_pack: Dict[str, Any]) -> StageResult:
        ...


# --- FACTORY PIPELINE ORCHESTRATOR ---

class IFactoryPipelineRunner(Protocol):
    """Orchestrates end-to-end execution of Stages 01 through 08."""
    
    def run_full_pipeline(self, context: PipelineContext, source_manifest: Dict[str, Any]) -> StageResult:
        ...

    def run_stage(self, stage_id: str, context: PipelineContext, input_payload: Dict[str, Any]) -> StageResult:
        ...
```
