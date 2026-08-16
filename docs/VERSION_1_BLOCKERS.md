# VERSION 1.0 BLOCKERS & RESOLUTION MATRIX
# OPERATION BROKEN PROMISES

> **Standard:** *Every promise made by Timonelo must be kept. No dead ends. No blank screens. No broken links. No false capabilities.*

---

## 1. Priority P0 — Broken Trust, Dead Ends & Broken Navigation
*Must be resolved before Version 1.0 General Availability.*

| ID | Issue Description | Location | Impact | Required Resolution |
| :---: | :--- | :--- | :--- | :--- |
| **P0-1** | **Header "Ships" link is a dead click on Landing** | `Navigation.tsx` / `HospitalityLanding.tsx` | User clicks "Ships" from `/` and nothing happens because `#fleet-gallery` ID is missing. | Add `id="fleet-gallery"` or `id="reference-voyages"` to the voyage selection section in `HospitalityLanding.tsx` and smooth scroll to it. |
| **P0-2** | **Footer "Constitutional Principles" link is a dead click** | `Footer.tsx` / `HospitalityLanding.tsx` | Clicking "Constitutional Principles" tries to find `#platform-principles` which does not exist on Landing. | Route directly to `/mission` or add anchor `id="philosophy"` in `HospitalityLanding.tsx`. |
| **P0-3** | **Unhandled 404 on Invalid Ship Route** | `App.tsx` (`loadShipData`) | Visiting an invalid URL (`/vessels/unknown`) hangs on a blank loading screen without explanation. | Render a calm, dignified 404 Empty State with Bridge Officer Tim: *"This vessel is not yet in our verified registry. Return to Fleet."* |

---

## 2. Priority P1 — Incomplete Experiences & Polish
*High priority to ensure consistent hospitality and depth.*

| ID | Issue Description | Location | Impact | Required Resolution |
| :---: | :--- | :--- | :--- | :--- |
| **P1-1** | **German Language Leaks on Deep Subpages** | `PortExplorer.tsx`, `ShipLandingPage.tsx`, `CrewSection.tsx`, `MissionSection.tsx` | User switches to Deutsch, but Port Explorer, Crew, and Mission remain in English. | Extract remaining subpage copy into `i18n/locales/de.ts` and `en.ts` for unified bilingual experience. |
| **P1-2** | **Tim's Voice in Port Explorer & Ship Landing** | `PortExplorer.tsx`, `ShipLandingPage.tsx` | Tim is present on Landing and Stateroom, but feels absent on Port and Vessel overviews. | Add a concise, 1-sentence Officer Note from Tim to the Port Explorer and Ship Landing Hero. |
| **P1-3** | **Search Modal Back-Navigation** | `UniversalSearchModal.tsx` | ESC key closes search, but clicking on mobile overlay should have explicit touch-target dismiss. | Ensure mobile swipe/tap backdrop dismissal is instantaneous and accessible. |

---

## 3. Priority P2 — Future Expansions & Post-1.0 Roadmap
*Capabilities planned for subsequent releases (v1.1+).*

| ID | Capability Description | Target Release | Notes |
| :---: | :--- | :---: | :--- |
| **P2-1** | **Interactive 3D Deck Plan Rendering** | v1.1 | Vector WebGL deck plan viewer for interactive corridor walking. |
| **P2-2** | **Flight PNR Direct Parsing** | v1.2 | Offline parsing of airline booking references to calculate live transfer MCT. |
| **P2-3** | **Additional Languages (FR, IT, ES)** | v1.2 | Expand i18n architecture to French, Italian, and Spanish. |
| **P2-4** | **108 Additional Interactive Stateroom JSON Packs** | v1.3 | Expand verified stateroom blueprints from 4 flagship twins to all 112 registry vessels. |

---

## 4. Immediate Action Plan for Version 1.0 Release

```
[P0-1 Fix] Add id="fleet-gallery" to HospitalityLanding voyages section
    ↓
[P0-2 Fix] Update Footer handleNavigatePrinciples to route cleanly to /mission
    ↓
[P0-3 Fix] Add VesselNotFound 404 state in App.tsx
    ↓
[P1-1 Fix] Localize PortExplorer, CrewSection, and MissionSection with useI18n()
    ↓
[Verification] End-to-end clickthrough across all 6 views in English & Deutsch
```
