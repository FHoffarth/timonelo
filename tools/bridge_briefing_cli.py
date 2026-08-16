#!/usr/bin/env python3
"""
CLI Tool: Bridge Officer Tim (BOT) v1.0 & Daily Bridge Briefing.
"Ich bleibe auf der Brücke. Melden Sie sich jederzeit."
Usage:
    python tools/bridge_briefing_cli.py [--phase pre12 | checkin3 | shanghai | embarkation | seaday | yokohama | disembark]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.bridge_officer import (
    BridgeOfficerEngine,
    BriefingPhase,
)


def main():
    parser = argparse.ArgumentParser(description="Bridge Officer Tim (BOT) Daily Briefing CLI")
    parser.add_argument(
        "--phase",
        type=str,
        default="pre12",
        choices=["pre12", "checkin3", "shanghai", "embarkation", "seaday", "yokohama", "disembark"],
        help="Journey phase for the Bridge Briefing"
    )
    parser.add_argument("--name", type=str, default="Florian", help="Traveler's name")
    args = parser.parse_args()

    phase_map = {
        "pre12": BriefingPhase.PRE_CRUISE_12D,
        "checkin3": BriefingPhase.CHECKIN_3D,
        "shanghai": BriefingPhase.CITY_SHANGHAI,
        "embarkation": BriefingPhase.EMBARKATION_BOARDING,
        "seaday": BriefingPhase.SEA_DAY,
        "yokohama": BriefingPhase.PORT_YOKOHAMA,
        "disembark": BriefingPhase.DISEMBARKATION,
    }

    briefing = BridgeOfficerEngine.generate_briefing(
        phase=phase_map[args.phase],
        traveler_name=args.name,
        ship_name="MSC Bellissima",
        cabin_num="14122",
    )

    print("==========================================================================")
    print(f"             BRIDGE BRIEFING · {briefing.date_display.upper()}            ")
    print(f"             Bridge Officer Tim (BOT) · {briefing.phase_context}          ")
    print("==========================================================================\n")

    print(briefing.greeting_line)
    print(f"{briefing.phase_context}\n")

    if briefing.proactive_notices:
        print("[BOT NOTICED · PROAKTIVE HINWEISE]")
        for n in briefing.proactive_notices:
            print(f"  * {n.headline}")
            print(f"    {n.content}")
            print(f"    (Evidenz: {n.evidence_source})\n")

    print("[HEUTIGE FOKUSPUNKTE & HANDLUNGEN]")
    for i, p in enumerate(briefing.daily_focus_points, 1):
        print(f"  {i}. {p}")

    print(f"\n[MARITIMER EINBLICK DER BRÜCKE]")
    print(f"  » {briefing.maritime_insight} «\n")

    print("--------------------------------------------------------------------------")
    print(briefing.sign_off)
    print("==========================================================================")


if __name__ == "__main__":
    main()
