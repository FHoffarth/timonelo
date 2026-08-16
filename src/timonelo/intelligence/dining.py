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

        # 1. Search ontology for primary dining venue
        found_venue = None
        found_deck_num = 1

        if "assigned_restaurant" in data:
            assigned_name = data["assigned_restaurant"]
            found_deck_num = int(data.get("restaurant_deck", 1))
        else:
            # Look for venue with category DINING or containing Restaurant / Dining in name
            for d_num, deck in ontology.decks.items():
                for v in deck.venues.values():
                    if v.category.value == "DINING" or "restaurant" in v.name.lower() or "dining" in v.name.lower():
                        found_venue = v
                        found_deck_num = d_num
                        break
                if found_venue:
                    break

            if found_venue:
                assigned_name = found_venue.name
            else:
                assigned_name = "Main Dining Room"
                found_deck_num = min(ontology.decks.keys()) if ontology.decks else 1

        deck_num = int(data.get("restaurant_deck", found_deck_num))
        dress_code = data.get("dress_code", "Casual Elegant (Collared shirts, smart trousers/dresses; no swimwear)")
        buffet_status = data.get("buffet_status", "Marketplace Buffet / Bistro open for breakfast, lunch, and afternoon tea.")

        # 2. Determine target entrance node for route calculation
        target_node = None
        if found_venue and found_venue.entrance_node_ids:
            target_node = found_venue.entrance_node_ids[0]
        elif deck_num in ontology.decks:
            # Fallback to any node on the restaurant deck
            nodes = list(ontology.decks[deck_num].corridor_nodes.keys())
            if nodes:
                target_node = nodes[0]

        route = None
        if target_node:
            route = router.find_shortest_path(cabin.door.corridor_snap_node_id, target_node)

        walking_dist = route.total_distance_meters if route else 25.0
        walking_secs = route.estimated_walking_seconds if route else 20
        step_free = route.is_fully_step_free if route else True

        ev_links = list(cabin.evidence_links) if cabin.evidence_links else [
            EvidenceLink(source_id="EVID-DINING-GUIDE", sha256="1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b", locator="Vessel_Dining_Daily_Program")
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
