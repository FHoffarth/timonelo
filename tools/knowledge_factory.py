#!/usr/bin/env python3
"""
CLI Tool: Timonelo Knowledge Factory Ingestion & Staging Engine.
Usage:
    python tools/knowledge_factory.py [--run-sample] [--status] [--approve <item_id>]
"""

import sys
import os
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.ingestion.pipeline import KnowledgeFactoryPipeline
from src.timonelo.ingestion.importers import OfficialCruiseLineImporter, MaritimeIMOImporter


def main():
    parser = argparse.ArgumentParser(description="Timonelo Cruise Knowledge Factory Ingestion Engine")
    parser.add_argument("--run-sample", action="store_true", help="Execute sample multi-operator ingestion test")
    parser.add_argument("--status", action="store_true", help="Display Review Queue status and staging statistics")
    parser.add_argument("--approve", type=str, help="Approve staged candidate by item ID")
    args = parser.parse_args()

    pipeline = KnowledgeFactoryPipeline(REPO_ROOT)

    if args.approve:
        success = pipeline.review_queue.approve_item(args.approve)
        if success:
            print(f"[OK] Staged item '{args.approve}' APPROVED for production.")
        else:
            print(f"[ERROR] Failed to approve item '{args.approve}' (check ID or validation status).")
        return

    if args.run_sample or not (args.status or args.approve):
        print("=========================================================")
        print("         TIMONELO CRUISE KNOWLEDGE FACTORY INGESTION     ")
        print("=========================================================")

        # Sample Candidate 1: Norwegian Prima (Prima Class)
        importer_ncl = OfficialCruiseLineImporter("src:ncl-corporate", "Norwegian Cruise Line")
        raw_prima = {
            "slug": "norwegian-prima",
            "name": "Norwegian Prima",
            "imo": "9823986",
            "mmsi": "311001149",
            "call_sign": "C6FM8",
            "flag_state": "Bahamas",
            "operator": "Norwegian Cruise Line",
            "ship_class": "Prima Class",
            "gross_tonnage": 143535,
            "length_m": 293.4,
            "beam_m": 40.5,
            "draft_m": 8.5,
            "passenger_capacity": 3100,
            "crew": 1506,
            "cabin_count": 1550,
            "builder": "Fincantieri (Marghera, Italy)",
            "build_year": 2022,
            "signature_venues": ["Ocean Boulevard", "Prima Speedway", "Indulge Food Hall"],
            "homeports": ["miami", "barcelona", "civitavecchia"],
        }
        res_prima = pipeline.ingest_ship_candidate(
            importer=importer_ncl,
            raw_data=raw_prima,
            source_url="https://www.ncl.com/cruise-ships/prima",
            confidence=1.0,
        )

        # Sample Candidate 2: Sun Princess (Sphere Class)
        importer_princess = OfficialCruiseLineImporter("src:princess-corporate", "Princess Cruises")
        raw_sun = {
            "slug": "sun-princess",
            "name": "Sun Princess",
            "imo": "9863118",
            "mmsi": "310839000",
            "call_sign": "ZCEV2",
            "flag_state": "Bermuda",
            "operator": "Princess Cruises",
            "ship_class": "Sphere Class",
            "gross_tonnage": 177882,
            "length_m": 345.3,
            "beam_m": 42.0,
            "draft_m": 8.9,
            "passenger_capacity": 4300,
            "crew": 1600,
            "cabin_count": 2157,
            "builder": "Fincantieri (Monfalcone, Italy)",
            "build_year": 2024,
            "signature_venues": ["The Dome (Geodesic Glass Structure)", "The Sphere Atrium", "Park19"],
            "homeports": ["fort-lauderdale", "barcelona", "civitavecchia"],
        }
        res_sun = pipeline.ingest_ship_candidate(
            importer=importer_princess,
            raw_data=raw_sun,
            source_url="https://www.princess.com/ships-and-experience/ships/su-sun-princess",
            confidence=1.0,
        )

        print(f"Candidate Ingested: {res_prima['normalized_entity']['name']['value']} -> Status: {res_prima['status']} (Diff: {res_prima['diff_type']})")
        print(f"Candidate Ingested: {res_sun['normalized_entity']['name']['value']} -> Status: {res_sun['status']} (Diff: {res_sun['diff_type']})")
        print("---------------------------------------------------------")

    stats = pipeline.review_queue.get_statistics()
    print(f"Review Queue Statistics: {stats}")
    print("=========================================================")


if __name__ == "__main__":
    main()
