"""
Plane 6: Travel & Transport Intelligence Evaluator (Stateless).
Resolves local currency, card acceptance, tipping etiquette, and transit options.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import TravelIntelligence


class TravelIntelligenceEvaluator:
    """Returns ground transport, connectivity and roaming ONLY when sourced data is supplied.

    Governed by ADR-0002 §1, §8, §9.

    Every value this evaluator previously returned was a hardcoded default,
    identical for every vessel, every itinerary and every date. It was then
    stamped with an EvidenceLink naming a service that is never called — the
    same defect the audit found in the embarkation evaluator, and the same
    shape as the 15,090 placeholder evidence links across the knowledge base.

    Ground transport, connectivity and roaming is also a VOLATILE domain: unlike quasi-static ship
    geometry it changes by the day, so it carries different validity semantics
    and is out of scope for the current confidence model (ADR-0002 §13).

    Until a sourced record exists this returns None, and the briefing renders
    the section as an explicit UNKNOWN.
    """

    @staticmethod
    def evaluate(country_name: str, travel_data: Optional[Dict[str, Any]] = None) -> Optional[TravelIntelligence]:
        if not travel_data:
            return None
        raise NotImplementedError(
            "Sourced transport intelligence is not yet wired to the evidence "
            "pipeline. Supply it via the Truth Engine (timonelo.evidence) "
            "rather than as an override dict, so that every value carries "
            "provenance through Artifact -> Event -> Statement -> Review."
        )
