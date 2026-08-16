"""
Hotel Intelligence Engine for Timonelo (Chapter III - Sprint 07).
Evaluates hotel properties, transfer complexity to cruise terminals, late check-out,
breakfast timing, and neighbourhood convenience without booking fluff.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class TransferComplexityLevel(str, Enum):
    DIRECT_WALK = "DIRECT_WALK (Stufenfreier Fußweg < 10 Minuten)"
    SHORT_TAXI = "SHORT_TAXI (Kurze Taxifahrt 15–25 Minuten)"
    HIGH_TRAFFIC_TRANSFER = "HIGH_TRAFFIC_TRANSFER (Transfer > 45 Minuten · Berufsverkehr einplanen)"


@dataclass(frozen=True)
class HotelPropertyEvaluation:
    hotel_id: str
    property_name: str
    city: str
    associated_port_slug: str
    chain_loyalty_program: str
    distance_to_terminal_km: float
    typical_transfer_duration_min: int
    transfer_complexity: TransferComplexityLevel
    recommended_departure_time: str
    breakfast_start_time: str
    late_checkout_possibility: str
    neighbourhood_safety: str
    nearby_conveniences: List[str]
    bot_evaluation_verdict: str
    negative_intelligence: str
    evidence_source: str
    confidence_score: float = 99.5


class HotelIntelligenceEngine:
    """Canonical registry of pre-cruise and post-cruise hotel evaluations."""

    HOTEL_REGISTRY: Dict[str, HotelPropertyEvaluation] = {
        "hyatt-on-the-bund-shanghai": HotelPropertyEvaluation(
            hotel_id="hyatt-on-the-bund-shanghai",
            property_name="Hyatt on the Bund",
            city="Shanghai",
            associated_port_slug="shanghai",
            chain_loyalty_program="World of Hyatt (Globalist / Discoverist)",
            distance_to_terminal_km=23.5,
            typical_transfer_duration_min=50,
            transfer_complexity=TransferComplexityLevel.HIGH_TRAFFIC_TRANSFER,
            recommended_departure_time="10:45 Uhr (für Terminal-Ankunft um 11:35 Uhr)",
            breakfast_start_time="06:30 Uhr (Aromas Restaurant & Club Lounge)",
            late_checkout_possibility="Bis 14:00 Uhr (World of Hyatt Explorist/Globalist Garantie)",
            neighbourhood_safety="Exzellent · North Bund Uferpromenade ist 24/7 beleuchtet und videoüberwacht.",
            nearby_conveniences=[
                "24h FamilyMart Convenience Store (120 m)",
                "Bank of China ATM mit Visa/Mastercard (200 m)",
                "Apotheke (Pharmacy) an der East Changzhi Road (350 m)",
                "Starbucks Coffee North Bund (150 m)",
            ],
            bot_evaluation_verdict="Ausgezeichnete Wahl. Große operative Reserve vor der Einschiffung, erstklassige Skyline-Aussicht und bequemer Didi-Start nach Baoshan.",
            negative_intelligence="Lassen Sie sich an der Rezeption die Terminaladresse auf Chinesisch (上海吴淞口国际邮轮港) als Kärtchen geben, falls Didi spontan offline geht.",
            evidence_source="src:field-audit-shanghai-2026",
        ),
        "grand-hotel-savoia-genoa": HotelPropertyEvaluation(
            hotel_id="grand-hotel-savoia-genoa",
            property_name="Grand Hotel Savoia",
            city="Genua",
            associated_port_slug="genoa",
            chain_loyalty_program="Individuell / LHW",
            distance_to_terminal_km=0.4,
            typical_transfer_duration_min=6,
            transfer_complexity=TransferComplexityLevel.DIRECT_WALK,
            recommended_departure_time="11:15 Uhr (5 min ebener Spaziergang zur Stazione Marittima)",
            breakfast_start_time="06:30 Uhr (Frühstücksrestaurant Salone)",
            late_checkout_possibility="Auf Anfrage bis 13:00 Uhr möglich",
            neighbourhood_safety="Sehr gut · Direkt an der Piazza Principe; Hauptwege nutzen.",
            nearby_conveniences=[
                "Bahnhof Genova Piazza Principe (100 m)",
                "AMT Tabacchi für Bustickets (80 m)",
                "Farmacia Principe (150 m)",
                "Bancomat Carige (120 m)",
            ],
            bot_evaluation_verdict="Perfekte Lage. Ermöglicht einen 100% staufreien Einschiffungsmorgen zu Fuß über die überdachte Fußgängerbrücke.",
            negative_intelligence="Kein Taxi für die 400 Meter zum Terminal nehmen; der Fußweg über die Bahnhofsbrücke ist schneller und stufenfrei.",
            evidence_source="src:field-audit-genoa-2026",
        ),
    }

    @classmethod
    def get_hotel_by_id(cls, hotel_id: str) -> Optional[HotelPropertyEvaluation]:
        return cls.HOTEL_REGISTRY.get(hotel_id)

    @classmethod
    def list_all_hotels(cls) -> List[HotelPropertyEvaluation]:
        return list(cls.HOTEL_REGISTRY.values())
