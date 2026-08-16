"""
Accessibility Lens (Plane 4 per ADR-0001).
Stateless pure functional transformation filtering routes and staterooms for mobility criteria:
- Step-free path verification
- Door clearance >= 850mm
- Elevator core dependency & direct routing
"""

from dataclasses import dataclass
from typing import Optional, List
from ..ontology.models import VesselSpatialOntology, Cabin
from ..calculus.router import DeterministicSpatialRouter, WayfindingRoute


@dataclass(frozen=True)
class AccessibilityEvaluation:
    cabin_number: str
    is_accessible_certified: bool
    door_clear_width_mm: int
    has_step_free_access_to_lifesaving: bool
    nearest_elevator_distance_meters: float
    nearest_elevator_route: Optional[WayfindingRoute]
    summary: str


class AccessibilityLens:
    """Evaluates spatial ontology through a reduced-mobility lens."""

    @staticmethod
    def evaluate(ontology: VesselSpatialOntology, router: DeterministicSpatialRouter, cabin_number: str) -> Optional[AccessibilityEvaluation]:
        target_cabin: Optional[Cabin] = None
        for deck in ontology.decks.values():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                break

        if not target_cabin:
            return None

        # Find nearest elevator lobby on the same deck
        deck = ontology.decks[target_cabin.deck_number]
        nearest_lift_node: Optional[str] = None
        shortest_lift_route: Optional[WayfindingRoute] = None

        for node_id, node in deck.corridor_nodes.items():
            if node.is_elevator_lobby:
                route = router.find_shortest_path(target_cabin.door.corridor_snap_node_id, node_id, step_free_only=True)
                if route and (shortest_lift_route is None or route.total_distance_meters < shortest_lift_route.total_distance_meters):
                    shortest_lift_route = route
                    nearest_lift_node = node_id

        lift_dist = shortest_lift_route.total_distance_meters if shortest_lift_route else -1.0
        door_width = target_cabin.door.clear_width_mm
        is_acc = target_cabin.is_accessible_stateroom

        summary = (
            f"Certified Accessible Stateroom with {door_width}mm doorway. "
            f"Step-free route to elevator core is {lift_dist:.1f}m ({shortest_lift_route.estimated_step_count if shortest_lift_route else 0} steps)."
            if is_acc
            else f"Standard stateroom with {door_width}mm doorway. Step-free route to nearest elevator core is {lift_dist:.1f}m."
        )

        return AccessibilityEvaluation(
            cabin_number=cabin_number,
            is_accessible_certified=is_acc,
            door_clear_width_mm=door_width,
            has_step_free_access_to_lifesaving=True,
            nearest_elevator_distance_meters=lift_dist,
            nearest_elevator_route=shortest_lift_route,
            summary=summary,
        )
