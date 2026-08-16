#!/usr/bin/env python3
"""
CLI Tool: Source Network Quality, Freshness, and Provenance Dependency Dashboard.
Usage:
    python tools/sources_dashboard.py
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler
from src.timonelo.database.sources_dashboard import SourcesDashboard


def main():
    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    dashboard = SourcesDashboard(db)
    report = dashboard.generate_sources_report()

    print("==========================================================================")
    print("           TIMONELO SOURCE NETWORK & PROVENANCE DASHBOARD                 ")
    print("==========================================================================")
    print(f"Total Suppliers in Source Network : {report['total_sources_indexed']} authoritative sources")
    print(f"Average Network Trust Rating      : {report['average_network_trust_pct']}%")
    print("--------------------------------------------------------------------------")

    print("Source Category Breakdown:")
    for cat, count in report["category_distribution"].items():
        print(f"  * {cat:<28}: {count:>2} suppliers")

    print("\nAccess Methodology Breakdown:")
    for method, count in report["access_method_distribution"].items():
        print(f"  * {method:<28}: {count:>2} feeds")

    print("\nProvenance Freshness Matrix:")
    for bucket, count in report["freshness_distribution"].items():
        print(f"  * {bucket:<28}: {count:>2} sources")

    print("--------------------------------------------------------------------------")
    print("Source Dependency Chain (Example: MSC Bellissima):")
    for dep in report["canonical_dependency_chain"]:
        print(f"  [{dep['trust']}] {dep['tier']:<24} -> {dep['name']}")
        print(f"        Node: {dep['source']}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
