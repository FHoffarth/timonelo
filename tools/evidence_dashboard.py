#!/usr/bin/env python3
"""
CLI Tool: Evidence Provenance, Trust Score, and Discrepancy Conflict Dashboard.
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler
from src.timonelo.database.evidence_dashboard import EvidenceDashboard


def main():
    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    dashboard = EvidenceDashboard(db)
    report = dashboard.generate_evidence_report()

    print("=========================================================")
    print("      TIMONELO MARITIME EVIDENCE & TRUST DASHBOARD       ")
    print("=========================================================")
    stats = report["statistics"]
    print(f"Total Atomic Facts Audited:    {stats['total_facts_audited']}")
    print(f"Official Records (IMO/Yard):   {stats['official_facts_pct']}%")
    print(f"Field & Crew Verified:         {stats['field_and_crew_verified_pct']}%")
    print(f"Community Confirmed:           {stats['community_pct']}%")
    print(f"Unknown (Explicit Omission):   {stats['unknown_pct']}%")
    print(f"Active Discrepancy Conflicts:  {stats['total_conflicts_detected']}")
    print("---------------------------------------------------------")
    print("Top Most Trusted Digital Twins:")
    for s in report["most_trusted_ships"]:
        print(f"  * {s['name']:<24}: Trust Score {s['score']:.1f}% ({s['facts']} facts, {s['conflicts']} conflicts)")
    print("---------------------------------------------------------")
    print("Active Evidence Conflicts & Discrepancy Queue:")
    for c in report["conflicts_report"]:
        print(f"  [CONFLICT] {c['entity']} -> {c['field']}")
        print(f"      Primary   : {c['primary']}")
        print(f"      Competing : {c['competing']}")
        print(f"      Status    : {c['status']}")
        print(f"      Rationale : {c['notes']}")
    print("=========================================================")


if __name__ == "__main__":
    main()
