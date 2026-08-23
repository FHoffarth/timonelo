"""
Knowledge Factory Core Engine Package (ADR-0001).
Automated compilation pipeline from raw ship manifests to verified spatial twins.
"""

from .manifest_importer import ManifestImporter, CabinManifestRecord
from .corridor_generator import CorridorMeshGenerator
from .validator import SpatialIntegrityValidator, ValidationReport
from .compiler import KnowledgeFactoryCompiler
from .voyage import (
    AdmissionDecision,
    AdmissionStatus,
    ParsedVoyageClaim,
    PassengerTripKnowledgePack,
    VoyageGapRecord,
    VoyageIntakeInput,
    VoyageKnowledgeFactory,
    VoyageKnowledgeResult,
)

__all__ = [
    "ManifestImporter",
    "CabinManifestRecord",
    "CorridorMeshGenerator",
    "SpatialIntegrityValidator",
    "ValidationReport",
    "KnowledgeFactoryCompiler",
    "AdmissionDecision",
    "AdmissionStatus",
    "ParsedVoyageClaim",
    "PassengerTripKnowledgePack",
    "VoyageGapRecord",
    "VoyageIntakeInput",
    "VoyageKnowledgeFactory",
    "VoyageKnowledgeResult",
]
