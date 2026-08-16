#!/usr/bin/env python3
"""
CLI Tool: Safety Intelligence & Muster Station Navigator.
Usage:
    python tools/safety_companion.py [--ship msc-bellissima] [--cabin 14122] [--from cabin]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.safety_intelligence import (
    SafetyIntelligenceEngine,
    CurrentLocationType,
)


def main():
    parser = argparse.ArgumentParser(description="Safety Intelligence & Muster Station Navigator CLI")
    parser.add_argument("--ship", type=str, default="msc-bellissima", help="Ship slug")
    parser.add_argument("--cabin", type=str, default="14122", help="Stateroom number")
    parser.add_argument(
        "--from",
        dest="from_loc",
        type=str,
        default="cabin",
        choices=["cabin", "buffet", "theater", "pool"],
        help="Current starting location"
    )
    args = parser.parse_args()

    loc_map = {
        "cabin": CurrentLocationType.CABIN,
        "buffet": CurrentLocationType.BUFFET,
        "theater": CurrentLocationType.THEATRE,
        "pool": CurrentLocationType.POOL,
    }

    plan = SafetyIntelligenceEngine.calculate_navigation_plan(
        ship_slug=args.ship,
        ship_name="MSC Bellissima",
        cabin_num=args.cabin,
        from_location=loc_map[args.from_loc],
    )

    print("==========================================================================")
    print("             TIMONELO SAFETY INTELLIGENCE & MUSTER COMPANION              ")
    print(f"             Schiff: {plan.ship_name} | Kabine: {plan.cabin_number} | Start: {plan.start_location}")
    print("==========================================================================\n")

    print("[1] ZUGEWIESENE MUSTERSTATION & SICHERHEITSDATEN:")
    print(f"  * Station Code  : Musterstation {plan.assigned_muster_station.station_code}")
    print(f"  * Deck & Seite  : Deck {plan.assigned_muster_station.deck} · {plan.assigned_muster_station.side.value}")
    print(f"  * Örtlichkeit   : {plan.assigned_muster_station.venue_name}")
    print(f"  * Rettungsboote : Boote #{', #'.join(map(str, plan.assigned_muster_station.primary_lifeboat_numbers))}")
    print(f"  * Drill-Status  : {plan.safety_drill_status}\n")

    print("[2] ROUTEN- & GEHZEIT-KALKULATION:")
    print(f"  * Gehzeit       : ca. {plan.estimated_walking_time_min} Minuten")
    print(f"  * Distanz       : {plan.distance_meters} Meter")
    print(f"  * Deckwechsel   : {plan.deck_changes} Decks\n")

    print("[3] EMPFOHLENE ROUTE (STEP-BY-STEP):")
    for s in plan.primary_route_steps:
        print(f"  [{s.step_number}] (Deck {s.deck} · {s.transit_element})")
        print(f"      {s.instruction}")
        print(f"      Tipp: {s.orientation_hint}\n")

    print("[4] NEGATIVE INTELLIGENCE (WAS NICHT TUN):")
    for r in plan.negative_intelligence_rules:
        print(f"  ! {r}")

    print("\n==========================================================================")


if __name__ == "__main__":
    main()
