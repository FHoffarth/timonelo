"""
Spatial Ontology Models (Plane 2 per ADR-0001).
Strict, immutable data structures representing vessel geometry, topology, and physical fixtures.
Contains zero human opinions, zero subjective ratings, and zero walking times.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any


class HullSide(str, Enum):
    PORT = "PORT"          # Even numbers
    STARBOARD = "STARBOARD"# Odd numbers
    CENTERLINE = "CENTERLINE"


class DeckVerticalZone(str, Enum):
    HULL_LOWER = "HULL_LOWER"          # Below main passenger decks
    RESIDENTIAL_LOWER = "RESIDENTIAL_LOWER" # Decks 08-11
    RESIDENTIAL_UPPER = "RESIDENTIAL_UPPER" # Decks 12-14
    PROMENADE = "PROMENADE"            # Decks 06-07
    LIDO_SPORTS = "LIDO_SPORTS"        # Decks 15-19


class VenueCategory(str, Enum):
    DINING = "DINING"
    BUFFET = "BUFFET"
    BAR_LOUNGE = "BAR_LOUNGE"
    THEATER = "THEATER"
    POOL_SOLARIUM = "POOL_SOLARIUM"
    SPA_FITNESS = "SPA_FITNESS"
    YOUTH_KIDS = "YOUTH_KIDS"
    ELEVATOR_LOBBY = "ELEVATOR_LOBBY"
    SERVICE_PANTRY = "SERVICE_PANTRY"
    PROMENADE_ATRIUM = "PROMENADE_ATRIUM"


class BalconyType(str, Enum):
    UNOBSTRUCTED = "UNOBSTRUCTED"
    PARTIAL_OBSTRUCTION_LIFEBOAT = "PARTIAL_OBSTRUCTION_LIFEBOAT"
    FULL_OBSTRUCTION_LIFEBOAT = "FULL_OBSTRUCTION_LIFEBOAT"
    METAL_SOLID_RAILING = "METAL_SOLID_RAILING"
    GLASS_TRANSPARENT_RAILING = "GLASS_TRANSPARENT_RAILING"
    NO_BALCONY = "NO_BALCONY"


@dataclass(frozen=True)
class Coordinate2D:
    x: float  # Normalized [0.0 (Aft) -> 1.0 (Bow)]
    y: float  # Normalized [-1.0 (Port) -> +1.0 (Starboard)]


@dataclass(frozen=True)
class Coordinate3D:
    x: float
    y: float
    deck_number: int


@dataclass(frozen=True)
class EvidenceLink:
    source_id: str
    sha256: str
    locator: str  # e.g., "GA_Drawing_Rev4_Page14" or "Survey_Photo_IMG_8921"


@dataclass(frozen=True)
class PowerSocketMatrix:
    eu_standard_count: int
    us_standard_count: int
    usb_a_count: int
    usb_c_count: int
    bedside_usb_available: bool


@dataclass(frozen=True)
class DoorNode:
    door_id: str
    deck_number: int
    coordinate: Coordinate2D
    corridor_snap_node_id: str
    clear_width_mm: int = 850


@dataclass(frozen=True)
class Cabin:
    cabin_number: str
    deck_number: int
    hull_side: HullSide
    category_code: str
    boundary_polygon: List[Coordinate2D]
    door: DoorNode
    square_meters: float
    balcony_type: BalconyType
    sockets: PowerSocketMatrix
    connecting_cabin_number: Optional[str] = None
    bed_near_balcony: Optional[bool] = None
    is_accessible_stateroom: bool = False
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class Venue:
    venue_id: str
    name: str
    deck_number: int
    category: VenueCategory
    boundary_polygon: List[Coordinate2D]
    entrance_node_ids: List[str]
    is_noise_generator: bool
    is_open_deck: bool
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class CorridorNode:
    node_id: str
    deck_number: int
    coordinate: Coordinate2D
    is_elevator_lobby: bool = False
    is_stairwell_access: bool = False
    is_step_free: bool = True
    vertical_core_id: Optional[str] = None


@dataclass(frozen=True)
class CorridorEdge:
    from_node_id: str
    to_node_id: str
    distance_meters: float
    is_step_free: bool = True
    is_exterior_weather_deck: bool = False


@dataclass(frozen=True)
class Deck:
    deck_number: int
    name: str
    elevation_meters: float
    perimeter_polygon: List[Coordinate2D]
    zone: DeckVerticalZone
    cabins: Dict[str, Cabin] = field(default_factory=dict)
    venues: Dict[str, Venue] = field(default_factory=dict)
    corridor_nodes: Dict[str, CorridorNode] = field(default_factory=dict)
    corridor_edges: List[CorridorEdge] = field(default_factory=list)


@dataclass(frozen=True)
class VesselSpatialOntology:
    imo_number: str
    name: str
    ship_class: str
    length_overall_meters: float
    beam_meters: float
    total_decks: int
    decks: Dict[int, Deck] = field(default_factory=dict)
