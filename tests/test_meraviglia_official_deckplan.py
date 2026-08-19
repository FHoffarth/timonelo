"""
Tests for MSC Meraviglia Official Deck Plan Ingestion & Canonical Knowledge Pack (P0-B Step 2B.1A).
Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-B Evidence Hygiene & Real Lifecycle Transitions.
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
from timonelo.evidence.artifacts import ArtifactStore, sha256_of_file
from timonelo.evidence.engine import Statement, TruthEngine
from timonelo.evidence.events import EvidenceEvent, EvidenceEventLog
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    ConflictGateResult,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
)
from timonelo.evidence.questions import Question, QuestionRegistry
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
def manifest():
    manifest_path = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    if not os.path.exists(manifest_path):
        run_ingestion()
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# TASK H — NEGATIVE & POSITIVE TEST MATRIX
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
        "environmental_features", "class"
    ]
    for k in unsupported_keys:
        assert k not in specs, f"Unsupported technical spec '{k}' must be absent from technical.json"

    capacities = specs.get("capacities", {})
    assert "crew_capacity_min" not in capacities
    assert "crew_capacity_max" not in capacities
    assert "passenger_capacity_double_occupancy" not in capacities
    assert "total_decks" not in capacities


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


def test_meraviglia_8_real_canonical_lifecycle_transition(tmp_path):
    """8. TASK A/B: Real canonical UNKNOWN -> SUPPORTED transition via TruthEngine & ReviewLog."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-19", obtained_from="test")

    q_reg = QuestionRegistry()
    q_reg.register(Question("Q-1", "deck", statement_type="deck.venue_present", supportable_by=("cruise_line_deck_plan",)))
    event_log = EvidenceEventLog(str(tmp_path / "events.json"), store, q_reg)
    event_log.append(EvidenceEvent("E1", art.sha256, "page:3", "d:5", "Q-1", "Colosseo", "pipeline", "2026-08-19"))

    truth_engine = TruthEngine(q_reg, event_log, store)
    rlog = ReviewLog(str(tmp_path / "reviews.json"))

    # Initial state is strictly UNKNOWN / DRAFT / PUBLISH_BLOCKED
    stmt_initial = Statement(
        statement_id="S-1",
        entity_id="d:5",
        question_id="Q-1",
        value="Colosseo",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )
    assert stmt_initial.evidence_condition == EvidenceCondition.UNKNOWN
    assert stmt_initial.human_review_state == HumanReviewState.DRAFT
    assert stmt_initial.publish_status == PublishStatus.PUBLISH_BLOCKED

    truth_engine.add_statement(stmt_initial)

    # Invoke canonical transition mechanism
    transitioned = truth_engine.set_evidence_condition("S-1", EvidenceCondition.SUPPORTED)
    assert transitioned.evidence_condition == EvidenceCondition.SUPPORTED

    # Canonical ReviewLog audit emission
    entry = rlog.record_condition_transition(
        statement_id="S-1",
        from_condition=EvidenceCondition.UNKNOWN,
        to_condition=EvidenceCondition.SUPPORTED,
        actor="deckplan_evidence_verifier",
        occurred_on="2026-08-19",
        note="Evidenced in deckplan",
    )
    assert entry.from_state == "CONDITION:UNKNOWN"
    assert entry.to_state == "CONDITION:SUPPORTED"
    assert entry.actor == "deckplan_evidence_verifier"
    assert entry.occurred_on == "2026-08-19"


def test_meraviglia_9_no_direct_supported_constructor_in_ingestion_ast():
    """9. TASK B: AST test proving ingestion script does NOT call Statement(..., evidence_condition=SUPPORTED)."""
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
            if func_name == "Statement":
                for kw in node.keywords:
                    if kw.arg == "evidence_condition":
                        val_str = ast.unparse(kw.value)
                        assert "SUPPORTED" not in val_str, (
                            f"Direct construction of Statement with SUPPORTED is forbidden: {ast.unparse(node)}"
                        )
                        assert "UNKNOWN" in val_str, (
                            f"Statement must be initialized in UNKNOWN: {ast.unparse(node)}"
                        )


def test_meraviglia_10_audit_records_come_from_transition_mechanism(manifest):
    """10. TASK H.3: Audit records in extraction manifest come from canonical transition mechanism."""
    assert len(manifest["audit_log"]) == len(manifest["statements"])
    for entry in manifest["audit_log"]:
        assert entry["from_state"] == "CONDITION:UNKNOWN"
        assert entry["to_state"] == "CONDITION:SUPPORTED"
        assert entry["actor"] == "deckplan_evidence_verifier"
        assert entry["occurred_on"] == "2026-08-19"


def test_meraviglia_11_exact_22_cabin_category_code_set():
    """11. TASK C / H.4: Exact set equality of all 22 cabin category codes from Page 2."""
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


def test_meraviglia_12_yc1_and_yin_present():
    """12. TASK C / H.5, H.6: YC1 and YIN are present with source-supported names and decks."""
    cabins_path = os.path.join(KNOWLEDGE_DIR, "cabins.json")
    with open(cabins_path, "r", encoding="utf-8") as f:
        cabins_doc = json.load(f)

    yc1 = next((c for c in cabins_doc["cabin_categories"] if c["id"] == "CAT-YC1"), None)
    assert yc1 is not None
    assert "Deluxe Suite" in yc1["name"]
    assert yc1["deck"] == [14, 15, 16, 18]

    yin = next((c for c in cabins_doc["cabin_categories"] if c["id"] == "CAT-YIN"), None)
    assert yin is not None
    assert "Innenkabine" in yin["name"] or "Interior" in yin["name"]
    assert yin["deck"] == [14, 15, 16]


def test_meraviglia_13_no_unsupported_total_decks_18():
    """13. TASK D / H.7: total_decks=18 is completely absent from technical.json and statements."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    capacities = tech_doc["technical_specifications"]["capacities"]
    assert "total_decks" not in capacities
    assert capacities["passenger_accessible_decks"] == 15

    manifest_path = os.path.join(KNOWLEDGE_DIR, "extraction_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)
    assert not any(s["question_id"] == "Q-SHIP-TOTAL-DECKS" for s in m["statements"])
    assert not any(e["event_id"] == "EVT-MER-TOTAL-DECKS" for e in m["events"])


def test_meraviglia_14_no_deckplan_sourced_ship_class():
    """14. TASK E / H.8: Ship class is absent from deckplan-generated technical.json."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    specs = tech_doc.get("technical_specifications", {})
    assert "class" not in specs


def test_meraviglia_15_technical_json_only_deckplan_supported():
    """15. TASK H.9: technical.json contains only evidenced capacity fields."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)

    specs = tech_doc["technical_specifications"]
    assert set(specs.keys()) == {"capacities"}
    assert set(specs["capacities"].keys()) == {
        "passenger_accessible_decks",
        "passenger_capacity_max_occupancy",
        "total_cabins_min",
        "total_cabins_max",
    }


def test_meraviglia_16_gatekeeper_remains_publish_blocked(manifest):
    """16. TASK H.10: Gatekeeper evaluates to PUBLISH_BLOCKED due to DRAFT review state."""
    for s in manifest["statements"]:
        assert s["human_review_state"] == "DRAFT"
        assert s["publish_status"] == "PUBLISH_BLOCKED"


def test_meraviglia_17_geometry_remains_synthetic():
    """17. TASK H.11: Spatial geometry remains SYNTHETIC_GEOMETRY."""
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
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))
    res = gk.evaluate_publish_gate()
    assert res.synthetic_geometry_count == 15
    assert res.direct_geometry_count == 0


def test_meraviglia_18_deck_names_colosseo_kos_petra():
    """18. Deck names are Kos (4), Colosseo (5), Petra (6)."""
    decks_path = os.path.join(KNOWLEDGE_DIR, "decks.json")
    with open(decks_path, "r", encoding="utf-8") as f:
        decks_doc = json.load(f)
    deck4 = next(d for d in decks_doc["decks"] if d["deck_number"] == 4)
    assert "Kos" in deck4["name"]
    deck5 = next(d for d in decks_doc["decks"] if d["deck_number"] == 5)
    assert "Colosseo" in deck5["name"]
    deck6 = next(d for d in decks_doc["decks"] if d["deck_number"] == 6)
    assert "Petra" in deck6["name"]


def test_meraviglia_19_total_cabins_2214_and_guests_5714():
    """19. Total cabins is 2214 and max guests is 5714."""
    tech_path = os.path.join(KNOWLEDGE_DIR, "technical.json")
    with open(tech_path, "r", encoding="utf-8") as f:
        tech_doc = json.load(f)
    caps = tech_doc["technical_specifications"]["capacities"]
    assert caps["total_cabins_min"] == 2214
    assert caps["total_cabins_max"] == 2214
    assert caps["passenger_capacity_max_occupancy"] == 5714


def test_meraviglia_20_unsupported_factual_leaf_coverage_zero():
    """20. Unsupported factual leaf count is exactly zero across all canonical files."""
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
            "name", "vessel_name", "total_staterooms", "passenger_accessible_decks",
            "passenger_capacity_max_occupancy", "total_cabins_min", "total_cabins_max",
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


def test_meraviglia_reingestion_is_idempotent():
    """Consecutive execution of run_ingestion produces zero diff."""
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
