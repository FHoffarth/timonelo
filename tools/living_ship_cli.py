#!/usr/bin/env python3
"""
CLI Tool: Living Ship Digital Twin & Operational Interpretation Engine (Chapter V - Final Sprint).
"AIS tells you where a ship is. Bridge Officer Tim tells you what that means for you."
Usage:
    python tools/living_ship_cli.py [--state bellissima | andorinha]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.living_ship_engine import (
    DigitalTwinEngine,
)


def main():
    parser = argparse.ArgumentParser(description="Living Ship Digital Twin CLI")
    parser.add_argument(
        "--state",
        type=str,
        default="bellissima",
        choices=["bellissima", "andorinha"],
        help="Live voyage state key"
    )
    args = parser.parse_args()

    s_map = {
        "bellissima": "bellissima-live-yokohama",
        "andorinha": "andorinha-live-douro",
    }
    state_key = s_map.get(args.state, "bellissima-live-yokohama")
    live_state = DigitalTwinEngine.get_live_voyage_state(state_key)

    print("==========================================================================")
    print(f"       TIMONELO LIVING SHIP · DIGITAL TWIN OF THE VOYAGE                 ")
    print(f"       Schiff: {live_state.ship_name} · Status: {live_state.current_status.value.split('(')[0].strip()}")
    print(f"       Position: {live_state.current_location}")
    print("==========================================================================\n")

    # 1. Operational Telemetry & Environmental Context
    print("[1] [OPERATIVE SITUATION & WETTER]:")
    print(f"  * Geschwindigkeit : {live_state.current_speed_knots} Knoten")
    print(f"  * Wetter          : {live_state.weather_summary}")
    print(f"  * Seegang / Wind  : {live_state.sea_state_description} (Windstärke {live_state.wind_force_beaufort} Bft)")
    print(f"  * Nächster Hafen  : {live_state.eta_next_port}")
    if live_state.all_aboard_time:
        print(f"  * All Aboard      : {live_state.all_aboard_time} (Pünktliche Rückkehr)")
    print(f"  * Gangway-Status  : {'Geöffnet (Freier Durchgang)' if live_state.gangway_open else 'Geschlossen / Auf See'}\n")

    # 2. Operational Impacts (Passenger Translation Layer)
    print("[2] [PASSENGER TRANSLATION LAYER · MARITIME REALITAET IN VERSTAENDNIS]:")
    for imp in live_state.operational_changes:
        print(f"  * [{imp.change_title}]")
        print(f"    Maritimer Fakt: {imp.raw_maritime_fact}")
        print(f"    Bedeutung     : {imp.passenger_translation}")
        print(f"    Handlung      : {imp.recommended_action}")
        print(f"    Bereiche      : {', '.join(imp.affected_services)}")
        print()

    # 3. Bridge Observations
    print("[3] [BRIDGE OFFICER TIM BEOBACHTUNGEN]:")
    for obs in live_state.bot_observations:
        print(f"  » {obs}")
    print()

    # 4. Recommended Actions
    print("[4] [EMPFOHLENE SCHRITTE FUER GAESTE]:")
    for act in live_state.recommended_passenger_actions:
        print(f"  [OK] {act}")
    print()

    print("--------------------------------------------------------------------------")
    print(f"Bridge Officer Tim: \"{live_state.bridge_sign_off}\"")
    print("==========================================================================")
    print("FOUNDATION COMPLETE")
    print("Timonelo now possesses a complete digital twin of the traveller, the voyage, the ship and the operational context.")
    print("Bridge Officer Tim remains on the bridge.")
    print("==========================================================================")


if __name__ == "__main__":
    main()
