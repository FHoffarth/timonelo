# Timonelo

> **Evidence-first cruise intelligence.**

Explainable knowledge about ships, cabins, routes and ports —
with provenance, uncertainty and geometry kept visible.

**Trust is part of the product. UNKNOWN is a valid answer.**

`Evidence → Knowledge → Geometry → Graph → Intelligence → Explainability → User`

Timonelo is an experimental Cruise Intelligence Platform built to answer
not only *what* is true, but *why the system believes it is true*.

---

## 1. What Timonelo Is

Timonelo is a **Cruise Intelligence Platform**. Its purpose is to provide explainable, evidence-based answers about ships, cabins, routes and ports.

Every passenger-facing statement is grounded in verifiable evidence. If a fact cannot be traced to physical evidence or deterministic derivation, it is explicitly rendered as **UNKNOWN**.

Core governing principle:
> **Timonelo must be able to say “we do not know” before it is allowed to say “this is true.”**

---

## 2. Canonical Architecture

```
Evidence
    ↓  (Physical artifacts, byte verification, SHA-256)
Knowledge
    ↓  (Truth statements, multi-axial epistemic model, authority matrix)
Geometry
    ↓  (Proven coordinate envelopes, vector slices, scale transforms)
Graph
    ↓  (W3C BOT topology, lift shafts, vertical core transit, adjacencies)
Intelligence
    ↓  (Acoustics, sightlines, solar orientation, distance calculations)
Explainability
    ↓  (Why-trace, evidence citations, epistemic badges, review history)
User
       (Passenger-facing digital twin and intelligence interface)
```

Knowledge flows downward only. No downstream layer may silently manufacture canonical truth.

---

## 3. Scientific Epistemic Model (ADR-0002)

| Dimension | Canonical Values | Meaning |
| :--- | :--- | :--- |
| **Method** | `DIRECT`, `CALCULATED`, `INFERRED` | How the statement was formed. |
| **Derivation** | `LOCAL`, `SISTER_SHIP`, `REFERENCE_MODEL`, `GENERATED` | The origin of the underlying data. |
| **Review State** | `DRAFT`, `SUBMITTED`, `CURATOR_REVIEWED`, `PUBLISHED` | Governance workflow status. |
| **Conflict** | `UNRESOLVED`, `RESOLVED` | Independent conflict tracking (no auto-resolving). |
| **Geometry Provenance** | `DIRECT_SOURCE_GEOMETRY`, `TRANSFORMED_SOURCE_GEOMETRY`, `DERIVED_GEOMETRY`, `SYNTHETIC_GEOMETRY`, `UNKNOWN_PROVENANCE` | Provenance of spatial coordinates. |
| **Confidence** | Computed dynamic metric $\in [0.0, 1.0]$ | Never a stored literal in ground truth. |

---

## 4. Governance & Role Separation

- **Evidence Gatekeeper**: Absolute trust gate. Verifies SHA-256 of physical bytes on disk, enforces epistemic ceilings, and blocks publication if unverified synthetic data or unresolved conflicts exist.
- **Bridge Officer Tim**: Orchestration and operational coordination only. It may request audits, summarize evidence, and expose uncertainty. It may **NOT** declare facts true, approve conflicts on its own, publish canonical knowledge, manufacture provenance, or override the Evidence Gatekeeper.
- **Quarantined Hypothesis Tools**: Legacy patch engines and archetype generators (`src/timonelo/factory/patch_engine.py`, `src/timonelo/factory/archetype_generator.py`) operate strictly in `data/hypotheses/` and are prohibited from authoring canonical truth in `knowledge/ships/`.

---

## 5. Repository Structure

```
timonelo/
├── knowledge/           # Canonical ground truth & physical evidence vault
│   ├── ships/           # Vessel knowledge (msc-bellissima, etc.)
│   ├── evidence/        # Physical artifacts with verified SHA-256
│   └── reports/         # Audits and architectural verification reports
├── src/timonelo/        # Backend Python package
│   ├── evidence/        # Evidence Gatekeeper, candidate bridge, harvester
│   ├── ontology/        # Canonical Pydantic models (BOT, Epistemology)
│   ├── database/        # Compiler, Bridge Officer orchestrator
│   └── factory/         # Quarantined hypothesis tools
├── frontend/            # Vite + React + TypeScript web application
│   └── src/
│       ├── living-deck/ # Living Deck Plan spatial viewer
│       ├── knowledge/   # Knowledge repository & pipeline gatekeeper
│       ├── intelligence/# Acoustic & distance calculation engines
│       └── explainability/ # Why-Trace & evidence inspector
├── docs/                # Architectural canon (ADR-0001 .. ADR-0004, etc.)
└── tests/               # Pytest suite & truth verification tests
```

---

## 6. Verification & Pre-flight Checks

```bash
# Backend pytest suite (100% green required)
python -m pytest tests/ -v

# Frontend TypeScript type check (strict, 0 errors required)
npm.cmd --prefix frontend run typecheck

# Frontend production build
npm.cmd --prefix frontend run build
```
