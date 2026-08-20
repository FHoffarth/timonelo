# Port & Route Geo Evidence-Safe Schema Proposal

Status: **DESIGN ONLY — NOT A PRODUCTION SCHEMA**

This proposal is governed by [ADR-GEO-001](../../adr/ADR-GEO-001.md). It does
not overwrite `knowledge/schema/port.schema.json` or
`knowledge/schema/route.schema.json`, authorize migration, or define persistence
technology.

## Common Semantics

- IDs are opaque, stable identifiers.
- All coordinates use WGS84 longitude/latitude and GeoJSON coordinate order
  `[longitude, latitude]`.
- A coordinate field on an evidence-backed entity is represented by a Statement
  reference, not an unproven numeric default.
- `null` means explicitly not established for this record.
- An omitted optional field means the producer did not supply the field.
- `[]` means confirmed empty only when evidence establishes emptiness. It MUST NOT be
  used as a substitute for unknown.
- Evidence links resolve to canonical Statement IDs or source/evidence records; they
  do not contain stored confidence.
- Temporal strings use RFC 3339 instants unless a field explicitly represents a date.
- Evidence, review, and publication states remain owned by canonical Statements.
- Entity existence does not itself authorize publication of every referenced claim.

## Port

Purpose: identify a canonical trade/transport port independently of a particular
terminal or berth.

| Field | Requirement | Semantics |
|---|---|---|
| `port_id` | required | Opaque Timonelo ID |
| `canonical_name` | required | Name carried by a supporting Statement |
| `country_code` | required | ISO country code carried by a supporting Statement |
| `timezone_id` | required | IANA timezone ID; fixed offsets are invalid |
| `un_locode` | optional, nullable | Code from an identified official release; null means not established |
| `un_locode_release` | required when `un_locode` is set | Version of the official UN/LOCODE release |
| `coordinate_statement_id` | required | Statement whose value defines the port reference point and its semantics |
| `evidence_statement_ids` | required, non-empty | Statements supporting identity fields |
| `valid_from` | optional | Applicability start |
| `valid_until` | optional | Applicability end |

Publication implications:

- The referenced coordinate Statement MUST explain whether the point represents a
  port centroid, authority reference point, entrance, or another defined location.
- UN/LOCODE MUST NOT be presented as a berth identifier.
- `timezone_id` MUST NOT be copied from a legacy `UTC` placeholder without evidence.

## CruiseTerminal

Purpose: identify a cruise passenger terminal independently of its port and berths.

| Field | Requirement | Semantics |
|---|---|---|
| `terminal_id` | required | Opaque Timonelo ID |
| `port_id` | required | Parent Port ID |
| `canonical_name` | required | Evidence-backed terminal name |
| `coordinate_statement_id` | optional, nullable | Terminal coordinate claim; null means not established |
| `operator_statement_id` | optional, nullable | Operator claim |
| `address_statement_id` | optional, nullable | Official address claim |
| `evidence_statement_ids` | required, non-empty | Statements supporting terminal identity |
| `valid_from` | optional | Applicability start |
| `valid_until` | optional | Applicability end |

Publication implications:

- A terminal coordinate MUST declare point semantics, such as passenger entrance or
  terminal building.
- Spatial proximity SHALL NOT establish a ship’s terminal assignment.
- Reverse-geocoded addresses are enrichment and SHALL NOT overwrite official address
  Statements.

## PortPOI

Purpose: preserve a bounded, attributed provider observation of a nearby transport or
safety-relevant point.

| Field | Requirement | Semantics |
|---|---|---|
| `poi_id` | required | Stable Timonelo ID |
| `port_id` | required | Port context |
| `poi_type` | required | Controlled design vocabulary; V1 limited to approved transport/safety types |
| `canonical_name` | required | Provider-observed or officially supported name |
| `coordinates` | required | WGS84 point observed from the provider |
| `provider` | required | Provider identity, for example OpenStreetMap |
| `provider_element_type` | required for OSM | Node, way, or relation |
| `provider_element_id` | required | Provider-native stable identifier |
| `provider_element_version` | optional, nullable | Null only when provider did not expose a version |
| `provider_element_timestamp` | optional, nullable | Provider object timestamp |
| `observed_at` | required | Time Timonelo observed provider state |
| `source_ref` | required | Source/evidence-event reference |
| `query_ref` | required for factory query output | Exact query or content-addressed query reference |
| `endpoint` | required for remote acquisition | Endpoint observed |
| `retrieved_at` | required | Retrieval time |

Publication implications:

- Publication describes observed provider state, not official operational truth.
- Missing nearby objects SHALL NOT be presented as confirmed absence unless the
  acquisition scope and evidence support completeness.
- POI freshness SHALL be visible when material to passenger use.

## PortConnection

Purpose: preserve a calculated relationship between two identified geo entities.

| Field | Requirement | Semantics |
|---|---|---|
| `connection_id` | required | Opaque Timonelo ID |
| `from_id` | required | Origin entity ID |
| `to_id` | required | Destination entity ID |
| `mode` | required | `GEODESIC` in V1; future modes require separate authorization |
| `distance_m` | optional, nullable | Calculated distance; null means not calculated |
| `duration_seconds` | optional, nullable | Deferred in V1 and therefore MUST be null or omitted |
| `route_geometry` | optional, nullable | Deferred routed geometry; not presentation geometry |
| `routing_provider` | optional, nullable | Required for a future routed connection |
| `routing_profile` | optional, nullable | Required for a future routed connection |
| `provider_data_version` | optional, nullable | Routing dataset version where exposed |
| `computed_at` | required | Computation time |
| `input_statement_ids` | required, non-empty | Complete input Statement closure |
| `rule_hash` | required | Content hash of the calculation rule |
| `derived` | required, constant `true` | Prevents representation as direct evidence |

Publication implications:

- V1 `distance_m` MUST be calculated geodesically on WGS84 and labelled
  “straight-line distance”.
- Longitude/latitude planar arithmetic is prohibited.
- No walking duration, accessibility implication, or navigable-path implication may
  be rendered from a V1 connection.

## CruiseRoute

Purpose: identify an evidence-backed itinerary topology without encoding sea legs or
display geometry.

| Field | Requirement | Semantics |
|---|---|---|
| `route_id` | required | Opaque Timonelo ID |
| `canonical_name` | required | Evidence-backed route label |
| `route_call_ids` | required, non-empty | Ordered RouteCall IDs |
| `evidence_statement_ids` | required, non-empty | Statements supporting the itinerary |
| `valid_from` | optional | Itinerary applicability start |
| `valid_until` | optional | Itinerary applicability end |

Publication implications:

- Call order is supported by itinerary evidence, not inferred from geometry.
- An empty call list is invalid; an unknown itinerary is represented by no publishable
  CruiseRoute.

## RouteCall

Purpose: represent one scheduled or published port call in itinerary order.

| Field | Requirement | Semantics |
|---|---|---|
| `route_call_id` | required | Opaque Timonelo ID |
| `route_id` | required | Parent CruiseRoute ID |
| `sequence` | required | Positive integer unique within route |
| `port_id` | required | Called Port ID |
| `terminal_id` | optional, nullable | Null means terminal assignment not established |
| `arrival_statement_id` | optional, nullable | Arrival claim |
| `departure_statement_id` | optional, nullable | Departure claim |
| `call_date_or_day_statement_id` | optional, nullable | Date or itinerary-day claim |
| `voyage_id` | optional, nullable | Voyage scope when established |
| `evidence_statement_ids` | required, non-empty | Statements supporting the call |
| `valid_from` | optional | Applicability start |
| `valid_until` | optional | Applicability end |

Publication implications:

- A call is not a sea leg.
- Unknown `terminal_id` MUST remain null. No port default, OSM proximity, or adjacent
  route call may populate it.

## RouteDisplayGeometry

Purpose: render itinerary context without asserting vessel movement.

| Field | Requirement | Semantics |
|---|---|---|
| `display_geometry_id` | required | Opaque Timonelo ID |
| `route_id` | required | Presented route |
| `geometry` | required | GeoJSON LineString or MultiLineString |
| `construction_method` | required | Named presentation algorithm |
| `input_route_call_ids` | required, non-empty | Ordered input calls |
| `rule_hash` | required | Content hash of generation rule |
| `generated_at` | required | Generation time |
| `presentation_only` | required, constant `true` | Mandatory semantic barrier |

Forbidden fields and semantics:

- `sailed_path`;
- real vessel distance;
- actual duration;
- observation status;
- movement evidence.

Publication implications:

- UI language SHALL identify this as itinerary visualization, not a sailed track.
- It SHALL NOT be accepted where `ActualTrackObservation` is required.

## ActualTrackObservation

Purpose: preserve time-bound observational vessel positions from a separately
authorized provider.

| Field | Requirement | Semantics |
|---|---|---|
| `track_observation_id` | required | Opaque Timonelo ID |
| `vessel_id` | required | Observed vessel |
| `voyage_id` | optional, nullable | Voyage association when established |
| `positions` | required, non-empty | Ordered timestamped WGS84 positions |
| `provider` | required | Observational source provider |
| `source_ref` | required | Evidence-event/source reference |
| `coverage_start` | required | First covered instant |
| `coverage_end` | required | Last covered instant |
| `coverage_gaps` | required | Explicit gap intervals; `[]` means completeness was assessed and no gaps found |
| `observed_at` | required | Acquisition observation time |
| `provider_data_version` | optional, nullable | Provider dataset/version marker |

Publication implications:

- Track positions are direct observations of provider data, not proof of the intended
  itinerary or complete physical path.
- Gaps MUST remain visible and MUST NOT be interpolated as observed movement.
- This object is outside V1 and cannot be synthesized from RouteDisplayGeometry.

## Legacy Migration / Quarantine Plan

1. Inventory each legacy field without modifying source records.
2. Resolve its exact source artifact and locator where one exists.
3. Assign a migration-only review label: `SUPPORTED`, `UNSUPPORTED`, `UNKNOWN`,
   `PLACEHOLDER-LIKE`, or `CONFLICTED`.
4. Create canonical Statements only for evidence-backed claims.
5. Build new objects solely from Statements that independently pass review and
   publication gates.
6. Preserve rejected or unresolved legacy values in quarantine; do not silently
   delete or promote them.
7. Reconstruct route topology as calls rather than mechanically translating legacy
   legs.

Mandatory quarantine candidates include fixed `UTC` values without timezone
evidence, repeated `500 m` / `10 min` values, generic source markers, and terminal
assignments or route topology without field-level provenance.

## Structural Invariants for Future Validation

1. `RouteDisplayGeometry.presentation_only` is always `true` and its schema has no
   movement-evidence fields.
2. OSM source references cannot satisfy a berth-assignment question by themselves.
3. `PortConnection.duration_seconds` is absent or null in V1.
4. Published V1 distance requires a WGS84 geodesic rule hash.
5. A legacy fixed timezone is never copied without a supporting Statement.
6. `RouteCall.terminal_id = null` remains a publishable explicit gap, not a trigger
   for default assignment.
7. Legacy route legs have no automatic conversion to RouteCall records.
