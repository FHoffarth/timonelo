# SPEC-004 — Ship Maturity Model

**Status:** Draft · **Deliverable:** 2 · **Adjudicated by:** SPEC-007

## 1. Purpose

Define the four maturity rungs a ship can reach and the objective, falsifiable
gate for each. Maturity communicates *how complete and how corroborated* a ship's
knowledge is, without ever inflating individual claims.

## 2. Maturity is a property of the sealed pack, not a mutation

A rung is **stamped on a sealed pack** by the Validation Framework. Raising a
ship's maturity means producing a *new* pack (more/better sources, re-derivation)
that satisfies a higher gate — never editing an existing pack. Maturity is thus
reproducible: given the pack's sources and rules, the adjudicated rung is
recomputable.

Gates are **monotonic**: a pack cannot be stamped at a rung unless it also
satisfies every lower rung.

## 3. The four rungs

### 3.1 Structured

The pack exists, is well-formed, and is honest about what it lacks.

**Gate:**
- Conforms to the canonical schema; identifiers stable and unique.
- Every predicate that could carry a value carries a value **or** an explicit
  `Unknown` (no silent omissions).
- Every asserted fact has valid provenance into a registered source.
- May be single-source; may be machine-produced with no human review.
- Derived facts are **not** required.

### 3.2 Verified

The pack's asserted facts are trustworthy and internally consistent, and its
deterministic relationships have been built.

**Gate (adds to Structured):**
- Every sealed (non-`Unknown`) asserted fact is backed within trust rules
  (SPEC-003 §3): T0–T2 sole backing, or T3 corroborated by ≥ T2.
- No unresolved `conflicted` predicates.
- Relationship Builder has run; all derived facts validate (SPEC-007 §3–4) and
  reproduce from their rules.
- Coverage thresholds met for the ship's defined structural set — e.g. all decks
  present, all cabins present with a position, all named venues located.

### 3.3 Field Validated

An independent ground-truth check has confirmed a defined sample of the pack.

**Gate (adds to Verified):**
- A defined sample of cabins/venues is confirmed against an *independent* second
  channel (independent source, on-board observation, dated photograph).
- Each validation event is itself recorded as provenance (what was checked, by
  what, when) and retained.
- Discrepancies found are reconciled and the reconciliation is provenance-recorded
  before the rung is stamped; an open discrepancy blocks the rung.

### 3.4 Knowledge Complete

The ship is fully covered, corroborated, and every remaining gap is *justified*.

**Gate (adds to Field Validated):**
- 100% of defined predicates for 100% of cabins are at Verified backing or above.
- Field-validated sample meets or exceeds the completeness threshold.
- Zero open conflicts and zero *unexplained* unknowns: every remaining `Unknown`
  is classified `unavailable` with a recorded reason — a genuine limit of the
  world, never a "not done yet." Any `not_sourced` unknown disqualifies this rung.

## 4. What maturity is not

- It is **not** a score, rating, or quality rank of the ship. It describes the
  *knowledge*, not the vessel.
- It does **not** raise any individual claim's confidence. A single fact backed by
  one T1 source has the same ceiling in a Structured pack and a Knowledge Complete
  pack; maturity summarises coverage and corroboration, not per-claim certainty.
- It is **not** a promise to consumers about experience. Consumers may display the
  rung as provenance, framed as knowledge completeness.

## 5. Adjudication

The Validation Framework computes the **highest rung whose gate fully passes** and
stamps exactly that rung on the pack. If the top gate that passes is below the
target, the pack seals at the lower rung (or, for blocking failures, does not seal
at all — SPEC-007 §5). The adjudication is part of the sealed
`validation_report`.
