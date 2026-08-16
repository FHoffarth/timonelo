---
status: Approved (Universal Architecture Milestone)
version: 1.0.0
authority: Chief Platform Architect & Naval Systems Lead
applies_to: Entire Timonelo Multi-Vessel Platform
ratified_date: 2026-08-16
---

# Universal Vessel Intelligence Platform
### Cross-Category Scaling from Ocean Mega-Liners to River & Expedition Ships

---

## 1. The Universal Mandate

Timonelo was never designed as an MSC application or a single-operator cabin finder.  
Timonelo is the **Universal Spatial Intelligence & Decision Platform for Passenger Maritime Vessels**.

The integration of **MS Andorinha (Tauck / Scylla AG Douro River Class)** represents the definitive proof of this universal architecture:
* **Ocean Mega-Liner**: *MSC Bellissima* (315.8m LOA, 171,598 GT, 19 Decks, 2,508 twin staterooms, 3 elevator cores).
* **Luxury Riverboat**: *MS Andorinha* (80.0m LOA, Douro lock fit, 4 Decks, 42 staterooms, 1 central lift).

Both vessels run on the exact same Five-Plane mathematical architecture with **zero operator coupling** and **zero size-specific code branches**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNIVERSAL MARITIME PLATFORM SPECTRUM                   │
│                                                                             │
│  [ OCEAN MEGA-LINERS ]          [ LUXURY RIVERBOATS ]   [ EXPEDITION / YACHT]│
│  • MSC Bellissima (315.8m)      • MS Andorinha (80.0m)  • Future Ingestions │
│  • MSC Grandiosa  (331.4m)      • Rhine/Danube Twins    • Polar Ice-Class   │
│  • MSC Meraviglia (315.8m)      • Douro Lock Scale      • Boutique Cruisers │
│                                                                             │
│                     ▼                     ▼                    ▼            │
│                     └──────────────┬───────────────────────────┘            │
│                                    │                                        │
│                     [ TIMONELO KNOWLEDGE FACTORY ]                          │
│                     • Plane 1: Content-Addressed Evidence                   │
│                     • Plane 2: Pure Spatial Ontology                        │
│                     • Plane 3: Deterministic Spatial Calculus (Dijkstra)    │
│                     • Plane 4: Interpretive Lenses (Mobility, Quiet, Family)│
│                     • Plane 5: Sealed Knowledge Packs (JSON)                │
│                     • Plane 6: Cruise Intelligence Runtime (Briefings)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Abstractions

To achieve true universality, all ship-specific assumptions were eliminated across the platform:

### A. Dynamic Vertical Circulation (Gate 4)
* **Previous Assumption**: Hardcoded search for specific elevator lobby nodes (e.g. `D06_AFT_LIFT`).
* **Universal Abstraction**: Gate 4 dynamically inspects the active vessel's deck graph for any valid vertical core node (`is_elevator_lobby` or `is_stairwell_access`), verifying that every stateroom door has a continuous, step-free or stair-assisted path to vertical circulation.

### B. Dynamic Venue & Dining Resolution (Plane 6)
* **Previous Assumption**: Fixed ocean restaurant IDs or hardcoded deck numbers (e.g. Deck 6 dining rooms).
* **Universal Abstraction**: Plane 6 evaluators inspect the active vessel's ontology dynamically. For *MS Andorinha*, it resolves *The Compass Rose Restaurant* on Deck 02; for *MSC Bellissima*, it resolves *Il Ciliegio* on Deck 06.

### C. Scaled Muster & Safety Logistics
* **Previous Assumption**: 6 ocean muster stations (A through F) on Promenade decks.
* **Universal Abstraction**: Vessels with $\le 5$ decks automatically map muster assemblies to primary guest lounges and reception atriums, while mega-vessels map to life-raft embarkation stations.

---

## 3. Fleet Registry & Unified URL Architecture

The platform supports uniform, permanent public URLs across all vessel classes:

* `/{ship-slug}` $\rightarrow$ Opens the vessel's default verified orientation (e.g. `/ms-andorinha`).
* `/{ship-slug}/cabin/{number}` $\rightarrow$ Direct stateroom orientation dossier (e.g. `/ms-andorinha/cabin/301` or `/msc-bellissima/cabin/14122`).
* `/{ship-slug}/deck/{number}` $\rightarrow$ Direct deck level orientation (e.g. `/ms-andorinha/deck/2`).

---

## 4. Current Compiled Fleet Status

```
┌──────────────────────────────┬──────────────────┬──────────────────┬────────────────────────┐
│ VESSEL NAME                  │ IDENTIFIER       │ OPERATOR         │ ARCHITECTURE ROLE      │
├──────────────────────────────┼──────────────────┼──────────────────┼────────────────────────┤
│ **MSC Bellissima**           │ IMO 9766205      │ MSC Cruises      │ Primary Ocean Baseline │
│ **MS Andorinha**             │ ENI 02338573     │ Tauck / Scylla   │ Primary River Baseline │
│ **MSC Meraviglia**           │ IMO 9647710      │ MSC Cruises      │ Class Prototype Patch  │
│ **MSC Grandiosa**            │ IMO 9803613      │ MSC Cruises      │ Meraviglia Plus Patch  │
└──────────────────────────────┴──────────────────┴──────────────────┴────────────────────────┘
```

*Every vessel is compiled, verified through 4 Quality Gates, and immediately accessible without developer actions.*
