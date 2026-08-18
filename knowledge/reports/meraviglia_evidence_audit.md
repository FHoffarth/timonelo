# MSC Meraviglia Evidence Audit

**Repository**: `Timonelo`  
**Audit Branch**: `audit/meraviglia-evidence-truth`  
**Target Commit**: `0ef5a21`  
**Auditor**: Independent Epistemic Integrity Auditor  
**Date**: 2026-08-18  

---

## Executive Verdict

# ❌ `EVIDENCE GATE BLOCKED`

**Summary**:  
The MSC Meraviglia ingestion delivered in commit `0ef5a21` does **not** satisfy Timonelo's epistemic evidence-first standards. While the JSON files are 100% syntactically valid against JSON Schema (Draft 2020-12) and Python unit tests pass, the ingestion is **fundamentally synthetic and ungrounded in physical source evidence**:
1. **No Source Artifact**: No physical PDF, blueprint, or GA plan exists in the repository for MSC Meraviglia. The cited SHA-256 hash is a synthetic placeholder.
2. **Synthetic Geometry**: All 2,148 spatial geometry polygons across 15 decks were generated algorithmically via mathematical coordinate loops (`cx = 120 + (c_idx // 2) * 5.2`), yet falsely marked as `"polygon": "DIRECT"`.
3. **Unreproducible Metric**: The claimed `99.4% Epistemic Knowledge Coverage` is a hardcoded string in the report generator with no mathematical backing.
4. **Ungrounded Graph**: The relationship graph contains only high-level summary counters, not actual verified W3C BOT spatial topology triples.

---

## 1. Source Artifact Verification

| Parameter | Stated in Commit `0ef5a21` | Actual Audit Finding | Verification Status |
| :--- | :--- | :--- | :--- |
| **Artifact Name** | `MSC Meraviglia Official Deck Plans & Builder Specifications (Edition 2025/2026)` | No file with this name exists in repo or brain storage | **FAIL / NOT AVAILABLE** |
| **File Type** | PDF / Vector GA Drawing | Missing | **FAIL** |
| **Publisher** | Chantiers de l'Atlantique & MSC Cruises S.A. | Unverified | **UNVERIFIED** |
| **File Path** | Not specified / Implicit | File not found anywhere on disk | **FAIL** |
| **SHA-256 Hash** | `9a71b283c4e512d109f8721a34bc0981e271409283741029c782109283741029` | Synthetic placeholder hash; no file matches this hash | **FAIL / SYNTHETIC HASH** |
| **Page Count** | Referenced as Pages 2, 3, 4, 5 | Cannot be inspected (artifact missing) | **UNVERIFIABLE** |

---

## 2. Fact-Level Provenance Findings

| Domain | Entity & Field | Stated Value | Stated Source / Provenance | Forensic Status | Finding Details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Technical** | `technical.json:imo_number` | `9760512` | `MSC_MER_GA` | `INFERRED` | Correct factual IMO from public domain, but ungrounded in local primary evidence. |
| **Technical** | `technical.json:tonnage_gt` | `171598` | `MSC_MER_GA` | `INFERRED` | Correct shipyard gross tonnage, but no verified document attached. |
| **Technical** | `technical.json:total_cabins_max` | `2244` | `MSC_MER_GA` | `INFERRED` | Public marketing cabin count; not verified against physical cabin numbering schedule. |
| **Technical** | `technical.json:max_passengers` | `5714` | `MSC_MER_GA` | `INFERRED` | Maximum safety certificate capacity; unverified against active SOLAS certificate. |
| **Decks** | `decks.json:DECK-04..19` | 15 Decks, skips 17 | `MSC-MER-GA-DECK*` | `INFERRED` | Deck names (*Corallo, Colosseo, Petra...*) match general ship knowledge, but deck plans not audited. |
| **Dining** | `restaurants.json:RES-WAVES` | Waves Restaurant (D5) | `MSC-MER-RES-WAVES` | `INFERRED` | Venue name matches MSC Meraviglia, but deck layout ungrounded. |
| **Dining** | `restaurants.json:RES-PANORAMA` | Panorama Restaurant (D6) | `MSC-MER-RES-PANORAMA` | `INFERRED` | Venue placement matches Meraviglia class. |
| **Dining** | `restaurants.json:RES-HOLA-TAPAS`| HOLA! Tapas Bar (D6) | `MSC-MER-RES-HOLATAPAS` | `INFERRED` | Installed during refit; unverified whether currently active or legacy Eataly. |
| **Bars** | `bars.json:BAR-EDGE` | Edge Cocktail Bar (D6) | `MSC-MER-BAR-EDGE` | `INFERRED` | Positioned at Atrium Mezzanine. |
| **Bars** | `bars.json:BAR-BRASS-ANCHOR` | Brass Anchor Pub (D7) | `MSC-MER-BAR-BRASSANCHOR` | `INFERRED` | Meraviglia features Brass Anchor (vs. Masters of the Sea on Bellissima). |
| **Entertainment**| `entertainment.json:ENT-BROADWAY`| Broadway Theatre (D5/6) | `MSC-MER-ENT-BROADWAY` | `INFERRED` | 985 seats stated. |
| **Entertainment**| `entertainment.json:ENT-CAROUSEL`| Carousel Lounge (D7) | `MSC-MER-ENT-CAROUSEL` | `INFERRED` | Aft circular lounge; seat count (413) inferred from class standard. |
| **Wellness** | `spa.json:SPA-AUREA` | MSC Aurea Spa (1100m²) | `MSC-MER-SPA-AUREA` | `INFERRED` | Area and facilities inferred from shipyard specification. |
| **Sports** | `sports.json:SPT-SPORTPLEX` | Sportplex Arena (D16) | `MSC-MER-SPT-SPORTPLEX` | `INFERRED` | Multi-sport hall. |
| **Pools** | `pools.json:POOL-ATMOSPHERE` | Atmosphere Main Pool (D15)| `MSC-MER-POOL-ATMOSPHERE` | `INFERRED` | Main lido pool. |

---

## 3. Geometry Forensics Findings

| Audited Deck | Object Type | Coordinate Source | Transformation Method | Claimed Provenance | True Provenance | Epistemic Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deck 04** | Lift Cores A/B/C/YC | Hardcoded `[180, 400, 620, 220]` | None (Synthetic loop) | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 04** | Corridors | Hardcoded `[100, 85]` & `[100, 145]` | None (Synthetic loop) | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 05** | Cabins 5001–5114 | `cx = 120 + (c_idx // 2) * 5.2` | Linear grid math | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 08** | Cabins 8001–8240 | `cx = 120 + (c_idx // 2) * 5.2` | Linear grid math | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 10** | Cabins 10001–10300 | `cx = 120 + (c_idx // 2) * 5.2` | Linear grid math | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 14** | Cabins 14001–14242 | `cx = 120 + (c_idx // 2) * 5.2` | Linear grid math | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **Deck 15** | Pool & Buffet Zones | Synthetic bounding box `800x250` | None | `DIRECT` | `SYNTHETIC_GEOMETRY` | **MISREPRESENTED** |
| **All Decks** | Door Positions | `None` / `null` | N/A | `UNKNOWN` | `UNKNOWN` | Correctly `null` |

### Forensic Analysis of Coordinate Generation:
Inspection of `scripts/ingest_msc_meraviglia.py` demonstrates that geometry coordinates were **not extracted from vector blueprints or scanned raster deck plans**. Instead, lines 1120–1210 utilize a synthetic template generator:
```python
cx = 120 + (c_idx // 2) * 5.2
cy = 50 if is_port else 155
polygon = [[cx, cy], [cx+4.8, cy], [cx+4.8, cy+32], [cx, cy+32]]
```
Labeling these programmatic grid boxes with `"polygon": "DIRECT"` is a critical provenance violation.

---

## 4. Coverage Metric Audit

- **Claimed Metric**: `99.4% Global Epistemic Knowledge Coverage`
- **Formula & Computation**: In `scripts/ingest_msc_meraviglia.py`, the number `99.4%` was written as a static string into the report markdown. There is **no mathematical computation, no ratio of verified vs. total attributes, and no uncertainty weighting**.
- **Audit Verdict**: **FAIL / METRIC NOT REPRODUCIBLE**

---

## 5. Conflict Detection Findings

- **Claimed Finding**: `0 Conflicts Detected, 0 Silent Overwrites`
- **Audit Finding**: `ConflictResolver.ts` and `KnowledgeDiff.ts` were **bypassed**. The script directly created new JSON files in an empty target directory without executing a comparative diff against existing shipyard records or conflicting sources.
- **Audit Verdict**: **CONFLICT DETECTION NOT IMPLEMENTED / NOT DEMONSTRATED**

---

## 6. Graph Provenance Findings

- **Claimed Structure**: `2,342 W3C BOT Semantic Spaces`
- **Audit Finding**: `graph.json` contains only a shallow metadata container:
  ```json
  {
    "total_spaces": 2342,
    "relations_summary": {
      "adjacent_overhead_count": 2244,
      "adjacent_underfoot_count": 2244
    }
  }
  ```
  It does **not** contain individual RDF triples, explicit topological adjacency edges (`bot:adjacentElement`, `bot:hasStorey`), or cabin-to-venue vertical raycasts.
- **Audit Verdict**: **SYNTHETIC & UNVERIFIABLE GRAPH**

---

## 7. Governance Findings

- In `meraviglia_publish_report.md`, the publishing entity was named `Bridge Officer Tim`.
- Under Timonelo's system architecture, **Bridge Officer Tim is an intelligent user-facing navigator and explanation orchestrator**, not an authoritative data publisher or release certifier.
- Publishing authority must reside with verified cryptographic hash chains and automated Evidence Gate validators.

---

## 8. Critical Findings Matrix

| Finding ID | Severity | Category | Description |
| :--- | :---: | :--- | :--- |
| **FIND-MER-001** | **P0** | **Evidence Basis** | Primary source PDF / GA blueprint is missing entirely from repository. SHA-256 hash is synthetic. |
| **FIND-MER-002** | **P0** | **Geometry Provenance** | Polygons are synthetically generated grid boxes falsely classified as `DIRECT` provenance. |
| **FIND-MER-003** | **P1** | **Metric Truth** | Claim of `99.4% Epistemic Coverage` is hardcoded and mathematically unreproducible. |
| **FIND-MER-004** | **P1** | **Graph Grounding** | `graph.json` is a summary stub lacking actual W3C BOT spatial triples. |
| **FIND-MER-005** | **P2** | **Conflict Bypass** | Ingestion bypassed `ConflictResolver.ts` and `KnowledgeDiff.ts`. |
| **FIND-MER-006** | **P3** | **Governance** | `Bridge Officer Tim` inappropriately cited as Publishing Authority. |

---

## 9. Trust Classification

| Layer / Component | Stated Status | Audited Status | Justification |
| :--- | :---: | :---: | :--- |
| **Knowledge Layer** | `VERIFIED` | **INFERRED (UNVERIFIED)** | Accurate domain facts, but no backing primary source artifact. |
| **Geometry Layer** | `DIRECT` | **SYNTHETIC (MISREPRESENTED)** | Generated by mathematical loop templates, not extracted. |
| **Semantic Graph** | `W3C BOT COMPLIANT` | **SYNTHETIC STUB** | Contains counters rather than queryable triples. |
| **Coverage Metrics** | `99.4%` | **UNREPRODUCIBLE** | Hardcoded string without algorithmic derivation. |
| **Publish Status** | `PUBLISHED` | **BLOCKED / UNPUBLISHED** | Fails Evidence Gate 1, 2, 3, and 4. |

---

## 10. Required Remediation

1. **Acquire Primary Source Artifact**: Ingest official, high-resolution MSC Meraviglia General Arrangement (GA) plans or official deck plan PDF with a genuine SHA-256 hash.
2. **Execute Vector Spatial Extraction**: Extract true polygon boundaries from raster/vector plans rather than generating synthetic grid offsets.
3. **Correct Provenance Classification**: Reclassify all non-extracted geometry as `SYNTHETIC_GEOMETRY` or `DERIVED` with realistic confidence scores ($\le 0.40$).
4. **Implement Dynamic Coverage Formula**: Compute Epistemic Coverage dynamically based on verified attribute counts divided by total schema properties.
5. **Generate True BOT Triples**: Populate `graph.json` with actual node and edge lists connecting specific staterooms and venues.
6. **Block Fleet Scaling**: MSC Grandiosa ingestion must remain blocked until the Knowledge Factory pipeline enforces physical artifact ingestion.

---

## 11. Final Declarations

1. **Is the Meraviglia ingestion evidence-based?** $\rightarrow$ **NO.** It is schema-valid but evidence-ungrounded.
2. **Are knowledge facts traceable to primary sources?** $\rightarrow$ **NO.** No local source artifact exists.
3. **Are geometry polygons extracted from official plans?** $\rightarrow$ **NO.** They are generated by a mathematical formula.
4. **Which geometry parts are synthetic?** $\rightarrow$ **100% of all cabins, lift cores, corridors, and venues.**
5. **Is `DIRECT` correctly used?** $\rightarrow$ **NO. It is mislabeled.**
6. **Is 99.4% coverage reproducible?** $\rightarrow$ **NO. It is hardcoded.**
7. **Is "0 conflicts" proven?** $\rightarrow$ **NO. Conflict detection was bypassed.**
8. **Is the graph evidence-backed?** $\rightarrow$ **NO. It is a synthetic counter summary.**
9. **May MSC Meraviglia be considered canonical/published?** $\rightarrow$ **NO. Status is reverted to BLOCKED / UNVERIFIED.**
10. **May the Knowledge Factory scale to MSC Grandiosa now?** $\rightarrow$ **NO. Strict block until Evidence Gate pipeline is enforced.**
