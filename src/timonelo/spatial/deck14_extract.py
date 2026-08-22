"""
Deterministic Deck 14 cabin-cell extraction from ART-0001 page 5.

This widens the original ten-cabin proof to the whole Deck 14 cabin block. It
is still a one-page, one-deck extractor: nothing here generalises to other
decks or other ships, and it must not be turned into a fleet pipeline.

What it reads and what it refuses
---------------------------------
The only geometry accepted is a stroked four-line rectangle drawn on page 5 of
the held ART-0001 bytes. A cabin exists here when exactly one ``14xxx`` label
centroid sits strictly inside exactly one such rectangle, and that rectangle
contains no other cabin label. Everything else is dropped rather than ranked:

* rectangles enclosing two or more cabin labels are **block outlines**, not
  cabins. One such container spans the 14102-14122 stack; without this rule it
  competes with all six of those cabins and the association is ambiguous.
* rectangles enclosing no cabin label are left unassociated. Two oversized
  blocks on Deck 14 fall here. They are reported, never guessed at.

The extractor fails closed. Any ambiguous label, any contested cell, or any
label the source does not resolve raises rather than emitting a best guess.

What it does not establish
--------------------------
A cabin envelope says where a cabin is drawn. It says nothing about corridors,
doors, connectivity, travel distance or cabin features, and this module derives
none of them. Coordinates are fractions of the page MediaBox under the existing
``pdf-page5-mediabox-to-unit-v2`` transform; they are not metres, and no scale
has been read. `review_viewport` is DISPLAY_ONLY and is never a render or
extraction frame.

Every object produced is DRAFT / UNKNOWN / PUBLISH_BLOCKED. Source containment
is deterministic; visual adjudication is still required before anything here
may be published.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from timonelo.evidence.registry import ArtifactRegistry

ARTIFACT_ID = "ART-0001"
ARTIFACT_SHA256 = "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"
PAGE_NUMBER = 5
DECK_NUMBER = 14
DECK_NAME = "World Class"
PAGE_WIDTH_POINTS = 589.606
PAGE_HEIGHT_POINTS = 807.874
TRANSFORM_ID = "pdf-page5-mediabox-to-unit-v2"

CABIN_LABEL_PATTERN = re.compile(r"14\d{3}")

#: The label centroid must clear the boundary by this much on every axis. A
#: centroid sitting exactly on a shared edge is unresolved, not assigned.
STRICT_INTERIOR_EPSILON_POINTS = 0.01

#: The Deck 14 panel band is derived from the Deck 14 labels themselves and
#: then padded. Page 5 carries five deck panels side by side; every ``14xxx``
#: label lies in one contiguous x range that no other deck's labels enter, so
#: the labels define their own panel without a hand-placed frame. The padding
#: admits the cell stroke around the outermost labels and nothing further.
PANEL_MARGIN_X_POINTS = 14.0
PANEL_MARGIN_Y_POINTS = 10.0

#: Cabin cells on this page run roughly 5-16 pt wide and 4-8 pt tall. The
#: bounds are deliberately loose: they exclude page furniture and hairlines,
#: and let the label-cardinality rules do the real discrimination.
MIN_CELL_SIDE_POINTS = 4.0
MAX_CELL_SIDE_POINTS = 40.0

#: A rectangle enclosing at least this many cabin labels is a block outline.
CONTAINER_LABEL_THRESHOLD = 2

ASSOCIATION_METHOD = "strict-label-centroid-containment-with-cardinality-gate"
ASSOCIATION_STAGING_NOTE = (
    "source containment is deterministic; visual adjudication remains required"
)


class Deck14ExtractionError(RuntimeError):
    """Raised when the source no longer supports a deterministic extraction."""


def _fitz() -> Any:
    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - environment guard
        raise Deck14ExtractionError(
            "PyMuPDF is required to reproduce this forensic extraction"
        ) from exc
    return fitz


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def verify_source(root: Optional[Path] = None) -> Path:
    """Resolve ART-0001 through the registry and recompute its digest."""
    root = root or repo_root()
    registry = ArtifactRegistry(str(root / "evidence" / "artifacts"))
    if not registry.verify(ARTIFACT_ID):
        raise Deck14ExtractionError("ART-0001 failed ArtifactRegistry verification")
    resolved = Path(registry.resolve_path(ARTIFACT_ID) or "").resolve()
    expected = (
        root / "evidence" / "raw" / "sha256" / "08" / f"{ARTIFACT_SHA256}.pdf"
    ).resolve()
    if resolved != expected:
        raise Deck14ExtractionError(
            f"ART-0001 resolved outside the locked SHA vault path: {resolved}"
        )
    if hashlib.sha256(resolved.read_bytes()).hexdigest() != ARTIFACT_SHA256:
        raise Deck14ExtractionError("ART-0001 digest changed after registry verification")
    return resolved


def round_bbox(rect: Any) -> List[float]:
    return [round(value, 6) for value in (rect.x0, rect.y0, rect.x1, rect.y1)]


def normalize_bbox(
    bbox: Sequence[float],
    page_width: float = PAGE_WIDTH_POINTS,
    page_height: float = PAGE_HEIGHT_POINTS,
) -> List[float]:
    """Map PDF page points into the neutral MediaBox-derived page frame."""
    return [
        round(bbox[0] / page_width, 9),
        round(bbox[1] / page_height, 9),
        round(bbox[2] / page_width, 9),
        round(bbox[3] / page_height, 9),
    ]


def polygon_from_bbox(bbox: Sequence[float]) -> List[List[float]]:
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _source_path(draw: Dict[str, Any], drawing_index: int) -> Dict[str, Any]:
    return {
        "source_reference": f"page5:drawing-index-{drawing_index}:seqno-{draw['seqno']}",
        "drawing_index": drawing_index,
        "sequence_number": draw["seqno"],
        "paint_type": draw["type"],
        "source_bbox": round_bbox(draw["rect"]),
        "item_count": len(draw["items"]),
        "fill_rgb": list(draw["fill"]) if draw["fill"] else None,
        "stroke_rgb": list(draw["color"]) if draw["color"] else None,
        "geometry_provenance": "DIRECT_SOURCE_GEOMETRY",
    }


def strictly_contains(
    bbox: Sequence[float],
    point: Sequence[float],
    epsilon: float = STRICT_INTERIOR_EPSILON_POINTS,
) -> bool:
    x0, y0, x1, y1 = bbox
    x, y = point
    return x0 + epsilon < x < x1 - epsilon and y0 + epsilon < y < y1 - epsilon


@dataclass(frozen=True)
class CabinLabel:
    text: str
    source_bbox: List[float]
    text_reference: str

    @property
    def centroid(self) -> List[float]:
        return [
            round((self.source_bbox[0] + self.source_bbox[2]) / 2, 6),
            round((self.source_bbox[1] + self.source_bbox[3]) / 2, 6),
        ]


@dataclass
class ExtractionReport:
    labels: List[CabinLabel] = field(default_factory=list)
    cells: List[Dict[str, Any]] = field(default_factory=list)
    containers: List[Dict[str, Any]] = field(default_factory=list)
    unlabeled_cells: List[Dict[str, Any]] = field(default_factory=list)
    associations: List[Dict[str, Any]] = field(default_factory=list)
    ambiguous_labels: List[str] = field(default_factory=list)
    contested_cells: List[str] = field(default_factory=list)
    unresolved_labels: List[str] = field(default_factory=list)
    panel_bounds: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    #: Live MediaBox dimensions, not the rounded constants. The original proof
    #: normalized against `page.rect`, and reusing the rounded values here would
    #: shift every existing coordinate by ~2e-9.
    page_width: float = PAGE_WIDTH_POINTS
    page_height: float = PAGE_HEIGHT_POINTS

    @property
    def unique_association_count(self) -> int:
        return len(self.associations)


def extract_labels(words: Sequence[Any]) -> List[CabinLabel]:
    """Every selectable five-digit Deck 14 cabin label on page 5."""
    labels = [
        CabinLabel(
            text=word[4],
            source_bbox=[round(value, 6) for value in word[:4]],
            text_reference=f"page5:text-block-{word[5]}:line-{word[6]}:word-{word[7]}",
        )
        for word in words
        if CABIN_LABEL_PATTERN.fullmatch(word[4])
    ]
    seen = [label.text for label in labels]
    duplicates = sorted({text for text in seen if seen.count(text) > 1})
    if duplicates:
        raise Deck14ExtractionError(
            f"Deck 14 cabin labels are not unique on page 5: {duplicates}"
        )
    return sorted(labels, key=lambda label: label.text)


def panel_bounds(labels: Sequence[CabinLabel]) -> Tuple[float, float, float, float]:
    """The Deck 14 panel band, derived from the Deck 14 labels themselves."""
    if not labels:
        raise Deck14ExtractionError("No Deck 14 cabin labels were found on page 5")
    return (
        min(label.source_bbox[0] for label in labels) - PANEL_MARGIN_X_POINTS,
        min(label.source_bbox[1] for label in labels) - PANEL_MARGIN_Y_POINTS,
        max(label.source_bbox[2] for label in labels) + PANEL_MARGIN_X_POINTS,
        max(label.source_bbox[3] for label in labels) + PANEL_MARGIN_Y_POINTS,
    )


def detect_cell_candidates(
    drawings: Sequence[Dict[str, Any]],
    bounds: Tuple[float, float, float, float],
) -> List[Dict[str, Any]]:
    """Stroked four-line rectangles inside the Deck 14 panel band."""
    x0, y0, x1, y1 = bounds
    candidates: List[Dict[str, Any]] = []
    for index, draw in enumerate(drawings):
        if draw["type"] != "s" or len(draw["items"]) != 4:
            continue
        if not all(item[0] == "l" for item in draw["items"]):
            continue
        rect = draw["rect"]
        if not (x0 <= rect.x0 and rect.x1 <= x1 and y0 <= rect.y0 and rect.y1 <= y1):
            continue
        if not (
            MIN_CELL_SIDE_POINTS <= rect.width <= MAX_CELL_SIDE_POINTS
            and MIN_CELL_SIDE_POINTS <= rect.height <= MAX_CELL_SIDE_POINTS
        ):
            continue
        candidates.append(_source_path(draw, index))
    return candidates


def partition_containers(
    candidates: Sequence[Dict[str, Any]],
    labels: Sequence[CabinLabel],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split candidates into cabin cells and multi-label block outlines."""
    cells: List[Dict[str, Any]] = []
    containers: List[Dict[str, Any]] = []
    for candidate in candidates:
        enclosed = [
            label.text
            for label in labels
            if strictly_contains(candidate["source_bbox"], label.centroid)
        ]
        if len(enclosed) >= CONTAINER_LABEL_THRESHOLD:
            containers.append({**candidate, "enclosed_labels": sorted(enclosed)})
        else:
            cells.append(candidate)
    return cells, containers


def associate(
    labels: Sequence[CabinLabel],
    cells: Sequence[Dict[str, Any]],
) -> ExtractionReport:
    """Strict 1:1 label-to-cell association. Fails closed on any ambiguity."""
    report = ExtractionReport(labels=list(labels), cells=list(cells))

    label_to_cells: Dict[str, List[int]] = {}
    cell_to_labels: Dict[int, List[str]] = {index: [] for index in range(len(cells))}
    for label in labels:
        hits = [
            index
            for index, cell in enumerate(cells)
            if strictly_contains(cell["source_bbox"], label.centroid)
        ]
        label_to_cells[label.text] = hits
        for index in hits:
            cell_to_labels[index].append(label.text)

    for label in labels:
        hits = label_to_cells[label.text]
        if not hits:
            report.unresolved_labels.append(label.text)
            continue
        if len(hits) > 1:
            report.ambiguous_labels.append(label.text)
            continue
        index = hits[0]
        if len(cell_to_labels[index]) > 1:
            report.contested_cells.append(cells[index]["source_reference"])
            continue
        report.associations.append(
            {
                "semantic_id": label.text,
                "text_reference": label.text_reference,
                "method": ASSOCIATION_METHOD,
                "status": "ACCEPTED",
                "label_text": label.text,
                "label_bbox": label.source_bbox,
                "reference_point": label.centroid,
                "candidate_count": 1,
                "candidate_source_drawing_ids": [cells[index]["source_reference"]],
                "accepted_geometry": cells[index],
                "ambiguity": False,
                "human_review_required": True,
            }
        )

    report.unlabeled_cells = [
        cells[index] for index, texts in cell_to_labels.items() if not texts
    ]
    return report


def build_cabin_object(
    association: Dict[str, Any],
    page_width: float = PAGE_WIDTH_POINTS,
    page_height: float = PAGE_HEIGHT_POINTS,
) -> Dict[str, Any]:
    """One cabin proof object. Lifecycle axes are fixed, never computed."""
    accepted = association["accepted_geometry"]
    boundary_bbox = accepted["source_bbox"]
    normalized = normalize_bbox(boundary_bbox, page_width, page_height)
    cabin_number = association["label_text"]
    return {
        "object_id": f"bellissima-deck14-cabin-{cabin_number}",
        "semantic_type": "cabin",
        "cabin_number": cabin_number,
        "source_text_bbox": association["label_bbox"],
        "source_bbox": boundary_bbox,
        "normalized_bbox": normalized,
        "normalized_polygon": polygon_from_bbox(normalized),
        "source_references": [
            association["text_reference"],
            accepted["source_reference"],
        ],
        "source_geometry": {
            "source_reference": accepted["source_reference"],
            "drawing_index": accepted["drawing_index"],
            "sequence_number": accepted["sequence_number"],
            "source_bbox": accepted["source_bbox"],
            "geometry_provenance": accepted["geometry_provenance"],
        },
        "transform_id": TRANSFORM_ID,
        "geometry_provenance": "TRANSFORMED_SOURCE_GEOMETRY",
        "semantic_association_method": ASSOCIATION_METHOD,
        "association_staging_note": ASSOCIATION_STAGING_NOTE,
        "human_review_state": "DRAFT",
        "evidence_condition": "UNKNOWN",
        "publish_status": "PUBLISH_BLOCKED",
    }


def extract(root: Optional[Path] = None) -> ExtractionReport:
    """Run the full deterministic extraction against the held ART-0001 bytes."""
    fitz = _fitz()
    source_path = verify_source(root)
    document = fitz.open(source_path)
    try:
        page = document[PAGE_NUMBER - 1]
        if (
            abs(page.rect.width - PAGE_WIDTH_POINTS) > 0.001
            or abs(page.rect.height - PAGE_HEIGHT_POINTS) > 0.001
        ):
            raise Deck14ExtractionError(
                "Page 5 dimensions no longer match the audited MediaBox frame"
            )
        if page.rotation != 0:
            raise Deck14ExtractionError("Page 5 is rotated; the locked frame assumes 0")
        page_width = page.rect.width
        page_height = page.rect.height
        words = page.get_text("words")
        drawings = page.get_drawings()
    finally:
        document.close()

    labels = extract_labels(words)
    bounds = panel_bounds(labels)
    candidates = detect_cell_candidates(drawings, bounds)
    cells, containers = partition_containers(candidates, labels)
    report = associate(labels, cells)
    report.containers = containers
    report.panel_bounds = bounds
    report.page_width = page_width
    report.page_height = page_height

    if report.ambiguous_labels or report.contested_cells or report.unresolved_labels:
        raise Deck14ExtractionError(
            "Deck 14 extraction is not deterministic: "
            f"{len(report.ambiguous_labels)} ambiguous labels, "
            f"{len(report.contested_cells)} contested cells, "
            f"{len(report.unresolved_labels)} unresolved labels"
        )
    if report.unique_association_count != len(labels):
        raise Deck14ExtractionError(
            f"Expected one cell per label; got {report.unique_association_count} "
            f"for {len(labels)} labels"
        )
    return report


def cabin_objects(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Cabin proof objects for every uniquely associated Deck 14 label."""
    report = extract(root)
    return [
        build_cabin_object(association, report.page_width, report.page_height)
        for association in sorted(
            report.associations, key=lambda item: item["label_text"]
        )
    ]
