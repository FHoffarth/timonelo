"""Structured exceptions raised by the Knowledge Loader."""

from __future__ import annotations


class KnowledgeLoaderError(Exception):
    """Base exception for loader failures unrelated to record validation."""


class KnowledgeRepositoryNotFoundError(KnowledgeLoaderError):
    """Raised when the configured knowledge repository does not exist."""


class KnowledgeDocumentError(KnowledgeLoaderError):
    """Raised when a Markdown document cannot be read safely."""
