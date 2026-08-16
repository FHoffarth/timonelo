---
status: Approved (Operational Standard)
version: 1.0.0
authority: Timonelo Cartography & Knowledge Factory
applies_to: MSC Bellissima (IMO 9766205) & Meraviglia Class Sister Ships
last_updated: 2026-08-16
---

# MSC Bellissima Numbering & Stateroom Taxonomy
### Authoritative Spatial Breakdown for Industrial-Scale Ontology Generation

---

## 1. Numbering Architecture & Maritime Conventions

The stateroom numbering system of **MSC Bellissima (Chantiers de l'Atlantique, Hull B34)** follows rigorous naval architectural rules across its 2,217 staterooms and 14 passenger decks.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STATEROOM NUMBER ANATOMY                              │
│                                                                             │
│      [ DECK PREFIX ]      [ CORRIDOR RANGE ]      [ HULL SIDE PARITY ]      │
│        (1 or 2 digits)       (2 digits: 00-24)        (Last digit: 0-9)     │
│             │                       │                        │              │
│             ▼                       ▼                        ▼              │
│            1 4                     1 2                      2               │
│        Deck 14 (Girasole)    Aft Corridor Station      Even = Starboard     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Parity Law
* **Even Last Digit ($0, 2, 4, 6, 8$)**: **Starboard Side (Right / Tribord)**
* **Odd Last Digit ($1, 3, 5, 7, 9$)**: **Port Side (Left / Bâbord)**
* **Centerline Interiors**: Arranged in central blocks, adopting the parity of the corridor branch they open onto.

---

## 2. Longitudinal Corridor Stations ($X \in [0.0, 1.0]$)

Staterooms are distributed along three primary longitudinal circulation zones:

| Stateroom Range | Longitudinal Station ($X$) | Zone Classification | Nearest Elevator Lobby |
| :--- | :--- | :--- | :--- |
| **`xx001` – `xx045`** | $X \in [0.72, 0.90]$ | **Forward (Bow)** | `CORE_FWD` (Forward Lift) |
| **`xx046` – `xx140`** | $X \in [0.42, 0.71]$ | **Midship** | `CORE_MID` (Central Atrium Lift) |
| **`xx141` – `xx250`** | $X \in [0.15, 0.41]$ | **Aft (Stern)** | `CORE_AFT` (Aft Lift) |

---

## 3. Stateroom Category Archetypes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARCHETYPE CLASSIFICATION MATRIX                     │
├──────┬───────────────────────────┬─────────┬──────────────┬─────────────────┤
│ CODE │ CATEGORY NAME             │ AREA    │ BALCONY TYPE │ SIGHTLINE ANGLE │
├──────┼───────────────────────────┼─────────┼──────────────┼─────────────────┤
│ BA   │ Deluxe Balcony            │ 19.0 m² │ Unobstructed │ 180° Horizon    │
│ BR1  │ Deluxe Balcony (Midship)  │ 19.0 m² │ Unobstructed │ 180° Horizon    │
│ OB   │ Balcony (Lifeboat Tier)   │ 19.0 m² │ Partial Obstr│ 120° Horizon    │
│ OL1  │ Premium Oceanview (Deck 8)│ 22.0 m² │ No Balcony   │ Sealed Window   │
│ IR1  │ Deluxe Interior           │ 16.0 m² │ No Balcony   │ None            │
│ BA_H │ Certified Accessible      │ 28.0 m² │ Unobstructed │ 180° (950mm Dr) │
│ SL1  │ Premium Suite Aurea       │ 27.0 m² │ Large Balcony│ 180° Extended   │
│ SLD  │ Duplex Suite Whirlpool    │ 59.0 m² │ Private Spa  │ 180° Two-Deck   │
│ YC1  │ Yacht Club Deluxe Suite   │ 28.0 m² │ YC Dedicated │ 180° Forward    │
│ YIN  │ Yacht Club Interior       │ 16.0 m² │ No Balcony   │ None            │
│ YCP  │ Yacht Club Royal Suite    │ 58.0 m² │ 33m² Balcony │ 180° Panoramic  │
└──────┴───────────────────────────┴─────────┴──────────────┴─────────────────┘
```

---

## 4. Deck-by-Deck Capacity & Archetype Distribution

* **Deck 08 (Camellia - 21.0m)**: 312 Staterooms (Lifeboat Level, Balconies with partial obstruction `OB`, Oceanview `OL1`, Interiors `IR1`, Accessible `BA_H`).
* **Deck 09 (Magnolia - 24.5m)**: 348 Staterooms (Deluxe Balconies `BA/BR1`, Duplex Suites Lower `SLD`, Interiors `IR1`).
* **Deck 10 (Mirto - 28.0m)**: 356 Staterooms (Deluxe Balconies `BA/BR1`, Duplex Suites Upper `SLD`, Interiors `IR1`).
* **Deck 11 (Ortensia - 31.5m)**: 356 Staterooms (Deluxe Balconies `BA/BR1`, Interiors `IR1`, Accessible `BA_H`).
* **Deck 12 (Rosa - 35.0m)**: 352 Staterooms (Deluxe Balconies `BA/BR1`, Duplex Suites Lower `SLD`, Interiors `IR1`).
* **Deck 13 (Ciclamino - 38.5m)**: 348 Staterooms (Deluxe Balconies `BA/BR1`, Duplex Suites Upper `SLD`, Interiors `IR1`).
* **Deck 14 (Girasole - 42.0m)**: 318 Staterooms (Directly beneath Deck 15 Lido/Buffet, Deluxe Balconies `BA`, Yacht Club Suites Forward `YC1`).
* **Decks 15, 16, 18 (Yacht Club Enclave)**: 95 Yacht Club Exclusive Suites (`YC1`, `YIN`, `YCP` Royal Suites).

**Total Vessel Capacity**: **2,217 Staterooms**.

---

## 5. Connecting Stateroom Pair Rules

Adjoining staterooms share an internal sound-insulated acoustic door. Connecting staterooms are defined in deterministic adjacent pairs:
* Starboard pairs: `(xx090, xx092)`, `(xx120, xx122)`, `(xx180, xx182)`
* Port pairs: `(xx089, xx091)`, `(xx119, xx121)`, `(xx179, xx181)`
* An adjoining stateroom's `connecting_cabin_number` points mutually to its pair.
