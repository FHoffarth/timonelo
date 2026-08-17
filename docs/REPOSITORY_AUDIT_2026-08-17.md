# Repository Audit — 2026-08-17

Deliverable 6. Every file classified. Two repositories, one logical system.

---

## Canonical data — the only sources of truth

| Location | Repo | Contents |
|---|---|---|
| `evidence/artifacts/` | **B** | 1 artifact, content-addressed. Blobs gitignored (CITE_ONLY). |
| `evidence/statements/statements.json` | **B** | 33 statements, 32 published |
| `evidence/reviews/log.json` | **B** | Review history |
| `evidence/reviews/conflicts.json` | **B** | 1 conflict, resolved |
| `evidence/registry/questions.json` | **B** | 15 registered questions |
| `evidence/registry/document_classes.json` | **B** | Workspace-declared classes |
| `ships/msc-bellissima/artifacts.json` | A | Artifact candidates. 1 of 5 held. |

**Finding:** canonical truth sits in Repo B, contrary to the intended boundary.
This is blocker M2.

---

## Derived data — regenerable, must not be edited

| Location | Repo | Derived from |
|---|---|---|
| `ships/msc-bellissima/topology.json` | A | Statement store + deck plan clustering |
| `ships/msc-bellissima/cabins/*.json` | A | Statement store |
| `ships/msc-bellissima/semantic_deck_14.svg` | A | topology.json + cabins |
| `ships/msc-bellissima/render_audit_deck14.json` | A | Declared by the renderer |

**Finding — duplicated truth:** cabin facts exist in both
`evidence/statements/statements.json` (Repo B, canonical) and
`ships/msc-bellissima/cabins/*.json` (Repo A, derived). The cabin files are a
projection and are currently committed as if they were data. They must become
build output (M2).

---

## Contradictory datasets

| File | Repo | Contradiction |
|---|---|---|
| `src/timonelo/ontology/bellissima.py` | **B** | Generates 2,508 cabins. Says 14122 = BA, 19.0 m², not accessible. Evidence says IR2, area UNKNOWN, accessible. **Live and unquarantined.** |
| `src/timonelo/ontology/andorinha.py` | B | Generated river-vessel ontology, no held artifact |
| `data/cruise_knowledge_graph.json` | B | 821 KB generated graph |
| `data/cruise_intelligence_db.json` | B | 460 KB generated database |

**These are the highest-priority cleanup (M1).** They are the only remaining
path by which the system can answer a curated question two different ways.

---

## Generated data — no held artifact

| File | Repo | Status |
|---|---|---|
| `src/timonelo/factory/archetype_generator.py` | B | Synthesizes cabin geometry arithmetically |
| `src/timonelo/factory/patch_engine.py` | B | Derives vessels by patch; no cabin operations |
| `data/knowledge_history.json`, `data/review_queue.json` | B | Generated, canonicalised |

---

## Quarantined — retained, may not seed any engine

`ships/msc-bellissima/hypothesis/_quarantined_2026-08-17/` — 25 entries:

`GEOMETRIC_PROOFS.md` · `distance_matrix.parquet` · `routing.graphml` ·
`navigation.yaml` · `graph.yaml` · `cabins/` · `statements/` ·
`cabin-index.json` · `manifest.json` · `ship.yaml` · `decks.yaml` ·
`cabins.yaml` · `corridors.yaml` · `doors.yaml` · `elevators.yaml` ·
`stairs.yaml` · `venues.yaml` · `restaurants.yaml` · `bars.yaml` · `pools.yaml`
· `shops.yaml` · `toilets.yaml` · `landmarks.yaml` · `zones.yaml` ·
`indexes.yaml`

Reason: none traceable to a held artifact. `GEOMETRIC_PROOFS.md` derived an
L_OA of 315.83 m and per-deck elevations at `0.99 DIRECT_EVIDENTIARY` citing
`art-bellissima-ga-2019`, which does not exist.

---

## Obsolete — review for removal

| File | Repo | Note |
|---|---|---|
| `ships/msc-bellissima/build_twin.py`, `engine.py`, `query.py`, `api.py` | A | Written against the quarantined dataset; untested against the current model |
| `ships/msc-bellissima/SHIP_STATUS.md` | A | Predates the quarantine; claims not re-verified |
| `ships/msc-bellissima/deckplan_overlay_d14.svg` | A | Internal tooling only (CITE_ONLY) |
| `tests/test_frontend_bridge.py` | B | Fails on missing `frontend/src/generated/fleet.ts`; generated artifacts must be reproducible or untracked |

---

## Summary

| Class | Count |
|---|---|
| Canonical | 7 |
| Derived (regenerable) | 4 |
| Contradictory, live | 4 |
| Generated | 5 |
| Quarantined | 25 |
| Obsolete / needs review | 6 |
