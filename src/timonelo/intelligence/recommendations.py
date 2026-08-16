"""
Plane 6: Decision Summary & Negative Intelligence Synthesizer (DECISION_FIRST.md).
Transforms raw spatial and journey facts into the calmest, highest-confidence resolutions.
"""

from typing import List
from timonelo.intelligence.models import (
    DecisionSummary,
    DecisionItem,
    DecisionUrgency,
    NegativeIntelligenceAction,
    CabinIntelligence,
    EmbarkationIntelligence,
    PortIntelligence,
    WeatherIntelligence,
    VisaIntelligence,
    DiningIntelligence,
    AccessibilityIntelligence,
)


class DecisionSummarySynthesizer:
    """Synthesizes the constitutional 'Three Things That Matter Today' and decisions avoided."""

    @staticmethod
    def synthesize(
        cabin_intel: CabinIntelligence,
        embark_intel: EmbarkationIntelligence,
        port_intel: PortIntelligence,
        weather_intel: WeatherIntelligence,
        visa_intel: VisaIntelligence,
        dining_intel: DiningIntelligence,
        acc_intel: AccessibilityIntelligence,
    ) -> DecisionSummary:
        decisions: List[DecisionItem] = []
        avoided: List[NegativeIntelligenceAction] = []

        # Decision 1: Mandatory Safety Drill & Muster Station
        decisions.append(
            DecisionItem(
                title="Mandatory Safety Briefing",
                recommendation=f"Report to {embark_intel.assigned_muster_station} on Deck {embark_intel.muster_station_deck:02d} before {embark_intel.mandatory_safety_drill_deadline}.",
                rationale="Required by maritime law prior to departure. Step-free route available via nearest elevator.",
                urgency=DecisionUrgency.CRITICAL_SAFETY,
                regret_avoided="Avoids being blocked from sailing or receiving boarding clearance delays.",
            )
        )
        avoided.append(
            NegativeIntelligenceAction(
                category="Safety & Compliance",
                regret_prevented="Searching through wrong deck corridors during emergency drill",
                calm_guidance=f"Take your nearest lift directly to Deck {embark_intel.muster_station_deck:02d}.",
                evidence_source_id="EVID-SOLAS-BELLISSIMA",
            )
        )

        # Decision 2: All-Aboard Time & Gangway Logistics
        decisions.append(
            DecisionItem(
                title="Port All-Aboard Deadline",
                recommendation=f"Be back on board through Gangway Deck {port_intel.gangway_deck:02d} by {port_intel.all_aboard_time} latest.",
                rationale=f"The ship sails promptly at departure. Pedestrian return route from historic center is only {port_intel.town_distance_meters}m.",
                urgency=DecisionUrgency.TIME_SENSITIVE,
                regret_avoided="Prevents being stranded in port or missing vessel departure.",
            )
        )
        avoided.append(
            NegativeIntelligenceAction(
                category="Port Logistics",
                regret_prevented="Arriving at the wrong terminal pier or wrong gangway deck",
                calm_guidance=f"Gangway is located on Deck {port_intel.gangway_deck:02d} ({port_intel.gangway_location}).",
                evidence_source_id="EVID-PORT-AUTHORITY-GENOA",
            )
        )

        # Decision 3: Evening Dinner & Circulation
        decisions.append(
            DecisionItem(
                title="Evening Dining Logistics",
                recommendation=f"Your assigned table is at {dining_intel.assigned_main_restaurant} (Deck {dining_intel.restaurant_deck:02d}).",
                rationale=f"Walking distance is {dining_intel.walking_meters_from_cabin:.0f}m ({dining_intel.walking_seconds} seconds) from Cabin {cabin_intel.cabin_number}. Dress code is {dining_intel.evening_dress_code}.",
                urgency=DecisionUrgency.COMFORT_OPTIMIZATION,
                regret_avoided="Avoids dress code refusal and wandering across distant restaurant decks.",
            )
        )
        avoided.append(
            NegativeIntelligenceAction(
                category="Dining & Comfort",
                regret_prevented="Walking the entire ship length in the wrong direction for dinner",
                calm_guidance=f"Your restaurant is on Deck {dining_intel.restaurant_deck:02d} Aft, accessible directly via your nearest elevator.",
                evidence_source_id="EVID-DINING-GUIDE",
            )
        )

        # Add accessibility protection if needed
        if acc_intel.cabin_is_accessible_certified or not acc_intel.has_step_free_access_to_gangway:
            avoided.append(
                NegativeIntelligenceAction(
                    category="Accessibility",
                    regret_prevented="Encountering step barriers on gangway paths",
                    calm_guidance="Elevator core routing is 100% step-free directly to Deck 05 gangway.",
                    evidence_source_id="EVID-ACC-STANDARDS",
                )
            )

        # Add roaming charge protection
        avoided.append(
            NegativeIntelligenceAction(
                category="Cellular Connectivity",
                regret_prevented="Accidental satellite cellular roaming charges at sea",
                calm_guidance="Switch to Airplane Mode once the ship departs port waters.",
                evidence_source_id="EVID-TRAVEL-DATA-EU",
            )
        )

        return DecisionSummary(
            headline="Three Essential Clearances for Today",
            calm_perspective="Your embarkation and day in Genoa are fully prepared. Follow these three timeframes for a completely relaxed day at sea.",
            core_decisions=decisions,
            decisions_avoided=avoided,
        )
