#!/usr/bin/env python3
"""
CLI Tool: Complete Travel Preparation Intelligence (Flight, Hotel, Status, Visa, Transfer).
Usage:
    python tools/travel_preparation_cli.py
"""

import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.flight_intelligence import (
    FlightIntelligenceEngine,
    FlightSegment,
    AirlineAlliance,
)
from src.timonelo.database.hotel_intelligence import (
    HotelIntelligenceEngine,
)
from src.timonelo.database.status_programs import (
    StatusProgramsEngine,
)
from src.timonelo.database.personal_intelligence import (
    TravelRulesEngine,
)


def main():
    print("==========================================================================")
    print("        TIMONELO COMPLETE TRAVEL PREPARATION DASHBOARD (SPRINT 07)        ")
    print("        'From Cruise Companion to Complete Journey Companion'             ")
    print("==========================================================================\n")

    # 1. Flight & Airport Intelligence
    segments = [
        FlightSegment("LH728", "FRA", "PVG", "17:15", "11:40 (+1)", "Lufthansa", AirlineAlliance.STAR_ALLIANCE)
    ]
    flt_eval = FlightIntelligenceEngine.evaluate_itinerary(segments, "2026-10-15", "Miles & More Senator")
    pvg_hub = FlightIntelligenceEngine.AIRPORT_REGISTRY["PVG"]

    print("[1] [FLUG] FLUG & FLUGHAFEN-INTELLIGENZ:")
    print(f"  * Flugverbindung: {segments[0].carrier_name} {segments[0].flight_number} ({segments[0].departure_airport_iata} -> {segments[0].arrival_airport_iata})")
    print(f"  * Ankunftszeit   : {segments[0].arrival_time_local} (Vortag vor Einschiffung)")
    print(f"  * Lounge-Zugang  : {flt_eval.lounge_eligibility_summary}")
    print(f"  * Zielflughafen  : {pvg_hub.airport_name} ({pvg_hub.iata_code})")
    print(f"  * Einreise (PVG) : ~{pvg_hub.immigration_duration_est_min} min | Maglev/Metro: {pvg_hub.public_transport_connection}")
    print(f"  * BOT-Urteil     : {flt_eval.bot_recommendation}")
    print(f"  ! MEIDEN         : {flt_eval.negative_intelligence}\n")

    # 2. Hotel Intelligence
    hotel = HotelIntelligenceEngine.get_hotel_by_id("hyatt-on-the-bund-shanghai")
    print("[2] [HOTEL] HOTEL-INTELLIGENZ (VORABEND):")
    if hotel:
        print(f"  * Hotel & Lage  : {hotel.property_name} ({hotel.city}) · {hotel.chain_loyalty_program}")
        print(f"  * Terminal-Dist : {hotel.distance_to_terminal_km} km (~{hotel.typical_transfer_duration_min} min Fahrzeit)")
        print(f"  * Abfahrt-Tipp  : {hotel.recommended_departure_time}")
        print(f"  * Late Check-out: {hotel.late_checkout_possibility} | Frühstück: ab {hotel.breakfast_start_time}")
        print(f"  * Umgebung      : {', '.join(hotel.nearby_conveniences[:2])}")
        print(f"  * BOT-Urteil    : {hotel.bot_evaluation_verdict}")
        print(f"  ! MEIDEN        : {hotel.negative_intelligence.encode('ascii', errors='replace').decode('ascii')}\n")

    # 3. Status Intelligence
    msc_stat = StatusProgramsEngine.evaluate_status("MSC Voyagers Club", "Diamond")
    hyatt_stat = StatusProgramsEngine.evaluate_status("World of Hyatt", "Globalist")
    print("[3] [STATUS] STATUS-PROGRAMME & FREIGESCHALTETE PERKS:")
    print(f"  * {msc_stat.program_name} ({msc_stat.tier_name}):")
    print(f"      - {msc_stat.key_unlocked_perks[0]}")
    print(f"      - {msc_stat.key_unlocked_perks[1]}")
    print(f"      - Check-out an Bord: {msc_stat.guaranteed_late_checkout}")
    print(f"  * {hyatt_stat.program_name} ({hyatt_stat.tier_name}):")
    print(f"      - {hyatt_stat.guaranteed_late_checkout}")
    print(f"      - {hyatt_stat.complimentary_breakfast}\n")

    # 4. Visa & Entry Requirements
    visa_rules = TravelRulesEngine.evaluate_rules("DE", ["China", "Japan"])
    print("[4] [VISA] EINREISE-VORAUSSETZUNGEN (VISA & DOKUMENTE):")
    for v in visa_rules:
        print(f"  * {v.destination_country}: {v.status.value}")
        print(f"      - Passgültigkeit: Mindestens {v.passport_validity_required_months} Monate gefordert")
        print(f"      - Details       : {v.details}")

    print("\n--------------------------------------------------------------------------")
    print("Bridge Officer Tim: 'Alles ist vorbereitet. Ich bleibe auf der Brücke.'")
    print("==========================================================================")


if __name__ == "__main__":
    main()
