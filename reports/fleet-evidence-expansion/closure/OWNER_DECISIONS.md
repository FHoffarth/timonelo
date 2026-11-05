# Owner decision sheet

Prepared 2026-11-05. There are 5 identity decisions, 1 source statement and 8 deck claims. All are open, and nothing has been applied.

Mark each row APPROVE, REJECT or DEFER, with your name, the date and a reason. Records: [identity-closure.json](identity-closure.json) and [meraviglia-review-batch.json](meraviglia-review-batch.json).

## Identity decisions

ITU means the [ship station list](https://mmsapp.itu.int/mmsapp/ShipStation/list). USCG means the [PSIX vessel search](https://cgmix.uscg.mil/PSIX/PSIXSearch.aspx). Neither is a flag register. IMO GISIS and the Transport Malta register were not read.

| ID | Change proposed | Currently stored | Evidence | Unresolved | Decision |
|---|---|---|---|---|---|
| ID-1 | MSC Meraviglia IMO becomes 9760512 | 9660463 | ITU and USCG agree, with 9HA4455 | Two other USCG rows carry this name: 9534690 (Panama) and a name-only Swiss row | OPEN |
| ID-2 | MSC Seascape IMO becomes 9843807 | 9805348 | ITU and USCG agree, with 9HA5677 | Wikipedia still shows Seashore's number | OPEN |
| ID-3 | MSC Seashore IMO becomes 9843792 | 9805336 | ITU and USCG agree, with 9HA5370 | None | OPEN |
| ID-4 | MSC Euribia MMSI becomes 256281000 | 248901544 | ITU row for 9HA5782 and IMO 9901544 | The MCA index still prints 256261000, which ITU assigns to HOUBARA | OPEN |
| ID-5 | Replace stored call signs and the other seven MMSIs, and drop the `src:imo-gisis` and `src:itu-maritime` attribution, using the table below | Generated values | ITU rows for all eight | ITU update dates have no stated format | OPEN |

ITU found no record for any of the three stored IMO numbers: 9660463, 9805348 and 9805336.

### Values covered by ID-5

| Ship | Stored MMSI | ITU MMSI | Stored call sign | ITU call sign |
|---|---|---|---|---|
| Grandiosa | 248803613 | 215325000 | 9HA3613 | 9HA5063 |
| Virtuosa | 248803625 | 215610000 | 9HA3625 | 9HA5209 |
| Euribia | see ID-4 | see ID-4 | 9HA1544 | 9HA5782 |
| World Europa | 248837420 | 256070000 | 9HA7420 | 9HA5682 |
| World America | 248837432 | 249193000 | 9HA7432 | 9HA6157 |
| Meraviglia | 248660463 | 249973000 | 9HA0463 | 9HA4455 |
| Seascape | 248805348 | 256059000 | 9HA5348 | 9HA5677 |
| Seashore | 248805336 | 215920000 | 9HA5336 | 9HA5370 |

## Source statement

| ID | What is needed | Decision |
|---|---|---|
| SRC-1 | State where and when `MSC_MERAVIGLIA_DECKPLAN_GER.pdf` was downloaded (SHA-256 `77f5a51b…45e9`). No URL or date is recorded, and the plan cannot be registered honestly without your statement. | OPEN |

## Meraviglia deck claims

These claims depend on ID-1 and SRC-1. Each one is what plan edition 11.2025 DEU labels, not a statement of current operations. Physical page numbers refer to the PDF.

| ID | Venue | Deck(s) | Page | Where on the page | Decision |
|---|---|---|---|---|---|
| MER-DK-01 | Broadway Theatre | 5, 6 | 3 | Forward section of the Deck 5 and Deck 6 columns | OPEN |
| MER-DK-02 | Waves Restaurant | 5 | 3 | Deck 5 column, aft half | OPEN |
| MER-DK-03 | Panorama Restaurant | 6 | 3 | Deck 6 column, aft end | OPEN |
| MER-DK-04 | Butcher's Cut | 7 | 3 | Deck 7 column, vertical label starboard of the galleria | OPEN |
| MER-DK-05 | Kaito Teppanyaki | 7 | 3 | Deck 7 column, vertical label port of the galleria | OPEN |
| MER-DK-06 | Casino Imperiale | 7 | 3 | Deck 7 column, aft half | OPEN |
| MER-DK-07 | Carousel Lounge | 7 | 3 | Deck 7 column, two-line label at the aft end | OPEN |
| MER-DK-08 | Marketplace Buffet | 15 | 5 | Deck 15 column, two vertical labels, aft half | OPEN |

For MER-DK-01, the stored knowledge disagrees with itself: `entertainment.json` says deck 6 and `venues.json` says deck 5. The plan labels both.

Your decisions here record your review. They cannot be fed to the factory as they stand: bindings match exact JSON, so these claims must be rebuilt with the real artifact ID after registration, and the rebuilt claims need a matching decision record.
