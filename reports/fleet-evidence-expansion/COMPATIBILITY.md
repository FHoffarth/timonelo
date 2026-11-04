# Compatibility notes for the Multi-Ship Integrity Hardening track

Read against `src/timonelo/factory/evidence_batch.py` at `6be38ab`. No implementation file was changed, and Codex's work was not read, so the guardrail points below are requirements to check, not findings about that work.

## What was validated

`validate_packages.py` passes 15 of 15 checks. Its probe batches exist only in memory. They show how the current contract treats these ships:

| Probe | Result today |
|---|---|
| Batch with no claims | `INVALID_BOUNDED_BATCH`, so source-blocked ships get no batch file |
| Meraviglia with candidate `IMO9760512` | `CANONICAL_VESSEL_IDENTITY_MISMATCH` |
| Meraviglia with seed `IMO9660463` | Passes the identity gate, stops only because the artifact is unregistered |
| Grandiosa and World Europa | Pass the identity gate, stop at the unregistered artifact |

The third row is the one to act on. The gate compares a batch with `identity.json` and treats that file as truth, so it would accept a correctly registered Meraviglia plan attributed to a wrong seed IMO. It would then build evidence on that number.

## Package formats

The files here use their own `v0` schemas: `timonelo.fleet-source-inventory.v0`, `timonelo.fleet-identity-matrix.v0` and `timonelo.fleet-review-package.v0`. They are research records and are not read by any tool. They are not `timonelo.evidence-batch.v1` batches.

`deck_location_candidates` is empty for every ship. When a plan is registered, each entry should be a v1 claim with the 16 fields the pilot uses. The decision fields in these packages bind to nothing yet, because the factory only accepts decisions shaped as `{claim_id, decision, binding}`.

## Requirements on the guardrails

1. **Identity trust.** Consider an identity state the gate can refuse on, so that seed values marked `OFFICIAL` cannot pass as verified. All eight ships here carry the same generated pattern: MMSI `248` plus six IMO digits, call sign `9HA` plus four.
2. **Corrected IMOs.** A correction must not strand records. Attribution, entity IDs and `subject_vessels` should be checked again after any change to `identity.json`.
3. **Positional entity grammar.** Expected form stays `venue:MSC-<SHIP>:<venue>`. Hyphenated ships need the rule to hold for `MSC-WORLD-EUROPA` and `MSC-WORLD-AMERICA`. The current check compares the whole segment to the slug, so a grammar that splits on hyphens would break those two.
4. **Generated `exact_claim`.** If the field becomes generated, the pilot template is `ART-XXXX (edition) labels <name> on deck(s) <n> of <ship>.` and new candidates should omit it.
5. **Deck-column check.** Column layout is not uniform. Meraviglia page 3 heads are near x 71, 183, 295, 407, 519 and page 5 near 74, 184, 295, 405, 516. Deck 17 does not exist on this plan. Bounds should be read per document, or the check will misplace labels on sister ships.
6. **Vessel-name check against the document.** Name matching needs to cope with spaced cover lettering: Meraviglia page 1 extracts as `M S C  M E R A V I G L I A`. Plans state no IMO, so this check can confirm a name but never an IMO.
7. **Intake route.** Plans in the vault can be unregistered: the Meraviglia file is tracked in `evidence/raw` but absent from `index.json`. Intake should adopt existing vault bytes without a second copy. `subject_vessels` must also be set on those new records, which `import_pdf` and the CLI cannot do today.
8. **Tests that break per artifact.** `test_no_parallel_blob_store_was_created` and `test_unattributed_records_carry_no_empty_assertion` hardcode the artifact set, so each new registration fails them. These should be fixed before the first fleet intake.
9. **Reader attribution.** `READER` is fixed as `Codex AI / registered PDF observation`. A reading by any other agent would be misattributed, so it needs to become a recorded field.
10. **Batch size.** The limit of 8 claims per batch stays workable if batches are per ship and per review round.
11. **Provenance fields.** `origin_limit` is free text. Fleet intake would benefit from structured download URL, retrieval date and attestation fields, since the Meraviglia file has none of the three.

## Identity source catalogue

`src:itu-maritime`, used for every seed MMSI and call sign, appears in `knowledge/sources/registry.json` but has no record file under `knowledge/sources/official/`, where only `src_itu-mars.json` exists. Any correction also needs a real source record. The Bellissima correction's `src:ispra-marine-fuel-report-2024` is the pattern for one. It covers the earlier ISPRA report, so World Europa would need a new record for the 2024-data report.
