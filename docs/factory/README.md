# The Knowledge Factory

The Knowledge Factory is the pipeline that turns official ship sources into
sealed, immutable **Knowledge Packs**. It exists so that producing ship #1000 is
as disciplined and as cheap as producing ship #2 — without ever letting the
output sound more certain than its evidence.

This directory specifies the factory. It does **not** import ships. Importing is
deliberately deferred until the factory is correct.

## Where this sits relative to the foundation

The authoritative foundation for Timonelo is the existing project
documentation — [vision](../vision.md), [product](../product.md), and
especially [architecture](../architecture.md). Those documents define the
dependency direction, the module boundaries, and the governing principle:

> **Timonelo must never sound more certain than its evidence.**

The handoff that commissioned this work refers to `SPEC-000` (foundation) and
`SPEC-001` (Knowledge Pack format) as authoritative. Those numbered documents are
not present in this repository; the specs here are grounded on
`docs/architecture.md` as the embodiment of the foundation. Where a canonical
`SPEC-000`/`SPEC-001` is later located, these documents defer to it and must be
cross-checked against it — this set never overrides the foundation, it operates
within it.

## The pipeline

```text
Official Sources
      ↓  acquire        (Source Registry — SPEC-003)
Retained raw artifacts
      ↓  normalize      (Importer Architecture — SPEC-005)
Canonical staging records
      ↓  assemble
Draft Knowledge Pack
      ↓  validate       (Validation Framework — SPEC-007)
      ↓  derive         (Relationship Builder — SPEC-006)
      ↓  re-validate    (Validation Framework — SPEC-007)
      ↓  seal + stamp   (Ship Maturity Model — SPEC-004)
Immutable Knowledge Pack  ──►  Explorer · Cabin Briefing · Spatial Evidence Engine
```

Everything to the left of the sealed pack is the **factory** (a producer).
Everything to the right is a **consumer** (read-only). Consumers never write back
into the graph or the pack. This preserves the foundation's dependency direction.

## Specification set

| Spec | Title | Deliverable |
|------|-------|-------------|
| [SPEC-002](SPEC-002-knowledge-factory.md) | Knowledge Factory | The master pipeline and the Knowledge Pack contract |
| [SPEC-003](SPEC-003-source-registry.md) | Source Registry | Canonical sources: trust, versions, languages, coverage |
| [SPEC-004](SPEC-004-ship-maturity-model.md) | Ship Maturity Model | Structured → Verified → Field Validated → Knowledge Complete |
| [SPEC-005](SPEC-005-importer-architecture.md) | Importer Architecture | The importer contract (architecture only — no importers built) |
| [SPEC-006](SPEC-006-relationship-builder.md) | Relationship Builder | Deterministic derivation rules |
| [SPEC-007](SPEC-007-validation-framework.md) | Validation Framework | Canonical validation and maturity adjudication |

## The invariants (the factory constitution)

Every stage, every spec, and every future importer inherits these. A change that
violates one of them is a defect, not a trade-off.

1. **Immutability by version.** A Knowledge Pack is frozen the moment it is
   sealed and is addressed by the SHA-256 of its content. Corrections, better
   sources, and higher maturity never mutate a pack — they produce a *new* pack
   in an append-only history. (See [artifact-identity discipline]: identity is
   commit + build + artifact id + hash, never name alone.)

2. **Provenance on every fact.** No fact enters a pack without a traceable
   origin: either a registered source (asserted) or a versioned rule plus its
   inputs (derived).

3. **Asserted and derived are always distinguishable.** A fact read from a source
   and a fact computed by a rule are different kinds and are never conflated.

4. **Unknown is first-class and propagates.** Absence of evidence is a typed,
   explicit value — never a silent null and never a guess. If a rule's inputs are
   Unknown, its output is Unknown.

5. **Confidence never exceeds evidence.** A claim's confidence ceiling is the
   trust level of its backing sources. Nothing downstream may raise it.

6. **Determinism.** `pack = F(sources@hash, rules@version)`. Re-running the
   factory on the same inputs reproduces the identical pack hash. This is the
   property that makes scale cheap.

7. **The factory does not reason.** No scoring, no ranking, no recommendation, no
   AI inference, no commercial optimisation, no user personalisation enters a
   pack. Interpretation lives strictly downstream of the sealed pack, and even
   there may not strengthen a claim.

[artifact-identity discipline]: recorded in the operator's working notes; the
same rule is applied here to Knowledge Pack identity.
