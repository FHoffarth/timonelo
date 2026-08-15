# Cruise Explorer — Architecture Summary

The Explorer is a **premium web front-end that renders a canonical Knowledge
Pack**. It consumes the pack schema defined by `src/timonelo/knowledge_pack`
(the MSC Bellissima reference architecture) and derives nothing of its own — it
selects and formats, but never strengthens a claim, invents a value, or hides an
Unknown.

## What changed, and the principle behind it

The Explorer was first prototyped against a bespoke geometry pack. It was then
**rebased onto the canonical architecture and the data migrated into the canonical
`knowledge-pack.json` schema** — migrate the data, not the architecture. The MSC
Meraviglia Spatial Evidence Engine output is kept under
`data/ships/msc-meraviglia/engine/` as the development reference; the Explorer
renders only the sealed canonical pack.

Because the Explorer speaks the canonical schema, **any canonical pack renders
unchanged** — the real Bellissima reference pack included. Meraviglia is simply
the pack that has been migrated here.

## Data flow

```text
Spatial Evidence Engine (data/ships/msc-meraviglia/engine/*.json)   ← dev reference
        │
        │  scripts/build_explorer_pack.py   (deterministic migration into the
        │                                     canonical schema; self-validates)
        ▼
data/ships/msc-meraviglia/knowledge-pack.json    (canonical source of truth)
frontend/public/packs/msc-meraviglia.pack.json   (asset the Explorer fetches)
        │
        ▼
Explorer UI  ──  Ship → Deck → Cabin
```

## How canonical concepts map to the UI

| Canonical concept | Where it appears |
|-------------------|------------------|
| `ship`, `decks`, `public_areas` | Ship overview, deck rail, deck pages |
| `cabins` (entities) | Deck cabin grids, cabin identity |
| `relationships` (deck `above`/`below`) | Deck & cabin "vertical connections" — authoritative, deterministic |
| `claims` (`motion_profile`, `noise_exposure`) | Cabin position, motion meters, noise section |
| `sources`, `status`, `limitations` | Provenance, maturity ladder, the Unknown section |
| `evidence_kind`, `derivation_rule`, `limitation` | The "how we know / what we don't" transparency ledger |

## Three honesty decisions

1. **Maturity is `Structured`, stated plainly.** The only source is a third-party
   deck-plan aggregator (rejsy.pl); it can structure the ship but not verify it.
2. **Vertical adjacency is stated at deck level, not cabin level.** Each deck is
   drawn in its own frame on the source, so a specific "cabin directly above"
   cannot be established without overclaiming. Deck-to-deck adjacency is
   authoritative; same-deck cabin numbers are shown only for onward exploration.
3. **Unknown is first-class.** Cabin category, view, balcony and dimensions are
   not in a deck plan and are shown as explicit Unknowns. Public-area `kind` is
   required by the schema but not stated by the source, so it is classified from
   the venue label and every area carries a limitation saying so; ambiguous
   labels are flagged.

## Constraint compliance

No recommendations, no scores, no suitability, no AI reasoning, no inferred
preferences, no commercial optimisation appear in the pack or the Explorer.

## Tech

Built onto the existing public site (React 19, Tailwind v4, self-hosted Inter +
Newsreader). React Router 7 adds the Explorer routes: `/ship/:shipId`,
`/ship/:shipId/deck/:deck`, `/ship/:shipId/deck/:deck/cabin/:cabin`. The pack
loads as a separate cacheable asset and is indexed once by `PackModel`
(`frontend/src/explorer/pack.ts`).

## Lighthouse (production build, Lighthouse 12.8.2)

| Target | Performance | Accessibility | Best Practices | SEO |
|--------|:-:|:-:|:-:|:-:|
| Ship page (desktop) | 100 | 100 | 100 | 92 |
| Cabin page (desktop) | 100 | 100 | 100 | 92 |
| Ship page (mobile, throttled) | 89 | 100 | 100 | 92 |

CLS is 0 across the board. Mobile LCP is 2.6 s under 4× CPU + slow-4G emulation;
the canonical pack (~2.3 MB, one fetch, ~2.5 k claims for 2,228 cabins) is the
main weight — an inherent property of a claim-based pack at this cabin count. SEO
92 is the base site's root-canonical strategy applied to deep routes, inherited
from the public site.

## Screenshots

See [`docs/factory/screenshots/`](factory/screenshots/): ship, deck and cabin
pages at desktop and mobile widths.

## Reproduce

```bash
# migrate the engine reference into a canonical pack
python scripts/build_explorer_pack.py

# run the app
cd frontend && npm install && npm run dev
# open http://localhost:5173/explore
```

## Relationship to the factory specs

The [`docs/factory/`](factory/) specs (SPEC-002…007) are the design-level account
of the same pipeline — sources, maturity, importers, relationship derivation and
validation. The canonical `src/timonelo/knowledge_pack` module is the concrete
schema those specs describe; where they differ in detail, the module is
authoritative.
