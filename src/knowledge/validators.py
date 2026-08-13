"""Metadata validation and reference resolution for Knowledge Records."""

from __future__ import annotations

from collections import Counter

from .models import KnowledgeRecord, SourceRecord, ValidationIssue, ValidationResult


ALLOWED_RECORD_FOLDERS = {
    "cruise-lines", "ship-classes", "ships", "cabin-types",
    "structural-features", "ship-systems", "operations", "regulations",
    "glossary",
}


def validate_records(
    records: list[KnowledgeRecord],
    sources: list[SourceRecord],
    initial: list[ValidationIssue] | None = None,
) -> ValidationResult:
    """Validate identity, placement, aliases, and metadata references."""

    issues = list(initial or [])
    all_items: list[KnowledgeRecord | SourceRecord] = [*records, *sources]
    identities = [
        item.knowledge_id if isinstance(item, KnowledgeRecord) else item.source_id
        for item in all_items
    ]
    counts = Counter(identity.casefold() for identity in identities)
    known_records = {record.knowledge_id.casefold() for record in records}
    known_sources = {source.source_id.casefold() for source in sources}

    for item, identity in zip(all_items, identities, strict=True):
        relative = item.path.as_posix()
        if counts[identity.casefold()] > 1:
            issues.append(ValidationIssue("DUPLICATE_ID", relative, f"duplicate ID '{identity}'", identity))
        if isinstance(item, SourceRecord):
            if item.folder != "sources":
                issues.append(ValidationIssue("INVALID_FILE_PLACEMENT", relative, "source record must be in sources/"))
        elif item.folder not in ALLOWED_RECORD_FOLDERS:
            issues.append(ValidationIssue("INVALID_FILE_PLACEMENT", relative, f"record folder '{item.folder}' is not allowed"))

    alias_owners: dict[str, set[str]] = {}
    for item, identity in zip(all_items, identities, strict=True):
        for alias in item.aliases:
            alias_owners.setdefault(alias.casefold(), set()).add(identity.casefold())
    canonical_ids = {identity.casefold() for identity in identities}
    for alias, owners in sorted(alias_owners.items()):
        if len(owners) > 1 or (alias in canonical_ids and alias not in owners):
            for owner in sorted(owners):
                issues.append(ValidationIssue("DUPLICATE_ALIAS", ".", f"alias '{alias}' is ambiguous", owner))

    for record in records:
        for reference in record.related:
            if reference.target_id.casefold() not in known_records:
                issues.append(ValidationIssue(
                    "MISSING_RELATED_RECORD", record.path.as_posix(),
                    f"related record '{reference.target_id}' does not exist", reference.target_id,
                ))
        for reference in record.sources:
            if reference.target_id.casefold() not in known_sources:
                issues.append(ValidationIssue(
                    "MISSING_SOURCE_RECORD", record.path.as_posix(),
                    f"source record '{reference.target_id}' does not exist", reference.target_id,
                ))
    return ValidationResult(tuple(sorted(set(issues))))
