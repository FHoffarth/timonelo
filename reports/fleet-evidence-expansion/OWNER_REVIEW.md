# Owner review sheet

Prepared 2026-11-04. Every decision below is open. Nothing here has been applied.

Each row is one decision. Enter APPROVE, REJECT or DEFER in the matching `review-packages/<ship>.json` entry with your name, date and reason. No deck-location rows appear, because no reading was possible (see README section 3).

## MSC Grandiosa

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-GRANDIOSA-IMO | 9803613 | 9803613 | MATCHES_SEED | [Steamship Mutual](https://www.steamshipmutual.com/msc-grandiosa) | OPEN |
| FEP-ID-GRANDIOSA-MMSI | 215325000 | 248803613 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |
| FEP-ID-GRANDIOSA-CALLSIGN | 9HA5063 | 9HA3613 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |

## MSC Virtuosa

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-VIRTUOSA-IMO | 9803625 | 9803625 | MATCHES_SEED | [Steamship Mutual](https://www.steamshipmutual.com/msc-virtuosa) | OPEN |
| FEP-ID-VIRTUOSA-MMSI | 215610000 | 248803625 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |
| FEP-ID-VIRTUOSA-CALLSIGN | 9HA5209 | 9HA3625 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |

## MSC Euribia

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-EURIBIA-IMO | 9901544 | 9901544 | MATCHES_SEED | [VesselFinder](https://www.vesselfinder.com/vessels/details/9901544); [MarineLink](https://ports.marinelink.com/vessels/vessel/256281000) | OPEN |
| FEP-ID-EURIBIA-MMSI | unresolved: 256261000 or 256281000 | 248901544 | UNRESOLVED_CONTRADICTION | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) 256261000, row amended 12-Jun-24; [VesselFinder](https://www.vesselfinder.com/vessels/details/9901544); [MarineLink](https://ports.marinelink.com/vessels/vessel/256281000); [MagicPort](https://magicport.ai/vessels/passenger/msc-euribia-mmsi-256281000); [Wikipedia](https://en.wikipedia.org/wiki/MSC_Euribia) | OPEN |
| FEP-ID-EURIBIA-CALLSIGN | 9HA5782 | 9HA1544 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [MarineLink](https://ports.marinelink.com/vessels/vessel/256281000) | OPEN |

Note: CONTRADICTION. The government row says 256261000; every tracker says 256281000. The numbers differ by one digit. Trackers read MMSI off live AIS, which favours 256281000 and suggests a transcription slip in the index, but that is an inference. ITU MARS would settle it and was not obtained.

## MSC World Europa

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-WORLD-EUROPA-IMO | 9837420 | 9837420 | MATCHES_SEED | [ISPRA (Italy)](https://www.isprambiente.gov.it/files2025/pubblicazioni/documenti-tecnici/relazione-zolfo-2024_sitoweb.pdf); [Steamship Mutual](https://www.steamshipmutual.com/msc-world-europa) | OPEN |
| FEP-ID-WORLD-EUROPA-MMSI | 256070000 | 248837420 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |
| FEP-ID-WORLD-EUROPA-CALLSIGN | 9HA5682 | 9HA7420 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |

## MSC World America

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-WORLD-AMERICA-IMO | 9837432 | 9837432 | MATCHES_SEED | [US Customs and Border Protection](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf); [VesselFinder](https://www.vesselfinder.com/vessels/details/9837432); [MarineVesselTraffic](https://www.marinevesseltraffic.com/ship-owner-manager-ism-data/MSC-WORLD-AMERICA/9837432/249193000) | OPEN |
| FEP-ID-WORLD-AMERICA-MMSI | 249193000 | 248837432 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [MarineVesselTraffic](https://www.marinevesseltraffic.com/ship-owner-manager-ism-data/MSC-WORLD-AMERICA/9837432/249193000) | OPEN |
| FEP-ID-WORLD-AMERICA-CALLSIGN | 9HA6157 | 9HA7432 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |

Note: Stray records treated as data errors: TrustedDocks shows a tug under this number and another listing shows MMSI 314151622 for Idyllic Ocean.

## MSC Meraviglia

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-MERAVIGLIA-IMO | 9760512 | 9660463 | CORRECTION_PROPOSED | [Steamship Mutual](https://www.steamshipmutual.com/msc-meraviglia); [VesselFinder](https://www.vesselfinder.com/vessels/details/9760512) | OPEN |
| FEP-ID-MERAVIGLIA-MMSI | 249973000 | 248660463 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [VesselFinder](https://www.vesselfinder.com/vessels/details/9760512) | OPEN |
| FEP-ID-MERAVIGLIA-CALLSIGN | 9HA4455 | 9HA0463 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv) | OPEN |

## MSC Seascape

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-SEASCAPE-IMO | 9843807 | 9805348 | CORRECTION_PROPOSED | [US Customs and Border Protection](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf); [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843807-msc-seascape); [VesselFinder](https://www.vesselfinder.com/vessels/details/9843807); [Shipspotting](https://www.shipspotting.com/photos/3497437) | OPEN |
| FEP-ID-SEASCAPE-MMSI | 256059000 | 248805348 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [VesselFinder](https://www.vesselfinder.com/vessels/details/9843807); [Shipspotting](https://www.shipspotting.com/photos/3497437) | OPEN |
| FEP-ID-SEASCAPE-CALLSIGN | 9HA5677 | 9HA5348 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843807-msc-seascape) | OPEN |

Note: Counterevidence: the Wikipedia infobox and luxurycruiseconnections give 9843792, which belongs to MSC Seashore. CruiseShipTracking gives 9745366 and 9745354, which no other source supports.

## MSC Seashore

| ID | Candidate | Repo seed | Status | Evidence | Decision |
|---|---|---|---|---|---|
| FEP-ID-SEASHORE-IMO | 9843792 | 9805336 | CORRECTION_PROPOSED | [US Customs and Border Protection](https://www.cbp.gov/sites/default/files/2026-08/CF1400%20-%20Record%20of%20Vessel%20in%20Foreign%20Trade%20-%20Entrances.pdf); [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843792-msc-seashore); [VesselFinder](https://www.vesselfinder.com/vessels/details/9843792) | OPEN |
| FEP-ID-SEASHORE-MMSI | 215920000 | 248805336 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [VesselFinder](https://www.vesselfinder.com/vessels/details/9843792) | OPEN |
| FEP-ID-SEASHORE-CALLSIGN | 9HA5370 | 9HA5336 | CORRECTION_PROPOSED | [UK Maritime and Coastguard Agency](https://assets.publishing.service.gov.uk/media/6aa25d214e17456e2cdf528c/International-search-and-rescue-index-August.csv); [usebase open-gov aggregator](https://open-gov.usebase.io/vessels/9843792-msc-seashore) | OPEN |
