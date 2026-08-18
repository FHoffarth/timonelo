# 08_GIT_WORKFLOW — Branching Strategy, Branch Protection & Semantic Releases

## 1. Environment & Branch Hierarchy

```
feature/<ticket-id> (e.g. feature/FE-019-route-waypoints)
       │
       ▼ Local Verification (Build & Pytest 100% Green)
develop (Staging Environment -> staging.timonelo.com)
       │
       ▼ Staging Approval & Release Tagging (e.g. v0.1.0)
main (Production Environment -> timonelo.com)
```

---

## 2. GitHub Branch Protection Settings (Mandatory)

For the `main` branch on GitHub:
* ✅ **Require a pull request before merging** (Direct push strictly disabled).
* ✅ **Require status checks to pass before merging** (Pytest suite + Vite build).
* ✅ **Require review from code owners**.
* ✅ **Include administrators** in protection rules.

---

## 3. Semantic Versioning & Release Tagging Schedule

Timonelo releases are tagged semantically as milestone capabilities stabilize:

| Release Tag | Milestone Name | Canonical Capabilities |
| :--- | :--- | :--- |
| **`v0.1.0`** | **Design Freeze v1 & Architecture Canon** | Figma tokens (`#FBF8F3`, `#0C1B2A`, `#C58A46`), 8 page shells, atomic component library, `/docs` canon, `AGENTS.md`. |
| **`v0.2.0`** | **Homepage & Discovery Intelligence** | Global search pill, 3-pillar intelligence grid, mobile responsiveness, fast route switches. |
| **`v0.3.0`** | **Ship Intelligence & Cabins Deep Dive** | Full fleet registry (112 ships), stateroom vertical buffer analysis, connecting doors, and builder GA provenance. |
| **`v0.4.0`** | **Living Deck & Spatial Topology** | 4 parallel tracks, structural lift cores, halo neighbor rays, W3C BOT / PROV-O / IndoorGML live standards inspector. |
| **`v0.5.0`** | **Ports & Routes Intelligence** | Port guides (tender logistics, all-aboard countdowns), maritime trajectory maps, weather overlays. |
| **`v0.6.0`** | **Cruise Math & Travel Regulations** | Independent cost calculator, drink package break-even formulas, Schengen visa & border controls. |
| **`v1.0.0`** | **Production General Availability** | Comprehensive multi-vessel verified knowledge graph with end-to-end voyage dossier briefing. |

---

## 4. Release Tagging Command

When tagging a verified milestone on `main`:

```bash
# Tag the canonical release
git tag -a v0.1.0 -m "Release v0.1.0 — Timonelo Design Freeze v1 & Canonical Architecture"

# Push tag to origin
git push origin v0.1.0
```
