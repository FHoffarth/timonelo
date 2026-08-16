"""
Shipmate Memory & Bridge Logbook Engine for Timonelo (Chapter V - Sprint 01).
"Bridge Officer Tim Remembers Every Voyage."
"Voyage completed successfully. Thank you for allowing me to accompany you. I have entered this journey into the ship's log, and I look forward to welcoming you aboard again."
Maintains factual, dignified travel memories, visited ports and ships, confirmed travel habits,
and chronological one-sentence daily Bridge Journal logs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class HabitCategory(str, Enum):
    DINING = "DINING (Gastronomie & Frühstück)"
    SCENIC_SPOT = "SCENIC_SPOT (Aussicht & Sonnenuntergang)"
    MOVEMENT = "MOVEMENT (Wege & Orientierung)"
    CABIN = "CABIN (Kabinen-Präferenzen)"
    RELAXATION = "RELAXATION (Ruhe & Rückzugsorte)"


@dataclass(frozen=True)
class TravelHabit:
    habit_id: str
    category: HabitCategory
    observation: str
    evidence_voyage: str
    confidence_level: float = 99.0


@dataclass(frozen=True)
class FavouriteLocation:
    location_id: str
    name: str
    category: str
    ship_name: str
    deck_location: str
    why_favoured: str
    evidence_source: str = "src:bridge-log-history"


@dataclass(frozen=True)
class BridgeJournalEntry:
    entry_id: str
    date_str: str
    voyage_day_label: str
    factual_milestone_sentence: str
    port_or_sea_location: str


@dataclass(frozen=True)
class CompletedVoyageLog:
    voyage_id: str
    ship_name: str
    cruise_line: str
    departure_date: str
    itinerary_summary: str
    visited_ports: List[str]
    visited_countries: List[str]
    cabin_booked: str
    favourite_venue: str
    favourite_memory: str
    journal_entries: List[BridgeJournalEntry]
    status: str = "COMPLETED_SUCCESSFULLY"


@dataclass(frozen=True)
class TravellerShipmateProfile:
    traveller_name: str
    total_voyages_count: int
    total_sea_days: int
    visited_countries: List[str]
    visited_ports: List[str]
    visited_ships: List[str]
    favourite_places: List[FavouriteLocation]
    confirmed_habits: List[TravelHabit]
    voyage_history: List[CompletedVoyageLog]
    bot_welcome_back_greeting: str
    bot_closing_log_note: str = "Voyage completed successfully. Thank you for allowing me to accompany you. I have entered this journey into the ship's log, and I look forward to welcoming you aboard again."


class BridgeMemoryEngine:
    """Canonical engine managing bridge logs, voyage journals, and travel memories."""

    CANONICAL_PROFILE: TravellerShipmateProfile = TravellerShipmateProfile(
        traveller_name="Florian",
        total_voyages_count=2,
        total_sea_days=18,
        visited_countries=["China", "Japan", "Italien", "Frankreich", "Spanien", "Portugal"],
        visited_ports=["Shanghai", "Yokohama", "Kagoshima", "Genua", "Neapel", "Barcelona", "Porto"],
        visited_ships=["MSC Bellissima", "MS Andorinha", "MSC Grandiosa"],
        favourite_places=[
            FavouriteLocation(
                location_id="fav:horizon-deck16",
                name="Horizon Bar & Heckpromenade",
                category="Observation Spot",
                ship_name="MSC Bellissima",
                deck_location="Deck 16 Heck",
                why_favoured="Bevorzugter Ort für den Sonnenuntergang mit 270°-Blick über das Kielwasser.",
            ),
            FavouriteLocation(
                location_id="fav:posidonia-deck5",
                name="Posidonia Menü-Restaurant",
                category="Dining Venue",
                ship_name="MSC Bellissima",
                deck_location="Deck 5 Mitte",
                why_favoured="Ruhiges Mittagessen mit À-la-carte-Service abseits des Buffet-Trubels.",
            ),
            FavouriteLocation(
                location_id="fav:sky-lounge-deck18",
                name="Sky Lounge & Panoramabibliothek",
                category="Quiet Lounge",
                ship_name="MSC Bellissima",
                deck_location="Deck 18 Mitte",
                why_favoured="Klassische Musik und absolute Ruhe bei abendlichen Pool-Events.",
            ),
        ],
        confirmed_habits=[
            TravelHabit(
                habit_id="hab:quiet-breakfast",
                category=HabitCategory.DINING,
                observation="Bevorzugt ruhige Frühstücksorte vor 08:30 Uhr statt des vollen Hauptbuffets.",
                evidence_voyage="MSC Bellissima · Tag 2–7",
            ),
            TravelHabit(
                habit_id="hab:stairs-over-lifts",
                category=HabitCategory.MOVEMENT,
                observation="Nutzt für 1–3 Decks Unterschied bevorzugt das Haupttreppenhaus statt der Lifts.",
                evidence_voyage="MSC Bellissima & MSC Grandiosa",
            ),
            TravelHabit(
                habit_id="hab:theatre-deck5-entry",
                category=HabitCategory.MOVEMENT,
                observation="Betritt das London Theatre über den staufreien unteren Eingang auf Deck 5.",
                evidence_voyage="MSC Bellissima · Abend-Shows",
            ),
            TravelHabit(
                habit_id="hab:sunset-stern",
                category=HabitCategory.SCENIC_SPOT,
                observation="Verfolgt das Auslaufen am liebsten windgeschützt am Heck mit Blick auf das Kielwasser.",
                evidence_voyage="Grand Voyage Ostasien 2026",
            ),
        ],
        voyage_history=[
            CompletedVoyageLog(
                voyage_id="voy:andorinha-douro-2025",
                ship_name="MS Andorinha",
                cruise_line="Tauck River Cruises",
                departure_date="Mai 2025",
                itinerary_summary="Porto · Douro-Tal · Pinhão · Vega de Terrón",
                visited_ports=["Porto", "Pinhão", "Régua", "Vega de Terrón"],
                visited_countries=["Portugal", "Spanien"],
                cabin_booked="Suite 218 (Oberdeck französische Balkone)",
                favourite_venue="Panoramaterrasse Deck 3",
                favourite_memory="Stilles Gleiten durch die terrassierten Weinberge des Douro im Abendlicht.",
                journal_entries=[
                    BridgeJournalEntry(
                        entry_id="jrn:and-1",
                        date_str="12. Mai 2025",
                        voyage_day_label="Tag 1 · Einschiffung",
                        factual_milestone_sentence="Sie haben in Porto an Bord der MS Andorinha eingecheckt.",
                        port_or_sea_location="Porto (Ribeira)",
                    ),
                    BridgeJournalEntry(
                        entry_id="jrn:and-4",
                        date_str="15. Mai 2025",
                        voyage_day_label="Tag 4 · Flusstag",
                        factual_milestone_sentence="Sie passierten die Schleuse Carrapatelo bei ruhigem Fahrwasser.",
                        port_or_sea_location="Douro-Flusstal",
                    ),
                ],
                status="COMPLETED_SUCCESSFULLY",
            ),
            CompletedVoyageLog(
                voyage_id="voy:bellissima-asia-2026",
                ship_name="MSC Bellissima",
                cruise_line="MSC Cruises",
                departure_date="Oktober 2026",
                itinerary_summary="Shanghai (Wusongkou) · Kagoshima · Tokio/Yokohama",
                visited_ports=["Shanghai", "Kagoshima", "Yokohama"],
                visited_countries=["China", "Japan"],
                cabin_booked="Balkonkabine 14122 (Steuerbord Hecknah)",
                favourite_venue="Horizon Bar Deck 16 Heck",
                favourite_memory="Auslaufen aus dem Hafen von Yokohama mit Blick auf den beleuchteten Marine Tower.",
                journal_entries=[
                    BridgeJournalEntry(
                        entry_id="jrn:bel-1",
                        date_str="15. Oktober 2026",
                        voyage_day_label="Tag 1 · Einschiffung",
                        factual_milestone_sentence="Sie haben Ihre Kabine 14122 bezogen und die Sicherheitsstation F absolviert.",
                        port_or_sea_location="Shanghai Wusongkou",
                    ),
                    BridgeJournalEntry(
                        entry_id="jrn:bel-3",
                        date_str="17. Oktober 2026",
                        voyage_day_label="Tag 3 · Seetag",
                        factual_milestone_sentence="Sie genossen den Sonnenuntergang auf Deck 16 mit Blick auf das Ostchinesische Meer.",
                        port_or_sea_location="Ostchinesisches Meer",
                    ),
                    BridgeJournalEntry(
                        entry_id="jrn:bel-5",
                        date_str="19. Oktober 2026",
                        voyage_day_label="Tag 5 · Landgang",
                        factual_milestone_sentence="Sie erkundeten Yokohama und kehrten 45 Minuten vor All Aboard an Bord zurück.",
                        port_or_sea_location="Yokohama Osanbashi",
                    ),
                ],
                status="COMPLETED_SUCCESSFULLY",
            ),
        ],
        bot_welcome_back_greeting="Willkommen zurück an Bord, Florian. Es ist mir eine Freude, Sie erneut begleiten zu dürfen. Ich habe Ihre bisherigen Logbucheinträge und bevorzugten Rückzugsorte auf der Brücke bereitgelegt.",
    )

    @classmethod
    def get_shipmate_profile(cls, traveller_name: str = "Florian") -> TravellerShipmateProfile:
        return cls.CANONICAL_PROFILE

    @classmethod
    def generate_proactive_memory_insights(cls, traveller_name: str = "Florian") -> List[str]:
        return [
            "BOT remembered: Auf Ihrer Reise mit MSC Bellissima schätzten Sie das ruhige Frühstück vor 08:30 Uhr. Ich habe für morgen früh passende Zeiten vorbereitet.",
            "BOT remembered: Für den heutigen Sonnenuntergang empfehle ich erneut die Horizon Bar auf Deck 16 am Heck.",
            "BOT remembered: Sie nutzen gerne den unteren Eingang des Theaters auf Deck 5, um den Einlassstau zu umgehen.",
        ]
