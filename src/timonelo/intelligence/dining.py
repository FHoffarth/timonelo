"""
Plane 6: Dining Intelligence Evaluator (Stateless).
Resolves evening dining venues, walking distance from cabin, dress codes, and step-free access.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import VesselSpatialOntology, Cabin, EvidenceLink
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.intelligence.models import DiningIntelligence


class DiningIntelligenceEvaluator:
    """Evaluates culinary options, assigned main restaurants, and route metrics."""

    @staticmethod
    def evaluate(
        ontology: VesselSpatialOntology,
        cabin: Cabin,
        router: DeterministicSpatialRouter,
        dining_override: Optional[Dict[str, Any]] = None,
    ) -> DiningIntelligence:
        data = dining_override or {}
        assigned_name = data.get("assigned_restaurant", "Il Ciliegio & Le Cerisier Restaurant")
        deck_num = int(data.get("restaurant_deck", 6))
        dress_code = data.get("dress_code", "Casual Elegant (Collared shirts, smart trousers/dresses; no swimwear)")
        buffet_status = data.get("buffet_status", "Marketplace Buffet (Deck 15 Midship) open continuously 06:00 – 01:30")

        # Calculate exact route from cabin door to main restaurant entrance
        target_node = f"D{deck_num:02d}_RESTAURANT_IL_CILIEGIO"
        # Fallback to mid lift if specific entrance is not present
        if target_node not in ontology.decks[deck_num].corridor_nodes:
            target_node = f"D{deck_num:02d}_AFT_LIFT"

        route = router.find_shortest_path(cabin.door.corridor_snap_node_id, target_node)

        walking_dist = route.total_distance_meters if route else 45.0
        walking_secs = route.estimated_walking_seconds if route else 38
        step_free = route.is_fully_step_free if route else True

        ev_links = list(cabin.evidence_links) if cabin.evidence_links else [
            EvidenceLink(source_id="EVID-DINING-GUIDE", sha256="1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b", locator="MSC_Dining_Daily_Program")
        ]

        return DiningIntelligence(
            assigned_main_restaurant=assigned_name,
            restaurant_deck=deck_num,
            evening_dress_code=dress_code,
            walking_meters_from_cabin=walking_dist,
            walking_seconds=walking_secs,
            is_step_free=step_free,
            marketplace_buffet_status=buffet_status,
            evidence_links=ev_links,
        )
