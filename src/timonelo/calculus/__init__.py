"""
Spatial Calculus Package (Plane 3 per ADR-0001).
Pure, stateless mathematical derivations over Plane 2 Spatial Ontology.
"""

from .router import DeterministicSpatialRouter, WayfindingRoute, RouteStep
from .sandwich import DeterministicSandwichResolver, CabinSandwichReport, VerticalLayerReport
from .sightlines import DeterministicSightlineCalculator, SightlineReport

__all__ = [
    "DeterministicSpatialRouter",
    "WayfindingRoute",
    "RouteStep",
    "DeterministicSandwichResolver",
    "CabinSandwichReport",
    "VerticalLayerReport",
    "DeterministicSightlineCalculator",
    "SightlineReport",
]
