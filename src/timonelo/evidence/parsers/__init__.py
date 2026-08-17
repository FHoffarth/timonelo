"""Parser contract. Definitions only — no extraction is implemented."""

from timonelo.evidence.parsers.base import (
    DocumentParser, ExtractionCandidate, Modality, ParserRegistry, ParserResult,
)

__all__ = [
    "DocumentParser", "ExtractionCandidate", "Modality", "ParserRegistry",
    "ParserResult",
]
