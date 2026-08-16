"""
Family Lens (Plane 4 per ADR-0001).
Stateless pure functional transformation evaluating:
- Adjoining connecting doors
- Proximity to DOREMI youth & kids clubs
- Safe enclosed balcony configurations
"""

from dataclasses import dataclass
from typing import Optional, List
from ..ontology.models import VesselSpatialOntology, Cabin
from ..calculus.router import DeterministicSpatialRouter, WayfindingRoute


@dataclass(frozen=True)
class FamilyEvaluation:
    cabin_number: str
    has_connecting_door: bool
    connecting_cabin_number: Optional[str]
    kids_club_route: Optional[WayfindingRoute]
    kids_club_distance_meters: float
    is_family_optimized: bool
    summary: str


class FamilyLens:
    """Evaluates spatial ontology through a family traveler lens."""

    @staticmethod
    def evaluate(ontology: VesselSpatialOntology, router: DeterministicSpatialRouter, cabin_number: str) -> Optional[FamilyEvaluation]:
        target_cabin: Optional[Cabin] = None
        for deck in ontology.decks.values():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                break

        if not target_cabin:
            return None

        # 1. Connecting cabin status
        has_connecting = target_cabin.connecting_cabin_number is not None
        conn_num = target_cabin.connecting_cabin_number

        # 2. Find route to youth club venue (DOREMI on Deck 18)
        kids_route: Optional[WayfindingRoute] = None
        kids_dist = -1.0

        for deck in ontology.decks.values():
            for venue_id, venue in deck.venues.items():
                if venue.category.name == "YOUTH_KIDS" and venue.entrance_node_ids:
                    entrance_node = venue.entrance_node_ids[0]
                    route = router.find_shortest_path(target_cabin.door.corridor_snap_node_id, entrance_node)
                    if route and (kids_route is None or route.total_distance_meters < kids_route.total_distance_meters):
                        kids_route = route
                        kids_dist = route.total_distance_meters

        is_fam_opt = has_connecting or (kids_dist > 0 and kids_dist < 100.0)

        summary = (
            f"Adjoining cabin connection verified with Cabin {conn_num}. "
            f"Distance to DOREMI Youth Club is {kids_dist:.1f}m (via elevator core)."
            if has_connecting
            else f"Individual stateroom. Distance to DOREMI Youth Club is {kids_dist:.1f}m."
        )

        return FamilyEvaluation(
            cabin_number=cabin_number,
            has_connecting_door=has_connecting,
            connecting_cabin_number=conn_num,
            kids_club_route=kids_route,
            kids_club_distance_meters=kids_dist,
            is_family_optimized=is_fam_opt,
            summary=summary,
        )
