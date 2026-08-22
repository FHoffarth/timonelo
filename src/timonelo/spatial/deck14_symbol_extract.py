"""
Deterministic Deck 14 cabin-symbol extraction from ART-0001 page 5.

Scope is deliberately narrow: the six sleeping-arrangement legend families that
prior audits grounded against the page-2 legend by normalized shape identity.
The other legend families are not implemented here. Three of them (`H`, `B`,
`BS`) are drawn as letter outlines, and the rest either have no page-5
counterpart or are separated only by fill colour; none is settled, so none is
extracted.

Grounding, and what "grounded" means
-----------------------------------
A family is grounded when its page-2 legend exemplar and its page-5 instances
are the same drawing up to translation, uniform scale, rotation and reflection.
Deck-plan instances are drawn at roughly a quarter of legend size, so raw
dimensions never match; the comparison is on the normalized point sequence.

Two families are shapes that carry no information on their own — a square and a
circle match every other square and circle. They are admitted only because
cluster cardinality reproduces the legend's own composite structure:

* one square  -> 3. Bett zum Herunterklappen
* two squares -> 3. und 4. Bett zum Herunterklappen
* two circles -> Etagenbett / umwandelbares Sofa

That is a derivation, not a direct read, and it is recorded as one on every
statement it produces.

What this refuses
-----------------
Absence of a symbol is not absence of a feature. A cabin with no mark is
unmarked, and this module emits nothing for it — never a negative claim. A
symbol whose centroid falls inside more than one cabin envelope is dropped
rather than assigned, and a symbol outside every envelope is dropped too.

Nothing here reads the raster underlay, uses OCR, or infers amenities from
cabin category names. Features come from vector symbol geometry alone.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from timonelo.spatial import deck14_extract

ARTIFACT_ID = deck14_extract.ARTIFACT_ID
ARTIFACT_SHA256 = deck14_extract.ARTIFACT_SHA256
SYMBOL_PAGE_NUMBER = 5
LEGEND_PAGE_NUMBER = 2

#: Maximum per-point deviation between a legend exemplar and a page-5 instance,
#: after both are normalized into the unit square. Every family lands below
#: 0.009 except the one exception recorded in `SHAPE_TOLERANCE_OVERRIDES`.
SHAPE_TOLERANCE = 0.02

#: `Schlafsofa für eine Person` is an 18-segment outline whose two page-5
#: instances both sit at 0.0203 — deviating from the exemplar identically and
#: from each other not at all, which is coordinate rounding at quarter scale
#: rather than a different shape.
#:
#: The override is per family on purpose. A blanket raise would also loosen the
#: square and circle families, and because those primitives carry no shape
#: information a looser threshold silently admits unrelated squares and circles:
#: at 0.025 the circle pool grows from 134 instances to 208.
SHAPE_TOLERANCE_OVERRIDES: Dict[str, float] = {"sofa_bed_single": 0.025}


def tolerance_for(family_id: str) -> float:
    return SHAPE_TOLERANCE_OVERRIDES.get(family_id, SHAPE_TOLERANCE)


#: Deck-plan symbols are drawn smaller than their legend exemplar, and the
#: reduction is per family rather than one global factor: the three families
#: whose outlines are distinctive enough to identify on shape alone measure
#: 0.250 (sofa_bed), 0.275 (sofa_bed_double) and 0.320 (sofa_bed_single) of
#: legend size. This band spans those observed ratios.
#:
#: It matters only for the square and circle families. A bare circle matches
#: every other circle at any size, so without a scale gate the pool picks up
#: unrelated plan circles at 0.73, 1.87, 2.70, 2.81 and 4.90 pt alongside the
#: 1.16 pt symbol — 208 instances instead of 148. Shape cannot separate those;
#: scale can.
SCALE_RATIO_BAND = (0.24, 0.33)


def _within_scale_band(legend: Any, candidate: Any) -> bool:
    legend_size = max(legend.width, legend.height)
    candidate_size = max(candidate.width, candidate.height)
    if legend_size <= 0:
        return False
    ratio = candidate_size / legend_size
    return SCALE_RATIO_BAND[0] <= ratio <= SCALE_RATIO_BAND[1]

#: The legend symbol column on page 2, left of the legend text at x=53.86.
LEGEND_COLUMN_MAX_X = 54.0
LEGEND_COLUMN_MIN_X = 18.0
LEGEND_ROW_TOLERANCE = 1.2

#: Legend pair spacing, as a fraction of symbol size, measured on page 2:
#: squares 1.41/4.25, circles 0.88/4.25. Instances further apart than this are
#: separate symbols, not a composite.
SQUARE_PAIR_GAP_RATIO = 0.332
CIRCLE_PAIR_GAP_RATIO = 0.207
PAIR_GAP_SLACK = 1.9
PAIR_ROW_TOLERANCE = 0.6


@dataclass(frozen=True)
class SymbolFamily:
    """One grounded legend family and how to recognise it."""

    family_id: str
    legend_de: str
    label_en: str
    statement_type: str
    question_id: str
    #: Top-left y of the legend exemplar on page 2, used to locate it.
    legend_symbol_y: float
    #: How many instances form one symbol. >1 means the family is derived from
    #: cluster cardinality rather than read directly.
    cardinality: int = 1
    pair_gap_ratio: Optional[float] = None
    #: True when the primitive is a bare square/circle that carries no shape
    #: information by itself.
    degenerate_primitive: bool = False

    @property
    def is_derived(self) -> bool:
        return self.cardinality > 1 or self.degenerate_primitive


#: The six families grounded by the symbol-mapping audits. Ordered as the
#: legend orders them.
GROUNDED_FAMILIES: Tuple[SymbolFamily, ...] = (
    SymbolFamily(
        family_id="sofa_bed",
        legend_de="Schlafsofa",
        label_en="Sofa bed",
        statement_type="cabin.sofa_bed",
        question_id="Q-0017",
        legend_symbol_y=177.74,
    ),
    SymbolFamily(
        family_id="sofa_bed_double",
        legend_de="Schlafsofa für zwei Personen",
        label_en="Sofa bed for two",
        statement_type="cabin.sofa_bed_double",
        question_id="Q-0018",
        legend_symbol_y=191.17,
    ),
    SymbolFamily(
        family_id="third_bed",
        legend_de="3. Bett zum Herunterklappen",
        label_en="3rd pull-down bed",
        statement_type="cabin.third_bed",
        question_id="Q-0020",
        legend_symbol_y=206.59,
        cardinality=1,
        pair_gap_ratio=SQUARE_PAIR_GAP_RATIO,
        degenerate_primitive=True,
    ),
    SymbolFamily(
        family_id="third_and_fourth_bed",
        legend_de="3. und 4. Bett zum Herunterklappen",
        label_en="3rd and 4th pull-down beds",
        statement_type="cabin.third_and_fourth_bed",
        question_id="Q-0021",
        legend_symbol_y=206.59,
        cardinality=2,
        pair_gap_ratio=SQUARE_PAIR_GAP_RATIO,
        degenerate_primitive=True,
    ),
    SymbolFamily(
        family_id="bunk_or_convertible_sofa",
        legend_de="Etagenbett oder Sofa, das in ein Etagenbett umgewandelt werden kann",
        label_en="Convertible bunk / sofa",
        statement_type="cabin.bunk_or_convertible_sofa",
        question_id="Q-0022",
        legend_symbol_y=242.03,
        cardinality=2,
        pair_gap_ratio=CIRCLE_PAIR_GAP_RATIO,
        degenerate_primitive=True,
    ),
    SymbolFamily(
        family_id="sofa_bed_single",
        legend_de="Schlafsofa für eine Person",
        label_en="Sofa bed for one",
        statement_type="cabin.sofa_bed_single",
        question_id="Q-0019",
        legend_symbol_y=262.68,
    ),
)

FAMILY_BY_ID: Dict[str, SymbolFamily] = {f.family_id: f for f in GROUNDED_FAMILIES}

#: Statement value domain. Explicit, closed, and one value per grounded family.
FEATURE_VALUES: Tuple[str, ...] = tuple(f.family_id for f in GROUNDED_FAMILIES)


class Deck14SymbolExtractionError(RuntimeError):
    """Raised when the source no longer supports a deterministic extraction."""


# --------------------------------------------------------------------------
# shape normalization
# --------------------------------------------------------------------------

def _points(drawing: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Flatten a PyMuPDF drawing into an ordered point sequence."""
    out: List[Tuple[float, float]] = []
    for item in drawing["items"]:
        for value in item[1:]:
            if hasattr(value, "x") and hasattr(value, "y"):
                out.append((value.x, value.y))
            elif hasattr(value, "x0"):
                # A rect: canonical corner order, so a negative width/height
                # cannot reverse the sequence.
                x0, x1 = sorted((value.x0, value.x1))
                y0, y1 = sorted((value.y0, value.y1))
                out += [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return out


def _unit(points: Sequence[Tuple[float, float]]) -> Optional[List[Tuple[float, float]]]:
    """Scale a point sequence into the unit square, preserving aspect."""
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    if span <= 0:
        return None
    return [((x - min(xs)) / span, (y - min(ys)) / span) for x, y in points]


def _variants(points: Sequence[Tuple[float, float]]) -> List[List[Tuple[float, float]]]:
    """Every cyclic start offset crossed with the four axis reflections.

    Reflections cover the 90/180/270 rotations these symbols actually appear in;
    the aft cabin block on Deck 14 is drawn rotated, so this is load-bearing.
    """
    out: List[List[Tuple[float, float]]] = []
    for flip in range(4):
        flipped = [
            ((1 - x) if flip & 1 else x, (1 - y) if flip & 2 else y) for x, y in points
        ]
        for start in range(len(flipped)):
            out.append(flipped[start:] + flipped[:start])
    return out


def shape_deviation(
    exemplar: Sequence[Tuple[float, float]],
    candidate: Sequence[Tuple[float, float]],
) -> Optional[float]:
    """Max per-point distance under the best rotation/reflection alignment."""
    if len(exemplar) != len(candidate):
        return None
    best: Optional[float] = None
    for variant in _variants(candidate):
        worst = max(
            math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(exemplar, variant)
        )
        best = worst if best is None else min(best, worst)
    return best


def _signature(drawing: Dict[str, Any]) -> str:
    return "".join(item[0] for item in drawing["items"])


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------

@dataclass
class SymbolObservation:
    """One symbol instance, grounded and attributed to exactly one cabin."""

    family_id: str
    cabin_number: str
    source_bbox: List[float]
    source_references: List[str]
    drawing_indices: List[int]
    shape_deviation: float
    instance_count: int

    @property
    def family(self) -> SymbolFamily:
        return FAMILY_BY_ID[self.family_id]


@dataclass
class SymbolReport:
    observations: List[SymbolObservation] = field(default_factory=list)
    #: Symbols matched to a family but owned by more than one cabin envelope.
    ambiguous_ownership: List[Dict[str, Any]] = field(default_factory=list)
    #: Symbols matched to a family but inside no Deck-14 cabin envelope.
    outside_cabin_geometry: Dict[str, int] = field(default_factory=dict)
    matched_instances: Dict[str, int] = field(default_factory=dict)
    #: Clusters whose size matches no grounded cardinality for that primitive.
    #: A lone circle is neither "3. Bett" nor "Etagenbett", so it yields
    #: nothing — but it is counted here rather than dropped silently.
    unmatched_cardinality: Dict[str, Dict[int, int]] = field(default_factory=dict)

    def by_cabin(self) -> Dict[str, List[SymbolObservation]]:
        out: Dict[str, List[SymbolObservation]] = {}
        for observation in self.observations:
            out.setdefault(observation.cabin_number, []).append(observation)
        for values in out.values():
            values.sort(key=lambda o: o.family_id)
        return out

    def counts_by_family(self) -> Dict[str, int]:
        counts = {family.family_id: 0 for family in GROUNDED_FAMILIES}
        for observation in self.observations:
            counts[observation.family_id] += 1
        return counts


def _legend_exemplars(legend_page: Any) -> Dict[str, Dict[str, Any]]:
    """Locate each grounded family's exemplar drawing in the page-2 legend."""
    exemplars: Dict[str, Dict[str, Any]] = {}
    drawings = legend_page.get_drawings()
    for family in GROUNDED_FAMILIES:
        matches = [
            drawing
            for drawing in drawings
            if LEGEND_COLUMN_MIN_X <= drawing["rect"].x0
            and drawing["rect"].x1 <= LEGEND_COLUMN_MAX_X
            and abs(drawing["rect"].y0 - family.legend_symbol_y) < LEGEND_ROW_TOLERANCE
            and drawing["rect"].width > 1
            and drawing["rect"].height > 1
        ]
        if not matches:
            raise Deck14SymbolExtractionError(
                f"Legend exemplar for {family.family_id!r} was not found on page "
                f"{LEGEND_PAGE_NUMBER}; the legend layout has changed"
            )
        exemplars[family.family_id] = matches[0]
    return exemplars


def _cluster(
    boxes: Sequence[Tuple[List[float], int, str, float]],
    gap_ratio: float,
) -> List[List[Tuple[List[float], int, str, float]]]:
    """Group neighbouring instances using the legend's own pair spacing."""
    used = [False] * len(boxes)
    groups: List[List[Tuple[List[float], int, str, float]]] = []
    for i, entry in enumerate(boxes):
        box = entry[0]
        if used[i]:
            continue
        group = [boxes[i]]
        used[i] = True
        size = max(box[2] - box[0], box[3] - box[1])
        for j, other_entry in enumerate(boxes):
            other = other_entry[0]
            if used[j] or j == i:
                continue
            dx = max(0.0, max(box[0], other[0]) - min(box[2], other[2]))
            dy = max(0.0, max(box[1], other[1]) - min(box[3], other[3]))
            if dy < size * PAIR_ROW_TOLERANCE and dx < size * gap_ratio * PAIR_GAP_SLACK:
                group.append(boxes[j])
                used[j] = True
        groups.append(group)
    return groups


def extract_symbols(root: Optional[Path] = None) -> SymbolReport:
    """Grounded symbol observations, each owned by exactly one Deck 14 cabin."""
    fitz = deck14_extract._fitz()
    source_path = deck14_extract.verify_source(root)
    geometry = deck14_extract.extract(root)
    cabins = {
        association["label_text"]: association["accepted_geometry"]["source_bbox"]
        for association in geometry.associations
    }

    document = fitz.open(source_path)
    try:
        legend_page = document[LEGEND_PAGE_NUMBER - 1]
        symbol_page = document[SYMBOL_PAGE_NUMBER - 1]
        exemplars = _legend_exemplars(legend_page)
        exemplar_shapes = {
            family_id: _unit(_points(drawing))
            for family_id, drawing in exemplars.items()
        }
        exemplar_signatures = {
            family_id: _signature(drawing) for family_id, drawing in exemplars.items()
        }
        page_drawings = list(enumerate(symbol_page.get_drawings()))
    finally:
        document.close()

    report = SymbolReport()

    def owner_of(bbox: Sequence[float]) -> Tuple[Optional[str], List[str]]:
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        owners = [
            number
            for number, cell in cabins.items()
            if cell[0] <= cx <= cell[2] and cell[1] <= cy <= cell[3]
        ]
        if len(owners) == 1:
            return owners[0], owners
        return None, owners

    # Families are processed independently. The two degenerate primitives share
    # a signature with each other's family, so their instance pool is clustered
    # once and split by cardinality.
    handled_signatures: Dict[str, List[Tuple[List[float], int, str, float]]] = {}

    for family in GROUNDED_FAMILIES:
        signature = exemplar_signatures[family.family_id]
        exemplar_shape = exemplar_shapes[family.family_id]
        tolerance = tolerance_for(family.family_id)
        pool_key = f"{signature}@{tolerance}"
        if pool_key not in handled_signatures:
            pool: List[Tuple[List[float], int, str, float]] = []
            for index, drawing in page_drawings:
                if _signature(drawing) != signature:
                    continue
                deviation = shape_deviation(exemplar_shape, _unit(_points(drawing)) or [])
                if deviation is None or deviation >= tolerance:
                    continue
                rect = drawing["rect"]
                if not _within_scale_band(exemplars[family.family_id]["rect"], rect):
                    continue
                pool.append(
                    (
                        [rect.x0, rect.y0, rect.x1, rect.y1],
                        index,
                        f"page5:drawing-index-{index}:seqno-{drawing['seqno']}",
                        deviation,
                    )
                )
            handled_signatures[pool_key] = pool
        pool = handled_signatures[pool_key]
        report.matched_instances[family.family_id] = len(pool)

        if family.cardinality > 1 or family.pair_gap_ratio is not None:
            groups = _cluster(pool, family.pair_gap_ratio or SQUARE_PAIR_GAP_RATIO)
            units = [g for g in groups if len(g) == family.cardinality]
            leftover: Dict[int, int] = {}
            for group in groups:
                if len(group) != family.cardinality:
                    leftover[len(group)] = leftover.get(len(group), 0) + 1
            report.unmatched_cardinality[family.family_id] = leftover
        else:
            units = [[entry] for entry in pool]

        outside = 0
        for unit in units:
            bbox = [
                min(entry[0][0] for entry in unit),
                min(entry[0][1] for entry in unit),
                max(entry[0][2] for entry in unit),
                max(entry[0][3] for entry in unit),
            ]
            owner, owners = owner_of(bbox)
            if owner is None:
                if len(owners) > 1:
                    report.ambiguous_ownership.append(
                        {
                            "family_id": family.family_id,
                            "source_bbox": bbox,
                            "candidate_cabins": sorted(owners),
                        }
                    )
                else:
                    outside += 1
                continue
            report.observations.append(
                SymbolObservation(
                    family_id=family.family_id,
                    cabin_number=owner,
                    source_bbox=[round(v, 6) for v in bbox],
                    source_references=sorted(entry[2] for entry in unit),
                    drawing_indices=sorted(entry[1] for entry in unit),
                    shape_deviation=round(max(entry[3] for entry in unit), 6),
                    instance_count=len(unit),
                )
            )
        report.outside_cabin_geometry[family.family_id] = outside

    if report.ambiguous_ownership:
        raise Deck14SymbolExtractionError(
            f"{len(report.ambiguous_ownership)} symbols are claimed by more than "
            "one cabin envelope; refusing to attribute them"
        )

    report.observations.sort(key=lambda o: (o.cabin_number, o.family_id))
    return report
