# Roadmap — Next

Executable milestones only. Each has a definition of done.

---

## M1 · Quarantine the legacy ontology (Repo B)
Move `ontology/bellissima.py`, `ontology/andorinha.py`, `factory/`, and the
generated `data/*.json` into a hypothesis namespace. Update or remove the
briefing path that reads them.
**Done when:** no code path can answer a question about cabin 14122 except
through the Truth Engine, and the full test suite passes.

---

## M2 · Execute the repository migration
Move the evidence store (`evidence/`, `src/timonelo/evidence/`) from Repo B to
Repo A. Move `src/renderer/` from Repo A to Repo B. Replace Repo A's
`ships/msc-bellissima/cabins/*.json` with build output regenerated from the
statement store — it is a projection, not a source.
**Done when:** Repo A contains no rendering code, Repo B contains no
statements, and no cabin fact is stored in two places.

---

## M3 · Serve the semantic model over an API
One endpoint: cabin by number, returning fields with epistemic state,
provenance, topology and explicit UNKNOWNs.
**Done when:** the Semantic Deck renderer consumes the API rather than reading
JSON files, and Repo B has no filesystem dependency on Repo A.

---

## M4 · Curate deck 14, block by block
Continue the manual workflow. 239 cabins remain. Extract block membership and
per-cell symbols for every block on deck 14.
**Done when:** every deck-14 cabin has either published statements or an
explicit uncurated marker, and deck coverage is a published number.

---

## M5 · Open the MSC licence conversation
Request permission to display deck plan artwork in a passenger-facing product.
Smaller ask than a general arrangement; unblocks the artifact-overlay surface.
**Done when:** a written answer exists, recorded as a decision.

---

## M6 · Acquire a dimensioned artifact
Pursue a Chantiers de l'Atlantique general arrangement, or plan a first-party
onboard survey for one deck.
**Done when:** an artifact is registered whose document class has authority
over `cabin.area_sqm`.

---

## M7 · Activate the Geometry Engine
Only after M6. Establish a coordinate frame from the dimensioned artifact,
register decks against a common datum, then derive distances.
**Done when:** at least one distance statement is published with provenance,
and the render audit's spacing nullification is replaced by a declared
geometric claim.

---

## Not scheduled

Parser implementation, OCR, computer vision, routing, walking times,
multi-ship scaling. None is blocked by engineering; all are blocked by M4 or M6.
