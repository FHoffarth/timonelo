"""
Bridge Officer Tim (BOT) v1.0 Engine for Timonelo.
Personal Bridge Officer & Proactive Travel Intelligence Companion.
"Ich bleibe auf der Brücke. Melden Sie sich jederzeit."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import datetime


class BriefingPhase(str, Enum):
    PRE_CRUISE_12D = "PRE_CRUISE_12D (T-12 Tage vor Abfahrt)"
    CHECKIN_3D = "CHECKIN_3D (T-3 Tage vor Abfahrt)"
    CITY_SHANGHAI = "CITY_SHANGHAI (Vorabend in Shanghai)"
    EMBARKATION_BOARDING = "EMBARKATION_BOARDING (Einschiffung & Kabine 14122)"
    SEA_DAY = "SEA_DAY (Seetag auf See)"
    PORT_YOKOHAMA = "PORT_YOKOHAMA (Hafentag Yokohama / Tokio)"
    DISEMBARKATION = "DISEMBARKATION (Ausschiffung & Heimreise)"


@dataclass(frozen=True)
class ProactiveNotice:
    notice_id: str
    headline: str
    content: str
    urgency: str  # "INFO", "RECOMMENDED_ACTION", "TIMING_HINT"
    evidence_source: str


@dataclass(frozen=True)
class BridgeBriefing:
    briefing_id: str
    date_display: str
    greeting_line: str
    phase_context: str
    proactive_notices: List[ProactiveNotice]
    daily_focus_points: List[str]
    maritime_insight: str
    sign_off: str = "Ich bleibe auf der Brücke. Melden Sie sich jederzeit."
    confidence_score: float = 99.5
    is_deterministic: bool = True


class BridgeOfficerEngine:
    """Deterministic Daily Bridge Briefing generator by Bridge Officer Tim (BOT)."""

    @classmethod
    def generate_briefing(
        cls,
        phase: BriefingPhase = BriefingPhase.PRE_CRUISE_12D,
        traveler_name: str = "Florian",
        ship_name: str = "MSC Bellissima",
        cabin_num: str = "14122",
    ) -> BridgeBriefing:
        if phase == BriefingPhase.PRE_CRUISE_12D:
            return BridgeBriefing(
                briefing_id="brf:bot-pre-cruise-12d",
                date_display="Samstag, 3. Oktober",
                greeting_line=f"Guten Morgen, {traveler_name}.",
                phase_context="Noch 12 Tage bis zur Einschiffung in Shanghai.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-1",
                        headline="Mir ist etwas bei Ihrer Hotel-Lage aufgefallen...",
                        content="Ihr Vorabend-Aufenthalt im Hyatt on the Bund liegt im optimalen Zeitfenster. Von dort aus erreichen wir das Wusongkou Cruise Terminal am Vormittag ohne Querverkehr.",
                        urgency="INFO",
                        evidence_source="src:field-audit-shanghai-2026",
                    ),
                    ProactiveNotice(
                        notice_id="ntc-2",
                        headline="Bevor wir weitermachen: Flug-Puffer",
                        content="Falls der Langstreckenflug noch nicht final bestätigt ist, würde ich mich jetzt darum kümmern. Bei Ankunft am Vortag haben Sie die maximale Reserve.",
                        urgency="RECOMMENDED_ACTION",
                        evidence_source="src:timonelo-regret-engine",
                    ),
                ],
                daily_focus_points=[
                    "Ihr Hyatt-Aufenthalt am Bund liegt im optimalen Zeitfenster vor der Kreuzfahrt.",
                    "Für die Einreise nach China: Als deutscher Staatsbürger reisen Sie für bis zu 15 Tage visumfrei ein; der Reisepass muss noch 6 Monate gültig sein.",
                    "Alipay und WeChat Pay vorab auf dem Smartphone einrichten und mit Ihrer Kreditkarte verknüpfen.",
                ],
                maritime_insight="Auf der Brücke gilt der Grundsatz: Eine gute Vorbereitung an Land nimmt dem ersten Seetag jegliche Hektik.",
            )

        elif phase == BriefingPhase.CHECKIN_3D:
            return BridgeBriefing(
                briefing_id="brf:bot-checkin-3d",
                date_display="Dienstag, 12. Oktober",
                greeting_line=f"Guten Morgen, {traveler_name}.",
                phase_context="Noch 3 Tage bis zum Ablegen.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-3d",
                        headline="Ich würde das heute erledigen...",
                        content="Heute wäre ein idealer Zeitpunkt, den MSC Web-Check-in abzuschließen und die Kofferanhänger für Kabine 14122 auszudrucken.",
                        urgency="RECOMMENDED_ACTION",
                        evidence_source="src:msc-cruises-official",
                    )
                ],
                daily_focus_points=[
                    "Web-Check-in abschließen und Boarding Pass digital speichern.",
                    "Kofferanhänger für Kabine 14122 (Deck 14 Heck Steuerbord) anbringen.",
                    "Medikamente und Reisedokumente zwingend ins Handgepäck packen.",
                ],
                maritime_insight="Koffer werden am Terminal direkt auf Ihre Kabine transportiert – bis 18:00 Uhr ist das Handgepäck Ihre autarke Versorgungseinheit.",
            )

        elif phase == BriefingPhase.CITY_SHANGHAI:
            return BridgeBriefing(
                briefing_id="brf:bot-city-shanghai",
                date_display="Mittwoch, 14. Oktober",
                greeting_line=f"Guten Morgen in Shanghai, {traveler_name}.",
                phase_context="Vorabend der Einschiffung am Bund.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-sh",
                        headline="Fahrzeit-Kalkulation zum Terminal",
                        content="Zwischen Ihrem Hotel am Bund und dem Wusongkou Cruise Terminal beträgt die Fahrzeit je nach Verkehr 45–70 Minuten. Ich empfehle die Abfahrt gegen 10:45 Uhr.",
                        urgency="TIMING_HINT",
                        evidence_source="src:port-authority-shanghai",
                    )
                ],
                daily_focus_points=[
                    "Didi Taxi über Alipay für 10:45 Uhr vorbestellen.",
                    "Reisepass und Boarding Pass griffbereit halten (nicht im Hauptkoffer).",
                    "MSC Diamond Priority Line bei Gate 2 am Terminal ansteuern.",
                ],
                maritime_insight="Die meisten Reisebusse erreichen das Terminal zwischen 12:30 und 14:00 Uhr. Wer um 11:15 Uhr ankommt, geht staufrei an Bord.",
            )

        elif phase == BriefingPhase.EMBARKATION_BOARDING:
            return BridgeBriefing(
                briefing_id="brf:bot-embarkation",
                date_display="Donnerstag, 15. Oktober",
                greeting_line=f"Willkommen an Bord der {ship_name}, {traveler_name}.",
                phase_context=f"Kabine {cabin_num} ist freigegeben · Einschiffungstag.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-emb",
                        headline="Mir ist etwas aufgefallen: Sicherheitsübung",
                        content=f"Ihre Kabine {cabin_num} ist jetzt bezugsbereit. Ich würde zunächst den 4-minütigen Sicherheitsfilm am Kabinenfernseher ansehen. Danach begleite ich Sie zur Musterstation F auf Deck 6.",
                        urgency="RECOMMENDED_ACTION",
                        evidence_source="src:msc-bellissima-imo-safety-cert",
                    )
                ],
                daily_focus_points=[
                    "Mittagessen à la carte im Posidonia Restaurant Deck 5 (ohne Rollkoffer-Gedränge).",
                    "Sicherheitsfilm am TV abschließen und Cruise Card an Musterstation F scannen lassen.",
                    "Diamond Willkommens-Prosecco auf Kabine 14122 genießen.",
                ],
                maritime_insight="Das Buffet auf Deck 15 entwickelt sich erfahrungsgemäß am ersten Tag schneller zur Expedition als zum Mittagessen. Das Restaurant auf Deck 5 ist die ruhigere Wahl.",
            )

        elif phase == BriefingPhase.SEA_DAY:
            return BridgeBriefing(
                briefing_id="brf:bot-sea-day",
                date_display="Samstag, 17. Oktober",
                greeting_line=f"Guten Morgen auf See, {traveler_name}.",
                phase_context="Erster Seetag im Ostchinesischen Meer.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-sea",
                        headline="Wetterlage & Deck-Empfehlung",
                        content="Das Wetter ist außergewöhnlich ruhig bei 1,2 m Dünung. Heute eignet sich das Heckdeck auf Deck 16 (Horizon Bar) hervorragend für einen ungestörten Aufenthalt im Freien.",
                        urgency="INFO",
                        evidence_source="src:ecmwf-marine-weather",
                    )
                ],
                daily_focus_points=[
                    "Heck-Sonnendeck Deck 16 für entspanntes Lesen und Weitblick nutzen.",
                    "Thermal-Spa Session (Diamond Benefit) für den späten Nachmittag reservieren.",
                    "Abendessen im Butcher's Cut Spezialitätenrestaurant.",
                ],
                maritime_insight="Wer die Morgenstunden zwischen 07:00 und 08:30 Uhr auf dem Außendeck verbringt, erlebt das Schiff in seiner reinsten, friedlichsten Form.",
            )

        elif phase == BriefingPhase.PORT_YOKOHAMA:
            return BridgeBriefing(
                briefing_id="brf:bot-port-yokohama",
                date_display="Dienstag, 20. Oktober",
                greeting_line=f"Guten Morgen in Yokohama, {traveler_name}.",
                phase_context="Hafentag Tokio / Yokohama · Anlegen 05:30 Uhr.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-yok",
                        headline="Rückkehrzeit-Empfehlung",
                        content="Wir liegen heute am Osanbashi Pier. Die letzte sichere Rückkehrzeit empfehle ich spätestens 45 Minuten vor 'All Aboard' (17:30 Uhr) – also bis 16:45 Uhr am Schiff zurück zu sein.",
                        urgency="TIMING_HINT",
                        evidence_source="src:port-authority-yokohama",
                    )
                ],
                daily_focus_points=[
                    "Staufreier Landgang um 09:15 Uhr über Gangway Deck 5.",
                    "Minatomirai Line per Suica Card auf dem Smartphone für Ausflüge nach Tokio (Shibuya/Ginza) nutzen.",
                    "Spätestens um 16:45 Uhr am Pier zurück sein.",
                ],
                maritime_insight="Ich verspreche nichts – aber wenn Sie um 09:15 Uhr von Bord gehen, stehen die Chancen gut, dass Sie völlig ohne Wartezeit durch den Zollscanner spazieren.",
            )

        else:
            return BridgeBriefing(
                briefing_id="brf:bot-disembarkation",
                date_display="Donnerstag, 22. Oktober",
                greeting_line=f"Guten Morgen, {traveler_name}.",
                phase_context="Ausschiffungstag & Heimflug ab Tokio Haneda.",
                proactive_notices=[
                    ProactiveNotice(
                        notice_id="ntc-dis",
                        headline="Teil 2 der Reise beginnt",
                        content="Als Diamond-Gast können Sie Ihre Kabine bis 09:00 Uhr nutzen. Danach bringt Sie die Keikyu Line in 25 Minuten direkt zum Flughafen Tokio Haneda.",
                        urgency="INFO",
                        evidence_source="src:tokyo-haneda-airport",
                    )
                ],
                daily_focus_points=[
                    "Late Check-out der Kabine bis 09:00 Uhr ausnutzen.",
                    "Bevorzugte Ausschiffung nutzen und Koffer in der Terminalhalle übernehmen.",
                    "Vor dem Langstrecken-Rückflug die ANA / Star Alliance Lounge in Haneda für eine frische Ramen-Nudelsuppe ansteuern.",
                ],
                maritime_insight="Eine gute Reise endet nicht mit dem Verlassen des Schiffs. Sie endet erst, wenn Sie erholt und ohne Hektik wieder an Ihrer Haustür ankommen.",
            )
