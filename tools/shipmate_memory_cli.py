#!/usr/bin/env python3
"""
CLI Tool: Shipmate Memory & Bridge Logbook (Chapter V - Sprint 01).
"Bridge Officer Tim Remembers Every Voyage."
"Voyage completed successfully. Thank you for allowing me to accompany you. I have entered this journey into the ship's log, and I look forward to welcoming you aboard again."
Usage:
    python tools/shipmate_memory_cli.py [--traveller Florian]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.shipmate_memory import (
    BridgeMemoryEngine,
)


def main():
    parser = argparse.ArgumentParser(description="Shipmate Memory & Bridge Logbook CLI")
    parser.add_argument("--traveller", type=str, default="Florian", help="Traveller name")
    args = parser.parse_args()

    prof = BridgeMemoryEngine.get_shipmate_profile(args.traveller)

    print("==========================================================================")
    print(f"       TIMONELO SHIPMATE MEMORY · CAPTAIN'S LOG & REISE-GEDAECHTNIS       ")
    print(f"       Reisender: {prof.traveller_name} · Seetage: {prof.total_sea_days} · Reisen: {prof.total_voyages_count}")
    print("==========================================================================\n")

    # 1. BOT Welcome Back
    print(f"Bridge Officer Tim: \"{prof.bot_welcome_back_greeting}\"\n")

    # 2. Visited Statistics
    print("[1] [LOGBUCH-STATISTIK DER BRUECKE]:")
    print(f"  * Schiffe     : {', '.join(prof.visited_ships)}")
    print(f"  * Haefen      : {', '.join(prof.visited_ports)}")
    print(f"  * Laender     : {', '.join(prof.visited_countries)}\n")

    # 3. Favourite Places
    print("[2] [BEVORZUGTE ORTE AN BORD]:")
    for f in prof.favourite_places:
        print(f"  * {f.name} ({f.ship_name} · {f.deck_location})")
        print(f"    Kategorie  : {f.category}")
        print(f"    Begruendung: {f.why_favoured}")
    print()

    # 4. Confirmed Travel Habits
    print("[3] [BEOBACHTETE REISEGEWOHNHEITEN]:")
    for h in prof.confirmed_habits:
        print(f"  * [{h.category.value.split('(')[0].strip()}] {h.observation}")
        print(f"    Evidenz: {h.evidence_voyage}")
    print()

    # 5. Bridge Journal Entries
    print("[4] [CHRONOLOGISCHES BRUECKEN-JOURNAL (EIN SATZ PRO TAG)]:")
    for voy in prof.voyage_history:
        print(f"  --- {voy.ship_name} ({voy.departure_date} · {voy.itinerary_summary}) ---")
        for j in voy.journal_entries:
            print(f"    [{j.date_str}] ({j.voyage_day_label} @ {j.port_or_sea_location}):")
            print(f"      \"{j.factual_milestone_sentence}\"")
        print()

    # 6. Proactive Memory Insights
    insights = BridgeMemoryEngine.generate_proactive_memory_insights(prof.traveller_name)
    print("[5] [PROAKTIVE ERINNERUNGEN FUER DIE NAECHSTE REISE]:")
    for ins in insights:
        print(f"  » {ins}")
    print()

    print("--------------------------------------------------------------------------")
    print(f"Bridge Officer Tim: \"{prof.bot_closing_log_note}\"")
    print("==========================================================================")


if __name__ == "__main__":
    main()
