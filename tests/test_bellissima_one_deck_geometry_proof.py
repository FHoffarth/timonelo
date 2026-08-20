from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_bellissima_one_deck_geometry_proof.py"
RAW_PATH = ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.raw.json"
PROOF_PATH = ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.proof.json"
EXPECTED_SYNTHETIC_HASHES = {
    "deck04.geometry.json": "e0a2e6dd2be1f3343274b3062504ae648bc3cf6423f89fb36f9ba627d8fc514a",
    "deck05.geometry.json": "608ff1f5bb8fcd1c74f8005a58750d6d5f3435f7ee6796634164757966bde591",
    "deck06.geometry.json": "d31ee3e93cdbbb1fdae9aba18f9f4b758c98e7bfa92d58fa84ed4977858b026d",
    "deck07.geometry.json": "1b6f5286287f3e8ca0f67d3565fa2db8678e9b66f486d7c448a40096272b528c",
    "deck08.geometry.json": "67624b83db34f290a25ff8f1c2db022a0f1024884d3c79a583a69a91f5c0cc5a",
    "deck09.geometry.json": "a9c4063d9fdecdcb655ecf3bcfeba372d6fc1c4f23e25221f809f185332070bb",
    "deck10.geometry.json": "8f047667ec64727525cc7fcb4636f1c7116752deba061b584916fbf278ea5ee7",
    "deck11.geometry.json": "7b40ca9f948851cc919d552d02b38bcacac3057cf5d2220e0766c622eb447682",
    "deck12.geometry.json": "d2f1e85434223c821692a38c4aa7dc554fad258337fd36c63e28537465d6e3a3",
    "deck13.geometry.json": "43c056fff19dbe3d73118d0f1799d1e8312b45f4368937834eecc32028c4b265",
    "deck14.geometry.json": "2db7c36b01683c9ec7353d2aeec90bce2ffeece2111f5153c0619b4a38016b05",
    "deck15.geometry.json": "eb8a9a0206d605f77a57eb35aeb407fcd9c8ce6ec42c852896fb7b676ae0cfbf",
    "deck16.geometry.json": "7f318291a4f35981f1031bc8936372b9fc3ceec370bb76f657ae233eabb69893",
    "deck18.geometry.json": "6fbef1d3d13c2e88f474328afae3cf98139ff03805dc9547d3a4e1e929fde748",
    "deck19.geometry.json": "0ed07dc553147eb685dd393ffff8e66236ee5510e42756f8c3f2ff639dc5bac5",
}


def _load_script():
    spec = importlib.util.spec_from_file_location("bellissima_geometry_proof", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_outputs():
    return (
        json.loads(RAW_PATH.read_text(encoding="utf-8")),
        json.loads(PROOF_PATH.read_text(encoding="utf-8")),
    )


def _candidate(reference: str, bbox: list[float], drawing_index: int = 1):
    return {
        "source_reference": reference,
        "drawing_index": drawing_index,
        "sequence_number": drawing_index + 100,
        "source_bbox": bbox,
        "geometry_provenance": "DIRECT_SOURCE_GEOMETRY",
    }


def test_proof_uses_verified_art_0001_and_preserves_digest():
    module = _load_script()
    source = module._verify_source()
    assert source.name == f"{module.ARTIFACT_SHA256}.pdf"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == module.ARTIFACT_SHA256
    _, proof = _load_outputs()
    assert proof["source"]["artifact_id"] == "ART-0001"
    assert proof["source"]["artifact_sha256"] == module.ARTIFACT_SHA256


def test_exactly_one_deck_and_page_are_represented():
    raw, proof = _load_outputs()
    assert raw["locked_scope"] == {"deck_numbers": [14], "pdf_pages": [5]}
    assert proof["deck"] == {"number": 14, "name": "World Class"}
    assert {obj["object_id"].split("deck14")[0] for obj in proof["objects"]} == {"bellissima-"}


def test_every_proof_object_has_complete_fail_closed_provenance():
    _, proof = _load_outputs()
    required = {
        "source_bbox", "normalized_bbox", "normalized_polygon", "source_references",
        "transform_id", "geometry_provenance", "semantic_association_method",
        "human_review_state", "evidence_condition", "publish_status",
    }
    assert all(required <= obj.keys() for obj in proof["objects"])
    cabins = [obj for obj in proof["objects"] if obj["semantic_type"] == "cabin"]
    core = next(obj for obj in proof["objects"] if obj["semantic_type"] == "vertical_core_region")
    assert all(obj["geometry_provenance"] == "TRANSFORMED_SOURCE_GEOMETRY" for obj in cabins)
    assert core["geometry_provenance"] == "DERIVED_GEOMETRY"
    assert all(obj["human_review_state"] in {"DRAFT", "UNDER_REVIEW"} for obj in proof["objects"])
    assert all(obj["evidence_condition"] == "UNKNOWN" for obj in proof["objects"])
    assert all(obj["publish_status"] == "PUBLISH_BLOCKED" for obj in proof["objects"])


def test_cabin_proof_set_is_source_backed_without_port_starboard_inference():
    raw, proof = _load_outputs()
    cabins = [obj for obj in proof["objects"] if obj["semantic_type"] == "cabin"]
    assert 5 <= len(cabins) <= 15
    assert len(cabins) == 10
    associations = {item["semantic_id"]: item for item in raw["semantic_associations"]}
    assert all(associations[cabin["cabin_number"]]["ambiguity"] is False for cabin in cabins)
    assert all(cabin["semantic_association_method"] == "strict-label-centroid-containment-with-cardinality-gate" for cabin in cabins)
    assert proof["port_starboard_associations"] == []


def test_transform_is_explicit_and_deterministic():
    module = _load_script()
    _, proof = _load_outputs()
    assert proof["transform"]["formula"] == "x'=x/page_width; y'=y/page_height"
    assert proof["transform"]["frame_type"] == "PDF_PAGE_MEDIABOX"
    assert proof["transform"]["source_bbox"] == [0.0, 0.0, 589.606, 807.874]
    bbox = [37.133801, 246.544495, 49.583801, 254.038498]
    assert module.normalize_bbox(bbox) == module.normalize_bbox(bbox)
    raw_again, proof_again, _ = module.extract()
    raw, committed_proof = _load_outputs()
    assert raw_again == raw
    assert proof_again == committed_proof


def test_corridor_is_not_promoted_from_negative_space():
    _, proof = _load_outputs()
    corridor = proof["corridor_observation"]
    assert corridor["classification"] == "INFERRED_NEGATIVE_SPACE"
    assert corridor["accepted_geometry"] is False
    assert corridor["geometry"] is None


def test_vertical_core_is_source_supported_but_not_promoted():
    raw, proof = _load_outputs()
    core = next(obj for obj in proof["objects"] if obj["semantic_type"] == "vertical_core_region")
    assert len(core["source_references"]) == 3
    association = next(item for item in raw["semantic_associations"] if item["semantic_id"] == core["object_id"])
    assert association["ambiguity"] is True
    assert core["publish_status"] == "PUBLISH_BLOCKED"


def test_no_cross_deck_navigation_or_derived_relationship_claims():
    _, proof = _load_outputs()
    assert proof["cross_deck_relationships"] == []
    assert proof["navigation_graph"] is None
    assert proof["nearest_core_calculation"] is None
    assert proof["above_below_relations"] == []


def test_existing_synthetic_geometry_is_byte_for_byte_unchanged():
    actual = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((ROOT / "geometry").glob("deck*.geometry.json"))
    }
    assert actual == EXPECTED_SYNTHETIC_HASHES


def test_zero_candidate_is_unresolved():
    module = _load_script()
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], [])
    assert result["status"] == "UNRESOLVED"
    assert result["candidate_count"] == 0
    assert result["accepted_geometry"] is None


def test_exactly_one_candidate_is_accepted():
    module = _load_script()
    candidate = _candidate("drawing-one", [0, 0, 10, 10])
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], [candidate])
    assert result["status"] == "ACCEPTED"
    assert result["candidate_count"] == 1
    assert result["accepted_geometry"] == candidate


def test_two_enclosing_candidates_fail_closed_even_when_areas_differ():
    module = _load_script()
    candidates = [
        _candidate("drawing-small", [1, 1, 9, 9], 1),
        _candidate("drawing-large", [0, 0, 10, 10], 2),
    ]
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], candidates)
    assert result["status"] == "AMBIGUOUS"
    assert result["candidate_count"] == 2
    assert result["ambiguity"] is True
    assert result["accepted_geometry"] is None


def test_equal_area_candidates_fail_closed():
    module = _load_script()
    candidates = [
        _candidate("drawing-a", [0, 0, 10, 10], 1),
        _candidate("drawing-b", [0, 0, 10, 10], 2),
    ]
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], candidates)
    assert result["status"] == "AMBIGUOUS"
    assert result["accepted_geometry"] is None


def test_boundary_reference_point_is_excluded_by_fixed_epsilon():
    module = _load_script()
    candidate = _candidate("drawing-boundary", [5, 0, 10, 10])
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], [candidate])
    assert result["reference_point"] == [5.0, 5.0]
    assert result["status"] == "UNRESOLVED"
    assert result["containment_policy"]["epsilon_points"] == 0.01


def test_nearby_non_enclosing_geometry_is_not_selected():
    module = _load_script()
    nearby = _candidate("drawing-nearby", [5.02, 4, 9, 6])
    result = module.resolve_cabin_boundary_association("14001", [4, 4, 6, 6], [nearby])
    assert result["status"] == "UNRESOLVED"
    assert result["accepted_geometry"] is None


def test_duplicate_label_is_rejected():
    module = _load_script()
    try:
        module.require_unique_text_match("14001", [object(), object()])
    except RuntimeError as exc:
        assert "found 2" in str(exc)
    else:  # pragma: no cover - assertion branch
        raise AssertionError("duplicate selectable text must fail closed")


def test_unrelated_numeric_text_is_not_treated_as_a_proof_cabin():
    module = _load_script()
    candidate = _candidate("drawing-number", [0, 0, 10, 10])
    result = module.resolve_cabin_boundary_association("2025", [4, 4, 6, 6], [candidate])
    assert result["status"] == "REJECTED"
    assert result["accepted_geometry"] is None


def test_display_viewport_cannot_change_canonical_normalization():
    module = _load_script()
    _, proof = _load_outputs()
    bbox = [37.133801, 246.544495, 49.583801, 254.038498]
    before = module.normalize_bbox(bbox)
    original = module.REVIEW_VIEWPORT
    module.REVIEW_VIEWPORT = (0.0, 0.0, 10.0, 10.0)
    try:
        assert module.normalize_bbox(bbox) == before
    finally:
        module.REVIEW_VIEWPORT = original
    assert proof["review_viewport"]["classification"] == "DISPLAY_ONLY"
    assert proof["review_viewport"]["geometry_provenance"] is False


def test_raw_and_normalized_provenance_are_explicit_and_linked():
    raw, proof = _load_outputs()
    raw_by_reference = {item["source_reference"]: item for item in raw["geometry"]}
    assert all(item["geometry_provenance"] == "DIRECT_SOURCE_GEOMETRY" for item in raw["geometry"])
    for cabin in [obj for obj in proof["objects"] if obj["semantic_type"] == "cabin"]:
        assert cabin["geometry_provenance"] == "TRANSFORMED_SOURCE_GEOMETRY"
        source = cabin["source_geometry"]
        assert raw_by_reference[source["source_reference"]]["drawing_index"] == source["drawing_index"]
        assert raw_by_reference[source["source_reference"]]["sequence_number"] == source["sequence_number"]
        assert raw_by_reference[source["source_reference"]]["source_bbox"] == source["source_bbox"]
