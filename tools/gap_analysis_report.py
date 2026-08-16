#!/usr/bin/env python3
"""
CLI Tool: Generate Knowledge Coverage Dashboard and Gap Analysis Report.
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler
from src.timonelo.database.gap_analyzer import KnowledgeGapAnalyzer


def main():
    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    analyzer = KnowledgeGapAnalyzer(db)
    report = analyzer.generate_coverage_report()

    print("=========================================================")
    print("      TIMONELO CRUISE INTELLIGENCE COVERAGE DASHBOARD    ")
    print("=========================================================")
    stats = report["statistics"]
    print(f"Total Ships Indexed:           {stats['total_ships']}")
    print(f"Total Strategic Ports:         {stats['total_ports']}")
    print(f"Total Ship Classes:            {stats['total_ship_classes']}")
    print(f"Total Canonical Routes:        {stats['total_routes']}")
    print(f"Total Public Venues Mapped:    {stats['total_venues']}")
    print(f"Total Knowledge Graph Nodes:   {db['statistics']['total_graph_nodes']}")
    print(f"Total Knowledge Graph Edges:   {db['statistics']['total_graph_edges']}")
    print(f"Knowledge Completeness:        {stats['completeness_score_pct']}%")
    print(f"Validation Score:              {stats['validation_score']}")
    print("---------------------------------------------------------")
    print("Top Operators by Fleet Size:")
    for op, count in list(report["ships_by_operator"].items())[:6]:
        print(f"  • {op:<30}: {count} ships")
    print("---------------------------------------------------------")
    print("Strategic Ports by Region:")
    for reg, count in list(report["ports_by_region"].items())[:6]:
        print(f"  • {reg:<30}: {count} ports")
    print("---------------------------------------------------------")
    print(f"Total Knowledge Gaps Detected: {report['total_detected_gaps']}")
    print("Sample Priority Gaps:")
    for g in report["knowledge_gaps_sample"][:5]:
        print(f"  [GAP] {g['entity']} -> {g['type']}")
    print("=========================================================")


if __name__ == "__main__":
    main()
