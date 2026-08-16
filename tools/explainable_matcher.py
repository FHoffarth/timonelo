#!/usr/bin/env python3
"""
CLI Tool: Explainable Recommendation Cards & Head-to-Head Ship Comparisons.
Usage:
    python tools/explainable_matcher.py [--target-ship <slug>] [--compare <slug_b>] [--persona <persona>]
"""

import sys
import os
import json
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.explainable_matching import (
    ExplainableMatchingEngine,
    PassengerPersona,
)


def render_recommendation_card(rec):
    print("+------------------------------------------------------------------------+")
    print(f"| RECOMMENDATION: {rec.candidate_ship_name:<55}|")
    print(f"| Match Strength: {rec.match_strength.value:<30} Confidence: {rec.confidence_level:<18}|")
    print(f"| Evidence Coverage: {rec.evidence_coverage_pct:.0f}%{' '*50}|")
    print("+------------------------------------------------------------------------+")
    print("| WHY TIMONELO RECOMMENDS IT:                                            |")
    for w in rec.why_recommended:
        print(f"|   [WHY] {w:<63}|")
    if rec.things_that_are_different:
        print("|                                                                        |")
        print("| THINGS THAT ARE DIFFERENT:                                             |")
        for d in rec.things_that_are_different:
            print(f"|   [DIFF] {d:<62}|")
    if rec.reasons_not_to_choose:
        print("|                                                                        |")
        print("| REASONS NOT TO CHOOSE (TRADE-OFFS):                                    |")
        for n in rec.reasons_not_to_choose:
            print(f"|   [RISK] {n:<62}|")
    if rec.persona_context:
        print("|                                                                        |")
        print(f"| PERSONA CONTEXT: {rec.persona_context:<53}|")
    print("+------------------------------------------------------------------------+")
    print(f"| Recommendation ID: {rec.recommendation_id:<30} Engine: {rec.engine_version:<19}|")
    print("+------------------------------------------------------------------------+")


def main():
    parser = argparse.ArgumentParser(description="Explainable Recommendation Engine")
    parser.add_argument("--target-ship", type=str, default="msc-bellissima", help="Reference ship")
    parser.add_argument("--candidate-ship", type=str, default="msc-world-europa", help="Candidate ship to explain")
    parser.add_argument("--compare", type=str, help="Run head-to-head comparison against target ship")
    parser.add_argument("--persona", type=str, help="Persona: families, luxury_couples, older_guests, etc.")
    args = parser.parse_args()

    print("==========================================================================")
    print("           TIMONELO EXPLAINABLE RECOMMENDATION INTELLIGENCE               ")
    print("==========================================================================")

    # 1. Generate Explainable Card
    persona_enum = None
    if args.persona:
        for p in PassengerPersona:
            if args.persona.lower() in p.name.lower():
                persona_enum = p
                break

    rec = ExplainableMatchingEngine.generate_recommendation(
        target_slug=args.target_ship,
        candidate_slug=args.candidate_ship,
        persona=persona_enum,
    )
    if rec:
        print(f"Target Baseline: {rec.target_ship_name}\n")
        render_recommendation_card(rec)

    # 2. Head-to-Head Comparison
    compare_target = args.compare or "msc-world-europa"
    comp = ExplainableMatchingEngine.compare_ships(args.target_ship, compare_target)
    if comp:
        print("\n==========================================================================")
        print(f"   HEAD-TO-HEAD COMPARISON: {comp.ship_a_name}  vs.  {comp.ship_b_name}")
        print("==========================================================================")
        print("\n[Shared Experience & Design DNA]:")
        for s in comp.shared_experiences:
            print(f"  * {s}")

        print("\n[Key Experiential & Architectural Differences]:")
        for d in comp.different_experiences:
            print(f"  * {d}")

        print("\n[Naval Engineering & Operational Differences]:")
        for o in comp.operational_differences:
            print(f"  * {o}")

        print("\n[Who Will Prefer Each Ship?]:")
        print(f"  -> Choose {comp.ship_a_name} if:")
        for pa in comp.who_will_prefer_ship_a:
            print(f"     * {pa}")
        print(f"  -> Choose {comp.ship_b_name} if:")
        for pb in comp.who_will_prefer_ship_b:
            print(f"     * {pb}")
        print("==========================================================================")


if __name__ == "__main__":
    main()
