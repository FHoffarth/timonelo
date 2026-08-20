# MSC Bellissima One-Deck Geometry Proof

Status: DRAFT / UNKNOWN / PUBLISH_BLOCKED - evidence-control repair applied, re-audit required

Scope: Deck 14 only

Artifact: ART-0001

Artifact SHA-256: `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0`

## Purpose

This experiment tests whether source-linked spatial geometry can be extracted from one official MSC Cruises deck-plan page without manufacturing spatial truth. It is not a whole-ship extraction, a navigation graph, or canonical geometry promotion.

## Source verification and page identity

`ArtifactRegistry.verify("ART-0001")` succeeded before extraction. The resolver returned `evidence/raw/sha256/08/085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0.pdf`, whose bytes reproduce the registered digest.

The locked source is PDF page 5, visible Deck 14, visible name "World Class". The page MediaBox and CropBox are `[0, 0, 589.606, 807.874]` points, rotation is 0 degrees, and the exposed source coordinate system has a top-left origin with positive x to the right and positive y downward. Extraction used PyMuPDF 1.26.4 and the reproducible extraction timestamp is `2026-08-20T00:00:00Z`.

## Six-page structural forensics

All six pages were inspected for document structure; extraction remained locked to page 5 and Deck 14.

| PDF page | Dimensions (pt) | Rotation | Text words | Vector drawings | Raster images | Character |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 595.276 x 807.874 | 0 | 22 | 34 | 1 | cover, hybrid |
| 2 | 583.937 x 807.874 | 0 | 320 | 205 | 1 | legend and categories, hybrid |
| 3 | 589.606 x 807.874 | 0 | 504 | 9,413 | 2 | Decks 4-8, vector plans plus raster photographs |
| 4 | 595.276 x 807.874 | 0 | 1,615 | 7,451 | 2 | Decks 9-13, vector plans plus raster photographs |
| 5 | 589.606 x 807.874 | 0 | 505 | 5,183 | 3 | Decks 14-19, vector plans plus raster photographs |
| 6 | 595.276 x 807.874 | 0 | 3 | 37 | 1 | back cover, hybrid |

Low-level content-stream inspection found clipping operators and repeated coordinate-matrix operations on every page. Pages 3-5 contain particularly heavy reuse of transformations: 8,857, 5,673, and 4,751 `cm` operations respectively. No reusable Form XObjects were present; page resources contained only raster image XObjects. Page 5 contains 154 clipping operations, 599 rectangle operators, and extensive path construction. The deck plans therefore remain vector content rather than flattened raster plans. The page-top photographs are embedded raster images.

Cabin numbers, deck labels, lift labels, panoramic-lift labels, and public-area labels are selectable text. Cabin boundaries and deck outlines are vector paths. Icons are mixed vector/text symbols; this proof records the lift vector groups and its selectable label separately. Repeated transformation patterns exist, but this proof does not infer cross-deck registration from them.

Rendered-page review agreed with the object-level inspection. OCR was not used.

## Deck selection

The candidates were:

- Deck 8: cabins, public areas, and a central core are visible, but the mixed-use plan would conflate the cabin-boundary test with venue-boundary interpretation.
- Decks 9-13: strong cabin density and selectable labels, but their near-repeated layouts add little experimental value beyond one cabin-rich specimen.
- Deck 14: strong cabin density, selectable cabin labels, source-drawn cabin boundaries, and a visibly labelled lift region, while remaining materially less complex than public-area decks.
- Decks 15, 16, 18, and 19: progressively fewer cabins or predominantly public areas, weakening the cabin association proof.

Deck 14 was selected and locked. No geometry from any other deck was extracted.

## Raw extraction

Raw source material is stored in [deck14.raw.json](../../geometry/proofs/bellissima/deck14/deck14.raw.json). Geometry, selectable text, symbols, and semantic associations remain separate collections. Source references preserve the page, PyMuPDF drawing index, content sequence number, or text block/line/word identity.

The initial proof incorrectly sorted multiple enclosing cabin-boundary candidates and selected the smallest while recording `ambiguity: false`. The repaired cardinality gate never ranks candidates: zero qualifying containers is `UNRESOLVED`, exactly one is `ACCEPTED`, and more than one is `AMBIGUOUS` with `accepted_geometry: null`. Ambiguous output preserves the label, label bbox, candidate count, every candidate source reference, and the failure reason.

The common containment policy uses the selectable label bbox centroid as its reference point. A candidate qualifies only when that point lies strictly inside the source bbox by more than `0.01` PDF points on every axis. A point on or within epsilon of a boundary is excluded. The epsilon is fixed for the proof and cannot vary by cabin. No number parity, list order, neighboring number, approximate side, nearest shape, area ranking, or port/starboard rule participates.

## Coordinate transform and review viewport

The previous canonical transform used the hand-selected review crop `[24, 198, 128, 748]`. Forensics found no defensible source object establishing those four limits. The repaired proof therefore uses Model C: canonical coordinates use the neutral physical PDF Page 5 MediaBox, while the crop remains display-only.

Canonical normalized output uses Page 5 dimensions `589.606 x 807.874` PDF points, retains the top-left origin and downward-positive y-axis, and applies no rotation:

```text
x' = x / page_width
y' = y / page_height
```

Translation is `[0, 0]`; scaling is `[1/589.606, 1/807.874]`. The transform is identified as `pdf-page5-mediabox-to-unit-v2`. Extraction fails if the physical page dimensions differ from the audited MediaBox dimensions. The frame is non-semantic but canonical and auditable because it comes directly from the verified PDF page.

The former crop remains `[24, 198, 128, 748]` solely as `DISPLAY_ONLY`, `semantic: false`, and `geometry_provenance: false`. Changing it affects only the review PNG and cannot affect normalized geometry.

Every raw PDF drawing record now explicitly states `DIRECT_SOURCE_GEOMETRY`. Normalized cabin polygons are `TRANSFORMED_SOURCE_GEOMETRY` and retain drawing index, sequence number, source bbox, source reference, and transform ID. The lift review region is honestly `DERIVED_GEOMETRY` because it is the union bbox of two direct source vector groups followed by page-frame normalization. Nothing is classified `SYNTHETIC_GEOMETRY`.

## Cabin proof set

Ten cabin labels and their uniquely containing source-drawn boundaries remain accepted after the stricter repair: 14001, 14002, 14003, 14004, 14005, 14006, 14007, 14008, 14009, and 14010. Each has exactly one qualifying boundary under the shared strict-interior policy. They cover both visible outer columns and the two inner cabin groups in the forward section of Deck 14.

Each proof object records its source text bounding box, source vector bounding box, normalized polygon, source references, transform, association method, review state, evidence condition, and publication status. Every cabin remains `DRAFT`, `UNKNOWN`, and `PUBLISH_BLOCKED` pending human adjudication.

## Corridor result

The apparent corridor is negative space between source-drawn structures. This proof did not establish a separately bounded source polygon. It is recorded only as `INFERRED_NEGATIVE_SPACE` with no accepted geometry. No fixed-width or approximate corridor was generated.

## Vertical-core result

One selectable "Lift" label and the two flanking direct-source vector groups were extracted. Their union bbox is a derived, source-supported spatial anchor classified `DERIVED_GEOMETRY`; the two components remain individually `DIRECT_SOURCE_GEOMETRY`. The association remains explicitly ambiguous and requires human review. It establishes neither the exact functional boundary nor cross-deck identity, nearest-core status, connectivity, or travel distance.

## Venue result

No public venue is labelled within the locked Deck 14 proof region. No venue geometry or anchor was created.

## Human adjudication artifact

The review overlay is [deck14.review.png](../../geometry/proofs/bellissima/deck14/deck14.review.png). It renders the original vector page through the explicitly display-only viewport, outlines the ten cabin boundaries in blue, outlines the lift source region in red, and prints the fail-closed state. The viewport has no role in canonical normalization. The underlying normalized record is [deck14.proof.json](../../geometry/proofs/bellissima/deck14/deck14.proof.json).

The overlay is a review aid only. It does not promote evidence or establish publication eligibility.

## Ambiguities and unknowns

- The lift label supports the functional reading of the flanking vector groups, but the exact core boundary remains under review.
- The corridor is visible as negative space but lacks an independently established source polygon.
- Cabin label containment is deterministic, but final semantic adjudication has not occurred.
- Deck orientation, port/starboard identity, and fore/aft semantics were not inferred.
- No venue boundary exists in the selected proof region.

## Existing synthetic geometry

All 15 pre-existing `geometry/deck*.geometry.json` Bellissima files remain byte-for-byte unchanged. They remain `SYNTHETIC_GEOMETRY` and non-canonical. The proof lives only under `geometry/proofs/bellissima/deck14/` and cannot be confused with those files.

## Explicit non-claims

This proof does not establish globally verified Bellissima geometry, any second deck, deck registration, same-core relationships across decks, Above/Below relationships, vertical alignment, routing, nearest lifts or stairs, walking distance, accessibility routes, cabin side, recommendations, scoring, or frontend behavior. It does not promote any object to published knowledge.
