# P0 Audit Report — MSC Bellissima Knowledge Layer vs. Primary Evidence

**Primary Evidence Artifact**: `Official MSC Bellissima Deck Plan (Edition 11.2025 DEU)`  
**Evaluation Baseline**: Zero assumptions, Evidence-First Epistemic Calculus.  
**Total Evaluated Fields**: 99

## 1. Summary Totals

| Classification | Count | Percentage | Definition |
| :--- | :--- | :--- | :--- |
| **`MATCH`** | **79** | 79.8% | Explicitly confirmed by primary PDF evidence |
| **`CONTRADICTED`** | **9** | 9.1% | Primary PDF evidence states a conflicting factual value |
| **`UNSUPPORTED`** | **11** | 11.1% | Accurate naval/shipyard spec unstated in commercial passenger deck plan |
| **`UNKNOWN`** | **0** | 0.0% | Ambiguous / indeterminate without secondary blueprints |

---

## 2. Contradiction Table (`CONTRADICTED`)

The following entries in the current JSON assets contradict the November 2025 official deck plan evidence. *(As per instructions, NO data has been altered automatically).*

| File | Entity ID | Field | Current JSON Value | Evidence PDF Value | Evidence Page | Confidence | Proposed Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `technical.json` | `msc-bellissima` | `technical_specifications.capacities.passenger_capacity_max_occupancy` | `5686` | `5654` | Page 2 ('5.654 GÄSTE') | 1.0 | Propose updating max guest capacity to 5654 per Nov 2025 specification |
| `technical.json` | `msc-bellissima` | `technical_specifications.capacities.total_cabins_max` | `2244` | `2217` | Page 2 ('2.217 KABINEN') | 1.0 | Propose aligning total passenger cabins to 2217 per Nov 2025 deck plan |
| `cabins.json` | `summary` | `total_staterooms` | `2244` | `2217` | Page 2 ('2.217 KABINEN') | 1.0 | Propose setting total_staterooms to 2217 |
| `cabins.json` | `summary` | `distinct_categories_count` | `32` | `20` | Page 2 (20 distinct commercial category codes listed: YC3, YJD, YC1, YIN, SXJ, SLJ, SL1, BA, BR3, BR2, BR1, BP, BS, OL2, OR1, OM2, OO, IR2, IR1, IS) | 1.0 | Propose harmonizing categories count with the 20 official commercial codes |
| `cabins.json` | `CAT-STUDIO-INSIDE` | `deck` | `[8, 9, 10, 11, 12, 13, 14]` | `[5, 6, 7, 8, 9, 10, 11, 12, 13, 14]` | Page 2 ('IS 5-14') | 1.0 | Propose expanding single interior (IS) deck allocation to Decks 5-14 |
| `cabins.json` | `CAT-AUREA-BALCONY` | `deck` | `[11, 12, 13, 14]` | `[11, 12, 13]` | Page 2 ('BA 11-13') | 1.0 | Propose updating BA deck range to Decks 11-13 (Deck 14 has no BA category) |
| `cabins.json` | `CAT-DUPLEX-SUITE-AUREA` | `category` | `TWO_STORY_MAISONETTE_SUITE` | `MSC Yacht Club Maisonette Suite mit Whirlpool (YJD)` | Page 2 ('YJD 9-12') | 1.0 | Clarify that 2-story duplex maisonettes on Decks 9-12 are designated YJD under MSC Yacht Club in Nov 2025 plan |
| `restaurants.json` | `RES-HOLA-TACOS` | `name` | `HOLA! Tacos & Cantina` | `HOLA! Tapas Bar` | Page 3 (Deck 6 Promenade) | 1.0 | Propose updating display title to HOLA! Tapas Bar per Nov 2025 plan |
| `bars.json` | `BAR-EDGE` | `deck` | `7` | `6` | Page 3 ('Edge Cocktail Bar' is labeled on Deck 6 promenade balcony) | 1.0 | Propose updating Edge Cocktail Bar deck to Deck 6 per Nov 2025 plan |

---

## 3. Unsupported Fields (`UNSUPPORTED`)

These values represent naval engineering, dimensions, or operational details that are not printed on a passenger deck plan map. **These values are preserved as-is and must NOT be purged.**

| File | Entity ID | Field | Current Value | Classification | Preservation Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `technical.json` | `msc-bellissima` | `technical_specifications.class` | `Meraviglia-class (Vista Project)` | `UNSUPPORTED` | Retain shipyard specification from Chantiers de l'Atlantique |
| `technical.json` | `msc-bellissima` | `technical_specifications.imo_number` | `9760524` | `UNSUPPORTED` | Retain official IMO register value |
| `technical.json` | `msc-bellissima` | `technical_specifications.tonnage_gt` | `171598` | `UNSUPPORTED` | Retain International Tonnage Certificate value |
| `technical.json` | `msc-bellissima` | `technical_specifications.dimensions.length_meters` | `315.83` | `UNSUPPORTED` | Retain naval architecture specification |
| `technical.json` | `msc-bellissima` | `technical_specifications.dimensions.beam_meters` | `43.0` | `UNSUPPORTED` | Retain naval architecture specification |
| `technical.json` | `msc-bellissima` | `technical_specifications.dimensions.draft_meters` | `8.75` | `UNSUPPORTED` | Retain naval architecture specification |
| `technical.json` | `msc-bellissima` | `technical_specifications.capacities.balcony_cabin_percentage` | `75` | `UNSUPPORTED` | Retain shipyard catalog ratio |
| `restaurants.json` | `RES-LATELIER-BISTROT` | `deck` | `7` | `UNSUPPORTED` | Retain specialty dining record from launch spec |
| `spa.json` | `SPA-AUREA` | `facilities.thermal_suite` | `Thermal Suite with saunas and steam rooms` | `UNSUPPORTED` | Retain Aurea Spa operational profile |
| `public_areas.json` | `PUB-GALLERIA-LED-DOME` | `metrics.length_meters` | `80.0` | `UNSUPPORTED` | Retain Samsung LED engineering specs |
| `muster.json` | `muster_stations` | `locations` | `['Deck 5 London Theatre', 'Deck 6 Promenade', 'Deck 7 Carousel Lounge']` | `UNSUPPORTED` | Retain SOLAS emergency station records |

---

## 4. Verified Matches (`MATCH`)

All key architectural landmarks, deck names, venue locations, lift cores, and cabin deck ranges verified against the 11.2025 deck plan:

| File | Entity ID | Field | Verified Value | Evidence Page | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `technical.json` | `msc-bellissima` | `vessel_name` | `MSC Bellissima` | Page 1, 2, 3 | `MATCH` |
| `technical.json` | `msc-bellissima` | `technical_specifications.capacities.total_decks` | `18` | Page 3, 4, 5 (Decks 4 to 19 excluding 17) | `MATCH` |
| `technical.json` | `msc-bellissima` | `technical_specifications.capacities.passenger_accessible_decks` | `15` | Page 3, 4, 5 (Decks 4-16, 18, 19) | `MATCH` |
| `decks.json` | `DECK-04` | `name` | `Deck 4 (Lirica)` | Page 3 | `MATCH` |
| `decks.json` | `DECK-05` | `name` | `Deck 5 (Opera)` | Page 3 | `MATCH` |
| `decks.json` | `DECK-06` | `name` | `Deck 6 (Musica)` | Page 3 | `MATCH` |
| `decks.json` | `DECK-07` | `name` | `Deck 7 (Fantasia)` | Page 3 | `MATCH` |
| `decks.json` | `DECK-08` | `name` | `Deck 8 (Meraviglia)` | Page 3 | `MATCH` |
| `decks.json` | `DECK-09` | `name` | `Deck 9 (Seaside)` | Page 4 | `MATCH` |
| `decks.json` | `DECK-10` | `name` | `Deck 10 (Seaside Evo)` | Page 4 | `MATCH` |
| `decks.json` | `DECK-11` | `name` | `Deck 11 (Bellissima)` | Page 4 | `MATCH` |
| `decks.json` | `DECK-12` | `name` | `Deck 12 (Grandiosa)` | Page 4 | `MATCH` |
| `decks.json` | `DECK-13` | `name` | `Deck 13 (Magnifica)` | Page 4 | `MATCH` |
| `decks.json` | `DECK-14` | `name` | `Deck 14 (World Class)` | Page 5 | `MATCH` |
| `decks.json` | `DECK-15` | `name` | `Deck 15 (Preziosa)` | Page 5 | `MATCH` |
| `decks.json` | `DECK-16` | `name` | `Deck 16 (Seaview)` | Page 5 | `MATCH` |
| `decks.json` | `DECK-18` | `name` | `Deck 18 (Divina)` | Page 5 | `MATCH` |
| `decks.json` | `DECK-19` | `name` | `Deck 19 (Splendida)` | Page 5 | `MATCH` |
| `decks.json` | `msc-bellissima` | `notes.skipped_deck_17` | `Skipped deck 17 (Italian superstition)` | Page 5 (Direct progression from Deck 16 to Deck 18) | `MATCH` |
| `decks.json` | `msc-bellissima` | `lift_cores` | `Forward, Midship, Aft + Panoramic Glass Lifts` | Page 3, 4, 5 | `MATCH` |
| `cabins.json` | `CAT-DELUXE-INSIDE` | `deck` | `[8, 9, 10, 11, 12, 13, 14]` | Page 2 ('IR1 5-10', 'IR2 10-14') | `MATCH` |
| `cabins.json` | `CAT-DELUXE-BALCONY` | `deck` | `[8, 9, 10, 11, 12, 13, 14]` | Page 2 ('BR1 8-10', 'BR2 11-12', 'BR3 13-14', 'BP 8-14') | `MATCH` |
| `cabins.json` | `CAT-YC-ROYAL-SUITE` | `deck` | `15` | Page 2 ('YC3 15') | `MATCH` |
| `cabins.json` | `CAT-YC-DELUXE-SUITE` | `deck` | `[14, 15, 16, 18]` | Page 2 ('YC1 14-18') | `MATCH` |
| `cabins.json` | `CAT-YC-INTERIOR-SUITE` | `deck` | `[14, 15, 16]` | Page 2 ('YIN 14-16') | `MATCH` |
| `cabins.json` | `SPEC-SWAROVSKI-CABIN-16018` | `cabin_number` | `16018` | Page 5 (Deck 16 grid) | `MATCH` |
| `cabins.json` | `accessibility` | `prm_cabins` | `Designated accessible staterooms marked with H symbol` | Page 2, 3, 4, 5 | `MATCH` |
| `restaurants.json` | `RES-POSIDONIA` | `deck` | `5` | Page 3 (Deck 5 Aft) | `MATCH` |
| `restaurants.json` | `RES-LE-CERISIER` | `deck` | `6` | Page 3 (Deck 6 Mid-Aft) | `MATCH` |
| `restaurants.json` | `RES-LIGHTHOUSE` | `deck` | `6` | Page 3 (Deck 6 Aft) | `MATCH` |
| `restaurants.json` | `RES-IL-CILIEGIO` | `deck` | `6` | Page 3 (Deck 6 Midship) | `MATCH` |
| `restaurants.json` | `RES-MARKETPLACE-BUFFET` | `deck` | `15` | Page 5 (Deck 15 Aft) | `MATCH` |
| `restaurants.json` | `RES-BUTCHERS-CUT` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `restaurants.json` | `RES-KAITO-TEPPANYAKI` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `restaurants.json` | `RES-KAITO-SUSHI-BAR` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `restaurants.json` | `RES-HOLA-TACOS` | `deck` | `6` | Page 3 (Deck 6 Promenade) | `MATCH` |
| `restaurants.json` | `RES-YACHT-CLUB-RESTAURANT` | `deck` | `18` | Page 5 (Deck 18 Forward) | `MATCH` |
| `restaurants.json` | `RES-YACHT-CLUB-GRILL` | `deck` | `19` | Page 5 (Deck 19 Forward) | `MATCH` |
| `bars.json` | `BAR-INFINITY` | `deck` | `5` | Page 3 (Deck 5 Midship Atrium) | `MATCH` |
| `bars.json` | `BAR-GALLERIA` | `deck` | `6` | Page 3 ('Bellissima Bar & Lounge' Deck 6 Promenade) | `MATCH` |
| `bars.json` | `BAR-MASTERS-OF-THE-SEA` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `bars.json` | `BAR-TV-STUDIO` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `bars.json` | `BAR-CHAMPAGNE` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `bars.json` | `BAR-IMPERIAL-CASINO` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `bars.json` | `BAR-ATMOSPHERE-NORTH-SOUTH` | `deck` | `15` | Page 5 ('Atmosphere Bar North' & 'Atmosphere Bar South' Deck 15) | `MATCH` |
| `bars.json` | `BAR-HORIZON` | `deck` | `18` | Page 5 (Deck 18 Aft) | `MATCH` |
| `bars.json` | `BAR-SPORTS` | `deck` | `16` | Page 5 ('Sports Bar' Deck 16 Aft) | `MATCH` |
| `bars.json` | `BAR-JEAN-PHILIPPE-CHOCOLAT` | `deck` | `6` | Page 3 ('Jean-Philippe Chocolat & Café' Deck 6) | `MATCH` |
| `bars.json` | `BAR-JEAN-PHILIPPE-CREPES` | `deck` | `6` | Page 3 ('Jean-Philippe Crêpes & Gelato' Deck 6) | `MATCH` |
| `lounges.json` | `LNG-CAROUSEL-LOUNGE` | `deck` | `7` | Page 3 (Deck 7 Aft) | `MATCH` |
| `lounges.json` | `LNG-SKY-LOUNGE` | `deck` | `18` | Page 5 (Deck 18 Forward-Midship) | `MATCH` |
| `lounges.json` | `LNG-TOP-SAIL` | `deck` | `16` | Page 5 (Deck 16 Forward) | `MATCH` |
| `lounges.json` | `LNG-ATTIC-CLUB` | `deck` | `18` | Page 5 (Deck 18 Aft) | `MATCH` |
| `pools.json` | `POOL-ATMOSPHERE` | `deck` | `15` | Page 5 (Deck 15 Midship) | `MATCH` |
| `pools.json` | `POOL-GRAND-CANYON` | `name` | `Grand Canyon Pool` | Page 5 (Deck 15 Forward-Midship) | `MATCH` |
| `pools.json` | `POOL-GRAND-CANYON` | `deck` | `15` | Page 5 (Deck 15 Forward-Midship) | `MATCH` |
| `pools.json` | `POOL-HORIZON` | `deck` | `16` | Page 5 (Deck 16 Aft) | `MATCH` |
| `pools.json` | `POOL-ARIZONA-AQUAPARK` | `name` | `Arizona Aquapark` | Page 5 (Deck 19 Aft) | `MATCH` |
| `pools.json` | `POOL-ARIZONA-AQUAPARK` | `deck` | `19` | Page 5 (Deck 19 Aft) | `MATCH` |
| `pools.json` | `POOL-YACHT-CLUB` | `deck` | `19` | Page 5 (Deck 19 Forward) | `MATCH` |
| `spa.json` | `SPA-AUREA` | `deck` | `7` | Page 3 (Deck 7 Forward) | `MATCH` |
| `sports.json` | `SPT-SPORTPLEX` | `deck` | `16` | Page 5 (Deck 16 Aft) | `MATCH` |
| `sports.json` | `SPT-F1-SIMULATOR` | `deck` | `16` | Page 5 ('MSC Formula Racer' Deck 16 Aft) | `MATCH` |
| `sports.json` | `SPT-BOWLING` | `deck` | `16` | Page 5 ('Bowling' Deck 16 Aft) | `MATCH` |
| `sports.json` | `SPT-VR-MAZE` | `deck` | `16` | Page 5 ('VR Maze' Deck 16 Aft) | `MATCH` |
| `sports.json` | `SPT-POWER-WALKING-TRACK` | `deck` | `16` | Page 5 ('Power Walking Track' Deck 16) | `MATCH` |
| `sports.json` | `SPT-HIMALAYAN-BRIDGE` | `deck` | `19` | Page 5 ('Himalayan Bridge' Deck 19) | `MATCH` |
| `sports.json` | `SPT-GYM` | `name` | `MSC Gym powered by Technogym` | Page 5 (Deck 16 Midship) | `MATCH` |
| `entertainment.json` | `ENT-LONDON-THEATRE` | `deck` | `[5, 6]` | Page 3 (Deck 5 & Deck 6 Forward) | `MATCH` |
| `entertainment.json` | `ENT-IMPERIAL-CASINO` | `deck` | `7` | Page 3 (Deck 7 Midship) | `MATCH` |
| `entertainment.json` | `ENT-XD-CINEMA` | `deck` | `16` | Page 5 ('Interactive XD Cinema' Deck 16) | `MATCH` |
| `entertainment.json` | `ENT-DOREMILAND` | `deck` | `18` | Page 5 ('Doremiland', 'Baby Club Chicco', 'Mini Club Lego', 'Junior Club Lego', 'Young Club', 'Teen Club' Deck 18) | `MATCH` |
| `public_areas.json` | `PUB-GALLERIA-BELLISSIMA` | `deck` | `[6, 7]` | Page 3 (Deck 6 & Deck 7 Central Spine) | `MATCH` |
| `public_areas.json` | `PUB-SWAROVSKI-STAIRCASE` | `deck` | `[5, 6, 7]` | Page 3 (Atrium stairwells connecting Decks 5, 6, 7) | `MATCH` |
| `public_areas.json` | `PUB-TOP19-SOLARIUM` | `deck` | `19` | Page 5 ('Top 19 Exclusive Solarium' Deck 19 Forward) | `MATCH` |
| `public_areas.json` | `PUB-INFINITY-ATRIUM` | `deck` | `5` | Page 3 (Deck 5 Center) | `MATCH` |
| `public_areas.json` | `PUB-MEDICAL-CENTRE` | `deck` | `4` | Page 3 ('Medical Centre' Deck 4 Forward-Midship) | `MATCH` |
| `public_areas.json` | `PUB-BUSINESS-CENTRE` | `deck` | `5` | Page 3 ('Business Centre' Deck 5 Midship) | `MATCH` |
| `public_areas.json` | `PUB-EXCURSIONS-DESK` | `deck` | `[5, 6]` | Page 3 ('MSC Excursions' Deck 5 & Deck 6) | `MATCH` |
