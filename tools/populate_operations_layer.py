#!/usr/bin/env python3
"""
Populates the Operational Data Layer: Deployments, Voyages, Schedules, Fleet Status, and Weather Contexts.
"""

from __future__ import annotations
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(REPO_ROOT, "knowledge")

# 1. SEASONAL DEPLOYMENTS
DEPLOYMENTS = [
    {
        "deployment_id": "dep:bellissima:summer-2026",
        "ship_slug": "msc-bellissima",
        "season": "SUMMER_2026",
        "region_slug": "western-mediterranean",
        "homeports": ["genoa", "barcelona", "naples", "marseille"],
        "primary_routes": ["western-mediterranean-7n"],
        "start_date": "2026-04-15",
        "end_date": "2026-10-31",
        "notes": "7-night circular Western Mediterranean deployment with multi-port embarkation.",
        "source_id": "src:official-msc-deployments-2026",
    },
    {
        "deployment_id": "dep:bellissima:winter-2026",
        "ship_slug": "msc-bellissima",
        "season": "WINTER_2026_27",
        "region_slug": "east-asia-japan",
        "homeports": ["yokohama", "tokyo", "keelung"],
        "primary_routes": ["japan-taiwan-roundtrip-9n"],
        "start_date": "2026-11-15",
        "end_date": "2027-03-30",
        "notes": "Japan & Taiwan winter season deployment.",
        "source_id": "src:official-msc-deployments-2026",
    },
    {
        "deployment_id": "dep:euribia:summer-2026",
        "ship_slug": "msc-euribia",
        "season": "SUMMER_2026",
        "region_slug": "norwegian-fjords",
        "homeports": ["kiel", "copenhagen"],
        "primary_routes": ["norwegian-fjords-7n"],
        "start_date": "2026-05-01",
        "end_date": "2026-09-30",
        "notes": "7-night roundtrip Norwegian Fjords calling at Hellesylt, Geiranger, Flaam.",
        "source_id": "src:official-msc-deployments-2026",
    },
    {
        "deployment_id": "dep:andorinha:summer-2026",
        "ship_slug": "ms-andorinha",
        "season": "SUMMER_2026",
        "region_slug": "douro-river-valley",
        "homeports": ["porto-leixoes"],
        "primary_routes": ["douro-valley-wine-7n"],
        "start_date": "2026-04-01",
        "end_date": "2026-10-25",
        "notes": "Exclusive 7-night Douro river yacht journeys from Porto to Vega de Terron.",
        "source_id": "src:tauck-river-operations-2026",
    },
]

# 2. VOYAGES
VOYAGES = [
    {
        "voyage_id": "voyage:bellissima:2026-10-04",
        "ship_slug": "msc-bellissima",
        "cruise_number": "BL20261004GEN",
        "route_slug": "western-mediterranean-7n",
        "start_date": "2026-10-04",
        "end_date": "2026-10-11",
        "embarkation_port": "genoa",
        "disembarkation_port": "genoa",
        "sea_days_count": 1,
        "nautical_miles": 1380.0,
        "weather_zone": "Western Mediterranean Warm Temperate",
        "status": "SCHEDULED",
        "port_calls": [
            {"call_id": "call:bl:genoa:01", "port_slug": "genoa", "terminal_name": "Ponte dei Mille (Genoa Cruise Terminal)", "arrival_iso": "2026-10-04T08:00:00+02:00", "departure_iso": "2026-10-04T18:00:00+02:00", "gangway_deck": 5, "is_turnaround": True, "is_tender": False},
            {"call_id": "call:bl:naples:02", "port_slug": "naples", "terminal_name": "Stazione Marittima di Napoli Pier 21", "arrival_iso": "2026-10-05T13:00:00+02:00", "departure_iso": "2026-10-05T20:00:00+02:00", "gangway_deck": 5, "is_turnaround": True, "is_tender": False},
            {"call_id": "call:bl:messina:03", "port_slug": "messina", "terminal_name": "Banchina Colapesce", "arrival_iso": "2026-10-06T09:00:00+02:00", "departure_iso": "2026-10-06T19:00:00+02:00", "gangway_deck": 5, "is_turnaround": False, "is_tender": False},
            {"call_id": "call:bl:valletta:04", "port_slug": "valletta", "terminal_name": "Valletta Waterfront Pinto Wharf", "arrival_iso": "2026-10-07T08:00:00+02:00", "departure_iso": "2026-10-07T17:00:00+02:00", "gangway_deck": 4, "is_turnaround": False, "is_tender": False},
            {"call_id": "call:bl:seaday:05", "port_slug": "sea-day", "terminal_name": "At Sea (Western Mediterranean Transit)", "arrival_iso": "2026-10-08T00:00:00+02:00", "departure_iso": "2026-10-08T23:59:00+02:00", "gangway_deck": 0, "is_turnaround": False, "is_tender": False},
            {"call_id": "call:bl:barcelona:06", "port_slug": "barcelona", "terminal_name": "Moll Adossat Terminal B", "arrival_iso": "2026-10-09T09:00:00+02:00", "departure_iso": "2026-10-09T18:00:00+02:00", "gangway_deck": 5, "is_turnaround": True, "is_tender": False},
            {"call_id": "call:bl:marseille:07", "port_slug": "marseille", "terminal_name": "Marseille Provence Cruise Center (MPCC) Mole Leon Gourret", "arrival_iso": "2026-10-10T09:00:00+02:00", "departure_iso": "2026-10-10T18:00:00+02:00", "gangway_deck": 5, "is_turnaround": True, "is_tender": False},
            {"call_id": "call:bl:genoa:08", "port_slug": "genoa", "terminal_name": "Ponte dei Mille", "arrival_iso": "2026-10-11T08:00:00+02:00", "departure_iso": "2026-10-11T18:00:00+02:00", "gangway_deck": 5, "is_turnaround": True, "is_tender": False},
        ],
    }
]

# 3. LIVE FLEET STATUS
FLEET_STATUS = [
    {
        "ship_slug": "msc-bellissima",
        "current_season": "SUMMER_2026",
        "deployment_region": "western-mediterranean",
        "current_voyage_id": "voyage:bellissima:2026-10-04",
        "operational_state": "DOCKED",
        "current_port_slug": "genoa",
        "next_port_slug": "naples",
        "eta_next_port": "2026-10-05T13:00:00+02:00",
        "etd_current_port": "2026-10-04T18:00:00+02:00",
        "speed_knots": 0.0,
        "course_deg": 0.0,
        "position_lat_lon": [44.4142, 8.9211],
        "local_time_zone": "Europe/Rome (CEST, UTC+2)",
        "last_observed_at": "2026-08-16T12:00:00Z",
        "source_feed": "src:official-cruise-line-schedule",
        "freshness_seconds": 300,
    },
    {
        "ship_slug": "msc-meraviglia",
        "current_season": "SUMMER_2026",
        "deployment_region": "caribbean-bahamas",
        "current_voyage_id": "voyage:meraviglia:2026-summer-bahamas",
        "operational_state": "DOCKED",
        "current_port_slug": "new-york",
        "next_port_slug": "port-canaveral",
        "eta_next_port": "2026-08-18T13:00:00-04:00",
        "etd_current_port": "2026-08-16T17:00:00-04:00",
        "speed_knots": 0.0,
        "course_deg": 0.0,
        "position_lat_lon": [40.6782, -74.0150],
        "local_time_zone": "America/New_York (EDT, UTC-4)",
        "last_observed_at": "2026-08-16T12:00:00Z",
        "source_feed": "src:official-cruise-line-schedule",
        "freshness_seconds": 300,
    },
]


def populate_operations():
    # 1. Deployments
    dep_dir = os.path.join(KNOWLEDGE_DIR, "deployments")
    os.makedirs(dep_dir, exist_ok=True)
    for d in DEPLOYMENTS:
        path = os.path.join(dep_dir, f"{d['deployment_id'].replace(':', '_')}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(f" [OK] Populated {len(DEPLOYMENTS)} Seasonal Deployments in knowledge/deployments/")

    # 2. Voyages
    voy_dir = os.path.join(KNOWLEDGE_DIR, "voyages")
    os.makedirs(voy_dir, exist_ok=True)
    for v in VOYAGES:
        path = os.path.join(voy_dir, f"{v['voyage_id'].replace(':', '_')}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(f" [OK] Populated {len(VOYAGES)} Structured Voyages in knowledge/voyages/")

    # 3. Fleet Status
    status_dir = os.path.join(KNOWLEDGE_DIR, "fleet-status")
    os.makedirs(status_dir, exist_ok=True)
    for fs in FLEET_STATUS:
        path = os.path.join(status_dir, f"{fs['ship_slug']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fs, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(f" [OK] Populated {len(FLEET_STATUS)} Live Fleet Status entities in knowledge/fleet-status/")


if __name__ == "__main__":
    populate_operations()
