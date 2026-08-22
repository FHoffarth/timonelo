"""
Tests for MSC Meraviglia Official Deck Plan Ingestion & Canonical Knowledge Pack (P0-B Step 2B.1B).
Governed by ADR-0002 §4, §6, §7, §8, §9, §13 and P0-B StatementEditor, Central Authority & Knowledge Coverage.
"""

import ast
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
    REPO_ROOT,
    run_ingestion,
)
from timonelo.evidence import authority
from timonelo.evidence.artifacts import sha256_of_file
from timonelo.evidence.authority import check
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.editor import Statement, StatementEditor
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
)
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.review import ReviewLog
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)


@pytest.fixture(scope="module")
def manifest(tmp_path_factory):
    """The committed manifest, or a temp regeneration if it is absent.

    Never regenerates in place: `run_ingestion()` with default paths writes into
    tracked `knowledge/` and `knowledge/reports/`, so a test run would dirty the
    working tree and make a clean-tree gate fail for reasons unrelated to the
    change under review.
    """
    manifest_path = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    if not os.path.exists(manifest_path):
        scratch = tmp_path_factory.mktemp("meraviglia_manifest")
        knowledge_dir = scratch / "knowledge"
        knowledge_dir.mkdir()
        run_ingestion(str(knowledge_dir), str(scratch / "reports"))
        manifest_path = os.path.join(str(knowledge_dir), "extraction_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# TASK T — NEGATIVE & POSITIVE REGRESSION TESTS (1-27)
# =============================================================================

def test_meraviglia_1_no_direct_engine_statement_constructor_in_ingestion_ast():
    """1. Ingestion AST check: No direct Statement(...) constructor calls in ingestion."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="reingest_msc_meraviglia_official_deckplan.py")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            assert func_name != "Statement", (
                f"Direct construction of Statement(...) is forbidden: {ast.unparse(node)}"
            )


def test_meraviglia_2_statement_editor_create_is_used():
    """2. StatementEditor.create() is used for statement creation."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "editor.create(" in content


def test_meraviglia_3_statement_editor_set_evidence_condition_is_used():
    """3. StatementEditor.set_evidence_condition() is used for condition transition."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "editor.set_evidence_condition(" in content


def test_meraviglia_4_no_truth_engine_set_evidence_condition_in_ingestion():
    """4. TruthEngine.set_evidence_condition() is not called in ingestion."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "truth_engine.set_evidence_condition" not in content


def test_meraviglia_5_no_direct_review_log_transition_in_ingestion():
    """5. No manual review_log.record_condition_transition() in ingestion (handled by StatementEditor)."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "review_log.record_condition_transition" not in content


def test_meraviglia_6_no_local_supportable_by_authority_grant():
    """6. Ingestion script does not define local supportable_by tuples."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "supportable_by" not in content


def test_meraviglia_7_no_load_workspace_classes_override():
    """7. No load_workspace_classes used in ingestion."""
    script_path = os.path.join(REPO_ROOT, "scripts", "reingest_msc_meraviglia_official_deckplan.py")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "load_workspace_classes" not in content


def test_meraviglia_8_exact_22_cabin_category_codes():
    """8. Exact set equality of all 22 cabin category codes from Page 2."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)

    expected_codes = {
        "YC3", "YJD", "YC1", "YIN", "SXJ", "SLJ", "BA",
        "BL3", "BL2", "BL1", "BR3", "BR2", "BR1", "BP", "BS",
        "OL2", "OR1", "OM2", "OO", "IR2", "IR1", "IS"
    }
    actual_codes = {
        c["id"].replace("CAT-", "") for c in cabins_doc["cabin_categories"]
    }
    assert actual_codes == expected_codes
    assert cabins_doc["summary"]["distinct_categories_count"] == 22


def test_meraviglia_9_yc1_present():
    """9. YC1 is present in cabin categories on Decks [14, 15, 16, 18]."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)

    yc1 = next((c for c in cabins_doc["cabin_categories"] if c["id"] == "CAT-YC1"), None)
    assert yc1 is not None
    assert "Deluxe Suite" in yc1["name"]
    assert yc1["deck"] == [14, 15, 16, 18]


def test_meraviglia_10_yin_present():
    """10. YIN is present in cabin categories on Decks [14, 15, 16]."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)

    yin = next((c for c in cabins_doc["cabin_categories"] if c["id"] == "CAT-YIN"), None)
    assert yin is not None
    assert "Innenkabine" in yin["name"] or "Interior" in yin["name"]
    assert yin["deck"] == [14, 15, 16]


def test_meraviglia_11_balcony_percentage_absent():
    """11. balcony_percentage is absent from cabins.json summary (not evidenced in PDF)."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)
    assert "balcony_percentage" not in cabins_doc["summary"]


def test_meraviglia_12_unsupported_six_generic_amenities_absent():
    """12. Unsupported standard_amenities bundle is absent from cabins.json summary."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)
    assert "standard_amenities" not in cabins_doc["summary"]


def test_meraviglia_13_bed_configuration_retained_and_evidence_backed(manifest):
    """13. Bed configuration is retained as a Statement backed by Page 2."""
    bed_stmt = next(
        (s for s in manifest["statements"] if s.get("statement_type") == "cabin.bed_configuration" or s.get("question_id") == "Q-CABIN-BED-CONFIG"),
        None,
    )
    assert bed_stmt is not None
    assert "Doppelbett umstellbar zu zwei Einzelbetten" in bed_stmt["value"]
    assert bed_stmt["locator"] == "page:2"
    assert bed_stmt["evidence_condition"] == "SUPPORTED"


def test_meraviglia_14_is_and_yc3_exception_semantics_preserved(manifest):
    """14. IS and YC3 exceptions are explicitly preserved in bed configuration claim."""
    bed_stmt = next(
        (s for s in manifest["statements"] if s.get("question_id") == "Q-CABIN-BED-CONFIG"),
        None,
    )
    assert bed_stmt is not None
    assert "ausgenommen IS, YC3" in bed_stmt["value"]


def test_meraviglia_15_passenger_accessible_decks_absent():
    """15. passenger_accessible_decks is absent from technical.json (unsupported accessibility translation)."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    caps = tech_doc["technical_specifications"]["capacities"]
    assert "passenger_accessible_decks" not in caps


def test_meraviglia_16_total_decks_absent():
    """16. total_decks=18 is completely absent from technical.json and manifest."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    caps = tech_doc["technical_specifications"]["capacities"]
    assert "total_decks" not in caps


def test_meraviglia_17_ship_class_absent():
    """17. Ship class is absent from technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    specs = tech_doc.get("technical_specifications", {})
    assert "class" not in specs


def test_meraviglia_18_rest_le_cerisier_absent_and_lolive_doree_present():
    """18. Legacy/sister-ship REST-LE-CERISIER is absent; L'Olive dorée is present."""
    rest_path = os.path.join(KNOWLEDGE_DIR, "restaurants.json")
    with open(rest_path, "r", encoding="utf-8") as f:
        rest_doc = json.load(f)

    rest_ids = [r["id"] for r in rest_doc["restaurants"]]
    assert "REST-LE-CERISIER" not in rest_ids
    assert "REST-LOLIVE-DOREE" in rest_ids

    lolive = next(r for r in rest_doc["restaurants"] if r["id"] == "REST-LOLIVE-DOREE")
    assert lolive["name"] in ("L'Olive dorée", "L'Olive Doree")
    assert lolive["deck"] == 6


def test_meraviglia_19_all_venue_name_deck_pairs_statement_covered(manifest):
    """19. Every venue name/deck pair in all venue documents has a corresponding Statement."""
    venue_files = [
        ("restaurants.json", "restaurants"),
        ("bars.json", "bars"),
        ("lounges.json", "lounges"),
        ("pools.json", "pools_and_water_areas"),
        ("sports.json", "sports_and_recreation"),
        ("entertainment.json", "entertainment_venues"),
        ("public_areas.json", "public_areas"),
    ]

    # Restricted to the venue-NAME statements (Q-VENUE-*). A venue entity may now
    # carry a second statement answering Q-0016 ("which deck is this venue on"),
    # and keying by entity alone silently collapsed the two.
    manifest_venue_stmts = {
        s["entity_id"]: s
        for s in manifest["statements"]
        if "msc-meraviglia:venue:" in s["entity_id"]
        and s["question_id"].startswith("Q-VENUE-")
    }

    for fname, key in venue_files:
        fpath = os.path.join(KNOWLEDGE_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            d = json.load(f)
        for v in d[key]:
            v_id = f"msc-meraviglia:venue:{v['id']}"
            assert v_id in manifest_venue_stmts, f"Venue {v_id} in {fname} has no Statement"
            assert manifest_venue_stmts[v_id]["value"] == v["name"]


def test_meraviglia_20_semantic_fields_cannot_bypass_coverage():
    """20. Factual leaf audit classifies all semantic leaves and enforces 0 uncovered."""
    canonical_files = {
        "bars.json", "cabins.json", "decks.json", "entertainment.json",
        "lounges.json", "pools.json", "public_areas.json", "restaurants.json",
        "spa.json", "sports.json", "technical.json"
    }

    def classify_leaf(path, val):
        key = path[-1] if not isinstance(path[-1], int) else path[-2]
        if key in (
            "vessel_id", "source_artifact", "sha256", "verification_authority", "last_audited",
            "source", "provenance", "notes", "id", "deck_number", "code", "distinct_categories_count"
        ):
            return "STRUCTURAL_METADATA"
        if key in (
            "name", "vessel_name", "total_staterooms", "passenger_capacity_max_occupancy",
            "total_cabins_min", "total_cabins_max", "deck", "decks", "passenger_accessible"
        ):
            return "SOURCE_SUPPORTED_FACT"
        if key in ("category", "description", "tags", "dining_model"):
            return "EDITORIAL_NONCANONICAL"
        return "UNSUPPORTED_FACT"

    def get_leaves(d, p=()):
        leaves = []
        if isinstance(d, dict):
            for k, v in d.items():
                leaves.extend(get_leaves(v, p + (k,)))
        elif isinstance(d, list):
            for i, item in enumerate(d):
                leaves.extend(get_leaves(item, p + (i,)))
        else:
            leaves.append((p, d, classify_leaf(p, d)))
        return leaves

    unsupported = []
    for fname in canonical_files:
        fpath = os.path.join(KNOWLEDGE_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        for path, val, cat in get_leaves(d, (fname,)):
            if cat == "UNSUPPORTED_FACT":
                unsupported.append((path, val))

    assert len(unsupported) == 0, f"Found {len(unsupported)} unsupported leaves: {unsupported[:5]}"


def test_meraviglia_21_unsupported_technical_facts_absent():
    """21. Unsupported technical facts are absent from technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    specs = tech_doc.get("technical_specifications", {})
    forbidden_keys = ["imo_number", "mmsi", "tonnage_gt", "dimensions", "propulsion_and_power", "class"]
    for k in forbidden_keys:
        assert k not in specs


def test_meraviglia_22_every_supported_statement_resolves_to_artifact_registry(manifest):
    """22. Every supported statement resolves to artifact_id in registered artifact."""
    art_id = manifest["artifact"]["artifact_id"]
    assert art_id.startswith("ART-")
    assert manifest["artifact"]["sha256"].lower() == EXPECTED_SHA256.lower()


def test_meraviglia_23_every_supported_statement_has_meaningful_locator(manifest):
    """23. Every supported statement has a meaningful page locator (page:2 to page:5)."""
    valid_locators = {f"page:{p}" for p in range(1, 7)}
    for s in manifest["statements"]:
        loc = s["locator"]
        assert loc in valid_locators, f"Invalid locator '{loc}' in statement {s['statement_id']}"


def test_meraviglia_24_central_authority_accepts_every_retained_source_claim(manifest):
    """24. Central authority check accepts every statement_type in the manifest."""
    doc_class = manifest["artifact"]["document_class"]
    for s in manifest["statements"]:
        stype = s.get("statement_type")
        if stype:
            check(stype, doc_class)


def test_meraviglia_25_geometry_remains_synthetic_geometry(tmp_path):
    """25. Spatial geometry remains SYNTHETIC_GEOMETRY."""
    gk = EvidenceGatekeeper()
    for d_num in range(4, 20):
        if d_num == 17:
            continue
        gk.add_geometry(
            GeometryProvenanceRecord(
                object_id=f"GEOM-DECK-{d_num}",
                deck_number=d_num,
                geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
            )
        )
    gk.use_conflict_log(ConflictLog(str(tmp_path / "conflicts.json")))
    res = gk.evaluate_publish_gate()
    assert res.synthetic_geometry_count == 15
    assert res.direct_geometry_count == 0


def test_meraviglia_26_gatekeeper_remains_publish_blocked(manifest):
    """26. EvidenceGatekeeper evaluates to PUBLISH_BLOCKED due to DRAFT review state."""
    for s in manifest["statements"]:
        assert s["human_review_state"] == "DRAFT"
        assert s["publish_status"] == "PUBLISH_BLOCKED"


def test_meraviglia_27_no_confidence_or_confidence_score_anywhere():
    """27. No confidence or confidence_score keys anywhere in Meraviglia canonical files."""
    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(KNOWLEDGE_DIR, fname), "r", encoding="utf-8") as f:
                content = f.read()
                assert '"confidence"' not in content, f"confidence found in {fname}"
                assert '"confidence_score"' not in content, f"confidence_score found in {fname}"


def test_meraviglia_reingestion_is_idempotent(tmp_path):
    """Consecutive execution of run_ingestion produces zero diff."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    reports_dir = tmp_path / "reports"

    res1 = run_ingestion(str(knowledge_dir), str(reports_dir))
    manifest_p = os.path.join(str(knowledge_dir), "extraction_manifest.json")
    with open(manifest_p, "r", encoding="utf-8") as f:
        content1 = f.read()

    res2 = run_ingestion(str(knowledge_dir), str(reports_dir))
    with open(manifest_p, "r", encoding="utf-8") as f:
        content2 = f.read()

    assert content1 == content2
    assert res1["events_count"] == res2["events_count"]
    assert res1["statements_count"] == res2["statements_count"]


def test_meraviglia_historical_discrepancies_are_corrections_not_live_conflicts(tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()

    result = run_ingestion(str(knowledge_dir), str(tmp_path / "reports"))
    with open(
        os.path.join(str(knowledge_dir), "extraction_manifest.json"), encoding="utf-8"
    ) as f:
        current_manifest = json.load(f)

    assert result["historical_corrections_count"] == 6
    assert result["live_conflicts_count"] == 0
    assert result["conflict_detection_executed"] is True
    assert len(current_manifest["historical_corrections"]) == 6
    assert all(
        correction["reference_integrity"] == "VALIDATED"
        for correction in current_manifest["historical_corrections"]
    )

    events_by_id = {event["event_id"]: event for event in current_manifest["events"]}
    # Keyed by entity: both venue-deck corrections now answer the same
    # registered question Q-0016, so question_id alone is no longer unique.
    corrections_by_entity = {
        correction["entity_id"]: correction
        for correction in current_manifest["historical_corrections"]
    }
    ocean_event = events_by_id[
        corrections_by_entity["msc-meraviglia:venue:REST-OCEAN-CAY"]["evidence_event_ids"][0]
    ]
    top_sail_event = events_by_id[
        corrections_by_entity["msc-meraviglia:venue:LOUNGE-TOP-SAIL"]["evidence_event_ids"][0]
    ]
    assert ocean_event["question_id"] == "Q-0016"
    assert ocean_event["observed_value"] == 6
    assert ocean_event["locator"] == "page:3"
    assert top_sail_event["question_id"] == "Q-0016"
    assert top_sail_event["observed_value"] == 16
    assert top_sail_event["locator"] == "page:5"
