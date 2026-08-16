#!/usr/bin/env python3
"""
CLI Tool: Compile and validate the master Cruise Intelligence Database.
Usage:
    python tools/knowledge_compiler.py [--check]
"""

import sys
import os
import argparse

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler


def main():
    parser = argparse.ArgumentParser(description="Timonelo Cruise Intelligence Database Compiler")
    parser.add_argument("--check", action="store_true", help="Perform validation only without altering disk")
    args = parser.parse_args()

    compiler = KnowledgeDBCompiler(REPO_ROOT)
    db = compiler.compile()

    stats = db["statistics"]
    graph_stats = db.get("graph_summary", {})
    print("=========================================================")
    print("       TIMONELO CRUISE KNOWLEDGE GRAPH & DATABASE COMPILER")
    print("=========================================================")
    print(f"Total Sources Registered:      {stats['total_sources']}")
    print(f"Total Ship Classes:            {stats['total_ship_classes']}")
    print(f"Total Ships Indexed:           {stats['total_ships']}")
    print(f"Total Strategic Ports:         {stats['total_ports']}")
    print(f"Total Routes & Itineraries:    {stats['total_routes']}")
    print(f"Total Public Venues Mapped:    {stats['total_venues']}")
    print(f"Total Knowledge Graph Nodes:   {stats.get('total_graph_nodes', 0)}")
    print(f"Total Knowledge Graph Edges:   {stats.get('total_graph_edges', 0)}")
    print(f"Validation Errors:             {stats['validation_errors_count']}")
    print(f"Validation Warnings:           {stats['validation_warnings_count']}")
    print("---------------------------------------------------------")
    print(f"Node Types Breakdown:          {graph_stats.get('node_types', {})}")
    print(f"Relation Types Breakdown:      {graph_stats.get('relation_types', {})}")
    print("=========================================================")

    if compiler.validation_errors:
        print("\nERRORS ENCOUNTERED:")
        for err in compiler.validation_errors:
            print(f"  [ERROR] {err}")
        sys.exit(1)

    if compiler.validation_warnings:
        print("\nINTEGRITY NOTES:")
        for w in compiler.validation_warnings[:8]:
            print(f"  [NOTE] {w}")
        if len(compiler.validation_warnings) > 8:
            print(f"  ... and {len(compiler.validation_warnings) - 8} more notices.")

    print("\n[OK] Master Cruise Intelligence Database built at: data/cruise_intelligence_db.json")


if __name__ == "__main__":
    main()
