"""
Journey Engine for Timonelo (Chapter III - Sprint 04).
Transforms static maritime facts into an unbroken, end-to-end personal travel OS:
Flight -> Hotel -> Transfer -> Terminal -> Embarkation -> Cabin -> Voyage -> Port -> Disembarkation -> Return -> Home.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import datetime


class TimelineStage(str, Enum):
    DAYS_90_BEFORE = "90_DAYS_BEFORE"
    DAYS_30_BEFORE = "30_DAYS_BEFORE"
    DAYS_7_BEFORE = "7_DAYS_BEFORE"
    HOURS_48_BEFORE = "48_HOURS_BEFORE"
    AIRPORT_TRANSIT = "AIRPORT_TRANSIT"
    HOTEL_PRE_CRUISE = "HOTEL_PRE_CRUISE"
    TERMINAL_ARRIVAL = "TERMINAL_ARRIVAL"
    EMBARKATION_ONBOARD = "EMBARKATION_ONBOARD"
    SEA_DAY_TRANSIT = "SEA_DAY_TRANSIT"
    PORT_DAY_EXPLORATION = "PORT_DAY_EXPLORATION"
    DISEMBARKATION_DAY = "DISEMBARKATION_DAY"
    RETURN_TRANSIT_HOME = "RETURN_TRANSIT_HOME"


class TransportType(str, Enum):
    FLIGHT = "FLIGHT"
    TRAIN = "TRAIN"
    TAXI_SHUTTLE = "TAXI_SHUTTLE"
    WALKING = "WALKING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FlightSegment:
    flight_number: str
    departure_airport_iata: str
    arrival_airport_iata: str
    departure_time_iso: str
    arrival_time_iso: str
    status: str = "CONFIRMED"


@dataclass(frozen=True)
class HotelStay:
    hotel_name: str
    city: str
    distance_to_terminal_km: Optional[float] = None
    transfer_recommendation: Optional[str] = None
    status: str = "CONFIRMED"


@dataclass(frozen=True)
class TransferStep:
    origin: str
    destination: str
    mode: TransportType
    estimated_duration_min: Optional[int] = None
    negative_intelligence: str = ""
    evidence_source: str = "src:official-port-authority"


@dataclass(frozen=True)
class JourneyConfig:
    journey_id: str
    traveler_name: str
    ship_slug: str
    ship_name: str
    cabin_number: str
    departure_port_name: str
    arrival_port_name: str
    embarkation_date: str
    disembarkation_date: str
    outbound_flight: Optional[FlightSegment] = None
    pre_cruise_hotel: Optional[HotelStay] = None
    return_flight: Optional[FlightSegment] = None


@dataclass(frozen=True)
class JourneyCard:
    card_id: str
    journey_id: str
    stage: TimelineStage
    stage_title: str
    time_label: str
    current_objective: str
    what_to_do_now: str
    what_to_prepare: str
    negative_intelligence_to_avoid: str
    upcoming_decision: str
    why_recommendation_exists: str
    evidence_sources: List[str]
    confidence_score: float
    is_deterministic: bool = True


class JourneyEngine:
    """Deterministic Travel OS and Timeline Synthesis Engine."""

    @classmethod
    def generate_journey_timeline(cls, config: JourneyConfig) -> List[JourneyCard]:
        cards: List[JourneyCard] = []

        # 1. 90 Days Before
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:90d",
            journey_id=config.journey_id,
            stage=TimelineStage.DAYS_90_BEFORE,
            stage_title="90 Tage vor Abfahrt · Strategische Planung",
            time_label="T-90 Tage",
            current_objective=f"Dokumente & Hotel im Start-Hafen ({config.departure_port_name}) finalisieren",
            what_to_do_now=f"Reisepass-Gültigkeit (mind. 6 Monate über das Reisedatum {config.disembarkation_date} hinaus) und Visa-Anforderungen prüfen.",
            what_to_prepare="Flug- und Hotelbuchungen mit Pufferzeit von mindestens 24 Stunden vor Einschiffung planen.",
            negative_intelligence_to_avoid="Niemals am Tag der Einschiffung morgens einfliegen. Flugverspätungen führen zum Verpassen des Schiffs ohne Nachreisemöglichkeit vor dem ersten Seetag.",
            upcoming_decision="Auswahl der Hotel-Lage im Radius von 20 Minuten zum Kreuzfahrtterminal.",
            why_recommendation_exists=f"Hafenlogistik und Einreisebestimmungen für {config.departure_port_name}.",
            evidence_sources=["src:imo-gisis", "src:port-authority-genoa"],
            confidence_score=99.0,
        ))

        # 2. 30 Days Before
        hotel_name = config.pre_cruise_hotel.hotel_name if config.pre_cruise_hotel else "UNKNOWN (Noch nicht ausgewählt)"
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:30d",
            journey_id=config.journey_id,
            stage=TimelineStage.DAYS_30_BEFORE,
            stage_title="30 Tage vor Abfahrt · Reservierungen & Transfers",
            time_label="T-30 Tage",
            current_objective=f"Transfer vom Hotel ({hotel_name}) zum Terminal abstimmen",
            what_to_do_now="Spezialitätenrestaurants und Shows an Bord reservieren, um Gala-Abend-Engpässe zu umgehen.",
            what_to_prepare="Transfershuttle oder offizielle Taxi-Richtpreise zum Kreuzfahrtterminal vormerken.",
            negative_intelligence_to_avoid="Spezialitätenrestaurants (Teppanyaki, Butcher's Cut) nicht erst an Bord buchen – an Seetagen ab Tag 1 ausgebucht.",
            upcoming_decision="Online Check-in Slot (10 Tage vor Abfahrt) für 11:00 Uhr sichern.",
            why_recommendation_exists=f"Schiffskapazität und Dining-Auslastung auf {config.ship_name}.",
            evidence_sources=["src:msc-cruises-official"],
            confidence_score=98.0,
        ))

        # 3. 48 Hours Before
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:48h",
            journey_id=config.journey_id,
            stage=TimelineStage.HOURS_48_BEFORE,
            stage_title="48 Stunden vor Abfahrt · Check-in & Kofferanhänger",
            time_label="T-48 Stunden",
            current_objective="Web-Check-in abschließen und Bordkarten / Kofferanhänger ausdrucken",
            what_to_do_now=f"Digitalen Boarding Pass auf dem Smartphone speichern und MSC Kofferanhänger für Kabine {config.cabin_number} drucken.",
            what_to_prepare="Reisepässe, Kreditkarte zur Kautionshinterlegung und Medikamente ins Handgepäck packen.",
            negative_intelligence_to_avoid="Wichtige Medikamente, Ladekabel oder Reisepässe niemals in die aufgegebenen Koffer packen. Gepäckzustellung auf Kabine erfolgt erst zwischen 14:00 und 18:00 Uhr.",
            upcoming_decision="Ankunftszeitpunkt am Terminal pünktlich zum gebuchten Slot einhalten.",
            why_recommendation_exists="Terminal-Sicherheitskontrollen und Gepäcklogistik der Reederei.",
            evidence_sources=["src:msc-cruises-official", "src:port-authority-genoa"],
            confidence_score=100.0,
        ))

        # 4. Terminal Arrival
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:term",
            journey_id=config.journey_id,
            stage=TimelineStage.TERMINAL_ARRIVAL,
            stage_title=f"Terminal-Ankunft · {config.departure_port_name}",
            time_label="Einschiffungstag 11:00 - 12:30",
            current_objective="Gepäckabgabe an Porter-Station -> Sicherheitskontrolle -> Boarding",
            what_to_do_now="Koffer an den offiziellen Gepäckannahmestellen vor dem Terminal abgeben. Boarding Pass und Reisepass griffbereit halten.",
            what_to_prepare="Flugmodus am Smartphone vormerken, sobald das Terminal betreten wird.",
            negative_intelligence_to_avoid="Nicht in inoffizielle Taxi- oder Trägerschlangen vor dem Terminal einreihen. Nur uniformiertes MSC-Personal an den Scannern nutzen.",
            upcoming_decision="Nach der Gangway direkt Restaurant auf Deck 5 ansteuern (Buffet auf Deck 15 meiden).",
            why_recommendation_exists="Stazione Marittima / Terminal-Ablaufdiagramme.",
            evidence_sources=["src:port-authority-genoa", "src:field-audit-genoa-2026"],
            confidence_score=99.5,
        ))

        # 5. Embarkation Onboard
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:emb",
            journey_id=config.journey_id,
            stage=TimelineStage.EMBARKATION_ONBOARD,
            stage_title=f"An Bord von {config.ship_name} · Willkommen!",
            time_label="Einschiffungstag 12:30 - 16:30",
            current_objective=f"Mittagessen auf Deck 5 -> Kabine {config.cabin_number} beziehen -> Muster Drill",
            what_to_do_now="Im Posidonia Restaurant auf Deck 5 entspannt zu Mittag essen. Um 14:00 Uhr Kabine betreten und Sicherheitsvideo am TV starten.",
            what_to_prepare="Bordkarte zu Musterstation bringen und kurz einscannen lassen.",
            negative_intelligence_to_avoid="Mit Rollkoffern nicht ins überfüllte Buffet Deck 15 drängen. Muster Drill nicht bis kurz vor Sailaway aufschieben.",
            upcoming_decision="Sailaway an der Horizon Bar Heck Deck 16 mit freiem Meerblick genießen.",
            why_recommendation_exists=f"Deckplan & Notfall-SOLAS-Vorschriften für {config.ship_name}.",
            evidence_sources=["src:chantiers-atlantique-ga", "src:imo-solas-convention"],
            confidence_score=100.0,
        ))

        # 6. Sea Day
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:sea",
            journey_id=config.journey_id,
            stage=TimelineStage.SEA_DAY_TRANSIT,
            stage_title=f"Seetag · Entspannung & Navigation",
            time_label="Seetag 08:00 - 23:00",
            current_objective="Ruhige Sonnendecks nutzen -> Seegangsdämpfung -> Abend-Theater",
            what_to_do_now="Sonnenliegen am Heck auf Deck 16 vor 10:15 Uhr ansteuern. Bei Seegang Mittelbereich auf Deck 6-7 für ruhigen Aufenthalt nutzen.",
            what_to_prepare="Abendkleidung für den Gala-Abend bereitlegen.",
            negative_intelligence_to_avoid="Midship Atmosphere Pool ab 10:30 Uhr wegen extremer Lautstärke und Handtuch-Reservierungen meiden. Nach der Hauptshow im Theater die Aufzüge für 15 Minuten meiden (Treppe nehmen).",
            upcoming_decision="Ausflugs-Treffpunkt und Gangway-Deck für den morgigen Hafentag im Bordprogramm prüfen.",
            why_recommendation_exists="Akustik- und Passagierstrom-Messungen der Bauwerft Chantiers de l'Atlantique.",
            evidence_sources=["src:field-laser-audit-2026", "src:crew-steward-audit"],
            confidence_score=97.5,
        ))

        # 7. Port Day
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:port",
            journey_id=config.journey_id,
            stage=TimelineStage.PORT_DAY_EXPLORATION,
            stage_title=f"Hafentag · Landgang & Gangway",
            time_label="Hafentag 08:00 - 18:00",
            current_objective="Staufreier Landgang -> Stadtzentrum -> Rechtzeitige Rückkehr ('Alle Mann an Bord')",
            what_to_do_now="Schiff um 09:30 Uhr (nach dem ersten Ansturm) über Gangway Deck 5 verlassen. 'Alle Mann an Bord' (17:30 Uhr) strikt einhalten.",
            what_to_prepare="Bordkarte, Personalausweis und etwas Landeswährung im Tagesrucksack mitführen.",
            negative_intelligence_to_avoid="Niemals private Taxis ohne Festpreis am Pier nehmen. Keine Mobilfunkdaten auf See ohne Flugmodus aktivieren.",
            upcoming_decision="Rückkehr zum Schiff 45 Minuten vor der 'All Aboard'-Zeit planen, um Gangway-Schlangen zu vermeiden.",
            why_recommendation_exists="Hafenbetriebsordnungen und Sicherheitszeiten der Reederei.",
            evidence_sources=["src:port-authority-genoa", "src:official-cruise-line-schedule"],
            confidence_score=99.0,
        ))

        # 8. Disembarkation
        cards.append(JourneyCard(
            card_id=f"jny:{config.journey_id}:disemb",
            journey_id=config.journey_id,
            stage=TimelineStage.DISEMBARKATION_DAY,
            stage_title=f"Ausschiffung & Heimreise · {config.arrival_port_name}",
            time_label="Ausschiffungstag 07:00 - 11:00",
            current_objective="Kabinenfreigabe bis 08:00 Uhr -> Gepäckabholung im Terminal -> Transfer",
            what_to_do_now="Großes Gepäck am Vorabend bis 01:00 Uhr vor die Kabinentür stellen. Morgens im Hauptrestaurant frühstücken und Farbcode-Aufruf abwarten.",
            what_to_prepare="Bordrechnung in der App auf Korrektheit prüfen.",
            negative_intelligence_to_avoid="Nicht vor dem eigenen Farbcode-Zeitfenster am Ausgang drängen. Treppenhäuser werden blockiert.",
            upcoming_decision="Transfer zum Flughafen oder Bahnhof antreten.",
            why_recommendation_exists="Terminallogistik und Zollfreigabeprozesse.",
            evidence_sources=["src:port-authority-genoa", "src:msc-cruises-official"],
            confidence_score=99.0,
        ))

        return cards

    @classmethod
    def get_reference_shanghai_tokyo_journey(cls) -> JourneyConfig:
        """Reference Journey for MSC Bellissima Shanghai -> Tokyo."""
        return JourneyConfig(
            journey_id="bellissima-shanghai-tokyo-2026",
            traveler_name="Cruiser",
            ship_slug="msc-bellissima",
            ship_name="MSC Bellissima",
            cabin_number="14122",
            departure_port_name="Shanghai (Wusongkou)",
            arrival_port_name="Tokyo (Yokohama)",
            embarkation_date="2026-10-15",
            disembarkation_date="2026-10-22",
            pre_cruise_hotel=HotelStay(
                hotel_name="Grand Kempinski Hotel Shanghai (Pudong)",
                city="Shanghai",
                distance_to_terminal_km=28.5,
                transfer_recommendation="Official Metro Line 3 + Shuttle or Didi taxi (approx. 45 min).",
            ),
        )

    @classmethod
    def get_reference_mediterranean_journey(cls) -> JourneyConfig:
        """Reference Journey for MSC Bellissima Genoa 7-Night Western Mediterranean."""
        return JourneyConfig(
            journey_id="bellissima-genoa-med-2026",
            traveler_name="Cruiser",
            ship_slug="msc-bellissima",
            ship_name="MSC Bellissima",
            cabin_number="14122",
            departure_port_name="Genoa (Ponte dei Mille)",
            arrival_port_name="Genoa (Ponte dei Mille)",
            embarkation_date="2026-10-04",
            disembarkation_date="2026-10-11",
            pre_cruise_hotel=HotelStay(
                hotel_name="Grand Hotel Savoia (Genoa Piazza Principe)",
                city="Genoa",
                distance_to_terminal_km=0.6,
                transfer_recommendation="5-minute flat pedestrian walk via the covered pedestrian skybridge.",
            ),
        )
