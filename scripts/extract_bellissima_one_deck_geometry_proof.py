"""Reproduce the fail-closed MSC Bellissima Deck 14 geometry proof.

This is deliberately a one-page, one-deck experiment. It is not a fleet or
whole-ship extractor. PyMuPDF is loaded lazily because it is forensic tooling,
not a Timonelo runtime dependency.

Cabin detection and association now live in
`timonelo.spatial.deck14_extract`, which covers the whole Deck 14 cabin block
rather than a locked ten. This script keeps the lift-region derivation, the
source identity block and the artifact writers.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from timonelo.evidence.registry import ArtifactRegistry
from timonelo.spatial import deck14_extract


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ID = "ART-0001"
ARTIFACT_SHA256 = "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"
PAGE_NUMBER = 5
DECK_NUMBER = 14
DECK_NAME = "World Class"
PAGE_WIDTH_POINTS = 589.606
PAGE_HEIGHT_POINTS = 807.874
REVIEW_VIEWPORT = (24.0, 198.0, 128.0, 748.0)
STRICT_INTERIOR_EPSILON_POINTS = 0.01
#: The original locked proof subset. The cabin block is now extracted in full
#: by `timonelo.spatial.deck14_extract`; this tuple is retained only as the
#: regression scope for `resolve_cabin_boundary_association`, which predates
#: the module and is still exercised directly by the test suite.
PROOF_CABINS = (
    "14001", "14002", "14003", "14004", "14005",
    "14006", "14007", "14008", "14009", "14010",
)
RAW_OUTPUT = ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.raw.json"
PROOF_OUTPUT = ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.proof.json"
OVERLAY_OUTPUT = ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.review.png"


def _fitz() -> Any:
    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError("PyMuPDF is required to reproduce this forensic proof") from exc
    return fitz


def _round_bbox(rect: Any) -> list[float]:
    return [round(value, 6) for value in (rect.x0, rect.y0, rect.x1, rect.y1)]


def normalize_bbox(
    bbox: list[float],
    page_width: float = PAGE_WIDTH_POINTS,
    page_height: float = PAGE_HEIGHT_POINTS,
) -> list[float]:
    """Map PDF page points into the neutral MediaBox-derived page frame."""
    return [
        round(bbox[0] / page_width, 9),
        round(bbox[1] / page_height, 9),
        round(bbox[2] / page_width, 9),
        round(bbox[3] / page_height, 9),
    ]


def _polygon_from_bbox(bbox: list[float]) -> list[list[float]]:
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _source_path(draw: dict[str, Any], drawing_index: int) -> dict[str, Any]:
    return {
        "source_reference": f"page5:drawing-index-{drawing_index}:seqno-{draw['seqno']}",
        "drawing_index": drawing_index,
        "sequence_number": draw["seqno"],
        "paint_type": draw["type"],
        "source_bbox": _round_bbox(draw["rect"]),
        "item_count": len(draw["items"]),
        "fill_rgb": list(draw["fill"]) if draw["fill"] else None,
        "stroke_rgb": list(draw["color"]) if draw["color"] else None,
        "geometry_provenance": "DIRECT_SOURCE_GEOMETRY",
    }


def _strictly_contains_reference_point(
    candidate_bbox: list[float],
    reference_point: list[float],
    epsilon: float = STRICT_INTERIOR_EPSILON_POINTS,
) -> bool:
    """Require the label centroid to be strictly inside by a fixed epsilon."""
    x0, y0, x1, y1 = candidate_bbox
    x, y = reference_point
    return x0 + epsilon < x < x1 - epsilon and y0 + epsilon < y < y1 - epsilon


def resolve_cabin_boundary_association(
    label_text: str,
    label_bbox: list[float],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Resolve one cabin label without ranking or guessing among containers."""
    reference_point = [
        round((label_bbox[0] + label_bbox[2]) / 2, 6),
        round((label_bbox[1] + label_bbox[3]) / 2, 6),
    ]
    if label_text not in PROOF_CABINS or not re.fullmatch(r"14\d{3}", label_text):
        return {
            "status": "REJECTED",
            "label_text": label_text,
            "label_bbox": label_bbox,
            "reference_point": reference_point,
            "candidate_count": 0,
            "candidate_source_drawing_ids": [],
            "reason": "label is outside the locked Deck 14 cabin proof set",
            "accepted_geometry": None,
            "ambiguity": False,
        }
    enclosing = [
        candidate
        for candidate in candidates
        if _strictly_contains_reference_point(candidate["source_bbox"], reference_point)
    ]
    base = {
        "label_text": label_text,
        "label_bbox": label_bbox,
        "reference_point": reference_point,
        "candidate_count": len(enclosing),
        "candidate_source_drawing_ids": [
            candidate["source_reference"] for candidate in enclosing
        ],
        "containment_policy": {
            "reference_point": "label_bbox_centroid",
            "epsilon_points": STRICT_INTERIOR_EPSILON_POINTS,
            "rule": "strictly inside on all axes by more than epsilon",
            "boundary_behavior": "excluded; unresolved unless exactly one other candidate contains the point",
        },
    }
    if not enclosing:
        return {
            **base,
            "status": "UNRESOLVED",
            "reason": "no qualifying source boundary strictly contains the label reference point",
            "accepted_geometry": None,
            "ambiguity": False,
        }
    if len(enclosing) > 1:
        return {
            **base,
            "status": "AMBIGUOUS",
            "reason": "multiple source boundaries strictly contain the label reference point",
            "accepted_geometry": None,
            "ambiguity": True,
        }
    return {
        **base,
        "status": "ACCEPTED",
        "reason": "exactly one source boundary strictly contains the label reference point",
        "accepted_geometry": enclosing[0],
        "ambiguity": False,
    }


def require_unique_text_match(label_text: str, matches: list[Any]) -> Any:
    """Reject missing or duplicate selectable text for a locked proof label."""
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one page-5 text object for {label_text}; found {len(matches)}"
        )
    return matches[0]


def _verify_source() -> Path:
    registry = ArtifactRegistry(str(ROOT / "evidence" / "artifacts"))
    if not registry.verify(ARTIFACT_ID):
        raise RuntimeError("ART-0001 failed ArtifactRegistry verification")
    resolved = Path(registry.resolve_path(ARTIFACT_ID) or "").resolve()
    expected = (
        ROOT
        / "evidence" / "raw" / "sha256" / "08"
        / f"{ARTIFACT_SHA256}.pdf"
    ).resolve()
    if resolved != expected:
        raise RuntimeError(f"ART-0001 resolved outside the locked SHA vault path: {resolved}")
    if hashlib.sha256(resolved.read_bytes()).hexdigest() != ARTIFACT_SHA256:
        raise RuntimeError("ART-0001 digest changed after registry verification")
    return resolved


def extract() -> tuple[dict[str, Any], dict[str, Any], Path]:
    fitz = _fitz()
    source_path = _verify_source()
    document = fitz.open(source_path)
    page = document[PAGE_NUMBER - 1]
    if (
        abs(page.rect.width - PAGE_WIDTH_POINTS) > 0.001
        or abs(page.rect.height - PAGE_HEIGHT_POINTS) > 0.001
    ):
        raise RuntimeError("Page 5 dimensions no longer match the audited MediaBox frame")
    words = page.get_text("words")
    drawings = page.get_drawings()

    selected_text: list[dict[str, Any]] = []
    selected_paths: dict[int, dict[str, Any]] = {}
    associations: list[dict[str, Any]] = []
    proof_objects: list[dict[str, Any]] = []

    labels = deck14_extract.extract_labels(words)
    bounds = deck14_extract.panel_bounds(labels)
    candidates = deck14_extract.detect_cell_candidates(drawings, bounds)
    cells, containers = deck14_extract.partition_containers(candidates, labels)

    extraction = deck14_extract.associate(
        deck14_extract.extract_labels(words),
        cells,
    )
    if (
        extraction.ambiguous_labels
        or extraction.contested_cells
        or extraction.unresolved_labels
    ):
        raise RuntimeError(
            "Deck 14 cabin association is not deterministic; refusing to write a proof"
        )
    for association in sorted(extraction.associations, key=lambda item: item["label_text"]):
        accepted = association["accepted_geometry"]
        selected_paths[accepted["drawing_index"]] = accepted
        selected_text.append({
            "source_reference": association["text_reference"],
            "text": association["label_text"],
            "source_bbox": association["label_bbox"],
            "object_kind": "selectable_text",
        })
        associations.append(association)
        proof_objects.append(
            deck14_extract.build_cabin_object(
                association, page.rect.width, page.rect.height
            )
        )

    lift_word_matches = [
        word for word in words
        if word[4] == "Lift" and 70.0 < word[0] < 76.0 and 310.0 < word[1] < 320.0
    ]
    if len(lift_word_matches) != 1:
        raise RuntimeError("Locked Deck 14 lift label was not uniquely recoverable")
    lift_word = lift_word_matches[0]
    lift_text_ref = f"page5:text-block-{lift_word[5]}:line-{lift_word[6]}:word-{lift_word[7]}"
    lift_text_bbox = [round(value, 6) for value in lift_word[:4]]
    selected_text.append({
        "source_reference": lift_text_ref,
        "text": "Lift",
        "source_bbox": lift_text_bbox,
        "object_kind": "selectable_text",
    })
    lift_indices = [1222, 1227]
    lift_paths = []
    for drawing_index in lift_indices:
        draw = drawings[drawing_index]
        selected_paths[drawing_index] = _source_path(draw, drawing_index)
        lift_paths.append(draw["rect"])
    lift_bbox_rect = lift_paths[0] | lift_paths[1]
    lift_bbox = _round_bbox(lift_bbox_rect)
    lift_normalized = normalize_bbox(lift_bbox, page.rect.width, page.rect.height)
    lift_geometry_refs = [selected_paths[index]["source_reference"] for index in lift_indices]
    associations.append({
        "semantic_id": "bellissima-deck14-lift-core-proof",
        "text_reference": lift_text_ref,
        "geometry_references": lift_geometry_refs,
        "method": "label-contained-by-union-bbox-of-two-source-vector-groups",
        "rule": "locked source drawing groups 1222 and 1227 flank the selectable Lift label",
        "ambiguity": True,
        "human_review_required": True,
    })
    proof_objects.append({
        "object_id": "bellissima-deck14-lift-core-proof",
        "semantic_type": "vertical_core_region",
        "source_text_bbox": lift_text_bbox,
        "source_bbox": lift_bbox,
        "normalized_bbox": lift_normalized,
        "normalized_polygon": _polygon_from_bbox(lift_normalized),
        "source_references": [lift_text_ref, *lift_geometry_refs],
        "source_geometry_components": [
            {
                "source_reference": selected_paths[index]["source_reference"],
                "drawing_index": selected_paths[index]["drawing_index"],
                "sequence_number": selected_paths[index]["sequence_number"],
                "source_bbox": selected_paths[index]["source_bbox"],
                "geometry_provenance": "DIRECT_SOURCE_GEOMETRY",
            }
            for index in lift_indices
        ],
        "transform_id": "pdf-page5-mediabox-to-unit-v2",
        "geometry_provenance": "DERIVED_GEOMETRY",
        "derivation": "union bbox of two DIRECT_SOURCE_GEOMETRY records, then normalized in the page MediaBox frame",
        "semantic_association_method": "label-contained-by-union-bbox-of-two-source-vector-groups",
        "association_staging_note": "source supports a labelled lift region, not connectivity or nearest-core claims",
        "human_review_state": "DRAFT",
        "evidence_condition": "UNKNOWN",
        "publish_status": "PUBLISH_BLOCKED",
    })

    source_identity = {
        "artifact_id": ARTIFACT_ID,
        "artifact_sha256": ARTIFACT_SHA256,
        "physical_pdf_path": source_path.relative_to(ROOT).as_posix(),
        "pdf_page_number": PAGE_NUMBER,
        "visible_deck_number": DECK_NUMBER,
        "visible_deck_name": DECK_NAME,
        "page_dimensions_points": [round(page.rect.width, 3), round(page.rect.height, 3)],
        "media_box_points": [0.0, 0.0, 589.606, 807.874],
        "crop_box_points": [0.0, 0.0, 589.606, 807.874],
        "rotation_degrees": page.rotation,
        "source_coordinate_system": "PDF page points as exposed by PyMuPDF; origin top-left; +x right; +y down",
        "extraction_timestamp": "2026-08-20T00:00:00Z",
        "extraction_tool": f"PyMuPDF {fitz.VersionBind}",
    }
    raw = {
        "schema": "timonelo.one-deck-geometry-raw.v1",
        "source": source_identity,
        "locked_scope": {"deck_numbers": [DECK_NUMBER], "pdf_pages": [PAGE_NUMBER]},
        "geometry": [selected_paths[index] for index in sorted(selected_paths)],
        "excluded_candidates": {
            "policy": {
                "multi_label_container": (
                    "a stroked rectangle enclosing two or more cabin labels is a block "
                    "outline, not a cabin, and is removed before association"
                ),
                "unlabeled_cell": (
                    "a candidate enclosing no cabin label yields no object; it is "
                    "recorded, never assigned"
                ),
            },
            "multi_label_containers": [
                {
                    "source_reference": container["source_reference"],
                    "drawing_index": container["drawing_index"],
                    "source_bbox": container["source_bbox"],
                    "enclosed_labels": container["enclosed_labels"],
                }
                for container in containers
            ],
            "unlabeled_cells": [
                {
                    "source_reference": cell["source_reference"],
                    "drawing_index": cell["drawing_index"],
                    "source_bbox": cell["source_bbox"],
                }
                for cell in extraction.unlabeled_cells
            ],
        },
        "text": selected_text,
        "symbols": [{
            "symbol_id": "deck14-lift-vector-groups",
            "source_references": lift_geometry_refs,
            "classification": "source_vector_groups_adjacent_to_selectable_lift_label",
        }],
        "semantic_associations": associations,
    }
    proof = {
        "schema": "timonelo.one-deck-geometry-proof.v1",
        "source": source_identity,
        "deck": {"number": DECK_NUMBER, "name": DECK_NAME},
        "transform": {
            "transform_id": "pdf-page5-mediabox-to-unit-v2",
            "frame_type": "PDF_PAGE_MEDIABOX",
            "frame_semantics": "CANONICAL_NON_SEMANTIC_PAGE_FRAME",
            "source_origin": [0.0, 0.0],
            "source_units": "PDF points",
            "source_axis_direction": {"x": "right", "y": "down"},
            "source_bbox": [0.0, 0.0, round(page.rect.width, 3), round(page.rect.height, 3)],
            "source_width": round(page.rect.width, 3),
            "source_height": round(page.rect.height, 3),
            "frame_source": "physical PDF page 5 MediaBox as exposed by PyMuPDF page.rect",
            "target_origin": [0.0, 0.0],
            "target_units": "normalized fraction of PDF page MediaBox",
            "target_axis_direction": {"x": "right", "y": "down"},
            "rotation_degrees": 0,
            "translation": [0.0, 0.0],
            "scaling": [1 / page.rect.width, 1 / page.rect.height],
            "clipping": None,
            "formula": "x'=x/page_width; y'=y/page_height",
            "semantic": False,
            "display_only": False,
        },
        "review_viewport": {
            "bbox": list(REVIEW_VIEWPORT),
            "classification": "DISPLAY_ONLY",
            "semantic": False,
            "geometry_provenance": False,
            "reason": "hand-selected viewport used only to make the Deck 14 overlay legible",
        },
        "objects": proof_objects,
        "corridor_observation": {
            "classification": "INFERRED_NEGATIVE_SPACE",
            "accepted_geometry": False,
            "geometry": None,
            "reason": "The apparent corridor is negative space; no independently bounded source polygon was established.",
            "human_review_state": "DRAFT",
            "evidence_condition": "UNKNOWN",
            "publish_status": "PUBLISH_BLOCKED",
        },
        "venue_observation": {
            "accepted_geometry": False,
            "geometry": None,
            "reason": "No public venue is labelled within the locked Deck 14 proof region.",
        },
        "cross_deck_relationships": [],
        "navigation_graph": None,
        "nearest_core_calculation": None,
        "above_below_relations": [],
        "port_starboard_associations": [],
    }
    return raw, proof, source_path


def _render_overlay(proof: dict[str, Any], source_path: Path) -> None:
    fitz = _fitz()
    source = fitz.open(source_path)
    clip = fitz.Rect(*REVIEW_VIEWPORT)
    review = fitz.open()
    page = review.new_page(width=clip.width, height=clip.height)
    page.show_pdf_page(page.rect, source, PAGE_NUMBER - 1, clip=clip)
    for obj in proof["objects"]:
        source_bbox = obj["source_bbox"]
        rect = fitz.Rect(
            source_bbox[0] - clip.x0,
            source_bbox[1] - clip.y0,
            source_bbox[2] - clip.x0,
            source_bbox[3] - clip.y0,
        )
        color = (0.0, 0.55, 0.9) if obj["semantic_type"] == "cabin" else (0.9, 0.2, 0.1)
        page.draw_rect(rect, color=color, width=0.8, overlay=True)
    note_rect = fitz.Rect(1, 1, clip.width - 1, 14)
    page.draw_rect(note_rect, color=(0.05, 0.05, 0.05), fill=(1, 1, 1), fill_opacity=0.85, overlay=True)
    page.insert_text((3, 10), "DRAFT / UNKNOWN / PUBLISH_BLOCKED", fontsize=3.5, color=(0.05, 0.05, 0.05), overlay=True)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
    OVERLAY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_OUTPUT.write_bytes(pixmap.tobytes("png"))


def write_outputs() -> None:
    raw, proof, source_path = extract()
    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    # Newlines are pinned to LF so the artifact is byte-identical regardless of
    # the platform it was generated on. The shipped frontend copy is compared to
    # this file by digest, and a CRLF host would break that comparison.
    RAW_OUTPUT.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    PROOF_OUTPUT.write_text(
        json.dumps(proof, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _render_overlay(proof, source_path)


if __name__ == "__main__":
    write_outputs()
