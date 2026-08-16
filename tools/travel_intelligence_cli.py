#!/usr/bin/env python3
"""
CLI Tool: Real-time Travel Intelligence & Negative Intelligence Companion.
Answers: "Was sollte ich JETZT tun?"
Usage:
    python tools/travel_intelligence_cli.py [--phase EMBARKATION_DAY | SEA_DAY | PORT_DAY | PRE_CRUISE]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.travel_intelligence import TravelIntelligenceEngine, JourneyPhase


def main():
    parser = argparse.ArgumentParser(description="Travel Intelligence Companion CLI")
    parser.add_argument("--phase", type=str, default="EMBARKATION_DAY", choices=[p.value for p in JourneyPhase])
    args = parser.parse_args()

    phase_enum = JourneyPhase(args.phase)
    actions = TravelIntelligenceEngine.get_actions_for_phase(phase_enum)

    print("==========================================================================")
    print(f"       TIMONELO TRAVEL INTELLIGENCE COMPANION · PHASE: {args.phase}       ")
    print("       Fokus: Negative Intelligence (Zeitfresser & Fallen vermeiden)      ")
    print("==========================================================================\n")

    for i, a in enumerate(actions, 1):
        print(f"[{i}] {a.urgency.value} ({a.time_window}): {a.headline}")
        print(f"    Was tun? : {a.what_to_do_now}")
        print(f"    ! MEIDEN : {a.negative_intelligence_to_avoid}")
        print("    Gruende  :")
        for r in a.reasons_top_3:
            print(f"      * {r}")
        print("    Schritte :")
        for s in a.concrete_steps:
            print(f"      -> {s}")
        print(f"    Quellen  : {', '.join(a.evidence_sources)} (Konfidenz: {a.confidence_score}%)")
        print("--------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
