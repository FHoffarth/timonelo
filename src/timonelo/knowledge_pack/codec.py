"""Strict JSON decoding for canonical cruise knowledge packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from .models import (
    AccommodationType,
    Cabin,
    CabinCategory,
    Claim,
    Deck,
    EvidenceKind,
    KnowledgePack,
    PublicArea,
    PublicAreaKind,
    Relationship,
    RelationshipKind,
    Ship,
    Source,
)
from .validation import require_valid_pack


class KnowledgePackFormatError(ValueError):
    """Raised when JSON cannot be decoded into the pack domain model."""


EnumT = TypeVar("EnumT")


def _string(data: dict[str, Any], key: str, path: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise KnowledgePackFormatError(f"{path}.{key} must be a non-empty string")
    return value


def _optional_string(data: dict[str, Any], key: str, path: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise KnowledgePackFormatError(f"{path}.{key} must be null or a non-empty string")
    return value


def _integer(data: dict[str, Any], key: str, path: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise KnowledgePackFormatError(f"{path}.{key} must be an integer")
    return value


def _optional_integer(data: dict[str, Any], key: str, path: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise KnowledgePackFormatError(f"{path}.{key} must be null or an integer")
    return value


def _strings(data: dict[str, Any], key: str, path: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise KnowledgePackFormatError(f"{path}.{key} must be an array of non-empty strings")
    return tuple(value)


def _integers(data: dict[str, Any], key: str, path: str) -> tuple[int, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise KnowledgePackFormatError(f"{path}.{key} must be an array of integers")
    return tuple(value)


def _enum(enum_type: type[EnumT], data: dict[str, Any], key: str, path: str) -> EnumT:
    value = _string(data, key, path)
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)  # type: ignore[attr-defined]
        raise KnowledgePackFormatError(f"{path}.{key} must be one of: {allowed}") from exc


def _objects(document: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise KnowledgePackFormatError(f"{key} must be an array of objects")
    return value


def decode_pack(document: object) -> KnowledgePack:
    if not isinstance(document, dict):
        raise KnowledgePackFormatError("knowledge pack root must be an object")

    sources = tuple(
        Source(
            source_id=_string(item, "source_id", path),
            title=_string(item, "title", path),
            publisher=_string(item, "publisher", path),
            url=_string(item, "url", path),
            accessed_at=_string(item, "accessed_at", path),
            source_type=_string(item, "source_type", path),
            published_at=_optional_string(item, "published_at", path),
            limitations=_strings(item, "limitations", path),
        )
        for index, item in enumerate(_objects(document, "sources"))
        for path in (f"sources[{index}]",)
    )
    ship_data = document.get("ship")
    if not isinstance(ship_data, dict):
        raise KnowledgePackFormatError("ship must be an object")
    ship = Ship(
        entity_id=_string(ship_data, "entity_id", "ship"),
        name=_string(ship_data, "name", "ship"),
        operator_name=_string(ship_data, "operator_name", "ship"),
        source_ids=_strings(ship_data, "source_ids", "ship"),
        source_locator=_string(ship_data, "source_locator", "ship"),
        cabin_count=_optional_integer(ship_data, "cabin_count", "ship"),
        guest_capacity=_optional_integer(ship_data, "guest_capacity", "ship"),
    )
    decks = tuple(
        Deck(
            entity_id=_string(item, "entity_id", path),
            ship_id=_string(item, "ship_id", path),
            number=_integer(item, "number", path),
            name=_string(item, "name", path),
            ordinal=_integer(item, "ordinal", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
        )
        for index, item in enumerate(_objects(document, "decks"))
        for path in (f"decks[{index}]",)
    )
    categories = tuple(
        CabinCategory(
            entity_id=_string(item, "entity_id", path),
            code=_string(item, "code", path),
            name=_string(item, "name", path),
            accommodation_type=_enum(AccommodationType, item, "accommodation_type", path),
            deck_numbers=_integers(item, "deck_numbers", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
        )
        for index, item in enumerate(_objects(document, "cabin_categories"))
        for path in (f"cabin_categories[{index}]",)
    )
    cabins = tuple(
        Cabin(
            entity_id=_string(item, "entity_id", path),
            ship_id=_string(item, "ship_id", path),
            deck_id=_string(item, "deck_id", path),
            number=_string(item, "number", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
            category_id=_optional_string(item, "category_id", path),
            feature_codes=_strings(item, "feature_codes", path),
            limitations=_strings(item, "limitations", path),
        )
        for index, item in enumerate(_objects(document, "cabins"))
        for path in (f"cabins[{index}]",)
    )
    public_areas = tuple(
        PublicArea(
            entity_id=_string(item, "entity_id", path),
            ship_id=_string(item, "ship_id", path),
            name=_string(item, "name", path),
            kind=_enum(PublicAreaKind, item, "kind", path),
            deck_ids=_strings(item, "deck_ids", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
            limitations=_strings(item, "limitations", path),
        )
        for index, item in enumerate(_objects(document, "public_areas"))
        for path in (f"public_areas[{index}]",)
    )
    relationships = tuple(
        Relationship(
            relationship_id=_string(item, "relationship_id", path),
            source_entity_id=_string(item, "source_entity_id", path),
            target_entity_id=_string(item, "target_entity_id", path),
            kind=_enum(RelationshipKind, item, "kind", path),
            evidence_kind=_enum(EvidenceKind, item, "evidence_kind", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
            derivation_rule=_optional_string(item, "derivation_rule", path),
            limitation=_optional_string(item, "limitation", path),
        )
        for index, item in enumerate(_objects(document, "relationships"))
        for path in (f"relationships[{index}]",)
    )
    claims = tuple(
        Claim(
            claim_id=_string(item, "claim_id", path),
            subject_entity_id=_string(item, "subject_entity_id", path),
            predicate=_string(item, "predicate", path),
            statement=_string(item, "statement", path),
            value=item.get("value"),
            evidence_kind=_enum(EvidenceKind, item, "evidence_kind", path),
            source_ids=_strings(item, "source_ids", path),
            source_locator=_string(item, "source_locator", path),
            unit=_optional_string(item, "unit", path),
            derivation_rule=_optional_string(item, "derivation_rule", path),
            limitation=_optional_string(item, "limitation", path),
        )
        for index, item in enumerate(_objects(document, "claims"))
        for path in (f"claims[{index}]",)
    )
    pack = KnowledgePack(
        schema_version=_string(document, "schema_version", "pack"),
        pack_id=_string(document, "pack_id", "pack"),
        version=_string(document, "version", "pack"),
        effective_date=_string(document, "effective_date", "pack"),
        status=_string(document, "status", "pack"),
        limitations=_strings(document, "limitations", "pack"),
        sources=sources,
        ship=ship,
        decks=decks,
        cabin_categories=categories,
        cabins=cabins,
        public_areas=public_areas,
        relationships=relationships,
        claims=claims,
    )
    require_valid_pack(pack)
    return pack


def load_pack(path: Path | str) -> KnowledgePack:
    source_path = Path(path)
    try:
        document = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgePackFormatError(f"cannot read {source_path}: {exc}") from exc
    return decode_pack(document)


def canonical_json_bytes(path: Path | str) -> bytes:
    """Return semantic canonical JSON bytes for stable import hashing."""

    source_path = Path(path)
    try:
        document = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgePackFormatError(f"cannot read {source_path}: {exc}") from exc
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
