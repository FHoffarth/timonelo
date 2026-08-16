"""
Quiet Cabin Lens (Plane 4 per ADR-0001).
Stateless pure functional transformation evaluating acoustic context:
- Overhead noise sandwich (buffets, galleys, nightclubs, open decks)
- Distance from high-traffic elevator lobbies
- Service pantry adjacency
"""

from dataclasses import dataclass
from typing import Optional, List
from ..ontology.models import VesselSpatialOntology, Cabin
from ..calculus.sandwich import DeterministicSandwichResolver, CabinSandwichReport
from ..calculus.router import DeterministicSpatialRouter


@dataclass(frozen=True)
class QuietCabinEvaluation:
    cabin_number: str
    is_quiet_tier: bool
    sandwich_report: Optional[CabinSandwichReport]
    elevator_lobby_distance_meters: float
    acoustic_flags: List[str]
    summary: str


class QuietCabinLens:
    """Evaluates spatial ontology through an acoustic sensitivity lens."""

    @staticmethod
    def evaluate(
        ontology: VesselSpatialOntology,
        sandwich_resolver: DeterministicSandwichResolver,
        router: DeterministicSpatialRouter,
        cabin_number: str,
    ) -> Optional[QuietCabinEvaluation]:
        target_cabin: Optional[Cabin] = None
        for deck in ontology.decks.values():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                break

        if not target_cabin:
            return None

        # 1. Sandwich analysis
        sandwich = sandwich_resolver.resolve_cabin_sandwich(cabin_number)
        flags: List[str] = []

        if sandwich and sandwich.overhead_layer:
            if sandwich.overhead_layer.is_active_noise_generator:
                flags.append(f"Overhead venue: {', '.join(sandwich.overhead_layer.intersecting_venues)} on Deck {sandwich.overhead_layer.deck_number}")
            elif sandwich.overhead_layer.is_residential_cabins_only:
                flags.append(f"Protected overhead: Residential cabins on Deck {sandwich.overhead_layer.deck_number}")

        if sandwich and sandwich.underfoot_layer:
            if sandwich.underfoot_layer.is_active_noise_generator:
                flags.append(f"Underfoot venue: {', '.join(sandwich.underfoot_layer.intersecting_venues)} on Deck {sandwich.underfoot_layer.deck_number}")
            elif sandwich.underfoot_layer.is_residential_cabins_only:
                flags.append(f"Protected underfoot: Residential cabins on Deck {sandwich.underfoot_layer.deck_number}")

        # 2. Elevator lobby distance
        deck = ontology.decks[target_cabin.deck_number]
        nearest_lift_dist = 999.0
        for node_id, node in deck.corridor_nodes.items():
            if node.is_elevator_lobby:
                route = router.find_shortest_path(target_cabin.door.corridor_snap_node_id, node_id)
                if route and route.total_distance_meters < nearest_lift_dist:
                    nearest_lift_dist = route.total_distance_meters

        if nearest_lift_dist < 10.0:
            flags.append("Proximity to elevator lobby (<10m): Higher corridor foot-traffic")
        else:
            flags.append(f"Buffered from elevator lobby ({nearest_lift_dist:.1f}m distance)")

        is_quiet = sandwich is not None and not (
            (sandwich.overhead_layer and sandwich.overhead_layer.is_active_noise_generator)
            or (sandwich.underfoot_layer and sandwich.underfoot_layer.is_active_noise_generator)
            or nearest_lift_dist < 8.0
        )

        summary = (
            "Acoustically buffered stateroom: Quiet sandwich layer above and below, standard corridor buffer."
            if is_quiet
            else "Acoustic notice: Proximity to active venue or high-traffic corridor."
        )

        return QuietCabinEvaluation(
            cabin_number=cabin_number,
            is_quiet_tier=is_quiet,
            sandwich_report=sandwich,
            elevator_lobby_distance_meters=nearest_lift_dist if nearest_lift_dist < 999.0 else 0.0,
            acoustic_flags=flags,
            summary=summary,
        )
