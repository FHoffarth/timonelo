# Timonelo

> **The scientific foundation of a Ground Truth Digital Twin.**
> A cruise ship model that can always say *why* it knows something — and shows,
> just as visibly, what it does not know.

---

## What this is

Timonelo is not a cruise viewer, not a travel app, and not a knowledge
platform. It is a digital twin of a ship in which **every visible statement is
traceable to a document we physically hold**, and everything else is explicitly
UNKNOWN.

The first ship is MSC Bellissima. The first cabin is 14122.

**Today, 0.6% of that ship is curated.** That number is honest, and it will not
be improved by generating data.

---

## The one sentence the system rests on

> **Evidence does not describe a value. It records how that value came into
> existence.**

---

## Scientific principles

| | |
|---|---|
| **Ground Truth always wins** | If the twin contradicts a held artifact, the twin is wrong. Generated content is never defended against evidence. |
| **UNKNOWN is a first-class result** | Computed by comparing the question registry against the statement graph. Never authored, never silently interpolated, always rendered as an explicit gap. |
| **Deterministic derivation is not direct evidence** | Reproducible is not certain. The distinction stays visible in every API and every render. |
| **Geometry requires geometric evidence** | No coordinate, distance, route or walking time without a dimensioned artifact. |
| **Render the semantic model, not publisher artwork** | The artifact is evidence, not a runtime dependency. |
| **The renderer must never silently invent facts** | A renderer cannot abstain, so every visual variable carries a claim. Each must be declared or nullified. |
| **Every visible statement must be traceable** | Artifact, page, locator, reader, date, review history. |

---

## Architecture

```
Artifacts                held documents, content-addressed by SHA-256
    ↓
Truth Engine             statements, provenance, review, conflicts
    ↓
Topology Engine          adjacency, containment, deck hierarchy
    ↓
Geometry Engine          INTENTIONALLY EMPTY — no dimensioned artifact held
    ↓
Semantic Deck Model      our own representation; ordinal, never metric
    ↓
API
    ↓
Frontend                 UI, rendering, interaction
```

Knowledge flows downward only.

---

## Current state

| | |
|---|---|
| Artifacts held | 1 — MSC Bellissima Deckpläne, 11.2025 DEU |
| Statements published | 112 |
| Cabins curated | 14 of 2,217 (0.6%) |
| Coverage per curated cabin | 53.3% — 8 of 15 questions |
| Topology facts | 153 (24 direct, 31 derived, 98 unknown) |
| Geometry coverage | 0% |

Per-cabin coverage is identical across all curated cabins because it is set by
the Statement Authority Matrix, not by effort. **It will not exceed 53.3% for
any cabin until a second artifact class is acquired.**

---

## Read this before writing code

| Document | Answers |
|---|---|
| [`docs/SESSION_2026-08-17_ARCHITECTURAL_BREAKTHROUGH.md`](docs/SESSION_2026-08-17_ARCHITECTURAL_BREAKTHROUGH.md) | What was discovered and decided, and why |
| [`docs/adr/ADR-0002.md`](docs/adr/) | The truth model |
| [`docs/adr/ADR-0003.md`](docs/adr/) | Runtime and determinism |

### Two contradictions are live today

1. `src/timonelo/ontology/bellissima.py` generates 2,508 cabins and answers
   cabin 14122 as *BA, 19.0 m², not accessible*. The evidence says *IR2, area
   UNKNOWN, accessible*. Until quarantined, the system can answer the same
   question two ways.
2. The evidence store lives in this repository, but per the agreed boundary
   truth belongs in `timonelo-knowledge-factory`. Migration pending.

---

## Curating evidence

```bash
python -m timonelo.evidence.cli artifact-create path/to/deckplan.pdf \
  --document-class cruise_line_deck_plan --acquired-on 2026-08-17 \
  --acquisition-method "download from msccruises.com" \
  --publisher "MSC Cruises" --published-on 2025-11 --version "Rev 4" --language de

python -m timonelo.evidence.cli statement-create \
  --entity cabin:MSC-BELLISSIMA:14122 --question Q-0001 \
  --statement-type cabin.deck --value 14 --artifact ART-0001 --page 5 \
  --locator "Deck 14 plan, cabin table" --read-by your.name --read-on 2026-08-17

python -m timonelo.evidence.cli submit  STM-0001 --actor your.name    --on 2026-08-17
python -m timonelo.evidence.cli approve STM-0001 --actor second.person --on 2026-08-18
python -m timonelo.evidence.cli publish STM-0001 --actor second.person --on 2026-08-18

python -m timonelo.evidence.cli trace --entity cabin:MSC-BELLISSIMA:14122 --question Q-0001
```

The reader of a document cannot publish their own statement. The Statement
Authority Matrix rejects a document class that cannot support the statement
type. Nothing bypasses the chain.

See [`evidence/CURATOR.md`](evidence/CURATOR.md).

---

## Current phase

**The bottleneck is no longer architecture. It is evidence.**

1. Acquire and curate evidence.
2. Expand the Truth Engine.
3. Expand the Topology Engine.
4. Extend the architecture only when evidence reveals a real deficiency.
