#!/usr/bin/env python3
"""
Populate Global Canonical Routes and Signature Venues.
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(REPO_ROOT, "knowledge")
ROUTES_DIR = os.path.join(KNOWLEDGE_DIR, "routes")
VENUES_DIR = os.path.join(KNOWLEDGE_DIR, "venues")

ROUTES_DATA = [
    {
        "slug": "western-mediterranean-7n",
        "title": "7-Night Classic Western Mediterranean",
        "region": "Western Mediterranean",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "genoa", "port_name": "Genoa", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "civitavecchia", "port_name": "Civitavecchia (Rome)", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "palermo", "port_name": "Palermo", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "ibiza", "port_name": "Ibiza", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "valencia", "port_name": "Valencia", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "marseille", "port_name": "Marseille", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "genoa", "port_name": "Genoa", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["MSC Cruises", "Costa Cruises", "AIDA Cruises", "Royal Caribbean"],
    },
    {
        "slug": "eastern-mediterranean-7n",
        "title": "7-Night Greek Isles & Aegean Odyssey",
        "region": "Eastern Mediterranean",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "piraeus", "port_name": "Piraeus (Athens)", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "santorini", "port_name": "Santorini", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "kusadasi", "port_name": "Kusadasi (Ephesus)", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "mykonos", "port_name": "Mykonos", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "rhodes", "port_name": "Rhodes", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "heraklion", "port_name": "Heraklion (Crete)", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "piraeus", "port_name": "Piraeus (Athens)", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Celebrity Cruises", "Norwegian Cruise Line", "Virgin Voyages", "MSC Cruises"],
    },
    {
        "slug": "norwegian-fjords-7n",
        "title": "7-Night Majestic Norwegian Fjords",
        "region": "Norwegian Fjords",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "southampton", "port_name": "Southampton", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "stavanger", "port_name": "Stavanger", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "flam", "port_name": "Flåm", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "geiranger", "port_name": "Geiranger", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "alesund", "port_name": "Ålesund", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "bergen", "port_name": "Bergen", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "southampton", "port_name": "Southampton", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["P&O Cruises", "Princess Cruises", "Celebrity Cruises", "AIDA Cruises"],
    },
    {
        "slug": "baltic-capitals-7n",
        "title": "7-Night Baltic Capitals & Scandinavia",
        "region": "Baltic Sea",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "copenhagen", "port_name": "Copenhagen", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "warnemunde-rostock", "port_name": "Warnemünde", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "tallinn", "port_name": "Tallinn", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "helsinki", "port_name": "Helsinki", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "stockholm", "port_name": "Stockholm", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "riga", "port_name": "Riga", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "copenhagen", "port_name": "Copenhagen", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["TUI Cruises", "AIDA Cruises", "MSC Cruises", "Viking Ocean"],
    },
    {
        "slug": "eastern-caribbean-7n",
        "title": "7-Night Perfect Eastern Caribbean",
        "region": "Eastern Caribbean",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "miami", "port_name": "Miami", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "nassau", "port_name": "Nassau", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "san-juan", "port_name": "San Juan", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "st-thomas", "port_name": "St. Thomas", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "st-maarten", "port_name": "St. Maarten", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "fort-lauderdale", "port_name": "Fort Lauderdale", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "miami", "port_name": "Miami", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Royal Caribbean", "Celebrity Cruises", "Disney Cruise Line", "MSC Cruises"],
    },
    {
        "slug": "western-caribbean-7n",
        "title": "7-Night Maya Riviera & Western Caribbean",
        "region": "Western Caribbean",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "port-canaveral", "port_name": "Port Canaveral", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "cozumel", "port_name": "Cozumel", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "costa-maya", "port_name": "Costa Maya", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "roatan", "port_name": "Roatan", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "grand-cayman", "port_name": "Grand Cayman", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "tampa", "port_name": "Tampa", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "port-canaveral", "port_name": "Port Canaveral", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Carnival Cruise Line", "Royal Caribbean", "Norwegian Cruise Line", "MSC Cruises"],
    },
    {
        "slug": "alaska-inside-passage-7n",
        "title": "7-Night Alaska Glacier & Inside Passage",
        "region": "Alaska",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "seattle", "port_name": "Seattle", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "juneau", "port_name": "Juneau", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "skagway", "port_name": "Skagway", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "ketchikan", "port_name": "Ketchikan", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "vancouver", "port_name": "Vancouver", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "victoria", "port_name": "Seattle Gateway", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "seattle", "port_name": "Seattle", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Princess Cruises", "Holland America Line", "Celebrity Cruises", "NCL"],
    },
    {
        "slug": "douro-river-experience-7n",
        "title": "7-Night Enchanting Douro River Valley",
        "region": "Douro River",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "porto", "port_name": "Porto (Ribeira)", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "regua", "port_name": "Peso da Régua", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "pinhao", "port_name": "Pinhão", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "pinhao", "port_name": "Pinhão Wine Estate", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "regua", "port_name": "Régua Palace", "type": "PORT_CALL"},
            {"day": 6, "port_slug": "porto", "port_name": "Porto Gaia", "type": "PORT_CALL"},
            {"day": 7, "port_slug": "porto", "port_name": "Porto (Ribeira)", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Tauck", "Viking River", "AmaWaterways", "Uniworld"],
    },
    {
        "slug": "rhine-castles-and-cathedrals-7n",
        "title": "7-Night Rhine Castles & Historic Cathedrals",
        "region": "Rhine River",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "amsterdam", "port_name": "Amsterdam", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "cologne", "port_name": "Cologne", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "koblenz", "port_name": "Koblenz (Rhine Gorge)", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "strasbourg", "port_name": "Strasbourg", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "basel", "port_name": "Basel", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Viking River", "Tauck", "AmaWaterways", "Emerald Cruises"],
    },
    {
        "slug": "danube-imperial-capitals-7n",
        "title": "7-Night Imperial Danube (Three Capitals)",
        "region": "Danube River",
        "duration_days": 7,
        "ports_sequence": [
            {"day": 1, "port_slug": "passau", "port_name": "Passau", "type": "EMBARKATION"},
            {"day": 2, "port_slug": "vienna", "port_name": "Vienna", "type": "PORT_CALL"},
            {"day": 3, "port_slug": "bratislava", "port_name": "Bratislava", "type": "PORT_CALL"},
            {"day": 4, "port_slug": "budapest", "port_name": "Budapest (Parliament)", "type": "PORT_CALL"},
            {"day": 5, "port_slug": "passau", "port_name": "Passau", "type": "DISEMBARKATION"},
        ],
        "common_operators": ["Viking River", "AmaWaterways", "Tauck", "Scenic"],
    },
]


def populate_routes():
    print("=" * 60)
    print("      TIMONELO MASTER ROUTES POPULATION ENGINE")
    print("=" * 60)

    os.makedirs(ROUTES_DIR, exist_ok=True)
    for r in ROUTES_DATA:
        slug = r["slug"]
        path = os.path.join(ROUTES_DIR, f"{slug}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[OK] Successfully Populated {len(ROUTES_DATA)} Canonical Itineraries.")


if __name__ == "__main__":
    populate_routes()
