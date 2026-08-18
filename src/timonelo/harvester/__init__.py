"""
src/timonelo/harvester/__init__.py

Official Source Harvester v0.1:
Automated discovery, verification, fingerprinting, and registration of primary source documents.
"""

from timonelo.harvester.models import (
    SourceTrustTier, DocumentType, HarvestState, HarvestedArtifactRecord, VersionRecord
)
from timonelo.harvester.config import MSC_SOURCE_CONFIG, classify_domain_tier
from timonelo.harvester.vessel_resolver import resolve_vessel
from timonelo.harvester.classifier import classify_document
from timonelo.harvester.verifier import verify_pdf_bytes, compute_bytes_sha256
from timonelo.harvester.vault import EvidenceVault
from timonelo.harvester.registry import SourceRegistry
from timonelo.harvester.fetcher import ArtifactFetcher
from timonelo.harvester.discovery import DiscoveryEngine
from timonelo.harvester.engine import HarvestEngine, HarvestRunReport

__all__ = [
    "SourceTrustTier", "DocumentType", "HarvestState", "HarvestedArtifactRecord", "VersionRecord",
    "MSC_SOURCE_CONFIG", "classify_domain_tier", "resolve_vessel", "classify_document",
    "verify_pdf_bytes", "compute_bytes_sha256", "EvidenceVault", "SourceRegistry",
    "ArtifactFetcher", "DiscoveryEngine", "HarvestEngine", "HarvestRunReport"
]
