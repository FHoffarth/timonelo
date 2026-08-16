"""
Global Companion & Regret Score Engine for Timonelo (Chapter III - Sprint 05).
"Timonelo doesn't help you travel more. It helps you regret less."
Accompanies the traveler across all 8 global phases:
1. HOME -> 2. FLIGHT -> 3. HOTEL -> 4. CITY -> 5. TERMINAL -> 6. SHIP -> 7. PORT DAYS -> 8. RETURN.
Includes Travel Memory and the Timonelo Regret Score Engine.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import datetime


class CompanionPhase(str, Enum):
    PHASE_1_HOME = "1. VORBEREITUNG & HAUSTÜR"
    PHASE_2_FLIGHT = "2. FLUG & AIRPORT-TRANSIT"
    PHASE_3_HOTEL = "3. HOTEL AM STARTHAFEN"
    PHASE_4_CITY = "4. ANKUNFT & ZIELSTADT"
    PHASE_5_TERMINAL = "5. KREUZFAHRT-TERMINAL"
    PHASE_6_SHIP = "6. AN BORD (STATUSERLEBNIS)"
    PHASE_7_PORT_DAYS = "7. HAFENTAGE & LANDGANG"
    PHASE_8_RETURN = "8. RÜCKREISE & HEIMKEHR"


class RegretLevel(str, Enum):
    LOW = "LOW (Geringes Reue-Risiko · Empfohlen)"
    MODERATE = "MODERATE (Mittleres Reue-Risiko · Puffer knapp)"
    HIGH = "HIGH (Hohes Reue-Risiko · Dringend vermeiden)"


@dataclass(frozen=True)
class TravelMemory:
    traveler_id: str
    preferred_name: str
    travel_style: str
    msc_loyalty_tier: str
    airline_tier: str
    hotel_preference: str
    likes: List[str]
    dislikes: List[str]
    is_solo_traveler: bool = True
    photography_enthusiast: bool = True
    culinary_preference: str = "Asian & Mediterranean Cuisine"


@dataclass(frozen=True)
class RegretScoreEvaluation:
    scenario_title: str
    level: RegretLevel
    regret_score_pct: int  # 0 to 100% risk
    why_you_will_regret_this: List[str]
    how_to_avoid_regret: str
    confidence: float = 99.0
    evidence_source: str = "src:timonelo-historical-delay-models"


@dataclass(frozen=True)
class CompanionPhaseCard:
    phase: CompanionPhase
    phase_number: int
    headline: str
    objective_now: str
    what_to_do_now: List[str]
    negative_intelligence_to_avoid: str
    insider_rules: List[str]
    travel_memory_adaptations: List[str]
    evidence_sources: List[str]
    confidence_score: float = 98.5


class RegretScoreEngine:
    """Calculates deterministic Regret Scores for travel decisions."""

    @classmethod
    def evaluate_flight_arrival_timing(
        cls,
        arrival_date_same_day: bool,
        arrival_time_str: str,
        departure_time_str: str,
        city_name: str = "Shanghai",
    ) -> RegretScoreEvaluation:
        if arrival_date_same_day:
            return RegretScoreEvaluation(
                scenario_title=f"Flugankunft am selben Tag ({arrival_time_str}) bei Schiffsabfahrt ({departure_time_str}) in {city_name}",
                level=RegretLevel.HIGH,
                regret_score_pct=92,
                why_you_will_regret_this=[
                    "Internationale Passkontrolle und Einreiseformular-Prüfung dauern bei Großraumflugzeugen 45–90 Minuten.",
                    "Gepäckausgabe und Zoll in Pudong (PVG) erfordern weitere 30–45 Minuten.",
                    "Fahrzeit nach Baoshan/Wusongkou beträgt 75–100 Minuten durch den Berufsverkehr.",
                    "Bei nur 90 Minuten Flugverspätung wird das Terminal-Check-in-Fenster (15:30 Uhr) verpasst.",
                    "Kein Puffertag bei Koffer-Fehlleitung durch die Airline.",
                ],
                how_to_avoid_regret="Flug mindestens 24 Stunden vor dem Einschiffungstag buchen und eine entspannte Hotelübernachtung in Starthafennähe einlegen.",
                confidence=99.5,
                evidence_source="src:shanghai-airport-authority",
            )
        else:
            return RegretScoreEvaluation(
                scenario_title=f"Anreise am Vortag mit Übernachtung im Hotel (z.B. Hyatt on the Bund / Baoshan)",
                level=RegretLevel.LOW,
                regret_score_pct=8,
                why_you_will_regret_this=[
                    "Sehr geringes Risiko: Selbst mehrstündige Flugverspätungen gefährden die Einschiffung nicht.",
                    "Ausgeschlafener Start in den Urlaub ohne Jetlag-Erschöpfung am ersten Seetag.",
                    "Entspannte Anreise zum Terminal um 11:00 Uhr vor dem Hauptansturm.",
                ],
                how_to_avoid_regret="Alles richtig gemacht: Zimmer mit Late Check-out oder direktem Terminaltransfer buchen.",
                confidence=99.0,
                evidence_source="src:field-audit-2026",
            )


class GlobalCompanionEngine:
    """Generates the full 8-phase global companion briefing tailored to traveler memory."""

    @classmethod
    def get_reference_memory_flo(cls) -> TravelMemory:
        return TravelMemory(
            traveler_id="flo-founder",
            preferred_name="Flo",
            travel_style="Bespoke Efficiency & Acoustic Sanctuary",
            msc_loyalty_tier="Diamond",
            airline_tier="Star Alliance Gold / Miles & More Senator",
            hotel_preference="Hyatt / Premium Boutique",
            likes=[
                "Balkonkabinen mit freier Sicht",
                "Ruhige Aft-Lounges & Heck-Sonnendecks",
                "Premium Economy / Business Langstrecke",
                "Authentisches asiatisches Dining & Ramen/Dim Sum",
                "Fotografie im goldenen Morgenlicht",
                "Schnelle, stufenfreie Fußwege ohne Schlangen",
            ],
            dislikes=[
                "Überfüllte Buffet-Gänge mit Rollkoffern",
                "Lange Schlangen vor Theatertüren und Fahrstühlen",
                "Unnötige Wartezeiten bei Terminal-Transfers",
                "Laute Pooldeck-Animation am Seetag",
            ],
            is_solo_traveler=True,
            photography_enthusiast=True,
            culinary_preference="Asian Fine Dining & Japanese Ramen",
        )

    @classmethod
    def generate_8_phase_journey(
        cls,
        memory: TravelMemory,
        ship_name: str = "MSC Bellissima",
        cabin_num: str = "14122",
        start_city: str = "Shanghai",
        end_city: str = "Tokio (Yokohama)",
    ) -> List[CompanionPhaseCard]:
        cards: List[CompanionPhaseCard] = []

        # Phase 1: Home
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_1_HOME,
            phase_number=1,
            headline="Haustür-Checkliste & Dokumenten-Souveränität",
            objective_now="Reisepass, Visa-Exemption, Reiseapotheke & Zahlungsmittel sichern",
            what_to_do_now=[
                "Reisepass-Gültigkeit prüfen: Mindestens 6 Monate Restgültigkeit über das Rückreisedatum hinaus.",
                "Zahlungs-Setup: Alipay & WeChat Pay vorab auf dem Smartphone installieren und Kreditkarte verknüpfen (Bargeld wird in China kaum noch akzeptiert).",
                "eSIM & VPN: Airalo / Holafly (mit integriertem VPN) vorab auf dem Smartphone installieren, um Google/WhatsApp in Shanghai nutzen zu können.",
                "Reiseapotheke & Stecker: Typ-I Adapter für Shanghai und Typ-A für Japan einpacken; wichtige Medikamente ins Handgepäck.",
            ],
            negative_intelligence_to_avoid="Niemals ohne vorab eingerichtetes Alipay/WeChat nach China reisen: Ausländische Kreditkarten werden an Taxiständen und Kiosken zu 90% abgelehnt.",
            insider_rules=[
                "Auslandskrankenversicherungspolice digital als PDF auf dem Smartphone speichern.",
                "Fototasche mit Objektiven als separates Personal Item deklarieren.",
            ],
            travel_memory_adaptations=[
                f"Da {memory.preferred_name} gerne fotografiert: Ersatz-Speicherkarten und Objektiv-Reinigungstücher ins Handgepäck packen."
            ],
            evidence_sources=["src:auswaertiges-amt-china-2026", "src:mofa-japan-official"],
        ))

        # Phase 2: Flight
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_2_FLIGHT,
            phase_number=2,
            headline="Flug & Lounge-Erlebnis",
            objective_now="Senator Lounge nutzen -> Fast Track Security -> Entspannter Langstreckenflug",
            what_to_do_now=[
                "Lufthansa Senator / Star Alliance Gold Lounge am Abflughafen (FRA) für Ruhe und Frühstück nutzen.",
                "Priority Boarding & Fast Lane Security durch Senator-Status in Anspruch nehmen.",
                "Zoll- und Ankunftskarte für China bereits im Flugzeug ausfüllen, um Wartezeit an der Immigration zu minimieren.",
            ],
            negative_intelligence_to_avoid="Keine Powerbanks ohne sichtbare mAh/CE-Kennzeichnung mitnehmen; chinesische Luftsicherheitskontrollen konfiszieren unbeschriftete Akkus ausnahmslos.",
            insider_rules=[
                "Flugzeug-Sitzplatz in vorderen Reihen wählen, um als einer der Ersten an der Immigration-Warteschlange zu sein."
            ],
            travel_memory_adaptations=[
                f"{memory.preferred_name} schätzt Ruhe: Lounge-Aufenthalt vor Abflug und Priority Baggage Delivery."
            ],
            evidence_sources=["src:miles-and-more-terms", "src:shanghai-airport-authority"],
        ))

        # Phase 3: Hotel
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_3_HOTEL,
            phase_number=3,
            headline="Vorabend-Hotel (z.B. Hyatt on the Bund / Baoshan)",
            objective_now="Ausschlafen -> Ausblick auf die Skyline -> Entspannter Transfer zum Hafen",
            what_to_do_now=[
                "Hotel-Check-in mit Reisepass durchführen (Hotel registriert Gäste automatisch bei der örtlichen Polizei).",
                "Frühstück im Hotel genießen und Late Check-out bis 12:00 Uhr vormerken lassen.",
                "Didi Taxi zur Baoshan Wusongkou Cruise Terminal vorab für 11:00 Uhr rufen.",
            ],
            negative_intelligence_to_avoid="Niemals spontan am Einschiffungsmorgen ein Hotel ohne vorherige Buchung suchen; beliebte Hotels am Bund sind oft ausgebucht.",
            insider_rules=[
                "Hoteladresse auf Chinesisch an der Rezeption auf eine Visitenkarte schreiben lassen."
            ],
            travel_memory_adaptations=[
                f"Passend zu {memory.preferred_name}'s Vorliebe für Hyatt & Fotografie: Hyatt on the Bund bietet die beste Dachterrassen-Sicht auf Pudong."
            ],
            evidence_sources=["src:field-audit-2026", "src:port-authority-shanghai"],
        ))

        # Phase 4: City
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_4_CITY,
            phase_number=4,
            headline="Shanghai Orientierung & Scam-Schutz",
            objective_now="Lokale Mobilität via Metro/Didi -> Streetfood & Bund-Spaziergang",
            what_to_do_now=[
                "Didi Mini-Program in Alipay für alle Taxifahrten nutzen (Preise sind fest vorgegeben und bargeldlos).",
                "Apple Maps oder Amap zur Navigation nutzen (Google Maps hat in Festlandchina GPS-Verschiebungen und Offline-Einschränkungen).",
                "Notruf-Nummern kennen: Polizei 110, Notarzt 120.",
            ],
            negative_intelligence_to_avoid="Teehaus-Scam & inoffizielle Taxifahrer am Bund: Lehnen Sie Einladungen von fremden 'Studenten' zu Tee-Zeremonien strikt ab.",
            insider_rules=[
                "Metro Shanghai ist extrem pünktlich und sauber; QR-Code-Scannen in Alipay öffnet die Schranken direkt."
            ],
            travel_memory_adaptations=[
                f"{memory.preferred_name} liebt asiatisches Essen: Din Tai Fung (Xiao Long Bao) oder traditionelle Nudel-Restaurants am Bund besuchen."
            ],
            evidence_sources=["src:field-audit-2026", "src:auswaertiges-amt-china-2026"],
        ))

        # Phase 5: Terminal
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_5_TERMINAL,
            phase_number=5,
            headline="Wusongkou Cruise Terminal Logistik",
            objective_now="Porter Gepäckabgabe -> VIP-Check-in -> Reibungslose Einschiffung",
            what_to_do_now=[
                "Ankunft am Terminal um 11:15 Uhr vor der großen Reisegruppen-Welle.",
                "Große Koffer an Gate 2 abgeben (MSC Kofferanhänger für Kabine 14122 muss befestigt sein).",
                "MSC Voyagers Club Diamond Priority Line für die Sicherheits- und Passkontrolle nutzen.",
            ],
            negative_intelligence_to_avoid="Nicht in die reguläre Economy-Schlange einreihen: Diamond-Status berechtigt zum direkten Fast-Track-Schalter.",
            insider_rules=[
                "Reisepass und Boarding Pass physisch in der Hand halten; Fotos auf dem Smartphone verlangsamen die Scanner."
            ],
            travel_memory_adaptations=[
                f"Vermeidet Warteschlangen: {memory.preferred_name} nutzt den Diamond-Priority-Check-in und ist in unter 15 Minuten durch das Terminal."
            ],
            evidence_sources=["src:port-authority-shanghai", "src:msc-voyagers-club-terms"],
        ))

        # Phase 6: Ship
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_6_SHIP,
            phase_number=6,
            headline=f"An Bord von {ship_name} · Kabine {cabin_num}",
            objective_now="Posidonia Lunch -> Diamond Perks aktivieren -> Sicherheitsübung am TV",
            what_to_do_now=[
                "Direkt auf Deck 5 ins Posidonia Restaurant gehen (Mittagessen à la carte ohne Rollkoffer-Gedränge).",
                "Um 14:00 Uhr Kabine 14122 beziehen: Willkommens-Prosecco & Macarons (Diamond Perk) genießen.",
                "Muster Drill am Fernseher in 4 Minuten abschließen und bei Musterstation kurz scannen lassen.",
                "Kostenloses Diamond-Dinner im Butcher's Cut oder Kaito Teppanyaki reservieren.",
            ],
            negative_intelligence_to_avoid="Marktplatz-Buffet Deck 15 am Einschiffungstag meiden (90% der Gäste drängen sich dort). Muster Drill nicht bis 16:30 Uhr aufschieben.",
            insider_rules=[
                "Kostenlose 1-stündige Thermal-Spa-Session für den ersten Seetag an der Aurea Spa Rezeption vormerken."
            ],
            travel_memory_adaptations=[
                f"{memory.preferred_name}'s Kabine 14122 (Aft Starboard): Nur 24.6 m zum hinteren Aufzugskern, direkter Zugang zur Horizon Bar Deck 16."
            ],
            evidence_sources=["src:msc-voyagers-club-terms", "src:chantiers-atlantique-ga"],
        ))

        # Phase 7: Port Days
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_7_PORT_DAYS,
            phase_number=7,
            headline=f"Hafentag Tokio / Yokohama · Landgang",
            objective_now="Frühstück mit Hafenblick -> Staufreier Landgang 09:15 -> Minatomirai & Tokio",
            what_to_do_now=[
                "Schiff legt um 05:30 Uhr an; entspanntes Frühstück auf dem Balkon oder Restaurant bis 08:45 Uhr.",
                "Um 09:15 Uhr über Gangway staufrei von Bord gehen.",
                "Suica IC-Card auf Apple Wallet nutzen für Minatomirai Line nach Yokohama Station und weiter nach Tokio (Shibuya/Ginza).",
                "Rechtzeitig vor 'Alle Mann an Bord' (17:30 Uhr) am Pier zurück sein.",
            ],
            negative_intelligence_to_avoid="Keine Taxis für lange Strecken zwischen Tokio und Yokohama nehmen (Kosten > 100 €); die Bahnverbindung ist dreimal schneller und kostet nur ~4 €.",
            insider_rules=[
                "Große Bahnhöfe haben Coin Lockers (Gepäckschließfächer) für Tagesrucksäcke."
            ],
            travel_memory_adaptations=[
                f"Fotografie-Empfehlung für {memory.preferred_name}: Osanbashi Pier Dachpromenade (Kujira-no-Senaka) bietet den besten Blick auf die Yokohama-Skyline beim Auslaufen."
            ],
            evidence_sources=["src:port-authority-yokohama", "src:japan-coast-guard"],
        ))

        # Phase 8: Return
        cards.append(CompanionPhaseCard(
            phase=CompanionPhase.PHASE_8_RETURN,
            phase_number=8,
            headline="Ausschiffung & Teil 2 der Reise (Heimflug Tokio)",
            objective_now="Late Stateroom Check-out -> Diamond Express Disembarkation -> Haneda Lounge",
            what_to_do_now=[
                "Als Diamond-Gast Kabine bis 09:00 Uhr nutzen (Late Check-out).",
                "Bevorzugte Ausschiffung nutzen und Koffer in der Terminal-Halle abholen.",
                "Keikyu Line oder Airport Limousine Bus direkt zum Flughafen Tokio Haneda (HND) nehmen.",
                "Tax-Free Belege am Flughafen scannen und vor dem Rückflug die Star Alliance / ANA Lounge nutzen.",
            ],
            negative_intelligence_to_avoid="Nicht vor dem eigenen Farbcode an den Ausgang drängen; Fahrstühle sind zwischen 07:30 und 08:30 Uhr für Kofferabtransporte stark ausgelastet.",
            insider_rules=[
                "Japanische Mehrwertsteuer (Tax Free) wird direkt beim Einkauf abgezogen; am Flughafen Haneda muss nur der Pass an den Zoll-Terminals gescannt werden."
            ],
            travel_memory_adaptations=[
                f"{memory.preferred_name} fliegt entspannt zurück: Diamond Late Check-out an Bord + ANA Lounge Haneda mit frisch zubereiteter Ramen-Bar."
            ],
            evidence_sources=["src:msc-voyagers-club-terms", "src:tokyo-haneda-airport"],
        ))

        return cards
