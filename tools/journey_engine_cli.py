#!/usr/bin/env python3
"""
CLI Tool: Journey Engine & Personal Travel OS.
Usage:
    python tools/journey_engine_cli.py [--journey shanghai | med]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.journey_engine import JourneyEngine


def main():
    parser = argparse.ArgumentParser(description="Personal Cruise Journey Engine CLI")
    parser.add_argument("--journey", type=str, default="shanghai", choices=["shanghai", "med"])
    args = parser.parse_args()

    if args.journey == "shanghai":
        config = JourneyEngine.get_reference_shanghai_tokyo_journey()
    else:
        config = JourneyEngine.get_reference_mediterranean_journey()

    cards = JourneyEngine.generate_journey_timeline(config)

    print("==========================================================================")
    print(f"       TIMONELO PERSONAL CRUISE OPERATING SYSTEM · MY JOURNEY             ")
    print(f"       Reise: {config.ship_name} ({config.departure_port_name} -> {config.arrival_port_name})")
    print(f"       Kabine: {config.cabin_number} | Daten: {config.embarkation_date} bis {config.disembarkation_date}")
    print("==========================================================================\n")

    for i, c in enumerate(cards, 1):
        print(f"[{i}] {c.time_label} · {c.stage_title}")
        print(f"    Ziel: {c.current_objective}")
        print(f"    Was tun? : {c.what_to_do_now}")
        print(f"    Planen   : {c.what_to_prepare}")
        print(f"    ! MEIDEN : {c.negative_intelligence_to_avoid}")
        print(f"    Nächste  : {c.upcoming_decision}")
        print(f"    Warum?   : {c.why_recommendation_exists}")
        print(f"    Quellen  : {', '.join(c.evidence_sources)} (Konfidenz: {c.confidence_score}%)")
        print("--------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
