# SPEC-002 — Knowledge Factory

**Status:** Draft · **Depends on:** foundation (`docs/architecture.md`) ·
**Governs:** SPEC-003 … SPEC-007

## 1. Purpose

Define the pipeline that produces a sealed **Knowledge Pack** for one ship from
official sources, and define the Knowledge Pack contract that pack consumers
depend on. The factory optimises for reproducibility and provenance so that
adding the thousandth ship requires no new bespoke logic.

## 2. The Knowledge Pack

A Knowledge Pack is the canonical, immutable, content-addressed representation of
a single ship at a single revision. It is the only artifact the factory emits and
the only artifact consumers read.

### 2.1 Shape

A pack is a set of **facts** over a ship's structural graph (decks, cabins,
venues, circulation, connections, coordinates), plus the metadata needed to trust
and reproduce it.

```text
KnowledgePack
├── identity
│   ├── ship_ref            stable ship identifier (not a source id)
│   ├── pack_version        monotonic revision number for this ship
│   ├── content_hash        SHA-256 over the canonicalised fact set + rules manifest
│   ├── parent_hash         previous sealed pack for this ship, or null
│   ├── sealed_at           timestamp of sealing
│   └── maturity            adjudicated rung (SPEC-004)
├── manifests
│   ├── sources[]           source_id + version + content_hash used (SPEC-003)
│   └── rules[]             rule_id + rule_version applied (SPEC-006)
├── facts[]                 the graph — see 2.2
└── validation_report       the report that authorised sealing (SPEC-007)
```

### 2.2 The fact

Every statement in a pack is a fact with an explicit kind, value, and provenance.

```text
Fact
├── id            stable within the pack
├── subject       node/edge the fact is about (e.g. cabin:8204)
├── predicate     canonical field (e.g. deck, adjacency.below, distance_to.lift)
├── value         a typed value OR the first-class Unknown (see 2.3)
├── kind          asserted | derived
├── provenance
│   ├── asserted → sources[]: {source_id, locator, retrieved_hash}
│   └── derived  → {rule_id, rule_version, inputs: [fact_id, …]}
└── confidence_ceiling   from source trust (asserted) or min(inputs) (derived)
```

`asserted` facts come from a source via an importer. `derived` facts come from
the Relationship Builder. The two are never merged into an undifferentiated
"value" — invariant 3.

### 2.3 Unknown

`Unknown` is a typed value, not a missing key, with a reason:

- `not_sourced` — no source yet covers this predicate (a coverage gap; may be
  closed by a higher-maturity re-derivation).
- `unavailable` — no reliable source is expected to exist (a genuine limit).
- `conflicted` — sources disagree and the conflict is unresolved (blocks
  maturity above Structured for that predicate).

A predicate that could carry a value but does not **must** carry an `Unknown`,
never be omitted. This is what lets consumers show a limitation instead of
implying one does not exist.

### 2.4 Immutability

A pack is sealed by computing `content_hash` over the canonicalised fact set plus
the source and rule manifests. After sealing it is frozen. A correction is a new
pack: same `ship_ref`, incremented `pack_version`, `parent_hash` pointing at the
prior seal. Packs form an append-only chain per ship. Nothing ever edits a sealed
pack in place.

## 3. Pipeline stages

Each stage has a typed input and output contract. A stage may only read its input
and its declared registries; it may not reach forward or backward.

| # | Stage | Input | Output | Spec |
|---|-------|-------|--------|------|
| 1 | Acquire | Official source | Registered source + retained raw artifact (hashed) | SPEC-003 |
| 2 | Normalize | Raw artifact + source meta | Canonical staging records (asserted, provenance-tagged) | SPEC-005 |
| 3 | Assemble | Staging records | Draft pack (conflicts recorded, not resolved) | this spec |
| 4 | Validate (pre) | Draft pack | Validation report; pass/fail | SPEC-007 |
| 5 | Derive | Validated draft pack | Draft pack + derived facts | SPEC-006 |
| 6 | Validate (post) | Derived pack | Validation report incl. derivation checks | SPEC-007 |
| 7 | Seal + stamp | Passing pack | Immutable pack + maturity rung | SPEC-004 |
| 8 | Publish | Sealed pack | Available to consumers (read-only) | consumers |

### 3.1 Assemble (stage 3)

Assembly merges normalized records into one draft graph under the canonical
schema. Assembly is **mechanical**: it places each record on its subject and
predicate and attaches provenance. When two sources assert different values for
the same predicate, assembly records **both** as a `conflicted` state and defers
to validation — it never picks a winner silently. Assembly derives nothing; that
is stage 5's job.

### 3.2 Ordering rationale

Validation runs **before** derivation so rules never build on an invalid graph,
and **again after** derivation so derived facts are held to the same contracts as
asserted ones. Sealing happens only after the post-derivation report passes at the
severity required for the target rung.

## 4. Determinism contract

The factory is a pure function of its versioned inputs:

```text
pack.content_hash = F( sources@content_hash , importers@version , rules@version )
```

Consequences that every implementation must honour:

- No wall-clock, randomness, network, or environment may influence pack content.
  `sealed_at` is metadata outside the hashed fact set.
- Re-running the factory over the recorded source hashes and rule versions must
  reproduce the identical `content_hash`. A mismatch is a factory defect.
- Canonicalisation (stable key ordering, normalised number/enum forms) is defined
  once and shared by hashing and validation so the hash is stable across
  platforms.

## 5. What the factory must never do

- Emit a value not backed by a source or a rule.
- Emit a score, ranking, recommendation, or verdict.
- Resolve a source conflict by preference, recency, or heuristic without an
  explicit, provenance-recorded rule.
- Raise a claim's confidence above its source trust ceiling.
- Carry ship-specific logic in shared code (see SPEC-005 §4).

## 6. Consumers (out of factory scope, stated for boundary)

Explorer, Cabin Briefing Generator, and the Spatial Evidence Engine read sealed
packs. They may simplify language and select what to show. They may **not**
strengthen a claim, invent a value, hide an `Unknown`, or write back into a pack.
The landing page's current "Highly Recommended / Final Verdict / scoring" framing
is marketing copy that predates this spec and is inconsistent with invariant 7; it
must not be taken as a consumer contract.
