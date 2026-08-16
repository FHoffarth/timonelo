#!/usr/bin/env python3
"""
CLI Tool: Context Engine & Proactive Bridge Officer Tim Briefing.
"I have reviewed your journey. Everything is proceeding as expected. I remain on the bridge."
Usage:
    python tools/context_engine_cli.py [--date 2026-10-03]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.context_engine import (
    ContextEngine,
    TravellerContext,
    JourneyContext,
    BotMemory,
)


def main():
    parser = argparse.ArgumentParser(description="Context Engine & Proactive Bridge Officer Tim CLI")
    parser.add_argument(
        "--date",
        type=str,
        default="2026-10-03",
        help="Simulated current date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    briefing = ContextEngine.generate_context_briefing(simulated_date_iso=args.date)

    print("==========================================================================")
    print("        TIMONELO CONTEXT ENGINE · BRIDGE OFFICER TIM BRIEFING             ")
    print(f"        Datum: {briefing.date_display}                                    ")
    print(f"        Phase: {briefing.phase.value}                                     ")
    print("==========================================================================\n")

    print(f"{briefing.greeting_line}")
    print(f"{briefing.status_headline}\n")

    # 1. BOT Noticed Observations
    print("[1] [BOT NOTICED] PROAKTIVE BEOBACHTUNGEN DER BRUECKE:")
    for notice in briefing.proactive_bot_notices:
        print(f"  * {notice}")
    print()

    # 2. Top 3 Priorities
    print("[2] [TOP 3 PRIORITAETEN] HANDLUNGSEMPFEHLUNGEN HEUTE:")
    for i, task in enumerate(briefing.top_priorities, 1):
        print(f"  [{i}] {task.title} (Frist: {task.deadline_display} · {task.priority.value.split('(')[0].strip()})")
        print(f"      Grund: {task.reason}")
        print(f"      Aktion: {task.recommended_action}")
        print(f"      Evidenz: {task.evidence_source}")
    print()

    # 3. Completed Milestones (Memory Layer)
    print("[3] [MEMORY LAYER] BEREITS ERFOLGREICH GEPRUEFT & GESICHERT:")
    for m in briefing.completed_milestones:
        print(f"  [OK] {m}")
    print()

    print("--------------------------------------------------------------------------")
    print(f"Bridge Officer Tim: \"{briefing.sign_off_phrase}\"")
    print("==========================================================================")


if __name__ == "__main__":
    main()
