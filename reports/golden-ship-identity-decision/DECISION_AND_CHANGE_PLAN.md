# Bellissima IMO: prepared owner decision and canonical correction plan

**DECISION PREPARED — AWAITING CANONICAL CHANGE AUTHORIZATION.**

Baseline: `649f47ba94359f19b90835546afa2478e338f90f`. Prepared in the existing isolated `feat/golden-ship-bellissima-phase1` worktree. This document records the scope of an explicit owner instruction; it is not a canonical review transition, evidence-condition change or publication authorization. No existing report is superseded or rewritten.

## 1. Decision record

| Field | Recorded scope |
| --- | --- |
| Local reference | BELLISSIMA-IMO-OWNER-2026-11-01 (report label only; not an issued ART/EVT/STM/CFL identifier) |
| Decision maker | Product Owner, as explicitly attributed in the current owner instruction |
| Decision date supplied by owner | 2026-11-01 |
| Instruction provenance | Current chat instruction titled “TIMONELO — Record Human Identity Decision”; no external signature or independent identity authentication is asserted |
| Exact confirmed proposition | “MSC Bellissima's correct IMO is 9760524.” |
| Exact rejected attribution | “The previously conflicting IMO 9766205 must not be treated as Bellissima's verified identity.” |
| Recorded by | Codex AI, documenting the owner's instruction; not claiming to have performed the human review |
| Status | Owner's **IMO-only** decision documented in preparation; canonical application not authorized or executed |
| Explicitly excluded | MMSI, call sign, specifications, ART source applicability approval, restaurant/venue approvals, evidence support upgrades, publication, deployment |

This decision does not imply that the owner inspected every linked source, accepted its edition/currentness, approved any of the 20 observations, or authorized correction of every dependent file. Those facts are not supplied by the instruction and are not manufactured here. The original eight blocked claims and the eight prioritized Phase 2 readings remain untouched.

## 2. Existing approved decision mechanisms inspected

The implemented governance path for **statement** human review is:

`Workspace.transition(statement_id, to_state, actor, occurred_on, note)` in `src/timonelo/evidence/workspace.py` → `StatementEditor.transition(...)` in `src/timonelo/evidence/editor.py` → `ReviewLog.transition(...)` in `src/timonelo/evidence/review.py`, persisted to `evidence/reviews/log.json`.

It records statement ID, actual from/to review state, actor, date and note. State transitions follow the existing allowed graph; a DRAFT cannot jump straight to APPROVED. Evidence condition is recorded separately by `record_condition_transition`. Publication is a separate `publish_statement` / PublicationAuthority operation, including independent-publisher and evidence checks.

`ConflictLog.resolve(...)` in `src/timonelo/evidence/conflicts.py` records a resolution revision in `evidence/reviews/conflicts.json` for a real existing conflict between statement IDs. It does not itself change evidence/review/publication state. The spatial review/adjudication APIs apply to spatial proof objects, not this ship-identifier metadata decision.

**No suitable generic identity-metadata decision writer or public artifact-attribution update API was found in these mechanisms.** The two conflicting JSON pack values are not, merely by existing, registered parties to a `ConflictLog` statement conflict. No eligible identity statement/conflict ID has been identified for this decision. Consequently, no fake statement, fabricated conflict, spatial adjudication or `APPROVED` transition was created to force this owner decision into an unrelated log.

This report is the prepared decision record; `evidence/reviews/log.json` and `conflicts.json` remain unchanged. The eventual canonical execution must use an expressly authorized metadata change with this decision as audit provenance, or an already valid identity statement workflow if one is concretely established. No new governance mechanism is implemented or implicitly approved here.

## 3. Evidence referenced, not newly admitted

The existing [Phase 2 review](../golden-ship-bellissima-phase2/REVIEW.md) contains source dates, access date 2026-11-01, limitations and the twenty-observation matrix. Its S1–S4 references are reused without another research pass:

| Source | Exact scope of supporting evidence | Limitation |
| --- | --- | --- |
| [ISPRA 2024 report, physical PDF p45 / printed p43, Annex II](https://www.isprambiente.gov.it/files2024/pubblicazioni/documenti-tecnici/relazione-tenore-di-zolfo.pdf#page=45) | MSC BELLISSIMA paired with IMO **9760524**; June 2024 report covering 2023 | Government primary operational name/IMO evidence, not a current flag certificate or proof of MMSI/call sign. Two adjacent rows are not two independent sources. |
| [Steamship Mutual vessel entry](https://www.steamshipmutual.com/msc-bellissima) | MSC BELLISSIMA, IMO **9760524**; visible cover period 20-Feb-2026 to 20-Feb-2027 | Independent first-party insurer corroboration. No explicit publication date; insurance period is not a publication date. |
| [MCA SAR index, Bellissima row](https://www.gov.uk/csv-preview/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | MMSI **248992000**, call sign **9HA4902**; row last amended 12-Jun-2024, page updated 10-Sep-2026 | Separately sourced radio identifiers; **not included in this owner authorization** and not evidence for IMO in that table. |
| [IMO MSC.4/Circ.265, physical PDF p10 / Annex 1 p6](https://wwwcdn.imo.org/localresources/en/OurWork/Security/Documents/MSC.4_Circ.265%20Annual%20Report%202020.pdf#page=10) | **BW TAGUS / 9766205**, incident row dated 14-Jun-2020; circular 29-Apr-2021 | Official historical counterevidence to the Bellissima attribution, not a current name/flag certificate. |

External sources remain research references rather than held, registered identity artifacts. This task records no ART/EVT intake or source classification approval. In particular, `src:imo-gisis` in the existing knowledge field is not supported by an actually inspected GISIS record in this packet; do not claim that source was verified.

## 4. Exact minimal proposed correction, not applied

### A. Canonical knowledge value

File: `knowledge/ships/msc-bellissima/identity.json`.

```json
[
  {"op":"test","path":"/imo_number/value","value":"9766205"},
  {"op":"replace","path":"/imo_number/value","value":"9760524"}
]
```

This is an illustrative guarded JSON Patch, not an execution script. Preserve the value's **string type**. `knowledge/ships/msc-bellissima/technical.json` already has integer `technical_specifications.imo_number = 9760524`; **no change is proposed to that file**.

No changes to `/mmsi`, `/call_sign`, review/publication axes, confidence, other specifications or passenger claims. Existing `OFFICIAL` labels are not upgraded, newly validated or treated as publication approval by this report.

**Provenance prerequisite:** the currently attached `/imo_number/source_id = "src:imo-gisis"` must not be represented as the evidence for this correction. Owner authorization must specify how the prepared decision and actual accepted source records will be linked. Do not invent a GISIS retrieval, new ART ID, source ID or approval status. A value-only patch can be described exactly now, but is not certified as a provenance-complete production operation until that link is approved. The same applies to any proposed explanatory metadata note: none is silently added to the canonical schema.

### B. Dependent artifact attribution, separately authorized

File: `evidence/artifacts/index.json`.

```json
[
  {"op":"test","path":"/ART-0001/subject_vessels","value":["IMO9766205"]},
  {"op":"replace","path":"/ART-0001/subject_vessels","value":["IMO9760524"]},
  {"op":"test","path":"/ART-0002/subject_vessels","value":["IMO9766205"]},
  {"op":"replace","path":"/ART-0002/subject_vessels","value":["IMO9760524"]}
]
```

These two replacements change an authority-bearing curated subject relationship. They **are not implicitly authorized by the IMO decision**. They require a separate human acceptance that these specific held documents concern Bellissima, and explicit permission for the bounded metadata correction.

`ArtifactRegistry` documents immutable registrations, exposes no public attribution-update method, and deduplicates `register()` by SHA: re-registering the same bytes with a new IMO simply returns the old entry. Therefore do not propose re-registration as a working correction, write private `_by_id` state, issue duplicate ART IDs, or disguise a hand edit as an existing approved API operation. An owner-approved, audited exception/migration for these exact metadata paths must be settled before execution. A generic registry redesign is outside this task.

The factual correction plan is **one knowledge value plus two conditional attribution values**. Its provenance recording and execution mechanism remain explicit approval prerequisites. Do not execute a partial update and then claim the whole Bellissima identity chain has been reconciled.

## 5. ART-0001 / ART-0002 provenance implications

| Artifact | Immutable SHA-256 | Existing subject | Proposed subject after separate authorization |
| --- | --- | --- | --- |
| ART-0001 | `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0` | IMO9766205 | IMO9760524 |
| ART-0002 | `4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603` | IMO9766205 | IMO9760524 |

Both PDFs visibly name MSC Bellissima but do not print either disputed IMO. Their original acquisition metadata, ART IDs, raw bytes, hash bindings, editions, page locators and event references must remain unchanged. The external identity records plus genuine document-applicability decision would justify a metadata correction; the PDFs alone do not establish the IMO.

Changing `subject_vessels` can change the result of `Artifact.establishes_vessel()` and current registry-based verification. It is not cosmetic. Existing EvidenceEvents remain bound to the same source SHA, but downstream spatial/admission consumers must be revalidated rather than assumed unchanged. No event is rewritten, no claim is approved and no `PUBLISH_ALLOWED` is granted by an attribution correction.

Preserve the prior wrong attribution in the authorized audit/decision history, not as a second currently valid `subject_vessels` entry. Do not retain both IMOs as a convenience. Neither artifact ID should be deleted, recycled or replaced, and no PDF artwork redistribution permission follows from identity reconciliation.

## 6. Other directly identified dependent references: no changes authorized

These exact-string findings are a bounded dependency inventory, not a new runtime or architecture audit. Reachability and regeneration safety have not been assumed:

- `src/timonelo/ontology/bellissima.py`: module header and `VesselSpatialOntology.imo_number="IMO9766205"` construction (line 322 at this baseline). Needs a separate identity-scoped execution decision and spatial regression validation; do not let a changed registry silently validate an old vessel object.
- `src/timonelo/factory/compiler.py`: Bellissima IMO in diagnostic text (line 286).
- `data/cruise_intelligence_db.json`, `data/cruise_knowledge_graph.json`, `frontend/src/generated/database.json`, `frontend/src/generated/fleet.ts`: stale Bellissima IMO copies. Regenerate only from corrected approved inputs after a separate scoped authorization; no blanket replacement or generator run now.
- `tools/mass_populate_ships.py`, `tools/expand_world_coverage.py`: hardcoded Bellissima seed; `tools/generate_frontend_bridge.py:40`: hardcoded fallback can reintroduce the wrong value. Merely regenerating output does not repair these upstream assumptions. No code changes are included in this plan execution scope.
- `frontend/public/media/manifest.json`: legacy `ship:IMO9766205` key pointing to the old unapproved portrait. Do not re-key/re-enable this media as part of an IMO correction; asset containment/licensed media policy remains intact.
- `data/hypotheses/legacy-runtime/msc-bellissima.json`, `data/hypotheses/legacy-derivatives/msc-bellissima/{manifest,knowledge-pack}.json` and Meraviglia/Grandiosa legacy derivative manifests/deltas contain old IMO or baseline references. Historical/quarantined material must not be globally rewritten or promoted. No sister-ship attribution is authorized.

An initial canonical correction alone will not eliminate all legacy strings. Until explicitly scoped follow-up is complete, do not claim repository-wide identity reconciliation, execute legacy population scripts or publish derived outputs.

## 7. Validation performed without canonical mutation

- Verified HEAD is the expected `649f47ba94359f19b90835546afa2478e338f90f` and reused the dedicated Golden Ship worktree.
- In-memory deep-copy check: the proposed knowledge change affects only `/imo_number/value`; MMSI and call-sign objects remain identical. Existing `normalize_vessel_imo` accepts the proposed value. A passing checksum is a format test, not the human identity decision.
- In-memory `Artifact.from_dict` checks for each proposed attribution: old object establishes only old IMO; proposed object establishes only correct IMO. ART ID and source SHA remain identical. No registry instance or write API was used against canonical data.
- Both held PDF byte hashes rechecked against ART-0001/0002; match.
- Existing `tests/test_ground_truth_pipeline.py::TestReviewWorkflow`: **6 passed in 0.32 s** (`py -3.14 -B -m pytest ... -q -p no:cacheprovider`). No synthetic owner approval was written by this test to canonical storage.
- No application code changed; no build or full-suite rerun is presented as necessary for this prepared document. The three-path proposal has **not** been executed or certified as a complete migration. Future execution must revalidate current publication/admission output, statement review and event integrity, artifact attribution and spatial refusal behavior after any approved metadata change.

## 8. Remaining authorization requirements

1. **No repeat confirmation of the IMO fact is needed:** the owner's explicit 2026-11-01 IMO decision is already documented above. Its scope stops at that proposition and rejection of the legacy attribution.
2. Explicit authorization for the exact canonical knowledge edit, plus the approved evidence/decision linkage replacing or qualifying the unsupported GISIS attribution.
3. Separate authorization and document-applicability decision for ART-0001/ART-0002 subject correction, including an accepted audited correction mechanism given the immutable registry contract.
4. Separate scope for stale code/generated derivatives if a coherent runtime identity correction is required. No bulk rewriting of historical/quarantined material and no reactivation of legacy media.
5. MMSI/call-sign decisions and every passenger-claim human review remain outstanding. No authority/publication approval follows from the IMO decision. The original eight claims remain blocked; no source, review, support or publication axis was changed.

No commit, push, merge, release or deployment was performed.

**DECISION PREPARED — AWAITING CANONICAL CHANGE AUTHORIZATION.**

Final preservation check: **PASS** — all 26 worktree HEADs/branches and pre-existing uncommitted bytes/statuses preserved, except this single added report; all 1095 tracked files in the isolated worktree byte-identical; original eight-claim packet SHA and blocked states unchanged; `git diff --check` and report whitespace check passed.
