#!/usr/bin/env python3
"""
CLI Tool: Context Engine Demonstration.
Evaluates the SAME physical cabin against DIFFERENT personal passenger and trip contexts.
Usage:
    python tools/context_engine_demo.py [--cabin 14122]
"""

import sys
import os
import json
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.context_engine import (
    ContextEngine,
    CabinFactProfile,
    PassengerContext,
    PassengerProfileType,
    TripContext,
    Season,
    SeaState,
    RouteHeading,
)


def render_context_decision_card(advice, passenger, trip):
    print("+------------------------------------------------------------------------+")
    print(f"| STATEROOM EVALUATION: Cabin {advice.cabin_number:<12} (FOR YOUR TRIP)          |")
    print(f"| Passenger Profile: {advice.passenger_profile:<30} Verdict: {advice.suitability_verdict:<15}|")
    print(f"| Suitability Score: {advice.suitability_score:>5.1f} / 100   Route: {trip.route_name:<30}|")
    print("+------------------------------------------------------------------------+")
    print("| WHY THIS STATEROOM WORKS FOR YOU:                                      |")
    for b in advice.benefits_for_you:
        print(f"|   [PRO] {b:<63}|")
    print("|                                                                        |")
    print("| SITUATIONAL TRADE-OFFS TO KEEP IN MIND:                                |")
    for t in advice.trade_offs_for_you:
        print(f"|   [CON] {t:<63}|")
    print("|                                                                        |")
    print("| CONTEXTUAL REASONING RULES APPLIED:                                    |")
    for r in advice.contextual_rules_triggered:
        print(f"|   * {r:<65}|")
    print("+------------------------------------------------------------------------+")
    print(f"| Summary: {advice.situational_verdict_summary:<61}|")
    print("+------------------------------------------------------------------------+\n")


def main():
    parser = argparse.ArgumentParser(description="Context Engine Demonstration")
    parser.add_argument("--cabin", type=str, default="14122", help="Cabin number to evaluate")
    args = parser.parse_args()

    # Universal Immutable Physical Facts of MSC Bellissima Cabin 14122
    cabin_14122 = CabinFactProfile(
        cabin_number=args.cabin,
        deck_number=14,
        deck_name="Tiziano",
        category="Balcony Deluxe (BR2)",
        hull_side="STARBOARD",
        zone="AFT",
        interior_sqm=19.0,
        balcony_sqm=4.5,
        distance_to_nearest_lift_m=24.6,
        distance_to_nearest_stairs_m=18.0,
        distance_to_main_theatre_m=195.0,  # Aft Deck 14 to Forward Deck 5
        distance_to_buffet_m=25.0,         # 1 Deck up via Aft stairs
        noise_risk_fact="LOW_PANTRY_ADJACENT",
        view_category_fact="UNOBSTRUCTED",
        step_free_accessible=False,
        vertical_neighbor_above="Marketplace Buffet Seating Area (Carpeted)",
        vertical_neighbor_below="Residential Staterooms (Deck 13)",
    )

    print("==========================================================================")
    print(f"       TIMONELO CONTEXT ENGINE: EVALUATING CABIN {args.cabin}               ")
    print("         (Universal Facts -> Highly Personalized Advice)                  ")
    print("==========================================================================\n")

    # SCENARIO 1: Motion Sensitive + Late Theatre Lover (Atlantic / Western Med)
    passenger_1 = PassengerContext(
        profile_type=PassengerProfileType.MOTION_SENSITIVE,
        motion_sensitive=True,
        priority_theatre_and_shows=True,
        prefers_quiet_sleep=True,
    )
    trip_1 = TripContext(
        ship_slug="msc-bellissima",
        route_slug="western-mediterranean-7n",
        route_name="7-Night Western Mediterranean",
        season=Season.AUTUMN,
        heading=RouteHeading.WESTBOUND,
        expected_sea_state=SeaState.MODERATE,
    )
    advice_1 = ContextEngine.evaluate_cabin_for_passenger(cabin_14122, passenger_1, trip_1)
    render_context_decision_card(advice_1, passenger_1, trip_1)

    # SCENARIO 2: Scenic Photographer & Early Riser (Norwegian Fjords Northbound)
    passenger_2 = PassengerContext(
        profile_type=PassengerProfileType.PHOTOGRAPHER,
        priority_scenic_photography=True,
        prefers_quiet_sleep=True,
    )
    trip_2 = TripContext(
        ship_slug="msc-bellissima",
        route_slug="norwegian-fjords-7n",
        route_name="7-Night Norwegian Fjords",
        season=Season.SUMMER,
        heading=RouteHeading.NORTHBOUND,
        expected_sea_state=SeaState.CALM,
    )
    advice_2 = ContextEngine.evaluate_cabin_for_passenger(cabin_14122, passenger_2, trip_2)
    render_context_decision_card(advice_2, passenger_2, trip_2)

    # SCENARIO 3: Family with Young Children & Stroller (Summer Med)
    passenger_3 = PassengerContext(
        profile_type=PassengerProfileType.FAMILY_WITH_KIDS,
        traveling_with_children=True,
        priority_quick_buffet_access=True,
    )
    trip_3 = TripContext(
        ship_slug="msc-bellissima",
        route_slug="western-mediterranean-7n",
        route_name="7-Night Western Mediterranean",
        season=Season.SUMMER,
        heading=RouteHeading.CIRCULAR,
        expected_sea_state=SeaState.CALM,
    )
    advice_3 = ContextEngine.evaluate_cabin_for_passenger(cabin_14122, passenger_3, trip_3)
    render_context_decision_card(advice_3, passenger_3, trip_3)


if __name__ == "__main__":
    main()
