"""
Assistant Engine and Bridge Officer Tim Personal Cruise Concierge for Timonelo (Chapter III - Sprint 10).
"Certainly. I've already prepared a recommendation for exactly that situation."
Provides deterministic daily missions, 2-hour decision options, quick actions, and concierge guidance.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class SuggestionCategory(str, Enum):
    DINING = "DINING (Gastronomie & Lunch)"
    QUIET_TIME = "QUIET_TIME (Ruhezone & Entspannung)"
    SUNSET_SCENIC = "SUNSET_SCENIC (Sonnenuntergang & Panorama)"
    ROUTE_NAVIGATION = "ROUTE_NAVIGATION (Wegeführung & Decks)"
    SHORE_ACTIVITY = "SHORE_ACTIVITY (Landgang & Rückkehr)"
    ENTERTAINMENT = "ENTERTAINMENT (Theater & Abendprogramm)"
    SAFETY_DRILL = "SAFETY_DRILL (Sicherheitsübung & Musterstation)"


class QuickActionQuery(str, Enum):
    MUSTER_STATION = "📍 Guide me to my muster station"
    LUNCH_WHERE = "🍽 Where should I have lunch?"
    SUNSET_SPOT = "🌅 Best sunset spot"
    QUIET_COFFEE = "☕ Quiet coffee"
    GUEST_SERVICES = "🚶 Route to Guest Services"
    THEATRE_TONIGHT = "🎭 Tonight's theatre"
    CITY_RETURN = "🚕 How do I get back from the city?"
    NEXT_STEP = "🧳 What should I do next?"


@dataclass(frozen=True)
class DecisionOption:
    option_id: str
    title: str
    deck_location: str
    category: SuggestionCategory
    time_required_min: int
    walking_effort: str  # "Minimal (<1 min)", "Low (2–4 min)", "Moderate (5–8 min)"
    crowd_level: str     # "Very Quiet (Sehr ruhig)", "Moderate (Angenehm)", "High (Lebhaft)"
    is_accessible: bool
    is_restricted: bool
    restriction_note: Optional[str]
    reasoning: str
    evidence_source: str


@dataclass(frozen=True)
class DailyMission:
    mission_id: str
    phase_name: str
    mission_title: str
    current_objective: str
    recommended_actions: List[str]
    negative_intelligence_avoid: List[str]
    estimated_duration_display: str
    evidence_source: str


@dataclass(frozen=True)
class AssistantRecommendationBundle:
    query_text: str
    bot_opening_line: str
    recommended_options: List[DecisionOption]
    top_recommendation_id: str
    bot_conclusion_line: str
    confidence_score: float = 99.5


class AssistantEngine:
    """Canonical concierge and decision assistant engine for Bridge Officer Tim."""

    DAILY_MISSIONS: Dict[str, DailyMission] = {
        "morning_yokohama": DailyMission(
            mission_id="msn:morning-yokohama",
            phase_name="Hafentag Tokio / Yokohama (Morgen)",
            mission_title="Staufreier Landgang & Vormittags-Erkundung",
            current_objective="Explore Yokohama comfortably before returning to the ship.",
            recommended_actions=[
                "✓ Verlassen Sie das Schiff nach dem ersten Stoß gegen 09:15 Uhr stufenfrei über Osanbashi.",
                "✓ Nutzen Sie die Minatomirai-Bahn mit Suica in Apple Wallet direkt nach Chinatown / Shibuya.",
                "✓ Planen Sie die Rückkehr an Bord spätestens für 16:45 Uhr (45 min vor All Aboard).",
            ],
            negative_intelligence_avoid=[
                "✗ Niemals erst um 17:15 Uhr zur Gangway eilen (Gefahr von Passkontroll-Stau).",
                "✗ Keine Taxis für die Langstrecke nach Tokio nehmen (> 100 €).",
            ],
            estimated_duration_display="Ca. 6–7 Stunden an Land",
            evidence_source="src:field-audit-yokohama-2026",
        ),
        "embarkation_afternoon": DailyMission(
            mission_id="msn:embarkation-day",
            phase_name="Einschiffungstag Shanghai Baoshan",
            mission_title="Entspannte Ankunft & Sicherheitsübung",
            current_objective="Kabine beziehen, Sicherheitsfilm ansehen und Koffer in Empfang nehmen.",
            recommended_actions=[
                "✓ Um 11:35 Uhr am Terminal Gate 2 eintreffen und Koffer abgeben.",
                "✓ Nach dem Betreten direkt ins Posidonia Restaurant auf Deck 5 zum stressfreien Mittagessen.",
                "✓ Sicherheitsvideo auf dem Kabinenfernseher ansehen und an Musterstation F scannen.",
            ],
            negative_intelligence_avoid=[
                "✗ Nicht mit Handgepäck und Koffern direkt ins Marketplace Buffet auf Deck 15 drängen.",
                "✗ Die Sicherheitsübung nicht auf den Abend nach dem Auslaufen verschieben.",
            ],
            estimated_duration_display="Ca. 2,5 Stunden bis zum Auslaufen",
            evidence_source="src:msc-bellissima-operations",
        ),
    }

    @classmethod
    def get_daily_mission(cls, mission_key: str = "morning_yokohama") -> DailyMission:
        return cls.DAILY_MISSIONS.get(mission_key, cls.DAILY_MISSIONS["morning_yokohama"])

    @classmethod
    def evaluate_free_time(
        cls,
        hours_available: float = 2.0,
        traveler_status: str = "Diamond",
        current_time_display: str = "17:00 Uhr",
    ) -> AssistantRecommendationBundle:
        options = [
            DecisionOption(
                option_id="opt:infinity-atrium",
                title="Infinity Atrium & Swarovski-Treppe",
                deck_location="Deck 5 & 6 Mitte",
                category=SuggestionCategory.QUIET_TIME,
                time_required_min=45,
                walking_effort="Low (2–3 min via Fahrstuhl)",
                crowd_level="Moderate (Angenehme Klaviermusik)",
                is_accessible=True,
                is_restricted=False,
                restriction_note=None,
                reasoning="Ruhige Atmosphäre und dezente Live-Musik vor Beginn des abendlichen Hauptunterhaltungsprogramms.",
                evidence_source="src:msc-bellissima-deckplan",
            ),
            DecisionOption(
                option_id="opt:champagne-bar",
                title="Champagne Bar & Horizon Heckdeck",
                deck_location="Deck 7 Galleria & Deck 16 Heck",
                category=SuggestionCategory.SUNSET_SCENIC,
                time_required_min=60,
                walking_effort="Low (3 min)",
                crowd_level="Very Quiet (Perfekter Panoramablick)",
                is_accessible=True,
                is_restricted=False,
                restriction_note=None,
                reasoning="Erstklassige Lage für den Sonnenuntergang auf See mit freiem Blick über das Heckfahrwasser.",
                evidence_source="src:msc-bellissima-deckplan",
            ),
            DecisionOption(
                option_id="opt:yacht-club-lounge",
                title="MSC Yacht Club Top Sail Lounge",
                deck_location="Deck 16 Bug",
                category=SuggestionCategory.QUIET_TIME,
                time_required_min=60,
                walking_effort="Minimal",
                crowd_level="Very Quiet",
                is_accessible=True,
                is_restricted=True,
                restriction_note="Zugang exklusiv für MSC Yacht Club Suiten-Gäste reserviert.",
                reasoning="Privater Lounge-Bereich am Bug; für Nicht-Yacht-Club-Kabinen nicht zugänglich.",
                evidence_source="src:msc-yacht-club-terms",
            ),
        ]

        return AssistantRecommendationBundle(
            query_text=f"Ich habe {hours_available:g} Stunden Zeit vor dem Abendessen.",
            bot_opening_line=f"Guten Tag, Florian. Bei etwa zwei Stunden freier Zeit vor dem Abendessen empfehle ich, den Nachmittag entspannt ausklingen zu lassen.",
            recommended_options=options,
            top_recommendation_id="opt:champagne-bar",
            bot_conclusion_line="Ich bleibe auf der Brücke. Melden Sie sich jederzeit, wenn Sie weitere Details wünschen.",
        )

    @classmethod
    def answer_quick_action(
        cls,
        action: QuickActionQuery,
        cabin_number: str = "14122",
        ship_slug: str = "msc-bellissima",
    ) -> AssistantRecommendationBundle:
        if action == QuickActionQuery.MUSTER_STATION:
            return AssistantRecommendationBundle(
                query_text=action.value,
                bot_opening_line=f"Ihre zugewiesene Musterstation für Kabine {cabin_number} ist Station F im London Theatre auf Deck 5 und 6 Bug.",
                recommended_options=[
                    DecisionOption(
                        option_id="act:muster-f",
                        title="Musterstation F · London Theatre",
                        deck_location="Deck 5 & 6 Forward (Bug)",
                        category=SuggestionCategory.SAFETY_DRILL,
                        time_required_min=3,
                        walking_effort="Low (195 m via Treppenhaus B)",
                        crowd_level="Moderate",
                        is_accessible=True,
                        is_restricted=False,
                        restriction_note=None,
                        reasoning="Stufenfreie Aufzüge B bringen Sie direkt von Deck 14 auf Deck 5 vor das Theater.",
                        evidence_source="src:safety-engine-bellissima",
                    )
                ],
                top_recommendation_id="act:muster-f",
                bot_conclusion_line="Sicherheitsvideo auf der Kabine starten, anschließend mit Bordkarte an Station F einchecken.",
            )

        elif action == QuickActionQuery.LUNCH_WHERE:
            return AssistantRecommendationBundle(
                query_text=action.value,
                bot_opening_line="Ich empfehle am Einschiffungstag und an Seetagen das bediente Hauptrestaurant anstelle des überfüllten Buffets.",
                recommended_options=[
                    DecisionOption(
                        option_id="act:posidonia-lunch",
                        title="Posidonia Restaurant (Bedientes Menü)",
                        deck_location="Deck 5 Mitte",
                        category=SuggestionCategory.DINING,
                        time_required_min=60,
                        walking_effort="Low (2 min mit Lift B)",
                        crowd_level="Very Quiet (Gepflegtes 3-Gänge-Mittagessen ohne Anstehen)",
                        is_accessible=True,
                        is_restricted=False,
                        restriction_note=None,
                        reasoning="Im Reisepreis inklusive; 100% staufrei und ideal, während die Koffer auf die Kabine gebracht werden.",
                        evidence_source="src:msc-dining-operations",
                    )
                ],
                top_recommendation_id="act:posidonia-lunch",
                bot_conclusion_line="Das Buffet auf Deck 15 hat am Anreisetag die höchste Gepäckdichte; Posidonia ist die souveräne Wahl.",
            )

        elif action == QuickActionQuery.SUNSET_SPOT:
            return AssistantRecommendationBundle(
                query_text=action.value,
                bot_opening_line="Der schönste und windgeschützte Sonnenuntergangsplatz befindet sich am Heck von Deck 16.",
                recommended_options=[
                    DecisionOption(
                        option_id="act:horizon-sunset",
                        title="Horizon Bar & Heck-Sonnendeck",
                        deck_location="Deck 16 Heck (Aft)",
                        category=SuggestionCategory.SUNSET_SCENIC,
                        time_required_min=45,
                        walking_effort="Minimal (2 Decks über Kabine 14122)",
                        crowd_level="Moderate (Beste Sicht auf das Kielwasser)",
                        is_accessible=True,
                        is_restricted=False,
                        restriction_note=None,
                        reasoning="Freier 270-Grad-Panoramablick über das offene Meer mit Bar-Service und bequemen Loungesesseln.",
                        evidence_source="src:msc-bellissima-deckplan",
                    )
                ],
                top_recommendation_id="act:horizon-sunset",
                bot_conclusion_line="Empfohlene Ankunft: Ca. 25 Minuten vor dem astronomischen Sonnenuntergang.",
            )

        elif action == QuickActionQuery.QUIET_COFFEE:
            return AssistantRecommendationBundle(
                query_text=action.value,
                bot_opening_line="Für exzellenten italienischen Espresso in ruhiger Atmosphäre empfehle ich die Jean-Philippe Chocolat & Café.",
                recommended_options=[
                    DecisionOption(
                        option_id="act:jp-cafe",
                        title="Jean-Philippe Chocolat & Café",
                        deck_location="Deck 6 Galleria Bellissima",
                        category=SuggestionCategory.QUIET_TIME,
                        time_required_min=20,
                        walking_effort="Low (120 m)",
                        crowd_level="Moderate (Hochwertige Röstungen & Macarons)",
                        is_accessible=True,
                        is_restricted=False,
                        restriction_note=None,
                        reasoning="Erstklassiger Espresso abseits des morgendlichen Buffet-Trubels.",
                        evidence_source="src:msc-bellissima-deckplan",
                    )
                ],
                top_recommendation_id="act:jp-cafe",
                bot_conclusion_line="Vormittags zwischen 09:30 und 11:00 Uhr besonders ruhig.",
            )

        else:
            return AssistantRecommendationBundle(
                query_text=action.value,
                bot_opening_line="Ich habe die operative Wegeführung und Empfehlung für Sie geprüft.",
                recommended_options=[
                    DecisionOption(
                        option_id="act:guest-services",
                        title="Guest Services Desk & Rezeption",
                        deck_location="Deck 5 Infinity Atrium",
                        category=SuggestionCategory.ROUTE_NAVIGATION,
                        time_required_min=10,
                        walking_effort="Low (Direkt an den Swarovski-Treppen)",
                        crowd_level="Moderate",
                        is_accessible=True,
                        is_restricted=False,
                        restriction_note=None,
                        reasoning="24/7 besetzt für Bordkonto-Abrechnung, Kabinenschlüssel und offizielle Anliegen.",
                        evidence_source="src:msc-bellissima-deckplan",
                    )
                ],
                top_recommendation_id="act:guest-services",
                bot_conclusion_line="Ich bleibe auf der Brücke. Melden Sie sich jederzeit.",
            )
