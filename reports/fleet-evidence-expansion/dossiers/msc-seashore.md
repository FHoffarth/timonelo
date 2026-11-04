# MSC Seashore identity-resolution dossier

Prepared 2026-11-04. Status: **blocked pending an owner decision.** No canonical record was changed.

## The question

Is the IMO number of MSC Seashore 9843792, as the evidence indicates, or 9805336, as stored in `knowledge/ships/msc-seashore/identity.json:9`?

## Why the stored value is doubtful

- Seeded by `tools/expand_world_coverage.py` and carried with `src:imo-gisis` and trust `OFFICIAL`, but `knowledge/sources/official/src_imo-gisis.json` is a generic catalogue entry with no retrieval record for this ship.
- The stored MMSI 248805336 is `248` plus the last six IMO digits, and the call sign 9HA5336 is `9HA` plus the last four. Both look generated rather than observed.
- A web search for 9805336 found no vessel record. That is weak evidence, since it does not prove the number is unassigned, but no source ties it to this ship.

## Evidence for the candidate

| Source | Class | Observed |
|---|---|---|
| [US Customs and Border Protection](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf) | OFFICIAL_GOVERNMENT_SEARCH_EXCERPT_ONLY | search-index reading only |
| [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843792-msc-seashore) | INDEPENDENT_MARITIME_TRACKING | IMO 9843792 with 9HA5370 |
| [VesselFinder](https://www.vesselfinder.com/vessels/details/9843792) | INDEPENDENT_MARITIME_TRACKING | IMO 9843792 |

## Radio identifiers

| Field | Stored | Candidate | Sources |
|---|---|---|---|
| mmsi | 248805336 | 215920000 | UK Maritime and Coastguard Agency, VesselFinder |
| call_sign | 9HA5336 | 9HA5370 | UK Maritime and Coastguard Agency, usebase open-gov aggregator |

## What would close it

Any one of these, read by the owner: the Transport Malta or IMO GISIS record, an Equasis entry, or the ship's class record. The CBP CF-1400 row is worth opening too if a registry cannot be reached.

## Notes

- This ship's number is not disputed among sources for Seashore itself. The dispute comes from sources assigning it to Seascape.
- It is the only ship of the eight with a deck plan URL seen in a search index, on the MSC UK host.

## Owner decision

Decision: OPEN. Reviewer: unset. Date: unset. Reason: unset.
