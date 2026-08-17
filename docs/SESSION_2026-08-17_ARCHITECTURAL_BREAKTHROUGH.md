# Session 2026-08-17 — Architectural Breakthrough

Canonical record of the day Timonelo became evidence-first. If this document
and any chat history disagree, this document wins.

---

## 1. Project evolution

### Where the day started

An audit of the repository found that the codebase systematically manufactured
certainty while publicly claiming the opposite. The landing page told users that
unverified details are marked UNKNOWN. The code did this:

```python
is_suite_stbd   = (deck_number >= 15) or (idx <= 12)
area_stbd       = 28.0 if is_yc_stbd else (27.0 if is_suite_stbd else 19.0)
bed_near_balcony = (idx % 4 == 2)
evidence_links  = evidence_links
```

Cabin geometry was synthesised by arithmetic — bed position from a modulo on the
cabin index — then stamped with a citation to a document that never contained
it. `EvidenceField` defaulted every unset field to
`VERIFIED / confidence 0.98 / chief_knowledge_architect`. `audit_ship()` computed
confidence from fabricated counters (`total_facts += 6`, `verified_count += 5`).
Of 15,090 evidence links in the knowledge base, two hand-typed hex patterns
accounted for 15,048. `hashlib` was imported in seven modules and never once
used to hash a document.

Cabin 14122 rendered as "Category BA (19 m²)" and "Pure residential buffer" —
the latter for a cabin sitting directly beneath the Marketplace Buffet, which
the sandwich resolver had correctly identified before the renderer overwrote it
with a hardcoded string.

### The chain that replaced it

```
Knowledge Factory      artifacts enter, content-addressed by SHA-256
        ↓
Truth Engine           statements with provenance, review, conflicts
        ↓
Topology Engine        adjacency, containment, block membership
        ↓
Semantic Deck Model    our own ordinal representation
        ↓
Living Deck Plan       renders what is known; shows what is not
```

### Why the twin is now evidence-first

Because the alternative was measured and found to be false. A twin that
contradicts a held document is not a twin with gaps — it is a confident source
of wrong answers. The first real artifact proved it: the twin said cabin 14122
was a **balcony cabin with unknown accessibility**, citing a Chantiers de
l'Atlantique general arrangement that does not exist in the repository. The
held MSC deck plan shows it is an **interior cabin, designated accessible**.
Both fields were inverted, and the fabricated provenance made them more
convincing, not less.

The twin now grows only as evidence grows. Never the other way around.

---

## 2. Scientific discoveries

### 2.1 Ground Truth always overrides generated content
Where the twin and a held artifact disagree, the artifact wins. Generated
content is never defended. The cost is real and was accepted: coverage
collapsed when fabrication was removed. That collapse was the first accurate
measurement the system had ever produced.

### 2.2 Quarantine, do not delete
24 untraceable files were moved to `hypothesis/_quarantined_2026-08-17/`.
Deletion would destroy the record of what was believed and why. Quarantine
preserves provenance while preventing contamination. Promotion back requires an
evidence event, not a file edit.

### 2.3 UNKNOWN is a valid scientific result
UNKNOWN is not a gap in the data — it is computed by comparing the question
registry against the statement graph. It cannot be discovered by looking at
answers, only by knowing which questions exist. This makes coverage measurable:
not "how many facts do we have" but "how many questions can this cabin answer".

An UNKNOWN fact carries no value. The engine rejects one that does.

### 2.4 Deterministic derivation is not direct evidence
`DERIVED_DETERMINISTIC` is reproducible, not certain. Block adjacency comes from
a clustering rule with a 2.5 pt x-threshold and a 2.2× y-gap split; a different
threshold would change every adjacency edge downstream. The deck plan draws
cells — it never prints "14118 is adjacent to 14122".

The distinction must remain visible in APIs and renderers. It must not collapse
into a known/unknown binary.

**Known limit, unresolved:** two derivations can differ in strength and the
system does not record it. Category IR2 was derived by *elimination* — the pink
legend swatch is shared by IR1 and IR2, resolved only by the printed deck
ranges. Category BP was derived from a *unique* swatch. BP is materially
stronger. Both are labelled identically.

### 2.5 Geometry cannot be established from ART-0001
Full text of all six pages searched: no scale bar, no ratio, no dimensions, no
frame datum. The only measurements printed anywhere are bed sizes (140×200 cm),
which are furniture.

Cross-deck registration also fails: drawn hull heights for decks 14, 15 and 16
are 511.2, 514.8 and 517.0 pt — decks spanning the same hull, differing by ~1%,
with no common datum. Decks 13 and 14 are not even on the same page.

Therefore no coordinate, distance, route, walking time, or "what is directly
above my cabin" is derivable. The Geometry Engine is empty **by evidence, not
by omission**.

### 2.6 Topology *can* be established from ART-0001
Cabin identity, deck membership, deck name, legend colour class, printed
symbols, block membership and drawn order are all readable. 153 topology facts
were extracted: 24 direct, 31 derived, 98 explicitly unknown.

This is the finding that made the twin buildable at all. A topological twin
answers "who are my neighbours", "which block am I in", "which deck is above",
"is this cabin accessible" — without asserting a single distance.

### 2.7 The renderer itself makes epistemic claims
The sharpest discovery of the day. A renderer **cannot abstain**: every element
must be placed somewhere, at some size, in some order. There is no null
rendering. Every visual variable therefore carries a claim whether or not the
author intended one — and unintended claims are the dangerous kind, because
nobody reviews them.

The first Semantic Deck render made two claims the Truth Engine had explicitly
refused:

1. **Orientation.** Blocks were stacked vertically in drawn page order and
   placed left-to-right mirroring page position. A reader reads vertical as
   fore/aft and horizontal as port/starboard. But `cabin.hull_side` is UNKNOWN
   for every curated cabin — the plan prints no port/starboard label and no bow
   marking.
2. **Block extent.** Block D14-B27 rendered shorter than D14-B35 because it
   holds six cabins rather than eight. Cardinality is topological; rendered as
   height it reads as physical extent.

Both passed a review that was specifically looking for fabricated geometry.

### 2.8 Every visual variable must be auditable
Nine variables are audited: `axis_vertical`, `axis_horizontal`, `spacing`,
`element_size`, `group_extent`, `order_within_group`, `colour`,
`border_pattern`, `absence`.

### 2.9 RenderAudit
A renderer declares, per variable, the claim it encodes or an explicit
nullification with a stated basis. `assert_complete()` raises before emit if any
audited variable is undeclared. The audit is serialized alongside the render so
a reviewer sees the claims without reading the drawing code.

**Known limit:** the audit catches *undeclared* variables. It cannot catch a
declaration that is wrong or self-serving. It forces claims into the open for
review; it does not judge them.

### 2.10 Uniform spacing communicates unknown geometry
Uniform spacing is not a styling choice. It is a scientific statement:

> We know order. We do not know distance.

Equal cell sizes state:

> We know identity. We do not know dimensions.

This is the metro-map convention. Nobody measures a Tube map, because uniform
spacing announces that distance carries no information. Draw the same cabins at
their relative spacing on the publisher's page and someone will measure them —
and page position is not ship position.

Enforced structurally: `SemanticCabin` accepts `ordinal` and **refuses page
coordinates**. A request for proportional layout is answered by pointing at the
empty Geometry Engine.

### 2.11 The Semantic Deck Model is an epistemic projection, not a floorplan
Its visual language communicates certainty, not appearance. Epistemic state is
carried by **border pattern** rather than colour, so the distinction survives
greyscale printing and colour-blindness.

**Absence is a claim.** A deck rendered with only its curated cabins asserts
those are the only cabins. Uncurated cabins render as explicit dotted gaps, and
the remaining count is stated numerically.

### 2.12 Silent defaults are the recurring defect
Three separate bugs this session shared one shape: a default that quietly
substituted for missing information.

- `SOURCE_RELIABILITY.get(c, 0.0)` made an unregistered document class
  indistinguishable from an unsupported claim.
- `DOCUMENT_CLASSES` module-global state made re-opening the same workspace
  trip a redefine guard, and let one test file overwrite another's fixture.
- A losing statement left in `DRAFT` after conflict resolution stayed alive and
  could be published later, recreating the same conflict.

All three were introduced in code written specifically to prevent this class of
error. The lesson is not "be careful"; it is that silent defaults must fail
loudly by construction.

---

## 3. Legal discoveries

Three things must be held separate, and merging them causes errors in both
directions.

| Layer | What it is | Legal status |
|---|---|---|
| **Artifact** | The publisher's document | Copyrighted artwork. `cruise_line_deck_plan` is **CITE_ONLY**: may be referenced, may not be redistributed. |
| **Semantic Model** | Our representation of facts extracted from it | Facts are not protectable. Freely publishable. |
| **Renderer** | Our own drawing of our own model | Ours. No dependency on publisher artwork. |

### Why the public product renders our semantic model

"Render the artifact, never an interpretation of the artifact" is
epistemically excellent — the positions of printed labels are *in* the
document, so marking them is reading rather than interpreting. It is also the
single riskiest thing legally, because it means displaying MSC's artwork.

The resolution keeps both properties. The artifact stays evidence; the product
renders our model. `include_base_page` defaults to `False` in the overlay
renderer, which is internal tooling only.

**This trade has a cost that runs in the opposite direction and must be
managed.** Rendering the artifact was epistemically safe and legally unsafe.
Rendering our own model is legally safe and epistemically unsafe — because now
*we* choose where everything sits, and we have no geometry. The safeguard is
that the layout must be visibly non-metric (§2.10), enforced by the type
system rather than by discipline.

Side benefits: complete control over accessibility, interaction, zoom,
localization, and long-term maintainability.

**Note on general arrangements:** obtaining one is not the same as being
permitted to publish from it. Shipyard GAs are `RESTRICTED` and
`LEGAL_REVIEW_REQUIRED`.

---

## 4. Architecture (frozen)

```
Artifacts                held documents, content-addressed by SHA-256
    ↓
Truth Engine             statements, provenance, confidence, review, conflicts
    ↓
Topology Engine          adjacency, containment, deck hierarchy, block membership
    ↓
Geometry Engine          INTENTIONALLY EMPTY — no dimensioned artifact held
    ↓
Semantic Deck Model      our own representation; ordinal, never metric
    ↓
API                      serves the semantic model
    ↓
Timonelo Frontend        renders the semantic model
```

Knowledge flows downward only. No layer may write upward.

| Layer | Responsibility | Explicitly not responsible for |
|---|---|---|
| **Artifacts** | Hold documents; compute digests from real bytes; record acquisition metadata | Interpreting content |
| **Truth Engine** | Statements, provenance, review workflow, conflict detection, computed confidence, UNKNOWN by construction | Spatial relationships |
| **Topology Engine** | Adjacency, containment, deck hierarchy, neighbour and venue graphs | Distances, coordinates, routes, times |
| **Geometry Engine** | Coordinates, distances, routing, walking times, cross-deck registration | — currently emits nothing |
| **Semantic Deck Model** | Ordinal representation of the topology for rendering | Metric layout; page coordinates |
| **API** | Serve the semantic model with epistemic state and provenance | Deciding what is true |
| **Frontend** | UI, rendering, interaction, animation | Storing or deriving truth |

### Invariants

- Confidence is computed at query time, never stored.
- Only `APPROVED` and `PUBLISHED` statements reach a passenger.
- A document class may only create statement types it can support
  (Statement Authority Matrix).
- Nothing bypasses `Artifact → Evidence → Statement → Review → Published`.
- Conflicts are recorded, never overwritten; losers become `SUPERSEDED`, never
  deleted.

---

## 5. Repository responsibilities

| Repository | Owns | Must not contain |
|---|---|---|
| **timonelo-knowledge-factory** | Artifacts, statements, topology, geometry, provenance, APIs | UI, rendering, animation |
| **timonelo** | UI, rendering, interaction, animation | Artifacts, statements, derived truth |

**Truth must exist only once.**

**Current state does not match this.** The evidence store (1 artifact, 113
statements, review log, conflict log, question registry) lives in **timonelo**,
and the topology and renderers live in **knowledge-factory** — the inverse of
the intended split for the truth half. Cabin JSON files exist in both the
statement store (canonical) and `ships/msc-bellissima/cabins/` (derived, but
committed as if it were data).

This is a known blocker, not an oversight. No code should be written against
the intended boundary until the migration is executed.

---

## 6. Current status

Facts only.

### Held evidence
| | |
|---|---|
| Artifacts held | **1** |
| | `MSC-BEL-ART-001` — MSC Bellissima Deckpläne, 11.2025 DEU |
| | sha256 `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0` |
| | class `cruise_line_deck_plan`, reliability 0.80, CITE_ONLY |
| Statements | 113 authored, **112 published**, 1 superseded |
| Conflicts | 1, resolved |
| Questions registered | 15 per cabin |

### Curation coverage
| | |
|---|---|
| Cabins curated | **14** |
| Of deck 14 (243 cabin cells) | 5.8% |
| Of the ship (2,217 staterooms) | 0.6% |
| Blocks fully curated | 2 — D14-B27 (6/6), D14-B35 (8/8) |
| Decks with topology extracted | 1 of 15 |

### Per-cabin coverage
All 14 curated cabins: **53.3%** — 8 of 15 questions answered.
Per cabin: 6 `DIRECT_EVIDENTIARY`, 2 `DERIVED_DETERMINISTIC`, 7 `UNKNOWN`.

The figure is identical for every cabin because it is set by the Statement
Authority Matrix, not by curation effort. One document class answers eight
questions. **Coverage will not exceed 53.3% for any cabin on this ship until a
second artifact class is acquired**, however many cabins are curated.

### Topology coverage
153 facts — 24 `DIRECT_EVIDENTIARY`, 31 `DERIVED_DETERMINISTIC`, 98 `UNKNOWN`.

### Geometry coverage
**0%.** No coordinate, distance, route or walking time exists. Not a backlog
item — see §2.5.

### Unknown coverage
7 of 15 questions per cabin: hull side, area, door clear width, balcony
dimensions, HVAC riser, noise exposure, vibration. Six are UNKNOWN because the
authority matrix refuses them to a deck plan. One — hull side — is refused by
choice: the deck plan is authoritative for it, but establishing it requires
inferring bow direction from the hull outline rather than reading a printed
marking.

### Blockers
1. **No geometric artifact.** Blocks the entire Geometry Engine.
2. **No MSC licence.** Blocks any surface displaying deck plan artwork.
3. **Repository boundary not migrated.** Truth in the wrong repository.
4. **Contradictory dataset live.** `ontology/bellissima.py` generates 2,508
   cabins and answers cabin 14122 as *BA, 19.0 m², not accessible*. The
   evidence says *IR2, area UNKNOWN, accessible*. Until quarantined, the system
   can answer the same question two ways.
5. **Curation is manual** — deliberately, until one deck is curated by hand.

---

## 7. Next phase

**The bottleneck is no longer architecture. It is evidence acquisition and
curation.**

The scientific foundation is sufficient. Further audit layers now have
diminishing returns compared to acquiring authoritative knowledge. Architecture
changes should **follow** evidence and be justified by a deficiency that real
evidence revealed — not precede it.

Two axes, independent of each other:

- **Widen** (M4): curate more cabins. A fully curated ship at 53.3% coverage.
- **Deepen** (M6): acquire a second artifact class. One accessibility guide
  would lift every already-curated cabin toward 70% without touching a single
  new cabin.

If the goal is a passenger who trusts the page, the second artifact is worth
more per hour than the next two hundred cabins.

Priority order from here:

1. Acquire and curate evidence.
2. Expand the Truth Engine.
3. Expand the Topology Engine.
4. Extend the architecture only when new evidence reveals a real deficiency.
