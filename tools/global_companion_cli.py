#!/usr/bin/env python3
"""
CLI Tool: Global Companion & Regret Score Engine.
"Timonelo doesn't help you travel more. It helps you regret less."
Usage:
    python tools/global_companion_cli.py
"""

import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.global_companion import (
    GlobalCompanionEngine,
    RegretScoreEngine,
    TravelMemory,
)


def main():
    memory = GlobalCompanionEngine.get_reference_memory_flo()
    phases = GlobalCompanionEngine.generate_8_phase_journey(memory)

    print("==========================================================================")
    print("           TIMONELO GLOBAL COMPANION & REGRET SCORE ENGINE                ")
    print("           'Timonelo doesn't help you travel more. It helps you regret less.'")
    print(f"           Reisender: {memory.preferred_name} | MSC Status: {memory.msc_loyalty_tier} | Airline: {memory.airline_tier}")
    print("==========================================================================\n")

    # 1. Travel Memory Profile
    print("[1] TRAVEL MEMORY (PERSÖNLICHE ERFAHRUNGSPROFILIERUNG):")
    print(f"  * Reisestil : {memory.travel_style}")
    print(f"  * Vorlieben : {', '.join(memory.likes[:4])}")
    print(f"  * Abneigungen: {', '.join(memory.dislikes[:3])}")
    print(f"  * Kulinarik : {memory.culinary_preference}")
    print("--------------------------------------------------------------------------\n")

    # 2. Regret Score Simulator
    print("[2] TIMONELO REGRET SCORE SIMULATOR:")
    eval_high = RegretScoreEngine.evaluate_flight_arrival_timing(
        arrival_date_same_day=True,
        arrival_time_str="09:50 Uhr (04.10.)",
        departure_time_str="17:00 Uhr (04.10.)",
        city_name="Shanghai",
    )
    print(f"  [SZENARIO A] {eval_high.scenario_title}")
    print(f"    Urteil        : [HIGH RISK] REGRET RISK: {eval_high.level.value} (Score: {eval_high.regret_score_pct}%)")
    print("    Warum Reue?   :")
    for w in eval_high.why_you_will_regret_this[:3]:
        print(f"      ! {w}")
    print(f"    Reue vermeiden: {eval_high.how_to_avoid_regret}\n")

    eval_low = RegretScoreEngine.evaluate_flight_arrival_timing(
        arrival_date_same_day=False,
        arrival_time_str="Vortag (03.10.)",
        departure_time_str="17:00 Uhr (04.10.)",
        city_name="Shanghai",
    )
    print(f"  [SZENARIO B] {eval_low.scenario_title}")
    print(f"    Urteil        : [LOW RISK] REGRET RISK: {eval_low.level.value} (Score: {eval_low.regret_score_pct}%)")
    print(f"    Reue vermeiden: {eval_low.how_to_avoid_regret}")
    print("--------------------------------------------------------------------------\n")

    # 3. The 8 Global Companion Phases
    print("[3] DIE 8 GLOBALEN REISEPHASEN (VOM VERLASSEN DER HAUSTÜR BIS ZUR HEIMKEHR):")
    for p in phases:
        print(f"  --- {p.phase.value}: {p.headline.upper()} ---")
        print(f"      Ziel     : {p.objective_now}")
        print(f"      Schritte : {p.what_to_do_now[0]}")
        print(f"      ! MEIDEN : {p.negative_intelligence_to_avoid}")
        print(f"      Memory   : {p.travel_memory_adaptations[0]}")
        print(f"      Quellen  : {', '.join(p.evidence_sources)}\n")

    print("==========================================================================")


if __name__ == "__main__":
    main()
