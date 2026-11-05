# Acquisition checklist: seven missing MSC deck plans

Checked 2026-11-05. Every URL below appeared in a search restricted to MSC's own domains, under a matching document title. None was opened, because MSC's plan hosts refuse automated requests (HTTP 401). Hashes and page counts stay unknown until the files are held.

German editions are preferred, because the held Bellissima and Meraviglia plans are DEU editions.

| Done | Ship | German edition (preferred) | English edition |
|---|---|---|---|
| [ ] | MSC Grandiosa | [MSC_GRANDIOSA_DECKPLAN_GER.pdf](https://www.msccruises.at/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_GRANDIOSA_DECKPLAN_GER.pdf) | [MSC_GRANDIOSA_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-grandiosa/MSC_GRANDIOSA_DECKPLAN.pdf) |
| [ ] | MSC Virtuosa | [MSC_VIRTUOSA_DECKPLAN_GER.pdf](https://www.msccruises.de/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_VIRTUOSA_DECKPLAN_GER.pdf) | [MSC_VIRTUOSA_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-virtuosa/MSC_VIRTUOSA_DECKPLAN.pdf) |
| [ ] | MSC Euribia | [MSC_EURIBIA_DECKPLAN_GER.pdf](https://www.msccruises.at/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_EURIBIA_DECKPLAN_GER.pdf) | [MSC_EURIBIA_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-euribia/MSC_EURIBIA_DECKPLAN.pdf) |
| [ ] | MSC World Europa | [MSC_WORLD_EUROPA_DECKPLAN_GER.pdf](https://www.msccruises.de/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_WORLD_EUROPA_DECKPLAN_GER.pdf) | [MSC_WORLD_EUROPA_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-world-europa/MSC_WORLD_EUROPA_DECKPLAN.pdf) |
| [ ] | MSC World America | [MSC_WORLD_AMERICA_DECKPLAN_GER.pdf](https://www.msccruises.at/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_WORLD_AMERICA_DECKPLAN_GER.pdf) | [MSC_WORLD_AMERICA_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-world-america/MSC_WORLD_AMERICA_DECKPLAN.pdf) |
| [ ] | MSC Seascape | [MSC_SEASCAPE_DECKPLAN_GER.pdf](https://www.msccruises.de/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_SEASCAPE_DECKPLAN_GER.pdf) | [MSC_SEASCAPE_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-seascape/MSC_SEASCAPE_DECKPLAN.pdf) |
| [ ] | MSC Seashore | [MSC_SEASHORE_DECKPLAN_GER.pdf](https://www.msccruises.de/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_SEASHORE_DECKPLAN_GER.pdf) | [MSC_SEASHORE_DECKPLAN.pdf](https://www.msccruises.co.uk/content/dam/msc-cruises/b2c-assets/fleet/msc-seashore/MSC_SEASHORE_DECKPLAN.pdf) |

Search excerpts put the German editions of Virtuosa, World Europa and Seashore at 11.2025, and the English editions of Grandiosa, Virtuosa, Euribia and Seashore at 10.2024. Take the edition from the file itself; these dates are not confirmed.

## For each file

1. Download it in your normal browser and leave the bytes untouched.
2. Record the URL, the download date and the printed edition mark.
3. Check that the cover names the ship you expected.
4. Leave it out of Git until a supported intake route exists.

## Alternative source: official ship maps

MSC also publishes ship maps that answered automated header checks with HTTP 200. These are venue-by-deck indexes, not deck plans. The `official_ship_map` class may support `deck.venue_present`, so they could supply venue claims without the plans. They were not downloaded, because that needs your go-ahead.

| Ship | File | Size in bytes | Last modified |
|---|---|---|---|
| MSC Grandiosa | [gr_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/gr_en-gb.pdf) | 1,194,308 | 2026-10-26 |
| MSC Virtuosa | [vi_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/vi_en-gb.pdf) | 1,213,843 | 2026-10-26 |
| MSC Euribia | [er_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/er_en-gb.pdf) | 1,326,727 | 2026-10-26 |
| MSC World Europa | [eu_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/eu_en-gb.pdf) | 3,154,119 | 2026-10-26 |
| MSC World America | [am_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/am_en-gb.pdf) | 1,541,888 | 2026-10-26 |
| MSC Seascape | [sc_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/sc_en-gb.pdf) | 1,232,452 | 2026-10-26 |
| MSC Seashore | [sh_en-gb.pdf](https://service.msccruises.com/images/shipmap/pdfs/sh_en-gb.pdf) | 2,587,869 | 2026-10-26 |

## Do not use

Third-party copies such as CruiseMapper, DC Cruising, Pure Holidays or agency brochures. They have no attributable MSC bytes.
