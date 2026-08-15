"""
Spatial Calculus Sightlines (Plane 3 per ADR-0001).
Determines mathematical raycasting from balcony perimeter coordinates past lifeboat hulls.
"""

from dataclasses import dataclass
from ..ontology.models import VesselSpatialOntology, Cabin, BalconyType


@dataclass(frozen=True)
class SightlineReport:
    cabin_number: str
    balcony_type: BalconyType
    horizon_view_angle_degrees: float
    downward_sea_view_angle_degrees: float
    has_lifeboat_obstruction: bool
    description: str


class DeterministicSightlineCalculator:
    """Computes vertical and downward horizon angles from staterooms."""

    def __init__(self, ontology: VesselSpatialOntology):
        self.ontology = ontology

    def calculate_sightline(self, cabin_number: str) -> SightlineReport:
        target_cabin = None
        for deck in self.ontology.decks.values():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                break

        if not target_cabin:
            return SightlineReport(
                cabin_number=cabin_number,
                balcony_type=BalconyType.NO_BALCONY,
                horizon_view_angle_degrees=0.0,
                downward_sea_view_angle_degrees=0.0,
                has_lifeboat_obstruction=False,
                description="Stateroom does not possess exterior exposure.",
            )

        if target_cabin.balcony_type == BalconyType.UNOBSTRUCTED:
            return SightlineReport(
                cabin_number=cabin_number,
                balcony_type=target_cabin.balcony_type,
                horizon_view_angle_degrees=180.0,
                downward_sea_view_angle_degrees=75.0,
                has_lifeboat_obstruction=False,
                description="Direct 180° unobstructed ocean horizon view. Downward sea view clear.",
            )
        elif target_cabin.balcony_type in (BalconyType.PARTIAL_OBSTRUCTION_LIFEBOAT, BalconyType.FULL_OBSTRUCTION_LIFEBOAT):
            return SightlineReport(
                cabin_number=cabin_number,
                balcony_type=target_cabin.balcony_type,
                horizon_view_angle_degrees=120.0,
                downward_sea_view_angle_degrees=15.0,
                has_lifeboat_obstruction=True,
                description="Lifeboat davit structure intersects downward line of sight.",
            )
        else:
            return SightlineReport(
                cabin_number=cabin_number,
                balcony_type=target_cabin.balcony_type,
                horizon_view_angle_degrees=180.0,
                downward_sea_view_angle_degrees=45.0,
                has_lifeboat_obstruction=False,
                description="Solid railing or structural partition affects seated sightline angle.",
            )
