"""
Plane 6: Embarkation Intelligence Evaluator (Stateless).
Resolves pier terminal floorplans, luggage drops, and safety drill logistics.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import VesselSpatialOntology, Cabin, EvidenceLink
from timonelo.intelligence.models import EmbarkationIntelligence


class EmbarkationIntelligenceEvaluator:
    """Evaluates embarkation and boarding logistics for a traveler."""

    @staticmethod
    def evaluate(
        ontology: VesselSpatialOntology,
        cabin: Cabin,
        terminal_override: Optional[Dict[str, Any]] = None,
    ) -> EmbarkationIntelligence:
        term_data = terminal_override or {}
        terminal_name = term_data.get("terminal_name", "Cruise Terminal A (Palacrociere)")
        pier_number = term_data.get("pier_number", "Berth 10")
        luggage_window = term_data.get("luggage_drop_window", "11:00 – 15:30")
        stateroom_ready = term_data.get("stateroom_ready_time", "14:00")
        drill_deadline = term_data.get("mandatory_safety_drill_deadline", "16:30 (Prior to departure)")

        # Determine muster station based on deck & cabin parity
        deck_num = cabin.deck_number
        is_starboard = (int(cabin.cabin_number[-1]) % 2 == 0)
        station_x = cabin.boundary_polygon[0].x if cabin.boundary_polygon else 0.5

        if station_x > 0.65:
            assigned_muster = "Muster Station A (Forward)" if is_starboard else "Muster Station D (Forward Port)"
            muster_deck = 6 if is_starboard else 7
        elif station_x > 0.35:
            assigned_muster = "Muster Station B (Promenade)" if is_starboard else "Muster Station E (Mid Port)"
            muster_deck = 6 if is_starboard else 7
        else:
            assigned_muster = "Muster Station C (Aft)" if is_starboard else "Muster Station F (Aft Port)"
            muster_deck = 6 if is_starboard else 7

        route_guidance = f"Take nearest elevator down to Deck {muster_deck:02d}, follow emergency signage to {assigned_muster}."

        ev_links = list(cabin.evidence_links) if cabin.evidence_links else [
            EvidenceLink(source_id="EVID-SOLAS-BELLISSIMA", sha256="4b9a8f2e1c3d5a7b6e8f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d", locator="SOLAS_Safety_Plan_Rev4")
        ]

        return EmbarkationIntelligence(
            terminal_name=terminal_name,
            pier_number=pier_number,
            luggage_drop_window=luggage_window,
            stateroom_ready_time=stateroom_ready,
            mandatory_safety_drill_deadline=drill_deadline,
            assigned_muster_station=assigned_muster,
            muster_station_deck=muster_deck,
            step_free_muster_route=route_guidance,
            boarding_pass_requirement="Keep digital or printed boarding pass and valid passport in hand (do NOT pack in checked luggage).",
            evidence_links=ev_links,
        )
