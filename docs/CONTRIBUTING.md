---
status: Frozen (v1.0)
version: 1.0.0
authority: Timonelo
owner: Maintainers
applies_to: All Contributors, Editors & Developers
last_updated: 2026-08-15
---

# Contributing to Timonelo

---

## 1. Core Contributor Rule

Before submitting code, vector cartography, stateroom attributes, or photography:

> **Timonelo must never sound more certain than its evidence.**

If evidence is missing or ambiguous, declare it as `unknown`. Never guess.

---

## 2. Contribution Streams

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CONTRIBUTION STREAMS                             │
│                                                                             │
│  [ STREAM 1: CODE & ENGINE ] ────── Python algorithms, contracts, UI runtimes│
│  [ STREAM 2: SHIP CARTOGRAPHY ] ─── Vector deck plans, polygons, graph nodes│
│  [ STREAM 3: FIELD EVIDENCE ] ───── Verified directional photography & specs│
│  [ STREAM 4: KNOWLEDGE RECORDS ] ── Ship histories, archetypes, source logs │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Contribution Standards

### 3.1 Code Contributions (`src/` and `frontend/`)
* Must adhere strictly to [ENGINEERING_PRINCIPLES.md](ENGINEERING_PRINCIPLES.md).
* Algorithms must be strictly deterministic; no random UUIDs or environment leaks in build steps.
* Zero layout shift ($CLS = 0$) and high performance must be preserved on all frontend routes.
* Run tests before submitting:
  ```bash
  python -m unittest discover -s tests
  ```

### 3.2 Cartography & Vector Data (`data/ships/`)
* Deck polygons must be non-self-intersecting and validated against normalized $[0.0, 1.0]$ coordinate bounds.
* Every stateroom door must snap to a valid circulation corridor node.
* Port (Even) and Starboard (Odd) numbering must match physical vessel door plates.

### 3.3 Field Evidence & Photography
* Photos must be captured at eye-level ($1.5m$ above deck) using rectilinear lenses ($24mm$ or $50mm$ equivalent).
* No beauty filters, no staging props (e.g., towel animals, wine glasses), and no fish-eye distortion.
* Every submission must declare: Cabin Number, Shot Angle (Yaw/Pitch), and Date of Capture.

### 3.4 Knowledge Records (`knowledge/`)
* Complete all required metadata fields (ISO `YYYY-MM-DD` dates, stable IDs, canonical entity types).
* Every factual assertion must link to an official Source record.

---

## 4. Review Workflow

```
[ Contributor Pull Request ]
              │
              ▼
[ 1. Automated Linting & Schema Validation ]
  ├── Python unit tests pass
  ├── Knowledge Pack schema validates against contract
  └── Coordinate boundaries check out
              ▼
[ 2. Maintainer Review ]
  ├── Source provenance verified
  └── Two-source rule verified for new claims
              ▼
[ 3. Merge to Main Repository ]
```

---

## 5. Cross-References

- Canon: [CANON.md](CANON.md)
- Mission: [MANIFESTO.md](MANIFESTO.md)
- Engineering Principles: [ENGINEERING_PRINCIPLES.md](ENGINEERING_PRINCIPLES.md)
- Trust Framework: [TRUST_FRAMEWORK.md](TRUST_FRAMEWORK.md)
- Documentation Hub: [README.md](README.md)
