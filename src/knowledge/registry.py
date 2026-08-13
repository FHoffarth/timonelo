"""Resolved in-memory registry for Knowledge Repository metadata."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import KnowledgeRecord, SourceRecord, ValidationResult


@dataclass(frozen=True)
class KnowledgeRegistry:
    """Case-insensitive lookup registry returned by the loader."""

    records: dict[str, KnowledgeRecord] = field(default_factory=dict)
    sources: dict[str, SourceRecord] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    validation: ValidationResult = field(default_factory=ValidationResult)

    def resolve(self, knowledge_id: str) -> KnowledgeRecord | SourceRecord | None:
        key = knowledge_id.casefold()
        canonical = self.aliases.get(key, key)
        return self.records.get(canonical) or self.sources.get(canonical)

    def resolve_record(self, knowledge_id: str) -> KnowledgeRecord | None:
        resolved = self.resolve(knowledge_id)
        return resolved if isinstance(resolved, KnowledgeRecord) else None

    def resolve_source(self, source_id: str) -> SourceRecord | None:
        resolved = self.resolve(source_id)
        return resolved if isinstance(resolved, SourceRecord) else None
