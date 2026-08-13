"""Metadata-only access to the Timonelo Knowledge Repository."""

from .loader import KnowledgeLoader, load_knowledge
from .models import KnowledgeRecord, KnowledgeReference, SourceRecord, ValidationResult
from .registry import KnowledgeRegistry

__all__ = [
    "KnowledgeLoader",
    "KnowledgeRecord",
    "KnowledgeReference",
    "KnowledgeRegistry",
    "SourceRecord",
    "ValidationResult",
    "load_knowledge",
]
