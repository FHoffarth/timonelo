#!/usr/bin/env python3
"""
Populate complete 25 Ship Classes and missing global ports.
"""

import sys
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
KNOWLEDGE_DIR = os.path.join(REPO_ROOT, "knowledge")

from src.timonelo.database.populate import SHIP_CLASSES_DATA

ADDITIONAL_PORTS = [
    {"slug": "los-angeles", "name": "Port of Los Angeles (World Cruise Center)", "un_locode": "USLAX", "country": "United States", "region": "US West Coast", "lat": 33.7430, "lon": -118.2670, "terminal": "Berths 91-93 San Pedro"},
    {"slug": "sydney", "name": "Port of Sydney (Overseas Passenger Terminal)", "un_locode": "AUSYD", "country": "Australia", "region": "Australia & Pacific", "lat": -33.8580, "lon": 151.2100, "terminal": "Circular Quay OPT (Direct Opera House View)"},
    {"slug": "singapore", "name": "Singapore Marina Bay Cruise Centre (MBCCS)", "un_locode": "SGSIN", "country": "Singapore", "region": "Southeast Asia", "lat": 1.2680, "lon": 103.8610, "terminal": "Marina Bay Cruise Centre Singapore"},
    {"slug": "shanghai", "name": "Shanghai Wusongkou International Cruise Terminal", "un_locode": "CNSHG", "country": "China", "region": "East Asia", "lat": 31.3960, "lon": 121.5050, "terminal": "Baoshan Wusongkou Terminal"},
    {"slug": "hong-kong", "name": "Kai Tak Cruise Terminal (Hong Kong)", "un_locode": "HKHKG", "country": "Hong Kong", "region": "East Asia", "lat": 22.3080, "lon": 114.2130, "terminal": "Kai Tak Runway Berths"},
    {"slug": "london", "name": "London Tilbury / Greenwich Cruise Terminal", "un_locode": "GBLON", "country": "United Kingdom", "region": "Northern Europe", "lat": 51.4600, "lon": 0.3600, "terminal": "London International Cruise Terminal Tilbury"},
    {"slug": "bremerhaven", "name": "Columbus Cruise Center Bremerhaven (CCCB)", "un_locode": "DEBRV", "country": "Germany", "region": "Northern Europe", "lat": 53.5600, "lon": 8.5600, "terminal": "Columbus Cruise Center Berths 1-3"},
    {"slug": "trieste", "name": "Port of Trieste (Molo Bersaglieri)", "un_locode": "ITTRS", "country": "Italy", "region": "Adriatic Sea", "lat": 45.6500, "lon": 13.7650, "terminal": "Stazione Marittima di Trieste"},
    {"slug": "bari", "name": "Port of Bari", "un_locode": "ITBRI", "country": "Italy", "region": "Adriatic Sea", "lat": 41.1350, "lon": 16.8650, "terminal": "Banchina di Ponente & Molo San Vito"},
    {"slug": "ushuaia", "name": "Port of Ushuaia (Antarctica Gateway)", "un_locode": "ARUSH", "country": "Argentina", "region": "South America / Patagonia", "lat": -54.8100, "lon": -68.3000, "terminal": "Muelle Comercial Ushuaia"},
    {"slug": "buenos-aires", "name": "Port of Buenos Aires (Benito Quinquela Martín)", "un_locode": "ARBUE", "country": "Argentina", "region": "South America", "lat": -34.5850, "lon": -58.3700, "terminal": "Terminal de Cruceros Benito Quinquela Martín"},
    {"slug": "ocho-rios", "name": "Port of Ocho Rios (Jamaica)", "un_locode": "JMOCH", "country": "Jamaica", "region": "Western Caribbean", "lat": 18.4100, "lon": -77.1080, "terminal": "Turtle Beach & James Bond Pier"},
    {"slug": "cabo-san-lucas", "name": "Port of Cabo San Lucas (Baja California)", "un_locode": "MXCSL", "country": "Mexico", "region": "Mexican Riviera", "lat": 22.8800, "lon": -109.9100, "terminal": "Marina Cabo Tender Pier (Land's End Arch)"},
    {"slug": "mazatlan", "name": "Port of Mazatlán (Sinaloa)", "un_locode": "MZMZT", "country": "Mexico", "region": "Mexican Riviera", "lat": 23.2000, "lon": -106.4150, "terminal": "Mazatlán Cruise Terminal (Blue Line Walk)"},
    {"slug": "puerto-vallarta", "name": "Port of Puerto Vallarta (Jalisco)", "un_locode": "MXPVR", "country": "Mexico", "region": "Mexican Riviera", "lat": 20.6550, "lon": -105.2400, "terminal": "Puerto Mágico Cruise Terminal"},
    {"slug": "ensenada", "name": "Port of Ensenada (Baja California)", "un_locode": "MXESE", "country": "Mexico", "region": "Mexican Riviera", "lat": 31.8550, "lon": -116.6200, "terminal": "Muelle de Cruceros Ensenada"},
    {"slug": "victoria", "name": "Port of Victoria (Ogden Point)", "un_locode": "CAVIC", "country": "Canada", "region": "Pacific Northwest / Alaska", "lat": 48.4150, "lon": -123.3850, "terminal": "Ogden Point Terminal (Piers A & B)"},
    {"slug": "port-everglades", "name": "Port Everglades (Fort Lauderdale)", "un_locode": "USPEF", "country": "United States", "region": "Florida / Caribbean", "lat": 26.0864, "lon": -80.1189, "terminal": "Terminal 25 & 18"},
]



def refuse_port_population(port_count: int) -> None:
    """Fail closed rather than regenerate the synthetic port identity layer.

    An error is the correct output here. The alternative -- emitting the
    fields with null values instead of literals -- would still overwrite 119
    tracked files, discarding the explicit nulls that record which claims were
    asserted and withdrawn, and would leave a bulk writer pointed at the
    knowledge layer for a job that no longer exists.

    Port identity now requires field-scoped evidence per port. There is no
    bulk path to that, so there is no safe way to run this.
    """
    raise RuntimeError(
        f"Refusing to populate {port_count} port identity packs.\n"
        "\n"
        "This generator wrote template constants into every "
        "knowledge/ports/<slug>/identity.json and attested them as OFFICIAL "
        "with a field:'all' source record. Those values were quarantined by "
        "ADR-0006 and the templates have been removed.\n"
        "\n"
        "Port identity facts now require field-scoped evidence per port. To "
        "add a port, create its identity.json with entity fields only "
        "(slug, name, un_locode, country, region, coordinates) and leave "
        "every passenger-facing field absent until sourced.\n"
        "\n"
        "See docs/adr/ADR-0006.md and "
        "docs/PORT_IDENTITY_CORPUS_AUDIT_2026-08-24.md"
    )


def populate_classes_and_extra_ports():
    # Fail closed before ANY write; see the note in mass_populate_knowledge.py.
    refuse_port_population(len(ADDITIONAL_PORTS))

    # 1. Ship Classes (25 Classes)
    classes_dir = os.path.join(KNOWLEDGE_DIR, "ship-classes")
    os.makedirs(classes_dir, exist_ok=True)
    for c in SHIP_CLASSES_DATA:
        slug = c["slug"]
        path = os.path.join(classes_dir, f"{slug}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[OK] Populated {len(SHIP_CLASSES_DATA)} Canonical Ship Classes.")

    # 2. Additional Strategic Ports
    #
    # RETIRED. This block previously synthesised every passenger-facing field
    # of knowledge/ports/<slug>/identity.json from hardcoded literals --
    # gangway_deck_default=5, distance_to_city_center_m=800,
    # walking_time_min=10, card_acceptance_pct=98, step_free_access=True,
    # berths named from the slug, negative_intelligence from an f-string
    # template -- and stamped the result with a blanket source record
    # (field:"all", source_id:"src:official-port-authority",
    # trust_level:"OFFICIAL"). None of it had evidence. See ADR-0006.
    #
    # ADDITIONAL_PORTS is kept above because it records where the port slugs,
    # names, coordinates and UN/LOCODEs entered the repository. That data is
    # unvalidated candidate identity, not canon, and nothing here may write it
    # back as fact.


if __name__ == "__main__":
    populate_classes_and_extra_ports()
