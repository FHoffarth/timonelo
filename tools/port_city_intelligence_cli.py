#!/usr/bin/env python3
"""
CLI Tool: Port & City Intelligence & Shore Time Companion.
"Enjoy your time ashore. I will be here when you return."
Usage:
    python tools/port_city_intelligence_cli.py [--city yokohama | shanghai | genoa | naples | barcelona | singapore]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.port_city_intelligence import PortCityIntelligenceEngine


def main():
    parser = argparse.ArgumentParser(description="Port & City Destination Intelligence CLI")
    parser.add_argument(
        "--city",
        type=str,
        default="yokohama",
        choices=["yokohama", "shanghai", "genoa", "naples", "barcelona", "singapore"],
        help="City destination slug"
    )
    args = parser.parse_args()

    profile = PortCityIntelligenceEngine.get_destination_profile(args.city)
    if not profile:
        print(f"Error: No profile found for '{args.city}'")
        return

    print("==========================================================================")
    print(f"       TIMONELO PORT & CITY INTELLIGENCE · {profile.official_name.upper()} ")
    print(f"       Terminal: {profile.terminal_name} ({profile.country})")
    print(f"       Zeitzone: {profile.timezone} | Waehrung: {profile.currency.split('·')[0]}")
    print("==========================================================================\n")

    # 1. Shore Time Window
    st = profile.shore_time
    print("[1] [SHORE TIME] ZEITFENSTER AN LAND & RUECKKEHR-PUFFER:")
    print(f"  * Anlegen         : {st.scheduled_arrival}")
    print(f"  * All Aboard      : {st.scheduled_all_aboard}")
    print(f"  * Spaeteste Rueckkehr: {st.recommended_latest_return} (Sicherheits-Puffer: {st.safe_buffer_minutes} min)")
    print(f"  * Stosszeiten     : {st.rush_hour_warning_window}")
    print(f"  * Sicherer Radius : {st.safe_walking_radius_km} km\n")

    # 2. Gangway-to-City Steps
    print("[2] [TRANSFER] VOM SCHIFF INS STADTZENTRUM (GANGWAY ROUTING):")
    for s in profile.gangway_steps:
        print(f"  [{s.step_num}] {s.title} (~{s.typical_minutes} min)")
        print(f"      {s.instruction}")
        print(f"      Orientierung: {s.orientation_hint}")
    print()

    # 3. Practical Essentials
    print("[3] [LOGISTIK] ESSENTIELLE STADTDATEN:")
    print(f"  * Sprache        : {profile.language} | Notruf: Polizei {profile.emergency_police} / Notarzt {profile.emergency_medical}")
    print(f"  * Trinkwasser    : {profile.tap_water.value}")
    print(f"  * OEPNV & Bahnen : {profile.public_transport_summary}")
    print(f"  * Ride-Hailing   : {', '.join(profile.ride_hailing_apps)}")
    print(f"  * Mobilfunk/eSIM : {profile.sim_esim_advice}\n")

    # 4. Negative Intelligence Traps
    print("[4] [NEGATIVE INTELLIGENCE] DIE HAEUFIGSTEN TOURISTENFALLEN:")
    for i, trap in enumerate(profile.negative_intelligence_traps, 1):
        print(f"  ! {trap}")
    print()

    # 5. Local Culinary Highlights
    print("[5] [KULINARIK] AUTHENTISCHE LOKALE HIGHLIGHTS:")
    for c in profile.local_culinary_tips:
        print(f"  * {c}")
    print()

    # 6. Bridge Officer Tim Proactive Notices & Closing
    print("[6] [BRIDGE OFFICER TIM] BEOBACHTUNGEN DER BRUECKE:")
    for notice in profile.bot_proactive_notices:
        print(f"  » {notice}")
    print()

    print("--------------------------------------------------------------------------")
    print(f"Bridge Officer Tim: \"{profile.bot_closing_phrase}\"")
    print("==========================================================================")


if __name__ == "__main__":
    main()
