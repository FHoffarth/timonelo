# Fleet evidence expansion, Track B

Prepared 2026-11-04 from `develop` at `6be38ab`. Research records only. No canonical record, registry entry or human decision was created.

**Final status: FLEET EVIDENCE PREPARATION PARTIAL.** Source inventory, identity evidence, dossiers, review packages and compatibility notes are complete. The five deck-location batches were not produced, because no primary deck plan for those ships could be obtained.

The main finding is that all eight ships carry generated radio identifiers, and three carry an IMO number that the evidence contradicts.

## 1. Source inventory

Full records: [source-inventory.json](source-inventory.json).

| Ship | Deck plan held | Edition | SHA-256 | Registered artifact |
|---|---|---|---|---|
| MSC Grandiosa | No | | | None |
| MSC Virtuosa | No | | | None |
| MSC Euribia | No | | | None |
| MSC World Europa | No | | | None |
| MSC World America | No | | | None |
| MSC Meraviglia | Yes, in the repo vault | 11.2025 DEU | `77f5a51b…45e9` | None |
| MSC Seascape | No | | | None |
| MSC Seashore | No | | | None |

Searched: the artifact index and vault, `knowledge/`, the owner's Drive (read-only), and PDF names in local Downloads, Documents and Desktop. The Drive's MSC folder holds only Divina and Seaside, and the Bellissima plans sit in another folder. The local scan exited with code 1, probably on unreadable folders, after reaching the last root, so an unreadable subfolder could still hide a file.

A second Meraviglia file exists locally (`6c343a1b…87f2`). It is a 2018 single sheet produced by a file converter, so it is not publisher bytes and is not recommended as evidence.

## 2. IMO and MMSI evidence matrix

Full records with sources: [identity-evidence-matrix.json](identity-evidence-matrix.json). Readable decision list: [OWNER_REVIEW.md](OWNER_REVIEW.md).

| Ship | Stored IMO | Candidate IMO | Stored MMSI | Candidate MMSI | Candidate call sign | Strongest IMO evidence |
|---|---|---|---|---|---|---|
| Grandiosa | 9803613 | same | 248803613 | 215325000 | 9HA5063 | Insurer |
| Virtuosa | 9803625 | same | 248803625 | 215610000 | 9HA5209 | Insurer |
| Euribia | 9901544 | same | 248901544 | **unresolved** | 9HA5782 | Trackers only |
| World Europa | 9837420 | same | 248837420 | 256070000 | 9HA5682 | Government and insurer |
| World America | 9837432 | same | 248837432 | 249193000 | 9HA6157 | Trackers, CBP excerpt unread |
| Meraviglia | **9660463** | **9760512** | 248660463 | 249973000 | 9HA4455 | Insurer and trackers |
| Seascape | **9805348** | **9843807** | 248805348 | 256059000 | 9HA5677 | Trackers, CBP excerpt unread |
| Seashore | **9805336** | **9843792** | 248805336 | 215920000 | 9HA5370 | Trackers, CBP excerpt unread |

By evidence class:

- **Official registry:** none obtained for any ship. GISIS, Transport Malta, Equasis, ITU MARS and class records were not read.
- **MSC operator:** none obtained. MSC hosts refused automated requests.
- **Government, non-registry:** the [UK MCA index](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) gives call sign and MMSI for all eight, and [ISPRA](https://www.isprambiente.gov.it/files2025/pubblicazioni/documenti-tecnici/relazione-zolfo-2024_sitoweb.pdf#page=44) gives the World Europa IMO. Direct retrieval of the [CBP CF-1400 file](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf) was refused, so only a search-index reading of it was seen.
- **Independent tracking and insurer:** [Steamship Mutual](https://www.steamshipmutual.com/msc-meraviglia) covers four ships. Euribia, World America, Seascape and Seashore have no page at the URLs tried.
- **Unverified seed:** every stored IMO, MMSI and call sign. All are marked `OFFICIAL`, but no retrieval record supports that. Each stored MMSI is `248` plus the last six IMO digits, and each call sign is `9HA` plus the last four.

Contradictions:

- **Euribia MMSI:** the MCA gives 256261000, while [MarineLink](https://ports.marinelink.com/vessels/vessel/256281000), MagicPort, VesselFinder and Wikipedia give 256281000. This favours a transcription slip in the index, but only ITU MARS would settle it. No value is proposed.
- **Seascape IMO:** the [Wikipedia infobox](https://en.wikipedia.org/wiki/MSC_Seascape) gives 9843792, which is Seashore's number. Decide these two ships together.
- **IMO check digits:** every number tested passes, seeds included, so the check separates nothing here.

## 3. Candidate review batches

**None were produced.** No plan for Grandiosa, Virtuosa, Euribia, World Europa or World America is held, so nothing is directly observable. The brief asked for batches where sources support them, and third-party copies are not admissible. A batch also needs a registered artifact ID and at least one claim.

Each ship has a package in [review-packages/](review-packages/) with `deck_location_candidates` empty and its identity candidates ready for decision. All decision fields are unset, across 24 candidates.

## 4. Identity-resolution dossiers

- [MSC Meraviglia](dossiers/msc-meraviglia.md)
- [MSC Seascape](dossiers/msc-seascape.md)
- [MSC Seashore](dossiers/msc-seashore.md)

No admission-ready batch exists for these ships. For Meraviglia, [meraviglia-page-locators.json](meraviglia-page-locators.json) maps 15 decks and 146 raw label fragments on pages 3 to 5. It is a finding aid only. Column placement was checked by eye on page 3, and the fragments have not been reviewed.

## 5. Source and rights limitations

- Deck plans are `CITE_ONLY`, and artwork redistribution is not authorized. No PDF or page image is included here.
- MSC hosts return HTTP 401 to automated clients. Early probes sent a browser-like User-Agent. That was stopped, and the block was not worked around.
- Only the Seashore plan URL was [seen in a search index](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-seashore/MSC_SEASHORE_DECKPLAN.pdf). The other URLs in the packages are unconfirmed guesses from that pattern.
- The held Meraviglia plan has no recorded download URL, date or owner attestation, and states no IMO.
- Government sources bind to ships mostly by name. The MCA index read here is the August file, and a later one may exist.
- Tracker pages and the search-index readings were not stored or hashed. Only the MCA and ISPRA files have digests, and those copies were not committed.
- A web search on the three doubtful seed IMOs found no vessel. That is weak evidence, and does not show the numbers are unassigned.

## 6. Compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md). The identity gate currently accepts seed values as truth, so a Meraviglia batch built on the wrong IMO would pass that gate. `validate_packages.py` passes 15 of 15 read-only checks.

## 7. Changed files

All new, under `reports/fleet-evidence-expansion/`:

- `README.md`, `OWNER_REVIEW.md`, `COMPATIBILITY.md`
- `source-inventory.json`, `identity-evidence-matrix.json`, `meraviglia-page-locators.json`
- `validate_packages.py`
- `dossiers/`: `msc-meraviglia.md`, `msc-seascape.md`, `msc-seashore.md`
- `review-packages/`: one JSON file per ship, eight in total

No tracked file was modified.

## 8. Remaining blockers

1. **Deck plans for seven ships.** Someone must download them from MSC in a normal browser and record the URL, date and attestation.
2. **Owner identity decisions.** Meraviglia, Seascape and Seashore block everything else for those ships.
3. **A registry read.** Equasis, GISIS or Transport Malta needs an owner login. ITU MARS is what resolves Euribia.
4. **Intake route.** No supported path registers a new plan with `subject_vessels`, which sits with the Codex track.
