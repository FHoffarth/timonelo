# Architecture

Timonelo is planned as a small set of modules with explicit responsibilities. The boundaries exist to keep source evidence, deterministic calculation, editorial presentation, and web delivery separate.

## Core principle

**Timonelo must never sound more certain than its evidence.**

The architecture must preserve provenance and limitations from ingestion through publication. Presentation layers may simplify language, but may not strengthen a claim beyond the evidence supplied by the underlying module.

## Spatial Evidence Engine

The Spatial Evidence Engine derives reproducible relationships and exposure indicators from configured ship geometry. It owns deterministic spatial algorithms, their versioned rules, and their evidence output. It does not write customer-facing recommendations and does not depend on passenger reviews.

## Ship Knowledge Graph

The Ship Knowledge Graph is the canonical structural representation of a ship. It holds cabins, decks, public areas, connections, coordinates, relationships, and source provenance. It provides stable identifiers and validated graph contracts to downstream modules.

## Cabin Briefing Generator

The Cabin Briefing Generator assembles the evidence available for one cabin into a consistent briefing structure. It preserves evidence type, provenance, confidence boundaries, and known limitations. It does not derive new spatial facts and does not conceal missing evidence.

## Web Platform

The Web Platform publishes Cabin Briefings and their supporting evidence. It owns navigation, retrieval, and presentation. It does not calculate spatial evidence or alter the meaning of briefing claims.

## Dependency direction

```text
Verified source material
          ↓
Ship Knowledge Graph
          ↓
Spatial Evidence Engine
          ↓
Cabin Briefing Generator
          ↓
Web Platform
```

Data and evidence move forward through this sequence. Product presentation must not feed unverified conclusions back into the graph or evidence layers.

## Architectural boundaries

- Ship-specific configuration belongs with ship data, not algorithm code.
- Derived artifacts must be reproducible from versioned inputs and rules.
- Source facts and derived evidence must remain distinguishable.
- Missing or unsupported evidence must remain explicit.
- Module interfaces should remain stable before infrastructure is added around them.

No database, frontend framework, container layer, or deployment architecture is selected at this stage.

