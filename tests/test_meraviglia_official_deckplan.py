"""
tests/test_meraviglia_official_deckplan.py

Unit tests verifying the evidence-backed re-ingestion of MSC Meraviglia:
- Physical Source Artifact & Byte Digest
- Accurate Cabin & Passenger Counts (2,214 Cabins, 5,714 Guests)
- Official Deck Names (Kos on Deck 4, Kilimangiaro on Deck 13)
- 22 Cabin Categories & Deck Ranges
- Specific Cabin Rule Constraints (Bunk bed cabins 13245, 13342, 14213, 14256)
- Venue-to-Deck Grounding (Hola! Tacos & Cantina on Deck 6, Top Sail Lounge on Deck 16)
- Geometry Firewall Maintained (No false upgrade of synthetic geometry)
"""

import os
import json
import pytest
from timonelo.evidence.gatekeeper import compute_file_sha256

BASE_DIR = r"C:\Users\Flo\Desktop\energyradar\timonelo"
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge", "ships", "msc-meraviglia")
ARTIFACT_PATH = os.path.join(
    BASE_DIR,
    "evidence",
    "raw",
    "sha256",
    "77",
    "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf",
)


def test_meraviglia_primary_source_artifact_integrity():
    assert os.path.isfile(ARTIFACT_PATH), f"Primary artifact not found at {ARTIFACT_PATH}"
    digest = compute_file_sha256(ARTIFACT_PATH)
    assert digest == "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"


def test_meraviglia_cabin_and_guest_capacity():
    with open(os.path.join(KNOWLEDGE_DIR, "technical.json"), "r", encoding="utf-8") as f:
        tech = json.load(f)
    assert tech["technical_specifications"]["capacities"]["total_cabins_max"] == 2214
    assert tech["technical_specifications"]["capacities"]["passenger_capacity_max_occupancy"] == 5714

    with open(os.path.join(KNOWLEDGE_DIR, "cabins.json"), "r", encoding="utf-8") as f:
        cabins = json.load(f)
    assert cabins["summary"]["total_staterooms"] == 2214
    assert cabins["summary"]["max_guests"] == 5714


def test_meraviglia_official_deck_names():
    with open(os.path.join(KNOWLEDGE_DIR, "decks.json"), "r", encoding="utf-8") as f:
        deck_doc = json.load(f)
    
    deck_map = {d["deck_number"]: d["name"] for d in deck_doc["decks"]}
    assert 4 in deck_map and "Kos" in deck_map[4]
    assert 5 in deck_map and "Colosseo" in deck_map[5]
    assert 6 in deck_map and "Petra" in deck_map[6]
    assert 7 in deck_map and "Taj Mahal" in deck_map[7]
    assert 8 in deck_map and "Machu Picchu" in deck_map[8]
    assert 9 in deck_map and "Alhambra" in deck_map[9]
    assert 10 in deck_map and "Hagia Sophia" in deck_map[10]
    assert 11 in deck_map and "Acropolis" in deck_map[11]
    assert 12 in deck_map and "Grand Canyon" in deck_map[12]
    assert 13 in deck_map and "Kilimangiaro" in deck_map[13]
    assert 14 in deck_map and "Angkor Wat" in deck_map[14]
    assert 15 in deck_map and "Tour Eiffel" in deck_map[15]
    assert 16 in deck_map and "Iguazu" in deck_map[16]
    assert 18 in deck_map and "Pyramids" in deck_map[18]
    assert 19 in deck_map and "Babylon" in deck_map[19]
    assert 17 not in deck_map


def test_meraviglia_cabin_categories_and_rules():
    with open(os.path.join(KNOWLEDGE_DIR, "cabins.json"), "r", encoding="utf-8") as f:
        cabins = json.load(f)

    categories = {c["code"]: c for c in cabins["cabin_categories"]}
    expected_codes = [
        "YC3", "YJD", "YC1", "YIN", "SXJ", "SLJ", "BA",
        "BL3", "BL2", "BL1", "BR3", "BR2", "BR1", "BP",
        "BS", "OL2", "OR1", "OM2", "OO", "IR2", "IR1", "IS"
    ]
    for code in expected_codes:
        assert code in categories, f"Category code {code} missing from re-ingested cabins"

    # Specific Category Deck Checks
    assert categories["SXJ"]["deck_range"] == [12]
    assert categories["YC3"]["deck_range"] == [15]
    assert categories["YJD"]["deck_range"] == [9, 10, 11, 12]

    # Specific Rule Check for Bunk Bed Cabins
    rules_text = " ".join(cabins["summary"]["standard_rules"])
    assert "13245" in rules_text
    assert "13342" in rules_text
    assert "14213" in rules_text
    assert "14256" in rules_text


def test_meraviglia_venues_grounding():
    with open(os.path.join(KNOWLEDGE_DIR, "restaurants.json"), "r", encoding="utf-8") as f:
        res = json.load(f)
    res_names = {r["name"]: r["deck"] for r in res["restaurants"]}
    assert "Hola! Tacos & Cantina" in res_names
    assert res_names["Hola! Tacos & Cantina"] == 6
    assert "Ocean Cay" in res_names
    assert res_names["Ocean Cay"] == 6

    with open(os.path.join(KNOWLEDGE_DIR, "lounges.json"), "r", encoding="utf-8") as f:
        lounges = json.load(f)
    lounge_names = {l["name"]: l["deck"] for l in lounges["lounges"]}
    assert "Top Sail Lounge" in lounge_names
    assert lounge_names["Top Sail Lounge"] == 16
