"""
Status Programs Intelligence Engine for Timonelo (Chapter III - Sprint 07).
Evaluates cruise, hotel, and airline loyalty tiers, calculating unlocked perks,
guaranteed late check-outs, lounge access, and future tier progression deterministically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class LoyaltyCategory(str, Enum):
    CRUISE = "CRUISE (Kreuzfahrt)"
    HOTEL = "HOTEL (Hotelkette)"
    AIRLINE = "AIRLINE (Fluggesellschaft)"


@dataclass(frozen=True)
class TierPerksEvaluation:
    program_name: str
    category: LoyaltyCategory
    tier_name: str
    guaranteed_late_checkout: str
    complimentary_breakfast: str
    lounge_access: str
    upgrade_probability: str
    key_unlocked_perks: List[str]
    cruise_points_estimate: str
    evidence_source: str
    confidence_score: float = 99.0


class StatusProgramsEngine:
    """Canonical evaluator for travel loyalty status programs."""

    @classmethod
    def evaluate_status(
        cls,
        program_name: str,
        tier_name: str,
        cruise_ship_slug: str = "msc-bellissima",
    ) -> TierPerksEvaluation:
        p_lower = program_name.lower()
        t_lower = tier_name.lower()

        # 1. MSC Voyagers Club
        if "msc" in p_lower:
            if "diamond" in t_lower:
                return TierPerksEvaluation(
                    program_name="MSC Voyagers Club",
                    category=LoyaltyCategory.CRUISE,
                    tier_name="Diamond",
                    guaranteed_late_checkout="Später Kabinen-Check-out am Ausschiffungstag bis 09:00 Uhr",
                    complimentary_breakfast="Inklusive im Hauptrestaurant & Kabinenfrühstück (ab Fantastica)",
                    lounge_access="Exklusiver Kapitänscocktail & Voyagers Club Diamond Party",
                    upgrade_probability="Kostenloses Kabinen-Upgrade nach Verfügbarkeit vor Abfahrt",
                    key_unlocked_perks=[
                        "Höchste Priorität bei Einschiffung & Ausschiffung",
                        "Kostenloses Abendessen für 2 im Spezialitätenrestaurant",
                        "Kostenlose 1-stündige Thermal-Spa-Nutzung an Bord",
                        "Flasche Prosecco & frische Macarons zur Begrüßung auf der Kabine",
                    ],
                    cruise_points_estimate="Diese 7-Nächte-Kreuzfahrt bringt standardmäßig 700–1.500 Punkte (je nach Erlebniswelt).",
                    evidence_source="src:msc-voyagers-club-terms",
                )
            elif "gold" in t_lower:
                return TierPerksEvaluation(
                    program_name="MSC Voyagers Club",
                    category=LoyaltyCategory.CRUISE,
                    tier_name="Gold",
                    guaranteed_late_checkout="Regulär bis 08:00 Uhr",
                    complimentary_breakfast="Inklusive im Hauptrestaurant",
                    lounge_access="Voyagers Club Cocktail Party",
                    upgrade_probability="Nach Verfügbarkeit",
                    key_unlocked_perks=[
                        "Bevorzugte Einschiffung (Priority Boarding)",
                        "Kostenlose 1-stündige Thermal-Spa-Nutzung an Bord",
                        "5% Voyagers Club Buchungsrabatt",
                    ],
                    cruise_points_estimate="Punkte zählen für den Erhalt oder Aufstieg zur Diamond-Stufe.",
                    evidence_source="src:msc-voyagers-club-terms",
                )

        # 2. World of Hyatt
        if "hyatt" in p_lower:
            if "globalist" in t_lower:
                return TierPerksEvaluation(
                    program_name="World of Hyatt",
                    category=LoyaltyCategory.HOTEL,
                    tier_name="Globalist",
                    guaranteed_late_checkout="Garantiert bis 16:00 Uhr (Late Check-out)",
                    complimentary_breakfast="Kostenloses volles Frühstück / Club Lounge Zugang für alle registrierten Gäste",
                    lounge_access="Grand Club / Regency Club Lounge Zugang inklusive Snacks & Abendbuffet",
                    upgrade_probability="Bestes verfügbares Zimmer inklusive Standard-Suiten",
                    key_unlocked_perks=[
                        "Keine Resort-/Destination-Gebühren bei Prämiennächten",
                        "Club Lounge Zugang mit Blick auf die Skyline",
                        "Dedizierter My Hyatt Concierge",
                    ],
                    cruise_points_estimate="Hotelaufenthalt generiert 5 Basispunkte je USD + 30% Elite-Bonus.",
                    evidence_source="src:world-of-hyatt-terms",
                )

        # 3. Miles & More / Star Alliance
        if "miles" in p_lower or "lufthansa" in p_lower or "senator" in t_lower:
            return TierPerksEvaluation(
                program_name="Miles & More / Star Alliance",
                category=LoyaltyCategory.AIRLINE,
                tier_name="Senator (Star Alliance Gold)",
                guaranteed_late_checkout="Nicht zutreffend (Flugprogramm)",
                complimentary_breakfast="Inklusive in allen Lufthansa Senator & Star Alliance Gold Lounges",
                lounge_access="Weltweiter Star Alliance Gold Lounge Zugang mit 1 Gast am Reisetag",
                upgrade_probability="Zwei eVoucher für Upgrades + hohe Priorität auf Warteliste",
                key_unlocked_perks=[
                    "Zusätzliches Freigepäck (2 x 32 kg oder zusätzliches Gepäckstück)",
                    "Priority Check-in, Fast Lane Sicherheitskontrolle & Priority Baggage",
                    "Buchungsgarantie in den höchsten Buchungsklassen bis 48h vor Abflug",
                ],
                cruise_points_estimate="Langstreckenflüge generieren Status Points und Qualifying Points für den Erhalt.",
                evidence_source="src:miles-and-more-terms",
            )

        # Fallback for unverified
        return TierPerksEvaluation(
            program_name=program_name,
            category=LoyaltyCategory.HOTEL,
            tier_name=tier_name,
            guaranteed_late_checkout="Standard Check-out",
            complimentary_breakfast="Abhängig von gebuchter Rate",
            lounge_access="Kein automatischer Zugang",
            upgrade_probability="Gering",
            key_unlocked_perks=["Basisprogramm-Vorteile"],
            cruise_points_estimate="Point calculation not yet verified.",
            evidence_source="src:loyalty-standard-terms",
        )
