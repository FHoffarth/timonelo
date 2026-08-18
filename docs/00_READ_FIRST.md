# 00_READ_FIRST — Mandatory Entry Point for All Contributors & AI Agents

> **CRITICAL INSTRUCTION FOR ALL AI AGENTS & ENGINEERS:**  
> Before writing, modifying, or deleting a single line of code in this repository, you **MUST** read and understand this document and the associated architectural canon in `/docs`.

---

## 1. What Timonelo IS

Timonelo is the world’s first **Scientific Cruise Intelligence Platform**.

It provides independent, evidence-grounded, verified spatial and decision intelligence for cruise passengers and maritime analysts.

Key platform pillars:
1. **The Living Deck**: A semantic spatial knowledge graph modeling vessels topologically (4 parallel walking tracks, structural elevator cores, vertical buffer zones, stateroom adjacencies, and line-of-sight verandas) rather than reproducing flat PDF floor plans.
2. **The Truth Engine**: An epistemic calculus engine tracking the origin, provenance, and confidence of every spatial statement (`KNOWN`, `DERIVED`, `VERIFIED`, `LIKELY`, `UNKNOWN`, `CONFLICT`).
3. **Independent Decision Math**: Unbiased, non-affiliate calculation of true cruise costs (beverage break-even math, gratuities, Wi-Fi, port transit costs).
4. **Port & Itinerary Intelligence**: Operational tender/berth mechanics, all-aboard safety buffers, DIY excursions, and consular/Schengen border regulations.

---

## 2. What Timonelo IS NOT

* ❌ **NOT an Online Travel Agency (OTA)**: We do not sell cabins, take bookings, or push inventory.
* ❌ **NOT an Affiliate Marketing Site**: We earn zero commissions from cruise lines, drink packages, or excursion operators. We have zero incentive to upsell.
* ❌ **NOT a Subjective Review Forum**: We do not rely on anecdotal ratings without evidentiary grounding.
* ❌ **NOT a CAD / Blueprint Viewer**: The Living Deck does not measure pixels or imitate PDF floor plans; it models the passenger's topological mental model.

---

## 3. The Canonical Hierarchy of Truth

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION (UI / Styling)              │
│            Figma Design Freeze v1 WINS                │
├────────────────────────────────────────────────────────┤
│          BUSINESS LOGIC & DOMAIN KNOWLEDGE             │
│            Existing Repository Models WIN             │
├────────────────────────────────────────────────────────┤
│           SPATIAL TOPOLOGY & EPISTEMOLOGY             │
│             Living Deck & Truth Engine WIN             │
└────────────────────────────────────────────────────────┘
```

1. **If code and Figma disagree on layout, typography, or styling $\rightarrow$ Figma wins.**
2. **If code and Figma disagree on domain rules, epistemic math, or graph edges $\rightarrow$ Repository wins.**
3. **Never simplify the Truth Engine or replace semantic models with dummy static data.**

---

## 4. Mandatory Rules of Engagement

1. **Design Freeze v1 is Canonical**: Do NOT redesign pages, alter color palettes (`#FBF8F3`, `#0C1B2A`, `#C58A46`), reconfigure spacing, or swap typography.
2. **Modify, Never Replace**: Never regenerate `App.tsx`, the router, global stylesheets, or canonical page shells (`HomePage`, `ShipProfilePage`, `CabinDeepDivePage`, `PortGuidePage`, `RouteIntelligencePage`, `CruiseMathPage`, `TravelInfoPage`) from scratch.
3. **Component-First Composition**: Assemble pages by composing reusable primitives from `frontend/src/components/ui/`.
4. **Epistemic Honesty**: Never display certainty (`[KNOWN]`) when a fact is derived or inferred. Always preserve provenance links to source artifacts.
5. **Git Hygiene**: Always work on feature branches (`feature/<ticket-id>`), verify locally with `pytest` and `vite build`, and merge into `develop` (staging) before promoting to `main` (production).

---

## 5. Reading Order for Architecture

1. [`01_PRODUCT_VISION.md`](./01_PRODUCT_VISION.md) — Product mission and core philosophy.
2. [`02_ARCHITECTURE.md`](./02_ARCHITECTURE.md) — End-to-end data pipeline and system topology.
3. [`03_TRUTH_ENGINE.md`](./03_TRUTH_ENGINE.md) — Epistemic calculus and evidentiary grounding.
4. [`04_SPATIAL_GRAMMAR.md`](./04_SPATIAL_GRAMMAR.md) — Living Deck topological grammar and passenger mental model.
5. [`05_KNOWLEDGE_MODEL.md`](./05_KNOWLEDGE_MODEL.md) — W3C BOT, PROV-O, IndoorGML, and JSON-LD data structures.
6. [`06_UI_PRINCIPLES.md`](./06_UI_PRINCIPLES.md) — Figma Design Freeze v1 tokens and component library.
7. [`07_IMPLEMENTATION_RULES.md`](./07_IMPLEMENTATION_RULES.md) — Exact rules for pull requests and code modifications.
8. [`08_GIT_WORKFLOW.md`](./08_GIT_WORKFLOW.md) — Branching strategy and deployment safeguards.
9. [`09_GLOSSARY.md`](./09_GLOSSARY.md) — Canonical vocabulary and definitions.
