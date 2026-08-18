# AGENTS.md — Instructions for Autonomous AI Coding Agents

> **ATTENTION AGENT:** You are operating in the **Timonelo** codebase.  
> This file outlines your strict operating constraints and architectural obligations.

---

## 1. Zero-Turn Reading Protocol

Whenever you begin a task in this repository:
1. **Always read [`docs/00_READ_FIRST.md`](./docs/00_READ_FIRST.md) first.**
2. Read the specific architecture document relevant to your task (e.g. [`docs/04_SPATIAL_GRAMMAR.md`](./docs/04_SPATIAL_GRAMMAR.md) for Living Deck, [`docs/03_TRUTH_ENGINE.md`](./docs/03_TRUTH_ENGINE.md) for data or inference, [`docs/06_UI_PRINCIPLES.md`](./docs/06_UI_PRINCIPLES.md) for UI).

---

## 2. Core Operational Directives

* **Preserve Design Freeze v1**: The Figma prototype is canonical for presentation. **Do NOT redesign pages, alter color schemes, reconfigure typography, or invent new UX patterns.**
* **Preserve Spatial Grammar & Living Deck**: The Living Deck models the passenger's topological mental model (4 parallel tracks, structural lift cores, vertical buffer zones). Never replace it with raster PDF viewers or flat CAD drawings.
* **Preserve Truth Engine & Epistemology**: Every assertion must maintain provenance and confidence weighting. Never present certainty where only inference exists.
* **Component-First Composition**: Use reusable UI primitives from `frontend/src/components/ui/` (`SectionHeader`, `QuickFactsCard`, `WarningCard`, `TimelineCard`, `WeatherCard`, `EpistemicBadge`, `InfoCard`).
* **Modify Surgically, Never Replace Wholesale**:
  - ❌ **NEVER replace `App.tsx` wholesale.**
  - ❌ **NEVER regenerate the router or layout shells.**
  - ❌ **NEVER wipe out `index.css`.**
  - ❌ **NEVER regenerate an entire page file when only updating one section.**
* **Zero Unrelated Diffs**: Keep `git diff` minimal and focused exclusively on the requested feature or bugfix.

---

## 3. Pre-Flight Verification Checklist

Before reporting task completion:
1. Run `python -m pytest tests/ -q` $\rightarrow$ **Must be 100% green**.
2. Run `npx vite build` in `frontend/` $\rightarrow$ **Must build with 0 errors**.
3. Verify that all 8 canonical pages (`/`, `/ships`, `/cabin/:id`, `/ports`, `/routes`, `/cruise-math`, `/travel-info`, `/my-cruise`) render identically unless explicitly modified.
