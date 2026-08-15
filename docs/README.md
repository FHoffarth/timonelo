---
status: Frozen (v1.0)
version: 1.0.0
authority: Timonelo
owner: Maintainers
applies_to: Entire Timonelo Ecosystem
last_updated: 2026-08-15
---

# Timonelo Documentation Hub

Welcome to the Timonelo documentation repository. Timonelo is an independent cruise knowledge platform and spatial orientation engine.

---

## 1. Foundation Suite (v1.0 Frozen)

Recommended reading sequence:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FOUNDATION READING SEQUENCE                           │
│                                                                             │
│  1. [ MANIFESTO.md ] ────────── Why Timonelo exists & core philosophy       │
│  2. [ CANON.md ] ────────────── Epistemic definitions & 20 spatial laws     │
│  3. [ PRODUCT.md ] ──────────── Screen specs, cabin briefing & personas     │
│  4. [ ARCHITECTURE.md ] ─────── Technical boundaries & Five-Plane model     │
│  5. [ ENGINEERING_PRINCIPLES ]─ Code rules, determinism & performance       │
│  6. [ TRUST_FRAMEWORK.md ] ──── Evidence hierarchy & institutional trust    │
│  7. [ BRIDGE_OFFICER.md ] ───── Constitutional voice & conversational guide │
│  8. [ SHIPBOOK.md ] ─────────── How a vessel becomes Timonelo (Shipbook)    │
│  9. [ ROADMAP.md ] ──────────── Milestone progression & future scaling      │
│  10. [ CONTRIBUTING.md ] ────── How to contribute code, data & cartography  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Document Directory

| Document | Purpose |
| :--- | :--- |
| **[MANIFESTO.md](MANIFESTO.md)** | Purpose, negative boundaries, and experience hierarchy ($Experience \uparrow Orientation \uparrow Knowledge \uparrow Assets$). |
| **[CANON.md](CANON.md)** | Immutable definitions (*Canonical, Verified, Unknown, Experience Ready*), strict terminology, and the 20 Spatial Laws. |
| **[PRODUCT.md](PRODUCT.md)** | Cabin Briefing standards, the 16 Human Experience Dimensions, and 8 User Personas. |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical module boundaries, Spatial Engine specification, and pipeline data flow. |
| **[ENGINEERING_PRINCIPLES.md](ENGINEERING_PRINCIPLES.md)** | Code invariants: determinism, immutable contracts, zero layout shifts, and offline-first capability. |
| **[TRUST_FRAMEWORK.md](TRUST_FRAMEWORK.md)** | Five-tier evidence hierarchy, two-source verification rule, and non-commercial independence. |
| **[BRIDGE_OFFICER.md](BRIDGE_OFFICER.md)** | The permanent Bridge Officer Constitution, Conversational Canon, and Oath. |
| **[SHIPBOOK.md](SHIPBOOK.md)** | The permanent operational handbook for vessel ingestion, compilation, and certification. |
| **[ROADMAP.md](ROADMAP.md)** | Milestone execution plan spanning from M0 foundation through multi-ship scaling. |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution standards for code, vector cartography, field photography, and knowledge records. |

---

## 2. Architecture Decision Records (ADRs)

Foundational architectural choices are captured and maintained under [`docs/adr/`](adr/README.md):

- **[ADR-0001: Adopt the Five-Plane Spatial Architecture](adr/ADR-0001.md)**: Establishes the decoupled five-plane spatial architecture (Evidence, Spatial Ontology, Spatial Calculus, Contextual Lenses, Presentation Runtime).

---

## 3. Technical & Factory Specifications

- **[Explorer Architecture](explorer-architecture.md)**: Web runtime specification for rendering canonical Knowledge Packs.
- **[Domain Model Specification](architecture/DOMAIN_MODEL.md)**: Entity-relationship specifications for spatial domains.
- **[Knowledge Factory Specifications](factory/README.md)**:
  - [SPEC-002: Knowledge Factory](factory/SPEC-002-knowledge-factory.md)
  - [SPEC-003: Source Registry](factory/SPEC-003-source-registry.md)
  - [SPEC-004: Ship Maturity Model](factory/SPEC-004-ship-maturity-model.md)
  - [SPEC-005: Importer Architecture](factory/SPEC-005-importer-architecture.md)
  - [SPEC-006: Relationship Builder](factory/SPEC-006-relationship-builder.md)
  - [SPEC-007: Validation Framework](factory/SPEC-007-validation-framework.md)
- **Knowledge Explorer Tooling**:
  - [Knowledge Explorer Guide](Knowledge%20Explorer.md)
  - [Knowledge Index Guide](Knowledge%20Index.md)
  - [Knowledge Loader Guide](Knowledge%20Loader.md)
  - [Knowledge Validation Guide](Knowledge%20Validation.md)

---

## 4. Technical Audits & Operational Certifications

- **[PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md)**: Final QA stress test, 100 simulated passenger journeys, and Production Launch Certification (GO).
- **[SHIPYARD_READY.md](SHIPYARD_READY.md)**: Formal shipyard readiness certification and multi-vessel scaling blueprint.
- **[MERAVIGLIA_INHERITANCE.md](MERAVIGLIA_INHERITANCE.md)**: Class-level inheritance and shipyard reuse analysis across the Meraviglia & Meraviglia-Plus fleet.
- **[BELLISSIMA_COMPLETENESS_REPORT.md](BELLISSIMA_COMPLETENESS_REPORT.md)**: Formal certification and completeness matrix of MSC Bellissima as a 100% Operational Digital Twin.
- **[AUDIT_BELLISSIMA_v1.md](AUDIT_BELLISSIMA_v1.md)**: Formal adversarial audit and epistemic verification of the MSC Bellissima reference implementation v1.0.
- **[AUDIT_BELLISSIMA_v2.md](AUDIT_BELLISSIMA_v2.md)**: Scientific peer review and spatial systems audit of industrial-scale ontology, graph circulation, and Knowledge Factory maturity.

---

## 5. Historical Records & Milestones

- **[FOUNDING.md](FOUNDING.md)**: The founding record of August 2026, marking the transition from concept to permanent spatial platform.

---

## 6. Governance Policy

As of **Milestone v1.0**, the foundation documents in this repository are **FROZEN**. Modifications to core contracts, definitions, or boundaries require a formal Architecture Decision Record (ADR) and maintainer review.
