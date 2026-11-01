# Passenger Beta integration candidate

Prepared 2026-11-01 in `integration/passenger-beta-candidate`, isolated managed
worktree `passenger-beta-integration/passenger-beta-phase1`.

## Exact history and integration scope

The original validated commits are retained without recreation or rewrite:

`f776d39cd6d83006cf6fcc242ee364421525d7de`
→ `9d639e67c0eb442d4c7aa7523da40455093307ae`
→ `fa596945ff60770edeb658550e20d47bba992a91`
→ this licensed-portrait integration commit.

The dedicated integration branch was created only in the new clean worktree.
Safety commits were applied as two fast-forwards, in order. No existing worktree
was switched, reset or cleaned. No merge to develop/main, push, visibility change
or deployment was performed. All 24 pre-existing worktrees were protected by a
before/after HEAD, branch, porcelain-status and changed/untracked-file hash check.

## Deliberate conflict resolution

The existing portrait implementation was compared to the shared f776d39 base
using a three-way text merge. Only the two known FleetDiscovery conflicts arose:

1. Imports: retain the safety types and `usePublicationSnapshot`, add `ShipPhoto`.
2. Discovery cards: retain portraits and their visible credit links; use snapshot
   data or explicit unavailable state. Do not restore the old loading branch.

The safety hook, snapshot implementation, Python exporter and strong public-asset
plugin remain byte-for-byte unchanged from fa596945. The older portrait/safety
worktree copies of package/Vite/containment scripts were not overlaid.

The existing portrait UI, 27 WebP variants and manifest were copied; original
worktrees were not modified. The attribution test was preserved and strengthened
with exact nine-ship coverage, rendition byte-count/SHA-256 checks, WebP format,
rendered author/change/license text and source-revision links. No new dependency,
router migration, data engine or governance rule was introduced.

## Content, identity and rights

All nine catalog entries retain their own image assignment. The nine stored
Commons file-page records match manifest author, license, source revision and
original file SHA-1; all 27 variants are byte-identical to the prepared portraits.
Integrated output images were visually inspected as a nine-photo contact sheet;
actual Bellissima/Euribia desktop/mobile renders were also inspected. Identity
assignment follows those individual photo records, not sister-ship inheritance.
Partial images remain labelled as photographs/details, not governed vessel identity.

Credits include author, source, individual CC0/BY/BY-SA license and changes notice;
BY-SA renditions retain their declared BY-SA license. Euribia uses the documented
superstructure crop excluding its separately authored hull artwork. There is no
inference of MSC image permission from correspondence or generic source labels.
Old unproven hero/social references were removed from the social metadata, and
no unknown ship receives another vessel's hero fallback. Uncleared source media
and deck artwork remain excluded by the existing build policy.

All nine production profiles still have zero admitted answers. Bellissima's 398
candidate records are not published answers. The eight human-review observations
remain withheld; the review package and canonical Evidence/Knowledge were not
changed. Review-pending panels do not disclose or approve their claim values.

## Combined validation

- Focused snapshot/fleet/portrait tests: 19 passed.
- Public asset containment regressions: 10 passed.
- Full frontend suite: 205 passed across 18 files, using one worker (no timeout,
  compiler or test-rule weakening).
- Full backend suite: 1136 passed, 1 skipped, 2 subtests passed.
- Production build and standalone containment guard: PASS.
- TypeScript: 282 existing baseline diagnostics, 282 candidate diagnostics,
  zero new diagnostics after line/column normalization. Existing technical debt
  remains; this is not an absolute green typecheck.
- HTTP: all 27 licensed renditions returned 200, image/webp and exact hashes;
  all 37 protected legacy/raw URLs returned 404.
- Browser discovery: nine images/credits at 1440/390/375/320 px, no overflow.
  Search filtering and all nine ship/profile/back transitions passed with the
  correct vessel-specific hero and credit.
- Bellissima and Euribia profiles: four widths each, images decoded successfully,
  no horizontal overflow, visible pending state and expandable source/license/
  modification details. My Cruise navigation retained the past unverified
  reference voyage and terminal/berth uncertainty, then returned to Ships.
- Actual corrupted snapshot: publication unavailable while nine photos/credits
  remained. Actual explicit block: unavailable; replaying the earlier active
  snapshot after reload still refused. A newly generated canonical snapshot
  recovered. Synthetic fact/source-trace removal is covered by inherited tests.
- Browser console errors: zero in the functioning test tab, including controlled
  corrupt/block/replay/recovery checks. An initial tab opened before preview
  startup was ready showed connection refused; a fresh tab after HTTP readiness
  was used for all application checks.
- Independent focused integration review: no P0/P1/P2 defect reported. It confirmed
  all 27 rendition hashes, attribution delivery, unchanged safety implementation
  and withholding of pending claim values.
- `git diff --check`: PASS. Canonical data, authority rules, Passenger Admission
  and existing source worktrees remain unchanged.

Private browser screenshots and logs are under `.local/`; not committed and not
publicly deployed. The snapshot probes modified only ignored generated dist data,
then regenerated the normal canonical projection. No source artifact was served.

## Recommendation and remaining release blockers

CONDITIONAL: ready for review as one coherent integration candidate, not public
release authorization.

P0 release prerequisite: already-public GitHub/source-history artwork and existing
hosting/CDN copies still require a separate owner/rights decision. Build containment
cannot retract public history and no repository visibility was changed.

P1 operations prerequisite: production canonical regeneration, atomic snapshot
replacement and verified CDN no-store behavior still need operator setup. The
600-second lease expires fail-closed without renewal; no instant/global/offline
revocation or signed authenticity is promised.

The ordered candidate is now Containment → Snapshot Safety → Licensed Portraits;
combined regressions and browser smokes passed. A reviewer can inspect this
branch without modifying the original worktrees. Publishing any of the eight
claims still requires Florian's later individual human decisions and the existing
canonical approval/publication path. No automatic approval was performed.

## Exact files in the integration commit (relative to fa596945)

```
docs/PASSENGER_BETA_INTEGRATION.md
frontend/index.html
frontend/public/media/ships/manifest.json
frontend/public/media/ships/msc-bellissima-1280.webp
frontend/public/media/ships/msc-bellissima-320.webp
frontend/public/media/ships/msc-bellissima-640.webp
frontend/public/media/ships/msc-euribia-1280.webp
frontend/public/media/ships/msc-euribia-320.webp
frontend/public/media/ships/msc-euribia-640.webp
frontend/public/media/ships/msc-grandiosa-1280.webp
frontend/public/media/ships/msc-grandiosa-320.webp
frontend/public/media/ships/msc-grandiosa-640.webp
frontend/public/media/ships/msc-meraviglia-1280.webp
frontend/public/media/ships/msc-meraviglia-320.webp
frontend/public/media/ships/msc-meraviglia-640.webp
frontend/public/media/ships/msc-seascape-320.webp
frontend/public/media/ships/msc-seascape-640.webp
frontend/public/media/ships/msc-seascape-980.webp
frontend/public/media/ships/msc-seashore-1280.webp
frontend/public/media/ships/msc-seashore-320.webp
frontend/public/media/ships/msc-seashore-640.webp
frontend/public/media/ships/msc-virtuosa-1280.webp
frontend/public/media/ships/msc-virtuosa-320.webp
frontend/public/media/ships/msc-virtuosa-640.webp
frontend/public/media/ships/msc-world-america-1280.webp
frontend/public/media/ships/msc-world-america-320.webp
frontend/public/media/ships/msc-world-america-640.webp
frontend/public/media/ships/msc-world-europa-1280.webp
frontend/public/media/ships/msc-world-europa-320.webp
frontend/public/media/ships/msc-world-europa-640.webp
frontend/src/media.tsx
frontend/src/passenger/FleetDiscovery.tsx
frontend/src/passenger/ShipPhoto.tsx
frontend/src/passenger/shipPortraits.test.tsx
```

## Exact files in the complete candidate stack (relative to f776d39)

```
.github/workflows/ci.yml
docs/PASSENGER_BETA_INTEGRATION.md
docs/PUBLIC_RELEASE_SAFETY.md
docs/SNAPSHOT_INTEGRATION_GATE.md
frontend/index.html
frontend/package.json
frontend/public/_headers
frontend/public/media/ships/manifest.json
frontend/public/media/ships/msc-bellissima-1280.webp
frontend/public/media/ships/msc-bellissima-320.webp
frontend/public/media/ships/msc-bellissima-640.webp
frontend/public/media/ships/msc-euribia-1280.webp
frontend/public/media/ships/msc-euribia-320.webp
frontend/public/media/ships/msc-euribia-640.webp
frontend/public/media/ships/msc-grandiosa-1280.webp
frontend/public/media/ships/msc-grandiosa-320.webp
frontend/public/media/ships/msc-grandiosa-640.webp
frontend/public/media/ships/msc-meraviglia-1280.webp
frontend/public/media/ships/msc-meraviglia-320.webp
frontend/public/media/ships/msc-meraviglia-640.webp
frontend/public/media/ships/msc-seascape-320.webp
frontend/public/media/ships/msc-seascape-640.webp
frontend/public/media/ships/msc-seascape-980.webp
frontend/public/media/ships/msc-seashore-1280.webp
frontend/public/media/ships/msc-seashore-320.webp
frontend/public/media/ships/msc-seashore-640.webp
frontend/public/media/ships/msc-virtuosa-1280.webp
frontend/public/media/ships/msc-virtuosa-320.webp
frontend/public/media/ships/msc-virtuosa-640.webp
frontend/public/media/ships/msc-world-america-1280.webp
frontend/public/media/ships/msc-world-america-320.webp
frontend/public/media/ships/msc-world-america-640.webp
frontend/public/media/ships/msc-world-europa-1280.webp
frontend/public/media/ships/msc-world-europa-320.webp
frontend/public/media/ships/msc-world-europa-640.webp
frontend/scripts/public-assets.d.mts
frontend/scripts/public-assets.mjs
frontend/scripts/public-assets.test.mjs
frontend/src/media.tsx
frontend/src/passenger/FleetDiscovery.tsx
frontend/src/passenger/ShipPhoto.tsx
frontend/src/passenger/publicationPolicy.json
frontend/src/passenger/publicationSnapshot.test.ts
frontend/src/passenger/publicationSnapshot.ts
frontend/src/passenger/shipPortraits.test.tsx
frontend/src/passenger/usePublicationSnapshot.ts
frontend/vite.config.ts
scripts/export_passenger_fleet.py
src/timonelo/evidence/publication_snapshot.py
tests/test_publication_snapshot.py
```
