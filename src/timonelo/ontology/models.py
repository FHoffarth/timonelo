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


class Method(str, Enum):
    """ADR-0002 §6.1 — how the statement was produced."""
    DIRECT = "DIRECT"
    CALCULATED = "CALCULATED"
    INFERRED = "INFERRED"


class Derivation(str, Enum):
    """ADR-0002 §6.2 — where the inputs originated. Orthogonal to Method."""
    LOCAL = "LOCAL"
    SISTER_SHIP = "SISTER_SHIP"
    REFERENCE_MODEL = "REFERENCE_MODEL"
    GENERATED = "GENERATED"


class EvidenceCondition(str, Enum):
    """Machine evidence state. Grounded in observations, independent of human review or publication gate."""
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"


class HumanReviewState(str, Enum):
    """Human review workflow state. Tracks curation lifecycle independently from evidence or publication."""
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class PublishStatus(str, Enum):
    """Publication gate status. Controls whether an item may be exposed to passengers or downstream systems."""
    PUBLISH_ALLOWED = "PUBLISH_ALLOWED"
    PUBLISH_ALLOWED_WITH_WARNINGS = "PUBLISH_ALLOWED_WITH_WARNINGS"
    PUBLISH_BLOCKED = "PUBLISH_BLOCKED"


class GeometryProvenance(str, Enum):
    """Canonical spatial geometry provenance."""
    DIRECT_SOURCE_GEOMETRY = "DIRECT_SOURCE_GEOMETRY"
    TRANSFORMED_SOURCE_GEOMETRY = "TRANSFORMED_SOURCE_GEOMETRY"
    DERIVED_GEOMETRY = "DERIVED_GEOMETRY"
    SYNTHETIC_GEOMETRY = "SYNTHETIC_GEOMETRY"
    UNKNOWN_PROVENANCE = "UNKNOWN_PROVENANCE"


@dataclass(frozen=True)
class EvidenceLink:
    """Reference to the observation event that produced a value.

    Governed by ADR-0002. This is the trust boundary of the entire engine:
    ~15,090 records depend on it. Every field must therefore be mechanically
    verifiable — no manually invented values, no decorative defaults, no
    placeholder identifiers.

    `sha256` is deliberately Optional and defaults to None. It may ONLY be
    populated with a digest actually computed from the referenced artifact's
    bytes. Every sha256 currently in the knowledge base is a hand-typed hex
    pattern (a1b2c3..., 9c8b7a... and rotations); two values account for
    15,048 of 15,090 links. No source document has ever been hashed. A
    placeholder in this field is worse than an empty one: it makes an
    unverifiable claim look verified.

    Fields merged here from the former database.evidence.EvidenceField, which
    was never referenced anywhere in the codebase and has been deleted. A
    dormant trust abstraction invites divergence from the real one.
    """
    source_id: str
    locator: str  # e.g., "GA_Drawing_Rev4_Page14" or "Survey_Photo_IMG_8921"

    # Only ever a digest of bytes actually held. None = no artifact possessed.
    sha256: Optional[str] = None

    # Origin axes (ADR-0002 §6). None until the statement is classified.
    method: Optional[Method] = None
    derivation: Optional[Derivation] = None

    # Canonical evidence condition and review workflow
    evidence_condition: EvidenceCondition = EvidenceCondition.UNKNOWN
    human_review_state: HumanReviewState = HumanReviewState.DRAFT

    # Provenance detail.
    evidence_type: Optional[str] = None
    observed_on: Optional[str] = None
    reviewer: Optional[str] = None

    # Temporal validity (ADR-0002 §7.2).
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    refit_version: Optional[str] = None

    def __post_init__(self) -> None:
        if self.sha256 is not None:
            v = self.sha256
            if len(v) != 64 or not all(c in "0123456789abcdef" for c in v.lower()):
                raise ValueError(
                    f"EvidenceLink.sha256 for {self.source_id!r} is not a valid "
                    "SHA-256 digest. Supply a digest computed from the artifact's "
                    "bytes, or leave it None."
                )
            if v == "0" * 64:
                raise ValueError(
                    f"EvidenceLink.sha256 for {self.source_id!r} is the all-zero "
                    "placeholder. Leave it None instead."
                )

    @property
    def is_content_addressed(self) -> bool:
        """True only if a real digest of a possessed artifact is attached."""
        return self.sha256 is not None


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
