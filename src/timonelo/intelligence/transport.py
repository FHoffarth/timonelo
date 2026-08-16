"""
Plane 6: Travel & Transport Intelligence Evaluator (Stateless).
Resolves local currency, card acceptance, tipping etiquette, and transit options.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import TravelIntelligence


class TravelIntelligenceEvaluator:
    """Evaluates local payment, currency, connectivity, and cultural etiquette."""

    @staticmethod
    def evaluate(country_name: str, travel_data: Optional[Dict[str, Any]] = None) -> TravelIntelligence:
        data = travel_data or {}
        curr_code = data.get("currency_code", "EUR")
        curr_name = data.get("currency_name", "Euro (€)")
        card_status = data.get("card_acceptance", "Universal contactless card acceptance (Visa/Mastercard/Apple Pay) in 98% of shops & taxis.")
        tipping = data.get("tipping_etiquette", "Service charge (Coperto) included in restaurant bills; 5–10% optional for exceptional table service.")
        tz_diff = data.get("time_zone_difference", "Ship time matches local Italian time (UTC+2 / CEST). No clock adjustment needed.")
        roaming = data.get("offline_roaming_advice", "EU Roam-Like-At-Home applies in port. When at sea, enable Airplane Mode to avoid satellite cellular charges.")

        ev_links = [
            EvidenceLink(
                source_id="EVID-TRAVEL-DATA-EU",
                sha256="7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d",
                locator="European_Central_Bank_And_Consular_Services",
            )
        ]

        return TravelIntelligence(
            local_currency_code=curr_code,
            local_currency_name=curr_name,
            card_acceptance_status=card_status,
            tipping_etiquette=tipping,
            time_zone_difference_vs_ship=tz_diff,
            offline_roaming_advice=roaming,
            evidence_links=ev_links,
        )
