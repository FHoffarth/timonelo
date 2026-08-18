# P3.1 Geometry Validation & Provenance Audit Report

**Target Dataset**: `geometry/*.geometry.json` (Decks 4 to 19)  
**Primary Ground Truth**: `Official MSC Bellissima Deck Plan (11.2025 DEU)`  
**Total Evaluated Spatial Entities**: `2113`  

## 1. Epistemic Provenance Classification by Attribute

In accordance with epistemic governance, all hardcoded `1.0` confidence scores have been replaced by provenance-weighted scoring:

| Spatial Geometry Field | `DIRECT` (Confidence = 1.0) | `DERIVED` (Confidence < 1.0) | `UNKNOWN` (Value = `null`) | Epistemic Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **`polygon`** | **2113** | 0 | 0 | Directly extracted from 2D vector boundaries & text placement |
| **`centroid`** | 0 | **2113** | 0 | Mathematically calculated from polygon coordinates |
| **`bounding_box`** | 0 | **2113** | 0 | Computed spatial envelope `(min_x, min_y, width, height)` |
| **`orientation`** | **65** | **2048** | 0 | Directly observable for structural cores/venues; derived for corridors |
| **`door_position`** | **65** | 0 | **2048** | Visible for lift portals & venues; set to `null` (`UNKNOWN`) for staterooms where individual swing arcs are unprinted |
| **`adjacent_objects`** | 0 | **2113** | 0 | Calculated from spatial adjacency graph traversal |

---

## 2. Confidence Distribution by Deck

| Deck | Name | Entity Count | Mean Epistemic Confidence | Schema Status |
| :--- | :--- | :---: | :---: | :--- |
| **Deck 4** | Lirica | 6 | `0.947` | `VALID (Draft 2020-12)` |
| **Deck 5** | Opera | 117 | `0.884` | `VALID (Draft 2020-12)` |
| **Deck 6** | Musica | 7 | `0.949` | `VALID (Draft 2020-12)` |
| **Deck 7** | Fantasia | 8 | `0.94` | `VALID (Draft 2020-12)` |
| **Deck 8** | Meraviglia | 242 | `0.882` | `VALID (Draft 2020-12)` |
| **Deck 9** | Seaside | 265 | `0.882` | `VALID (Draft 2020-12)` |
| **Deck 10** | Seaside Evo | 297 | `0.881` | `VALID (Draft 2020-12)` |
| **Deck 11** | Bellissima | 293 | `0.881` | `VALID (Draft 2020-12)` |
| **Deck 12** | Grandiosa | 280 | `0.881` | `VALID (Draft 2020-12)` |
| **Deck 13** | Magnifica | 278 | `0.881` | `VALID (Draft 2020-12)` |
| **Deck 14** | World Class | 238 | `0.882` | `VALID (Draft 2020-12)` |
| **Deck 15** | Preziosa | 27 | `0.898` | `VALID (Draft 2020-12)` |
| **Deck 16** | Seaview | 25 | `0.899` | `VALID (Draft 2020-12)` |
| **Deck 18** | Divina | 24 | `0.897` | `VALID (Draft 2020-12)` |
| **Deck 19** | Splendida | 6 | `0.947` | `VALID (Draft 2020-12)` |

---

## 3. Epistemic Rules Compliance Verification

- ✅ **No hardcoded 1.0**: Every entity confidence score is computed dynamically based on attribute-level provenance.
- ✅ **Unknowns explicitly mapped to `null`**: Unverified door positions are stored as `null` rather than estimated coordinates.
- ✅ **Knowledge & Graph unmutated**: `knowledge/` and `data/` graphs remain untouched; provenance updates are strictly confined to `geometry/`.
- ✅ **Schema Validated**: All 15 files conform to `deck_geometry.schema.json`.