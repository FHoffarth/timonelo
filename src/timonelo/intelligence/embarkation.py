"""
Plane 6: Embarkation Intelligence Evaluator (Stateless).
Resolves pier terminal floorplans, luggage drops, and safety drill logistics.
"""

from typing import Optional, Dict, Any, List
from timonelo.ontology.models import VesselSpatialOntology, Cabin, EvidenceLink
from timonelo.intelligence.models import EmbarkationIntelligence


class EmbarkationIntelligenceEvaluator:
    """Evaluates embarkation and boarding logistics for a traveler."""

    @staticmethod
    def evaluate(
        ontology: VesselSpatialOntology,
        cabin: Cabin,
        terminal_override: Optional[Dict[str, Any]] = None,
    ) -> Optional[EmbarkationIntelligence]:
        """
        Returns embarkation intelligence ONLY when sourced data is supplied.

        Everything this evaluator previously returned was fabricated:

          * terminal name, berth, luggage window, stateroom-ready time and
            drill deadline were hardcoded string literals, identical for every
            cabin on every vessel, including vessels that have never called at
            that terminal;
          * the muster station was COMPUTED from `cabin.boundary_polygon[0].x`
            and the parity of the last digit of the cabin number. Those
            polygons are produced arithmetically by StateroomArchetypeGenerator
            and correspond to no surveyed geometry;
          * the result was then stamped with the cabin's evidence links, or
            with a placeholder SOLAS EvidenceLink, presenting it as sourced.

        Muster assignment is SOLAS safety information. Rendering a guessed
        muster station inside a calm, authoritative interface is worse than
        rendering nothing, because it displaces the passenger's check of their
        actual cabin card and stateroom door notice.

        No information is preferable to incorrect information. Until a sourced
        terminal and muster record exists, this returns None and the briefing
        renders the section as UNKNOWN.
        """
        if not terminal_override:
            return None

        required = (
            "terminal_name",
            "pier_number",
            "luggage_drop_window",
            "stateroom_ready_time",
            "mandatory_safety_drill_deadline",
            "assigned_muster_station",
            "muster_station_deck",
            "step_free_muster_route",
            "boarding_pass_requirement",
            "evidence_links",
        )
        missing = [k for k in required if not terminal_override.get(k)]
        if missing:
            raise ValueError(
                "Refusing to render partial embarkation intelligence. "
                f"Missing sourced fields: {', '.join(missing)}. "
                "Supply every field with provenance, or supply none."
            )

        return EmbarkationIntelligence(
            terminal_name=terminal_override["terminal_name"],
            pier_number=terminal_override["pier_number"],
            luggage_drop_window=terminal_override["luggage_drop_window"],
            stateroom_ready_time=terminal_override["stateroom_ready_time"],
            mandatory_safety_drill_deadline=terminal_override["mandatory_safety_drill_deadline"],
            assigned_muster_station=terminal_override["assigned_muster_station"],
            muster_station_deck=terminal_override["muster_station_deck"],
            step_free_muster_route=terminal_override["step_free_muster_route"],
            boarding_pass_requirement=terminal_override["boarding_pass_requirement"],
            evidence_links=terminal_override["evidence_links"],
        )
