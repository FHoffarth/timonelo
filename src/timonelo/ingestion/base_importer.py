"""
Base Importer Interface for the Cruise Knowledge Factory.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import datetime


class SourceCategory(str, Enum):
    OFFICIAL_CRUISE_LINE = "OFFICIAL_CRUISE_LINE"
    OFFICIAL_SHIPYARD = "OFFICIAL_SHIPYARD"
    OFFICIAL_PORT_AUTHORITY = "OFFICIAL_PORT_AUTHORITY"
    OFFICIAL_MARITIME_REGULATOR = "OFFICIAL_MARITIME_REGULATOR"  # IMO, ITU, Class Societies
    PUBLIC_ITINERARY = "PUBLIC_ITINERARY"
    COMMUNITY_CONTRIBUTOR = "COMMUNITY_CONTRIBUTOR"


@dataclass(frozen=True)
class RawPayload:
    source_id: str
    source_name: str
    category: SourceCategory
    source_url: str
    license_note: str
    retrieval_timestamp: str
    confidence: float
    payload: Dict[str, Any]
    sha256_checksum: str


class BaseImporter(ABC):
    """Abstract base class for all lawful, provenanced maritime importers."""

    def __init__(self, source_id: str, source_name: str, category: SourceCategory, license_note: str):
        self.source_id = source_id
        self.source_name = source_name
        self.category = category
        self.license_note = license_note

    @abstractmethod
    def ingest_payload(self, raw_data: Dict[str, Any], source_url: str, confidence: float = 1.0) -> RawPayload:
        """Ingest and seal raw data payload with provenance metadata."""
        pass

    @abstractmethod
    def extract_entities(self, payload: RawPayload) -> Dict[str, List[Dict[str, Any]]]:
        """Extract candidate normalized entities (ships, ports, venues, routes)."""
        pass
