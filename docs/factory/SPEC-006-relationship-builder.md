# SPEC-006 — Relationship Builder

**Status:** Draft · **Deliverable:** 5 · **Runs at:** pipeline stage 5

## 1. Purpose

The Relationship Builder derives new facts from the assembled graph using
deterministic, versioned rules. It is the only stage allowed to *create* facts
that no source asserted — and it is bound by strict rules so that a derived fact is
always as honest, as traceable, and as reproducible as an asserted one.

## 2. The rule contract

A rule is a pure function over the pack graph that returns derived facts:

```text
rule(pack) -> [DerivedFact]
```

Each `DerivedFact` carries:

```text
DerivedFact
├── subject, predicate, value        value may be Unknown(reason)
├── kind = derived
├── rule_id + rule_version
├── inputs: [fact_id, …]             the exact facts this depends on
└── confidence_ceiling = min(ceiling of inputs)   never higher than any input
```

Rules are **versioned**. Changing a rule's logic is a new `rule_version`, which
re-derives affected ships into new packs (SPEC-002 §4). The `rules[]` manifest in
the pack pins which versions produced it.

## 3. Hard constraints

1. **Read-only over assertions.** A rule may read any fact but may only *write*
   `derived` facts. It can never overwrite or "correct" an asserted fact.
2. **Unknown propagates.** If any required input is `Unknown`, the output is
   `Unknown` with reason `not_sourced` (or `conflicted` if inputs conflict). A
   rule never fills a gap by assumption. (Invariant 4.)
3. **No confidence inflation.** A derived fact's ceiling is the minimum of its
   inputs' ceilings. Deriving never manufactures certainty. (Invariant 5.)
4. **Full reproducibility.** Given `(rule_version, inputs)`, the output is exactly
   reproducible. Validation replays derivations to confirm (SPEC-007 §3).
5. **Geometry only — no inference of experience.** Rules derive *structural*
   relationships. They may compute exposure and distance; they may **not**
   translate those into predicted loudness, comfort, or a recommendation. That
   line is the boundary between the factory and interpretation.
6. **No cross-ship input.** A rule sees one pack. It cannot borrow "typical"
   values from other ships — that would be hidden inference.

## 4. Rule catalogue (initial, deterministic)

Each rule states its inputs and its output predicate. All are pure geometry over
the pack.

| Rule | Inputs | Derives |
|------|--------|---------|
| **Vertical adjacency** | deck index + footprint coordinates of two cabins | `adjacency.above` / `adjacency.below` |
| **Horizontal adjacency** | same-deck cabins + coordinates | `adjacency.beside[]` |
| **Vertical exposure** | cabin footprint vs. venue footprint on adjacent deck | `exposure.structural` (e.g. venue above/below) — an *exposure flag*, not loudness |
| **Circulation proximity** | cabin centroid + lift/stair coordinates | `distance_to.lift`, `distance_to.stair` (straight-line, explicitly **not** a walking route) |
| **Venue proximity** | cabin centroid + venue coordinates | `distance_to.venue[]` (straight-line) |
| **Longitudinal band** | cabin position vs. ship length | `position.longitudinal` = forward / mid / aft |
| **Vertical band** | deck index vs. deck range | `position.vertical` = low / mid / high |

Straight-line distances are labelled as such in the predicate semantics so a
consumer can never present them as walkable routes (the product doc's Walking
Distance caution). Any of these outputs is `Unknown` whenever its coordinate
inputs are `Unknown`.

## 5. Determinism and ordering

- Rules are applied in a defined, versioned order recorded in the `rules[]`
  manifest. A rule may consume the derived output of an earlier rule **only if
  that dependency is declared**, keeping the derivation a pure, replayable DAG.
- No rule reads wall-clock, randomness, or external data.
- Re-running the catalogue over the same assembled pack yields byte-identical
  derived facts.

## 6. What the builder must never derive

- Scores, rankings, recommendations, verdicts.
- "Likely" or "typical" values inferred from other ships or priors.
- Any value that raises a claim above its evidentiary ceiling.
- Experience predictions (perceived noise, sea comfort) from structural exposure.
