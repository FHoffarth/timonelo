#!/usr/bin/env python3
"""
CLI Tool: Voyage Experience & Community Intelligence (Sprint 12 / Chapter IV).
"Every Voyage Has Its Own Culture."
"Whatever tonight's programme may hold, I wish you a wonderful evening aboard. I'll remain on the bridge should you need me."
Usage:
    python tools/experience_intelligence_cli.py [--voyage standard | music | gourmet]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.experience_intelligence import (
    ExperienceIntelligenceEngine,
)


def main():
    parser = argparse.ArgumentParser(description="Voyage Experience Intelligence CLI")
    parser.add_argument(
        "--voyage",
        type=str,
        default="standard",
        choices=["standard", "music", "gourmet"],
        help="Voyage experience profile key"
    )
    args = parser.parse_args()

    v_map = {
        "standard": "bellissima-asia-standard",
        "music": "music-festival-charter",
        "gourmet": "gourmet-food-wine",
    }
    voyage_id = v_map.get(args.voyage, "bellissima-asia-standard")
    profile = ExperienceIntelligenceEngine.get_experience_profile(voyage_id)

    print("==========================================================================")
    print(f"       TIMONELO EXPERIENCE INTELLIGENCE · {profile.voyage_theme_title.upper()}")
    print(f"       Schiff: {profile.ship_name} · Format: {profile.experience_type.value.split('(')[0].strip()}")
    if profile.charter_organizer:
        print(f"       Veranstalter / Charter: {profile.charter_organizer}")
    print("==========================================================================\n")

    # 1. Dress Code & Atmosphere
    print("[1] [KLEIDERORDNUNG & ABENDMOTTO]:")
    print(f"  * {profile.dress_guidance_summary}\n")

    # 2. Today's Event Timeline
    print("[2] [TAGES- & ABENDPROGRAMM DER REISE]:")
    for ev in profile.events_schedule:
        print(f"  * {ev.start_time} - {ev.title} ({ev.venue_name} · {ev.deck_location})")
        print(f"    Kleidung  : {ev.dress_code.value.split('(')[0].strip()} | Andrang: {ev.crowd_expectation}")
        print(f"    Inhalt    : {ev.description}")
        if ev.quieter_alternative_venue:
            print(f"    Ruhig-Tipp: {ev.quieter_alternative_venue}")
        print()

    # 3. Busy Areas to Avoid (Negative Intelligence)
    print("[3] [MEIDEN · HIGH TRAFFIC ZONEN]:")
    for b in profile.busy_areas_to_avoid:
        print(f"  ! {b}")
    print()

    # 4. Quiet Retreats
    print("[4] [RUHIGE RUECKZUGS-ORTE AN BORD]:")
    for q in profile.quiet_retreat_venues:
        print(f"  * {q}")
    print()

    # 5. BOT Proactive Observations
    print("[5] [BRIDGE OFFICER TIM BEOBACHTUNGEN]:")
    for obs in profile.bot_proactive_observations:
        print(f"  » {obs}")
    print()

    print("--------------------------------------------------------------------------")
    print(f"Bridge Officer Tim: \"{profile.bot_evening_sign_off}\"")
    print("==========================================================================")


if __name__ == "__main__":
    main()
