"""
Plane 6: Cruise Intelligence Runtime Models (ADR-0001 / DECISION_FIRST.md).
Immutable, technology-agnostic dataclasses representing the unified Cruise Briefing.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from timonelo.ontology.models import EvidenceLink


class DecisionUrgency(str, Enum):
    CRITICAL_SAFETY = "CRITICAL_SAFETY"
    TIME_SENSITIVE = "TIME_SENSITIVE"
    COMFORT_OPTIMIZATION = "COMFORT_OPTIMIZATION"
    CALM_INFORMATIONAL = "CALM_INFORMATIONAL"


class PortDockingType(str, Enum):
    PIER_BERTH = "PIER_BERTH"
    OFFSHORE_TENDER = "OFFSHORE_TENDER"
    AT_SEA = "AT_SEA"


@dataclass(frozen=True)
class NegativeIntelligenceAction:
    """A specific costly mistake or friction prevented by Timonelo before it happens."""
    regret_prevented: str
    calm_guidance: str
    category: str
    evidence_source_id: str


@dataclass(frozen=True)
class CabinIntelligence:
    """Briefing section for stateroom orientation and physical surroundings."""
    cabin_number: str
    deck_number: int
    deck_name: str
    hull_side: str
    zone: str
    category_name: str
    nearest_elevator_core: str
    steps_to_elevator: int
    vertical_sandwich_status: str
    is_quiet_tier: bool
    balcony_sightline_summary: str
    power_socket_summary: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class EmbarkationIntelligence:
    """Briefing section for terminal arrival and boarding assurance."""
    terminal_name: str
    pier_number: str
    luggage_drop_window: str
    stateroom_ready_time: str
    mandatory_safety_drill_deadline: str
    assigned_muster_station: str
    muster_station_deck: int
    step_free_muster_route: str
    boarding_pass_requirement: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class PortIntelligence:
    """Briefing section for shoreside navigation, port logistics, and tender safety."""
    port_name: str
    country: str
    docking_type: PortDockingType
    gangway_deck: int
    gangway_location: str
    all_aboard_time: str
    last_tender_time: Optional[str]
    town_distance_meters: int
    is_walkable_to_center: bool
    walking_route_summary: str
    official_taxi_fare_notes: str
    local_emergency_phone: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class WeatherIntelligence:
    """Briefing section for maritime sea state, motion prediction, and solar position."""
    weather_summary: str
    air_temperature_celsius: float
    sea_swell_meters: float
    beaufort_scale: int
    motion_risk_level: str
    ship_stabilizer_status: str
    sunrise_time: str
    sunset_time: str
    sun_side_docked: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class VisaIntelligence:
    """Briefing section for sovereign entry, customs, and passport compliance."""
    destination_country: str
    passport_validity_required_months: int
    visa_required_for_passengers: bool
    visa_notes: str
    currency_import_limit_notes: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class DiningIntelligence:
    """Briefing section for evening culinary decisions and venue proximity."""
    assigned_main_restaurant: str
    restaurant_deck: int
    evening_dress_code: str
    walking_meters_from_cabin: float
    walking_seconds: int
    is_step_free: bool
    marketplace_buffet_status: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class AccessibilityIntelligence:
    """Briefing section for reduced mobility and step-free travel assurance."""
    cabin_is_accessible_certified: bool
    door_clear_width_mm: int
    has_step_free_access_to_gangway: bool
    tender_boat_accessibility_status: str
    nearest_accessible_restroom_deck: int
    summary: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class TravelIntelligence:
    """Briefing section for local currency, tipping etiquette, and connectivity."""
    local_currency_code: str
    local_currency_name: str
    card_acceptance_status: str
    tipping_etiquette: str
    time_zone_difference_vs_ship: str
    offline_roaming_advice: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)


@dataclass(frozen=True)
class DecisionItem:
    """A prioritized, actionable decision resolution for the traveler today."""
    title: str
    recommendation: str
    rationale: str
    urgency: DecisionUrgency
    regret_avoided: str


@dataclass(frozen=True)
class DecisionSummary:
    """The constitutional 'Three Things That Matter Today' resolution."""
    headline: str
    calm_perspective: str
    core_decisions: List[DecisionItem]
    decisions_avoided: List[NegativeIntelligenceAction]


@dataclass(frozen=True)
class CruiseBriefing:
    """
    The master Plane 6 Cruise Intelligence Runtime Container.
    Synthesizes all intelligence planes into a single, cohesive, calm decision briefing.
    """
    briefing_id: str
    ship_name: str
    ship_imo: str
    itinerary_day: int
    date_iso: str
    cabin_intelligence: CabinIntelligence
    embarkation_intelligence: EmbarkationIntelligence
    port_intelligence: PortIntelligence
    weather_intelligence: WeatherIntelligence
    visa_intelligence: VisaIntelligence
    dining_intelligence: DiningIntelligence
    accessibility_intelligence: AccessibilityIntelligence
    travel_intelligence: TravelIntelligence
    decision_summary: DecisionSummary
    evidence_manifest: List[EvidenceLink] = field(default_factory=list)
