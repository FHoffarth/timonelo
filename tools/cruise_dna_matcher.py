#!/usr/bin/env python3
"""
CLI Tool: Cruise Genome & Multidimensional DNA Matcher.
Usage:
    python tools/cruise_dna_matcher.py [--target-ship <slug>] [--run-scenarios]
"""

import sys
import os
import json
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.cruise_dna import (
    CruiseDNAMatcher,
    CANONICAL_GENOMES,
    PassengerPreferenceDNA,
)


def main():
    parser = argparse.ArgumentParser(description="Cruise Genome & Personal Preference Matcher")
    parser.add_argument("--target-ship", type=str, default="msc-bellissima", help="Ship slug to match similarity against")
    parser.add_argument("--run-scenarios", action="store_true", help="Run sample passenger preference matching scenarios")
    args = parser.parse_args()

    print("=========================================================")
    print("           TIMONELO CRUISE GENOME & DNA MATCHER          ")
    print("=========================================================")

    # 1. Ship Similarity Vector Calculation
    target_slug = args.target_ship
    if target_slug in CANONICAL_GENOMES:
        target = CANONICAL_GENOMES[target_slug]
        print(f"Target Vessel Genome: {target.ship_name} [{target.archetype.value}]")
        print(f"Signature Traits    : {', '.join(target.signature_traits)}")
        print("---------------------------------------------------------")
        print(f"If you loved {target.ship_name}, you will appreciate:")
        matches = CruiseDNAMatcher.find_top_matches(target_slug, top_k=6)
        for m in matches:
            print(f"  * {m['name']:<22}: {m['similarity_pct']:>5.1f}% match -> {m['relationship']}")
            print(f"      Archetype: {m['archetype']}")
            print(f"      Key Hook : {m['signature_traits'][0]}")
        print("---------------------------------------------------------")

    # 2. Explainable Passenger Preference Scenarios
    print("PASSENGER PREFERENCE REASONING ENGINE SCENARIOS:")
    
    # Scenario 1: Modern Luxury & Adults Only
    pref_luxury_adults = PassengerPreferenceDNA(
        avoids_children_and_noise=True,
        loves_culinary_variety=True,
        prefers_modern_luxury=True,
        seeks_quiet_and_relaxation=True,
    )
    res_1 = CruiseDNAMatcher.match_passenger_preferences(pref_luxury_adults, top_k=2)
    print("\n[Scenario A] 'I avoid children, love fine dining & modern luxury, and seek relaxation':")
    for r in res_1:
        print(f"  -> Recommended: {r['name']} ({r['match_score_pct']}% Match) [{r['archetype']}]")
        for w in r["why"]:
            print(f"     * WHY: {w}")

    # Scenario 2: Intimate River & Short Walking Distances
    pref_river_compact = PassengerPreferenceDNA(
        prefers_intimate_river_feeling=True,
        dislikes_long_walking_distances=True,
        avoids_crowded_buffets=True,
        seeks_quiet_and_relaxation=True,
    )
    res_2 = CruiseDNAMatcher.match_passenger_preferences(pref_river_compact, top_k=2)
    print("\n[Scenario B] 'I dislike long walking distances, hate crowded buffets, and love intimate river sailing':")
    for r in res_2:
        print(f"  -> Recommended: {r['name']} ({r['match_score_pct']}% Match) [{r['archetype']}]")
        for w in r["why"]:
            print(f"     * WHY: {w}")

    print("=========================================================")


if __name__ == "__main__":
    main()
