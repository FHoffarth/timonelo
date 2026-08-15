---
status: Approved (Platform Specification)
version: 1.0.0
authority: Chief Fleet Architect of Timonelo
applies_to: Timonelo Knowledge Factory Multi-Vessel Patch System
last_updated: 2026-08-16
---

# Timonelo Ship Patch Specification (SPEC-008)
### Non-Destructive Delta Compilation for Fleet-Scale Spatial Twin Inheritance

---

## 1. Purpose & Architectural Principles

The **Timonelo Ship Patch System** enables derivative vessels to inherit the entire spatial stack (geometry, topology, calculus, lenses) from a reference vessel without modifying the baseline codebase.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SHIP PATCH PIPELINE FLOW                              │
│                                                                             │
│   [ Reference Vessel Ontology ] ── (Immutable Base: Bellissima v1.0)        │
│                 │                                                           │
│                 ▼                                                           │
│   [ Patch Engine (SPEC-008) ]   ── Ingests deltas.json                      │
│                 │                                                           │
│                 ├── Op 1: RENAME_VENUE                                      │
│                 ├── Op 2: REPLACE_VENUE                                     │
│                 ├── Op 3: MUTATE_STATEROOM_CATEGORY                         │
│                 ├── Op 4: ADD_LONGITUDINAL_STATION                          │
│                 └── Op 5: OVERRIDE_NOISE_PROFILE                            │
│                 │                                                           │
│                 ▼                                                           │
│   [ 4-Gate Quality Validator ]  ── Enforces 100% Zero-Orphan Topology       │
│                 │                                                           │
│                 ▼                                                           │
│   [ Output: Derivative Twin ]   ── (e.g. MSC Meraviglia / MSC Grandiosa)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Invariants:
1. **Immutability of Baseline**: A patch must NEVER alter the reference vessel in-memory or on disk.
2. **Determinism**: Applying patch $P$ to baseline $B$ produces the exact same derivative twin $D = B \oplus P$ across all environments.
3. **Atomic Validation**: If any patch operation violates a Quality Gate (e.g. creating an orphaned door), the entire patch transaction is rolled back.

---

## 2. Patch Operator Taxonomy

```
┌─────────────────────────────┬────────────────────────────────────────────────────────────┐
│ OPERATOR                    │ PURPOSE & BEHAVIOR                                         │
├─────────────────────────────┼────────────────────────────────────────────────────────────┤
│ `RENAME_VENUE`              │ Updates human-readable venue name & signage.               │
│ `REPLACE_VENUE`             │ Replaces concept, category, noise profile & access nodes.  │
│ `MUTATE_POLYGON`            │ Modifies boundary coordinates without altering door snaps. │
│ `MUTATE_STATEROOM_CATEGORY` │ Changes category code, socket matrix, or balcony type.     │
│ `ADD_CABIN_RANGE`           │ Inserts new staterooms along a specified corridor station. │
│ `REMOVE_CABIN_RANGE`        │ Removes staterooms and cleanly detaches door nodes.        │
│ `EXTEND_CORRIDOR_SPINE`     │ Adds longitudinal stations for stretched hull classes.     │
│ `OVERRIDE_NOISE_PROFILE`    │ Adjusts acoustic noise generator flags for venues.         │
└─────────────────────────────┴────────────────────────────────────────────────────────────┘
```

---

## 3. JSON Patch Schema (`deltas.json`)

```json
{
  "$schema": "https://timonelo.org/schemas/ship-patch-v1.json",
  "patch_version": "1.0.0",
  "target_imo": "9647710",
  "target_name": "MSC Meraviglia",
  "base_vessel_imo": "9766205",
  "base_vessel_name": "MSC Bellissima",
  "operations": [
    {
      "op": "RENAME_VENUE",
      "deck": 6,
      "venue_id": "VENUE_THEATER",
      "new_name": "Broadway Theatre (Lower Level)"
    },
    {
      "op": "RENAME_VENUE",
      "deck": 7,
      "venue_id": "VENUE_THEATER_UPPER",
      "new_name": "Broadway Theatre (Balcony Level)"
    },
    {
      "op": "REPLACE_VENUE",
      "deck": 6,
      "venue_id": "VENUE_HOLA_TAPAS",
      "replacement": {
        "venue_id": "VENUE_EATALY",
        "name": "Eataly Ristorante Italiano & Market",
        "category": "DINING",
        "is_noise_generator": false,
        "is_open_deck": false
      }
    },
    {
      "op": "RENAME_VENUE",
      "deck": 6,
      "venue_id": "VENUE_PROMENADE",
      "new_name": "Galleria Meraviglia (80m LED Dome)"
    }
  ]
}
```

---

## 4. Conflict Detection & Resolution Matrix

```
┌───────────────────────────────┬────────────────────────────────────────────────────────────┐
│ CONFLICT SCENARIO             │ RESOLUTION POLICY                                          │
├───────────────────────────────┼────────────────────────────────────────────────────────────┤
│ Target Venue ID Not Found     │ HARD ERROR: Abort compilation with missing locator alert.  │
│ Stateroom Parity Violation    │ HARD ERROR: Reject patch if even number assigned to port.  │
│ Orphaned Door Created         │ HARD ERROR: Reverted by Gate 2 Topological Validator.      │
│ Overlapping Venue Polygon     │ WARNING + RAYCAST CLIPPING: Trim boundaries at centerline. │
└───────────────────────────────┴────────────────────────────────────────────────────────────┘
```

---

## 5. Versioning & Future Compatibility

* **Patch Compatibility Guarantee**: A patch authored for Baseline `v1.x` will remain valid across all minor and patch updates of the reference vessel.
* **Semantic Tagging**: Patches are cryptographically signed with the SHA-256 hash of the baseline `knowledge-pack.json`.
