#!/usr/bin/env python3
"""
CLI Tool: Bridge Officer Tim Personal Cruise Concierge & Assistant Engine.
"Certainly. I've already prepared a recommendation for exactly that situation."
Usage:
    python tools/assistant_engine_cli.py [--action lunch | sunset | coffee | muster | time2h | mission]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.assistant_engine import (
    AssistantEngine,
    QuickActionQuery,
)


def main():
    parser = argparse.ArgumentParser(description="Bridge Officer Tim Cruise Concierge CLI")
    parser.add_argument(
        "--action",
        type=str,
        default="time2h",
        choices=["lunch", "sunset", "coffee", "muster", "time2h", "mission"],
        help="Action to query"
    )
    args = parser.parse_args()

    print("==========================================================================")
    print("      TIMONELO CRUISE ASSISTANT · BRIDGE OFFICER TIM CONCIERGE (SPRINT 10)")
    print("      'Certainly. I've already prepared a recommendation for that.'       ")
    print("==========================================================================\n")

    if args.action == "mission":
        msn = AssistantEngine.get_daily_mission("morning_yokohama")
        print(f"[TAGES-MISSION] {msn.mission_title.upper()}")
        print(f"  Phase   : {msn.phase_name} ({msn.estimated_duration_display})")
        print(f"  Ziel    : {msn.current_objective}\n")
        print("  [EMPFOHLEN]:")
        for r in msn.recommended_actions:
            print(f"    {r}")
        print("\n  [MEIDEN]:")
        for a in msn.negative_intelligence_avoid:
            print(f"    {a}")
        print(f"\n  Evidenz : {msn.evidence_source}\n")

    elif args.action == "time2h":
        bundle = AssistantEngine.evaluate_free_time(hours_available=2.0)
        print(f"{bundle.bot_opening_line}\n")
        print(f"[OPTIONEN FUER DIE NAECHSTEN 2 STUNDEN]:")
        for i, opt in enumerate(bundle.recommended_options, 1):
            status_tag = "[VERFUEGBAR]" if not opt.is_restricted else "[EINGESCHRAENKT]"
            print(f"  {i}. {opt.title} ({opt.deck_location}) · {status_tag}")
            print(f"     Grund      : {opt.reasoning}")
            print(f"     Aufwand    : Gehdistanz: {opt.walking_effort} | Stimmung: {opt.crowd_level}")
            if opt.is_restricted and opt.restriction_note:
                print(f"     Hinweis    : {opt.restriction_note}")
            print()
        print(f"Bridge Officer Tim: \"{bundle.bot_conclusion_line}\"\n")

    else:
        query_map = {
            "lunch": QuickActionQuery.LUNCH_WHERE,
            "sunset": QuickActionQuery.SUNSET_SPOT,
            "coffee": QuickActionQuery.QUIET_COFFEE,
            "muster": QuickActionQuery.MUSTER_STATION,
        }
        query = query_map.get(args.action, QuickActionQuery.LUNCH_WHERE)
        bundle = AssistantEngine.answer_quick_action(query)
        print(f"Frage: {bundle.query_text}")
        print(f"Bridge Officer Tim: {bundle.bot_opening_line}\n")
        for opt in bundle.recommended_options:
            print(f"  * {opt.title} ({opt.deck_location})")
            print(f"    Details: {opt.reasoning}")
            print(f"    Gehzeit: ~{opt.time_required_min} min | {opt.walking_effort}")
        print(f"\nFazit: {bundle.bot_conclusion_line}\n")

    print("--------------------------------------------------------------------------")
    print("Bridge Officer Tim: 'Ich bleibe auf der Brücke. Melden Sie sich jederzeit.'")
    print("==========================================================================")


if __name__ == "__main__":
    main()
