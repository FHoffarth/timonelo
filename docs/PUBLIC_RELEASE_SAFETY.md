# Public release safety: artwork and publication leases

## Product / operations rule

Public, authority-bearing fleet content is a short-lived build projection. The versioned rule in `frontend/src/passenger/publicationPolicy.json` is: **maximum age 600 seconds, refresh interval 30 seconds, request timeout 5 seconds**. A production operator must refresh/re-evaluate the canonical snapshot at least every five minutes to maintain availability. If no fresh snapshot can be obtained, discovery remains available and published content is withheld. This is an explicit availability trade-off, not new evidence or publication policy.

The browser validates at load, on becoming visible, on online/pageshow events, every 30 seconds and at expiry. Hidden/offline/pagehide clears displayed publication data. Failed refreshes (including timeout), malformed payloads, hash failures, blocks and expiry clear content. An independent expiry timer plus a monotonic deadline prevents repeated delivery of the same revision or a backwards clock change from extending its lifetime. Older revisions cannot supersede a newer revision already observed in the same session. A new active revision after a block must have a strictly later generation timestamp.

The browser session retains only the highest observed generation/revision/block
marker in `sessionStorage` (`timonelo.publication.watermark.v1`), never payloads
or facts. This preserves an observed revocation across navigation and reload.
Corrupt or unavailable storage refuses publication display. This is session-local
anti-rollback metadata, not a global revocation list, a trusted clock or protection
against someone controlling the publishing origin/browser storage. The monotonic
deadline applies within a live client; after reload expiry uses the current wall
clock. New tabs without a prior marker still depend on fresh origin delivery.

## Snapshot contract

`timonelo.fleet.snapshot.v1`: UTC millisecond `generated_at`, `expires_at`, boolean `blocked`, string `payload`, and SHA-256 hex `revision`. The payload string contains the existing Python-generated `timonelo.fleet.v1` projection. Keeping its exact UTF-8 representation avoids JSON number / Unicode reserialization differences between Python and JavaScript.

Revision input is exactly `schema + LF + generated_at + LF + expires_at + LF + (blocked ? "blocked" : "active") + LF + payload`, encoded as UTF-8. All metadata is bound, not only the facts. SHA-256 detects inconsistent/corrupt delivery; it is **not a signature** or protection from a compromised publishing origin. TLS and trusted publication infrastructure remain prerequisites.

The Python projector still owns all publication decisions through PublicationAuthority and TruthEngine. No snapshot field grants evidence, human review, geometry or passenger admission. Blocking always emits an empty payload. The exporter writes a temporary file and replaces the output atomically; generation failure removes the old output and fails the build.

## Local commands and production operations

From the repository root:

1. Normal refresh: `python -B scripts/export_passenger_fleet.py --output <staging>/fleet.publication.json`. Re-evaluates current canonical evidence without modifying it.
2. Emergency revoke: `python -B scripts/export_passenger_fleet.py --block --output <staging>/fleet.publication.json`. Does not require a readable evidence store and grants no publication.
3. Publish the one resulting file atomically at `/data/fleet.publication.json` using the existing hosting control plane. Purge any prior CDN copy; verify the new revision, block flag and `Cache-Control: no-store, max-age=0` through the public URL.
4. Roll back UI code if needed, but **never restore an archived active snapshot**. Re-run normal refresh against current canonical state with a fresh timestamp, validate it, then atomically publish it. If regeneration or delivery fails, retain the block / unavailable state.

The app refetches within 30 seconds; a failed request removes content after at most its five-second timeout while the browser is actively executing. This is not guaranteed instant revocation, particularly for offline, sleeping or suspended browsers. Static snapshots cannot discover a canonical withdrawal until regeneration reaches the origin. Expiry still bounds snapshot validity; no assurance is made about a frozen screen or screenshots.

Vite dev and preview send `no-store` for the snapshot. `frontend/public/_headers` provides the same rule for hosts honoring that format. There is no configured production hosting adapter in this repository; GitHub Pages does not honor `_headers`. Production must explicitly configure or verify equivalent CDN/origin headers and schedule refresh publication before enabling authoritative content. Neither a new hosting provider nor a deployment is created here. CI explicitly provides Python for the projection build.

## Protected artwork

The eleven source files remain byte-for-byte under `frontend/public/decks`: deck 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18. Their generated copies, other uncleared raster images and byte-identical held raw-source copies are removed after Vite writes the build, including direct `vite build` use. CI also runs the standalone output guard. Raster extensions and common image signatures are checked independently of folder/name. The optional Commons manifest allows only fully documented, hash-matching exact renditions. It never deletes source or evidence records.

Vite dev/production-preview returns 404 for the protected URLs before SPA fallback. Existing application image consumers are not changed in this integration candidate, and no substitute image is made to look official. Geometry/admission behavior is untouched. This output containment is not a general scanner for copyrighted material embedded into arbitrary source code, SVG, CSS or re-encoded documents.

Previously deployed `/decks/deck_5.png`, `/decks/deck_8.png`, `/decks/deck_9.png`, `/decks/deck_10.png`, `/decks/deck_11.png`, `/decks/deck_12.png`, `/decks/deck_13.png`, `/decks/deck_14.png`, `/decks/deck_15.png`, `/decks/deck_16.png`, `/decks/deck_18.png` require removal from old deployment artifacts and CDN caches separately. Preview deployments, old-version URLs and copies in an already public Git repository are not made private by this build change. Before release, verify that the hosting layer does not retain/serve old files after replacing the build. Internal originals are preserved.
