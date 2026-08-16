"""
Normalized Cruise Intelligence Schema & Types.
Defines strict entities for Ships, Ship Classes, Decks, Cabins, Venues, Ports, Terminals, Routes, and Sources.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any


class TrustLevel(str, Enum):
    OFFICIAL = "OFFICIAL"          # From Cruise Line, Yard, Port Authority, IMO/GISIS
    VERIFIED = "VERIFIED"          # Field-audited, crew-corroborated, multi-source triangulated
    COMMUNITY = "COMMUNITY"        # Passenger reports, community observation
    UNKNOWN = "UNKNOWN"            # Missing/unverified (explicit omission over guessing)


class IntelligenceLevel(IntEnum):
    LEVEL_0_REGISTERED = 0        # Basic identity only
    LEVEL_1_TECHNICAL = 1         # Dimensions, builder, capacity, operator
    LEVEL_2_DECK_ARCH = 2         # Deck hierarchy, public areas, vertical circulation
    LEVEL_3_CABIN_INTEL = 3       # Cabin catalogue, view profile, noise profile, accessibility
    LEVEL_4_VENUE_INTEL = 4       # Restaurants, bars, pools, spa, walking distances
    LEVEL_5_OPERATIONAL = 5       # Embarkation, gangway, safety drill, terminal logistics
    LEVEL_6_PASSENGER = 6         # FAQs, negative intelligence, practical avoidance advice
    LEVEL_7_VERIFIED_TWIN = 7     # Crew verified, field audited, reference quality digital twin


@dataclass(frozen=True)
class ProvenanceValue:
    value: Any
    trust_level: TrustLevel = TrustLevel.OFFICIAL
    source_id: Optional[str] = None
    confidence: float = 1.0
    retrieved_at: Optional[str] = None


@dataclass(frozen=True)
class NegativeIntelligenceEntry:
    id: str
    title: str
    category: str  # "ACOUSTIC", "ELEVATOR_CONGESTION", "EMBARKATION", "ROAMING", "HEAT_EXPOSURE", "VIEW_OBSTRUCTION"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    impact: str
    mitigation: str
    verification_type: str = "FIELD_AUDITED"
    evidence: str = ""


@dataclass
class ShipEntity:
    slug: str
    name: ProvenanceValue
    imo: ProvenanceValue
    operator: ProvenanceValue
    ship_class: ProvenanceValue
    class_id: str
    mmsi: Optional[ProvenanceValue] = None
    call_sign: Optional[ProvenanceValue] = None
    flag_state: Optional[ProvenanceValue] = None
    builder: Optional[ProvenanceValue] = None
    delivery_date: Optional[ProvenanceValue] = None
    dimensions: Dict[str, ProvenanceValue] = field(default_factory=dict)
    capacities: Dict[str, ProvenanceValue] = field(default_factory=dict)
    signature_venues: List[str] = field(default_factory=list)
    homeports: List[str] = field(default_factory=list)
    intelligence_level: IntelligenceLevel = IntelligenceLevel.LEVEL_1_TECHNICAL
    negative_intelligence: List[NegativeIntelligenceEntry] = field(default_factory=list)


@dataclass
class CabinEntity:
    cabin_number: str
    ship_slug: str
    deck_number: int
    deck_name: str
    category: str
    hull_side: str  # "PORT", "STARBOARD", "CENTER"
    zone: str       # "FORWARD", "MIDSHIP", "AFT"
    square_meters: float
    balcony_sqm: float = 0.0
    nearest_lift_m: float = 0.0
    nearest_stairs_m: float = 0.0
    noise_risk: str = "CALM"  # "CALM", "LOW_PANTRY", "MID_ELEVATOR", "HIGH_VENUE_OVERHEAD"
    view_category: str = "UNOBSTRUCTED"  # "UNOBSTRUCTED", "PARTIALLY_OBSTRUCTED", "INTERIOR"
    step_free_accessible: bool = False
    connecting_cabin: Optional[str] = None
    vertical_neighbors: Dict[str, str] = field(default_factory=dict)  # {"deck_above": "...", "deck_below": "..."}
    trust_level: TrustLevel = TrustLevel.OFFICIAL


@dataclass
class VenueEntity:
    slug: str
    name: str
    ship_slug: str
    deck_number: int
    deck_name: str
    venue_type: str  # "RESTAURANT", "BAR", "THEATRE", "POOL", "SPA", "PROMENADE", "LOUNGE", "KIDS_CLUB"
    category: str    # "INCLUDED", "SPECIALTY", "PUBLIC_SANCTUARY", "WELLNESS"
    capacity: Optional[int] = None
    opening_context: str = "All Day"
    noise_level: str = "MODERATE"  # "QUIET", "MODERATE", "VIBRANT", "LIVELY"
    step_free_access: bool = True
    dress_code: str = "Casual"
    signature_features: List[str] = field(default_factory=list)
    nearest_lift: str = "Midship Panoramic Elevators"
    trust_level: TrustLevel = TrustLevel.OFFICIAL


@dataclass
class PortEntity:
    slug: str
    name: str
    un_locode: str
    country: str
    region: str
    coordinates: Dict[str, float]
    timezone: str
    terminals: List[Dict[str, Any]] = field(default_factory=list)
    logistics: Dict[str, Any] = field(default_factory=dict)
    negative_intelligence: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RouteEntity:
    slug: str
    title: str
    region: str
    duration_days: int
    ports_sequence: List[Dict[str, Any]] = field(default_factory=list)
    common_operators: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ShipClassEntity:
    slug: str
    name: str
    operator: str
    category: str
    builder_shipyard: str
    lead_ship_name: str
    lead_ship_year: int
    gross_tonnage_typical: int
    length_m_typical: float
    beam_m_typical: float
    passenger_capacity_max: int
    description: str
    sister_ships: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


@dataclass
class SourceRecord:
    source_id: str
    category: str
    title: str
    url: str
    license_type: str
    verified_fields: List[str] = field(default_factory=list)
    retrieved_at: str = ""
