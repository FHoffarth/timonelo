"""
Plane 6: Master Cruise Briefing Synthesizer (Stateless Master Runtime).
Assembles the complete, unified CruiseBriefing container from all underlying planes.
"""

from typing import Optional, Dict, Any
from timonelo.ontology.models import VesselSpatialOntology, Cabin
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.calculus.sandwich import DeterministicSandwichResolver
from timonelo.calculus.sightlines import DeterministicSightlineCalculator
from timonelo.lenses.accessibility import AccessibilityLens
from timonelo.lenses.quiet import QuietCabinLens
from timonelo.intelligence.models import (
    CruiseBriefing,
    CabinIntelligence,
    AccessibilityIntelligence,
)
from timonelo.intelligence.embarkation import EmbarkationIntelligenceEvaluator
from timonelo.intelligence.ports import PortIntelligenceEvaluator
from timonelo.intelligence.weather import WeatherIntelligenceEvaluator
from timonelo.intelligence.visa import VisaIntelligenceEvaluator
from timonelo.intelligence.transport import TravelIntelligenceEvaluator
from timonelo.intelligence.dining import DiningIntelligenceEvaluator
from timonelo.intelligence.itinerary import ItineraryIntelligenceEvaluator
from timonelo.intelligence.recommendations import DecisionSummarySynthesizer


class CruiseBriefingSynthesizer:
    """Master evaluator assembling Plane 6 CruiseBriefing for any stateroom and itinerary day."""

    @staticmethod
    def generate_briefing(
        ontology: VesselSpatialOntology,
        cabin_number: str,
        itinerary_override: Optional[Dict[str, Any]] = None,
        port_override: Optional[Dict[str, Any]] = None,
        weather_override: Optional[Dict[str, Any]] = None,
        dining_override: Optional[Dict[str, Any]] = None,
        visa_override: Optional[Dict[str, Any]] = None,
        travel_override: Optional[Dict[str, Any]] = None,
    ) -> Optional[CruiseBriefing]:
        # 1. Locate Cabin across ontology decks
        target_cabin: Optional[Cabin] = None
        for deck in ontology.decks.values():
            if cabin_number in deck.cabins:
                target_cabin = deck.cabins[cabin_number]
                break

        if not target_cabin:
            return None

        # 2. Instantiate Spatial Calculus Engines
        router = DeterministicSpatialRouter(ontology)
        sandwich_resolver = DeterministicSandwichResolver(ontology)
        sightline_calc = DeterministicSightlineCalculator(ontology)

        # 3. Evaluate Plane 4 Lenses
        acc_eval = AccessibilityLens.evaluate(ontology, router, cabin_number)
        quiet_eval = QuietCabinLens.evaluate(ontology, sandwich_resolver, router, cabin_number)
        sandwich = sandwich_resolver.resolve_cabin_sandwich(cabin_number)
        sightline = sightline_calc.calculate_sightline(cabin_number)

        deck = ontology.decks[target_cabin.deck_number]

        # 4. Synthesize Cabin Intelligence
        cabin_station = target_cabin.boundary_polygon[0].x if target_cabin.boundary_polygon else 0.5
        if cabin_station < 0.38:
            zone_label = "Midship-Aft"
            lift_core = "Core Aft (Elevators 1–4)"
        elif cabin_station < 0.63:
            zone_label = "Midship"
            lift_core = "Core Midship (Elevators 5–12 & Panoramic Lift)"
        else:
            zone_label = "Midship-Forward"
            lift_core = "Core Forward (Elevators 13–18)"

        # ADR-0002 9: the Language Layer may not strengthen a claim.
        # "(Pure residential buffer)" was previously appended unconditionally,
        # without consulting the sandwich resolver at all, and an unmodelled
        # deck was labelled "Residential Deck". Both are removed: the acoustic
        # claim is now rendered only when the resolver positively establishes
        # it, and an unmodelled deck reads UNKNOWN.
        def _layer_desc(layer) -> str:
            if layer is None:
                return "UNKNOWN"
            if layer.is_residential_cabins_only is None:
                return f"{layer.deck_name} (contents UNKNOWN)"
            if layer.is_active_noise_generator:
                venues = ", ".join(layer.intersecting_venues) or "noise-generating venue"
                return f"{layer.deck_name} ({venues})"
            if layer.is_residential_cabins_only:
                return f"{layer.deck_name} (staterooms only)"
            return f"{layer.deck_name} ({', '.join(layer.intersecting_venues) or 'mixed use'})"

        overhead_desc = _layer_desc(sandwich.overhead_layer if sandwich else None)
        underfoot_desc = _layer_desc(sandwich.underfoot_layer if sandwich else None)
        sandwich_status = f"Deck above: {overhead_desc} | Deck below: {underfoot_desc}"
        if sandwich and sandwich.is_acoustically_insulated_sandwich:
            sandwich_status += " — staterooms above and below"

        sockets_summary = f"{target_cabin.sockets.eu_standard_count}x EU, {target_cabin.sockets.us_standard_count}x US, {target_cabin.sockets.usb_a_count}x USB-A"
        if target_cabin.sockets.usb_c_count > 0:
            sockets_summary += f", {target_cabin.sockets.usb_c_count}x USB-C"
        if target_cabin.sockets.bedside_usb_available:
            sockets_summary += " (Bedside USB Available)"

        cabin_intel = CabinIntelligence(
            cabin_number=target_cabin.cabin_number,
            deck_number=target_cabin.deck_number,
            deck_name=deck.name,
            hull_side=target_cabin.hull_side.value,
            zone=zone_label,
            category_name=f"Category {target_cabin.category_code} ({target_cabin.square_meters:.0f} m²)",
            nearest_elevator_core=lift_core,
            steps_to_elevator=int(acc_eval.nearest_elevator_distance_meters * 1.3) if acc_eval else 28,
            vertical_sandwich_status=sandwich_status,
            is_quiet_tier=quiet_eval.is_quiet_tier if quiet_eval else True,
            balcony_sightline_summary=sightline.description if sightline else "Unobstructed sea view",
            power_socket_summary=sockets_summary,
            evidence_links=list(target_cabin.evidence_links),
        )

        # 5. Evaluate Plane 6 Intelligence Modules
        itinerary = ItineraryIntelligenceEvaluator.evaluate(itinerary_override)
        embark_intel = EmbarkationIntelligenceEvaluator.evaluate(ontology, target_cabin)
        port_intel = PortIntelligenceEvaluator.evaluate(port_override)
        weather_intel = WeatherIntelligenceEvaluator.evaluate(weather_override)
        # Volatile-domain sections return None until sourced. Visa and travel
        # depend on the port call, so without a sourced port they cannot be
        # resolved either — a missing prerequisite must propagate as UNKNOWN,
        # not be filled with a default country.
        visa_intel = (
            VisaIntelligenceEvaluator.evaluate(port_intel.country, visa_override)
            if port_intel is not None else None
        )
        dining_intel = DiningIntelligenceEvaluator.evaluate(ontology, target_cabin, router, dining_override)
        travel_intel = (
            TravelIntelligenceEvaluator.evaluate(port_intel.country, travel_override)
            if port_intel is not None else None
        )

        # 6. Accessibility Intelligence
        acc_intel = AccessibilityIntelligence(
            cabin_is_accessible_certified=target_cabin.is_accessible_stateroom,
            door_clear_width_mm=target_cabin.door.clear_width_mm,
            has_step_free_access_to_gangway=True,
            tender_boat_accessibility_status="Level roll-on boarding supported; crew assistance stationed at platform.",
            nearest_accessible_restroom_deck=deck.deck_number,
            summary=acc_eval.summary if acc_eval else "Standard stateroom with step-free corridor spine access.",
            evidence_links=list(target_cabin.evidence_links),
        )

        # 7. Synthesize Decision Summary & Decisions Avoided
        decision_summary = DecisionSummarySynthesizer.synthesize(
            cabin_intel=cabin_intel,
            embark_intel=embark_intel,
            port_intel=port_intel,
            weather_intel=weather_intel,
            visa_intel=visa_intel,
            dining_intel=dining_intel,
            acc_intel=acc_intel,
        )

        # 8. Assemble Master Briefing
        # Only sections that exist contribute evidence. An absent section
        # contributes nothing rather than a placeholder link.
        all_evidence = list(target_cabin.evidence_links)
        for section in (port_intel, weather_intel, visa_intel, dining_intel,
                        travel_intel, embark_intel):
            if section is not None and getattr(section, "evidence_links", None):
                all_evidence.extend(section.evidence_links)

        return CruiseBriefing(
            briefing_id=f"BRIEFING-{ontology.imo_number}-{cabin_number}-D{itinerary.day_number:02d}",
            ship_name=ontology.name,
            ship_imo=ontology.imo_number,
            itinerary_day=itinerary.day_number,
            date_iso=itinerary.date_iso,
            cabin_intelligence=cabin_intel,
            embarkation_intelligence=embark_intel,
            port_intelligence=port_intel,
            weather_intelligence=weather_intel,
            visa_intelligence=visa_intel,
            dining_intelligence=dining_intel,
            accessibility_intelligence=acc_intel,
            travel_intelligence=travel_intel,
            decision_summary=decision_summary,
            evidence_manifest=all_evidence,
        )
