# Scientific Principles — frozen 2026-08-17

Seven principles. Each is enforced by a mechanism, not by intention. Where a
principle has a known limit, the limit is stated.

---

### P1 · Ground Truth always wins
If the Digital Twin contradicts a held artifact, the twin is wrong. Generated
content is never defended against evidence.
**Enforced by:** the hypothesis namespace; promotion requires an evidence event.
**Cost accepted:** coverage collapses when fabrication is removed. That is the
first accurate measurement, not a regression.

---

### P2 · UNKNOWN is a first-class result
UNKNOWN is computed by comparing the question registry against the statement
graph, never authored. It carries no value. It renders as an explicit gap,
never as silence — a hidden UNKNOWN is indistinguishable from a question never
asked.
**Enforced by:** `TopologyEngine.add()` rejects an UNKNOWN fact carrying a
value; renderers must declare `absence`.

---

### P3 · Deterministic derivation is not direct evidence
`DERIVED_DETERMINISTIC` is reproducible, not certain. A clustering threshold at
2.5 pt instead of 2.2 pt would change every adjacency edge downstream.
**Enforced by:** derivations require a written note; border pattern distinguishes
the states in every render.
**Known limit:** the system does not yet record that two derivations can differ
in strength. IR2 (by elimination) is weaker than BP (unique swatch); both are
labelled identically.

---

### P4 · Render the semantic model, not publisher artwork
The artifact is evidentiary source, not a runtime dependency.
**Enforced by:** the semantic renderer imports nothing that reads a PDF;
`include_base_page` defaults to `False`.

---

### P5 · Geometry requires authoritative geometric evidence
No coordinate, distance, route or walking time may be emitted without a
dimensioned artifact. Uniform spacing states *we know order, we do not know
distance*. Equal sizes state *we know identity, we do not know dimensions*.
**Enforced by:** `SemanticCabin` accepts `ordinal` and refuses page coordinates;
the Geometry Engine emits nothing.

---

### P6 · The renderer must never silently invent facts
A renderer cannot abstain — every element is placed somewhere, at some size, in
some order — so every visual variable carries a claim whether intended or not.
Each must be declared or explicitly nullified.
**Enforced by:** `RenderAudit.assert_complete()` raises on any undeclared
variable.
**Known limit:** the audit catches undeclared variables. It cannot catch a
declaration that is wrong. It forces claims into the open for review; it does
not judge them.

---

### P7 · Every visible statement must be traceable
Every published statement names its artifact, page, locator, reader, date and
review history. Confidence is computed at query time from the document class and
never stored.
**Enforced by:** `StatementEditor.create()` refuses a statement without locator,
reader and date; the Statement Authority Matrix refuses a document class that
cannot support the statement type; publication refuses the reader as approver.

---

## The sentence the whole system rests on

> Evidence does not describe a value. It records how that value came into
> existence.
