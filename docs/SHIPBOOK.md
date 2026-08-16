---
status: Approved (Operational Handbook)
version: 1.0.0
authority: Timonelo
owner: Maintainers & Cartography Operations
applies_to: All Ship Ingestion, Factory Compilation & Verification Pipelines
last_updated: 2026-08-16
---

# The Timonelo Shipbook
### How a Vessel Becomes Timonelo: The Permanent Operational Manual for Ship Construction

---

## Purpose of the Shipbook

The **Timonelo Shipbook** defines the complete operational and epistemic lifecycle of a vessel within Timonelo.

It answers one fundamental question:
> **"How does a real physical ship become a trusted, verifiable Timonelo digital twin?"**

This handbook serves as the permanent standard for maintainers, naval cartographers, field researchers, contributors, and verification officers. It establishes the rigorous procedures required to transform raw shipyard blueprints and physical survey evidence into an immutable, passenger-ready spatial system.

---

## Chapter 1: The Philosophy of Ship Building

Timonelo does not catalogue ships. Timonelo reconstructs spatial understanding.

Every vessel is treated as a complex, living architectural volume:
* **No shortcuts**: We do not trace marketing deck plans when General Arrangement blueprints are required.
* **No assumptions**: We do not infer socket pinouts or bed placements across sister vessels without verification.
* **No invented knowledge**: Missing data remains an explicit, honest void.

The objective of ship construction is not throughput or inventory volume. The objective is unyielding accuracy, calm orientation, and permanent trust.

---

## Chapter 2: The Life of a Ship

A vessel progresses through twelve distinct, non-overlapping operational stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE SHIP LIFECYCLE                                │
│                                                                             │
│   [ 01. DISCOVERY ] ────────── Initial Registry Identification (IMO)        │
│          │                                                                  │
│          ▼                                                                  │
│   [ 02. EVIDENCE INTAKE ] ──── Blueprint, Manifest & Photo Ingestion        │
│          │                                                                  │
│          ▼                                                                  │
│   [ 03. NORMALIZATION ] ────── Cartesian Metric Grid & Coordinate Bounds    │
│          │                                                                  │
│          ▼                                                                  │
│   [ 04. ARCHETYPE MATCH ] ──── Baseline Geometry Inheritance (80-90%)       │
│          │                                                                  │
│          ▼                                                                  │
│   [ 05. DELTA DETECTION ] ──── Drydock & Vessel-Specific Refits Isolated    │
│          │                                                                  │
│          ▼                                                                  │
│   [ 06. KNOWLEDGE PACK ] ───── Canonical Physical Twin Compiled (Plane 2)   │
│          │                                                                  │
│          ▼                                                                  │
│   [ 07. EXPERIENCE PACK ] ──── Contextual Lenses & Routines Compiled (P3/4) │
│          │                                                                  │
│          ▼                                                                  │
│   [ 08. SPATIAL AUDIT ] ────── Zero Collision & 100% Door Snapping Verified │
│          │                                                                  │
│          ▼                                                                  │
│   [ 09. BRIDGE OFFICER ] ───── Conversational Guidance Grounding Verified  │
│          │                                                                  │
│          ▼                                                                  │
│   [ 10. EXPLORER READY ] ───── 15-Second Passenger Orientation Certified    │
│          │                                                                  │
│          ▼                                                                  │
│   [ 11. PUBLICATION ] ──────── Cryptographic Sealing & Global CDN Deploy    │
│          │                                                                  │
│          ▼                                                                  │
│   [ 12. ARCHIVAL ] ─────────── Preserved Upon Drydock Major Refit           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Chapter 3: Required Evidence & Provenance

Every factual claim in a ship's profile must possess an unbroken chain of custody referencing immutable primary sources, governed by [CANON.md](CANON.md) and [TRUST_FRAMEWORK.md](TRUST_FRAMEWORK.md).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVIDENCE HIERARCHY TIERS                            │
├────────┬────────────────────────────────┬─────────┬─────────────────────────┤
│ TIER   │ EVIDENCE CATEGORY              │ WEIGHT  │ OPERATIONAL STANDARD    │
├────────┼────────────────────────────────┼─────────┼─────────────────────────┤
│ Tier 1 │ Primary Shipyard GA Blueprints │ 1.0     │ CAD / Vector Naval Arch │
│ Tier 2 │ On-Site Surveyor Photographs   │ 0.9     │ Rectilinear EXIF-tagged │
│ Tier 3 │ Double-Verified Contributor    │ 0.7     │ Corroborated field data │
│ Tier 4 │ Cruise Line Schematics (PDF)   │ 0.4     │ Audited for distortions │
│ Tier 5 │ Forums / Unverified Blogs      │ 0.0     │ STRICTLY FORBIDDEN      │
└────────┴────────────────────────────────┴─────────┴─────────────────────────┘
```

### The Two-Source Rule
No stateroom attribute (e.g., bed placement, connecting door, socket matrix) can be certified as **Verified** without corroboration from at least two independent Tier 1–3 sources.

---

## Chapter 4: The Knowledge Factory Compilation Pipeline

Governed by **[ADR-0001: The Five-Plane Spatial Architecture](adr/ADR-0001.md)**, ship compilation executes across eight modular stages:

1. **Stage 01: Evidence Intake**: Ingests, SHA-256 hashes, and registers raw blueprints, CSV manifests, and survey photos into content-addressed storage (Plane 1).
2. **Stage 02: Normalization**: Calibrates optical blueprint scales to the naval baseline ($LOA \times Beam$) and projects boundaries into the unit Cartesian box ($X \in [0,1], Y \in [-1,1]$).
3. **Stage 03: Archetype Matching**: Binds the vessel to its Master Archetype template, inheriting verified sister-ship geometry.
4. **Stage 04: Delta Detection**: Computes structural differences, drydock refits, and cabin renumbering mutations.
5. **Stage 05A: Knowledge Pack Compilation**: Compiles the immutable physical vector mesh (Plane 2).
6. **Stage 05B: Spatial Calculus Compilation**: Pre-indexes all-pairs shortest paths, vertical lift cores, and vertical sandwich co-locations (Plane 3).
7. **Stage 06: Spatial Validation**: Mathematical verification of non-overlapping polygons ($0.00\ m^2$ collision) and door-to-corridor graph connectivity.
8. **Stage 07: Experience Validation**: Audits contextual lenses (*Accessibility*, *Family*, *Quiet Cabin*) for epistemic compliance (Plane 4).
9. **Stage 08: Publication**: Cryptographically signs, seals, and deploys the production spatial twin (Plane 5).

---

## Chapter 5: Mandatory Quality Gates

A vessel cannot be published to production if a single quality gate fails:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION QUALITY GATES                           │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ GATE 1: PROVENANCE    │ 100% of spatial claims link to SHA-256 evidence.    │
│ GATE 2: TOPOLOGY      │ Zero orphan cabins; 100% doors snap to corridors.   │
│ GATE 3: GEOMETRY      │ Zero self-intersecting or colliding cabin polygons. │
│ GATE 4: UNKNOWN STATE │ Missing attributes explicitly declared as Unknown.  │
│ GATE 5: ZERO MOCK     │ Zero placeholder coordinates or synthetic routes.   │
│ GATE 6: LENS PURITY   │ Contextual lenses execute as pure stateless funcs.  │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

---

## Chapter 6: The Definition of "Experience Ready"

A ship is certified as **Experience Ready** only when it satisfies objective operational criteria across all decks:

1. **Complete Vertical Stack**: 100% of public and residential decks (Keel to Lido) are vectorized and vertically indexed.
2. **Total Stateroom Coverage**: 100% of passenger cabins defined in the operator manifest exist as closed polygons with verified door coordinates.
3. **Multi-Deck Circulation**: Every stateroom door can compute a step-free path to at least two distinct vertical elevator/stair cores.
4. **Sandwich Resolution**: 100% of residential cabins possess computed ceiling (Deck $N+1$) and floor (Deck $N-1$) adjacency records.
5. **Sightline Verification**: 100% of balcony staterooms have verified horizon angles and lifeboat obstruction classifications.

---

## Chapter 7: Ship Completeness Matrix

Each sub-system tracks distinct, verifiable completion states:

| Category | Level 1: Ingested | Level 2: Reconciled | Level 3: Verified | Level 4: Experience Ready |
| :--- | :--- | :--- | :--- | :--- |
| **Decks** | Blueprints Hashed | Bounds Calibrated | Elevations Matched | Vertical Stacks Sealed |
| **Cabins** | Manifest Loaded | Polygons Closed | Fixtures Corroborated | Sandwiches Mapped |
| **Venues** | Names Registered | Polygons Placed | Entrances Snapped | Noise Tags Assigned |
| **Topology** | Corridors Drawn | Nodes Connected | Lift Cores Linked | Multi-Deck Router Green |
| **Evidence** | Files Stored | Locators Assigned | Hashes Recorded | Two-Source Rule Passed |
| **Bridge Officer** | Pack Mounted | Grounding Tested | Voice Rules Passed | Oath Compliant |
| **Explorer** | Vectors Rendered | Routing Visualized | Lenses Responsive | 15-Second Test Passed |

---

## Chapter 8: The Necessity of Human Review

The Knowledge Factory accelerates data ingestion, but **trust is never fully automated.**

* **The Role of Automation**: Normalizes coordinates, detects polygon collisions, runs shortest-path calculus, and flags missing attributes.
* **The Role of the Human Shipkeeper**: Audits ambiguous structural deltas, reviews sightline photographs, verifies multi-source evidence, and certifies final launch readiness.

> **Law**: An algorithm may compile a ship, but only a human Shipkeeper can sign the certificate of publication.

---

## Chapter 9: The First Passenger Test

The ultimate proof of ship construction is not passing unit tests; it is human comprehension.

Before public deployment, an auditor unfamiliar with the vessel performs **The 15-Second Orientation Test**:
1. Select a random stateroom number.
2. Within 15 seconds, without reading external guides, answer:
   * *Where is my cabin on this ship?*
   * *What sits directly above my head?*
   * *How do I walk to the nearest breakfast venue?*
   * *Is my route step-free?*

If the auditor experiences confusion or hesitation, the vessel is sent back to Cartography for schematic refinement.

---

## 10. Launch Readiness Checklist

```markdown
### Pre-Launch Verification Ledger
- [ ] 1. Knowledge Pack passes strict JSON schema validation.
- [ ] 2. Zero polygon collisions detected across all deck planes.
- [ ] 3. 100% of staterooms snap to walkable corridor graph nodes.
- [ ] 4. Multi-deck Dijkstra router resolves all venue wayfinding routes.
- [ ] 5. Contextual Lenses (Accessibility, Family, Quiet) pass functional unit tests.
- [ ] 6. Bridge Officer conversational grounding passes zero-hallucination audit.
- [ ] 7. Cruise Explorer renders with zero layout shift ($CLS = 0$).
- [ ] 8. Primary GA blueprints and survey photos archived with SHA-256 hashes.
- [ ] 9. Two-source verification rule satisfied for all published staterooms.
- [ ] 10. Human Shipkeeper review signed and sealed in release manifest.
```

---

## The Shipkeeper's Pledge

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SHIPKEEPER'S PLEDGE                             │
│                                                                             │
│  I will never invent the ship.                                              │
│  I will never sacrifice trust for speed.                                    │
│  I will respect every vessel as a unique spatial system.                    │
│  I will leave the ship more understandable than I found it.                 │
│  I will honor the sacred Unknown.                                           │
│  I will build confidence for the traveler.                                  │
│  I preserve spatial truth for the lifetime of the vessel.                   │
│                                                                             │
│  I am a Shipkeeper of Timonelo.                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
