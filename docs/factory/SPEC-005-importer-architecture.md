# SPEC-005 — Importer Architecture

**Status:** Draft · **Deliverable:** 4 · **Scope:** architecture only

> This spec designs the importer contract. It deliberately **does not implement
> multiple importers**. The goal is that, once this contract is fixed, adding the
> hundredth importer is a bounded, testable unit of work with no changes to shared
> code.

## 1. What an importer is

An importer is a pure, versioned function that turns one raw source artifact into
canonical staging records:

```text
normalize(raw_artifact, source_meta) -> NormalizedRecordSet
```

- **Pure** — output depends only on the inputs; no network, clock, randomness, or
  global state.
- **Stateless** — holds no cross-ship or cross-run state.
- **Versioned** — `importer_version` participates in the determinism contract
  (SPEC-002 §4); changing an importer re-derives affected packs into new packs.

## 2. Keying: per format, never per ship

Importers are keyed by **(publisher_class, format, schema_version)** — for
example "cruise-line deck-plan PDF, layout A" — **not** by ship. One importer
normalises every ship that ships that source in that format. This is the single
most important scaling decision: ship count does not multiply importer count.

Importer selection is **data-driven**: the Source Registry entry (SPEC-003)
declares publisher class, format, and version; the factory looks up the matching
importer. No ship name ever appears in a `switch`.

## 3. What an importer may and may not do

**May:**
- Parse the raw artifact and emit `NormalizedRecordSet` records.
- Attach provenance to every record: `source_id`, a precise `locator` (page,
  table cell, coordinate, line), and the source's `content_hash`.
- Emit `Unknown(not_sourced)` for predicates the artifact does not cover.
- Translate labels to the canonical language while retaining the original.

**May not:**
- Derive relationships (that is SPEC-006). Importers emit only what the source
  *asserts*.
- Resolve conflicts, merge across sources, or touch other ships' data.
- Write to persistence or read another pack.
- Raise a value's trust above its source's level.
- Contain ship-specific branches. If a ship "needs special handling," it is one
  of: (a) a genuinely new source format → a **new importer**; (b) a correction
  → a registered **override source** with its own provenance and trust. Never a
  hardcoded exception.

## 4. The canonical boundary

This spec is where the architecture's rule — *ship-specific configuration belongs
with ship data, not algorithm code* — is enforced. Importers are shared algorithm
code. Everything ship-specific is data flowing through them. A code review that
finds a ship identifier inside an importer has found a defect.

## 5. NormalizedRecordSet contract

```text
NormalizedRecordSet
├── source_id
├── importer_id + importer_version
└── records[]
    ├── subject          canonical node/edge ref
    ├── predicate        canonical predicate (shared vocabulary, SPEC-003 §4)
    ├── value            typed value | Unknown(reason)
    ├── locator          precise position within the raw artifact
    └── original         pre-translation label + language, when applicable
```

Records are **asserted** by construction. The assemble stage (SPEC-002 §3.1)
places them and attaches full provenance; the importer's job ends at emitting
faithful, located records.

## 6. Capability declaration

Each importer declares, as data, the predicates it *can* populate from its format
and the trust mapping it applies. This lets the factory:

- verify at registration time that a source's `authority_scope` is achievable by
  its importer, and
- report coverage gaps as an artifact of declared-vs-populated predicates rather
  than as silent absence.

## 7. Testing contract (why adding one is cheap)

Every importer ships with **golden fixtures**: a retained raw sample →
expected `NormalizedRecordSet`. Because importers are pure, the test is exact and
hermetic. Adding importer N means: write it, add fixtures, pass the shared
importer conformance suite (provenance present on every record, no derivation, no
ship branch, deterministic output). No integration with the rest of the factory is
required to prove it correct.

## 8. Reference sketch (illustrative — not an implementation)

```python
# Illustrative signature only. One importer, to fix the shape.
def normalize(raw: RawArtifact, meta: SourceMeta) -> NormalizedRecordSet:
    """Pure. No I/O. No ship-specific branches. Emits asserted records only."""
    ...
```

Building the *first* real importer (for the reference ship) is future work under
the roadmap. This spec exists so that importer #2 through #1000 cost the same as
importer #1.
