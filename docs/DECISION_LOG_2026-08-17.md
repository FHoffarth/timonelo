# Decision Log — 2026-08-17

Every decision that governs the system. Each records the decision, why it was
made, and what it costs. Nothing here lives only in chat history.

---

### D-001 · The connector performs no trust evaluation
**Decision.** The Truth Engine Connector Bridge performs only deterministic
mechanical transformations. It assigns no trust, credibility or authority
field, and never synthesizes an authority string.
**Rationale.** A connector that assigns trust becomes a partial Truth Engine,
so trust policy changes require connector changes. Synthesizing
`"Authority for msc-bellissima"` when no publisher is declared inserts a
fabricated string into an artifact record.
**Consequence.** The Truth Engine receives `source_type` and derives trust
itself. `artifact.schema.json` no longer requires `trust_level`. Enforced by CI.
*(Formalised as ADR-0001.)*

---

### D-002 · Ground Truth always overrides generated content
**Decision.** Where the Digital Twin contradicts a held artifact, the artifact
wins and the twin is wrong.
**Rationale.** `cabins/14122.json` asserted `"cabin_category": "Balcony"`,
`"has_balcony": true`, `"accessible": "UNKNOWN"`, citing
`art-bellissima-ga-2019` — a Chantiers de l'Atlantique general arrangement that
does not exist in the repository. The held deck plan shows cell 14122 filled
`RGB(238,168,196)`, the legend swatch for *Deluxe Innenkabine*, in an inner
block with no hull contact, carrying the `H` symbol. The cabin is interior and
accessible. Both fields were inverted.
**Consequence.** Generated content is never defended against evidence. Coverage
fell sharply when the fabricated dataset was removed; that is the first
accurate measurement the system has produced.

---

### D-003 · Fabricated geometry quarantined, not deleted
**Decision.** 24 untraceable files moved to
`hypothesis/_quarantined_2026-08-17/`. Nothing deleted.
**Rationale.** Deletion destroys the record of what was believed and why.
Quarantine preserves provenance while preventing contamination of Ground Truth.
**Consequence.** `GEOMETRIC_PROOFS.md`, `distance_matrix.parquet`,
`navigation.yaml`, `routing.graphml` and all deck YAML are retained but may not
seed any engine. Promotion requires an evidence event, not a file edit.

---

### D-004 · Hypothesis namespace introduced
**Decision.** Generated and unevidenced material lives in a namespace that
cannot be mistaken for, or read by, the truth path.
**Rationale.** Semantic separation depends on every future query remembering to
check origin. Eventually one will not.
**Consequence.** Duplicate storage is accepted over reliance on developer
discipline. Promotion from hypothesis to ground truth requires an evidence
event; there is no automatic path.

---

### D-005 · Topology before geometry
**Decision.** Build the topological twin first. The Geometry Engine stays
empty until authoritative geometric evidence exists.
**Rationale.** The held deck plan contains no scale bar, no ratio, no
dimensions and no frame datum — the only measurements in six pages are bed
sizes (140×200 cm). Drawn hull heights for decks 14, 15 and 16 differ (511.2,
514.8, 517.0 pt) with no common datum, so cross-deck registration is not
derivable either.
**Consequence.** "How far is the buffet", "how long will it take", "which route
is wheelchair accessible", "what is directly above my cabin" all return
UNKNOWN. "Which deck is above", "who are my neighbours", "which block am I in"
are answerable.

---

### D-006 · The renderer must never invent geometry
**Decision.** Renderers emit no wall positions, corridor widths, distances,
ship coordinates, routing geometry or travel times.
**Rationale.** Text can say UNKNOWN; a map cannot. Empty space on a drawing
reads as "nothing is there", not "we do not know". A corridor drawn at a
plausible width reads as measured.
**Consequence.** No floorplan is rendered. The `does_not_assert` list is
emitted in every render manifest.

---

### D-007 · Semantic Deck Model
**Decision.** The renderer consumes our own semantic representation. Layout is
ordinal and uniform by construction; the type refuses page coordinates.
**Rationale.** Page position is not ship position. Carrying the artifact's
relative spacing into our model reintroduces the publisher's geometry through
layout rather than through coordinates. Uniform spacing is the metro-map
convention: nobody measures a Tube map because uniform spacing announces that
distance carries no information.
**Consequence.** `SemanticCabin` takes `ordinal`, not `x`/`y`. Proportional
layout is not available, and the answer to a request for it is that the
Geometry Engine is empty.

---

### D-008 · Artifact-first
**Decision.** Nothing enters the system except through
`Artifact → Evidence → Statement → Review → Published`. No override dicts, no
direct writes, no importer-created statements.
**Rationale.** A value handed in at call time carries no artifact, no locator
and no review, and reaches a passenger indistinguishable from an evidenced one.
**Consequence.** Volatile-domain evaluators (port, weather, visa, dining,
transport, embarkation) return `None` until sourced. Override paths raise.

---

### D-009 · Living Deck Plan
**Decision.** The passenger-facing surface is a deck view that exposes, per
object, its epistemic state, provenance and review history — with uncurated
objects visible as explicit gaps.
**Rationale.** A deck rendered with only its curated cabins claims those are
the only cabins.
**Consequence.** Deck 14 renders 14 cells of which 10 are dotted "exists, not
yet curated", with the 239 remaining stated numerically.

---

### D-010 · Legal separation of evidence and product
**Decision.** The artifact is evidentiary source, not a runtime dependency. The
product never displays publisher artwork.
**Rationale.** `cruise_line_deck_plan` is CITE_ONLY. Extracted facts are not
protectable and may be published; the page artwork is MSC's copyright.
**Consequence.** `include_base_page` defaults to `False`. Full control over
accessibility, zoom, localization and maintainability is gained as a
side-effect. A licence conversation with MSC is required before any
artwork-based surface ships.

---

### D-011 · Repository responsibilities
**Decision.** Knowledge Factory owns artifacts, statements, topology, future
geometry and APIs. Timonelo owns UI, rendering, interaction and animation. No
duplicated datasets, no copied cabin files, no copied truth.
**Rationale.** Two Bellissima datasets already disagreed, and the one with more
content was the wrong one.
**Consequence.** **Not yet true.** The evidence store is in Repo B and the
topology in Repo A. Migration is a blocker, recorded in
`CURRENT_PROJECT_STATUS.md`.

---

### D-012 · Rendering is an epistemic claim
**Decision.** Every renderer declares, per visual variable, the claim it
encodes or an explicit nullification. Enforced by `RenderAudit`.
**Rationale.** A renderer cannot abstain. The first Semantic Deck render made
two claims the Truth Engine had refused: vertical/horizontal placement implied
fore/aft and port/starboard when `cabin.hull_side` is UNKNOWN, and block height
tracking cabin count read as physical extent. Both passed a review that was
specifically looking for fabricated geometry.
**Consequence.** Nine audited variables. Undeclared use raises before emit.
The audit catches undeclared variables; it cannot catch a wrong declaration.
*(Formalised as ADR-0004.)*

---

### D-013 · Confidence is computed, never stored
**Decision.** No schema contains a writable confidence field.
**Rationale.** A stored confidence drifts from reality. The predecessor system
defaulted every evidence field to `VERIFIED / 0.98 / chief_knowledge_architect`
and computed audit scores from fabricated counters.
**Consequence.** Confidence derives from the artifact's document class at query
time. Ordinal, not probabilistic, and never rendered as a number.

---

### D-014 · Conflicts are recorded, never overwritten
**Decision.** A new statement contradicting an answerable one creates a
conflict. Both are marked, resolution requires a written reason, the loser
becomes `SUPERSEDED`.
**Rationale.** `SUPERSEDED` and `REJECTED` are different claims: rejected means
the reading was wrong, superseded means it was right for its source and has
been replaced.
**Consequence.** Nothing disappears. Contested answers still serve the
published value but carry a `contested` flag that renderers must disclose.
