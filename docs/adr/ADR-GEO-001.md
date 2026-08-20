---
id: ADR-GEO-001
title: Port & Route Geo Architecture
status: DRAFT / READY FOR AUDIT
date: 2026-08-20
layer: Knowledge / Geometry / Presentation
applies_to: future port factory, route factory, geo enrichment, distance derivation, and map presentation
proposal: ../design/geo/SCHEMA-PROPOSAL.md
---

# ADR-GEO-001 — Port & Route Geo Architecture

## Context

Timonelo requires geospatial support for ports, cruise terminals, itinerary topology,
nearby transport, limited safety-relevant points of interest, and route presentation.
These uses produce different classes of information. Official operational facts,
third-party map observations, calculated distances, and decorative map geometry MUST
NOT be collapsed into a single claim class.

This ADR freezes architecture only. It does not authorize ingestion, migration,
runtime APIs, dependency installation, routing, geocoding, or AIS acquisition.

## Decision

Timonelo SHALL separate port and route geo information into four layers:

1. Evidence Facts;
2. Geo Enrichment;
3. Derived Routing;
4. Presentation Geometry.

A downstream layer SHALL NOT upgrade the authority of an upstream source.
Official berth assignment is not established by OSM proximity. Straight-line
distance is not a walking route. A display line is not an actual sailed path.
An unknown terminal assignment SHALL remain unknown.

Canonical claims SHALL continue to use the existing Statement and evidence-event
architecture. This ADR introduces no production evidence enum and no stored
confidence value.

## Four-Layer Model

### 1. Evidence Facts

Evidence Facts are provenance-bearing claims read from applicable sources. They
include port identity, terminal identity, official coordinates, and cruise itinerary
calls. Their authority is limited to the source, locator, time, and scope represented
by their evidence events.

### 2. Geo Enrichment

Geo Enrichment records what a geospatial provider reported at an observed time. It
may identify candidate transport nodes, POIs, or terminal geometry. It SHALL retain
provider identity and acquisition provenance. It SHALL NOT establish cruise-line or
port-operational truth merely because an object is spatially near another object.

### 3. Derived Routing

Derived Routing contains calculated distance, duration, or path results. Every result
SHALL identify its input statements, rule, provider where applicable, profile, data
version where available, and computation time. Derived results SHALL NOT be stored as
direct observations.

V1 includes geodesic straight-line distance only. Road-network routes and durations
are deferred.

### 4. Presentation Geometry

Presentation Geometry exists only to render context. It SHALL be structurally
separate from itinerary topology and observational tracks. It MUST NOT carry actual
distance, actual duration, sailed-path, or observed-movement semantics.

## Global Geo

Natural Earth SHALL be used only for global or regional cartographic context,
including coastlines, national boundaries, global port dots, itinerary overview
context, and static fallback context.

Natural Earth SHALL NOT be authority for cruise terminals, berths, pedestrian
infrastructure, POIs, routing truth, or actual vessel tracks.

## Port Geo Enrichment

OpenStreetMap SHALL be treated as attributed geospatial enrichment. It SHALL NOT
establish berth assignment, cruise-terminal assignment, or cruise-line itinerary
truth.

Overpass acquisition SHALL occur only in an offline or factory workflow. Runtime
Overpass queries are prohibited in V1.

Each retained OSM observation SHALL include, where supplied:

- element type;
- element ID;
- element version;
- element timestamp;
- exact query;
- endpoint;
- retrieval time.

General geocoding is deferred from V1. Public Nominatim SHALL NOT be production
infrastructure. Terminal coordinate sources SHALL be prioritized as follows:

1. official port-authority GIS, map, or coordinate publication;
2. human-reviewed OSM fallback;
3. curator-assisted geocoding for discovery only.

Reverse geocoding SHALL NOT overwrite an official address.

## Geometry / Distance

The preferred future tools are:

- Shapely for geometry validation and processing;
- `pyproj.Geod` for canonical WGS84 geodesic calculations;
- TurfJS for presentation-only browser geometry.

This preference does not authorize dependency installation.

Published distance MUST NOT be calculated by treating longitude and latitude as
planar coordinates. A V1 distance SHALL be a WGS84 geodesic calculation, SHALL be
labelled as straight-line distance, and SHALL retain input Statement IDs and a rule
hash.

V1 SHALL NOT publish walking duration, road-network duration, or a generic walking
estimate.

## Map Renderer

MapLibre GL JS is the preferred renderer for future implementation because it
supports vector tiles, GeoJSON layers, maritime styling, and a future cached or
self-hosted tile path without raster-first lock-in.

Every implementation SHALL provide:

- a semantic text equivalent for map meaning;
- keyboard-operable controls outside the map canvas;
- no color-only meaning;
- reduced-motion support;
- bounded mobile feature and label density.

Renderer preference does not make the map a canonical evidence surface.

## Tile Strategy

V1 SHALL use a commercial vector-tile provider selected through a separate review.
The provider SHALL permit commercial use, support MapLibre, publish explicit caching
terms, support correct attribution, provide a production SLA, and permit configuration
through a replaceable provider abstraction. Cost controls and privacy, including EU
delivery considerations, SHALL be evaluated before selection.

Public OpenStreetMap tile servers SHALL NOT be used as production infrastructure.
OpenMapTiles self-hosting is a later migration option. Raster tiles or static maps MAY
be used only as an approved fallback.

## Routing Boundary

Routing is deferred from V1. GraphHopper is the preferred first future evaluation;
OSRM remains an alternative. No routing-engine selection becomes final until walking
and driving benchmark routes across Barcelona, Marseille, Genoa, Naples, and Valletta
have been manually validated.

Generic routing output SHALL NOT establish an accessibility claim. Turn-by-turn
shipboard routing is outside this ADR.

## Port Factory Model

The design-only model SHALL contain:

- `Port`;
- `CruiseTerminal`;
- `PortPOI`;
- `PortConnection`.

Port and terminal coordinates are separate claims. UN/LOCODE is optional, SHALL cite
a versioned official release, and identifies a trade or transport location rather
than a cruise berth. Timezones SHALL use IANA timezone IDs rather than fixed UTC
offsets.

`PortConnection` is always derived. Absence of a duration SHALL remain explicit; a
generic walking time MUST NOT be substituted.

The normative design fields and null semantics are specified in the linked schema
proposal. Existing production schemas are not changed by this decision.

## Route Factory Model

The design-only model SHALL contain:

- `CruiseRoute`;
- `RouteCall`;
- `RouteDisplayGeometry`;
- `ActualTrackObservation`.

`CruiseRoute` and `RouteCall` represent itinerary topology. A call is not a sea leg.
`RouteDisplayGeometry` represents presentation only. `ActualTrackObservation`
represents time-bound observational track evidence and SHALL preserve coverage gaps.

Route-call order SHALL NOT be inferred from display geometry. Actual movement SHALL
NOT be inferred from itinerary topology or presentation geometry.

## Trust Mapping

The following mappings are conceptual and introduce no new production enums:

| Information | Method | Derivation | Required closure |
|---|---|---|---|
| Official port or cruise fact | `DIRECT` | `LOCAL` | Evidence event and applicable artifact locator |
| OSM state observation | `DIRECT` | `LOCAL` | Provider observation metadata and source reference |
| Geodesic distance | `CALCULATED` | inherited from inputs | Input Statement IDs and rule hash |
| Future routed result | `CALCULATED` | inherited from inputs | Provider, profile, version, inputs, and rule hash |
| Presentation geometry | `CALCULATED` | `GENERATED` | Generation inputs; no movement semantics |
| Observed vessel track | `DIRECT` | `LOCAL` | Provider, observation times, positions, and explicit gaps |

`EvidenceCondition`, `HumanReviewState`, and `PublishStatus` remain independent.
Confidence SHALL be computed through the evidence derivation graph and SHALL NOT be
stored on these objects.

## Legacy Data Quarantine

Existing port and route records SHALL NOT be automatically promoted into the new
model. Migration SHALL classify each legacy field as one of the following review
labels without creating a new production evidence enum:

- `SUPPORTED`;
- `UNSUPPORTED`;
- `UNKNOWN`;
- `PLACEHOLDER-LIKE`;
- `CONFLICTED`.

These are migration-workflow labels only. Canonical UNKNOWN remains the absence of a
satisfying published Statement, not a stored truth value.

Fixed `UTC` values, repeated `500 m` / `10 min` values, generic source markers, and
the current call/leg representation SHALL be quarantined until field-level evidence
establishes them. Migration SHALL create new evidence-backed objects; it SHALL NOT
copy legacy values merely because they are syntactically valid.

An unknown terminal assignment SHALL remain a null reference and SHALL NOT be filled
from proximity, route order, or a port default.

## Offline / Mobile

Future presentation SHALL support three explicit states:

1. `FULL ONLINE`;
2. `CACHED MAP`;
3. `TEXT FALLBACK`.

Text fallback SHALL independently communicate the port, terminal when established,
nearby transport, distances where available, source, freshness, and limitations. Core
meaning SHALL NOT require map availability.

Cached presentation SHALL expose cache age and SHALL NOT imply current operational
status. Full offline navigation is deferred.

## V1 Scope

V1 includes:

- evidence-backed port identity;
- IANA timezone;
- versioned UN/LOCODE where supported;
- port and terminal coordinates;
- itinerary topology;
- presentation route geometry;
- curated transport nodes;
- limited safety-relevant POIs;
- labelled geodesic straight-line distance;
- source and freshness visibility;
- online, cached-map, and text-fallback states.

V1 excludes:

- walking duration and road-network routing;
- live transit, live traffic, and crowding;
- real-time berth claims;
- inferred accessibility routing;
- turn-by-turn navigation;
- AIS playback;
- public-runtime geocoding;
- runtime Overpass;
- broad tourism POI ingestion.

## Risks

- Official maps may identify a terminal area without identifying the passenger
  entrance, berth, or coordinate semantics.
- OSM completeness and tagging vary by port and time.
- Secure port boundaries may make a geometrically plausible pedestrian connection
  operationally invalid.
- Tile-provider licence, caching, privacy, and attribution terms may constrain
  offline behavior.
- Display geometry may be mistaken for observed movement unless schema and language
  constraints are enforced.
- Legacy records may appear authoritative despite insufficient field-level evidence.

## Deferred Work

- Production schema migration and legacy-field adjudication;
- official-source acquisition for the first five ports;
- dependency and renderer implementation;
- tile-provider selection;
- Overpass query implementation and caching;
- geocoder selection or self-hosting;
- GraphHopper and OSRM benchmark evaluation;
- GTFS, live transit, traffic, and disruption feeds;
- accessibility-routing research;
- AIS acquisition, licensing, and gap semantics;
- full offline navigation.
