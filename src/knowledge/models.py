"""Implementation-neutral metadata models for knowledge loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeReference:
    """A typed reference from one record to another record identifier."""

    target_id: str
    kind: str


@dataclass(frozen=True)
class KnowledgeRecord:
    """Metadata for one non-source Knowledge Repository record."""

    knowledge_id: str
    title: str
    category: str
    status: str
    folder: str
    path: Path
    aliases: tuple[str, ...] = ()
    related: tuple[KnowledgeReference, ...] = ()
    sources: tuple[KnowledgeReference, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict, compare=False, repr=False)


@dataclass(frozen=True)
class SourceRecord:
    """Metadata for one source record."""

    source_id: str
    title: str
    status: str
    folder: str
    path: Path
    aliases: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict, compare=False, repr=False)


@dataclass(frozen=True, order=True)
class ValidationIssue:
    """One structured validation finding."""

    code: str
    path: str
    message: str
    reference: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Complete validation outcome for one load operation."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def by_code(self, code: str) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.code == code)
