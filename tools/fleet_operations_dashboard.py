#!/usr/bin/env python3
"""
CLI Tool: Live Fleet Operations & Seasonal Deployment Dashboard.
Usage:
    python tools/fleet_operations_dashboard.py [--ship <slug>]
"""

import sys
import os
import json
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler


def main():
    parser = argparse.ArgumentParser(description="Live Fleet Operations Dashboard")
    parser.add_argument("--ship", type=str, default="msc-bellissima", help="Ship slug to inspect operations for")
    args = parser.parse_args()

    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    deployments = db.get("deployments", {})
    voyages = db.get("voyages", {})
    fleet_status = db.get("fleet_status", {})

    print("==========================================================================")
    print("           TIMONELO LIVE FLEET & OPERATIONS INTELLIGENCE DASHBOARD        ")
    print("==========================================================================")

    # 1. Active Fleet Status
    print("[1] ACTIVE LIVE FLEET STATUS & POSITIONING:")
    for slug, status in fleet_status.items():
        coords = status.get("position_lat_lon")
        pos_str = f"({coords[0]:.4f} N, {coords[1]:.4f} E)" if coords else "UNKNOWN (No AIS lock)"
        print(f"  * {slug.upper():<20} -> State: {status.get('operational_state'):<12} Port: {status.get('current_port_slug'):<10} Next: {status.get('next_port_slug')}")
        print(f"      Position: {pos_str} | ETA: {status.get('eta_next_port')} | Timezone: {status.get('local_time_zone')}")
        print(f"      Source: {status.get('source_feed')} (Freshness: {status.get('freshness_seconds')}s)")
    print("--------------------------------------------------------------------------")

    # 2. Seasonal Deployments
    print("[2] SEASONAL MIGRATION & DEPLOYMENT SCHEDULES:")
    for dep_id, dep in deployments.items():
        print(f"  * [{dep.get('season')}] {dep.get('ship_slug').upper()} -> Region: {dep.get('region_slug')}")
        print(f"      Dates    : {dep.get('start_date')} to {dep.get('end_date')}")
        print(f"      Homeports: {', '.join(dep.get('homeports', []))}")
        print(f"      Notes    : {dep.get('notes')}")
    print("--------------------------------------------------------------------------")

    # 3. Structured Voyages & Port Calls
    print(f"[3] STRUCTURED VOYAGE SCHEDULE (Cruise {args.ship.upper()}):")
    for v_id, voy in voyages.items():
        if voy.get("ship_slug") == args.ship:
            print(f"  Voyage ID    : {voy.get('voyage_id')} (Cruise No: {voy.get('cruise_number')})")
            print(f"  Route & Span : {voy.get('start_date')} to {voy.get('end_date')} ({voy.get('nautical_miles')} nm, {voy.get('sea_days_count')} Sea Days)")
            print(f"  Weather Zone : {voy.get('weather_zone')}")
            print("  Port Calls & Turnaround Logistics:")
            for call in voy.get("port_calls", []):
                t_flag = "[TURNAROUND]" if call.get("is_turnaround") else "[PORT CALL]"
                print(f"    * {call.get('port_slug'):<12} {t_flag:<14} Arr: {call.get('arrival_iso')[11:16] if call.get('arrival_iso') else '--:--'} Dep: {call.get('departure_iso')[11:16] if call.get('departure_iso') else '--:--'} | Gangway Deck {call.get('gangway_deck')} | {call.get('terminal_name')}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
