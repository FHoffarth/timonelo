# Timonelo — Repository Hygiene & Deployment Safeguards (Mandatory)

> **Status**: Canonical Governance Document  
> **Applicability**: All Developers, Agents, and CI Pipelines  
> **Effective Date**: August 2026

---

## 1. Protected Page Shells (Canonical Surfaces)

The following pages and views represent **Design Freeze v1** and are strictly protected against accidental wholesale replacement:

1. **Homepage** (`frontend/src/components/pages/HomePage.tsx`)
2. **Ship Profile** (`frontend/src/components/pages/ShipProfilePage.tsx`)
3. **Living Deck** (`frontend/src/semantic-deck/components/SpatialGrammarCanvas.tsx`)
4. **Cabin Analysis** (`frontend/src/components/pages/CabinDeepDivePage.tsx`)
5. **Port Guide** (`frontend/src/components/pages/PortGuidePage.tsx`)
6. **Route Intelligence** (`frontend/src/components/pages/RouteIntelligencePage.tsx`)
7. **Cruise Math** (`frontend/src/components/pages/CruiseMathPage.tsx`)
8. **Travel Info** (`frontend/src/components/pages/TravelInfoPage.tsx`)

### Modification Rule:
- Future tasks may **only modify sections that are explicitly requested**.
- **Never regenerate an entire page file** when updating a single section, token, or dataset.
- Always use targeted edits or compose atomic components.

---

## 2. Component-First Architecture

All pages must compose standardized, reusable UI primitives from `frontend/src/components/ui/`:

* `MainNavbar` — Sticky top navigation with brand logo, route links, and search trigger.
* `Footer` — Colophon with standards metadata (W3C BOT/PROV-O).
* `SearchPill` — Central search control with `#0C1B2A` submit button.
* `SectionHeader` — Eyebrow + Newsreader display title + optional lead paragraph.
* `QuickFactsCard` — Key facts list with `[KNOWN]` / `[DERIVED]` epistemic badges (Light and Navy variants).
* `InfoCard` — Structured white card for staterooms, venues, and immigration items.
* `WarningCard` — Critical notices (Amber all-aboard warning, Navy passport validity).
* `TimelineCard` — Waypoint row for itineraries and day-by-day logistics.
* `WeatherCard` — Meteorological summary box with seasonal temperature ranges.
* `EpistemicBadge` — Standardized truth status pill (`[KNOWN]`, `[DERIVED]`, `[VERIFIED]`, `[LIKELY]`).
* `SubTabBar` — Horizontal tab selector with active gold indicator line.

---

## 3. Route & Component Isolation

Every page operates as an independent, isolated unit:
* Changes to `/cabin/:id` must never alter `/`.
* Changes to `/ship/:slug` must never alter `/route/:slug`.
* Changing one component must never trigger a cascade that rewrites unrelated pages.

---

## 4. Design Freeze Policy

The design tokens and visual language are **frozen**:
* **Canvas Colors**: `#FBF8F3` (warm ivory canvas), `#0C1B2A` (midnight navy), `#C58A46` (warm gold).
* **Typography**: `Newsreader` display serif for headlines, `Inter` for body copy and metrics, monospace for coordinates and codes.
* **Layout Structure**: 80rem max-width container, rounded card radii (`20px` / `28px`), subtle borders (`rgba(12, 27, 42, 0.08)`).

**Strict Prohibition**:
Do NOT redesign spacing, typography, colors, navbar, or footer unless explicitly requested by the user.

---

## 5. Git Workflow & Environment Strategy

### Environment Separation:
* `main` $\rightarrow$ **Production** (`timonelo.com`). Protected branch.
* `develop` $\rightarrow$ **Staging / Preview** (`staging.timonelo.com`).
* **Feature Branches**: `feature/<ticket-id>-<description>` (e.g. `feature/FE-014-cruise-math`).

```
feature/<ticket-id>
       │
       ▼ (Local Verification & Testing)
Pull Request into develop
       │
       ▼ (Staging Deployment & Review)
Merge into main (Production)
```

**Production updates may ONLY occur via a verified merge from `develop` into `main`.**

---

## 6. Pre-Modification Safety Backups

Before performing significant modifications to any canonical page:
1. Ensure the working tree is clean (`git status`).
2. Create a safety tag or branch:
   ```bash
   git branch backup/YYYY-MM-DD-<page-name>
   # or
   git tag backup-YYYY-MM-DD-<page-name>
   ```
3. If an edit fails or introduces regressions, restore immediately:
   ```bash
   git checkout backup/<branch-name> -- <file-path>
   ```

---

## 7. Forbidden Operations

1. ❌ Never rewrite or replace `App.tsx` wholesale.
2. ❌ Never regenerate the router or layout shells from scratch.
3. ❌ Never replace `index.css` or the design token system.
4. ❌ Never delete components in `components/ui/` or `semantic-deck/`.
5. ❌ Never simplify the Truth Engine, Calculus, or BOT/PROV-O models.
6. ❌ Never commit broken builds or failing tests.

---

## 8. Definition of Done (DoD)

Every ticket and pull request is only complete when:
- [x] All 8 canonical pages render identically unless intentionally updated.
- [x] No unrelated files or directories are modified.
- [x] Git diff contains exclusively the expected ticket changes.
- [x] `npx vite build` executes with **0 errors**.
- [x] `python -m pytest tests/ -q` executes with **100% passing tests**.
- [x] Tested on desktop and mobile breakpoints.
- [x] Accessibility and epistemic provenance integrity maintained.
