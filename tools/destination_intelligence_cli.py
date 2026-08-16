#!/usr/bin/env python3
"""
CLI Tool: Destination Intelligence & Port City Logistics Engine.
Usage:
    python tools/destination_intelligence_cli.py [--city shanghai | tokyo-yokohama | genoa | barcelona]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.destination_engine import DestinationIntelligenceEngine


def main():
    parser = argparse.ArgumentParser(description="Destination Intelligence CLI")
    parser.add_argument(
        "--city",
        type=str,
        default="shanghai",
        choices=["shanghai", "tokyo-yokohama", "genoa", "barcelona"],
        help="Port slug to inspect destination logistics for"
    )
    args = parser.parse_args()

    dest = DestinationIntelligenceEngine.get_destination_by_slug(args.city)
    if not dest:
        print(f"Error: Unknown destination slug '{args.city}'")
        return

    print("==========================================================================")
    print(f"     TIMONELO DESTINATION INTELLIGENCE · {dest.city_name.upper()}, {dest.country.upper()}     ")
    print(f"     Zeitzone: {dest.timezone} | Währung: {dest.currency}")
    print(f"     Stecker : {dest.power_plugs.value} | ÖPNV-Ticket: {dest.local_transport_card}")
    print(f"     Notruf  : Polizei {dest.emergency_phone_police} / Notarzt {dest.emergency_phone_medical}")
    print("==========================================================================\n")

    print("[1] FLUGHAFEN-ANBINDUNG & TERMINAL-TRANSFERS:")
    for a in dest.airports:
        print(f"  * {a.airport_name} ({a.iata_code}) -> Distanz: {a.distance_to_terminal_km} km (~{a.typical_duration_min} min)")
        print(f"      Bester Transfer: {a.best_transit_mode}")
        print(f"      Geschätzte Kosten: {a.estimated_cost_range}")
        print(f"      ! VORSICHT      : {a.negative_intelligence}")
        print(f"      Quelle          : {a.evidence_source}\n")

    print("[2] OFFIZIELLES KREUZFAHRTTERMINAL & LIEGEPLÄTZE:")
    for t in dest.terminals:
        print(f"  * {t.terminal_name} ({t.distance_to_city_center_km} km zum Zentrum)")
        print(f"      Liegeplätze     : {', '.join(t.berths)}")
        print(f"      Porter Dropoff  : {t.porter_dropoff_location}")
        print(f"      Sicherheit      : {t.security_lane_notes}")
        print(f"      ÖPNV / Anbindung: {t.nearest_metro_or_train}")
        print(f"      ! MEIDEN        : {t.negative_intelligence}\n")

    print("[3] EMPFOHLENE HOTELZONEN (VORABEND):")
    for z in dest.recommended_hotel_zones:
        print(f"  * {z}")

    print("\n[4] TOP 3 LOKALE TOURISTENFALLEN & NEGATIVE INTELLIGENCE:")
    for i, n in enumerate(dest.negative_intelligence_top_3, 1):
        print(f"  {i}. {n}")

    print("==========================================================================")


if __name__ == "__main__":
    main()
