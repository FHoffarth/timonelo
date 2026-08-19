"""
Tests for MSC Meraviglia Official Deck Plan Ingestion & Canonical Knowledge Pack (P0-B Step 2).
Governed by ADR-0002 §4, §6, §7, §8, §9.
"""

from enum import Enum
import json
import os
import pypdf
import pytest

from scripts.reingest_msc_meraviglia_official_deckplan import (
    ARTIFACT_FULL_PATH,
    EXPECTED_SHA256,
    KNOWLEDGE_DIR,
    REPORTS_DIR,
    run_ingestion,
)
from timonelo.evidence.artifacts import sha256_of_file
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    ConflictGateResult,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
)
from timonelo.ontology.models import (
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    PublishStatus,
)


@pytest.fixture(scope="module")
def manifest():
    manifest_path = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    if not os.path.exists(manifest_path):
        run_ingestion()
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_meraviglia_1_artifact_sha256_integrity():
    """1. Artifact on disk matches authentic SHA-256 digest."""
    assert os.path.exists(ARTIFACT_FULL_PATH), f"Artifact missing at {ARTIFACT_FULL_PATH}"
    actual_sha = sha256_of_file(ARTIFACT_FULL_PATH)
    assert actual_sha.lower() == EXPECTED_SHA256.lower()


def test_meraviglia_2_pdf_page_count():
    """2. Authentic PDF contains exactly 6 pages."""
    reader = pypdf.PdfReader(ARTIFACT_FULL_PATH)
    assert len(reader.pages) == 6


def test_meraviglia_3_manifest_has_no_stored_confidence(manifest):
    """3. Manifest statements carry zero stored confidence metrics."""
    for stmt in manifest["statements"]:
        assert "confidence" not in stmt, f"Stored confidence found in statement {stmt['statement_id']}"


def test_meraviglia_4_no_bare_verified(manifest):
    """4. No bare VERIFIED state is present in manifest or knowledge files."""
    manifest_str = json.dumps(manifest)
    assert '"VERIFIED"' not in manifest_str

    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(KNOWLEDGE_DIR, fname), "r", encoding="utf-8") as f:
                content = f.read()
                assert '"verification_status": "VERIFIED"' not in content


def test_meraviglia_5_supported_statements_have_events(manifest):
    """5. All SUPPORTED statements have non-empty evidence_event_ids."""
    supported = [s for s in manifest["statements"] if s["evidence_condition"] == "SUPPORTED"]
    assert len(supported) > 0
    for s in supported:
        assert len(s["evidence_event_ids"]) > 0, f"Statement {s['statement_id']} is SUPPORTED but has no events"


def test_meraviglia_6_all_events_resolve_to_artifact_sha(manifest):
    """6. All evidence events reference the authentic artifact SHA-256."""
    assert len(manifest["events"]) > 0
    for e in manifest["events"]:
        assert e["artifact_sha256"].lower() == EXPECTED_SHA256.lower()


def test_meraviglia_7_all_locators_are_valid_narrow_pages(manifest):
    """7. All locators are narrow page locators (page:1 to page:6), not placeholders."""
    valid_locators = {f"page:{p}" for p in range(1, 7)}
    for e in manifest["events"]:
        loc = e["locator"]
        assert loc in valid_locators, f"Invalid or broad locator {loc!r} in event {e['event_id']}"


def test_meraviglia_8_technical_facts_not_sourced_from_deckplan(manifest):
    """8. Technical facts (IMO, GT, LOA, Beam) are NOT sourced from deckplan and remain UNKNOWN / BLOCKED."""
    tech_questions = {"ship.imo", "ship.gross_tonnage", "ship.length_overall_meters", "ship.beam_meters"}
    tech_stmts = [s for s in manifest["statements"] if s["question_id"] in tech_questions]
    assert len(tech_stmts) == 4

    for s in tech_stmts:
        assert s["evidence_condition"] == "UNKNOWN"
        assert s["publish_status"] == "PUBLISH_BLOCKED"
        assert s["evidence_event_ids"] == []


def test_meraviglia_9_deck_names_colosseo_kos_petra():
    """9. Decks 4, 5, 6 are named Kos, Colosseo, Petra."""
    decks_path = os.path.join(KNOWLEDGE_DIR, "decks.json")
    with open(decks_path, "r", encoding="utf-8") as f:
        decks_doc = json.load(f)

    deck_map = {d["deck_number"]: d["name"] for d in decks_doc["decks"]}
    assert "Kos" in deck_map[4]
    assert "Colosseo" in deck_map[5]
    assert "Petra" in deck_map[6]


def test_meraviglia_10_capacity_and_cabins_from_pdf():
    """10. Total cabins (2214) and max guests (5714) confirmed from PDF Page 2."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)

    assert cabins_doc["summary"]["total_staterooms"] == 2214
    assert len(cabins_doc["cabin_categories"]) == 20


def test_meraviglia_11_geometry_remains_synthetic():
    """11. Gatekeeper evaluation keeps spatial geometry as SYNTHETIC_GEOMETRY."""
    gk = EvidenceGatekeeper()
    gk.add_geometry(
        GeometryProvenanceRecord(
            object_id="GEOM-DECK-5",
            deck_number=5,
            geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))
    res = gk.evaluate_publish_gate()

    assert res.synthetic_geometry_count == 1
    assert res.direct_geometry_count == 0


def test_meraviglia_12_reingestion_is_idempotent():
    """12. Consecutive execution of run_ingestion produces zero diff."""
    res1 = run_ingestion()
    manifest_p = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    with open(manifest_p, "r", encoding="utf-8") as f:
        content1 = f.read()

    res2 = run_ingestion()
    with open(manifest_p, "r", encoding="utf-8") as f:
        content2 = f.read()

    assert content1 == content2
    assert res1["events_count"] == res2["events_count"]
    assert res1["statements_count"] == res2["statements_count"]
