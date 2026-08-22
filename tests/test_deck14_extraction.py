"""
Guards the deterministic Deck 14 cabin-cell extraction.

The proof widened from ten hand-checked cabins to the whole Deck 14 block. That
is only safe while the extraction stays deterministic and while the original ten
envelopes are reproduced exactly — a silent shift in those would mean the
widening rewrote adjudicated geometry instead of extending it.

These tests read the held ART-0001 bytes directly, so they assert what the
source says rather than what the artifact claims.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from timonelo.spatial import deck14_extract

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROOF = REPO_ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.proof.json"

EXPECTED_LABELS = 243
EXPECTED_CELLS = 245
EXPECTED_CONTAINERS = 1
EXPECTED_UNLABELED = 2
ORIGINAL_TEN = (
    "14001", "14002", "14003", "14004", "14005",
    "14006", "14007", "14008", "14009", "14010",
)

pytest.importorskip("fitz", reason="PyMuPDF is forensic tooling, not a runtime dependency")


@pytest.fixture(scope="module")
def report():
    return deck14_extract.extract()


@pytest.fixture(scope="module")
def proof():
    return json.loads(PROOF.read_text(encoding="utf-8"))


def test_every_deck14_label_is_found_and_distinct(report):
    assert len(report.labels) == EXPECTED_LABELS
    texts = [label.text for label in report.labels]
    assert len(set(texts)) == EXPECTED_LABELS
    assert all(text.startswith("14") and len(text) == 5 for text in texts)


def test_association_is_one_to_one_with_no_residue(report):
    assert report.unique_association_count == EXPECTED_LABELS
    assert report.ambiguous_labels == []
    assert report.contested_cells == []
    assert report.unresolved_labels == []


def test_exactly_one_multi_label_container_is_excluded(report):
    assert len(report.containers) == EXPECTED_CONTAINERS
    container = report.containers[0]
    # The container spans the 14102-14122 stack. Without the exclusion rule it
    # contains all six labels and every one of them becomes ambiguous.
    assert container["enclosed_labels"] == [
        "14102", "14106", "14110", "14114", "14118", "14122",
    ]
    assert len(container["enclosed_labels"]) >= deck14_extract.CONTAINER_LABEL_THRESHOLD


def test_exactly_two_unlabeled_blocks_are_excluded_from_cabins(report):
    assert len(report.unlabeled_cells) == EXPECTED_UNLABELED
    accepted = {
        association["accepted_geometry"]["source_reference"]
        for association in report.associations
    }
    for cell in report.unlabeled_cells:
        assert cell["source_reference"] not in accepted


def test_detected_cell_count_is_stable(report):
    assert len(report.cells) == EXPECTED_CELLS
    assert len(report.cells) + len(report.containers) == EXPECTED_CELLS + 1


def test_original_ten_source_bboxes_reproduce_exactly(report, proof):
    """The regression that matters: widening must not move adjudicated geometry."""
    committed = {
        obj["cabin_number"]: obj
        for obj in proof["objects"]
        if obj["semantic_type"] == "cabin"
    }
    extracted = {
        association["label_text"]: deck14_extract.build_cabin_object(
            association, report.page_width, report.page_height
        )
        for association in report.associations
    }
    for cabin in ORIGINAL_TEN:
        assert extracted[cabin]["source_bbox"] == committed[cabin]["source_bbox"]
        assert extracted[cabin]["normalized_bbox"] == committed[cabin]["normalized_bbox"]
        assert extracted[cabin] == committed[cabin]


def test_normalization_uses_the_canonical_mediabox_transform(report, proof):
    assert proof["transform"]["transform_id"] == deck14_extract.TRANSFORM_ID
    width, height = report.page_width, report.page_height
    for obj in proof["objects"]:
        if obj["semantic_type"] != "cabin":
            continue
        assert obj["normalized_bbox"] == deck14_extract.normalize_bbox(
            obj["source_bbox"], width, height
        )


def test_extraction_fails_closed_on_ambiguity(report):
    """A duplicated cell makes one label ambiguous, and nothing is emitted for it."""
    doubled = list(report.cells) + [dict(report.cells[0])]
    degraded = deck14_extract.associate(report.labels, doubled)
    assert degraded.unique_association_count < EXPECTED_LABELS
    assert degraded.ambiguous_labels


def test_duplicate_labels_are_refused():
    label = deck14_extract.CabinLabel("14001", [1.0, 1.0, 2.0, 2.0], "ref")
    with pytest.raises(deck14_extract.Deck14ExtractionError):
        deck14_extract.extract_labels(
            [
                (1.0, 1.0, 2.0, 2.0, "14001", 0, 0, 0),
                (3.0, 3.0, 4.0, 4.0, "14001", 0, 0, 1),
            ]
        )
    assert label.centroid == [1.5, 1.5]


def test_boundary_touching_centroid_is_not_assigned():
    """A centroid on the shared edge is unresolved, never rounded into a cell."""
    bbox = [0.0, 0.0, 10.0, 10.0]
    assert deck14_extract.strictly_contains(bbox, [5.0, 5.0])
    assert not deck14_extract.strictly_contains(bbox, [0.0, 5.0])
    assert not deck14_extract.strictly_contains(bbox, [10.0, 5.0])


def test_proof_carries_every_cabin_and_the_lift_region(proof):
    cabins = [o for o in proof["objects"] if o["semantic_type"] == "cabin"]
    cores = [o for o in proof["objects"] if o["semantic_type"] == "vertical_core_region"]
    assert len(proof["objects"]) == 244
    assert len(cabins) == EXPECTED_LABELS
    assert len(cores) == 1
    assert len({o["cabin_number"] for o in cabins}) == EXPECTED_LABELS


def test_new_geometry_stays_unpublished_and_source_derived(proof):
    for obj in proof["objects"]:
        assert obj["human_review_state"] == "DRAFT"
        assert obj["evidence_condition"] == "UNKNOWN"
        assert obj["publish_status"] == "PUBLISH_BLOCKED"
    for obj in proof["objects"]:
        if obj["semantic_type"] == "cabin":
            assert obj["geometry_provenance"] == "TRANSFORMED_SOURCE_GEOMETRY"
            assert obj["source_geometry"]["geometry_provenance"] == "DIRECT_SOURCE_GEOMETRY"


def test_expansion_introduced_no_connectivity_and_no_metric_scale(proof):
    assert proof["navigation_graph"] is None
    assert proof["nearest_core_calculation"] is None
    assert proof["cross_deck_relationships"] == []
    assert proof["above_below_relations"] == []
    assert proof["port_starboard_associations"] == []
    assert proof["corridor_observation"]["accepted_geometry"] is False
    assert proof["corridor_observation"]["geometry"] is None
    assert proof["transform"]["target_units"] == "normalized fraction of PDF page MediaBox"
    assert proof["transform"]["semantic"] is False
    # No object may carry a metre-denominated field.
    serialized = json.dumps(proof)
    for banned in ('"length_meters"', '"distance_meters"', '"walking_time'):
        assert banned not in serialized


def test_review_viewport_did_not_become_the_extraction_frame(proof, report):
    """The extraction band is derived from the labels, never from the viewport.

    Checking for cabins outside the viewport would prove nothing: the viewport
    was hand-picked to cover this very panel, so the two regions overlap by
    construction. What can be checked is that they are not the same region, and
    that the extractor never reads the viewport at all.
    """
    viewport = proof["review_viewport"]
    assert viewport["classification"] == "DISPLAY_ONLY"
    assert viewport["semantic"] is False

    assert tuple(round(v, 6) for v in report.panel_bounds) != tuple(viewport["bbox"])
    assert report.panel_bounds == deck14_extract.panel_bounds(report.labels)

    source = pathlib.Path(deck14_extract.__file__).read_text(encoding="utf-8")
    assert "review_viewport" not in source.replace(
        "`review_viewport` is DISPLAY_ONLY and is never a render or", ""
    ), "the extractor must not read the DISPLAY_ONLY viewport"
