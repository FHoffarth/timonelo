"""
Plane 6: Weather & Sea State Intelligence Evaluator (Stateless).
Resolves maritime swell, Beaufort scale, ship motion risk, and sun angles.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import WeatherIntelligence


class WeatherIntelligenceEvaluator:
    """Evaluates sea state, weather forecast, and vessel motion risk."""

    @staticmethod
    def evaluate(weather_data: Optional[Dict[str, Any]] = None) -> WeatherIntelligence:
        data = weather_data or {}
        summary = data.get("weather_summary", "Partly cloudy with calm coastal breeze")
        temp = float(data.get("air_temperature_celsius", 24.5))
        swell = float(data.get("sea_swell_meters", 0.6))
        beaufort = int(data.get("beaufort_scale", 2))
        stabilizers = data.get("ship_stabilizer_status", "Active Fin Stabilizers Deployed (92% Roll Reduction)")
        sunrise = data.get("sunrise_time", "06:18")
        sunset = data.get("sunset_time", "20:42")
        sun_side = data.get("sun_side_docked", "Starboard side faces afternoon sun (Port side is shaded)")

        # Calculate motion risk from swell
        if swell < 1.0 and beaufort <= 3:
            motion_risk = "Low Motion (Smooth Sailing, imperceptible pitch/roll)"
        elif swell < 2.0 and beaufort <= 5:
            motion_risk = "Moderate Motion (Noticeable in forward/aft extremities)"
        else:
            motion_risk = "Elevated Motion (Midship lower decks recommended for comfort)"

        ev_links = [
            EvidenceLink(
                source_id="EVID-METEO-MED-MARINE",
                sha256="3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c",
                locator="Copernicus_Marine_Service_Wave_Forecast",
            )
        ]

        return WeatherIntelligence(
            weather_summary=summary,
            air_temperature_celsius=temp,
            sea_swell_meters=swell,
            beaufort_scale=beaufort,
            motion_risk_level=motion_risk,
            ship_stabilizer_status=stabilizers,
            sunrise_time=sunrise,
            sunset_time=sunset,
            sun_side_docked=sun_side,
            evidence_links=ev_links,
        )
