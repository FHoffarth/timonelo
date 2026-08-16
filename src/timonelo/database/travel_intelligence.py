"""
Travel Intelligence Engine for Timonelo (Chapter III - Sprint 03).
Prescriptive, time-aware and phase-aware cruise companion:
Transforms static maritime facts into "What should I do RIGHT NOW?" action cards
powered by Negative Intelligence (avoiding lines, noise, bottlenecks, and regret).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib


class JourneyPhase(str, Enum):
    PRE_CRUISE = "PRE_CRUISE"           # 30 Tage bis 1 Tag vor Abfahrt
    EMBARKATION_DAY = "EMBARKATION_DAY" # Ankunft im Hafen, Boarding, Muster Drill
    SEA_DAY = "SEA_DAY"                 # Seetag, Pooldeck, Dining, Shows
    PORT_DAY = "PORT_DAY"               # Anlegen, Gangway, Landgang, Alle Mann an Bord
    DISEMBARKATION = "DISEMBARKATION"   # Letzter Abend, Kofferabgabe, Ausschiffung


class ActionUrgency(str, Enum):
    NOW = "JETZT HANDELN"
    UPCOMING = "DEMNÄCHST BEACHTEN"
    PRO_TIP = "INSIDER-TIPP"


@dataclass(frozen=True)
class TravelActionCard:
    action_id: str
    phase: JourneyPhase
    time_window: str
    urgency: ActionUrgency
    headline: str
    what_to_do_now: str
    negative_intelligence_to_avoid: str
    reasons_top_3: List[str]
    concrete_steps: List[str]
    evidence_sources: List[str]
    confidence_score: float = 98.0
    is_deterministic: bool = True


class TravelIntelligenceEngine:
    """Computes deterministic, phase-specific prescriptive travel actions."""

    ACTIONS_CATALOGUE = [
        # --- EMBARKATION DAY ---
        TravelActionCard(
            action_id="act:emb:buffet-bypass",
            phase=JourneyPhase.EMBARKATION_DAY,
            time_window="12:00 - 14:30",
            urgency=ActionUrgency.NOW,
            headline="Marktplatz-Buffet auf Deck 15 meiden",
            what_to_do_now="Gehen Sie nach dem Betreten des Schiffes direkt in das Posidonia Restaurant auf Deck 5 oder die Carousel Lounge statt auf Deck 15.",
            negative_intelligence_to_avoid="90% der Passagiere strömen mit Handgepäck auf Deck 15. Überfüllung, Wartezeiten an den Ausgaben und extreme Lautstärke.",
            reasons_top_3=[
                "Posidonia Restaurant bietet ruhiges 3-Gänge-À-la-carte-Mittagessen ohne Tischsuche mit Gepäck.",
                "Kein Warten mit Rollkoffern in engen Buffet-Gängen.",
                "Erhöhte Gepäcksicherheit und entspannter Einstieg in den ersten Urlaubstag."
            ],
            concrete_steps=[
                "Nach der Gangway auf Deck 5 bleiben (nicht die Aufzüge zu Deck 15 nehmen).",
                "Im Posidonia Restaurant melden und entspannt Platz nehmen.",
                "Warten, bis um 14:00 Uhr die Kabinenfreigabe per Borddurchsage erfolgt."
            ],
            evidence_sources=["src:field-audit-genoa-2026", "src:msc-cruises-official", "src:crew-steward-audit"],
            confidence_score=99.0,
        ),
        TravelActionCard(
            action_id="act:emb:muster-drill",
            phase=JourneyPhase.EMBARKATION_DAY,
            time_window="14:00 - 16:30",
            urgency=ActionUrgency.NOW,
            headline="Sicherheitsübung sofort nach Kabinenfreigabe abschließen",
            what_to_do_now="Starten Sie das Sicherheitsvideo sofort nach Betreten der Kabine auf dem Fernseher und gehen Sie direkt zur Musterstation.",
            negative_intelligence_to_avoid="Wer bis 16:30 Uhr wartet, blockiert den Sailaway und wird namentlich aufgerufen. Treppenhäuser vor Auslaufen überlastet.",
            reasons_top_3=[
                "Dauert nur 4 Minuten auf der Kabine plus 1 Minute Karte scannen.",
                "Danach uneingeschränkte Freiheit für das Auslaufen auf dem Oberdeck.",
                "Vermeidet Warteschlangen vor den Scannern der Crew an den Musterstationen."
            ],
            concrete_steps=[
                "In Kabine 14122 gehen, TV einschalten und Notfall-Briefing starten.",
                "Bordtelefon abheben und Bestätigungscode wählen.",
                "Mit Bordkarte zu Musterstation A (Deck 6 Theater) gehen und kurz scannen lassen."
            ],
            evidence_sources=["src:imo-solas-convention", "src:msc-cruises-official"],
            confidence_score=100.0,
        ),

        # --- SEA DAY ---
        TravelActionCard(
            action_id="act:sea:pooldeck-bottleneck",
            phase=JourneyPhase.SEA_DAY,
            time_window="10:00 - 15:00",
            urgency=ActionUrgency.NOW,
            headline="Atmosphere Pooldeck meiden – Aft Horizon Bar wählen",
            what_to_do_now="Weichen Sie für Sonnenbaden und Ruhe auf das Horizon-Sonnendeck am Heck (Deck 16) oder das Aurea-Sonnendeck auf Deck 19 aus.",
            negative_intelligence_to_avoid="Midship Atmosphere Pool (Deck 15) hat ab 10:15 Uhr 100% Liegenbelegung, laute Animationsmusik und lange Barschlangen.",
            reasons_top_3=[
                "Heckbereich auf Deck 16 bietet freien Meerblick über das Kielwasser und deutlich geringeren Lärmpegel.",
                "Eigene Bar ohne Schlangenbildung und direkte Nähe zu den Heck-Aufzügen.",
                "Bester Windschutz bei Seegang durch die rückwärtige Aufbauten-Geometrie."
            ],
            concrete_steps=[
                "Mit den hinteren Aufzügen auf Deck 16 fahren.",
                "Durch den Horizon-Poolbereich direkt zu den Heckliegen gehen.",
                "Handtücher an der Horizon Bar abholen."
            ],
            evidence_sources=["src:field-laser-audit-2026", "src:chantiers-atlantique-ga"],
            confidence_score=97.5,
        ),
        TravelActionCard(
            action_id="act:sea:theatre-reservations",
            phase=JourneyPhase.SEA_DAY,
            time_window="16:00 - 18:00",
            urgency=ActionUrgency.UPCOMING,
            headline="Theater-Vorstellung für 20:00 Uhr vorab reservieren",
            what_to_do_now="Buchen Sie über die MSC for Me Touchscreens oder die Smartphone-App Ihren Sitzplatz für die Abendshow im London Theatre.",
            negative_intelligence_to_avoid="Ohne Reservierung wird der Einlass 10 Minuten vor Showbeginn verweigert. Einlass-Stau vor den Theatertüren auf Deck 6.",
            reasons_top_3=[
                "Garantierter Sitzplatz ohne 30 Minuten früheres Anstehen vor der Tür.",
                "Ermöglicht entspanntes Abendessen im Hauptrestaurant um 18:30 Uhr.",
                "Plätze im vorderen Parkett sind für App-Reservierer optimiert."
            ],
            concrete_steps=[
                "MSC for Me App öffnen oder Touchscreen auf Deck 14 neben Aufzug nutzen.",
                "Event 'London Theatre Production' wählen und Showzeit bestätigen.",
                "10 Minuten vor Beginn am Eingang Deck 6 Bordkarte kurz vorzeigen."
            ],
            evidence_sources=["src:msc-cruises-official", "src:crew-steward-audit"],
            confidence_score=98.5,
        ),

        # --- PORT DAY ---
        TravelActionCard(
            action_id="act:port:gangway-timing",
            phase=JourneyPhase.PORT_DAY,
            time_window="08:00 - 09:30",
            urgency=ActionUrgency.NOW,
            headline="Gangway-Rush um 08:30 Uhr abwarten",
            what_to_do_now="Frühstücken Sie in Ruhe bis 09:15 Uhr und verlassen Sie das Schiff entspannt um 09:30 Uhr über Gangway Deck 5.",
            negative_intelligence_to_avoid="Warteschlange von bis zu 400 Personen in den Decks-5-Korridoren zwischen 08:15 und 08:50 Uhr direkt nach Freigabe.",
            reasons_top_3=[
                "Ab 09:30 Uhr ist der Gangway-Korridor auf Deck 5 komplett staufrei.",
                "Hafen Genua (Ponte dei Mille) ist in nur 8 Minuten zu Fuß erreichbar – keine Eile nötig.",
                "Erhöhter Komfort und null Gedränge am Kartenscanner."
            ],
            concrete_steps=[
                "Borddurchsage 'Schiff für Landgang freigegeben' abwarten.",
                "Frühstück im Restaurant oder Kabinenbalkon genießen.",
                "Um 09:30 Uhr mit Bordkarte und Ausweis über Gangway Deck 5 staufrei von Bord gehen."
            ],
            evidence_sources=["src:port-authority-genoa", "src:field-audit-genoa-2026"],
            confidence_score=99.0,
        ),
        TravelActionCard(
            action_id="act:port:cellular-roaming",
            phase=JourneyPhase.PORT_DAY,
            time_window="Bei Abfahrt / Ankunft",
            urgency=ActionUrgency.NOW,
            headline="Flugmodus aktivieren vor Verlassen der Hafenmole",
            what_to_do_now="Schalten Sie mobile Daten oder das Smartphone in den Flugmodus, sobald das Schiff die Hafenmole verlässt.",
            negative_intelligence_to_avoid="Satelliten-Mobilfunknetz (TIM@Sea / Cellular@Sea) schaltet sich automatisch ein und verursacht Roaming-Kosten von bis zu 12 €/MB.",
            reasons_top_3=[
                "Verhindert automatische Hintergrund-Updates über teure maritime Satelliten-Netze.",
                "Bord-WLAN (MSC Starlink) funktioniert auch im Flugmodus problemlos.",
                "Keine unbemerkten Kostenfallen auf der Abrechnung."
            ],
            concrete_steps=[
                "In den Smartphone-Einstellungen 'Flugmodus' aktivieren.",
                "WLAN manuell einschalten und mit MSC Guest Network verbinden."
            ],
            evidence_sources=["src:itu-mars", "src:official-cruise-line-schedule"],
            confidence_score=100.0,
        ),

        # --- PRE-CRUISE ---
        TravelActionCard(
            action_id="act:pre:checkin-slot",
            phase=JourneyPhase.PRE_CRUISE,
            time_window="10 Tage vor Abfahrt",
            urgency=ActionUrgency.UPCOMING,
            headline="Frühestes Einschiffungs-Zeitfenster (11:00 Uhr) sichern",
            what_to_do_now="Führen Sie den Web-Check-in sofort bei Freischaltung durch und wählen Sie das Ankunftsfenster 11:00 - 11:30 Uhr.",
            negative_intelligence_to_avoid="Späte Zeitfenster (14:00-16:00 Uhr) führen zu langen Schlangen bei der Sicherheitskontrolle im Terminal Genua.",
            reasons_top_3=[
                "Früher Zugang zum Schiff ermöglicht entspanntes Boarding vor dem Hauptansturm.",
                "Gepäck wird als eines der ersten auf die Kabine geliefert.",
                "Zeitgewinn von 3 Stunden zusätzlichem Urlaub an Bord."
            ],
            concrete_steps=[
                "MSC App öffnen und Passdaten / Passfoto hochladen.",
                "Einschiffungsslot 11:00 Uhr auswählen und Boarding Pass digital speichern.",
                "Gepäckanhänger vorab ausdrucken und an Koffern befestigen."
            ],
            evidence_sources=["src:msc-cruises-official", "src:port-authority-genoa"],
            confidence_score=99.0,
        ),
    ]

    @classmethod
    def get_actions_for_phase(cls, phase: JourneyPhase) -> List[TravelActionCard]:
        return [a for a in cls.ACTIONS_CATALOGUE if a.phase == phase]

    @classmethod
    def get_action_by_id(cls, action_id: str) -> Optional[TravelActionCard]:
        for a in cls.ACTIONS_CATALOGUE:
            if a.action_id == action_id:
                return a
        return None
