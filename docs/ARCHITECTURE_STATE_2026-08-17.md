# Timonelo — Architecture State, 2026-08-17

Canonical architecture document. Supersedes every architectural statement made
in chat. If this document and a chat message disagree, this document wins.

---

## 1. What Timonelo is

An evidence-first Digital Twin of a cruise ship. The product is not a viewer
and not a knowledge platform: it is a ship model that can say, for any visible
statement, **why it believes it** — and can show, equally visibly, what it does
not know.

The first ship is MSC Bellissima. The first cabin is 14122.

---

## 2. Repository responsibilities

Two repositories, one logical system.

| Repo | Owns | Must not contain |
|---|---|---|
| **timonelo-knowledge-factory** (A) | Artifacts, statements, topology, future geometry, APIs | UI, rendering, animation |
| **timonelo** (B) | UI, rendering, interaction, animation | Artifacts, statements, derived truth |

**This boundary is a target, not the current state.** See §9 and
`CURRENT_PROJECT_STATUS.md` §Blocked. Today the evidence store lives in Repo B
and the topology in Repo A — the inverse of the intended split for the truth
half. No code should be written against the intended boundary until the
migration is executed.

---

## 3. Pipeline

```
Artifacts            held documents, content-addressed by SHA-256
   |
Truth Engine         statements, provenance, review state, conflicts
   |
Topology Engine      adjacency, containment, block membership, deck hierarchy
   |
Geometry Engine      INACTIVE — no held artifact supports geometry
   |
Semantic Deck Model  our own representation; ordinal, never metric
   |
API                  serves the semantic model
   |
Timonelo Frontend    renders the semantic model
```

Knowledge flows one way. No layer may write upward.

---

## 4. Engine responsibilities

### Truth Engine (`timonelo/src/timonelo/evidence/`)
Statements, provenance, computed confidence, review workflow, conflict
detection and resolution. Answers a registered question for an entity, or
returns UNKNOWN. Consults only `APPROVED` and `PUBLISHED` statements.

Components: `registry.py` (sole issuer of artifact IDs), `importer.py` (PDF in,
artifact out, nothing else), `editor.py` (sole creator of statements),
`review.py` (five-state workflow), `conflicts.py`, `truth.py`, `authority.py`
(Statement Authority Matrix), `workspace.py`, `cli.py`.

### Topology Engine (`knowledge-factory/src/topology/engine.py`)
Adjacency, containment, deck hierarchy, block membership, neighbour graph.
Emits `TopologyFact` records carrying an epistemic state. Refuses a
`DIRECT_EVIDENTIARY` fact without provenance, a `DERIVED_DETERMINISTIC` fact
without a stated derivation, and an `UNKNOWN` fact carrying a value.

Owns no distances, coordinates, routes or times.

### Geometry Engine
**Inactive by evidence, not by omission.** Owns coordinates, distances,
routing, walking times, cross-deck registration. Emits nothing. See
`GEOMETRY.md` for the measurements that establish why.

### Semantic Deck Model / Renderer
Our own representation, rendered from our own model. Reads no artifact at
runtime. Layout is ordinal and uniform by construction: the type refuses page
coordinates.

---

## 5. Epistemic model

Three states, and they are not interchangeable.

| State | Meaning | Requirement |
|---|---|---|
| `DIRECT_EVIDENTIARY` | Read off a held artifact | Provenance: artifact, page, locator, reader, date |
| `DERIVED_DETERMINISTIC` | Computed from held-artifact readings by a stated, reproducible rule | A written derivation |
| `UNKNOWN` | No held artifact supports it | Carries no value |

**A deterministic derivation is reproducible, not certain.** A clustering
threshold at 2.5 pt instead of 2.2 pt would change every adjacency edge
downstream. The distinction must remain visible in APIs and renderers and must
not collapse into a known/unknown binary.

Confidence is computed from the artifact's document class at query time and is
never stored.

### Statement Authority Matrix
A document class may only create statement types it is capable of supporting.
A `cruise_line_deck_plan` can establish deck, side, category, connecting door
and lift-lobby membership. It cannot establish an area, a door width or a
distance — those need a shipyard general arrangement or an onboard survey.
Enforced at statement creation, not by review.

Three properties are held separate and must not be merged: **epistemic
authority** (can this class establish the fact), **acquisition** (can we obtain
a copy), **use permission** (may we publish from it).

---

## 6. Rendering philosophy

**Render the semantic model, never publisher artwork.** The deck plan is
evidence, not a runtime dependency.

**Every visual decision is an epistemic claim** (ADR-0004). A renderer cannot
abstain — every element is placed somewhere, at some size, in some order — so
every visual variable carries a claim whether intended or not. Renderers
declare what each variable encodes or explicitly nullify it, enforced by
`RenderAudit.assert_complete()`.

Uniform spacing states *we know order, we do not know distance*. Equal cell
sizes state *we know identity, we do not know dimensions*. Both are scientific
statements, not styling.

Epistemic state is carried by **border pattern**, not colour, so it survives
greyscale and colour-blindness.

Absence is a claim. Uncurated objects render as explicit gaps.

---

## 7. Legal constraints

`cruise_line_deck_plan` is **CITE_ONLY**.

- Facts extracted from a deck plan are not protectable and may be published.
  The 32 statements are safe.
- The page artwork is MSC Cruises' copyright. Displaying it in a
  passenger-facing product requires permission.
- Therefore the product renders our semantic model, and the artifact stays
  evidence. `include_base_page` defaults to `False` in the overlay renderer.
- Shipyard general arrangements are `RESTRICTED` and
  `LEGAL_REVIEW_REQUIRED` — obtaining one does not by itself permit publishing
  from it.

---

## 8. Current blockers

1. **Geometry.** No held artifact contains a scale, ratio, dimension or datum.
   Unblocked only by a dimensioned general arrangement or a first-party onboard
   survey.
2. **Coverage.** 4 of 2,217 staterooms curated, from 1 artifact.
3. **Repository boundary.** Truth lives in Repo B, contrary to §2.
4. **Contradictory dataset live in Repo B.** `ontology/bellissima.py` generates
   2,508 cabins and asserts cabin 14122 is category BA, 19 m², not accessible.
   The evidence says IR2, area UNKNOWN, accessible. Not yet quarantined.
5. **Licence.** No agreement with MSC covering artwork display.

---

## 9. Next milestones

See `ROADMAP_NEXT.md`. Summary: quarantine the legacy ontology in Repo B,
execute the repository migration, curate the remaining deck-14 cabins, open the
MSC licence conversation, pursue a dimensioned drawing.
