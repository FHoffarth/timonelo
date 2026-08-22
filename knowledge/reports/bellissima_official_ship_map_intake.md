# MSC Bellissima Official Ship Map Intake

Status: DRAFT / UNKNOWN / PUBLISH_BLOCKED — ingested, pending human adjudication

Scope: venue-to-deck assignments only

Artifact: ART-0002

Artifact SHA-256: `4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603`

## Purpose

This intake registers a second official MSC Bellissima source and reads the
venue-to-deck assignments it prints. It is not a geometry extraction, not a
navigation graph, and not a replacement for ART-0001.

## Artifact identity

| Field | Value |
|---|---|
| Artifact ID | ART-0002 |
| Visible title | MSC BELLISSIMA SHIP MAP |
| Filename | `be_en-gb.pdf` |
| SHA-256 | `4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603` |
| Byte length | 1 177 146 |
| Document class | `official_ship_map` |
| Publisher | MSC Cruises |
| Language | en-GB |
| Vessel | MSC Bellissima |
| Page count | 10 |
| Canonical vault path | `evidence/raw/sha256/4f/4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603.pdf` |

Acquisition note, recorded verbatim on the artifact:

> supplied by project owner; obtained from the myMSC application

No claim of public availability or distribution right is made or implied. The
class declares `Acquisition.REQUESTABLE` and `UsePermission.CITE_ONLY`.

The digest and byte length were computed from the bytes on disk, never typed.
`ArtifactRegistry.resolve_path("ART-0002")` returns the canonical vault path
above and re-hashes to the same digest. The legacy `evidence/artifacts/blobs/`
directory remains empty; no parallel blob store was created.

## Document class

`official_ship_map` is a new curated class in `authority.py`, distinct from
`cruise_line_deck_plan` (ART-0001). The deck plan draws stateroom topology; the
ship map indexes venues by category. Neither is dimensioned.

The class is granted authority over `deck.venue_present` and nothing else. It
is deliberately absent from `deck.venue_position`: a thematic map places a
label where the layout reads well, not where the venue is.

## Extraction

Pages 3–10 carry two-column index tables ("Restaurants | Deck",
"Bars - Lounges | Deck", "Outdoor Bars | Deck", "Shops | Deck", "Fun | Deck",
"Family Areas | Deck", "MSC Yacht Club | Deck"). Only those tables were read.

- **115** printed table rows read
- **87** distinct venue-to-deck statements created
- **22** venues printed on more than one category page with an identical deck
  value. These are one claim observed several times, not several claims: each
  produced a single statement whose locator names the primary occurrence and
  enumerates the repeats. There is exactly one statement per venue.

Every statement records its source page, and a locator naming the section, the
table, the row, and the printed deck token.

## Deck values and multi-deck venues

Every value is an ordered list of decks, including single-deck venues, so a
printed range cannot degrade to a scalar through a change of type. No range was
collapsed.

Four venues are printed with a range:

| Venue | Printed token | Recorded value |
|---|---|---|
| GALLERIA BELLISSIMA | `6-7` | `[6, 7]` |
| LONDON THEATRE | `5-6` | `[5, 6]` |
| MSC EXCURSIONS | `5-6` | `[5, 6]` |
| HORIZON AMPHITHEATRE | `16-18` | `[16, 18]` |

`HORIZON AMPHITHEATRE` is recorded as `[16, 18]`, not `[16, 17, 18]`. The deck
selector on page 2 of this same document lists the vessel's fifteen decks —
19, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5 and 4 — and does not list a
Deck 17. Expanding the range to include Deck 17 would assert a deck this
source denies.

Expanding a range consults that second printed fact, so the four range
statements carry `method: CALCULATED` with a derivation note naming the deck
selector. The other 83 are `DIRECT`. The printed token is preserved in the
locator and note in every case.

## Conflicts

**Intra-document conflicts: 0.** Every venue is printed with the same deck
value across every category table in which it appears.

## Legacy / non-canonical discrepancies

Files under `knowledge/ships/msc-bellissima/` cite sources that are not
registered artifacts (`MSC_BELLISSIMA_SHIP_INTELLIGENCE_PROFILE_2026`,
`MSC Bellissima Dining Directory`, and similar). They are therefore not
canonical evidence and were not treated as evidence conflicts. They are
preserved unchanged and may not override an artifact-backed fact.

| Venue | Legacy record | Ship map |
|---|---|---|
| London Theatre | `venues.json` `deck_number: 5` | `[5, 6]` |
| Galleria Bellissima | `venues.json` `deck_number: 6` | `[6, 7]` |

`entertainment.json` independently records the London Theatre as decks 5 and 6,
agreeing with the ship map and disagreeing with `venues.json`. That internal
inconsistency is pre-existing and was left untouched.

## What this source does not establish

The intake created **no geometry**: no coordinate, polygon, bounding box or
centroid. `geometry/deck*.geometry.json` and the Deck 14 geometry proof are
byte-unchanged, and neither references ART-0002.

The intake created **no routing edges**. The ingestion script imports nothing
from the spatial or calculus packages, and no statement carries a graph-shaped
field.

The intake created **no distance, walking-time or accessibility claims**.

Schematic ship silhouettes and the callout lines tying a venue label to a drawn
shape are presentational. No position was inferred from them.

The only intended future bridge is manual and sequential:

```text
official_ship_map -> evidenced venue identity/deck
                  -> spatial object association (later)
                  -> navigation graph (later)
```

## Publication state

All 87 statements are `DRAFT`, `UNKNOWN`, `PUBLISH_BLOCKED`. Nothing was
promoted. An intake registers and reads; it does not adjudicate.

The 113 ART-0001 statements are unmodified and remain persisted in their
original schema; rewriting them would be a silent mutation of accepted facts.

## Machine-readable record

[bellissima-official-ship-map-intake.json](../../evidence/audits/bellissima-official-ship-map-intake.json)

## Reproduction

```text
python scripts/ingest_bellissima_official_ship_map.py <path-to-be_en-gb.pdf>
```

Re-registering the same bytes issues no second artifact ID, and venues already
carrying a `deck.venue_present` statement are skipped.
