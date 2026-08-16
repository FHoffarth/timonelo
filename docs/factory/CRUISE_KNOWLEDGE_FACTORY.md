# SPEC-009: CRUISE KNOWLEDGE FACTORY ARCHITECTURE
### Standardized Ingestion Pipeline for Vessels, Ports, and Maritime Routes

---

## 1. Executive Summary & Core Principle

> **The Fundamental Law of the Knowledge Factory:**  
> *"Never ask 'How do we build another ship?' Instead ask 'How do we build the system that builds every future ship?'"*

The **Cruise Knowledge Factory** is Timonelo’s industrial data ingestion and curation pipeline. It transforms legally obtainable, publicly verifiable, and properly attributed maritime data into immutable, structured **Knowledge Packs** (Ships, Ports, and Routes) that feed directly into the Timonelo Spatial Twin and Decision Engine.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               CRUISE KNOWLEDGE FACTORY PIPELINE                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [STAGE 1: DISCOVERY & HARVESTING]                                                               │
│  Public Ship Fact Sheets · IMO / GISIS Registry · Port Authority GA Maps · Shipyard Releases     │
│                                  │                                                               │
│                                  ▼                                                               │
│  [STAGE 2: PROVENANCE & SCHEMA PARSING]                                                          │
│  Field-Level Source Attribution · SHA-256 Checksum · 4-Tier Trust Assignment                     │
│                                  │                                                               │
│                                  ▼                                                               │
│  [STAGE 3: QUALITY GATE AUDIT & VALIDATION]                                                     │
│  SOLAS Statutory Check · Doorway Minimums · Vertical Consistency · No Anonymous Facts           │
│                                  │                                                               │
│                                  ▼                                                               │
│  [STAGE 4: COMPILATION & CANONICAL PACKAGING]                                                    │
│  Standardized Ship Pack (`ships/<slug>/`) · Port Pack (`ports/<slug>/`) · Manifest Registry      │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Four-Tier Trust Classification Model

Every single data point, geometry node, and operational constraint inside Timonelo must belong to one of four immutable trust tiers:

```
┌─────────────────┬──────────────────────────────────────────┬─────────────────────────────────────┐
│ TRUST LEVEL     │ DEFINITION & AUTHORITATIVE SOURCES       │ USAGE RULE IN TIMONELO              │
├─────────────────┼──────────────────────────────────────────┼─────────────────────────────────────┤
│ 🟢 OFFICIAL     │ Direct from Cruise Line, Shipyard (Chantiers│ Treated as authoritative fact.      │
│                 │ de l'Atlantique, Meyer Werft, Fincantieri),│ Geometry & dimensions benchmark.    │
│                 │ Port Authority, IMO/GISIS, or Class      │                                     │
│                 │ Societies (DNV, Bureau Veritas, Lloyd's). │                                     │
├─────────────────┼──────────────────────────────────────────┼─────────────────────────────────────┤
│ 🔵 VERIFIED     │ Cross-checked by Timonelo field audits,  │ Primary ground truth for routing,   │
│                 │ trusted crew measurements, or            │ elevator offsets, and sightlines.   │
│                 │ triangulated across ≥3 public sources.   │                                     │
├─────────────────┼──────────────────────────────────────────┼─────────────────────────────────────┤
│ 🟡 COMMUNITY    │ Passenger deck reviews, historical forum │ Flagged clearly as community insight│
│                 │ observations, travel blogs.              │ Never treated as geometric fact.    │
├─────────────────┼──────────────────────────────────────────┼─────────────────────────────────────┤
│ ⚪ UNKNOWN      │ Inconclusive or missing information.     │ Strictly omitted. Never fabricate   │
│                 │                                          │ or extrapolate without evidence.    │
└─────────────────┴──────────────────────────────────────────┴─────────────────────────────────────┘
```

---

## 3. Provenance & Source Register Design

Anonymous information is strictly forbidden in Timonelo. Every field in a Knowledge Pack is encapsulated in a **Provenanced Field Structure**:

```json
{
  "value": 5655,
  "unit": "passengers",
  "source_id": "src:msc-bellissima-official-factsheet-2024",
  "source_url": "https://www.msccruises.com/fleet/msc-bellissima/technical-sheet.pdf",
  "retrieved_at": "2026-08-16T12:00:00Z",
  "confidence": 1.0,
  "trust_level": "OFFICIAL",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### Master Source Register (`knowledge/sources/registry.json`)
```json
{
  "src:msc-bellissima-official-factsheet-2024": {
    "title": "MSC Bellissima Official Technical & Venue Fact Sheet",
    "publisher": "MSC Cruises S.A.",
    "category": "OFFICIAL_CRUISE_LINE",
    "published_year": 2024,
    "url": "https://www.msccruises.com/fleet/msc-bellissima",
    "license": "Public Informational",
    "verified_by": "Timonelo Knowledge Factory"
  }
}
```

---

## 4. Standardized Ship Knowledge Pack Specification

A Ship Knowledge Pack is stored under `knowledge/ships/<slug>/` and compiles into a single, self-contained entity:

```
knowledge/ships/msc-bellissima/
├── identity.json            # IMO, ENI, MMSI, Call Sign, Flag, Operator, Class, Shipyard
├── technical.json           # Gross Tonnage, Length, Beam, Draft, Power, Stabilizers
├── decks/
│   ├── index.json           # Deck numbering, deck names, elevations above waterline
│   └── deck-14.json         # Spatial boundaries, fire zones, elevator core coordinates
├── cabins/
│   ├── index.json           # Cabin index, category mapping, accessible staterooms
│   └── 14122.json           # Exact dimensions, door width, balcony sightline, sockets
├── venues/
│   ├── restaurants.json     # Dining venues, deck locations, capacity, dress code
│   ├── entertainment.json   # Theatres, lounges, promenades, LED dome specs
│   └── wellness.json        # Pools, spas, solariums, gym footprints
├── ports/
│   └── turnaround.json      # Typical homeports, gangway elevations, tender status
├── limitations.json         # Known sightline obstructions, high-traffic corridors
├── media/
│   └── manifest.json        # Attribution-checked photography and deck drawing paths
└── manifest.json            # Cryptographic SHA-256 seal of all constituent files
```

### Canonical Ship Schema (`identity.json`)
```json
{
  "slug": "msc-bellissima",
  "name": { "value": "MSC Bellissima", "trust_level": "OFFICIAL", "source_id": "src:imo-gisis" },
  "imo": { "value": "9766205", "trust_level": "OFFICIAL", "source_id": "src:imo-gisis" },
  "mmsi": { "value": "248946000", "trust_level": "OFFICIAL", "source_id": "src:itu-maritime" },
  "call_sign": { "value": "9HA4915", "trust_level": "OFFICIAL", "source_id": "src:itu-maritime" },
  "flag_state": { "value": "Malta", "trust_level": "OFFICIAL", "source_id": "src:imo-gisis" },
  "operator": { "value": "MSC Cruises", "trust_level": "OFFICIAL", "source_id": "src:msc-corporate" },
  "ship_class": { "value": "Original Meraviglia Class", "trust_level": "OFFICIAL", "source_id": "src:chantiers-atlantique" },
  "sister_ships": [
    { "name": "MSC Meraviglia", "imo": "9647710", "relationship": "CLASS_LEAD_SHIP" }
  ],
  "subclass_evolutions": [
    { "name": "MSC Grandiosa", "imo": "9803613", "relationship": "MERAVIGLIA_PLUS_SUBCLASS" },
    { "name": "MSC Virtuosa", "imo": "9803625", "relationship": "MERAVIGLIA_PLUS_SUBCLASS" },
    { "name": "MSC Euribia", "imo": "9901544", "relationship": "MERAVIGLIA_PLUS_LNG_SUBCLASS" }
  ],
  "builder": { "value": "Chantiers de l'Atlantique (Saint-Nazaire, France)", "trust_level": "OFFICIAL", "source_id": "src:shipyard-b34" },
  "delivery_date": { "value": "2019-02-27", "trust_level": "OFFICIAL", "source_id": "src:shipyard-b34" },
  "dimensions": {
    "length_m": { "value": 315.8, "trust_level": "OFFICIAL" },
    "beam_m": { "value": 43.0, "trust_level": "OFFICIAL" },
    "draft_m": { "value": 8.75, "trust_level": "OFFICIAL" },
    "gross_tonnage": { "value": 171598, "trust_level": "OFFICIAL" }
  },
  "capacities": {
    "passenger_max": { "value": 5655, "trust_level": "OFFICIAL" },
    "passenger_double_occ": { "value": 4434, "trust_level": "OFFICIAL" },
    "crew": { "value": 1536, "trust_level": "OFFICIAL" },
    "total_staterooms": { "value": 2217, "trust_level": "OFFICIAL" },
    "accessible_staterooms": { "value": 55, "trust_level": "VERIFIED" }
  }
}
```

---

## 5. Standardized Port Knowledge Pack Specification

Ports are standalone reusable entities stored under `knowledge/ports/<slug>/`. Every vessel calling at a port inherits this knowledge instantly:

```
knowledge/ports/genoa/
├── identity.json            # UN/LOCODE (ITGOA), Port Authority, Coordinates, Timezone
├── terminals/
│   └── stazione-marittima.json # Berth numbers, air-draft limits, gangway deck connections
├── logistics/
│   ├── walking.json         # Step-free pathways to city center, pedestrian bridges
│   ├── transit.json         # Taxi flat fares, airport express shuttles, train links
│   └── tender.json          # Docking vs. tender anchorage coordinates, swell limits
├── practical/
│   ├── currency.json        # Local currency, tipping culture, contactless adoption
│   ├── customs.json         # Schengen rules, passport validity, duty-free limits
│   └── emergency.json       # European emergency numbers, nearest international clinic
└── media/
    └── terminal-map.svg     # Simplified step-free passenger walking diagram
```

---

## 6. Standardized Route Knowledge Pack Specification

Routes connect Ships, Ports, and Days into a coherent traveler narrative:

```
knowledge/routes/western-mediterranean-7n/
├── identity.json            # Route slug, duration, operating season, typical sea conditions
├── itinerary.json           # Sequence: Genoa -> Civitavecchia -> Palermo -> Ibiza -> Valencia -> Marseille
├── briefings/
│   ├── day-01-genoa.json    # The Three Clearances, all-aboard, mandatory muster drill
│   ├── day-02-civitavecchia.json # High-speed train to Rome logistics, gangway return
│   └── day-04-sea-day.json  # Horizon sunlight, galley operating hours, fin stabilizers
└── negative-intelligence.json # Known bottlenecks (e.g. Rome train timing, roaming shock)
```

---

## 7. Wave 1 Fleet Ingestion Roadmap (MSC Initial Target)

```
┌──────────────────────────────┬──────────────────┬────────────────────────────┬────────────────────────┐
│ BATCH & SHIP NAME            │ IDENTIFIER       │ NAVAL CLASSIFICATION       │ INGESTION MILESTONE    │
├──────────────────────────────┼──────────────────┼────────────────────────────┼────────────────────────┤
│ **Batch 1: Meraviglia Class**│                  │                            │                        │
│ • MSC Bellissima             │ IMO 9766205      │ Original Meraviglia Class  │ Canonical Reference ✅ │
│ • MSC Meraviglia             │ IMO 9647710      │ Original Class Prototype   │ Sister Ship Twin ✅    │
│                              │                  │                            │                        │
│ **Batch 2: Meraviglia Plus** │                  │                            │                        │
│ • MSC Grandiosa              │ IMO 9803613      │ Meraviglia Plus Subclass   │ Stretched Twin ✅      │
│ • MSC Virtuosa               │ IMO 9803625      │ Meraviglia Plus Subclass   │ Queue Wave 1.2         │
│ • MSC Euribia                │ IMO 9901544      │ Meraviglia Plus LNG Evol.  │ Queue Wave 1.2         │
│                              │                  │                            │                        │
│ **Batch 3: Seaside Series**  │                  │                            │                        │
│ • MSC Seaside                │ IMO 9745366      │ Seaside Class Prototype    │ Queue Wave 1.3         │
│ • MSC Seaview                │ IMO 9745378      │ Seaside Class Sister       │ Queue Wave 1.3         │
│ • MSC Seashore               │ IMO 9805336      │ Seaside EVO Subclass       │ Queue Wave 1.3         │
│ • MSC Seascape               │ IMO 9805348      │ Seaside EVO Subclass       │ Queue Wave 1.3         │
│                              │                  │                            │                        │
│ **Batch 4: World Class**     │                  │                            │                        │
│ • MSC World Europa           │ IMO 9837420      │ World Class Prototype (LNG)│ Queue Wave 1.4         │
│ • MSC World America          │ IMO 9837432      │ World Class Sister (2025)  │ Queue Wave 1.4         │
└──────────────────────────────┴──────────────────┴────────────────────────────┴────────────────────────┘
```

---

## 8. Ingestion Workflow & Quality Gates

```
  [1. HARVEST]       Fetch public Fact Sheet PDF & GISIS record
         │
  [2. POPULATE]      Draft `knowledge/ships/<slug>/identity.json` with field-level sources
         │
  [3. VALIDATE]      Run `python tools/knowledge_factory.py --validate <slug>`:
                     • Gate 1: Checksum verification
                     • Gate 2: Dimension bounds (Draft < Depth < Length)
                     • Gate 3: Cabin-deck count integrity
                     • Gate 4: Zero unprovenanced fields
         │
  [4. COMPILE]       Generate sealed `data/ships/<slug>/knowledge_pack.json`
```

---

> **Constitutional Compliance:** The Cruise Knowledge Factory strictly forbids unauthorized scraping, private data harvesting, and synthetic data fabrication. Every fact is traceable to verified public naval, maritime, and port authority records.
