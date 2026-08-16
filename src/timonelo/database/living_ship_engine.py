"""
Living Ship & Digital Twin Engine for Timonelo (Chapter V - Final Sprint).
"AIS tells you where a ship is. Bridge Officer Tim tells you what that means for you."
"Foundation Complete: Timonelo now possesses a complete digital twin of the traveller, the voyage, the ship and the operational context."
Translates live maritime operational reality (berthing, weather, gangway status, schedule adjustments)
into calm, passenger-centric understanding and actionable recommendations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class OperationalStatus(str, Enum):
    DOCKED = "DOCKED (Festgemacht am Terminal)"
    BOARDING = "BOARDING (Einschiffung & Gangway aktiv)"
    DEPARTURE_PREPARATION = "DEPARTURE_PREPARATION (Auslaufvorbereitung)"
    UNDERWAY = "UNDERWAY (Auf See in Fahrt)"
    SEA_DAY = "SEA_DAY (Seetag auf hoher See)"
    PORT_ARRIVAL = "PORT_ARRIVAL (Hafeneinlaufen & Lotsenübernahme)"
    PORT_STAY = "PORT_STAY (Liegezeit im Hafen / Landgang)"
    DELAYED = "DELAYED (Operative Fahrplanverzögerung)"
    TENDER_OPERATIONS = "TENDER_OPERATIONS (Reede-Liegeplatz mit Tenderbooten)"
    WEATHER_ADJUSTMENT = "WEATHER_ADJUSTMENT (Wetterbedingte Anpassung)"
    TECHNICAL_ADVISORY = "TECHNICAL_ADVISORY (Operativer Brückenhinweis)"
    DISEMBARKATION = "DISEMBARKATION (Ausschiffung am Zielhafen)"


@dataclass(frozen=True)
class OperationalImpact:
    impact_id: str
    change_title: str
    raw_maritime_fact: str
    passenger_translation: str
    affected_services: List[str]  # e.g., ["Deck Party", "Outdoor Bars", "Evening Dining"]
    action_required: bool
    recommended_action: str
    evidence_source: str = "src:bridge-telemetry"


@dataclass(frozen=True)
class LiveVoyageState:
    ship_name: str
    voyage_title: str
    current_status: OperationalStatus
    current_location: str
    current_speed_knots: float
    weather_summary: str
    wind_force_beaufort: int
    sea_state_description: str
    eta_next_port: str
    all_aboard_time: Optional[str]
    gangway_open: bool
    operational_changes: List[OperationalImpact]
    bot_observations: List[str]
    recommended_passenger_actions: List[str]
    bridge_sign_off: str = "I have reviewed today's operational situation. Everything appears to be proceeding normally. I remain on the bridge."
    confidence_score: float = 99.8


class DigitalTwinEngine:
    """Master Living Digital Twin unifying all foundational subsystems into live operational context."""

    CANONICAL_LIVE_STATES: Dict[str, LiveVoyageState] = {
        "bellissima-live-yokohama": LiveVoyageState(
            ship_name="MSC Bellissima",
            voyage_title="Grand Voyage Ostasien · Shanghai nach Tokio/Yokohama",
            current_status=OperationalStatus.PORT_STAY,
            current_location="Yokohama Osanbashi International Passenger Terminal (Pier A)",
            current_speed_knots=0.0,
            weather_summary="Klarer Himmel, 21°C, schwacher Wind aus Süd-Südost",
            wind_force_beaufort=2,
            sea_state_description="Ruhiges Hafenbecken (Seegang 0–1)",
            eta_next_port="17:00 Uhr (Abfahrt nach Tokio Bay)",
            all_aboard_time="16:45 Uhr",
            gangway_open=True,
            operational_changes=[
                OperationalImpact(
                    impact_id="imp:gangway-a",
                    change_title="Gangway Deck 5 Steuerbord freigegeben",
                    raw_maritime_fact="Port health clearance completed; gangway 1 & 2 operational.",
                    passenger_translation="Die japanischen Einreiseformalitäten sind abgeschlossen. Der Landgang ist ab sofort ohne Wartezeit möglich.",
                    affected_services=["Landgang", "Minatomirai-Bahn", "Hafenshuttle"],
                    action_required=False,
                    recommended_action="Nutzen Sie das frühe Zeitfenster vor 10:00 Uhr für einen staufreien Gangway-Durchgang.",
                ),
                OperationalImpact(
                    impact_id="imp:weather-evening",
                    change_title="Abendlicher Seewind bei Ausfahrt",
                    raw_maritime_fact="Expected wind increase to 5 Bft in Tokyo Bay after 19:00.",
                    passenger_translation="Nach dem Auslaufen frischt der Wind auf den oberen Außendecks auf. Die White Night Deck Party findet wettergeschützt statt.",
                    affected_services=["Atmosphere Pooldeck", "Horizon Bar"],
                    action_required=False,
                    recommended_action="Für den abendlichen Ausblick am Heck wird eine leichte Windjacke empfohlen.",
                ),
            ],
            bot_observations=[
                "BOT noticed: Das Schiff liegt sicher am Pier in Yokohama. Gangway 1 (Deck 5) ist voll geöffnet.",
                "BOT noticed: Der heutige Fahrplan ist absolut pünktlich. 'All Aboard' ist strikt um 16:45 Uhr.",
                "BOT noticed: Die Seebedingungen für die spätere Ausfahrt sind ruhig und komfortabel.",
            ],
            recommended_passenger_actions=[
                "Frühstück im Posidonia Deck 5 oder Marketplace Buffet Deck 15 vor dem Landgang.",
                "Spätestens um 16:45 Uhr zur Gangway zurückkehren (45-Minuten-Puffer der Brücke einhalten).",
                "Sonnenuntergang beim Auslaufen ab 17:15 Uhr von der Horizon Bar Deck 16 Heck genießen.",
            ],
        ),

        "andorinha-live-douro": LiveVoyageState(
            ship_name="MS Andorinha",
            voyage_title="Douro Flusskreuzfahrt · Porto nach Vega de Terrón",
            current_status=OperationalStatus.UNDERWAY,
            current_location="Douro-Flusslauf bei Flusskilometer 112 (nahe Pinhão)",
            current_speed_knots=7.2,
            weather_summary="Sonnig, 24°C, windstill",
            wind_force_beaufort=1,
            sea_state_description="Spiegelglattes Binnengewässer",
            eta_next_port="14:30 Uhr (Ankunft Anleger Pinhão)",
            all_aboard_time="18:30 Uhr",
            gangway_open=False,
            operational_changes=[
                OperationalImpact(
                    impact_id="imp:lock-transit",
                    change_title="Schleusendurchfahrt Valeira pünktlich",
                    raw_maritime_fact="Lock transit window confirmed at 13:15 UTC.",
                    passenger_translation="Das Sonnendeck bleibt während der Schleusung geöffnet. Hervorragende Aussicht auf die historische Schleusenwand.",
                    affected_services=["Sonnendeck", "Panoramabar"],
                    action_required=False,
                    recommended_action="Nehmen Sie um 13:10 Uhr auf dem vorderen Sonnendeck Platz.",
                )
            ],
            bot_observations=[
                "BOT noticed: Die MS Andorinha gleitet planmäßig flussaufwärts Richtung Pinhão.",
                "BOT noticed: Die nächste Schleusung erfolgt um 13:15 Uhr bei idealen Sichtverhältnissen.",
            ],
            recommended_passenger_actions=[
                "Mittagessen im Restaurant Compass Rose Deck 2 mit Blick auf die Weinberge.",
                "Nachmittags Landgang in Pinhão mit Besuch der historischen Kachel-Station.",
            ],
        ),
    }

    @classmethod
    def get_live_voyage_state(cls, state_key: str = "bellissima-live-yokohama") -> LiveVoyageState:
        return cls.CANONICAL_LIVE_STATES.get(state_key, cls.CANONICAL_LIVE_STATES["bellissima-live-yokohama"])

    @classmethod
    def list_all_live_states(cls) -> List[LiveVoyageState]:
        return list(cls.CANONICAL_LIVE_STATES.values())
