"""
Spatial Calculus Sandwich Resolver (Plane 3 per ADR-0001).
Determines 3D vertical spatial adjacencies (Ceiling on Deck N+1 and Floor on Deck N-1) for staterooms.
"""

from dataclasses import dataclass
from typing import List, Optional
from ..ontology.models import VesselSpatialOntology, Cabin, Venue, DeckVerticalZone, VenueCategory


@dataclass(frozen=True)
class VerticalLayerReport:
    deck_number: int
    deck_name: str
    zone: DeckVerticalZone
    intersecting_venues: List[str]
    is_residential_cabins_only: bool
    is_active_noise_generator: bool


@dataclass(frozen=True)
class CabinSandwichReport:
    cabin_number: str
    cabin_deck_number: int
    overhead_layer: Optional[VerticalLayerReport]
    underfoot_layer: Optional[VerticalLayerReport]
    is_acoustically_insulated_sandwich: bool


class DeterministicSandwichResolver:
    """Computes vertical structural layer intersections directly above and below a stateroom."""

    def __init__(self, ontology: VesselSpatialOntology):
        self.ontology = ontology

    def resolve_cabin_sandwich(self, cabin_number: str) -> Optional[CabinSandwichReport]:
        # 1. Locate cabin
        target_cabin: Optional[Cabin] = None
        target_deck_num: Optional[int] = None
        for deck_num, deck in self.ontology.decks.items():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                target_deck_num = deck_num
                break

        if not target_cabin or target_deck_num is None:
            return None

        # 2. Resolve Deck N+1 (Overhead)
        overhead_report = self._resolve_deck_layer(target_deck_num + 1, target_cabin)
        
        # 3. Resolve Deck N-1 (Underfoot)
        underfoot_report = self._resolve_deck_layer(target_deck_num - 1, target_cabin)

        # 4. Acoustic insulation status (true if both overhead and underfoot are pure residential cabins)
        # `is` True, not truthiness: is_residential_cabins_only may be None
        # (UNKNOWN), and None must never satisfy an acoustic-comfort claim.
        is_insulated = (
            overhead_report is not None
            and overhead_report.is_residential_cabins_only is True
            and underfoot_report is not None
            and underfoot_report.is_residential_cabins_only is True
        )

        return CabinSandwichReport(
            cabin_number=cabin_number,
            cabin_deck_number=target_deck_num,
            overhead_layer=overhead_report,
            underfoot_layer=underfoot_report,
            is_acoustically_insulated_sandwich=is_insulated,
        )

    def _resolve_deck_layer(self, deck_number: int, cabin: Cabin) -> Optional[VerticalLayerReport]:
        if deck_number not in self.ontology.decks:
            return None

        deck = self.ontology.decks[deck_number]
        # Check intersecting venues on that deck
        intersecting: List[str] = []
        has_noise = False

        for venue_id, venue in deck.venues.items():
            # Check 2D bounding box longitudinal overlap (X axis)
            cabin_min_x = min(p.x for p in cabin.boundary_polygon)
            cabin_max_x = max(p.x for p in cabin.boundary_polygon)
            venue_min_x = min(p.x for p in venue.boundary_polygon)
            venue_max_x = max(p.x for p in venue.boundary_polygon)

            if not (cabin_max_x < venue_min_x or cabin_min_x > venue_max_x):
                intersecting.append(venue.name)
                if venue.is_noise_generator:
                    has_noise = True

        # ADR-0002 I3: absence of modelled venues is NOT evidence of absence.
        # A deck with no venue coverage is UNKNOWN, never "pure residential".
        # Reporting an unmodelled deck as quiet is the single most dangerous
        # inference in the engine: it converts missing data into reassurance.
        deck_has_venue_coverage = len(deck.venues) > 0
        if not deck_has_venue_coverage:
            is_residential = None   # UNKNOWN
        else:
            is_residential = len(deck.cabins) > 0 and len(intersecting) == 0

        return VerticalLayerReport(
            deck_number=deck_number,
            deck_name=deck.name,
            zone=deck.zone,
            intersecting_venues=intersecting,
            is_residential_cabins_only=is_residential,
            is_active_noise_generator=has_noise,
        )
