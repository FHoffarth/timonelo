"""
Parser contract.

Governed by ADR-0002 §1, §5.

DEFINITION ONLY. No extraction is implemented, and none should be until one
document has been curated by hand — an interface designed before a single real
extraction will encode assumptions about a document nobody has read.

THE ONE INVARIANT THAT MATTERS

A parser produces CANDIDATES, never Statements.

    Artifact -> Parser -> ExtractionCandidate -> human -> StatementEditor
                                                          -> Statement -> Review

A candidate is a proposal: "on page 12, at this locator, I read the value X."
It carries no authority and cannot answer a passenger's question. Only a human
promotes it, through the Statement Editor, which is still the sole creator of
Statements.

This is not ceremony. An importer that could also make claims is how
synthesized cabins came to carry evidence links in the old engine; a parser
that could write Statements would reintroduce the same defect with better
tooling behind it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


class Modality(str, Enum):
    """How a parser reads bytes. NOT a hierarchy — these are alternatives.

    A raster parser is not a specialisation of a vector parser; they read
    different things and fail differently. Modelling them as a subclass chain
    would force shared behaviour that does not exist.
    """
    VECTOR_TEXT = "VECTOR_TEXT"       # embedded text objects
    VECTOR_GRAPHICS = "VECTOR_GRAPHICS"  # paths, lines, fills
    RASTER = "RASTER"                 # rendered pixels
    OCR = "OCR"                       # pixels -> characters
    VISION = "VISION"                 # pixels -> structures


@dataclass(frozen=True)
class ExtractionCandidate:
    """A proposal for a Statement. Not evidence. Not an answer.

    Every field a human needs to check the proposal against the document is
    mandatory: without page and locator a candidate cannot be verified, and an
    unverifiable proposal is worse than no proposal.
    """
    artifact_id: str
    statement_type: str
    value: Any
    page: Optional[int]
    locator: str
    modality: Modality
    parser_id: str
    parser_version: str
    # Parser self-report only. NOT confidence in the truth of the value, and
    # never propagated into the Truth Engine's confidence computation.
    extraction_score: Optional[float] = None
    entity_id: Optional[str] = None
    raw_context: str = ""

    def __post_init__(self) -> None:
        if not self.locator:
            raise ValueError(
                "An ExtractionCandidate requires a locator. A human must be "
                "able to find the same place in the document."
            )
        if not self.parser_id or not self.parser_version:
            raise ValueError(
                "A candidate must name the parser and version that produced "
                "it, so a later extraction bug can be traced to its output."
            )

    @property
    def requires_human_confirmation(self) -> bool:
        """Always True. There is no automatic promotion path."""
        return True


@dataclass(frozen=True)
class ParserResult:
    """What a parse run returns. Candidates plus what went wrong."""
    artifact_id: str
    parser_id: str
    parser_version: str
    candidates: Sequence[ExtractionCandidate] = ()
    pages_read: int = 0
    warnings: Sequence[str] = ()
    # Regions the parser could not interpret. Reporting these matters more than
    # the candidates: silence about a region a human would have read is how a
    # gap becomes invisible (ADR-0002 §8).
    unreadable_regions: Sequence[str] = ()


class DocumentParser(ABC):
    """Base contract. Subclass per modality, not per document.

    Implementations are expected AFTER the first manual curation, when the
    shape of a real deck plan is known. Anything written before then is a guess
    about a document nobody has read.
    """

    parser_id: str = ""
    parser_version: str = ""
    modality: Modality

    @abstractmethod
    def can_read(self, path: str) -> bool:
        """Whether this parser can process the file at all.

        Cheap check on the bytes. Must not raise for unsupported files: an
        orchestrator asks several parsers before choosing one.
        """

    @abstractmethod
    def supported_statement_types(self) -> List[str]:
        """Statement types this parser could propose candidates for.

        Must be a subset of what the artifact's document class has authority
        over. A parser cannot widen the Statement Authority Matrix: reading a
        number off a deck plan does not make the deck plan authoritative for
        areas.
        """

    @abstractmethod
    def parse(self, path: str, artifact_id: str) -> ParserResult:
        """Read the document and return candidates. Writes nothing.

        Implementations must not touch the ArtifactRegistry, the
        StatementEditor, the ReviewLog or the Truth Engine.
        """

    def describe(self) -> Dict[str, Any]:
        return {
            "parser_id": self.parser_id,
            "parser_version": self.parser_version,
            "modality": self.modality.value,
            "supported_statement_types": sorted(self.supported_statement_types()),
        }


class ParserRegistry:
    """Registry of available parsers. Flat, not a hierarchy."""

    def __init__(self) -> None:
        self._parsers: Dict[str, DocumentParser] = {}

    def register(self, parser: DocumentParser) -> None:
        if not parser.parser_id:
            raise ValueError("A parser must declare a parser_id.")
        key = f"{parser.parser_id}@{parser.parser_version}"
        if key in self._parsers:
            raise ValueError(f"Parser {key} is already registered.")
        self._parsers[key] = parser

    def get(self, parser_id: str, version: str) -> DocumentParser:
        return self._parsers[f"{parser_id}@{version}"]

    def candidates_for(self, path: str) -> List[DocumentParser]:
        """Parsers that claim they can read this file, in registration order."""
        return [p for _, p in sorted(self._parsers.items()) if p.can_read(path)]

    def for_statement_type(self, statement_type: str) -> List[DocumentParser]:
        return [
            p for _, p in sorted(self._parsers.items())
            if statement_type in p.supported_statement_types()
        ]

    def all(self) -> List[DocumentParser]:
        return [p for _, p in sorted(self._parsers.items())]

    def __len__(self) -> int:
        return len(self._parsers)
