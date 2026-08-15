# SPEC-001 - Cruise Knowledge Pack

## Metadata

- Title: Cruise Knowledge Pack
- Version: 1.0.0
- Status: Working Specification
- Classification: Normative Architecture
- Owner: Timonelo
- Canonical reference: MSC Bellissima pack version 2022.10.0

## 1. Purpose

The Cruise Knowledge Pack SHALL represent one versioned, evidence-bound structural account of one ship. It SHALL provide the canonical input for ship, deck, cabin, public-area, relationship, and factual-claim persistence.

The pack SHALL represent observable knowledge. It MUST NOT contain assessments, recommendations, rankings, predicted passenger impact, or presentation logic.

## 2. Version Boundary

A pack version SHALL be immutable. A changed fact, relationship, source interpretation, or limitation SHALL require a new pack version. Importing different content under an existing pack identifier and version MUST fail.

The effective date SHALL identify the configuration snapshot represented by the pack. A later source MUST NOT silently rewrite an earlier snapshot.

## 3. Domain Model

### 3.1 Source

A Source SHALL identify provenance material by stable ID, title, publisher, URL, access context, type, and explicit limitations.

### 3.2 Ship

A Ship SHALL be the identity root of one physical vessel. Ship-wide factual values MAY be present only when supported by cited Sources.

### 3.3 Deck

A Deck SHALL identify one structural level of the Ship by stable ID, number, name, and explicit order. Deck names and order SHALL remain scoped to the pack version.

### 3.4 Cabin Category

A Cabin Category SHALL preserve an operator-defined classification separately from individual Cabins. Category definitions MUST NOT imply that all assigned Cabins are structurally identical.

### 3.5 Cabin

A Cabin SHALL identify one numbered position on the Ship and one Deck. Category assignment and structural feature codes MAY remain unknown. Unknown assignments MUST NOT be inferred from nearby Cabins or from naming conventions alone.

### 3.6 Public Area

A Public Area SHALL identify one addressable guest-facing space. A Public Area MAY occupy more than one Deck. Its classification SHALL describe the space kind without asserting quality or passenger impact.

### 3.7 Relationship

A Relationship SHALL connect two known entities through a controlled structural predicate. Each Relationship SHALL state its evidence kind, cited Sources, and source locator. Derived Relationships SHALL additionally identify a deterministic derivation rule.

### 3.8 Claim

A Claim SHALL preserve one bounded factual statement about one entity. It SHALL contain a predicate, human-readable statement, machine-readable value, evidence kind, cited Sources, and source locator. A Claim is not an Assessment.

## 4. Validation

Before persistence, an importer SHALL verify:

- global identifier uniqueness;
- source and entity reference integrity;
- unique Deck numbers and ordering;
- Cabin-to-Deck consistency;
- Cabin Category applicability when a category is assigned;
- Public Area Deck membership;
- relationship endpoint integrity;
- provenance for every entity, Relationship, and Claim;
- a derivation rule for every deterministic derivation.

Validation failure SHALL prevent all persistence changes.

## 5. Import Contract

Canonical input SHALL be UTF-8 JSON using schema version `1.0`. The importer SHALL decode, validate, hash, and persist the complete pack in one transaction.

Re-importing semantically identical JSON SHALL be idempotent. Whitespace or object-key ordering SHALL NOT change the semantic content hash.

## 6. Persistence Contract

SQLite SHALL be the first persistence implementation. It SHALL be a reproducible projection of the canonical JSON, not an alternative authoring surface.

Persistence SHALL retain:

- immutable pack versions and semantic content hashes;
- a global entity registry;
- typed Ship, Deck, Cabin Category, Cabin, and Public Area projections;
- Public Area to Deck membership;
- generic provenance-bearing Relationships;
- provenance-bearing Claims;
- Source links for every material entity, Relationship, and Claim.

Foreign-key enforcement SHALL be enabled. Import MUST NOT update or delete an existing pack version.

## 7. MSC Bellissima Reference Boundary

Pack `knowledge-pack:msc-bellissima` version `2022.10.0` SHALL model the structural configuration documented by the official MSC Bellissima technical sheet marked October 2022.

The reference pack SHALL favor a small number of individually verifiable Cabins and Public Areas over unsupported bulk extraction. It SHALL record that ship configuration may vary by season or destination and requires verification at booking time.

Current MSC web material that differs from the 2022 technical sheet SHALL be retained as a Source limitation and MUST NOT silently alter the 2022 configuration snapshot.
