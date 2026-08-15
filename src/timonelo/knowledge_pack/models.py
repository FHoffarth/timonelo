"""Domain objects for one immutable cruise knowledge pack version."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class EvidenceKind(StrEnum):
    """How a material statement entered the knowledge layer."""

    SOURCE_ASSERTION = "source_assertion"
    DETERMINISTIC_DERIVATION = "deterministic_derivation"


class AccommodationType(StrEnum):
    INTERIOR = "interior"
    OCEAN_VIEW = "ocean_view"
    BALCONY = "balcony"
    SUITE = "suite"


class PublicAreaKind(StrEnum):
    DINING = "dining"
    ENTERTAINMENT = "entertainment"
    GUEST_SERVICE = "guest_service"
    LOUNGE = "lounge"
    PROMENADE = "promenade"
    RECREATION = "recreation"
    RETAIL = "retail"
    WELLNESS = "wellness"


class RelationshipKind(StrEnum):
    """Supported structural relationships; none imply passenger impact."""

    ABOVE = "above"
    ADJACENT_TO = "adjacent_to"
    BELOW = "below"
    CONNECTED_TO = "connected_to"
    CONTAINS = "contains"
    LOCATED_ON = "located_on"
    SPANS = "spans"


@dataclass(frozen=True, slots=True)
class Source:
    source_id: str
    title: str
    publisher: str
    url: str
    accessed_at: str
    source_type: str
    published_at: str | None = None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Ship:
    entity_id: str
    name: str
    operator_name: str
    source_ids: tuple[str, ...]
    source_locator: str
    cabin_count: int | None = None
    guest_capacity: int | None = None


@dataclass(frozen=True, slots=True)
class Deck:
    entity_id: str
    ship_id: str
    number: int
    name: str
    ordinal: int
    source_ids: tuple[str, ...]
    source_locator: str


@dataclass(frozen=True, slots=True)
class CabinCategory:
    entity_id: str
    code: str
    name: str
    accommodation_type: AccommodationType
    deck_numbers: tuple[int, ...]
    source_ids: tuple[str, ...]
    source_locator: str


@dataclass(frozen=True, slots=True)
class Cabin:
    entity_id: str
    ship_id: str
    deck_id: str
    number: str
    source_ids: tuple[str, ...]
    source_locator: str
    category_id: str | None = None
    feature_codes: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PublicArea:
    entity_id: str
    ship_id: str
    name: str
    kind: PublicAreaKind
    deck_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    source_locator: str
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Relationship:
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    kind: RelationshipKind
    evidence_kind: EvidenceKind
    source_ids: tuple[str, ...]
    source_locator: str
    derivation_rule: str | None = None
    limitation: str | None = None


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    subject_entity_id: str
    predicate: str
    statement: str
    value: JsonValue
    evidence_kind: EvidenceKind
    source_ids: tuple[str, ...]
    source_locator: str
    unit: str | None = None
    derivation_rule: str | None = None
    limitation: str | None = None


@dataclass(frozen=True, slots=True)
class KnowledgePack:
    schema_version: str
    pack_id: str
    version: str
    effective_date: str
    status: str
    limitations: tuple[str, ...]
    sources: tuple[Source, ...]
    ship: Ship
    decks: tuple[Deck, ...]
    cabin_categories: tuple[CabinCategory, ...]
    cabins: tuple[Cabin, ...]
    public_areas: tuple[PublicArea, ...]
    relationships: tuple[Relationship, ...]
    claims: tuple[Claim, ...]

    def entities(self) -> tuple[Ship | Deck | CabinCategory | Cabin | PublicArea, ...]:
        return (self.ship, *self.decks, *self.cabin_categories, *self.cabins, *self.public_areas)
