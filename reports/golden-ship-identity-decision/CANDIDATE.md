# Bellissima IMO correction candidate

Candidate branch: `fix/bellissima-imo-identity-candidate`.
Base: `649f47ba94359f19b90835546afa2478e338f90f`.
Prepared 2026-11-01. Integration, artifact reassignment and publication are not authorized.

## Exact scope

- `knowledge/ships/msc-bellissima/identity.json`: only `/imo_number/value` changes from string `9766205` to string `9760524`, and `/imo_number/source_id` changes from `src:imo-gisis` to `src:ispra-marine-fuel-report-2024`. Existing trust labels are unchanged; this does not create a canonical Statement, SUPPORTED condition, human-review transition or publication admission.
- `knowledge/sources/official/src_ispra-marine-fuel-report-2024.json`: one concrete source-catalogue record using the **existing** `KnowledgeDBCompiler._load_sources()` path, which reads individual JSON files under `knowledge/sources/` keyed by `source_id` (or `id`). No new provenance engine/schema/API is added. The record identifies the publisher, exact PDF URL, report date, exact name/IMO row, prior remote access date and decision-record path. It is not an ArtifactRegistry registration or a held-byte assertion.
- `tests/test_cruise_intelligence_db.py`: the existing ship identity integration assertion now expects `9760524` instead of `9766205`. The old assertion was independently reproduced failing on the corrected candidate. No test is removed, weakened or skipped, and no unrelated fixture identity is rewritten.
- `reports/golden-ship-identity-decision/DECISION_AND_CHANGE_PLAN.md`: preserves the earlier preparation record's text. Original and copied working-file SHA-256: `b445052e72e4841dc146face5ea7685e0caa381bfddda44b06ff45a732d8ec17`. Git normalizes CRLF to LF; the staged/committed LF blob SHA-256 is `a1d777566b972e86122630c8016dc2d144efda89614863af7e91a3d5cea58258`. The exact difference was verified to be line endings only; the original worktree file is untouched. Its descriptions of no canonical edits refer to that earlier preparation step; its illustrative ART reassignment remains **unexecuted and outside this candidate**.
- This `CANDIDATE.md`: current scope, evidence linkage, validation and remaining gates. It supplements rather than alters the preserved decision record.

The decision is the Product Owner's explicit 2026-11-01 confirmation of **IMO only**, quoted in the preserved record. Codex records no additional human approval, no individual venue decision and no MMSI/call-sign decision. The source metadata references the record; the identity field resolves to the concrete ISPRA source via the existing source catalogue. The former unsupported GISIS attribution is removed from this field only; the global GISIS catalogue and other consumers are unchanged.

## Independently identifiable source linkage

- **Primary:** [ISPRA government report](https://www.isprambiente.gov.it/files2024/pubblicazioni/documenti-tecnici/relazione-tenore-di-zolfo.pdf#page=45), June 2024, Annex II, physical PDF page 45 / printed page 43: MSC BELLISSIMA paired with IMO9760524. It reports on 2023; it is not a current flag certificate. The recorded 2026-11-01 access refers to the earlier Phase 2 remote inspection, not a fabricated human-review or fresh download date.
- **Corroboration:** [Steamship Mutual Bellissima entry](https://www.steamshipmutual.com/msc-bellissima), name/IMO9760524, visible insurance period 20-Feb-2026 to 20-Feb-2027; period is not publication date.
- **Counterevidence:** [IMO circular MSC.4/Circ.265](https://wwwcdn.imo.org/localresources/en/OurWork/Security/Documents/MSC.4_Circ.265%20Annual%20Report%202020.pdf#page=10), 29-Apr-2021, Annex 1 p6 / physical PDF p10, BW TAGUS / IMO9766205. This is a historical identity pairing, not a current name claim.
- [MCA SAR index](https://www.gov.uk/csv-preview/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) documents separate radio identifiers; it neither supplies the IMO in that table nor authorizes MMSI/call-sign changes. Those fields are preserved exactly.

These links and locators are a traceable **source-catalogue** binding for a proposed Knowledge metadata correction. No new source bytes are imported, no ART/EVT identifier is invented, and no report is classified as eligible evidence for a new authoritative statement. A later governed evidence intake still requires permitted held bytes, hash verification, semantic/source-class checks and any genuine approvals. Neither a source catalogue entry nor this candidate is a substitute for PublicationAuthority.

## Preserved boundaries and deliberate mismatch

`technical.json` already identifies IMO9760524 and remains byte-identical. MMSI and call-sign fields remain byte-identical, including their unresolved disagreement between packs. All fields outside the two IMO leaves remain identical.

ART-0001 and ART-0002 retain their IDs, exact source bytes, SHA-256 values, acquisition metadata and existing `subject_vessels=["IMO9766205"]`. Both held PDF hashes were reverified. The evidence tree and every review/event/statement record remain unchanged. Consequently the corrected proposed Knowledge IMO **does not match the still-uncorrected artifact subject attribution**. Current attribution checks must continue to refuse that match; the candidate does not claim the entire provenance chain has been reconciled.

No generated database, frontend source, ontology constructor, legacy seed, quarantined hypothesis or media manifest is rewritten. Those old references identified in the preserved plan remain a separately authorized follow-up; no global replacement or regeneration was run. No old image is re-enabled. No application code, authority rule or passenger admission rule changes.

The original eight-claim review packet remains unchanged at SHA-256 `fef8e3d65100562d4bcbaca9e723b8a1a5223deb85f03df2f446f17adc7c131f`, with zero human decisions and no publication authorization. No part of the source-catalogue binding approves those claims.

## Data and governance verification

Actual private-copy/read-only validation confirms:

1. JSON structural comparison has exactly two changed leaves in identity; original string type preserved. Existing IMO normalizer accepts the value, which agrees with unchanged `technical.json`.
2. The existing compiler source loader resolves the new `source_id` to the exact ISPRA PDF/locator/decision reference; the global GISIS entry remains unchanged.
3. ART-0001/0002 still establish old IMO9766205 and do not establish IMO9760524. PDF hashes match. No reassignment or duplicated artifact is performed.
4. A private copy of the canonical evidence store still has **398 Bellissima candidates / 0 authoritative facts**. Overlapping refusal counts are unchanged: CONDITION_NOT_SUPPORTED390; ZERO_EVIDENCE_EVENTS390; REVIEW_NOT_APPROVED278; EVENT_PRIVATE_SOURCE_NOT_REVERIFIABLE6; INFERRED_RULE_PROVENANCE_UNRESOLVABLE2; INFERRED_INPUT_NOT_ADMITTED2.
5. Canonical Evidence, `technical.json`, frontend files, implementation and all eight prior claims are preserved. Existing worktrees are checked against a pre-task HEAD/branch/status/dirty-byte snapshot before the final commit.

Final regression results (2026-11-01):

| Gate | Actual result |
| --- | --- |
| `py -3.14 -B -m pytest tests/ -q -p no:cacheprovider` | **1,136 passed, 1 skipped, 2 subtests passed**, 310.53 seconds; final run after updating the obsolete IMO assertion |
| `py -3.14 -B -m pytest spikes/ -q -p no:cacheprovider` | **22 passed**, 2.11 seconds |
| Focused database/source/knowledge/schema/fleet suites | **50 passed**, 44.06 seconds |
| Frontend `npm test` | **205 passed**, 18 test files |
| Frontend `npm run build` | **PASS**, 39.20 seconds; existing large-chunk warning, no new build failure |
| Frontend `npm run check:public-assets` | **PASS** |
| Typecheck comparison | **282 baseline diagnostics = 282 candidate diagnostics**, exact sorted diagnostic lines identical; **0 new**. Both typechecks exit 2: this is existing technical debt, not a zero-error typecheck. |
| Data/source/publication checks | Exact two-leaf identity change; source resolves; technical/MMSI/call sign unchanged; both PDF hashes match; ART subjects unchanged; 398 candidates / 0 authoritative facts and identical refusal counts |
| Worktree preservation | All **26 pre-existing worktrees** retain HEAD, branch, porcelain status and recorded dirty-file hashes |
| Diff / supporting document checks | `git diff --check` PASS; JSON and new-document whitespace checks PASS; copied decision-record SHA verified |

Typecheck baseline was materialized privately from the exact base commit, including `frontend/` and its imported `geometry/`, `evidence/`, `knowledge/` and `data/` inputs, using the same dependency installation. Neither an active worktree nor a compiler rule was altered for the comparison. Logs and temporary validation copies remain ignored under `.local/` and are not committed.

The normal build's generated snapshot still exports **0 facts for Bellissima and 0 for each other launch ship**. Generated preview/build outputs are not canonical review records and are not included in the candidate. No result is inferred from source strength alone.

## Remaining approval gates

1. Owner/reviewer accepts this exact candidate for a future canonical integration. Creating the local candidate/commit does not apply it to develop/main or authorize push/publication.
2. Separate document-applicability approval and a permitted audited correction mechanism for ART-0001/0002 attribution; neither is contained here. Until then, the correct IMO must not obtain evidence authority from the incorrect attribution.
3. Separate scope for dependent runtime/generated identity copies and their safety validation if coherent runtime integration is requested. This is not a fleet-wide identity migration.
4. MMSI/call-sign and individual passenger-claim decisions remain outstanding. Any later publication requires the existing genuine review, evidence and publication gates plus explicit authorization. No automatic release or deployment.
