"""End-to-end guards for the legacy/schematic -> passenger trust boundary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_legacy_semantic_dataset_is_explicitly_schematic_at_frontend_ingress():
    client = read("frontend/src/semantic-deck/apiClient.ts")
    assert "...LEGACY_SCHEMATIC_ADMISSION" in client
    assert "mean_confidence: null" in client
    assert "confidence_avg || 0.99" not in client


def test_cabin_deep_dive_has_no_manufactured_verified_entity():
    page = read("frontend/src/components/pages/CabinDeepDivePage.tsx")
    forbidden = (
        'epistemic_state: "DIRECT"',
        'review_state: "PUBLISHED_VERIFIED"',
        "confidence: 0.95",
        "parseInt(cabinId) - 2",
        "parseInt(cabinId) + 2",
        'connected_vertical_core: "Midship Lift Bank B"',
        'CANONICAL_CABINS["14122"]',
    )
    for value in forbidden:
        assert value not in page
    assert "isPassengerEntityAdmitted" in page


def test_unsupported_14122_briefing_was_removed_from_frontend_canonical_map():
    data = read("frontend/src/data/canonicalPlatformData.ts")
    assert '"14122": {' not in data
    assert "PRM-accessible Deluxe Interior" not in data
    assert "STM-BEL-14122-PRM" not in data


def test_missing_confidence_has_no_passenger_numeric_fallback():
    engine = read("frontend/src/intelligence/CabinIntelligenceEngine.ts")
    assert "entity.confidence ||" not in engine
    assert "entity.confidence ??" not in engine
    assert "epistemic_confidence: entity.confidence" not in engine


def test_schematic_renderer_declares_null_physical_semantics():
    renderer = read("frontend/src/semantic-deck/renderer/DeckRenderer.tsx")
    assert "Schematic layout only" in renderer
    for term in ("Position", "size", "orientation", "distance", "adjacency", "lift connectivity"):
        assert term.lower() in renderer.lower()


def test_cabin_14122_proof_remains_source_derived_but_unadmitted_and_unroutable():
    proof = json.loads(
        read("geometry/proofs/bellissima/deck14/deck14.proof.json")
    )
    cabin = next(o for o in proof["objects"] if o.get("cabin_number") == "14122")

    assert cabin["geometry_provenance"] == "TRANSFORMED_SOURCE_GEOMETRY"
    assert cabin["evidence_condition"] == "UNKNOWN"
    assert cabin["human_review_state"] == "DRAFT"
    assert cabin["publish_status"] == "PUBLISH_BLOCKED"
    assert proof["navigation_graph"] is None
    assert proof["nearest_core_calculation"] is None
    assert proof["port_starboard_associations"] == []
    assert proof["cross_deck_relationships"] == []
    assert proof["above_below_relations"] == []


def test_legacy_direct_label_cannot_become_prov_or_bot_truth_export():
    client = read("frontend/src/semantic-deck/apiClient.ts")
    assert (
        "const admitted = isPassengerEntityAdmitted(entity, this.activeVesselId)"
        in client
    )
    assert "BOT topology unavailable" in client
    assert "Provenance unavailable" in client
