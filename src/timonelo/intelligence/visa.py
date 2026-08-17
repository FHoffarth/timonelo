"""
Plane 6: Sovereign Visa & Entry Intelligence Evaluator (Stateless).
Resolves international passport validity rules, transit visas, and customs.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.models import VisaIntelligence


class VisaIntelligenceEvaluator:
    """Returns entry, visa and passport-validity requirements ONLY when sourced data is supplied.

    Governed by ADR-0002 §1, §8, §9.

    Every value this evaluator previously returned was a hardcoded default,
    identical for every vessel, every itinerary and every date. It was then
    stamped with an EvidenceLink naming a service that is never called — the
    same defect the audit found in the embarkation evaluator, and the same
    shape as the 15,090 placeholder evidence links across the knowledge base.

    Entry, visa and passport-validity requirements is also a VOLATILE domain: unlike quasi-static ship
    geometry it changes by the day, so it carries different validity semantics
    and is out of scope for the current confidence model (ADR-0002 §13).

    Until a sourced record exists this returns None, and the briefing renders
    the section as an explicit UNKNOWN.
    """

    @staticmethod
    def evaluate(country_name: str, visa_data: Optional[Dict[str, Any]] = None) -> Optional[VisaIntelligence]:
        if not visa_data:
            return None
        raise NotImplementedError(
            "Sourced visa intelligence is not yet wired to the evidence "
            "pipeline. Supply it via the Truth Engine (timonelo.evidence) "
            "rather than as an override dict, so that every value carries "
            "provenance through Artifact -> Event -> Statement -> Review."
        )
