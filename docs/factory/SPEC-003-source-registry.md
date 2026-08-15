# SPEC-003 — Source Registry

**Status:** Draft · **Deliverable:** 1 · **Consumed by:** SPEC-005, SPEC-007

## 1. Purpose

The Source Registry is the single canonical record of every official source the
factory is allowed to trust. It answers, for any fact in any pack: *what backed
this, how much can it be trusted, which version was used, in what language, and
what did that source actually cover?*

The registry is **data, not code**, and it is **append-only**. It lives under
`data/` (registry entries are reviewable; retained raw artifacts live in the
Git-ignored `data/source/`). A source is never edited in place; a changed source
is a new version that `supersedes` the old.

## 2. Source entry

```text
Source
├── source_id        stable canonical id (publisher + slug + version)
├── publisher        the issuing body
├── publisher_class  cruise_line | shipyard | class_society | regulator | reference | community
├── title
├── locator          URL or physical/archival reference
├── trust_level      T0 … T4 (see §3)
├── version          publisher's edition/revision label
├── retrieved_at     when the artifact was captured
├── content_hash     SHA-256 of the retained raw artifact
├── language         BCP-47 tag (e.g. en, it, de)
├── coverage[]       canonical predicates this source speaks to (§4)
├── authority_scope  the predicates this source may *back* (subset of coverage)
├── supersedes       prior source_id, or null
└── notes            capture context, limitations, known errata
```

A pack's `sources[]` manifest references entries by `source_id` **and**
`content_hash`, so a pack is pinned to the exact bytes that were read. If the
registry entry and the pack's recorded hash disagree, validation fails
(SPEC-007 §3) — the source was changed after the pack was built.

## 3. Trust levels

Trust is a small, ordered, closed set. It is a property of the *source*, and it
sets the **confidence ceiling** of any fact that source backs (invariant 5).

| Level | Name | Examples | Can solely back a fact? |
|-------|------|----------|-------------------------|
| **T0** | Official Primary | Cruise-line official deck plans, shipyard general-arrangement plans, class-society register entry | Yes |
| **T1** | Official Secondary | Cruise-line spec sheets, official brochures, official site copy | Yes |
| **T2** | Regulatory / Registry | IMO number registries, flag-state records | Yes, within scope |
| **T3** | Reputable Third-Party | Established ship-reference databases | No — requires corroboration by ≥ T2 |
| **T4** | Community / Unverified | Forums, passenger-contributed notes | No — may only produce `Unknown(conflicted)` context, never a sealed value |

### 3.1 Corroboration rules

- A fact backed only by **T3** is held at `Unknown(not_sourced)` until a T2+
  source corroborates it; once corroborated, its ceiling is the higher source's
  level.
- A **T4** source may never raise a fact above `Unknown`. It can flag that a
  conflict or claim exists, which is provenance, not a value.
- Where two sources of equal trust conflict, the fact is `conflicted` and cannot
  seal above Structured for that predicate until reconciled with a recorded
  reconciliation rule.

## 4. Coverage and authority scope

`coverage` is what the source *talks about*; `authority_scope` is what it is
*allowed to back*. They differ because a source can mention something it is not
authoritative for (a brochure may show a deck plan sketch but is not authoritative
for exact coordinates).

Coverage and scope are expressed in the **canonical predicate vocabulary** shared
with the pack schema and the Validation Framework — e.g. `deck`, `cabin.category`,
`cabin.coordinates`, `venue.location`, `dimensions.length`, `capacity`. Using one
shared vocabulary is what lets validation check, per predicate, that at least one
in-scope source of sufficient trust backs it.

## 5. Languages

Every source records its `language`. Normalisation (SPEC-005) may translate
*labels* into a canonical language for the pack, but the source language and the
original label are retained in provenance so a translation can never silently
become the evidence. Values that are language-independent (numbers, coordinates,
identifiers) are unaffected.

## 6. Versioning

- Sources are immutable once registered. A new edition is a new `source_id` with
  `supersedes` set.
- Re-deriving a ship against a newer source edition produces a **new pack**
  (SPEC-002 §2.4); it never edits the pack that used the old edition.
- The registry therefore also serves as an audit trail: given any historical
  pack, its exact source editions are recoverable by hash.

## 7. Registry invariants

1. Append-only; entries are never mutated, only superseded.
2. Every registered source has a retained, hash-verified raw artifact.
3. `trust_level` is from the closed T0–T4 set; no ad-hoc levels.
4. A source may back only predicates in its `authority_scope`.
5. Nothing in a pack references a source that is not in the registry.
