# Launch fleet identity quarantine — 2026-11-04

This read-only audit covers the eight non-Bellissima launch identities. The
machine-readable enforcement record is
`src/timonelo/evidence/vessel_identity_quarantine.json`. The `authoritative_*`
keys preserve what the repository currently stores; they do not endorse those
values. No Knowledge or Evidence records were corrected, approved or published.

| Ship | Persisted IMO | Unapproved candidate IMO | Persisted MMSI | Disposition |
| --- | --- | --- | --- | --- |
| MSC Meraviglia | 9660463 | 9760512 | 248660463 | IMO unresolved; canonical vessel admission blocked |
| MSC Grandiosa | 9803613 | — | 248803613 | IMO unchanged; MMSI unresolved |
| MSC Euribia | 9901544 | — | 248901544 | IMO unchanged; MMSI unresolved |
| MSC Virtuosa | 9803625 | — | 248803625 | IMO unchanged; MMSI unresolved |
| MSC World Europa | 9837420 | — | 248837420 | IMO unchanged; MMSI unresolved |
| MSC World America | 9837432 | — | 248837432 | IMO unchanged; MMSI unresolved |
| MSC Seascape | 9805348 | 9843807 | 248805348 | IMO unresolved; canonical vessel admission blocked |
| MSC Seashore | 9805336 | 9843792 | 248805336 | IMO unresolved; canonical vessel admission blocked |

The candidate IMOs come from the integrity-hardening task and remain candidate
identifiers only. No independent source retrieval or identity confirmation was
performed. A valid IMO checksum establishes syntax, not the ship's identity.

Every MMSI above equals `248` followed by the last six digits of the persisted
IMO. This repeated pattern is a reason to request assignment evidence; it does
not prove that any particular MMSI is wrong. Each identity file labels the MMSI
`src:itu-maritime` and `OFFICIAL`, but a source label supplies neither a physical
artifact nor an assignment locator. All eight MMSI admissions remain blocked
pending evidence and human review. The five `audit_only` records grant no MMSI
verification and do not constitute new approval of their existing IMOs.

For the three conflicting IMO records, canonical admission stays closed until
independent vessel identity evidence resolves the conflict through the existing
governance process. Private acquisition and candidate preparation may proceed;
neither changes authoritative identity nor permits publication. Existing
Bellissima statements and ART-0002 attribution are outside this audit and remain
unchanged.
