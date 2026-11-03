# Consolidated validation — 2026-11-03

Base: `de8c8d12a6da49cd6bc42f3c489bf130a3b3c613`. Isolated branch: `feat/evidence-factory-automation-mvp`.

| Gate | Actual result |
|---|---|
| Full backend, `py -3.14 -B -m pytest -q -p no:cacheprovider` | 1180 passed, 1 skipped, 2 subtests passed; 388.34 s |
| New batch regression coverage included above | 21 tests: real eight-claim pilot, exact-binding replay refusal, pending/rejected decisions, source mismatch, duplicate IDs, conflicts, missing metadata, output isolation, read-only inspection, approval audit despite publication refusal |
| Full frontend, `npm test` | 207 passed, 18 files |
| Public asset tests | 10 passed |
| Production build | PASS; existing large-chunk advisory remains |
| Public asset guard | PASS |
| Typecheck | 282 existing diagnoses before and after, zero new; sorted file/code/message comparison ignores line/column shifts. Absolute typecheck remains nonzero technical debt. Compiler settings unchanged. |
| Python import/AST checks | PASS |
| `git diff --check` | PASS |
| Narrow final read-only Codex review | No blocking findings; existing authority rules unchanged |

The publication-refusal negative control first failed because the export counted only admitted records as human approvals; it now preserves all eight actual approval histories while reporting zero admitted records. The read-only-constructor regression first detected Registry's directory-creation behavior on the source checkout; inspection now constructs Registry only on its temporary copy. Positive pilot, projection edition transport and visible edition wording were also tested RED then GREEN.

## Real private pilot

Eight APPROVED owner decisions dated 2026-11-03, eight API-created statements STM-0411…STM-0418, eight admitted TruthEngine answers, eight Bellissima snapshot facts. Zero blocked/pending/rejected selected claims. All 410 original statement records and authority results unchanged, including 303 ART-0001-dependent records. No ART-0002 reassignment or modification. Original blocked claim packages remain untouched. Source evidence/knowledge bytes remain unchanged.

Local output (outside all Git checkouts): `C:/Users/Flo/Documents/Codex/2026-08-30/files-pasted-by-the-user-you/reports/evidence-factory-automation-private-2026-11-03/pilot/`. Contains full new event, statement, review/history and answer traces plus original decision input and private snapshot. No PDF/artwork export; these outputs are not committed or uploaded.

## Browser / local production preview

Built application on loopback `127.0.0.1:5201`, with the private snapshot copied only into this worktree's ignored `frontend/dist`. No deployment. Desktop 1440 px and mobile 390/375/320 px: all eight deck facts present, edition limitation visible, source trace opens, no horizontal page overflow and no console errors/warnings. Licensed photograph and attribution retained. Source trace shows canonical new ID, Q-0016, ART-0001, physical page and exact locator. Screenshots saved outside Git alongside the private pilot.

Explicitly revoked the local ignored preview snapshot with the existing `make_snapshot(..., blocked=True)`. After reloading and reopening Bellissima: zero fact/trace cards, no “8 published answers”, visible “Publication data unavailable”; ship navigation remains. Preview is left revoked, not restored from an archived active snapshot. Existing snapshot expiry/corruption/replacement tests also pass in the full suites.

Direct local requests: protected deck PNG 404, source-page PNG 404, held raw PDF path 404. `/evidence/artifacts/index.json` returns the SPA's `text/html` fallback, not Registry JSON; no evidence data is exported. Asset containment guard passes. Only loopback application content was served; source-review documents were not served.

## Repository integrity / release boundary

33 worktrees inventoried. Thirty prior recorded worktrees checked against saved HEADs/statuses/dirty-file hashes (using the explicitly completed ART-0001 correction commit as that worktree's expected HEAD): no unexpected differences. The two later Golden Ship worktrees retain their own HEADs and existing reports; no writes were made there. Current automation worktree is the only edited checkout. Registry SHA-256 remains `a15e9facd27cc00285c99ed2e8583afadd530cfbfee70b557521c0ec24df1546`.

No Evidence/Knowledge, publication-policy, Passenger Admission, Geometry, dependency or CI workflow changes. No external ingestion, source registration, artwork redistribution, canonical apply, public snapshot upload, deployment, Railway change, main/develop merge or history rewrite. Feature push/PR are authorized; integration and public release remain separate gates. Remote CI results must be read from the exact final PR commit, not inferred from these local results.
