---
status: Frozen (v1.0)
version: 1.0.0
authority: Timonelo
owner: Maintainers
applies_to: Timonelo Core Engine, Factory, Explorer, Pack Schemas
last_updated: 2026-08-15
---

# Timonelo Technical Architecture

---

## 1. Architecture Decision Reference

Timonelo's system architecture is governed by **[ADR-0001: Adopt the Five-Plane Spatial Architecture](adr/ADR-0001.md)**. 

The system decouples data, geometry, mathematics, human context, and rendering into five strictly independent planes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE FIVE-PLANE ARCHITECTURAL MODEL                       │
│                                                                             │
│   Plane 1: Evidence Plane          ── Content-addressed raw sensory records │
│   Plane 2: Spatial Ontology Plane  ── Metric geometry & topological graphs  │
│   Plane 3: Spatial Calculus Plane  ── Pure mathematical derivations         │
│   Plane 4: Contextual Lens Plane   ── Stateless human orientation functions │
│   Plane 5: Presentation Runtime    ── Multi-surface headless client runtimes│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architecture & Data Flow

Timonelo operates as a unidirectional spatial processing pipeline:

```text
Verified Source Material (Shipyard GA Drawings, On-site Surveys) [Plane 1]
                                 ↓
                     Ship Knowledge Factory
                                 ↓
                    Canonical Spatial Ontology [Plane 2]
                                 ↓
                    Spatial Calculus Engine [Plane 3]
                                 ↓
                    Contextual Lens Engine [Plane 4]
                                 ↓
                    Cruise Explorer Runtime [Plane 5]
```

### Architectural Boundaries
- **Source Separation**: Raw source material and derived spatial evidence remain strictly segregated.
- **Unidirectional Flow**: Presentation layers never feed unverified conclusions back into data layers.
- **Deterministic Derivation**: Given an identical source blueprint and rule set, spatial outputs are 100% reproducible.
- **No Inferred Truth**: Presentation layers may format or filter, but may never strengthen a claim or conceal an `Unknown`.

---

## 3. Core Technical Modules

### 3.1 Spatial Evidence Engine (`timonelo.engine`)
* **Role**: Computes reproducible geometric relationships, line-of-sight raycasting, walking paths, and overhead vertical sandwiches from normalized coordinates (Plane 3: Spatial Calculus).
* **Contracts**: Emits deterministic claims backed by derivation rules and evidence references.

### 3.2 Canonical Knowledge Pack (`timonelo.knowledge_pack`)
* **Role**: The authoritative, sealed, immutable data artifact representing a ship's complete spatial state (Plane 2: Spatial Ontology).
* **Format**: Self-validating schema encapsulating vessel metadata, deck meshes, stateroom polygons, venue nodes, claims, sources, and limitations.
* **Distribution**: Distributed as lightweight, cacheable static assets capable of operating offline.

### 3.3 Knowledge Factory (`docs/factory/`)
* **Role**: Ingests, lints, correlates, and compiles raw shipyard GA drawings and survey data into candidate Knowledge Packs (Planes 1 $\rightarrow$ 2).
* **Sub-systems**: Source Registry, Importer Architecture, Relationship Builder, and Validation Framework.

### 3.4 Cruise Explorer Runtime (`frontend/`)
* **Role**: High-performance client rendering engine that evaluates contextual lenses and presents orientation interfaces (Planes 4 $\rightarrow$ 5).
* **Performance Standard**: Sub-second spatial snapping, zero layout shift, and instant deck transitions.

---

## 4. The Spatial Coordinate Framework

```
                    ▲ +X (Longitudinal: Aft ──► Bow)
                    │
   -Y (Port) ◄──────┼──────► +Y (Starboard)
                    │
                    ▼ -X (Stern / Transom)

   Vertical Axis: +Z (Keel ──► Deck 01 ──► Deck 20)
   Origin [0,0,0]: Keel Centerline at Forward Perpendicular
```

All geometries are normalized within the vessel’s bounding envelope ($X \in [0.0, 1.0]$, $Y \in [-1.0, 1.0]$, $Z \in \text{Deck Tier}$).

---

## 5. Cross-References

- Architectural Decision: [ADR-0001: Adopt the Five-Plane Spatial Architecture](adr/ADR-0001.md)
- Canon: [CANON.md](CANON.md)
- Engineering Principles: [ENGINEERING_PRINCIPLES.md](ENGINEERING_PRINCIPLES.md)
- Domain Model: [architecture/DOMAIN_MODEL.md](architecture/DOMAIN_MODEL.md)
- Explorer Architecture: [explorer-architecture.md](explorer-architecture.md)
- Knowledge Factory Specs: [factory/README.md](factory/README.md)
- Trust Framework: [TRUST_FRAMEWORK.md](TRUST_FRAMEWORK.md)
