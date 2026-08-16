"""
Experience Intelligence Engine for Timonelo (Chapter IV - Sprint 01).
"Every Voyage Has Its Own Culture."
"Whatever tonight's programme may hold, I wish you a wonderful evening aboard. I'll remain on the bridge should you need me."
Understands voyage culture, themes, charters, dress codes, event timelines, and quieter alternatives
without making assumptions about individual travellers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class ExperienceType(str, Enum):
    STANDARD_CRUISE = "STANDARD_CRUISE (Klassische Premium-Kreuzfahrt)"
    FAMILY_CRUISE = "FAMILY_CRUISE (Familien- & Mehrgenerationenreise)"
    ADULTS_ONLY = "ADULTS_ONLY (Erwachsenenreise ab 18 Jahren)"
    FULL_SHIP_CHARTER = "FULL_SHIP_CHARTER (Vollcharter / Exklusives Event)"
    CORPORATE_CHARTER = "CORPORATE_CHARTER (Incentive- & Firmencharter)"
    MUSIC_CRUISE = "MUSIC_CRUISE (Musikfestival- & Konzert-Kreuzfahrt)"
    LGBTQ_CHARTER = "LGBTQ_CHARTER (LGBTQ+ Community Vollcharter)"
    WELLNESS_CRUISE = "WELLNESS_CRUISE (Health-, Yoga- & Spa-Fokus)"
    FOOD_AND_WINE = "FOOD_AND_WINE (Gourmet- & Wein-Themenreise)"
    CHRISTMAS_CRUISE = "CHRISTMAS_CRUISE (Festtags- & Neujahrsreise)"
    EXPEDITION_CRUISE = "EXPEDITION_CRUISE (Natur- & Entdeckungsreise)"
    WORLD_CRUISE = "WORLD_CRUISE (Weltreise / Grand Voyage)"
    RIVER_CRUISE = "RIVER_CRUISE (Flusskreuzfahrt Kultur)"
    SINGLES_CRUISE = "SINGLES_CRUISE (Reise für Alleinreisende)"
    EDUCATIONAL_CRUISE = "EDUCATIONAL_CRUISE (Wissenschafts- & Vortragsreise)"


class DressCode(str, Enum):
    CASUAL = "CASUAL (Legere Urlaubsbekleidung)"
    SMART_CASUAL = "SMART_CASUAL (Gepflegte Freizeitkleidung · Hemd / Sommerkleid)"
    ELEGANT_GALA = "ELEGANT_GALA (Gala-Abend · Abendkleid / Anzug / Sakko)"
    WHITE_NIGHT = "WHITE_NIGHT (White Party · Weiße / Helle Kleidung empfohlen)"
    FLOWER_GLORY_70S = "FLOWER_GLORY_70S (70er / 80er Retro Party)"
    CARIBBEAN_TROPICAL = "CARIBBEAN_TROPICAL (Tropisch bunte Sommermuster)"
    OPTIONAL_THEME = "OPTIONAL_THEME (Mottokleidung vollkommen freiwillig)"


@dataclass(frozen=True)
class VoyageEvent:
    event_id: str
    title: str
    start_time: str
    venue_name: str
    deck_location: str
    dress_code: DressCode
    crowd_expectation: str  # "Very High", "High", "Moderate", "Quiet"
    description: str
    is_optional: bool = True
    quieter_alternative_venue: Optional[str] = None


@dataclass(frozen=True)
class ExperienceProfile:
    voyage_id: str
    ship_name: str
    experience_type: ExperienceType
    charter_organizer: Optional[str]
    voyage_theme_title: str
    description: str
    community_highlights: List[str]
    dress_guidance_summary: str
    events_schedule: List[VoyageEvent]
    busy_areas_to_avoid: List[str]
    quiet_retreat_venues: List[str]
    bot_proactive_observations: List[str]
    bot_evening_sign_off: str = "Whatever tonight's programme may hold, I wish you a wonderful evening aboard. I'll remain on the bridge should you need me."
    evidence_source: str = "src:voyage-manifest-experience"
    confidence_score: float = 99.5


class ExperienceIntelligenceEngine:
    """Canonical registry and evaluation engine for voyage experience profiles."""

    VOYAGE_EXPERIENCES: Dict[str, ExperienceProfile] = {
        "bellissima-asia-standard": ExperienceProfile(
            voyage_id="bellissima-asia-standard",
            ship_name="MSC Bellissima",
            experience_type=ExperienceType.STANDARD_CRUISE,
            charter_organizer=None,
            voyage_theme_title="Grand Voyage Ostasien · Shanghai & Japan",
            description="Klassische internationale Reiseroute mit eleganter Bordkultur, hochkarätigem Showprogramm und abendlichen Themenfesten.",
            community_highlights=[
                "Internationale Gästestruktur mit ruhiger, stilvoller Atmosphäre.",
                "Abendliche Themenabende: White Night, Gala-Abend des Kapitäns und Mediterranean Fiesta.",
                "Täglich dezent kuratierte Live-Musik von Klassik im Infinity Atrium bis Jazz in der Champagne Bar.",
            ],
            dress_guidance_summary="Tagsüber vollkommen leger. Für den heutigen Abend steht die beliebte 'White Night' auf dem Programm: Helle oder weiße Kleidung wird gern getragen, die Teilnahme ist selbstverständlich freiwillig.",
            events_schedule=[
                VoyageEvent(
                    event_id="evt:white-night-party",
                    title="White Night Deck Party & Tanz",
                    start_time="22:15 Uhr",
                    venue_name="Atmosphere Pool Deck & Horizon Bar",
                    deck_location="Deck 15 & 16 Mitte/Heck",
                    dress_code=DressCode.WHITE_NIGHT,
                    crowd_expectation="High (Sehr beliebt)",
                    description="Das offizielle Highlight des Seetags: Live-Band, Tanz und weiß illuminierte Poollandschaft unter dem Sternenhimmel.",
                    is_optional=True,
                    quieter_alternative_venue="Sky Lounge auf Deck 18 für ruhigen Panoramablick mit Klaviermusik.",
                ),
                VoyageEvent(
                    event_id="evt:theatre-show",
                    title="Broadway-Stil Show 'Solid Gold'",
                    start_time="20:00 Uhr & 21:45 Uhr",
                    venue_name="London Theatre",
                    deck_location="Deck 5 & 6 Forward (Bug)",
                    dress_code=DressCode.SMART_CASUAL,
                    crowd_expectation="High",
                    description="Hochkarätige Akrobatik- und Gesangsproduktion des internationalen MSC Ensembles.",
                    is_optional=True,
                    quieter_alternative_venue="Jean-Philippe Chocolat & Café für ruhigen Kaffeegenuss.",
                ),
                VoyageEvent(
                    event_id="evt:classical-piano",
                    title="Klassisches Duo · Chopin & Debussy",
                    start_time="19:00 Uhr",
                    venue_name="Infinity Atrium",
                    deck_location="Deck 5 Mitte",
                    dress_code=DressCode.SMART_CASUAL,
                    crowd_expectation="Quiet (Sehr entspannt)",
                    description="Dezente Klaviermusik an den funkelnden Swarovski-Treppen vor dem Dinner.",
                    is_optional=True,
                    quieter_alternative_venue=None,
                ),
            ],
            busy_areas_to_avoid=[
                "Atmosphere Pool Deck zwischen 22:00 und 23:30 Uhr (Hohe Lautstärke & Menschendichte während der White Night).",
                "London Theatre Haupteingang Deck 6 ca. 10 Minuten vor Showbeginn (Stau am Einlass; nutzen Sie den unteren Eingang Deck 5).",
                "Fotostudio Galleria Bellissima vor dem Gala-Dinner (Wartezeiten bei den offiziellen Fotowänden).",
            ],
            quiet_retreat_venues=[
                "Horizon Bar Heckdeck (Deck 16 Heck) – Windgeschützt und perfekt für ruhige Abendgespräche.",
                "Sky Lounge & Bibliothek (Deck 18 Mitte) – Sanftes Licht und Panoramablick.",
                "Private Balkonkabine 14122 – Vollkommene Ruhe mit Meeresrauschen.",
            ],
            bot_proactive_observations=[
                "BOT noticed: Heute Abend findet die White Night statt. Falls Sie teilnehmen möchten, wird helle Kleidung empfohlen.",
                "BOT noticed: Wenn Sie dem Trubel der Poolparty entgehen möchten, bietet die Sky Lounge auf Deck 18 die perfekte ruhige Alternative.",
            ],
        ),

        "music-festival-charter": ExperienceProfile(
            voyage_id="music-festival-charter",
            ship_name="MSC Bellissima",
            experience_type=ExperienceType.MUSIC_CRUISE,
            charter_organizer="Symphony at Sea Festival",
            voyage_theme_title="Symphonic & Jazz Sea Festival",
            description="Exklusiver Musik-Vollcharter mit ganztägigen Meisterkursen, Kammerkonzerten und abendlichen Open-Air-Sinfonien auf dem Pooldeck.",
            community_highlights=[
                "100% thematisch fokussierte Musik-Community mit gemeinsamen Jam-Sessions.",
                "Zusätzliche Akustikbühnen in der Galleria und im Carousel Lounge Theater.",
                "Meet & Greet Empfänge mit renommierten Dirigenten und Solisten.",
            ],
            dress_guidance_summary="Konzert-Abendgarderobe (Smart Casual bis Elegant) für die abendlichen Hauptkonzerte im London Theatre.",
            events_schedule=[
                VoyageEvent(
                    event_id="evt:main-concert",
                    title="Gala-Eröffnungskonzert: Dvořák 9. Sinfonie",
                    start_time="20:30 Uhr",
                    venue_name="London Theatre",
                    deck_location="Deck 5 & 6 Bug",
                    dress_code=DressCode.ELEGANT_GALA,
                    crowd_expectation="Very High (Ausgebucht)",
                    description="Vollbesetztes Festival-Sinfonieorchester unter Leitung renommierter Gastdirigenten.",
                    is_optional=True,
                    quieter_alternative_venue="Horizon Bar auf Deck 16 für Jazz-Trio.",
                )
            ],
            busy_areas_to_avoid=[
                "Carousel Lounge während der Meisterklassen (Kein Durchgang möglich).",
                "London Theatre Foyer 15 Minuten vor Konzertbeginn.",
            ],
            quiet_retreat_venues=[
                "Aurea Spa Thermalbereich (Deck 7 Bug)",
                "Top Sail Lounge (nur Yacht Club)",
            ],
            bot_proactive_observations=[
                "BOT noticed: Diese Reise ist ein exklusives Musik-Event. Das abendliche Haupttheater ist ca. 20 Minuten vor Beginn voll besetzt.",
            ],
        ),

        "gourmet-food-wine": ExperienceProfile(
            voyage_id="gourmet-food-wine",
            ship_name="MSC Bellissima",
            experience_type=ExperienceType.FOOD_AND_WINE,
            charter_organizer="Connoisseur Voyages",
            voyage_theme_title="Culinary Grand Tour · Sommelier & Star Chefs",
            description="Feinschmecker-Themenkreuzfahrt mit Weinverkostungen, Kochkursen bei Sterneköchen und exklusiven Menü-Abenden.",
            community_highlights=[
                "Fokus auf regionale Gastronomie und Pairing mit Spitzenweinen der besuchten Häfen.",
                "Spezialitätenrestaurants (Butcher's Cut, Kaito Teppanyaki, HOLA! Tapas) mit exklusiven Sonderkarten.",
            ],
            dress_guidance_summary="Smart Casual für alle Verkostungen; Gala-Garderobe für das 7-Gänge-Kapitäns-Gourmet-Dinner.",
            events_schedule=[
                VoyageEvent(
                    event_id="evt:wine-tasting",
                    title="Masterclass: Japanische Saké & Rebsorten",
                    start_time="16:00 Uhr",
                    venue_name="Champagne Bar",
                    deck_location="Deck 7 Galleria",
                    dress_code=DressCode.SMART_CASUAL,
                    crowd_expectation="Moderate",
                    description="Geführte Verkostung mit zertifiziertem Master-Sommelier.",
                    is_optional=True,
                )
            ],
            busy_areas_to_avoid=[
                "Galleria Bellissima während der Koch-Showcases (17:30–18:30 Uhr).",
            ],
            quiet_retreat_venues=[
                "Deck 16 Heckbereich Horizon Lounge",
            ],
            bot_proactive_observations=[
                "BOT noticed: Für die Sommelier-Verkostung um 16:00 Uhr sind alle Plätze reserviert. Einlass beginnt 10 Minuten vorher.",
            ],
        ),
    }

    @classmethod
    def get_experience_profile(cls, voyage_id: str = "bellissima-asia-standard") -> ExperienceProfile:
        return cls.VOYAGE_EXPERIENCES.get(voyage_id, cls.VOYAGE_EXPERIENCES["bellissima-asia-standard"])

    @classmethod
    def list_all_experience_profiles(cls) -> List[ExperienceProfile]:
        return list(cls.VOYAGE_EXPERIENCES.values())
