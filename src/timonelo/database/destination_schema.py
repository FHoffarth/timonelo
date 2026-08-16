"""
Destination Intelligence Schema and Domain Models for Timonelo (Chapter III - Sprint 05).
Provides practical operational logistics for arrival airports, transfers, cruise terminals,
recommended hotel zones, public transit cards, emergency contacts, and Negative Intelligence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class PowerPlugType(str, Enum):
    TYPE_A = "TYPE_A (US/Japan 2-pin)"
    TYPE_C_F = "TYPE_C/F (European Europlug/Schuko 230V)"
    TYPE_G = "TYPE_G (UK 3-pin 230V)"
    TYPE_I = "TYPE_I (Australia/China 220V)"
    MULTI = "MULTI_TYPE"


@dataclass(frozen=True)
class AirportTransferOption:
    airport_name: str
    iata_code: str
    distance_to_terminal_km: float
    best_transit_mode: str
    typical_duration_min: int
    estimated_cost_range: str
    negative_intelligence: str
    evidence_source: str


@dataclass(frozen=True)
class CruiseTerminalLayout:
    terminal_name: str
    berths: List[str]
    porter_dropoff_location: str
    security_lane_notes: str
    distance_to_city_center_km: float
    nearest_metro_or_train: str
    negative_intelligence: str


@dataclass(frozen=True)
class DestinationIntelligence:
    port_slug: str
    city_name: str
    country: str
    primary_language: str
    currency: str
    timezone: str
    power_plugs: PowerPlugType
    sim_esim_recommendation: str
    emergency_phone_police: str
    emergency_phone_medical: str
    local_transport_card: str
    airports: List[AirportTransferOption]
    terminals: List[CruiseTerminalLayout]
    recommended_hotel_zones: List[str]
    negative_intelligence_top_3: List[str]
    evidence_sources: List[str]
    confidence_score: float = 98.0
    unknown_fields: List[str] = field(default_factory=list)
