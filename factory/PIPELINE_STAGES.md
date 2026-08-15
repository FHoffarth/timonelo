# Knowledge Factory Pipeline Stages (Stages 01–08)
### Detailed Engineering Specifications for the Timonelo Compilation Pipeline

---

# STAGE 01: EVIDENCE INTAKE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 01: EVIDENCE INTAKE                          │
│                                                                             │
│  [ RAW INPUTS ] ──► [ SOURCE REGISTRATION ] ──► [ CHECKSUM & SANITIZATION ] │
│  (GA Blueprints,                                     │                      │
│   Manifests,                                         ▼                      │
│   Survey Photos)                           [ INGESTION BATCH ]              │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Ingests, registers, hashes, and stores raw primary source materials from shipyards, cruise operators, and field survey teams.
* **Inputs**:
  - Raw General Arrangement (GA) vector/raster blueprints (PDF, DXF, DWG, SVG).
  - Operator cabin manifest tables (CSV, JSON, XLSX).
  - Field survey photography files with EXIF metadata (JPEG, PNG, RAW).
  - Vessel IMO number and source attribution manifest.
* **Outputs**:
  - `RawEvidenceBatch`: Cryptographically hashed container storing source artifacts with assigned `source_id`s and immutable timestamps.
* **Validation**:
  - Cryptographic checksum verification (SHA-256) on every file.
  - File format validation against allowed MIME types.
  - IMO number validity check against global maritime registry.
* **Failure Conditions**:
  - Checksum mismatch or corrupted binary payloads.
  - Missing mandatory attribution metadata (author, access date, license type).
  - Unrecognized or unsupported file formats.
* **Quality Gates**:
  - **Gate 1.1 (Source Integrity)**: 100% of files in batch possess valid SHA-256 hashes and license descriptors.

---

# STAGE 02: NORMALIZATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 02: NORMALIZATION                            │
│                                                                             │
│  [ INGESTION BATCH ] ──► [ OPTICAL CALIBRATION ] ──► [ COORDINATE MAPPING ] │
│                                                              │              │
│                                                              ▼              │
│                                                    [ NORMALIZED SHIP DRAFT ]│
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Translates raw blueprints and cabin manifests into a unified, vessel-relative Cartesian coordinate space ($X \in [0.0, 1.0]$, $Y \in [-1.0, 1.0]$, $Z \in \text{Deck Tier}$).
* **Inputs**:
  - `RawEvidenceBatch` from Stage 01.
  - Physical vessel dimensions (Length Overall $LOA$, Beam, Draft).
* **Outputs**:
  - `NormalizedShipDraft`: Geometric entities representing deck boundaries, cabin perimeter polygons, corridor graph centerlines, and door coordinates in normalized floating-point space.
* **Validation**:
  - Optical aspect-ratio calibration: Verifies that blueprint length-to-beam ratio matches official naval architecture records within $\pm 0.5\%$.
  - Polygon closure: Verifies all staterooms and venue boundaries form closed, non-self-intersecting polylines.
* **Failure Conditions**:
  - Blueprint scale distortion exceeds calibration tolerance.
  - Self-intersecting polygons or open geometric contours.
  - Cabin numbers failing to conform to string validation specs.
* **Quality Gates**:
  - **Gate 2.1 (Geometric Normalization)**: 100% of polygons normalize cleanly into the unit box without out-of-bounds coordinate points.

---

# STAGE 03: ARCHETYPE MATCHING

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STAGE 03: ARCHETYPE MATCHING                          │
│                                                                             │
│  [ NORMALIZED DRAFT ] ──► [ ARCHETYPE REGISTRY ] ──► [ GEOMETRY INHERIT ]   │
│                                                             │               │
│                                                             ▼               │
│                                                   [ BASELINE COMPOSITE ]    │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Compares the normalized vessel draft against the Master Archetype Registry to bind shared sister-ship geometries, stateroom module templates, and elevator core configurations.
* **Inputs**:
  - `NormalizedShipDraft` from Stage 02.
  - Master Archetype Registry records (`ARCH-*`).
* **Outputs**:
  - `ArchetypeBoundVessel`: Composite model combining inherited class-level baseline geometry ($80\text{--}90\%$) with vessel-specific source overlays.
* **Validation**:
  - Structural alignment check: Superimposes the vessel's hull perimeter over the master archetype template to calculate geometric similarity score.
* **Failure Conditions**:
  - Archetype binding requested for non-existent archetype ID.
  - Structural divergence from master archetype exceeds maximum class variance threshold ($>25\%$ layout mutation).
* **Quality Gates**:
  - **Gate 3.1 (Archetype Alignment)**: Archetype reuse ratio ($ARR$) calculated and logged; baseline geometries inherited cleanly.

---

# STAGE 04: SHIP DELTA DETECTION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STAGE 04: SHIP DELTA DETECTION                         │
│                                                                             │
│  [ BASELINE COMPOSITE ] ──► [ DIFFERENTIAL SCAN ] ──► [ MUTATION LEDGER ]   │
│                                                              │              │
│                                                              ▼              │
│                                                   [ RECONCILED VESSEL MODEL]│
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Isolates vessel-specific physical modifications, drydock mutations, cabin renumbering, or venue substitutions from the master archetype.
* **Inputs**:
  - `ArchetypeBoundVessel` from Stage 03.
  - Direct vessel evidence layers from Stage 01.
* **Outputs**:
  - `ReconciledVesselModel`: Complete vessel representation with an explicit `MutationLedger` detailing every added, modified, or deprecated spatial polygon.
* **Validation**:
  - Spatial delta verification: Confirms that modified cabin polygons do not overlap unchanged archetype polygons.
  - Category consistency: Validates that operator-specific cabin categories map to valid physical layouts.
* **Failure Conditions**:
  - Unresolved collisions between inherited archetype structures and ship-specific deltas.
  - Missing cabin numbers present in the manifest but absent from the vectorized deck plan.
* **Quality Gates**:
  - **Gate 4.1 (Delta Reconciliation)**: Zero unindexed cabins; 100% of manifest cabins reconciled against physical polygons.

---

# STAGE 05: KNOWLEDGE PACK GENERATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STAGE 05: KNOWLEDGE PACK GENERATION                       │
│                                                                             │
│  [ RECONCILED MODEL ] ──► [ CANONICAL COMPILER ] ──► [ JSON PACK ARTIFACT ] │
│                                                             │               │
│                                                             ▼               │
│                                                   [ CANDIDATE PACK ]        │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Compiles the reconciled spatial model, evidence references, claims, and limitations into the canonical `knowledge-pack.json` schema.
* **Inputs**:
  - `ReconciledVesselModel` from Stage 04.
  - Compiler derivation rules (motion profile rules, acoustic adjacency rules).
* **Outputs**:
  - `CandidateKnowledgePack`: Unsealed, fully structured JSON data artifact conforming to `src/timonelo/knowledge_pack`.
* **Validation**:
  - Schema self-validation: Validates candidate JSON against the canonical Knowledge Pack Pydantic/JSON Schema.
  - Referential integrity: Confirms all entity IDs (`cabin:`, `deck:`, `venue:`, `source:`, `claim:`) resolve without broken pointers.
* **Failure Conditions**:
  - JSON schema validation errors.
  - Orphan claims referencing non-existent entities or missing source IDs.
* **Quality Gates**:
  - **Gate 5.1 (Schema Conformance)**: 100% schema validation pass with zero unreferenced entity identifiers.

---

# STAGE 06: SPATIAL VALIDATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STAGE 06: SPATIAL VALIDATION                         │
│                                                                             │
│  [ CANDIDATE PACK ] ──► [ TOPOLOGICAL LINTING ] ──► [ GRAPH CONNECTIVITY ]  │
│                                                             │               │
│                                                             ▼               │
│                                                   [ SPATIALLY VERIFIED PACK]│
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Performs rigorous mathematical and topological auditing on the spatial and graph integrity of the vessel.
* **Inputs**:
  - `CandidateKnowledgePack` from Stage 05.
* **Outputs**:
  - `SpatiallyVerifiedPack`: Pack annotated with validated spatial audit tokens.
* **Validation**:
  - **Polygon Collision Audit**: Computes intersection matrix between all adjacent cabin polygons on every deck; collision area must equal $0.00\ m^2$.
  - **Corridor Snapping Audit**: Every stateroom door coordinate must intersect a walkable corridor circulation graph node within $1.5\text{ meters}$.
  - **Vertical Core Alignment**: Validates that elevator shafts and stairwell nodes align vertically across contiguous deck planes.
* **Failure Conditions**:
  - Overlapping cabin polygons or intersecting structural bulkheads.
  - "Orphan cabins" whose doors cannot calculate a walkable route to an elevator or stairwell.
* **Quality Gates**:
  - **Gate 6.1 (Spatial Topology)**: Zero polygon collisions, zero disconnected doors, 100% vertical shaft alignment.

---

# STAGE 07: EXPERIENCE VALIDATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STAGE 07: EXPERIENCE VALIDATION                        │
│                                                                             │
│  [ SPATIALLY VERIFIED ] ──► [ SANDWICH AUDIT ] ──► [ SIGHTLINE RAYCAST ]    │
│                                                             │               │
│                                                             ▼               │
│                                                   [ AUDITED KNOWLEDGE PACK] │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Verifies that human-centric spatial truths (overhead noise sandwich, balcony obstruction raycasts, bed placement, electrical specs) meet canonical evidence thresholds.
* **Inputs**:
  - `SpatiallyVerifiedPack` from Stage 06.
* **Outputs**:
  - `AuditedKnowledgePack`: Knowledge Pack certified with an Experience Ready score ($ER\%$).
* **Validation**:
  - **Overhead Sandwich Audit**: 100% of residential staterooms must possess a computed ceiling adjacency entity on $Deck_{N+1}$ and floor adjacency on $Deck_{N-1}$.
  - **Obstruction Truth Audit**: Balconies marked "Unobstructed" must possess line-of-sight raycasts confirming zero intersection with lifeboat davits.
  - **Unknown Honesty Audit**: Confirms that missing socket configurations or unverified bed positions are explicitly marked `unknown` rather than populated with default fallback values.
* **Failure Conditions**:
  - Euphemistic or unbacked obstruction claims.
  - Missing overhead sandwich mapping on residential deck tiers.
* **Quality Gates**:
  - **Gate 7.1 (Experience Integrity)**: Experience Ready score $\ge 90.0\%$; zero unbacked claims.

---

# STAGE 08: PUBLICATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGE 08: PUBLICATION                              │
│                                                                             │
│  [ AUDITED PACK ] ──► [ CRYPTOGRAPHIC SEAL ] ──► [ EDGE DISTRIBUTION ]      │
│                                                             │               │
│                                                             ▼               │
│                                                   [ PUBLISHED / LIVE PACK ] │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Purpose**: Digitally signs, seals, compresses, and publishes the immutable Knowledge Pack to production distribution endpoints.
* **Inputs**:
  - `AuditedKnowledgePack` from Stage 07.
  - Release channel configuration (`staging` vs. `production`).
* **Outputs**:
  - `SealedKnowledgePack` (`knowledge-pack.json` & `.pack.json` asset).
  - Release manifest record in the Fleet Registry.
* **Validation**:
  - Cryptographic signature generation and checksum recording.
  - Compression ratio verification ($\le 5\text{ MB}$ typical target).
* **Failure Conditions**:
  - Checksum or signature generation failure.
  - CDN deployment verification timeout or asset corruption.
* **Quality Gates**:
  - **Gate 8.1 (Production Release)**: Immutable release artifact generated, signed, and serving with $200\text{ OK}$ response from distribution CDN.
