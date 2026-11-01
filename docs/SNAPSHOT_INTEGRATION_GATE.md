# Snapshot Safety & Integration Gate

Review candidate prepared 2026-11-01 on base
`f776d39cd6d83006cf6fcc242ee364421525d7de` in the isolated managed
`snapshot-integration-gate/passenger-beta-phase1` worktree. Existing active
worktrees are read-only inputs. No merge, deployment, visibility change or push
is part of this candidate.

## Verified findings and corrections

1. **Containment path-change bypass:** an unapproved image moved outside
   `public/media` / `public/decks` was no longer denied. Reproduced with a failing
   test before correction. Output raster denial now applies independently of
   folder, with only exact licensed variants allowed.
2. **Extension disguise:** JPEG bytes under an unrelated `.bin` filename were
   accepted. Reproduced before correction. Common JPEG/PNG/GIF/WebP/AVIF
   signatures now supplement extensions and known raw-source hashes. The
   independent focused review additionally reproduced disguised BMP/TIFF;
   BMP, little/big-endian TIFF and BigTIFF headers are covered as well.
3. **Forgotten revocation:** a client could observe a block, unmount, then a new
   client could accept the previous active revision. Reproduced before correction.
   The actual browser hook now persists only the highest generation/revision/block
   watermark in sessionStorage. Invalid/unavailable storage refuses facts.

The snapshot transport and UI wiring already prepared in the separate safety
worktree are incorporated here for validation. The eight human-review candidates
are not incorporated or approved. No authority rule or canonical data changed.

An additional independent read-only reviewer checked this scoped diff, found the
BMP/TIFF signature omission, and confirmed its regression-backed correction.
No further concrete snapshot, exporter, UI-wiring or CI defect was reported.

## Validation

- Containment regressions: 10/10 passed, including the reproduced bypasses,
  exact rendition integrity, malformed rights records and preservation of originals.
- Frontend: 202/202 passed with `npm test -- --maxWorkers=1`. The first parallel
  run hit the existing spatial-proof all-cabin rendering test's 10-second timeout
  under concurrent build/backend load. No test timeout or compiler setting changed.
- Backend: 1136 passed, 1 skipped, 2 subtests passed (`pytest tests/ -q`).
- Focused Python envelope/projection tests: 5 passed. The exporter separately
  removed stale output on missing evidence and generated an empty emergency block
  without a readable evidence store. Compile checks passed.
- Build and independent output guard: PASS. 37/37 protected local preview URLs
  returned 404. Snapshot response: `Cache-Control: no-store, max-age=0`.
- Typecheck: 282 pre-existing diagnostics and 282 current, no new diagnostics
  after line/column normalization. This is existing technical debt, not a green
  absolute typecheck.
- Actual nine-ship Commons manifest compatibility: all 27 exact WebP variants
  survived containment in a private test copy. The licensed media source worktree
  and its attribution tests were not changed.
- Browser: nine discovery entries at 1440/390/375/320 px, no horizontal overflow.
  Normal snapshot → explicit block → unavailable; restoring the previous active
  snapshot after reload remained unavailable; a freshly reevaluated newer active
  snapshot recovered. No console errors observed. All real profiles still had
  zero admitted facts. Synthetic fact replacement/removal and source-trace removal
  were checked against the real FleetProfile renderer in regression tests.
- All 23 pre-existing worktrees: unchanged HEAD/branch/status and hashes of
  pre-existing changed/untracked files. Human packet SHA-256 remained
  `fef8e3d65100562d4bcbaca9e723b8a1a5223deb85f03df2f446f17adc7c131f`.
- `git diff --check`: PASS. Canonical Evidence, Knowledge, original media,
  PublicationAuthority and Passenger Admission remain unchanged.

Browser evidence is private under `.local/screenshots/fleet-recovered.jpg`.
Logs, compatibility copies and generated snapshots are private/ignored and must
not be committed. There are no approved ship claims in these tests or outputs.

## Exact scoped files

Containment/CI:

```
.github/workflows/ci.yml
frontend/package.json
frontend/vite.config.ts
frontend/scripts/public-assets.mjs
frontend/scripts/public-assets.d.mts
frontend/scripts/public-assets.test.mjs
```

Snapshot lifecycle:

```
frontend/public/_headers
frontend/src/passenger/FleetDiscovery.tsx
frontend/src/passenger/publicationPolicy.json
frontend/src/passenger/publicationSnapshot.ts
frontend/src/passenger/publicationSnapshot.test.ts
frontend/src/passenger/usePublicationSnapshot.ts
scripts/export_passenger_fleet.py
src/timonelo/evidence/publication_snapshot.py
tests/test_publication_snapshot.py
docs/PUBLIC_RELEASE_SAFETY.md
docs/SNAPSHOT_INTEGRATION_GATE.md
```

## Integration sequence and conflict handling

1. Review the containment commit first: keep the output policy and its CI gates.
2. Review the snapshot commit next: Python envelope + atomic exporter + browser
   lifecycle + session watermark + no-store headers form one compatibility unit.
   Do not ship only one side of the envelope contract.
3. Integrate licensed portraits in a separately authorized isolated integration
   worktree. `FleetDiscovery.tsx` has two actual conflict regions against the old
   portrait patch: imports and discovery cards. Keep `usePublicationSnapshot()`
   and fail-closed data removal from this candidate, then add `ShipPhoto` and
   visible credits from portraits. Do not restore its one-shot raw-projection
   fetch or old loading branch. Retain all attribution tests. Consolidate Vite,
   package and media-script overlaps without reverting to the old limited denylist.
4. Run combined containment, expiry, revocation, transport, attribution and full
   frontend tests; compare the TypeScript baseline and build the final output.
5. Browser-smoke the combined visual result at 1440/390/375/320 px, ship switching,
   valid/unavailable transitions, credit links and direct asset requests.

The currently preserved portrait worktree itself has not been merged or edited.

## Remaining publication blockers and limits

- **P0 release decision:** already-public GitHub files/history and older deployed
  source artwork are not withdrawn by build containment. Asset-specific
  redistribution rights and owner/hosting cleanup decisions remain outstanding.
  No rights are inferred from MSC correspondence or generic source labels.
- **P1 operations:** production snapshot regeneration (at least every five minutes),
  atomic origin replacement and actual CDN no-store behavior are not configured
  or verified here. `_headers` is only effective on hosts that honor it. Expiry
  fails closed if renewal is absent. No immediate/offline/global revocation is
  promised; the revision hash is integrity framing, not a signature.
- **P1 integration:** licensed portraits still require the combined conflict
  resolution and final regression/browser gates above.
- The eight claims remain individually blocked until Florian's later documented
  human decisions and the existing independent publication process. Honest
  zero-fact discovery can remain available without those claims.

Review readiness is not authorization to integrate, publish or deploy.
