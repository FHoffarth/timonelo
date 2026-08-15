---
status: Frozen (v1.0)
version: 1.0.0
authority: Timonelo
owner: Maintainers
applies_to: All Python, TypeScript, Schema & Data Tooling
last_updated: 2026-08-15
---

# Timonelo Engineering Principles

---

## 1. Core Engineering Axioms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE 6 ENGINEERING PILLARS                                │
│                                                                             │
│  [1] Determinism Over Cleverness      [4] Zero Layout Shifts (CLS = 0)      │
│  [2] Immutable Data Contracts         [5] Offline-First Capability          │
│  [3] Strict Schema Validation         [6] Strict Module Separation          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Engineering Laws

### 1. Determinism Over Cleverness
Given the same source dataset and rule version, the engine must produce bit-for-bit identical Knowledge Pack outputs across all environments. Non-deterministic operations (random UUID generation in data transforms, floating-point timestamp drift) are strictly forbidden in build pipelines.

### 2. Immutable Data Contracts
Once a Knowledge Pack is sealed and assigned a SemVer release hash, it is permanently immutable. Client applications treat Knowledge Packs as read-only spatial maps.

### 3. Strict Schema Validation
No data artifact may be committed, built, or deployed without passing automatic schema validation against the canonical `src/timonelo/knowledge_pack` contract. 

### 4. Separation of Data, Rules, and Presentation
- **Data** lives in `data/` and canonical packs.
- **Algorithms & Spatial Rules** live in `src/timonelo/`.
- **Presentation Logic** lives in `frontend/`.
- Code must never contain hardcoded ship dimensions or deck labels.

### 5. Zero Layout Shift & Performance Rigor
The presentation layer must maintain zero Cumulative Layout Shift ($CLS = 0$) across all screen sizes. Image containers and vector blueprint canvases must maintain pre-computed aspect ratio reserves.

### 6. Offline-First Capability
Every core feature—from cabin lookup to multi-deck wayfinding—must function with zero server network round-trips once the ship's Knowledge Pack is cached on client hardware.

---

## 3. Data Integrity & Codebase Rules

- **No Code in Data**: JSON data files must contain pure spatial assertions; never store executable scripts or display HTML inside data payloads.
- **Explicit Unknowns**: Missing attributes must be explicitly declared as `unknown` or omitted per schema spec; never populate dummy or default placeholder values (e.g., `area: 0` or `"TBD"`).
- **Coordinate Precision**: All spatial coordinates are floating-point numbers normalized to the hull's bounding box and validated for non-intersection.

---

## 4. Cross-References

- Canon: [CANON.md](CANON.md)
- Technical Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Trust Framework: [TRUST_FRAMEWORK.md](TRUST_FRAMEWORK.md)
- Contributor Guidelines: [CONTRIBUTING.md](CONTRIBUTING.md)
