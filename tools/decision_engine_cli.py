#!/usr/bin/env python3
"""
CLI Tool: Deterministic Decision Engine (Chapter III - Sprint 01).
Renders the standard 5-point decision format:
- Warum?
- 3 wichtigste Gründe
- 2 Unterschiede
- 1 Risiko
- Nächster Schritt
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.decision_engine import DecisionEngine
from src.timonelo.database.context_engine import (
    CabinFactProfile,
    PassengerContext,
    PassengerProfileType,
    TripContext,
    Season,
    SeaState,
    RouteHeading,
)


def render_decision_card(card):
    print("+------------------------------------------------------------------------+")
    print(f"| ENTSCHEIDUNG: {card.target_entity:<25} -> {card.candidate_entity:<28}|")
    print(f"| Urteil: {card.verdict.value:<30} Konfidenz: {card.confidence_score:>5.1f}%{' '*12}|")
    print("+------------------------------------------------------------------------+")
    print(f"| WARUM?                                                                 |")
    print(f"|   > {card.warum:<67}|")
    print("|                                                                        |")
    print("| 3 WICHTIGSTE GRUENDE:                                                  |")
    for i, g in enumerate(card.gruende_top_3, 1):
        print(f"|   {i}. {g:<66}|")
    print("|                                                                        |")
    print("| 2 UNTERSCHIEDE:                                                        |")
    for i, u in enumerate(card.unterschiede_2, 1):
        print(f"|   {i}. {u:<66}|")
    print("|                                                                        |")
    print("| 1 RISIKO / TRADE-OFF:                                                  |")
    print(f"|   ! {card.risiko_1:<67}|")
    print("|                                                                        |")
    print("| NAECHSTER SCHRITT:                                                     |")
    print(f"|   -> {card.naechster_schritt:<66}|")
    print("+------------------------------------------------------------------------+")
    print(f"| Decision-ID: {card.decision_id:<28} Deterministisch: {str(card.is_deterministic):<16}|")
    print("+------------------------------------------------------------------------+\n")


def main():
    parser = argparse.ArgumentParser(description="Deterministic Decision Engine CLI")
    parser.add_argument("--ship-target", type=str, default="msc-bellissima")
    parser.add_argument("--ship-candidate", type=str, default="msc-world-europa")
    args = parser.parse_args()

    print("==========================================================================")
    print("           TIMONELO DETERMINISTIC DECISION ENGINE (CHAPTER III)           ")
    print("==========================================================================\n")

    # 1. Ship Selection Decision
    print("[FALL 1: SCHIFFS-ENTSCHEIDUNG]")
    ship_decision = DecisionEngine.evaluate_ship_decision(args.ship_target, args.ship_candidate)
    render_decision_card(ship_decision)

    # 2. Cabin Decision (Motion Sensitive)
    cabin_14122 = CabinFactProfile(
        cabin_number="14122",
        deck_number=14,
        deck_name="Tiziano",
        category="Balcony Deluxe (BR2)",
        hull_side="STARBOARD",
        zone="AFT",
        interior_sqm=19.0,
        balcony_sqm=4.5,
        distance_to_nearest_lift_m=24.6,
        distance_to_nearest_stairs_m=18.0,
        distance_to_main_theatre_m=195.0,
        distance_to_buffet_m=25.0,
        noise_risk_fact="LOW_PANTRY_ADJACENT",
        view_category_fact="UNOBSTRUCTED",
        step_free_accessible=False,
        vertical_neighbor_above="Marketplace Buffet Seating Area (Carpeted)",
        vertical_neighbor_below="Residential Staterooms (Deck 13)",
    )

    passenger_motion = PassengerContext(
        profile_type=PassengerProfileType.MOTION_SENSITIVE,
        motion_sensitive=True,
        priority_theatre_and_shows=True,
    )
    trip_med = TripContext(
        ship_slug="msc-bellissima",
        route_slug="western-med-7n",
        route_name="7-Nächte Westliches Mittelmeer",
        season=Season.AUTUMN,
        heading=RouteHeading.WESTBOUND,
        expected_sea_state=SeaState.MODERATE,
    )

    print("[FALL 2: KABINEN-ENTSCHEIDUNG (SEEKRANKHEIT / LAUFWEGE)]")
    cabin_decision_1 = DecisionEngine.evaluate_cabin_decision(cabin_14122, passenger_motion, trip_med)
    render_decision_card(cabin_decision_1)

    # 3. Cabin Decision (Photographer)
    passenger_photo = PassengerContext(
        profile_type=PassengerProfileType.PHOTOGRAPHER,
        priority_scenic_photography=True,
    )
    trip_fjord = TripContext(
        ship_slug="msc-bellissima",
        route_slug="norwegian-fjords-7n",
        route_name="7-Nächte Norwegische Fjorde",
        season=Season.SUMMER,
        heading=RouteHeading.NORTHBOUND,
        expected_sea_state=SeaState.CALM,
    )

    print("[FALL 3: KABINEN-ENTSCHEIDUNG (FOTOGRAF / FJORDE)]")
    cabin_decision_2 = DecisionEngine.evaluate_cabin_decision(cabin_14122, passenger_photo, trip_fjord)
    render_decision_card(cabin_decision_2)


if __name__ == "__main__":
    main()
