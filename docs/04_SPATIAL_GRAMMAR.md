# 04_SPATIAL_GRAMMAR — The Living Deck Topological Engine

## 1. The Tube Map Paradigm

The **Living Deck** is **NOT** a visual CAD floor plan or a raster PDF drawing.

It is a **Semantic Spatial Knowledge Graph** structured around the **Passenger’s Mental Model** of navigating a modern cruise vessel (analogous to the London Underground diagram).

```
                             [ PORT (Odd Numbers / Sea View) ↑ ]
 ┌─BOW WEDGE──────────────────────────────────────────────────────────────────────STERN TRANSOM─┐
 │ ┌─────────┐                                                                     ┌──────────┐  │
 │ │Track 1  │───[Port Outer Track: Balconies & Ocean Views (Odd: 14005, 14007...)]─│Aft Wake  │  │
 │ │Bow      │                                                                     │Balconies │  │
 │ │Suites   │───[Track 2: Port Inner Track: Interior Hallway (Odd: 14089, 14091...)]──│& Suites  │  │
 │ └─────────┘    ┌─────────────┐        ┌──────────────┐        ┌─────────────┐   └──────────┘  │
 │                │ LIFT CORE A │        │ MIDSHIP VOID │        │ LIFT CORE B │                 │
 │                │ 6 Elevators │        │Panoramic Core│        │ 4 Elevators │                 │
 │                │   & Stairs  │        │& Atrium View │        │  & Service  │                 │
 │ ┌─────────┐    └─────────────┘        └──────────────┘        └─────────────┘   ┌──────────┐  │
 │ │Bow      │───[Track 3: Starboard Inner Track: Interior (Even: 14088, 14090...)]─│Aft Wake  │  │
 │ │Suites   │                                                                     │Balconies │  │
 │ │(Even)   │───[Track 4: Starboard Outer Track: Balconies (Even: 14006, 14008...)]│& Suites  │  │
 │ └─────────┘                                                                     └──────────┘  │
 └─BOW WEDGE──────────────────────────────────────────────────────────────────────STERN TRANSOM─┘
                          [ STARBOARD (Even Numbers / Sea View) ↓ ]
```

---

## 2. The 4 Parallel Longitudinal Tracks

1. **Track 1: Port Outer Track** (`PORT_OUTER`): Balconies and Ocean View staterooms with sea views on portside (Odd numbers).
2. **Track 2: Port Inner Track** (`PORT_INNER`): Interior staterooms facing the portside corridor (Odd numbers).
3. **Track 3: Starboard Inner Track** (`STARBOARD_INNER`): Interior staterooms facing the starboard corridor (Even numbers).
4. **Track 4: Starboard Outer Track** (`STARBOARD_OUTER`): Balconies and Ocean View staterooms on starboard (Even numbers).

---

## 3. Structural Skeleton & Vertical Transit

Cabins wrap around structural elevator cores rather than forming a monotonous spreadsheet:
- **Bow Wedge Cap**: Forward-facing suites and panoramic staterooms.
- **Forward Lift Core A**: 6 Elevators + Grand Staircase + Linen Riser connecting Decks 4–19.
- **Midship Void & Core**: Panoramic glass elevators overlooking the central multi-deck Galleria.
- **Aft Lift Core B**: 4 Elevators + Service Risers connecting Decks 5–18.
- **Stern Transom Cap**: Aft wake view staterooms and wraparound balconies.

---

## 4. Graph Adjacency Relations

Every stateroom node models 5 topological neighbors:
1. `adjacent_fore`: Door immediately ahead along the corridor run.
2. `adjacent_aft`: Door immediately behind along the corridor run.
3. `adjacent_across`: Door directly across the hallway (e.g. Balcony facing Interior).
4. `adjacent_overhead`: Structural zone on the deck directly above (e.g. Serene Staterooms vs. Buffet Kitchen).
5. `adjacent_underfoot`: Structural zone on the deck directly below (e.g. Serene Staterooms vs. Theatre).
