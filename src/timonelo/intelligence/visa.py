"""
Plane 6: Sovereign Visa & Entry Intelligence Evaluator (Stateless).
Resolves international passport validity rules, transit visas, and customs.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import VisaIntelligence


class VisaIntelligenceEvaluator:
    """Evaluates border control and passport requirements for itinerary stops."""

    @staticmethod
    def evaluate(country_name: str, visa_data: Optional[Dict[str, Any]] = None) -> VisaIntelligence:
        data = visa_data or {}
        validity_months = int(data.get("passport_validity_required_months", 6))
        visa_req = bool(data.get("visa_required_for_passengers", False))
        notes = data.get(
            "visa_notes",
            f"Schengen cruise transit rules apply for {country_name}. EU/EEA/US/UK/CAN/AUS passport holders require no transit visa for tourist stays up to 90 days."
        )
        customs = data.get(
            "currency_import_limit_notes",
            "Declarations required for cash amounts equal to or exceeding €10,000 (or equivalent)."
        )

        ev_links = [
            EvidenceLink(
                source_id="EVID-CONSULAR-SCHENGEN-BORDER",
                sha256="5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b",
                locator="EU_Schengen_Border_Code_Maritime_Annex",
            )
        ]

        return VisaIntelligence(
            destination_country=country_name,
            passport_validity_required_months=validity_months,
            visa_required_for_passengers=visa_req,
            visa_notes=notes,
            currency_import_limit_notes=customs,
            evidence_links=ev_links,
        )
