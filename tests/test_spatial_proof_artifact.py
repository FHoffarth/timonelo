"""
Guards the shipped copy of the Deck 14 geometry proof.

The viewer under `frontend/src/spatial-proof/` renders
`frontend/public/data/deck14.proof.json`, which is a build-time copy of the
canonical artifact. A copy can drift from its origin silently, and a viewer
rendering a stale proof would misrepresent the evidence while looking correct.

This asserts byte identity, not semantic equality: the canonical artifact is
digest-asserted elsewhere, so anything less than byte-for-byte would leave a gap.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = REPO_ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.proof.json"
SHIPPED = REPO_ROOT / "frontend" / "public" / "data" / "deck14.proof.json"


def test_shipped_proof_is_byte_identical_to_canonical():
    assert CANONICAL.is_file(), "canonical Deck 14 proof is missing"
    assert SHIPPED.is_file(), "shipped Deck 14 proof is missing"

    canonical = CANONICAL.read_bytes()
    shipped = SHIPPED.read_bytes()

    assert hashlib.sha256(shipped).hexdigest() == hashlib.sha256(canonical).hexdigest(), (
        "frontend/public/data/deck14.proof.json has drifted from the canonical "
        "artifact. Re-copy it; do not edit the shipped copy."
    )
    assert shipped == canonical


def test_shipped_proof_still_refuses_connectivity():
    """The viewer's refusal state is only honest while the artifact refuses too."""
    doc = json.loads(SHIPPED.read_text(encoding="utf-8"))

    assert doc["schema"] == "timonelo.one-deck-geometry-proof.v1"
    assert doc["deck"]["number"] == 14
    assert len(doc["objects"]) == 11

    assert doc["navigation_graph"] is None
    assert doc["nearest_core_calculation"] is None
    assert doc["corridor_observation"]["accepted_geometry"] is False
    assert doc["corridor_observation"]["geometry"] is None
    assert doc["cross_deck_relationships"] == []
    assert doc["above_below_relations"] == []
    assert doc["port_starboard_associations"] == []


def test_shipped_proof_carries_no_metric_scale():
    """No viewer may display metres, because the artifact establishes none."""
    doc = json.loads(SHIPPED.read_text(encoding="utf-8"))
    assert doc["transform"]["target_units"] == "normalized fraction of PDF page MediaBox"
    assert doc["review_viewport"]["classification"] == "DISPLAY_ONLY"
    assert doc["review_viewport"]["semantic"] is False


def test_viewer_does_not_read_the_display_only_overlay():
    """`deck14.review.png` is cropped to a hand-picked viewport and is not a frame."""
    source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (REPO_ROOT / "frontend" / "src" / "spatial-proof").glob("*.ts*")
    )
    # The check is on USE, not on mention. Both the overlay and the viewport are
    # named in prose explaining why they are excluded, and flagging that prose
    # would penalise the documentation for describing the exclusion.
    assert "<image" not in source
    assert 'src="/data/deck14.review' not in source
    assert "url(/data/deck14.review" not in source
    assert ".review_viewport" not in source
    assert "review_viewport[" not in source


def test_viewer_uses_no_legacy_synthetic_geometry():
    source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (REPO_ROOT / "frontend" / "src" / "spatial-proof").glob("*.ts*")
    )
    assert "geometry.json" not in source
    assert "deck14.geometry" not in source
