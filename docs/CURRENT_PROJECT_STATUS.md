# Current Project Status — 2026-08-17

---

## What exists today

### Held evidence
| | |
|---|---|
| Artifacts | **1** |
| `MSC-BEL-ART-001` | MSC Bellissima Deckpläne, 11.2025 DEU, MSC Cruises |
| SHA-256 | `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0` |
| Class | `cruise_line_deck_plan` · reliability 0.80 · CITE_ONLY |
| Statements | 33 authored, **32 published**, 1 superseded |
| Conflicts | 1, resolved |
| Questions registered | 15 (per cabin) |
| Cabins curated | **4** of 2,217 — 14120, 14122, 14124, 14126 |
| Coverage per cabin | 53.3% (6 direct, 2 derived, 7 unknown) |
| Topology facts | 153 — 24 direct, 31 derived, 98 unknown |

### Infrastructure
Truth Engine (registry, importer, editor, review, conflicts, authority matrix,
CLI workspace) · Topology Engine · Semantic Deck renderer · Render audit ·
Overlay renderer (internal only) · Test suite, 275 passing.

---

## What is verified

- Cabin 14122 is a **Deluxe Innenkabine, category IR2, designated for guests
  with reduced mobility (H)**, in block D14-B27, adjacent to 14118, on deck 14
  (World Class). Every field traces to page 5 with a locator and a named reader.
- Cabins 14120, 14124, 14126 are **BP — Balkonkabine mit teilweiser
  Sichteinschränkung** in block D14-B35, none mobility-designated, with bed
  symbols read individually.
- Deck 15 (Preziosa) sits above deck 14 and contains the Marketplace Buffet.
- The ship has 2,217 staterooms (printed, page 2).
- The held artifact contains **no scale, ratio, dimension or datum**.

---

## What is experimental

- **Block clustering.** Adjacency is `DERIVED_DETERMINISTIC` from a 2.5 pt
  x-threshold and a 2.2× y-gap split. Reproducible, not certain: a different
  threshold changes every adjacency edge. The plan never prints adjacency.
- **Category derivation.** IR2 by elimination (pink swatch shared with IR1,
  resolved by printed deck ranges); BP by unique swatch. Both are
  `DERIVED_DETERMINISTIC` and are **not equally strong** — the system does not
  currently record that difference.
- **Parser contract.** Interface only, no implementation. Designed before any
  real extraction; expected to change on first contact.
- **Semantic Deck renderer.** One deck, two blocks.

---

## What is blocked

| Blocker | Blocks | Unblocked by |
|---|---|---|
| No geometric artifact | Geometry Engine, distances, routing, walking times, wheelchair routes, "what is directly above" | Dimensioned shipyard GA, or first-party onboard survey |
| No MSC licence | Any surface displaying deck plan artwork | Agreement with MSC Cruises |
| Repository boundary not migrated | Clean separation of truth and UI | Migration (see roadmap M2) |
| Legacy ontology live in Repo B | Contradictory answers for 14122 | Quarantine (see roadmap M1) |
| Curation is manual | Scale beyond a few cabins | Deliberate — no parser until one deck is curated by hand |

---

## What is missing

- **2,213 uncurated staterooms.** Deck 14 alone has 239 known-to-exist,
  uncurated cabins.
- **Decks 4–13 and 15–19** — no topology extracted.
- **Venues** beyond the Marketplace Buffet.
- **Every dimensioned fact** — areas, door widths, corridor widths, balcony
  dimensions, HVAC.
- **Accessibility beyond the H designation.** The deck plan marks which cabins
  are designated; it does not give door widths, turning radii or bathroom
  layout. Those need an accessibility guide.
- **Cross-deck registration.**
- **A second artifact.** Everything known about this ship comes from one PDF.

---

## Known contradiction, unresolved

`timonelo/src/timonelo/ontology/bellissima.py` generates 2,508 cabins and
asserts cabin 14122 is category **BA, 19.0 m², not accessible**. The evidence
says **IR2, area UNKNOWN, accessible**. The legacy briefing path still reads
it. Until quarantined, the system can answer the same question two ways.
