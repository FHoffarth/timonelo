"""
Plane 6: Dining Intelligence Evaluator (Stateless).
Resolves evening dining venues, walking distance from cabin, dress codes, and step-free access.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import VesselSpatialOntology, Cabin, EvidenceLink
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.intelligence.models import DiningIntelligence


class DiningIntelligenceEvaluator:
    """Evaluates culinary options, assigned main restaurants, and route metrics."""

    @staticmethod
    def evaluate(
        ontology: VesselSpatialOntology,
        cabin: Cabin,
        router: DeterministicSpatialRouter,
        dining_override: Optional[Dict[str, Any]] = None,
    ) -> Optional[DiningIntelligence]:
        """Returns dining intelligence ONLY when sourced data is supplied.

        Governed by ADR-0002 §1, §8.

        Two distinct defects were present here:

        1. Fabrication. Dress code, buffet hours and service times were
           hardcoded strings applied to every vessel; a missing venue fell back
           to the invented name "Main Dining Room" on an arbitrary deck.

        2. A category error, which is worse. The evaluator scanned the ontology
           for the FIRST venue whose category or name looked like dining, and
           presented it as the passenger's ASSIGNED restaurant. Assignment is a
           booking fact: it lives in the reservation, not in the ship's
           geometry. No amount of spatial data can establish it, so this can
           never be inferred — only sourced.

        Which venues exist and where they are remains answerable from ship
        evidence, and is served by the ontology directly. Assignment, dress
        code and service times are not.
        """
        if not dining_override:
            return None
        raise NotImplementedError(
            "Sourced dining intelligence is not yet wired to the evidence "
            "pipeline. Restaurant assignment is a booking fact and must enter "
            "through Artifact -> Event -> Statement -> Review like any other."
        )
