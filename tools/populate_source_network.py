#!/usr/bin/env python3
"""
Populates the Timonelo Source Network with categorized provenance records.
"""

from __future__ import annotations
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(REPO_ROOT, "knowledge", "sources")

SOURCES = [
    # 1. Official & Government
    {
        "category_folder": "official",
        "source_id": "src:imo-gisis",
        "name": "IMO Global Integrated Shipping Information System (GISIS)",
        "owner": "International Maritime Organization (UN Specialized Agency)",
        "category": "IMO_GISIS",
        "website": "https://gisis.imo.org",
        "country": "International (UN)",
        "jurisdiction": "Global Maritime Safety",
        "licence": "Public Statutory Maritime Safety Data",
        "terms": "Official statutory registry for IMO ship numbers, tonnages, and flag states.",
        "access_method": "API",
        "allowed_usage": "Statutory vessel identity verification and flag state tracking.",
        "update_frequency": "DAILY",
        "last_retrieved": "2026-08-16",
        "freshness_days": 0,
        "priority": 1,
        "trust_score": 1.0,
    },
    {
        "category_folder": "official",
        "source_id": "src:itu-mars",
        "name": "ITU Maritime Mobile Access and Retrieval System (MARS)",
        "owner": "International Telecommunication Union",
        "category": "GOVERNMENT_MARITIME",
        "website": "https://www.itu.int/mmsapp/ShipStation/list",
        "country": "International (UN)",
        "jurisdiction": "Global Maritime Radiocommunications",
        "licence": "Public Telecommunications Data",
        "terms": "Official registry for Call Signs and Maritime Mobile Service Identities (MMSI).",
        "access_method": "API",
        "allowed_usage": "MMSI and call sign verification.",
        "update_frequency": "WEEKLY",
        "last_retrieved": "2026-08-15",
        "freshness_days": 1,
        "priority": 1,
        "trust_score": 1.0,
    },
    # 2. Classification Societies
    {
        "category_folder": "classification",
        "source_id": "src:dnv-gl-vessel-register",
        "name": "DNV Vessel Register (Veritas)",
        "owner": "DNV Group (Det Norske Veritas)",
        "category": "CLASSIFICATION_SOCIETY",
        "website": "https://vesselregister.dnv.com",
        "country": "Norway / Germany",
        "jurisdiction": "International Marine Classification",
        "licence": "Authorized Marine Classification Access",
        "terms": "Hull dimensions, gross tonnage certifications, hull framing calculations.",
        "access_method": "PDF",
        "allowed_usage": "Naval architecture verification.",
        "update_frequency": "MONTHLY",
        "last_retrieved": "2026-08-10",
        "freshness_days": 6,
        "priority": 2,
        "trust_score": 0.99,
    },
    {
        "category_folder": "classification",
        "source_id": "src:bureau-veritas-marine",
        "name": "Bureau Veritas Marine Register",
        "owner": "Bureau Veritas Marine & Offshore",
        "category": "CLASSIFICATION_SOCIETY",
        "website": "https://marine-offshore.bureauveritas.com",
        "country": "France",
        "jurisdiction": "International Classification",
        "licence": "Public Marine Directory",
        "terms": "Classification society records for Chantiers de l'Atlantique builds (MSC Meraviglia / Bellissima).",
        "access_method": "HTML",
        "allowed_usage": "Statutory classification survey tracking.",
        "update_frequency": "MONTHLY",
        "last_retrieved": "2026-08-01",
        "freshness_days": 15,
        "priority": 2,
        "trust_score": 0.99,
    },
    # 3. Shipyards
    {
        "category_folder": "shipyards",
        "source_id": "src:chantiers-atlantique-ga",
        "name": "Chantiers de l'Atlantique General Arrangement Specifications",
        "owner": "Chantiers de l'Atlantique (Saint-Nazaire)",
        "category": "SHIPYARD",
        "website": "https://chantiers-atlantique.com",
        "country": "France",
        "jurisdiction": "French Naval Engineering",
        "licence": "Shipyard Press Releases & Technical Sheets",
        "terms": "Engineering blueprints for Meraviglia and World Class hulls.",
        "access_method": "PDF",
        "allowed_usage": "Vessel spatial modeling and deck dimensioning.",
        "update_frequency": "EVENT_DRIVEN",
        "last_retrieved": "2026-08-16",
        "freshness_days": 0,
        "priority": 2,
        "trust_score": 0.98,
    },
    # 4. Cruise Lines
    {
        "category_folder": "cruise-lines",
        "source_id": "src:msc-cruises-official",
        "name": "MSC Cruises Official Fleet & Deployment Releases",
        "owner": "MSC Cruises S.A. (Geneva, Switzerland)",
        "category": "CRUISE_LINE",
        "website": "https://www.msccruises.com",
        "country": "Switzerland",
        "jurisdiction": "Commercial Maritime Operator",
        "licence": "Public Customer Operations & Deck Plans",
        "terms": "Official stateroom categorization, venue menus, and itinerary schedules.",
        "access_method": "HTML",
        "allowed_usage": "Passenger experience modeling and deck plan verification.",
        "update_frequency": "WEEKLY",
        "last_retrieved": "2026-08-16",
        "freshness_days": 0,
        "priority": 3,
        "trust_score": 0.95,
    },
    # 5. Port Authorities
    {
        "category_folder": "ports",
        "source_id": "src:port-authority-genoa",
        "name": "Autorita di Sistema Portuale del Mar Ligure Occidentale",
        "owner": "Ports of Genoa Authority",
        "category": "PORT_AUTHORITY",
        "website": "https://www.portsofgenoa.com",
        "country": "Italy",
        "jurisdiction": "Italian State Port Authority",
        "licence": "Public Maritime Port Operations",
        "terms": "Berth assignments at Ponte dei Mille, draft limitations, and cruise terminal procedures.",
        "access_method": "CSV",
        "allowed_usage": "Port logistics and turnaround mapping.",
        "update_frequency": "DAILY",
        "last_retrieved": "2026-08-16",
        "freshness_days": 0,
        "priority": 2,
        "trust_score": 0.98,
    },
    # 6. Weather & Oceanography
    {
        "category_folder": "weather",
        "source_id": "src:noaa-marine-ecmwf",
        "name": "NOAA Marine Forecast & ECMWF Wave Models",
        "owner": "National Oceanic and Atmospheric Administration",
        "category": "WEATHER_METEOROLOGY",
        "website": "https://marine.weather.gov",
        "country": "USA / European Union",
        "jurisdiction": "Global Ocean Meteorology",
        "licence": "Public Domain Atmospheric and Wave Forecasts",
        "terms": "Wave height (swell), wind velocity, and sea state forecasts.",
        "access_method": "API",
        "allowed_usage": "Dynamic weather and comfort zone contextualization.",
        "update_frequency": "DAILY",
        "last_retrieved": "2026-08-16",
        "freshness_days": 0,
        "priority": 4,
        "trust_score": 0.96,
    },
]


def populate_sources():
    for s in SOURCES:
        folder = os.path.join(SOURCES_DIR, s["category_folder"])
        os.makedirs(folder, exist_ok=True)
        fname = f"{s['source_id'].replace(':', '_')}.json"
        path = os.path.join(folder, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
    print(f" [OK] Populated {len(SOURCES)} structured source records across 6 source categories.")


if __name__ == "__main__":
    populate_sources()
