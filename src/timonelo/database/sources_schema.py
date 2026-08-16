"""
Source Network Schema for Timonelo.
Every fact in Timonelo must have provenance, access methodology, update frequency, and trust rating.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class SourceCategory(str, Enum):
    IMO_GISIS = "IMO_GISIS"
    CLASSIFICATION_SOCIETY = "CLASSIFICATION_SOCIETY"
    GOVERNMENT_MARITIME = "GOVERNMENT_MARITIME"
    SHIPYARD = "SHIPYARD"
    CRUISE_LINE = "CRUISE_LINE"
    PORT_AUTHORITY = "PORT_AUTHORITY"
    WEATHER_METEOROLOGY = "WEATHER_METEOROLOGY"
    AIS_COAST_GUARD = "AIS_COAST_GUARD"
    TRANSIT_AUTHORITY = "TRANSIT_AUTHORITY"
    FIELD_INSPECTION = "FIELD_INSPECTION"


class AccessMethod(str, Enum):
    API = "API"
    PDF = "PDF"
    HTML = "HTML"
    CSV = "CSV"
    MANUAL = "MANUAL"
    SCRAPING = "SCRAPING"


@dataclass(frozen=True)
class SourceEntity:
    source_id: str
    name: str
    owner: str
    category: SourceCategory
    website: str
    country: str
    jurisdiction: str
    licence: str
    terms: str
    access_method: AccessMethod
    allowed_usage: str
    update_frequency: str
    last_retrieved: str
    freshness_days: int
    priority: int
    trust_score: float
    entities_served_count: int = 1
