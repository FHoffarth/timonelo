#!/usr/bin/env python3
"""
CLI Tool: Ship Intelligence Levels & Digital Twin Depth Dashboard.
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler
from src.timonelo.database.depth_dashboard import ShipDepthDashboard


def main():
    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    dashboard = ShipDepthDashboard(db)
    report = dashboard.generate_depth_report()

    print("=========================================================")
    print("      TIMONELO VESSEL INTELLIGENCE & DEPTH DASHBOARD     ")
    print("=========================================================")
    print("Fleet Intelligence Level Distribution:")
    for lvl_name, count in report["level_distribution"].items():
        bar = "#" * min(count, 30)
        print(f"  * {lvl_name:<38}: {count:>3} ships {bar}")
    print("---------------------------------------------------------")
    print("Premium Reference Digital Twins:")
    for v in report["reference_vessels"]:
        print(f"  [{v['stars']}] {v['name']:<22} [Level {v['level']}] -> {v['status']}")
        if "cabins_count" in v:
            print(f"      Staterooms: {v['cabins_count']} | Venues: {v['venues_count']} | Negative Intel: {v['negative_intel_count']} | Ops: {v['operations_indexed']}")
    print("---------------------------------------------------------")
    print("Evidence & Provenance Integrity:")
    ev = report["evidence_statistics"]
    print(f"  * Official Authority & Yard Records : {ev['official_records_pct']}%")
    print(f"  * Field-Audited Spatial Dimensions   : {ev['field_audited_records_pct']}%")
    print(f"  * Crew-Corroborated Observations     : {ev['crew_verified_records_pct']}%")
    print(f"  * Hallucination Suppression Score    : {ev['unknown_suppression_score']}")
    print("=========================================================")


if __name__ == "__main__":
    main()
