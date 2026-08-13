"""Metadata-only loader for the canonical Timonelo Knowledge Repository."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .exceptions import KnowledgeDocumentError, KnowledgeRepositoryNotFoundError
from .models import KnowledgeRecord, KnowledgeReference, SourceRecord, ValidationIssue
from .registry import KnowledgeRegistry
from .validators import validate_records


FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")
ID_FIELDS = ("ID", "Entity ID", "Term ID")
TITLE_FIELDS = ("Canonical name", "Canonical term", "Title")
SKIPPED_FILES = {"README.md", "CONTRIBUTING.md", "INDEX.md", "GRAPH.md"}
SKIPPED_FOLDERS = {"templates", "images"}
SOURCE_REQUIRED = (
    "Source ID", "Title", "Publisher", "URL", "Published date",
    "Accessed date", "Source type", "Review status",
)
ENTITY_REQUIRED = ("Entity ID", "Canonical name", "Entity type", "Status", "Last reviewed")
GLOSSARY_REQUIRED = ("Term ID", "Canonical term", "Status", "Last reviewed")
KNOWLEDGE_REQUIRED = ("ID", "Canonical name", "Record type", "Status", "Last reviewed")


def values(raw: str) -> tuple[str, ...]:
    """Split a comma-separated metadata value without interpreting content."""

    return tuple(dict.fromkeys(value.strip() for value in raw.split(",") if value.strip()))


def metadata_from(path: Path) -> dict[str, str]:
    """Read only the named Metadata section of a Markdown document."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise KnowledgeDocumentError(f"cannot read {path}: {exc}") from exc
    metadata: dict[str, str] = {}
    active = False
    for line in lines:
        if line.startswith("## "):
            active = line[3:].strip() == "Metadata"
            continue
        if active and (match := FIELD_RE.match(line)):
            metadata[match.group(1).strip()] = match.group(2).strip()
    return metadata


def first(metadata: dict[str, str], fields: tuple[str, ...]) -> str:
    return next((metadata[field] for field in fields if metadata.get(field)), "")


class KnowledgeLoader:
    """Discover records and return a registry plus structured validation."""

    def __init__(self, knowledge_root: Path | str) -> None:
        self.knowledge_root = Path(knowledge_root)

    def load(self) -> KnowledgeRegistry:
        if not self.knowledge_root.is_dir():
            raise KnowledgeRepositoryNotFoundError(f"knowledge directory does not exist: {self.knowledge_root}")
        records: list[KnowledgeRecord] = []
        sources: list[SourceRecord] = []
        initial: list[ValidationIssue] = []

        for path in sorted(self.knowledge_root.rglob("*.md")):
            relative = path.relative_to(self.knowledge_root)
            if path.name in SKIPPED_FILES or relative.parts[0] in SKIPPED_FOLDERS:
                continue
            metadata = metadata_from(path)
            folder = relative.parent.as_posix()
            if "Source ID" in metadata:
                for name in SOURCE_REQUIRED:
                    if not metadata.get(name):
                        initial.append(ValidationIssue("MISSING_METADATA", relative.as_posix(), f"missing '{name}'"))
                sources.append(SourceRecord(
                    metadata.get("Source ID", ""), metadata.get("Title", ""), metadata.get("Review status", ""),
                    folder, relative, values(metadata.get("Aliases", "")), dict(metadata),
                ))
                continue

            knowledge_id = first(metadata, ID_FIELDS)
            title = first(metadata, TITLE_FIELDS)
            category = metadata.get("Entity type") or metadata.get("Record type") or ("Glossary" if metadata.get("Term ID") else "")
            required_fields = ENTITY_REQUIRED if "Entity ID" in metadata else GLOSSARY_REQUIRED if "Term ID" in metadata else KNOWLEDGE_REQUIRED
            for name in required_fields:
                if not metadata.get(name):
                    initial.append(ValidationIssue("MISSING_METADATA", relative.as_posix(), f"missing '{name}'"))
            records.append(KnowledgeRecord(
                knowledge_id, title, category, metadata.get("Status", ""), folder, relative,
                values(metadata.get("Aliases", "")),
                tuple(KnowledgeReference(value, "related") for value in values(metadata.get("Related IDs", ""))),
                tuple(KnowledgeReference(value, "source") for value in values(metadata.get("Source IDs", ""))),
                dict(metadata),
            ))

        validation = validate_records(records, sources, initial)
        identities = [record.knowledge_id.casefold() for record in records if record.knowledge_id]
        identities.extend(source.source_id.casefold() for source in sources if source.source_id)
        identity_counts = Counter(identities)
        record_map = {
            record.knowledge_id.casefold(): record for record in records
            if record.knowledge_id and identity_counts[record.knowledge_id.casefold()] == 1
        }
        source_map = {
            source.source_id.casefold(): source for source in sources
            if source.source_id and identity_counts[source.source_id.casefold()] == 1
        }
        alias_owners: dict[str, set[str]] = {}
        for item in [*records, *sources]:
            identity = item.knowledge_id if isinstance(item, KnowledgeRecord) else item.source_id
            for alias in item.aliases:
                alias_owners.setdefault(alias.casefold(), set()).add(identity.casefold())
        aliases: dict[str, str] = {}
        for item in [*records, *sources]:
            identity = item.knowledge_id if isinstance(item, KnowledgeRecord) else item.source_id
            for alias in item.aliases:
                key = alias.casefold()
                if len(alias_owners[key]) == 1 and key not in identity_counts and identity_counts[identity.casefold()] == 1:
                    aliases[key] = identity.casefold()
        return KnowledgeRegistry(record_map, source_map, aliases, validation)


def load_knowledge(knowledge_root: Path | str) -> KnowledgeRegistry:
    """Convenience entrypoint for loading one Knowledge Repository."""

    return KnowledgeLoader(knowledge_root).load()
