# Evidence Factory Automation MVP

This is a **private-copy pilot**, not a canonical migration or public publication. It consumes the existing eight Bellissima observations and actual Product Owner APPROVE decisions of 2026-11-03. The canonical evidence/knowledge files and all 410 original statement records remain unchanged. The original blocked packages and earlier DEFER records are preserved.

## Repeatable workflow

From the repository root, with the existing Python development dependencies installed, set `PYTHONPATH` to this checkout's `src` and run:

```powershell
$env:PYTHONPATH=(Resolve-Path src).Path
python -B -m timonelo.factory.evidence_batch `
  --root . `
  --batch reports/evidence-factory-automation/pilot-batch.json `
  --decisions reports/evidence-factory-automation/pilot-approvals.json `
  --output C:/path/outside/all/git-checkouts/new-private-batch
```

Use a new, private output directory. Existing destinations and any destination inside a Git checkout are refused. Only the configured registered-local-artifact route is implemented. No network or Drive retrieval is performed; no route can infer admissibility from a Drive location.

1. Resolve canonical ship identity and registered artifacts; verify held SHA-256, version, vessel attribution, question/source class and exact PDF region text.
2. Detect duplicate selected claims, contradictory existing values, existing same-source claims and ambiguous duplicate artifact registrations.
3. Require exact structured binding of claim, source digest/revision, vessel, locator, value, entity, question, type, source boxes and scope to a real operator-supplied decision. Missing/DEFER remains pending; REJECT stays rejected; mismatch refuses reuse.
4. Copy evidence into an automatically created temporary workspace. Use existing EvidenceEventLog, StatementEditor, ReviewLog, PublicationAuthority and TruthEngine. The source-reading instrument and genuine human reviewer remain distinct. Record the actual review date, not a fabricated timestamp/signature. Human approval does not skip publication validation; a later refusal retains the approval audit history.
5. Verify all original statement records and authority outcomes, ART-0002 and source files remain unchanged. Generate the snapshot using the existing Python projector/envelope. Delete the temporary workspace.
6. Export `result.json` (new statement/event/history/trace records), unchanged `decision-records.json`, `private.snapshot.json` and one compact `review-package.md` containing the selected claims and unresolved exceptions. No PDF or source artwork is exported.

`inspect_batch()` performs the same source/decision preflight without lifecycle transitions. Registry construction itself creates directories, so even inspection constructs Registry only on a private copy. There is no canonical-apply mode.

## Existing functions reused

Registered source resolution: ArtifactRegistry/ArtifactStore. Source admissibility: existing Source Authority/question model and vessel attribution. Claim conflicts: `values_disagree`. Evidence and lifecycle: Workspace's existing event/editor/review APIs. Authority and answer selection: PublicationAuthority and TruthEngine. Passenger output: `project_fleet` and `make_snapshot`; existing `usePublicationSnapshot()` retains expiry/revocation handling. The only new projection metadata is registered source edition; the existing profile labels these deck locations as edition-specific, not current operations.

No new engine, source class, dependency, external ingestion route or approval rule is introduced. Automated text-region equality verifies the documented reading; it is not a semantic proof or substitute for human source inspection. Unsupported claim types remain outside this bounded MVP.

## Pilot outcome

| Observation | Private new statement | Reference-only old statement | Decks |
|---|---|---|---|
| GSB-P1-017 Guest Service | STM-0411 | none | 5 |
| GSB-P1-007 Le Cerisier | STM-0412 | STM-0157 | 6 |
| GSB-P1-008 Lighthouse Restaurant | STM-0413 | STM-0158 | 6 |
| GSB-P1-009 Posidonia Restaurant | STM-0414 | STM-0182 | 5 |
| GSB-P1-010 Marketplace Buffet | STM-0415 | STM-0163 | 15 |
| GSB-P1-011 London Theatre | STM-0416 | STM-0159 | 5, 6 |
| GSB-P1-012 Carousel Lounge | STM-0417 | STM-0128 | 7 |
| GSB-P1-018 MSC Excursions | STM-0418 | STM-0170 | 5, 6 |

Eight distinct actual human decisions were recorded through existing APIs on the private copy; all eight new records passed PublicationAuthority and TruthEngine and appeared in the private Bellissima snapshot. The old ART-0002-bound records were not rebound, overwritten or promoted. No other ship gained facts. New IDs are allocated by the existing editor and may differ when a later input dataset changes.

Canonical Registry SHA-256 remains `a15e9facd27cc00285c99ed2e8583afadd530cfbfee70b557521c0ec24df1546`. ART-0001 remains `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0`, IMO9760524; ART-0002 remains unchanged, including IMO9766205. All 303 existing ART-0001-dependent statements retain their prior authority outcomes.

## Trust and release boundaries

The decision JSON is a trusted operator's transcription of the actual owner instruction, linked in [OWNER_AUTHORIZATION.md](OWNER_AUTHORIZATION.md). Exact equality/digests prevent accidental drift and stale approval reuse; they are **not signatures, authentication, or independent proof of reviewer identity**. Human approval remains a manual prerequisite. Do not feed arbitrary untrusted decision files to this operator tool.

Document authenticity is reported separately from vessel attribution and redistribution permission. Owner attestation of the MSC download and Drive byte identity is preserved; historical acquisition is not independently verified. No external source was registered or reassigned. No artwork rights are inferred from factual approval. Source review excerpts remain available in the owner's existing visual-review PDF; they are not redistributed by this tool.

Private snapshots are local test artifacts. Their existing expiry/revocation rules apply. No public upload, hosting refresh, automatic merge or deployment is performed. A later canonical application requires a separate, exact audited change and integration authorization; this MVP deliberately does not write canonical data.

Manual work reduced: repeated digest/identity/locator checks, binding comparison, conflict/duplicate screening, lifecycle API sequencing, original-authority comparison, trace export and snapshot assembly. Manual work preserved: source authenticity/rights assessment, semantic source reading, genuine adjudication, independent integration/release decisions. Next increment: a separately reviewed canonical-application manifest with exact before-state checks, reusing this preflight and existing governance APIs.
