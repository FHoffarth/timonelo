# BROKEN PROMISES AUDIT · TIMONELO V1.0
# WHAT WAS PROMISED VS WHAT ACTUALLY WORKS

> **Standard:** *Every unfulfilled expectation is a broken promise. Marketing claims that exceed reality destroy product credibility.*

---

## 1. The Broken Promises Register

### 🔴 Promise 1: "The Universal Vessel Intelligence Platform · 112 Ships, 119 Ports"
* **The Marketing Claim:** We cover the global fleet and provide verified deck-by-deck blueprints across all major cruise lines.
* **The Brutal Reality:** Only **4 ships** (`msc-bellissima`, `ms-andorinha`, `msc-grandiosa`, `msc-meraviglia`) have interactive JSON packs. The other 108 ships exist only in backend Python schemas or SQLite databases, but cannot be rendered or explored by a user in the web application.
* **Verdict:** **BROKEN.** Overselling by 28x. The frontend must either render all 112 ships or honestly state that only 4 flagship twins are active in Version 1.0.

---

### 🔴 Promise 2: "Bridge Officer Tim will accompany you throughout your journey"
* **The Marketing Claim:** Tim is a continuous maritime companion who guides you before and during your cruise.
* **The Brutal Reality:** Tim is prominently displayed on the homepage (`/`). The moment a user navigates to `/ports/genoa`, `/vessels/msc-bellissima`, `/crew`, or `/mission`, Tim disappears completely. There is no officer presence, no dynamic commentary, and no persistent companion interface.
* **Verdict:** **BROKEN.** Tim is currently a hero banner, not an operating companion.

---

### 🔴 Promise 3: "Native Bilingual Communication (English & Deutsch)"
* **The Marketing Claim:** Tim and the platform communicate natively without feeling like machine translation.
* **The Brutal Reality:** Switching to Deutsch translates only `HospitalityLanding.tsx`, `Navigation.tsx`, and `Footer.tsx`. As soon as a German traveller visits `/ports` (Port Explorer), `/crew` (Bridge Team), or `/mission` (Platform Philosophy), 100% of the body content is in English.
* **Verdict:** **BROKEN.** A German user will feel misled on their second click.

---

### 🔴 Promise 4: "Never more certain than the evidence"
* **The Marketing Claim:** We never guess; unknown is marked explicitly as UNKNOWN.
* **The Brutal Reality:** If a user searches for an unmapped cabin number (e.g. `Cabin 99999` or `Cabin 10042`), the application silently falls back to `Cabin 14122` without informing the user: *"Cabin 10042 is not yet verified; showing default stateroom."* The traveller leaves thinking they are viewing their cabin.
* **Verdict:** **BROKEN.** Silent fallback violates the core constitutional principle of absolute transparency.

---

### 🔴 Promise 5: "Navigation Centred Around the Traveller"
* **The Marketing Claim:** Seamless, intuitive exploration across ships, staterooms, destinations, and philosophy.
* **The Brutal Reality:**
  - Clicking `Ships` on the homepage does nothing (broken DOM anchor `#fleet-gallery`).
  - Clicking `Constitutional Principles` in the footer does nothing (broken DOM anchor `#platform-principles`).
  - Typing an invalid vessel URL hangs indefinitely on a loading spinner.
* **Verdict:** **BROKEN.** 3 basic navigational interactions fail silently.

---

## 2. Summary Table

| Promise Made | Scope | Reality | Verdict |
| :--- | :--- | :--- | :---: |
| Universal Fleet (112 Ships) | Global | 4 Interactive Ships | 🔴 **BROKEN** |
| Continuous Bridge Officer Tim | Full Lifecycle | Homepage & Cabin Only | 🔴 **BROKEN** |
| Native German Experience | Platform-Wide | Top-level Only (Subpages English) | 🔴 **BROKEN** |
| Absolute Transparency (No Guessing)| Cabin Lookup | Silent Fallback to 14122 | 🔴 **BROKEN** |
| Fluid Navigation | UI/UX | 2 Dead Links + 1 Crash Route | 🔴 **BROKEN** |
| Acoustic & Step-Free Cabin Dossier | Flagship Twins | Verified & Accurate | ✅ **FULFILLED** |
| Strategic Port Buffer Logistics | 6 Flagship Ports | Verified & Accurate | ✅ **FULFILLED** |
| 11 Constitutional Articles | Philosophy | Fully Articulated | ✅ **FULFILLED** |
