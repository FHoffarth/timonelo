# MSC Meraviglia identity-resolution dossier

Prepared 2026-11-04. Status: **blocked pending an owner decision.** No canonical record was changed.

## The question

Is the IMO number of MSC Meraviglia 9760512, as the evidence indicates, or 9660463, as stored in `knowledge/ships/msc-meraviglia/identity.json:9`?

## Why the stored value is doubtful

- Seeded by `tools/expand_world_coverage.py` and carried with `src:imo-gisis` and trust `OFFICIAL`, but `knowledge/sources/official/src_imo-gisis.json` is a generic catalogue entry with no retrieval record for this ship.
- The stored MMSI 248660463 is `248` plus the last six IMO digits, and the call sign 9HA0463 is `9HA` plus the last four. Both look generated rather than observed.
- A web search for 9660463 found no vessel record. That is weak evidence, since it does not prove the number is unassigned, but no source ties it to this ship.

## Evidence for the candidate

| Source | Class | Observed |
|---|---|---|
| [Steamship Mutual](https://www.steamshipmutual.com/msc-meraviglia) | INSURER_FIRST_PARTY | IMO 9760512, Valletta, GT 171598, Compania Naviera Vista 1 |
| [VesselFinder](https://www.vesselfinder.com/vessels/details/9760512) | INDEPENDENT_MARITIME_TRACKING | IMO 9760512 |

## Radio identifiers

| Field | Stored | Candidate | Sources |
|---|---|---|---|
| mmsi | 248660463 | 249973000 | UK Maritime and Coastguard Agency, VesselFinder |
| call_sign | 9HA0463 | 9HA4455 | UK Maritime and Coastguard Agency |

## What would close it

Any one of these, read by the owner: the Transport Malta or IMO GISIS record, or an Equasis entry. The insurer page plus the tracker agreement may already be enough for the owner, following the Bellissima precedent in `reports/golden-ship-identity-decision/`.

## Notes

- A plan is already held, so this ship can move first once its IMO is decided.
- `tests/test_artifact_registry_sha_vault.py:20` already names the held plan's hash, and `tests/test_knowledge_schema_validation.py:510` uses 9760512 only as a neutral fixture value, so neither is identity evidence.
- Rich `knowledge/ships/msc-meraviglia/*.json` files predate the evidence regime; they should not be treated as confirmation of venue decks.

## Owner decision

Decision: OPEN. Reviewer: unset. Date: unset. Reason: unset.
