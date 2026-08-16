#!/usr/bin/env python3
"""
CLI Tool: Complete First Voyage Simulation & Product Audit Engine (Sprint 11).
"Welcome home, Florian. I hope your voyage was everything you had hoped for."
Usage:
    python tools/first_voyage_cli.py
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.first_voyage_engine import (
    FirstVoyageEngine,
    JourneyStage,
    ProductAuditEngine,
)


def main():
    print("==========================================================================")
    print("       TIMONELO FIRST VOYAGE SIMULATION · DOORSTEP TO HOMECOMING          ")
    print("       Reisender: Florian · Schiff: MSC Bellissima · Kabine: 14122        ")
    print("==========================================================================\n")

    # 1. Journey Readiness Health Score
    readiness = FirstVoyageEngine.calculate_journey_readiness(flight_confirmed=False)
    print(f"[1] [JOURNEY READINESS SCORE] OPERATIVER HEALTH SCORE: {readiness.total_score}% ({readiness.status_label})")
    print("  [+] Verifizierte Meilensteine:")
    for v in readiness.verified_items:
        print(f"    [OK] {v}")
    print("  [!] Punktabzuege & offene Punkte:")
    for d in readiness.deductions:
        print(f"    [-{d.points_deducted}%] {d.item_name}: {d.reason}")
        print(f"         Empfohlene Handlung: {d.action_to_resolve}")
    print(f"\n  Bridge Officer Tim: \"{readiness.bot_verdict}\"\n")

    # 2. Stage Details (T-12 Preparation & Embarkation)
    prep_stage = FirstVoyageEngine.get_stage_detail(JourneyStage.PREPARATION)
    print(f"[2] [AKTUELLE REISEPHASE] {prep_stage.title.upper()} ({prep_stage.estimated_duration}):")
    print(f"  * Ziel        : {prep_stage.objective}")
    print(f"  * Morgen-Tipp : {prep_stage.bot_morning_briefing}")
    print(f"  * Anti-Regret : ! {prep_stage.anti_regret_warning}\n")

    # 3. Anti-Regret Register
    regrets = FirstVoyageEngine.get_anti_regret_register()
    print("[3] [ANTI-REGRET REGISTER] SYSTEMATISCHE REUE-VERMEIDUNG DER BRUECKE:")
    for r in regrets:
        print(f"  * [{r.stage_name}]")
        print(f"    Gefahr : {r.typical_regret_trap}")
        print(f"    Loesung: {r.prevention_rule}")
    print()

    # 4. Product Quality Audit
    audit = ProductAuditEngine.evaluate_experience()
    print(f"[4] [PRODUCT AUDIT REPORT] UX HEALTH SCORE: {audit.total_ux_score}% ({audit.clarity_verdict.split('(')[0].strip()}):")
    print(f"  * Unnoetige Klicks: {audit.unnecessary_clicks_count} | Unnoetige Fragen: {audit.unnecessary_questions_asked}")
    print(f"  * Proaktives Timing: {audit.proactive_timing_score}%")
    print(f"  * Fazit: {audit.audit_summary}\n")

    print("--------------------------------------------------------------------------")
    print("Bridge Officer Tim: \"Welcome home, Florian. I hope your voyage was everything you had hoped for. Whenever you're ready for your next adventure, I'll be here on the bridge.\"")
    print("==========================================================================")


if __name__ == "__main__":
    main()
