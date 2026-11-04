# MSC Seascape identity-resolution dossier

Prepared 2026-11-04. Status: **blocked pending an owner decision.** No canonical record was changed.

## The question

Is the IMO number of MSC Seascape 9843807, as the evidence indicates, or 9805348, as stored in `knowledge/ships/msc-seascape/identity.json:9`?

## Why the stored value is doubtful

- Seeded by `tools/expand_world_coverage.py` and carried with `src:imo-gisis` and trust `OFFICIAL`, but `knowledge/sources/official/src_imo-gisis.json` is a generic catalogue entry with no retrieval record for this ship.
- The stored MMSI 248805348 is `248` plus the last six IMO digits, and the call sign 9HA5348 is `9HA` plus the last four. Both look generated rather than observed.
- A web search for 9805348 found no vessel record. That is weak evidence, since it does not prove the number is unassigned, but no source ties it to this ship.

## Evidence for the candidate

| Source | Class | Observed |
|---|---|---|
| [US Customs and Border Protection](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf) | OFFICIAL_GOVERNMENT_SEARCH_EXCERPT_ONLY | search-index reading only |
| [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843807-msc-seascape) | INDEPENDENT_MARITIME_TRACKING | IMO 9843807 with 9HA5677 |
| [VesselFinder](https://www.vesselfinder.com/vessels/details/9843807) | INDEPENDENT_MARITIME_TRACKING | IMO 9843807 |
| [Shipspotting](https://www.shipspotting.com/photos/3497437) | INDEPENDENT_MARITIME_TRACKING | IMO 9843807 |

## Radio identifiers

| Field | Stored | Candidate | Sources |
|---|---|---|---|
| mmsi | 248805348 | 256059000 | UK Maritime and Coastguard Agency, VesselFinder, Shipspotting |
| call_sign | 9HA5348 | 9HA5677 | UK Maritime and Coastguard Agency, usebase open-gov aggregator |

## Counterevidence

Counterevidence: the Wikipedia infobox and luxurycruiseconnections give 9843792, which belongs to MSC Seashore. CruiseShipTracking gives 9745366 and 9745354, which no other source supports.

## What would close it

Any one of these, read by the owner: the Transport Malta or IMO GISIS record, an Equasis entry, or the ship's class record. The CBP CF-1400 row is worth opening too if a registry cannot be reached.

## Notes

- The main risk here is a swap with MSC Seashore. Wikipedia's infobox gives Seascape the Seashore number, so a decision should be taken on both ships together.
- Radio identifiers are consistent: MCA, Shipspotting and VesselFinder agree on MMSI 256059000, and the MCA and usebase agree on 9HA5677.

## Owner decision

Decision: OPEN. Reviewer: unset. Date: unset. Reason: unset.
