"""Constitutional and referential validation for cruise knowledge packs."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse

from .models import EvidenceKind, KnowledgePack, RelationshipKind


ID_SEGMENT = r"[a-z0-9]+(?:-[a-z0-9]+)*"
ID_RE = re.compile(rf"{ID_SEGMENT}(?::{ID_SEGMENT})+")
VERSION_RE = re.compile(r"\d+\.\d+\.\d+")


@dataclass(frozen=True, order=True, slots=True)
class ValidationIssue:
    code: str
    path: str
    message: str


class PackValidationError(ValueError):
    """Raised when a pack cannot enter canonical persistence."""

    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        summary = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
        super().__init__(summary)


def validate_pack(pack: KnowledgePack) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    def add(code: str, path: str, message: str) -> None:
        issues.append(ValidationIssue(code, path, message))

    if pack.schema_version != "1.0":
        add("SCHEMA_VERSION", "schema_version", "only schema version 1.0 is supported")
    if not VERSION_RE.fullmatch(pack.version):
        add("VERSION", "version", "version must use MAJOR.MINOR.PATCH")
    try:
        date.fromisoformat(pack.effective_date)
    except ValueError:
        add("DATE", "effective_date", "effective date must use YYYY-MM-DD")

    sources = {source.source_id: source for source in pack.sources}
    entities = {entity.entity_id: entity for entity in pack.entities()}
    all_ids = [pack.pack_id, *(source.source_id for source in pack.sources)]
    all_ids.extend(entities)
    all_ids.extend(relationship.relationship_id for relationship in pack.relationships)
    all_ids.extend(claim.claim_id for claim in pack.claims)

    for identifier in all_ids:
        if not ID_RE.fullmatch(identifier):
            add("IDENTIFIER", identifier, "identifier must be lowercase colon-delimited kebab-case")
    duplicates = sorted(identifier for identifier, count in Counter(all_ids).items() if count > 1)
    for identifier in duplicates:
        add("DUPLICATE_ID", identifier, "identifier is not unique within the pack")

    for source in pack.sources:
        try:
            date.fromisoformat(source.accessed_at)
        except ValueError:
            add("SOURCE_DATE", source.source_id, "accessed_at must use YYYY-MM-DD")
        if source.published_at is not None:
            try:
                date.fromisoformat(source.published_at)
            except ValueError:
                add("SOURCE_DATE", source.source_id, "published_at must use YYYY-MM-DD")
        parsed_url = urlparse(source.url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            add("SOURCE_URL", source.source_id, "source URL must be an absolute HTTP(S) URL")

    if pack.ship.entity_id not in entities:
        add("SHIP", "ship", "ship entity is missing")
    if pack.ship.cabin_count is not None and pack.ship.cabin_count <= 0:
        add("SHIP_COUNT", "ship.cabin_count", "cabin count must be positive when known")
    if pack.ship.guest_capacity is not None and pack.ship.guest_capacity <= 0:
        add("SHIP_COUNT", "ship.guest_capacity", "guest capacity must be positive when known")
    deck_ids = {deck.entity_id for deck in pack.decks}
    deck_numbers = {deck.number for deck in pack.decks}
    category_ids = {category.entity_id for category in pack.cabin_categories}
    category_codes = {category.code for category in pack.cabin_categories}
    if len(deck_ids) != len(pack.decks) or len(deck_numbers) != len(pack.decks):
        add("DECK_UNIQUENESS", "decks", "deck IDs and numbers must be unique")
    if len({deck.ordinal for deck in pack.decks}) != len(pack.decks):
        add("DECK_ORDER", "decks", "deck ordinals must be unique")
    if len(category_ids) != len(pack.cabin_categories) or len(category_codes) != len(pack.cabin_categories):
        add("CATEGORY_UNIQUENESS", "cabin_categories", "category IDs and codes must be unique")

    def validate_sources(path: str, source_ids: tuple[str, ...]) -> None:
        if not source_ids:
            add("MISSING_PROVENANCE", path, "at least one source is required")
        if len(set(source_ids)) != len(source_ids):
            add("DUPLICATE_PROVENANCE", path, "source references must be unique")
        for source_id in source_ids:
            if source_id not in sources:
                add("UNKNOWN_SOURCE", path, f"source '{source_id}' does not exist")

    validate_sources("ship", pack.ship.source_ids)
    for deck in pack.decks:
        validate_sources(deck.entity_id, deck.source_ids)
        if deck.number <= 0 or deck.ordinal <= 0:
            add("DECK_VALUE", deck.entity_id, "deck number and ordinal must be positive")
        if deck.ship_id != pack.ship.entity_id:
            add("SHIP_REFERENCE", deck.entity_id, "deck must reference the pack ship")
    for category in pack.cabin_categories:
        validate_sources(category.entity_id, category.source_ids)
        if not category.deck_numbers:
            add("CATEGORY_DECK", category.entity_id, "category requires at least one documented deck")
        if len(set(category.deck_numbers)) != len(category.deck_numbers):
            add("CATEGORY_DECK", category.entity_id, "category deck numbers must be unique")
        unknown_decks = sorted(set(category.deck_numbers) - deck_numbers)
        if unknown_decks:
            add("CATEGORY_DECK", category.entity_id, f"unknown deck numbers: {unknown_decks}")
    seen_cabin_numbers: set[str] = set()
    for cabin in pack.cabins:
        validate_sources(cabin.entity_id, cabin.source_ids)
        if len(set(cabin.feature_codes)) != len(cabin.feature_codes):
            add("CABIN_FEATURE", cabin.entity_id, "feature codes must be unique")
        if cabin.ship_id != pack.ship.entity_id:
            add("SHIP_REFERENCE", cabin.entity_id, "cabin must reference the pack ship")
        if cabin.deck_id not in deck_ids:
            add("DECK_REFERENCE", cabin.entity_id, f"deck '{cabin.deck_id}' does not exist")
            continue
        if cabin.number in seen_cabin_numbers:
            add("CABIN_NUMBER", cabin.entity_id, f"duplicate cabin number '{cabin.number}'")
        seen_cabin_numbers.add(cabin.number)
        deck = next(deck for deck in pack.decks if deck.entity_id == cabin.deck_id)
        if not cabin.number.startswith(str(deck.number)):
            add("CABIN_DECK", cabin.entity_id, "cabin number is inconsistent with its deck")
        if cabin.category_id is not None:
            if cabin.category_id not in category_ids:
                add("CATEGORY_REFERENCE", cabin.entity_id, f"category '{cabin.category_id}' does not exist")
            else:
                category = next(item for item in pack.cabin_categories if item.entity_id == cabin.category_id)
                if deck.number not in category.deck_numbers:
                    add("CATEGORY_DECK", cabin.entity_id, "category is not documented for the cabin deck")
    for area in pack.public_areas:
        validate_sources(area.entity_id, area.source_ids)
        if len(set(area.deck_ids)) != len(area.deck_ids):
            add("DECK_REFERENCE", area.entity_id, "public area deck references must be unique")
        if area.ship_id != pack.ship.entity_id:
            add("SHIP_REFERENCE", area.entity_id, "public area must reference the pack ship")
        if not area.deck_ids:
            add("DECK_REFERENCE", area.entity_id, "public area requires at least one deck")
        for deck_id in area.deck_ids:
            if deck_id not in deck_ids:
                add("DECK_REFERENCE", area.entity_id, f"deck '{deck_id}' does not exist")

    relationship_ids: set[tuple[str, str, RelationshipKind]] = set()
    for relationship in pack.relationships:
        validate_sources(relationship.relationship_id, relationship.source_ids)
        if relationship.source_entity_id not in entities:
            add("ENTITY_REFERENCE", relationship.relationship_id, "source entity does not exist")
        if relationship.target_entity_id not in entities:
            add("ENTITY_REFERENCE", relationship.relationship_id, "target entity does not exist")
        if relationship.source_entity_id == relationship.target_entity_id:
            add("SELF_RELATIONSHIP", relationship.relationship_id, "relationship cannot reference one entity twice")
        signature = (relationship.source_entity_id, relationship.target_entity_id, relationship.kind)
        if signature in relationship_ids:
            add("DUPLICATE_RELATIONSHIP", relationship.relationship_id, "relationship is duplicated")
        relationship_ids.add(signature)
        if relationship.evidence_kind == EvidenceKind.DETERMINISTIC_DERIVATION and not relationship.derivation_rule:
            add("DERIVATION_RULE", relationship.relationship_id, "derived relationship requires a rule")
        if relationship.evidence_kind == EvidenceKind.SOURCE_ASSERTION and relationship.derivation_rule:
            add("DERIVATION_RULE", relationship.relationship_id, "source assertion must not declare a derivation rule")

    for claim in pack.claims:
        validate_sources(claim.claim_id, claim.source_ids)
        if claim.subject_entity_id not in entities:
            add("ENTITY_REFERENCE", claim.claim_id, "claim subject does not exist")
        if not claim.statement.strip() or not claim.predicate.strip():
            add("EMPTY_CLAIM", claim.claim_id, "claim statement and predicate are required")
        if claim.evidence_kind == EvidenceKind.DETERMINISTIC_DERIVATION and not claim.derivation_rule:
            add("DERIVATION_RULE", claim.claim_id, "derived claim requires a rule")
        if claim.evidence_kind == EvidenceKind.SOURCE_ASSERTION and claim.derivation_rule:
            add("DERIVATION_RULE", claim.claim_id, "source assertion must not declare a derivation rule")

    return tuple(sorted(set(issues)))


def require_valid_pack(pack: KnowledgePack) -> None:
    issues = validate_pack(pack)
    if issues:
        raise PackValidationError(issues)
