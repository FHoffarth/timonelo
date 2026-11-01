# MSC fleet launch: first implementation boundary

Base: `3492c5684982ae6f147189acffdac6b2621351e0`. No changes to canonical records or approval policy.

## Reused architecture

Statement entity IDs, question IDs, EvidenceEvents, ArtifactRegistry, PublicationAuthority and TruthEngine already operate independently of cruise line and vessel class. The legacy frontend repository, however, imports Bellissima material directly and its OFFICIAL labels are not publication decisions. It is retained for explicitly labelled reference tools only.

`fleetCatalog.json` is a product discovery list supplied by the launch scope. Its names and operator IDs are navigation metadata, not governed identity facts. Class, IMO, capacity and other legacy identity fields are not copied into the published profile.

`FleetProfileData` is one transport view for identity, decks, venues, cabins, sources and publication coverage. The Python projector calls current PublicationAuthority and dated TruthEngine answers. Only the selected, uncontested answer with held, matching, non-private event provenance is exported. The first projection deliberately omits inference-only and mixed-artifact provenance until the transport can represent them correctly. No publication policy is reimplemented in TypeScript.

The existing nav and page switcher are extended. Search carries vessel context for cabin requests; returning through browser history restores it. Bellissima reference tools never render inside another ship profile. Geometry admission remains a separate existing boundary.

## Coverage contract

- Level 0: no admitted identity answer; a catalog entry alone does not achieve Level 1.
- Level 1: one or more published identity answers.
- Level 2: Level 1 plus published deck and venue answers.
- Level 3: Level 2 plus published cabin answers.

These are category-presence levels, not percentages, full-ship completeness, navigability or accessibility. A venue-to-deck observation alone does not establish geometry or a whole profile.

The current canonical store produces Bellissima **398 candidates / 0 exported answers / Level 0**. Meraviglia, Grandiosa, Euribia, Virtuosa, World Europa, World America, Seascape and Seashore each produce **0 matching canonical candidates / 0 exported answers / Level 0**. Legacy knowledge packs may exist, but do not qualify by their own trust labels.

## Build and fail-closed behavior

`npm run build` and `npm run dev` first invoke `scripts/export_passenger_fleet.py` using Python. The script reads the evidence store without flushing it. Generated `frontend/public/data/fleet.publication.json` is ignored by Git and contains no source artwork or source byte paths. Missing store or evaluation failure blocks generation/build; missing or malformed transport keeps frontend facts unavailable. Profile display never falls back to a sister ship.

This is a build snapshot, **not live authority**. It has an explicit as-of date. Changes, withdrawals or review decisions after the build require a fresh build and deployment. Launch operations must define this rebuild/revocation process; this implementation does not pretend to solve instant revocation on a static host.

## First controlled factory slice and release blockers

The ART-0002 restaurant pilot remains preparation only: Le Cerisier (6), Lighthouse Restaurant (6), Posidonia Restaurant (5), page 4. The dry run uses actual AI observation labels and current dates on a temporary three-claim store. Human approval is not automated. Published product facts remain zero until the normal review and independent publication steps occur.

Next stage: complete those three genuine human reviews, capture their evidence through existing APIs with real identities/dates, publish through the existing gate, and rebuild the projection. Then repeat a bounded source-to-claim slice per vessel, with that vessel's own held artifact and explicit source/validity scope. Reuse extraction/workflow code; do not inherit facts, coordinates or source claims from sister ships. Identity/class facts need their own admissible evidence before coverage can progress.

Discovery is usable now, but an information-rich public fleet launch remains blocked by the lack of published knowledge, human approvals, source-specific usage decisions and a defined static publication refresh process. Existing TypeScript debt and the bundle-size warning are separate existing limitations, not green gates.

The baseline `frontend/public/decks/*.png` assets are still copied by Vite into `dist/decks/`. This sprint adds no artwork and does not display them in fleet discovery, but their public distribution rights were not established here. Resolve their rights or quarantine their build output before a public deployment; UI admission alone does not remove publicly addressable files.
