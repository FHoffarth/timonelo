"""
Tests for MSC Meraviglia Official Deck Plan Ingestion & Canonical Knowledge Pack (P0-B Step 2B.1).
Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-B Evidence Hygiene.
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
from timonelo.evidence.engine import Statement
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    ConflictGateResult,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
)
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)


@pytest.fixture(scope="module")
def manifest():
    manifest_path = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    if not os.path.exists(manifest_path):
        run_ingestion()
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# TASK M — NEGATIVE & POSITIVE TEST MATRIX (20 REQUIREMENTS)
# =============================================================================

def test_meraviglia_1_no_confidence_or_confidence_score_exists(manifest):
    """1. No confidence or confidence_score keys exist in manifest or canonical files."""
    for stmt in manifest["statements"]:
        assert "confidence" not in stmt, f"confidence found in statement {stmt['statement_id']}"
        assert "confidence_score" not in stmt, f"confidence_score found in statement {stmt['statement_id']}"

    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(KNOWLEDGE_DIR, fname), "r", encoding="utf-8") as f:
                content = f.read()
                assert '"confidence"' not in content, f"confidence found in {fname}"
                assert '"confidence_score"' not in content, f"confidence_score found in {fname}"


def test_meraviglia_2_unsupported_technical_facts_are_absent():
    """2. Unsupported technical facts (IMO, GT, LOA, Beam, Propulsion, Crew) are absent in technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    specs = tech_doc.get("technical_specifications", {})
    unsupported_keys = [
        "imo_number", "mmsi", "call_sign", "builder", "cost_to_build",
        "key_milestones", "port_of_registry", "flag_state", "tonnage_gt",
        "dimensions", "propulsion_and_power", "connectivity_and_smart_systems",
        "environmental_features"
    ]
    for k in unsupported_keys:
        assert k not in specs, f"Unsupported technical spec '{k}' must be absent from technical.json"

    # Also verify inside capacities that unsupported crew counts are absent
    capacities = specs.get("capacities", {})
    assert "crew_capacity_min" not in capacities
    assert "crew_capacity_max" not in capacities
    assert "passenger_capacity_double_occupancy" not in capacities


def test_meraviglia_3_no_fake_or_null_sha_used_for_technical_claims():
    """3. No fake/null SHA (e.g. 0000...0000) is used in technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    sha = tech_doc["provenance"]["sha256"]
    assert sha.lower() == EXPECTED_SHA256.lower()
    assert sha != "0000000000000000000000000000000000000000000000000000000000000000"


def test_meraviglia_4_all_supported_statements_have_evidence_events(manifest):
    """4. All SUPPORTED statements have non-empty evidence_event_ids."""
    supported = [s for s in manifest["statements"] if s["evidence_condition"] == "SUPPORTED"]
    assert len(supported) > 0
    for s in supported:
        assert len(s["evidence_event_ids"]) > 0, f"Statement {s['statement_id']} is SUPPORTED but has no events"


def test_meraviglia_5_all_events_resolve_to_artifact_sha(manifest):
    """5. All evidence events reference the authentic artifact SHA-256."""
    assert len(manifest["events"]) > 0
    for e in manifest["events"]:
        assert e["artifact_sha256"].lower() == EXPECTED_SHA256.lower()


def test_meraviglia_6_all_locators_are_meaningful(manifest):
    """6. All locators are narrow page locators (page:1 to page:6), not placeholders."""
    valid_locators = {f"page:{p}" for p in range(1, 7)}
    for e in manifest["events"]:
        loc = e["locator"]
        assert loc in valid_locators, f"Invalid or broad locator {loc!r} in event {e['event_id']}"


def test_meraviglia_7_all_source_supported_facts_use_eligible_document_class(manifest):
    """7. All source-supported facts use eligible document class (cruise_line_deck_plan)."""
    assert manifest["artifact"]["document_class"] == "cruise_line_deck_plan"


def test_meraviglia_8_statements_begin_fail_closed():
    """8. Statements begin fail-closed in UNKNOWN, DRAFT, and PUBLISH_BLOCKED."""
    stmt = Statement(
        statement_id="STMT-TEST",
        entity_id="msc-meraviglia",
        question_id="Q-TEST",
        value="test",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
    )
    assert stmt.evidence_condition == EvidenceCondition.UNKNOWN
    assert stmt.human_review_state == HumanReviewState.DRAFT
    assert stmt.publish_status == PublishStatus.PUBLISH_BLOCKED


def test_meraviglia_9_support_requires_recorded_transition(manifest):
    """9. Promotion to SUPPORTED requires an explicit recorded transition in audit log."""
    assert "audit_log" in manifest
    assert len(manifest["audit_log"]) > 0
    for entry in manifest["audit_log"]:
        assert entry["transition"] == "CONDITION:UNKNOWN -> CONDITION:SUPPORTED"
        assert entry["from_condition"] == "UNKNOWN"
        assert entry["to_condition"] == "SUPPORTED"
        assert entry["actor"] == "deckplan_evidence_verifier"
        assert entry["occurred_on"] == "2026-08-19"


def test_meraviglia_10_approval_requires_recorded_transition(manifest):
    """10. Human review states remain DRAFT when no live human curation session occurs."""
    for s in manifest["statements"]:
        assert s["human_review_state"] == "DRAFT"


def test_meraviglia_11_publication_requires_recorded_transition(manifest):
    """11. Publication status remains PUBLISH_BLOCKED while statements are in DRAFT."""
    for s in manifest["statements"]:
        assert s["publish_status"] == "PUBLISH_BLOCKED"


def test_meraviglia_12_automation_actor_not_mislabeled_human(manifest):
    """12. Automation actors describe pipeline honestly (no fake human_curator)."""
    for e in manifest["events"]:
        assert e["observed_by"] == "deckplan_extraction_pipeline"
    for entry in manifest["audit_log"]:
        assert entry["actor"] == "deckplan_evidence_verifier"


def test_meraviglia_13_unsupported_factual_leaf_coverage_zero():
    """13. Unsupported factual leaf count is exactly zero across all canonical files."""
    canonical_files = {
        "bars.json", "cabins.json", "decks.json", "entertainment.json",
        "lounges.json", "pools.json", "public_areas.json", "restaurants.json",
        "spa.json", "sports.json", "technical.json"
    }

    def classify_leaf(path, val):
        key = path[-1] if not isinstance(path[-1], int) else path[-2]
        if key in (
            "vessel_id", "source_artifact", "sha256", "verification_authority", "last_audited",
            "passenger_accessible", "source", "provenance", "notes", "id", "category", "dining_model",
            "tags", "standard_amenities", "distinct_categories_count", "deck_number", "deck", "decks", "code"
        ):
            return "STRUCTURAL_METADATA"
        if key in (
            "name", "vessel_name", "total_staterooms", "total_decks", "passenger_accessible_decks",
            "passenger_capacity_max_occupancy", "total_cabins_min", "total_cabins_max", "class",
            "balcony_percentage"
        ):
            return "SOURCE_SUPPORTED_FACT"
        if key in ("description",):
            return "EDITORIAL_DERIVATION"
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


def test_meraviglia_14_editorial_descriptions_tags_cannot_bypass_evidence_classification():
    """14. Retained descriptions and tags are free from unevidenced marketing claims."""
    banned_keywords = ["luxury", "budget", "oysters", "caviar", "live-music", "british-style", "exclusive-vibe"]
    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".json") and fname != "extraction_manifest.json":
            with open(os.path.join(KNOWLEDGE_DIR, fname), "r", encoding="utf-8") as f:
                content = f.read().lower()
                for kw in banned_keywords:
                    assert kw not in content, f"Banned marketing keyword '{kw}' found in {fname}"


def test_meraviglia_15_geometry_remains_synthetic():
    """15. Gatekeeper evaluation keeps spatial geometry as SYNTHETIC_GEOMETRY."""
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


def test_meraviglia_16_deck_4_is_kos():
    """16. Deck 4 is Kos."""
    decks_path = os.path.join(KNOWLEDGE_DIR, "decks.json")
    with open(decks_path, "r", encoding="utf-8") as f:
        decks_doc = json.load(f)
    deck4 = next(d for d in decks_doc["decks"] if d["deck_number"] == 4)
    assert "Kos" in deck4["name"]


def test_meraviglia_17_deck_5_is_colosseo():
    """17. Deck 5 is Colosseo."""
    decks_path = os.path.join(KNOWLEDGE_DIR, "decks.json")
    with open(decks_path, "r", encoding="utf-8") as f:
        decks_doc = json.load(f)
    deck5 = next(d for d in decks_doc["decks"] if d["deck_number"] == 5)
    assert "Colosseo" in deck5["name"]


def test_meraviglia_18_deck_6_is_petra():
    """18. Deck 6 is Petra."""
    decks_path = os.path.join(KNOWLEDGE_DIR, "decks.json")
    with open(decks_path, "r", encoding="utf-8") as f:
        decks_doc = json.load(f)
    deck6 = next(d for d in decks_doc["decks"] if d["deck_number"] == 6)
    assert "Petra" in deck6["name"]


def test_meraviglia_19_cabins_count_is_2214():
    """19. Total cabins is 2214 in cabins.json and technical.json."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)
    assert cabins_doc["summary"]["total_staterooms"] == 2214

    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    assert tech_doc["technical_specifications"]["capacities"]["total_cabins_min"] == 2214
    assert tech_doc["technical_specifications"]["capacities"]["total_cabins_max"] == 2214


def test_meraviglia_20_max_guests_is_5714():
    """20. Max guests is 5714 in technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    assert tech_doc["technical_specifications"]["capacities"]["passenger_capacity_max_occupancy"] == 5714


def test_meraviglia_reingestion_is_idempotent():
    """Consecutive execution of run_ingestion produces zero diff (TASK N)."""
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
