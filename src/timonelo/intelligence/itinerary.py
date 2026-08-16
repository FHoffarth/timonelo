"""
Plane 6: Itinerary & Timeline Intelligence Evaluator (Stateless).
Resolves day number, arrival/departure clocks, and navigational context.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class ItineraryContext:
    day_number: int
    date_iso: str
    port_name: str
    country: str
    arrival_time: str
    departure_time: str
    all_aboard_time: str
    is_sea_day: bool


class ItineraryIntelligenceEvaluator:
    """Evaluates itinerary progression and daily temporal milestones."""

    @staticmethod
    def evaluate(itinerary_data: Optional[Dict[str, Any]] = None) -> ItineraryContext:
        data = itinerary_data or {}
        return ItineraryContext(
            day_number=int(data.get("day_number", 1)),
            date_iso=data.get("date_iso", "2026-08-16"),
            port_name=data.get("port_name", "Genoa (Genova)"),
            country=data.get("country", "Italy"),
            arrival_time=data.get("arrival_time", "08:00"),
            departure_time=data.get("departure_time", "18:00"),
            all_aboard_time=data.get("all_aboard_time", "17:30"),
            is_sea_day=bool(data.get("is_sea_day", False)),
        )
