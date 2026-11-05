# Official MSC source expansion

Prepared 2026-11-05 from commit `ffce96b`. Research only. No artifact was registered, no decision was recorded, and no canonical record changed.

**Final status: SOURCE EXPANSION READY FOR REVIEW.** All seven ship maps were retrieved and read. Five are eligible candidates and two need review until their stored IMO numbers are corrected. No official deck-plan PDF was obtained, and the current Evidence Factory would refuse these maps until the missing-version question is settled.

## 1. Official Ship Maps retrieved

All seven came from `service.msccruises.com/images/shipmap/pdfs/` over plain HTTPS on 2026-11-05 with HTTP 200. Full records are in [source-register.json](source-register.json).

| Ship | File | Bytes | Pages | SHA-256 |
|---|---|---|---|---|
| MSC Grandiosa | `gr_en-gb.pdf` | 1,194,308 | 10 | `679270bee3a41efdbd5dcb6eab4ce53c45c2d51713166f8e5e9e3b1592e5f2bb` |
| MSC Virtuosa | `vi_en-gb.pdf` | 1,213,843 | 10 | `d87c22e83f3a7e07bb59e0776aa05b2a9d0912bbd6e908d76c5162c9b6a282a0` |
| MSC Euribia | `er_en-gb.pdf` | 1,326,727 | 10 | `4ea7b06bf513e63aa7ee42931e629cd890ef1deb55348ff73596c38a2e837782` |
| MSC World Europa | `eu_en-gb.pdf` | 3,154,119 | 10 | `e8825bda8c88f529e987f79a9d28813482e582779157b84c3b70cd12619bd702` |
| MSC World America | `am_en-gb.pdf` | 1,541,888 | 17 | `f17d25c23930d1d357b8a239c4362d016f89c90c31298e5202ae2893f4727330` |
| MSC Seascape | `sc_en-gb.pdf` | 1,232,452 | 10 | `35f9f46f2e5477cb9fb65ed4bf4c2b7fbe5e3f5a335b4c0f684ba92885323ef7` |
| MSC Seashore | `sh_en-gb.pdf` | 2,587,869 | 10 | `cedd7c9d5e778bb8c1020a00183c356afc11ae9f3849f7f509b9640249d509ce` |

The MSC Meraviglia map (`mr_en-gb.pdf`, `7f9aad35…9916`) was also retrieved, for comparison only.

The official deck-plan PDFs were not retrieved. Their hosts refused automated access earlier, and that restriction stands.

## 2. Source eligibility results

| Ship | Result | Reason |
|---|---|---|
| Grandiosa | ELIGIBLE CANDIDATE | All tests met, version unknown |
| Virtuosa | ELIGIBLE CANDIDATE | All tests met, version unknown |
| Euribia | ELIGIBLE CANDIDATE | All tests met, version unknown |
| World Europa | ELIGIBLE CANDIDATE | All tests met, version unknown |
| World America | ELIGIBLE CANDIDATE | All tests met, version unknown; highest conflict count |
| Seascape | NEEDS REVIEW | Stored IMO 9805348 differs from verified 9843807 |
| Seashore | NEEDS REVIEW | Stored IMO 9805336 differs from verified 9843792; stray SEASCAPE label on page 2 |

None was classed NOT SUITABLE. These are research outcomes, not admission decisions.

The Seashore map's page 2 profile carries a tiny `SEASCAPE` label, the only sign of cross-ship reuse in the seven documents. It suggests the artwork was adapted from the sister ship.

## 3. Verified identities and edition status

Identities are unchanged from the earlier ITU and US Coast Guard verification, and no new contradiction appeared. Each map names its ship in the cover title, but none prints an IMO, so the link to an IMO comes from the title.

No map prints an edition or date. Every version is recorded as unknown. Production data is kept in the register but is not an edition:

- PDF creation dates: 21 August 2025 for five maps, 28 August 2025 for World Europa, 9 June 2026 for Seashore.
- Server last-modified: 26 October 2026 for all seven.

## 4. Candidate deck-location observations

Each map is read twice, independently. One reading is the "Deck" tables. The other is the deck index page, which lists labels under "DECK n" headings: page 2, or page 3 on World America.

- **Agreed:** both readings match.
- **One reading:** table only, so no second reading exists. Kept as an observation, not a first-batch claim.
- **Rejected:** the document contradicts itself. No deck value is recorded.

| Ship | Labels | Agreed | One reading | Rejected | First batch |
|---|---|---|---|---|---|
| Grandiosa | 87 | 67 | 18 | 2 | 8 |
| Virtuosa | 88 | 66 | 21 | 1 | 8 |
| Euribia | 84 | 59 | 22 | 3 | 8 |
| World Europa | 87 | 63 | 18 | 6 | 8 |
| World America | 86 | 55 | 23 | 8 | 8 |
| Seascape | 91 | 61 | 28 | 2 | 8 |
| Seashore | 91 | 57 | 32 | 2 | 8 |

Records are in [observations/](observations/), one file per ship, with the required vessel, source, label, deck value, claim, locator, version status, limitations and conflicts. Each file's first batch uses the Evidence Factory's claim fields, with the artifact ID and version empty.

Rejected readings are listed ship by ship in [HUMAN_REVIEW.md](HUMAN_REVIEW.md). Examples: on World Europa, La Brasserie Buffet prints deck 19 in its table but deck 20 in the index. On Seascape and Seashore, Interactive XD Cinema prints decks 18 and 7. Euribia's Delphi Theatre prints 5-6 but is indexed only under deck 6.

Two label pairs are held out of first batches as possible language variants of one venue: Aurora Boreale and Aurora Borealis on Euribia, Esagono and Hexagon on World Europa. Whether they are one venue is not established. Printed ranges are not expanded: "6-8" means decks 6 and 8, because the index lists only those.

## 5. Missing or unsuitable documents

- **Official deck plans:** seven still missing. [ACQUISITION_CHECKLIST.md](../closure/ACQUISITION_CHECKLIST.md) remains the download list.
- **Unsuitable documents:** none among the maps. Third-party plan copies stay excluded.
- **Theatres:** World Europa and World America theatre rows conflict, and Seashore's theatre is spelled two ways, so none is in a first batch. Those ships' theatre decks need a deck plan.

### Meraviglia comparison

The eight MER-DK candidates still rest on the held plan. The map agrees on seven. It differs on Broadway Theatre: the plan labels decks 5 and 6, while the map lists deck 6 only, in both tables and the index. Both readings are kept in [meraviglia-source-comparison.json](meraviglia-source-comparison.json), and neither overrides the other. The plan remains unregistered.

## 6. Copyright and provenance limitations

- Maps are `CITE_ONLY`, and artwork redistribution is not authorized. No PDF or image is committed. Files record short labels, deck values, digests and locators.
- Acquired bytes are in the session scratchpad only, which is temporary. Intake should download again and compare digests. If a digest differs, MSC has changed the file and readings must be redone.
- Retrieval origin is recorded by URL, date, server headers and digest. No independent check of authenticity exists beyond the official host.
- Maps establish a deck assignment only: no position, distance, adjacency or current operations. The Evidence Factory scope stays edition-bound, though these editions are unknown.

## 7. Consolidated human review requirements

[HUMAN_REVIEW.md](HUMAN_REVIEW.md) is one sheet with 56 open claims: 40 for the five eligible ships and 16 for Seascape and Seashore. Before those claims can be used:

1. **Unknown versions.** Decide how a map without a printed version is identified. The current factory refuses an empty version with `SOURCE_VERSION_MISMATCH`, confirmed by a probe. Inventing an edition is not an option; this needs a Codex contract decision, and the digest is an obvious stable identifier.
2. **Seascape and Seashore IMOs.** Decisions ID-2 and ID-3 from [OWNER_DECISIONS.md](../closure/OWNER_DECISIONS.md) remain open.
3. **Registration.** Each map needs a real artifact ID through a supported intake route. Claims must then be rebuilt, because decision bindings match exact JSON.
4. **Broadway Theatre.** Decide how MER-DK-01 should stand given the plan and map difference.

## 8. Changed files and validation

All files are new, under `reports/fleet-evidence-expansion/ship-maps/`:

- `SOURCE_EXPANSION_REPORT.md`, `HUMAN_REVIEW.md`
- `source-register.json`, `meraviglia-source-comparison.json`
- `extract_ship_maps.py`, `build_observations.py`, `validate_ship_maps.py`
- `observations/`: `msc-grandiosa.json`, `msc-virtuosa.json`, `msc-euribia.json`, `msc-world-europa.json`, `msc-world-america.json`, `msc-seascape.json`, `msc-seashore.json`

`validate_ship_maps.py` passes 85 of 85 read-only checks. The extractor was tested against the audited Bellissima map and reproduces its 115 rows, 87 labels and all deck values. The factory's own box routine reproduces all 56 first-batch readings.
