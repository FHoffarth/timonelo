# CHAPTER II REPOSITORY HYGIENE & REORGANIZATION PROPOSAL
### Structural Cleanliness Plan for Mainline Freeze

---

## 1. Executive Summary

As Timonelo transitions from Chapter I (Foundation & Twin Engine) into Chapter II (Onboard Product, Port Intelligence & Crew Foundation), the repository must be cleansed of historical artifacts, temporary scratch scripts, and legacy naming remnants.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            PROPOSED CLEAN REPOSITORY TOPOLOGY                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  timonelo/                                                                                       │
│  ├── data/                  # Sealed compiled digital twins & ship manifests                     │
│  ├── docs/                                                                                       │
│  │   ├── constitution/      # MANIFESTO, CANON, DECISION_FIRST, TRUST_FRAMEWORK                  │
│  │   ├── architecture/      # 5-Plane model, Cruise Intelligence Runtime, SPEC-008               │
│  │   ├── factory/           # CRUISE_KNOWLEDGE_FACTORY, SHIPBOOK, SHIPYARD_READY                 │
│  │   ├── operations/        # FOUNDER_CRUISE_KIT, CREW_CONTRIBUTION, INTERVIEW_GUIDE             │
│  │   └── archive/           # Historical notes & early research iterations                       │
│  ├── frontend/              # React/Vite editorial web application                               │
│  │   ├── public/media/      # Authentic maritime photography & manifests                         │
│  │   └── src/               # Pure presentation & verified route controllers                    │
│  ├── knowledge/             # Canonical Cruise Knowledge Factory sources                         │
│  │   ├── ships/             # Ship Knowledge Packs (Bellissima, Andorinha, Meraviglia...)        │
│  │   ├── ports/             # Port Knowledge Packs (Genoa, Barcelona, Porto, Marseille, Naples)  │
│  │   ├── routes/            # Route Knowledge Packs (Western Med, Douro...)                      │
│  │   └── sources/           # Master provenance registry.json                                    │
│  ├── src/timonelo/          # Production spatial graph compiler & factory engine                 │
│  ├── tests/                 # Deterministic Python test suites (34 tests)                        │
│  └── tools/                 # CLI utilities (knowledge_explorer.py, verify_twin.py)              │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Identified Files for Proposed Archival / Relocation

> **Rule:** *No files will be deleted automatically. All legacy documents are moved into `docs/archive/` or `.gitignore`.*

1. **Legacy Knowledge Notes with space filenames**:
   - `docs/Knowledge Explorer.md` $\rightarrow$ `docs/archive/legacy_notes/Knowledge_Explorer.md`
   - `docs/Knowledge Index.md` $\rightarrow$ `docs/archive/legacy_notes/Knowledge_Index.md`
   - `docs/Knowledge Loader.md` $\rightarrow$ `docs/archive/legacy_notes/Knowledge_Loader.md`
   - `docs/Knowledge Validation.md` $\rightarrow$ `docs/archive/legacy_notes/Knowledge_Validation.md`
2. **Historical Screenshot Export Folders**:
   - `docs/explorer-screenshots/` and `docs/export-screenshots/` $\rightarrow$ `docs/archive/screenshots/`
3. **Workspace Path Remnant Check**:
   - Verify that any legacy references to `energyradar` in internal docs are updated to standard project paths.

---

## 3. Chapter II Git Workflow & Tagging Standard

* **Default Branch:** `main` (Protected, requires passing unit tests and clean Vite build).
* **Feature Branches:** `feature/<slug>` or `wave/<number>` (e.g. `wave/01-msc-fleet-ingestion`).
* **Release Tags:**
  * `v0.9.5-foundation` (Foundation Freeze — sealed today)
  * `v1.0.0-october` (Onboard MSC Bellissima Maiden Operational Release)
