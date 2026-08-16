#!/usr/bin/env python3
"""
CLI Tool: Personal Travel Intelligence & Decision Briefing.
Usage:
    python tools/personal_travel_briefing.py [--nationality DE | US] [--cruise msc-bellissima]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.personal_intelligence import (
    PersonalIntelligenceEngine,
    TravellerProfile,
    TravelPartyType,
    MobilityLevel,
)


def main():
    parser = argparse.ArgumentParser(description="Personal Travel Intelligence Briefing CLI")
    parser.add_argument("--nationality", type=str, default="DE", help="Traveler nationality (e.g. DE, US)")
    parser.add_argument("--cruise", type=str, default="msc-bellissima", help="Ship slug")
    parser.add_argument("--airline-loyalty", type=str, default="Miles & More Senator", help="Airline loyalty tier")
    parser.add_argument("--cruise-loyalty", type=str, default="MSC Voyagers Club Gold", help="Cruise line loyalty tier")
    parser.add_argument("--hotel-loyalty", type=str, default="Hilton Diamond", help="Hotel loyalty tier")
    parser.add_argument("--party", type=str, default="COUPLE", choices=[p.value for p in TravelPartyType])
    args = parser.parse_args()

    profile = TravellerProfile(
        traveller_id="Max Mustermann",
        nationality=args.nationality,
        residence_country="Germany" if args.nationality == "DE" else "United States",
        preferred_home_airport="FRA" if args.nationality == "DE" else "JFK",
        airline_loyalty=args.airline_loyalty,
        hotel_loyalty=args.hotel_loyalty,
        cruise_loyalty=args.cruise_loyalty,
        travel_party=TravelPartyType(args.party),
        mobility=MobilityLevel.STANDARD,
    )

    briefing = PersonalIntelligenceEngine.generate_briefing(
        profile=profile,
        ship_slug=args.cruise,
        ship_name="MSC Bellissima",
        route_name="Shanghai nach Tokio (Transasien)",
        destination_countries=["China", "Japan"],
    )

    print("==========================================================================")
    print("           TIMONELO PERSONAL TRAVEL INTELLIGENCE BRIEFING                 ")
    print(f"           Reisender: {briefing.traveller_name} ({briefing.nationality}) | Schiff: {briefing.cruise_ship}")
    print(f"           Route    : {briefing.cruise_route}")
    print("==========================================================================\n")

    print("[1] DOKUMENTE & EINREISE-BESTIMMUNGEN:")
    for v in briefing.visa_and_documents_status:
        print(f"  * {v.destination_country.upper()}: {v.status.value}")
        print(f"      Passgltigkeit: Mindestens {v.passport_validity_required_months} Monate gefordert")
        print(f"      Regelung       : {v.details}")
        print(f"      Quelle         : {v.evidence_source} (Konfidenz: {v.confidence}%)\n")

    print("[2] LOYALITT & STATUS-VORTEILE:")
    for l in briefing.loyalty_programs:
        print(f"  * {l.program_name} (Status: {l.current_tier})")
        for b in l.unlocked_benefits_on_trip:
            print(f"      [Vorteil] {b}")
        print(f"      Fortschritt: {l.potential_tier_progress}\n")

    print("[3] WICHTIGSTE PERSNLICHE SCHRITTE:")
    for i, a in enumerate(briefing.important_actions, 1):
        print(f"  {i}. {a}")

    print("\n[4] PERSNLICHE RISIKEN & NEGATIVE INTELLIGENCE:")
    for i, r in enumerate(briefing.potential_risks, 1):
        print(f"  ! {r}")

    print("\n[5] STATUS-CHANCEN & OPPORTUNITIES:")
    for i, o in enumerate(briefing.status_opportunities, 1):
        print(f"  + {o}")

    print(f"\nGesamt-Konfidenz: {briefing.confidence_overall} | Quellen: {', '.join(briefing.evidence_sources)}")
    print(f"Briefing-ID     : {briefing.briefing_id} (100% Deterministisch)")
    print("==========================================================================")


if __name__ == "__main__":
    main()
