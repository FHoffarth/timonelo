# First Port Source-Matrix Templates

Status: **TEMPLATE ONLY — NO FACTS INGESTED**

These templates cover Barcelona, Marseille, Genoa, Naples, and Valletta. Rows are
research requirements, not claims that a source or value has been verified.

Allowed method values refer to the existing canonical Statement `Method`. Fallback
discovery does not authorize publication.

## Barcelona

| Entity / field | Preferred official source class | Fallback source class | Evidence method | Freshness sensitivity | Publication guardrail |
|---|---|---|---|---|---|
| Port identity / country | Port authority; official UN/LOCODE release | National gazetteer | `DIRECT` | Low; revalidate by release | Require artifact and locator |
| IANA timezone | IANA tzdb plus evidenced port coordinate | Reviewed authoritative gazetteer | `DIRECT` / `CALCULATED` | Medium at rule changes | Never copy fixed `UTC` placeholder |
| Port coordinate | Port-authority GIS/map | Human-reviewed OSM | `DIRECT` | Medium | Declare point semantics |
| Cruise terminal identity / coordinate | Port-authority terminal map/GIS | Human-reviewed OSM | `DIRECT` | High | Does not establish ship assignment |
| Route call / terminal assignment | Cruise-line itinerary plus port call/berth schedule | None for automatic publication | `DIRECT` | Very high | Scope to vessel/voyage/date; unknown remains null |
| Nearby transport / safety POI | Transit/municipal/medical authority | Reviewed OSM extract | `DIRECT` | High | Show provider and observation time |
| Straight-line distance | Canonical coordinate Statements | None | `CALCULATED` | Follows inputs | WGS84 geodesic; label straight-line |

## Marseille

| Entity / field | Preferred official source class | Fallback source class | Evidence method | Freshness sensitivity | Publication guardrail |
|---|---|---|---|---|---|
| Port identity / country | Port authority; official UN/LOCODE release | National gazetteer | `DIRECT` | Low; revalidate by release | Require artifact and locator |
| IANA timezone | IANA tzdb plus evidenced port coordinate | Reviewed authoritative gazetteer | `DIRECT` / `CALCULATED` | Medium at rule changes | Never copy fixed `UTC` placeholder |
| Port coordinate | Port-authority GIS/map | Human-reviewed OSM | `DIRECT` | Medium | Declare point semantics |
| Cruise terminal identity / coordinate | Port-authority terminal map/GIS | Human-reviewed OSM | `DIRECT` | High | Keep distinct terminal areas separate |
| Route call / terminal assignment | Cruise-line itinerary plus port call/berth schedule | None for automatic publication | `DIRECT` | Very high | Scope to vessel/voyage/date; unknown remains null |
| Nearby transport / safety POI | Transit/municipal/medical authority | Reviewed OSM extract | `DIRECT` | High | Secure-area access is not inferred |
| Straight-line distance | Canonical coordinate Statements | None | `CALCULATED` | Follows inputs | WGS84 geodesic; label straight-line |

## Genoa

| Entity / field | Preferred official source class | Fallback source class | Evidence method | Freshness sensitivity | Publication guardrail |
|---|---|---|---|---|---|
| Port identity / country | Port authority; official UN/LOCODE release | National gazetteer | `DIRECT` | Low; revalidate by release | Require artifact and locator |
| IANA timezone | IANA tzdb plus evidenced port coordinate | Reviewed authoritative gazetteer | `DIRECT` / `CALCULATED` | Medium at rule changes | Never copy fixed `UTC` placeholder |
| Port coordinate | Port-authority GIS/map | Human-reviewed OSM | `DIRECT` | Medium | Declare point semantics |
| Cruise terminal identity / coordinate | Passenger-terminal operator or port-authority GIS | Human-reviewed OSM | `DIRECT` | High | Do not conflate terminal, quay, or station |
| Route call / terminal assignment | Cruise-line itinerary plus port call/berth schedule | None for automatic publication | `DIRECT` | Very high | Scope to vessel/voyage/date; unknown remains null |
| Nearby transport / safety POI | Transit/municipal/medical authority | Reviewed OSM extract | `DIRECT` | High | Show provider and observation time |
| Straight-line distance | Canonical coordinate Statements | None | `CALCULATED` | Follows inputs | WGS84 geodesic; label straight-line |

## Naples

| Entity / field | Preferred official source class | Fallback source class | Evidence method | Freshness sensitivity | Publication guardrail |
|---|---|---|---|---|---|
| Port identity / country | Port authority; official UN/LOCODE release | National gazetteer | `DIRECT` | Low; revalidate by release | Require artifact and locator |
| IANA timezone | IANA tzdb plus evidenced port coordinate | Reviewed authoritative gazetteer | `DIRECT` / `CALCULATED` | Medium at rule changes | Never copy fixed `UTC` placeholder |
| Port coordinate | Port-authority GIS/map | Human-reviewed OSM | `DIRECT` | Medium | Declare point semantics |
| Cruise terminal identity / coordinate | Port authority or terminal operator | Human-reviewed OSM | `DIRECT` | High | Keep cruise terminal and ferry piers distinct |
| Route call / terminal assignment | Cruise-line itinerary plus port call/berth schedule | None for automatic publication | `DIRECT` | Very high | Scope to vessel/voyage/date; unknown remains null |
| Nearby transport / safety POI | Transit/municipal/medical authority | Reviewed OSM extract | `DIRECT` | High | Show provider and observation time |
| Straight-line distance | Canonical coordinate Statements | None | `CALCULATED` | Follows inputs | WGS84 geodesic; label straight-line |

## Valletta

| Entity / field | Preferred official source class | Fallback source class | Evidence method | Freshness sensitivity | Publication guardrail |
|---|---|---|---|---|---|
| Port identity / country | Maritime authority; official UN/LOCODE release | National gazetteer | `DIRECT` | Low; revalidate by release | Require artifact and locator |
| IANA timezone | IANA tzdb plus evidenced port coordinate | Reviewed authoritative gazetteer | `DIRECT` / `CALCULATED` | Medium at rule changes | Never copy fixed `UTC` placeholder |
| Port coordinate | Maritime-authority GIS/map | Human-reviewed OSM | `DIRECT` | Medium | Declare point semantics |
| Cruise terminal identity / coordinate | Maritime authority or cruise-terminal operator | Human-reviewed OSM | `DIRECT` | High | Keep terminal building, wharf, and spill-over quay distinct |
| Route call / terminal assignment | Cruise-line itinerary plus port call/berth schedule | None for automatic publication | `DIRECT` | Very high | Scope to vessel/voyage/date; unknown remains null |
| Nearby transport / safety POI | Transport/municipal/medical authority | Reviewed OSM extract | `DIRECT` | High | Show provider and observation time |
| Straight-line distance | Canonical coordinate Statements | None | `CALCULATED` | Follows inputs | WGS84 geodesic; label straight-line |
