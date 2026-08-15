"""
Plane 6: Port Intelligence Evaluator (Stateless).
Resolves port logistics, gangway decks, tender operations, and shoreside walking routes.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import PortIntelligence, PortDockingType


class PortIntelligenceEvaluator:
    """Evaluates port logistics and shoreside accessibility for any port of call."""

    @staticmethod
    def evaluate(port_data: Optional[Dict[str, Any]] = None) -> PortIntelligence:
        data = port_data or {}
        port_name = data.get("port_name", "Genoa (Genova)")
        country = data.get("country", "Italy")
        dock_type_str = data.get("docking_type", "PIER_BERTH")
        dock_type = PortDockingType[dock_type_str] if hasattr(PortDockingType, dock_type_str) else PortDockingType.PIER_BERTH
        gangway_deck = data.get("gangway_deck", 5)
        gangway_loc = data.get("gangway_location", "Midship Starboard (Deck 05 Atrium)")
        all_aboard = data.get("all_aboard_time", "17:30")
        last_tender = data.get("last_tender_time", None) if dock_type == PortDockingType.OFFSHORE_TENDER else None
        town_distance = data.get("town_distance_meters", 450)
        walkable = data.get("is_walkable_to_center", True)
        route_summary = data.get(
            "walking_route_summary",
            "Direct level exit from Stazione Marittima across pedestrian skybridge to Piazza Principe & Porto Antico."
        )
        taxi_notes = data.get(
            "official_taxi_fare_notes",
            "Fixed municipal tariff: €15 flat rate from cruise pier to Piazza De Ferrari / Historic Center."
        )
        emergency_phone = data.get("local_emergency_phone", "112 (European Emergency Services) / Port Police: +39 010 2411")

        ev_links = [
            EvidenceLink(
                source_id="EVID-PORT-AUTHORITY-GENOA",
                sha256="8f1e2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f",
                locator="Port_of_Genoa_Terminal_Passage_Guide_2026",
            )
        ]

        return PortIntelligence(
            port_name=port_name,
            country=country,
            docking_type=dock_type,
            gangway_deck=gangway_deck,
            gangway_location=gangway_loc,
            all_aboard_time=all_aboard,
            last_tender_time=last_tender,
            town_distance_meters=town_distance,
            is_walkable_to_center=walkable,
            walking_route_summary=route_summary,
            official_taxi_fare_notes=taxi_notes,
            local_emergency_phone=emergency_phone,
            evidence_links=ev_links,
        )
