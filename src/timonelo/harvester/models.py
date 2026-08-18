"""
src/timonelo/harvester/models.py

Data models for the Official Source Harvester v0.1:
- SourceTrustTier (TIER_A, TIER_B, TIER_C)
- DocumentType (DECK_PLAN, UNKNOWN)
- HarvestState lifecycle
- HarvestedArtifactRecord (Registry item with explicit Origin Provenance)
- VersionRecord (Version candidate tracking)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class SourceTrustTier(str, Enum):
    TIER_A = "TIER_A"  # Direct Official MSC Primary Domain
    TIER_B = "TIER_B"  # Official MSC Asset / CDN Host with verified provenance
    TIER_C = "TIER_C"  # Third-party / Mirror / Cruise Portal (Discovery hint only, never official primary)


class DocumentType(str, Enum):
    DECK_PLAN = "DECK_PLAN"
    UNKNOWN = "UNKNOWN"


class HarvestState(str, Enum):
    # Positive Lifecycle States
    DISCOVERED = "DISCOVERED"
    FETCHED = "FETCHED"
    FILE_VALID = "FILE_VALID"
    OFFICIAL_DOMAIN_VERIFIED = "OFFICIAL_DOMAIN_VERIFIED"
    FINGERPRINTED = "FINGERPRINTED"
    CLASSIFIED = "CLASSIFIED"
    VESSEL_MATCHED = "VESSEL_MATCHED"
    REGISTERED = "REGISTERED"

    # Negative / Exceptional States
    ROBOTS_BLOCKED = "ROBOTS_BLOCKED"
    HTTP_FAILED = "HTTP_FAILED"
    NOT_A_PDF = "NOT_A_PDF"
    CORRUPT_FILE = "CORRUPT_FILE"
    UNKNOWN_PUBLISHER = "UNKNOWN_PUBLISHER"
    DUPLICATE = "DUPLICATE"
    VESSEL_UNRESOLVED = "VESSEL_UNRESOLVED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    VERSION_CANDIDATE = "VERSION_CANDIDATE"


class OriginVerificationStatus(str, Enum):
    LIVE_VERIFIED = "LIVE_VERIFIED"
    CANDIDATE_ONLY = "CANDIDATE_ONLY"
    FIXTURE_ONLY = "FIXTURE_ONLY"
    FAILED = "FAILED"


class DiscoveryMethod(str, Enum):
    SITEMAP = "SITEMAP"
    INTERNAL_LINK = "INTERNAL_LINK"
    KNOWN_PATTERN = "KNOWN_PATTERN"
    SEARCH_HINT = "SEARCH_HINT"
    LOCAL_FIXTURE = "LOCAL_FIXTURE"


@dataclass
class HarvestedArtifactRecord:
    source_id: str
    cruise_line_id: str
    vessel_id: Optional[str]
    document_type: DocumentType
    title: str
    publisher: str
    language: str
    edition: Optional[str]
    source_url: str
    final_url: str
    retrieved_at: str
    sha256: str
    file_size_bytes: int
    page_count: int
    mime_type: str
    source_tier: SourceTrustTier
    verification_status: str  # "VERIFIED_OFFICIAL_SOURCE" | "UNVERIFIED_THIRD_PARTY"
    vault_path: str
    discovery_method: str = "LOCAL_FIXTURE"
    origin_verification_status: str = "FIXTURE_ONLY"
    origin_verified_at: Optional[str] = None
    origin_page_url: Optional[str] = None
    download_url: Optional[str] = None
    retrieval_history: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["document_type"] = self.document_type.value
        d["source_tier"] = self.source_tier.value
        return d


@dataclass
class VersionRecord:
    document_family: str
    vessel_id: str
    artifact_sha256: str
    edition: Optional[str]
    retrieved_at: str
    status: str = "CURRENT_CANDIDATE"  # CURRENT_CANDIDATE | SUPERSEDED | DUPLICATE

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
