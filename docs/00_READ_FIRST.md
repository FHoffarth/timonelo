# 00_READ_FIRST — Mandatory Entry Point for All Contributors & AI Agents

> **CRITICAL INSTRUCTION FOR ALL AI AGENTS & ENGINEERS:**  
> Before writing, modifying, or deleting a single line of code in this repository, you **MUST** read and understand this document, [`/docs/adr/ADR-0002.md`](./adr/ADR-0002.md), and [`/README.md`](../README.md).

---

## 1. What Timonelo IS

**Timonelo is a Cruise Intelligence Platform.**

Its purpose is to provide explainable, evidence-based answers about ships, cabins, routes and ports.

Core governing principle:
> **Timonelo must be able to say “we do not know” before it is allowed to say “this is true.”**

Canonical Product Architecture:
```
Evidence → Knowledge → Geometry → Graph → Intelligence → Explainability → User
```

Key platform pillars:
1. **The Living Deck**: A semantic spatial knowledge graph modeling vessels topologically and geometrically from verified primary deck plans and technical sheets.
2. **The Truth Engine & Evidence Gatekeeper**: Multi-axial epistemic model (`METHOD`, `DERIVATION`, `REVIEW_STATE`, `CONFLICT`) where every statement is grounded in verifiable evidence.
3. **Independent Decision Math**: Unbiased, non-affiliate calculation of true cruise costs (beverage break-even math, gratuities, Wi-Fi, port transit costs).
4. **Port & Itinerary Intelligence**: Operational tender/berth mechanics, all-aboard safety buffers, DIY excursions, and consular/Schengen border regulations.

---

## 2. What Timonelo IS NOT

* ❌ **NOT an Online Travel Agency (OTA)**: We do not sell cabins, take bookings, or push inventory.
* ❌ **NOT an Affiliate Marketing Site**: We earn zero commissions from cruise lines, drink packages, or excursion operators.
* ❌ **NOT a Subjective Review Forum**: We do not rely on anecdotal ratings without evidentiary grounding.
* ❌ **NOT a Synthetic Fact Generator**: We never invent facts or interpolate unverified values into canonical ground truth.

---

## 3. The Canonical Hierarchy of Truth

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION (UI / Styling)              │
│            Figma Design Freeze v1 WINS                │
├────────────────────────────────────────────────────────┤
│          BUSINESS LOGIC & DOMAIN KNOWLEDGE             │
│            Canonical Repository Models WIN             │
├────────────────────────────────────────────────────────┤
│           SPATIAL TOPOLOGY & EPISTEMOLOGY             │
│          Evidence Gatekeeper & Truth Engine WIN        │
└────────────────────────────────────────────────────────┘
```

1. **If code and Figma disagree on layout, typography, or styling $\rightarrow$ Figma wins.**
2. **If code and Figma disagree on domain rules, epistemic math, or graph edges $\rightarrow$ Repository wins.**
3. **Never simplify the Truth Engine or replace semantic models with unverified static mocks.**

---

## 4. Mandatory Rules of Engagement

1. **Design Freeze v1 is Canonical**: Do NOT redesign pages, alter color palettes (`#FBF8F3`, `#0C1B2A`, `#C58A46`), reconfigure spacing, or swap typography.
2. **Modify, Never Replace**: Never regenerate `App.tsx`, the router, global stylesheets, or canonical page shells (`HomePage`, `ShipProfilePage`, `CabinDeepDivePage`, `PortGuidePage`, `RouteIntelligencePage`, `CruiseMathPage`, `TravelInfoPage`) from scratch.
3. **Component-First Composition**: Assemble pages by composing reusable primitives from `frontend/src/components/ui/`.
4. **Epistemic Honesty**: Never display certainty when a fact is derived or inferred. Always preserve provenance links to source artifacts.
5. **Git Hygiene**: Work on feature branches, verify locally with `pytest` and `npm run typecheck`, and maintain zero unrelated diff.

---

## 5. Architectural Reference Links

1. [`/README.md`](../README.md) — Platform overview and architecture.
2. [`/docs/adr/ADR-0001.md`](./adr/ADR-0001.md) — Two-tier source hierarchy.
3. [`/docs/adr/ADR-0002.md`](./adr/ADR-0002.md) — Canonical multi-axial epistemic model.
4. [`/docs/adr/ADR-0003.md`](./adr/ADR-0003.md) — Determinism and runtime verification.
5. [`/docs/adr/ADR-0004.md`](./adr/ADR-0004.md) — Evidence Gatekeeper and release gates.
