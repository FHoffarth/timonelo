# MSC fleet launch — limited implementation plan

Base: 3492c5684982ae6f147189acffdac6b2621351e0. No commit, push or deployment.

1. Reuse Statement, EvidenceEvent, PublicationAuthority and TruthEngine. Add only a read projection for the static passenger build; never load legacy trust labels as approval.
2. Share one nine-entry product catalog and profile view. Catalog names are discovery labels, not governed vessel identity. Do not copy IMO, class, dimensions or venues across vessels.
3. Project current canonical answers into identity/decks/venues/cabins sections with statement and source provenance. Empty or failed projection remains unavailable. Registered source candidates are distinct from published answers.
4. Coverage: L1 needs admitted identity; L2 also needs admitted deck and venue facts; L3 also needs admitted cabin facts. Spatial admission is separate and cannot be inferred from a coverage level.
5. Wire Ships, search and history with explicit vessel selection; retain the Bellissima reference guide only for that vessel.
6. Run focused/full frontend tests, backend projection tests, build, normalized TypeScript baseline comparison and browser switching at desktop/mobile widths. Re-run the ART-0002 pilot only on a temporary copy without human approval.

Static publication is a build-time snapshot, not live authority. Revocation requires rebuilding/deploying. Do not claim the launch is ready merely because discovery works. No new runtime server, intelligence engine, artwork or source imports.
