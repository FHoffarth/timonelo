# Fleet Evidence Track B: source and identity closure

Prepared 2026-11-05 from commit `cff78eb`. Research records only. No canonical record, evidence registry or human decision was changed.

The eight earlier review packages are unchanged. Where this report differs from the earlier README, this report is newer.

## Verified versus unresolved identities

All eight IMO numbers are now confirmed by two official-institutional sources: the ITU ship station list and the US Coast Guard PSIX database. Radio identifiers come from ITU. Rows are in [identity-closure.json](identity-closure.json).

| Ship | IMO | MMSI | Call sign | Stored IMO | State |
|---|---|---|---|---|---|
| Grandiosa | 9803613 | 215325000 | 9HA5063 | Correct | Verified |
| Virtuosa | 9803625 | 215610000 | 9HA5209 | Correct | Verified |
| Euribia | 9901544 | 256281000 | 9HA5782 | Correct | Verified, MMSI conflict resolved |
| World Europa | 9837420 | 256070000 | 9HA5682 | Correct | Verified |
| World America | 9837432 | 249193000 | 9HA6157 | Correct | Verified |
| Meraviglia | 9760512 | 249973000 | 9HA4455 | **Wrong: 9660463** | Verified, owner decision needed |
| Seascape | 9843807 | 256059000 | 9HA5677 | **Wrong: 9805348** | Verified, owner decision needed |
| Seashore | 9843792 | 215920000 | 9HA5370 | **Wrong: 9805336** | Verified, owner decision needed |

Source hierarchy, strongest first:

1. **Not obtained:** IMO GISIS and the Transport Malta register. Neither was read, so "verified" means ITU and USCG agree, not that a flag register was seen.
2. **ITU MARS:** read through its public search. It lists the ship with its IMO, and found no record for any of the three stored IMOs.
3. **USCG PSIX:** last updated 2 November 2026.
4. **UK MCA index, then insurer and tracker records.**

Discrepancies kept open:

- **Meraviglia:** PSIX has two more rows under this name, 9534690 (Panama) and a name-only Swiss row. Neither is explained.
- **Seascape:** the [Wikipedia infobox](https://en.wikipedia.org/wiki/MSC_Seascape) still shows Seashore's number. ITU and USCG both contradict it.
- **Dates:** ITU update dates have no stated format, so 02/11/2026 could be February or November.

### MSC Euribia MMSI

- **Current assignment:** ITU gives 256281000 for 9HA5782 and for IMO 9901544, with an update date shown as 06/01/2026.
- **The other number:** ITU assigns 256261000 to a different Maltese ship, HOUBARA (9HB9271), update date shown as 02/09/2024.
- **MCA row:** the October 2026 index still prints 256261000 for Euribia, on a row last amended 12-Jun-24. Given the ITU record, that row looks like a one-digit error.
- **History:** not established. ITU shows only current rows. Earlier MCA files returned HTTP 410 from GOV.UK, and archived copies failed. Nothing found shows that 256261000 was ever assigned to Euribia, or rules it out.

## Meraviglia review-ready candidate set

[meraviglia-review-batch.json](meraviglia-review-batch.json) holds eight claims read from plan edition 11.2025 DEU, SHA-256 `77f5a51b…45e9`. They use the exact claim fields the Evidence Factory expects.

- Broadway Theatre: decks 5, 6
- Waves Restaurant: deck 5
- Panorama Restaurant: deck 6
- Butcher's Cut, Kaito Teppanyaki, Casino Imperiale, Carousel Lounge: deck 7
- Marketplace Buffet: deck 15

Each label was reproduced by the factory's own box-reading routine, and each box sits under the matching deck heading. I also checked placement by eye on rendered pages. The artifact ID is empty because the plan is unregistered, so the batch cannot enter the factory as it stands.

## Seven missing-document requirements

[ACQUISITION_CHECKLIST.md](ACQUISITION_CHECKLIST.md) lists the exact German and English file names and URLs for all seven plans. All were found in MSC-domain search results, which replaces the earlier "unconfirmed pattern" status. None could be opened by this review.

MSC's official ship maps for all seven ships do answer automated requests, and that document class can support `deck.venue_present`. They are not deck plans, and I did not download them.

## Source acquisition and rights limitations

- Deck plans and ship maps are `CITE_ONLY`, and artwork redistribution is not authorized. No PDF, crop or page image is committed.
- MSC plan hosts return HTTP 401 and cbp.gov returned 403. Neither was worked around, so the CBP rows remain unread and are not relied on.
- ITU and USCG rows are transcriptions from live pages, not stored bytes, so they have no hashes.
- ITU returned 403 and 429 after a burst of my queries. I stopped, waited, and finished at one query about every 20 seconds. PSIX searches were also run by script in the browser. Neither site needed a sign-in.
- The held plan has no recorded URL, date or owner attestation.
- MSC technical sheets for Seascape and Euribia were read and state no IMO, so no MSC operator source for identity exists yet.

Two corrections to the earlier README:

- The MCA file it calls the August index is byte-identical to the current October 2026 file, so no later index is outstanding.
- It said only the Seashore plan URL was confirmed. All seven now are.

## Exact remaining owner decisions

[OWNER_DECISIONS.md](OWNER_DECISIONS.md) is the single sheet:

- ID-1 to ID-3: the three IMO corrections
- ID-4: the Euribia MMSI
- ID-5: the remaining generated radio identifiers and their source attribution
- SRC-1: the origin statement for the held Meraviglia plan
- MER-DK-01 to MER-DK-08: the eight deck claims

Two other things need your action: downloading the seven plans, and saying whether the ship maps should be fetched.

## Local commit and file inventory

The commit SHA is given in the delivery message. All files are new, under `reports/fleet-evidence-expansion/closure/`:

- `REPORT.md`
- `OWNER_DECISIONS.md`
- `ACQUISITION_CHECKLIST.md`
- `identity-closure.json`
- `meraviglia-review-batch.json`
- `validate_closure.py`

`validate_closure.py` passes 28 of 28 read-only checks.
