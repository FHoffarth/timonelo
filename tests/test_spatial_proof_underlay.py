"""
Guards the Deck 14 source-plan underlay asset and its provenance record.

The underlay is a raster of the source deck plan shown beneath the accepted proof
geometry. It is visual context and never evidence — page 5 carries 243 Deck-14
cabin labels while the proof accepts 10, so with the layer on, most of what a
reader sees is unproven.

That makes the provenance record load-bearing: it is the only place recording
which bytes the raster came from, at what frame, and that it carries no
geometric authority. These tests keep the asset, the record and the live source
in agreement.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import struct

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PNG = REPO_ROOT / "frontend" / "public" / "data" / "deck14.page5.png"
PROV = REPO_ROOT / "frontend" / "public" / "data" / "deck14.page5.provenance.json"
SOURCE_SHA = "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"
VAULT = REPO_ROOT / "evidence" / "raw" / "sha256" / "08" / f"{SOURCE_SHA}.pdf"


def _png_size(path: pathlib.Path) -> tuple[int, int]:
    """Read dimensions from the IHDR chunk, without an image library."""
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _prov() -> dict:
    return json.loads(PROV.read_text(encoding="utf-8"))


def test_asset_and_provenance_record_exist():
    assert PNG.is_file(), "underlay raster is missing"
    assert PROV.is_file(), "underlay provenance record is missing"


def test_png_dimensions_match_declared_provenance():
    prov = _prov()
    assert _png_size(PNG) == (prov["render"]["width_px"], prov["render"]["height_px"])


def test_png_digest_matches_declared_provenance():
    assert hashlib.sha256(PNG.read_bytes()).hexdigest() == _prov()["output_sha256"]


def test_source_sha_recorded_correctly_and_still_held():
    prov = _prov()
    assert prov["source"]["sha256"] == SOURCE_SHA
    assert prov["source"]["artifact_id"] == "ART-0001"
    assert prov["source"]["pdf_page_number"] == 5
    assert VAULT.is_file(), "source artifact is not in the canonical vault"
    assert hashlib.sha256(VAULT.read_bytes()).hexdigest() == SOURCE_SHA


def test_aspect_matches_live_mediabox_within_tolerance():
    """A raster whose aspect drifts from the page would misalign the geometry."""
    fitz = __import__("fitz")
    doc = fitz.open(VAULT)
    try:
        page = doc[4]
        live_w, live_h = page.rect.width, page.rect.height
        assert page.rotation == 0
        assert page.cropbox == page.mediabox
    finally:
        doc.close()

    prov = _prov()
    assert prov["frame"]["page_width_points"] == live_w
    assert prov["frame"]["page_height_points"] == live_h

    width, height = _png_size(PNG)
    # One pixel of rounding at either edge is the whole budget.
    assert abs(width / height - live_w / live_h) < 1e-3
    assert abs(width - live_w * prov["render"]["zoom"]) <= 1
    assert abs(height - live_h * prov["render"]["zoom"]) <= 1


def test_provenance_declares_full_mediabox_and_no_crop():
    frame = _prov()["frame"]
    assert frame["full_mediabox"] is True
    assert frame["cropped"] is False
    assert frame["review_viewport_used"] is False, (
        "the review viewport is DISPLAY_ONLY and must never frame a render"
    )
    assert frame["cropbox_equals_mediabox"] is True
    assert frame["rotation_degrees"] == 0


def test_provenance_declares_context_only_semantics():
    prov = _prov()
    assert prov["purpose"] == "visual context only; not canonical geometry"
    semantics = prov["semantics"]
    assert semantics["is_canonical_geometry"] is False
    assert semantics["carries_geometry_provenance"] is False
    assert semantics["hit_testable"] is False
    assert semantics["implies_connectivity"] is False
    assert semantics["implies_metric_scale"] is False


def test_renderer_is_recorded_reproducibly():
    render = _prov()["render"]
    assert render["renderer"] == "PyMuPDF"
    assert render["pymupdf_version"] and render["mupdf_version"]
    assert "get_pixmap" in render["command"] and "alpha=False" in render["command"]
    assert render["dpi"] == round(72 * render["zoom"])


def test_underlay_is_never_treated_as_proof_geometry():
    source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (REPO_ROOT / "frontend" / "src" / "spatial-proof").glob("*.ts*")
    )
    # The raster must not be pickable, and must carry no provenance attribute.
    assert "pointerEvents: \"none\"" in source
    assert 'data-layer="source-context"' in source
    # Hit-testing still reads only the proof's own bboxes.
    assert "normalized_bbox" in source
    assert "deck14.page5.png" not in source.replace(
        'export const UNDERLAY_HREF = "/data/deck14.page5.png";', ""
    ), "the raster path should be declared once, not scattered"
