# SPEC-007 — Validation Framework

**Status:** Draft · **Deliverable:** 6 · **Runs at:** pipeline stages 4 and 6;
**adjudicates:** SPEC-004

## 1. Purpose

Validation is the gate every pack passes through before it may seal, and the
authority that adjudicates maturity. It is **fail-closed**: a pack seals only if
its report passes at the severity required for its target rung. The report is
retained inside the sealed pack, so any published pack carries the evidence that
it was allowed to exist.

## 2. Layers

Validation is layered; a pack is checked at every layer and the report records
each result.

### L1 — Structural
- Conforms to the canonical schema; required predicates present.
- Types, enums, and units are canonical.
- Identifiers unique and stable within the pack.

### L2 — Provenance
- Every `asserted` fact references a source that exists in the Source Registry.
- The pack's recorded source `content_hash` matches the registry's — the exact
  bytes are pinned (SPEC-003 §2).
- Every `derived` fact references a real `rule_id@version` and existing input
  facts.

### L3 — Evidential / Trust
- No fact's value exceeds its source trust ceiling (invariant 5).
- Corroboration rules satisfied: T3-only facts are held at `Unknown` until a T2+
  source corroborates; T4 never backs a sealed value (SPEC-003 §3.1).
- Each source backs only predicates within its `authority_scope`.

### L4 — Consistency
- No contradictions: `asserted ↔ asserted` and `asserted ↔ derived`. A derived
  fact that contradicts an asserted fact is a blocking failure (the rule or the
  input is wrong).
- Geometric sanity: a cabin has one position; adjacencies are mutual; referenced
  nodes exist.

### L5 — Unknown discipline
- Every eligible predicate is a value or an explicit `Unknown(reason)`; no silent
  nulls or omissions.
- Each `Unknown` is classified (`not_sourced` / `unavailable` / `conflicted`).

### L6 — Determinism / reproducibility
- The `content_hash` recomputes from the canonicalised facts + manifests.
- Every `derived` fact is reproduced by replaying its rule over its inputs
  (SPEC-006 §3.4).

## 3. Severity

Each check has a severity:

- **Blocking** — the pack may not seal at all (L1 schema break, L2 missing
  provenance, L4 asserted↔derived contradiction, L6 non-reproducible hash).
- **Rung-limiting** — the pack may seal, but not above a given rung (an
  unresolved `conflicted` predicate caps at Structured; missing corroboration
  caps below Verified).
- **Advisory** — recorded for review; does not block or cap (e.g. a coverage gap
  that is legitimately `unavailable`).

Fail-closed default: any check whose severity is unproven is treated as blocking
until classified.

## 4. Maturity adjudication

After the layers pass, validation evaluates the SPEC-004 gates bottom-up and
stamps the **highest rung whose gate fully passes**. Rung-limiting failures cap
the result; blocking failures prevent sealing. The adjudicated rung and the full
per-check results are written into the `validation_report` that becomes part of
the sealed pack.

## 5. Outputs

```text
ValidationReport
├── pack_ref (pre-seal draft ref)
├── checks[]     {layer, id, severity, result, detail, offending_fact_ids}
├── conflicts[]  unresolved conflicted predicates
├── adjudicated_maturity   rung or "unsealable"
└── verdict      seal | seal-capped-at(rung) | reject
```

- `seal` / `seal-capped-at(rung)` → the factory proceeds to seal at that rung.
- `reject` → no pack is produced; the draft and its report are retained for
  diagnosis. Nothing partial is ever published.

## 6. Validation invariants

1. Fail-closed: unproven or unresolved states never seal upward.
2. The report is retained in the sealed pack; sealing without a passing report is
   impossible.
3. Validation reads the draft pack and the registries only; it never edits facts
   (it cannot "fix" a pack — a fix is a new draft).
4. The same canonicalisation feeds hashing and validation, so what is validated is
   exactly what is hashed.
