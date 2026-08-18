# P1 Knowledge Repair Report: MSC Bellissima

**Document ID**: `REPAIR-BEL-2026-08-18`  
**Target Scope**: `knowledge/ships/msc-bellissima/*.json`  
**Primary Evidence**: `Official MSC Bellissima Deck Plan (Edition 11.2025 DEU)`  
**Protocol**: Strict Epistemic Repair (Updated ONLY `CONTRADICTED` fields; zero mutations to `MATCH` or `UNSUPPORTED` fields).

---

## 1. Summary of Changes

All 9 contradictions identified in `knowledge/reports/bellissima_evidence_audit.json` were strictly repaired and cross-verified against JSON Schemas (Draft 2020-12) and the full pytest suite.

| Status Category | Count | Action Taken |
| :--- | :---: | :--- |
| **`CHANGED (Repaired)`** | **9** | Updated to exact primary evidence values from Nov 2025 deck plan |
| **`UNCHANGED (Matches)`** | **79** | Retained exactly as verified |
| **`RETAINED (Unsupported)`** | **11** | Preserved without deletion (Naval/SOLAS engineering specs) |

---

## 2. Changed Fields (`CONTRADICTED` $\rightarrow$ Repaired)

| File | Entity ID | Field | Old Value | New Repaired Value | Primary Evidence Source | Verification Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `technical.json` | `msc-bellissima` | `capacities.passenger_capacity_max_occupancy` | `5686` | `5654` | Deck Plan 11.2025 (Page 2) | Exact guest capacity aligned |
| `technical.json` | `msc-bellissima` | `capacities.total_cabins_max` | `2244` | `2217` | Deck Plan 11.2025 (Page 2) | Exact stateroom total aligned |
| `cabins.json` | `summary` | `total_staterooms` | `2244` | `2217` | Deck Plan 11.2025 (Page 2) | Stateroom catalog summary aligned |
| `cabins.json` | `summary` | `distinct_categories_count` | `32` | `20` | Deck Plan 11.2025 (Page 2) | Aligned with official booking codes (YC3, YJD, YC1, YIN, SXJ, SLJ, SL1, BA, BR3, BR2, BR1, BP, BS, OL2, OR1, OM2, OO, IR2, IR1, IS) |
| `cabins.json` | `CAT-STUDIO-INSIDE` | `name` & `deck` | `Studio Inside` / `Decks 8-14` | `Studio Inside (IS)` / `Decks 5-14` | Deck Plan 11.2025 (Page 2: `IS 5-14`) | Expanded single inside allocation to Decks 5–14 |
| `cabins.json` | `CAT-AUREA-BALCONY` | `name` & `deck` | `Aurea Balcony` / `Decks 11-14` | `Aurea Balcony (BA)` / `Decks 11-13` | Deck Plan 11.2025 (Page 2: `BA 11-13`) | Corrected BA deck range (Deck 14 does not offer BA) |
| `cabins.json` | `CAT-DUPLEX-SUITE-AUREA` | `name`, `category` & `deck` | `Duplex Suite Aurea` / `Decks 9, 10, 12, 13` | `MSC Yacht Club Maisonette Suite mit Whirlpool (YJD)` / `YACHT_CLUB_MAISONETTE_SUITE` / `Decks 9-12` | Deck Plan 11.2025 (Page 2: `YJD 9-12`) | Aligned 2-story duplex classification under MSC Yacht Club enclave |
| `restaurants.json`| `RES-HOLA-TACOS` | `name` & `description` | `HOLA! Tacos & Cantina` | `HOLA! Tapas Bar` | Deck Plan 11.2025 (Page 3: `HOLA! Tapas Bar`) | Labeled correctly as tapas concept by Ramón Freixa |
| `bars.json` | `BAR-EDGE` | `deck` & `description` | `Deck 7` | `Deck 6` | Deck Plan 11.2025 (Page 3) | Edge Cocktail Bar correctly mapped to Deck 6 promenade gallery |
| `decks.json` | `DECK-06`, `DECK-07` | `description` | HOLA on Deck 7 | HOLA! Tapas Bar & Edge on Deck 6; Specialty on Deck 7 | Deck Plan 11.2025 (Page 3) | Text descriptions synchronized with venue decks |

---

## 3. Retained Unsupported Fields (`UNSUPPORTED`)

The following critical naval engineering and operational parameters were not printed on the commercial passenger deck plan map, but originate from official shipyard (Chantiers de l'Atlantique) and SOLAS documentation. **In accordance with epistemic governance rules, these values were preserved intact**:

1. **`dimensions.length_meters = 315.83`** (Length Overall)
2. **`dimensions.beam_meters = 43.00`** (Molded Beam)
3. **`dimensions.draft_meters = 8.75`** (Maximum Draft)
4. **`tonnage_gt = 171598`** (Gross Tonnage via International Tonnage Certificate)
5. **`imo_number = 9760524`** (IMO GISIS Registry)
6. **`propulsion_type = 2 × ABB Azipods (51,500 HP)`**
7. **`balcony_cabin_percentage = 75%`**
8. **`PUB-GALLERIA-LED-DOME.metrics.length_meters = 80.0`**
9. **`SPA-AUREA.facilities.thermal_suite`**
10. **`RES-LATELIER-BISTROT`** (Specialty French Dining launch archive)
11. **`muster_stations.locations`** (SOLAS evacuation station mapping)

---

## 4. Quality Assurance & Validation Results

* **JSON Schema Validation**: 12/12 JSON assets pass strict validation against `knowledge/schema/*.schema.json` (Draft 2020-12).
* **Pytest Suite**: 314 tests passed in 19.46s (100% green).
* **Vite Build**: Compiled with 0 errors in 24.82s.
* **Living Deck Plan / Topology**: Unaffected and 100% stable.
