"""
Guards the Deck 14 cabin-feature layer.

The layer turns printed deck-plan symbols into statements. Two things make that
dangerous, and both are asserted here.

First, silence. The deck plan marks what a stateroom has, never what it lacks,
so a cabin without a symbol is unknown — not featureless. Any negative
statement, or any UI copy that reads as one, would invent evidence.

Second, degeneracy. Half the grounded families are bare squares and circles
that match every other square and circle. They are admitted only because
cluster cardinality reproduces the legend's own composite structure, and each
statement they produce must say so.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from timonelo.evidence import authority
from timonelo.spatial import deck14_symbol_extract as symbols

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
STATEMENTS = REPO_ROOT / "evidence" / "statements" / "statements.json"
QUESTIONS = REPO_ROOT / "evidence" / "registry" / "questions.json"
FEATURES = REPO_ROOT / "frontend" / "public" / "data" / "deck14.features.json"

FEATURE_TYPES = {f.statement_type for f in symbols.GROUNDED_FAMILIES}

EXPECTED_COUNTS = {
    "sofa_bed": 87,
    "sofa_bed_double": 8,
    "third_bed": 4,
    "third_and_fourth_bed": 18,
    "bunk_or_convertible_sofa": 71,
    "sofa_bed_single": 2,
}
EXPECTED_CABINS_WITH_FEATURES = 186

pytest.importorskip("fitz", reason="PyMuPDF is forensic tooling, not a runtime dependency")


@pytest.fixture(scope="module")
def report():
    return symbols.extract_symbols()


@pytest.fixture(scope="module")
def statements():
    return json.loads(STATEMENTS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def feature_statements(statements):
    return [s for s in statements.values() if s["statement_type"] in FEATURE_TYPES]


@pytest.fixture(scope="module")
def features_doc():
    return json.loads(FEATURES.read_text(encoding="utf-8"))


# -- extraction -------------------------------------------------------------

def test_extraction_counts_per_grounded_family(report):
    assert report.counts_by_family() == EXPECTED_COUNTS


def test_only_the_six_grounded_families_are_implemented(report):
    assert len(symbols.GROUNDED_FAMILIES) == 6
    assert {f.family_id for f in symbols.GROUNDED_FAMILIES} == set(EXPECTED_COUNTS)
    # The families prior audits left ungrounded must not have crept in.
    for absent in ("mobility", "bathtub", "bathtub_shower", "connecting_door",
                   "obstructed_view", "balcony", "whirlpool"):
        assert absent not in symbols.FAMILY_BY_ID


def test_zero_ambiguous_cabin_ownership(report):
    assert report.ambiguous_ownership == []


def test_symbols_outside_deck14_cabin_geometry_are_not_attached(report):
    """Page 5 draws Decks 14-19; only symbols inside a cabin envelope attach."""
    assert report.outside_cabin_geometry["sofa_bed"] == 16
    assert report.outside_cabin_geometry["sofa_bed_double"] == 8
    attached = sum(report.counts_by_family().values())
    assert attached == len(report.observations)
    cabins = {o.cabin_number for o in report.observations}
    assert all(number.startswith("14") and len(number) == 5 for number in cabins)


def test_cluster_cardinality_derivation_is_explicit(report):
    """A lone circle is not a bunk; a lone square is not a pair."""
    assert symbols.FAMILY_BY_ID["third_bed"].cardinality == 1
    assert symbols.FAMILY_BY_ID["third_and_fourth_bed"].cardinality == 2
    assert symbols.FAMILY_BY_ID["bunk_or_convertible_sofa"].cardinality == 2
    for family_id in ("third_bed", "third_and_fourth_bed", "bunk_or_convertible_sofa"):
        assert symbols.FAMILY_BY_ID[family_id].is_derived
        assert symbols.FAMILY_BY_ID[family_id].degenerate_primitive
    for family_id in ("sofa_bed", "sofa_bed_double", "sofa_bed_single"):
        assert not symbols.FAMILY_BY_ID[family_id].is_derived

    for observation in report.observations:
        expected = symbols.FAMILY_BY_ID[observation.family_id].cardinality
        assert observation.instance_count == expected


def test_clusters_of_unexpected_size_yield_nothing(report):
    """Leftovers are counted, not quietly folded into a neighbouring family."""
    leftovers = report.unmatched_cardinality["bunk_or_convertible_sofa"]
    assert leftovers, "expected some lone circles to be reported"
    assert 2 not in leftovers  # every pair was consumed as a bunk symbol


def test_extraction_is_reproducible_across_runs():
    first = symbols.extract_symbols()
    second = symbols.extract_symbols()
    assert first.counts_by_family() == second.counts_by_family()
    assert [
        (o.cabin_number, o.family_id, o.source_references) for o in first.observations
    ] == [
        (o.cabin_number, o.family_id, o.source_references) for o in second.observations
    ]


def test_degenerate_families_need_the_scale_gate():
    """Without it a bare circle matches unrelated plan circles at any size."""
    assert symbols.SCALE_RATIO_BAND[0] < symbols.SCALE_RATIO_BAND[1]
    assert symbols.tolerance_for("sofa_bed") == symbols.SHAPE_TOLERANCE
    # The one documented exception stays scoped to the family that needs it.
    assert symbols.tolerance_for("sofa_bed_single") > symbols.SHAPE_TOLERANCE
    assert set(symbols.SHAPE_TOLERANCE_OVERRIDES) == {"sofa_bed_single"}


# -- statements -------------------------------------------------------------

def test_every_feature_statement_is_positive(feature_statements):
    assert feature_statements
    assert {str(s["value"]) for s in feature_statements} == {"true"}


def test_absence_produces_no_statement(report, statements):
    """A cabin with no symbol has no feature statement of any kind."""
    with_features = set(report.by_cabin())
    all_cabins = {
        s["entity_id"].rsplit(":", 1)[-1]
        for s in statements.values()
        if s["statement_type"] == "cabin.exists"
    }
    unmarked = all_cabins - with_features
    assert unmarked, "expected some stated cabins to carry no grounded symbol"
    for statement in statements.values():
        if statement["statement_type"] not in FEATURE_TYPES:
            continue
        assert statement["entity_id"].rsplit(":", 1)[-1] not in unmarked


def test_no_negative_feature_vocabulary_anywhere(feature_statements):
    serialized = json.dumps(feature_statements).lower()
    for banned in ("no sofa", "not present", "absent", "without a sofa",
                   "no pullman", "no bunk", "does not have", '"false"'):
        assert banned not in serialized


def test_statement_count_matches_extraction(report, feature_statements):
    assert len(feature_statements) == len(report.observations)
    by_type: dict[str, int] = {}
    for statement in feature_statements:
        by_type[statement["statement_type"]] = by_type.get(statement["statement_type"], 0) + 1
    for family in symbols.GROUNDED_FAMILIES:
        assert by_type[family.statement_type] == EXPECTED_COUNTS[family.family_id]


def test_source_sha_page_and_locator_are_preserved(feature_statements):
    for statement in feature_statements:
        assert statement["artifact_id"] == symbols.ARTIFACT_ID
        assert statement["page"] == symbols.SYMBOL_PAGE_NUMBER
        assert "page5:drawing-index-" in statement["locator"]
        assert "Deck 14" in statement["locator"]


def test_derived_families_carry_a_derivation_note(feature_statements):
    for statement in feature_statements:
        family = next(
            f for f in symbols.GROUNDED_FAMILIES
            if f.statement_type == statement["statement_type"]
        )
        if family.is_derived:
            assert statement["method"] == "CALCULATED"
            assert "cardinality" in statement["derivation_note"]
        else:
            assert statement["method"] == "DIRECT"
            assert statement["derivation_note"] == ""


def test_all_feature_statements_are_draft_and_publish_blocked(feature_statements):
    for statement in feature_statements:
        assert statement["human_review_state"] == "DRAFT"
        assert statement["publish_status"] == "PUBLISH_BLOCKED"
        assert statement["evidence_condition"] == "UNKNOWN"


# -- vocabulary -------------------------------------------------------------

def test_each_family_has_its_own_question_and_statement_type():
    """One axis per family: co-occurring features must not look like conflicts."""
    types = [f.statement_type for f in symbols.GROUNDED_FAMILIES]
    questions = [f.question_id for f in symbols.GROUNDED_FAMILIES]
    assert len(set(types)) == len(types) == 6
    assert len(set(questions)) == len(questions) == 6


def test_deck_plan_has_authority_over_every_feature_type():
    for family in symbols.GROUNDED_FAMILIES:
        authority.check(family.statement_type, "cruise_line_deck_plan")


def test_feature_types_do_not_overload_unrelated_vocabulary():
    for family in symbols.GROUNDED_FAMILIES:
        assert family.statement_type.startswith("cabin.")
        assert family.statement_type not in ("deck.venue_present", "cabin.bed_configuration")


def test_questions_are_registered_with_unknown_guidance():
    registry = json.loads(QUESTIONS.read_text(encoding="utf-8"))["questions"]
    entries = registry.values() if isinstance(registry, dict) else registry
    by_id = {q["question_id"]: q for q in entries}
    for family in symbols.GROUNDED_FAMILIES:
        question = by_id[family.question_id]
        assert question["entity_type"] == "cabin"
        assert question["statement_type"] == family.statement_type
        # The unknown path must read as silence, never as denial.
        guidance = question["unknown_guidance"].lower()
        assert "not a statement that the feature is absent" in guidance


def test_no_conflicts_were_raised_between_co_occurring_features():
    conflicts = json.loads(
        (REPO_ROOT / "evidence" / "reviews" / "conflicts.json").read_text(encoding="utf-8")
    )
    records = conflicts.get("conflicts", conflicts)
    if isinstance(records, dict):
        records = list(records.values())
    for record in records:
        if isinstance(record, dict):
            assert record.get("statement_type") not in FEATURE_TYPES


# -- frontend projection ----------------------------------------------------

def test_frontend_features_match_the_statement_graph(features_doc, feature_statements):
    assert features_doc["schema"] == "timonelo.deck14-cabin-features.v0"
    assert features_doc["deck"] == 14
    assert len(features_doc["cabins"]) == EXPECTED_CABINS_WITH_FEATURES
    exported = sum(len(v) for v in features_doc["cabins"].values())
    assert exported == len(feature_statements)
    ids = {f["statement_id"] for v in features_doc["cabins"].values() for f in v}
    assert ids == {s["statement_id"] for s in feature_statements}


def test_frontend_features_carry_provenance_and_lifecycle(features_doc):
    for entries in features_doc["cabins"].values():
        for feature in entries:
            assert feature["artifact_id"] == symbols.ARTIFACT_ID
            assert feature["page"] == symbols.SYMBOL_PAGE_NUMBER
            assert feature["locator"]
            assert feature["human_review_state"] == "DRAFT"
            assert feature["publish_status"] == "PUBLISH_BLOCKED"
            assert feature["evidence_condition"] == "UNKNOWN"


def test_frontend_features_never_encode_absence(features_doc):
    """Only cabins with a symbol appear; nothing records a missing feature.

    The scan is on the cabin payload alone. The `families` block legitimately
    carries `derived_from_cardinality: false` — a schema flag describing how a
    family is recognised, not a claim about any stateroom — and scanning it
    would flag the description rather than a denial.
    """
    serialized = json.dumps(features_doc["cabins"]).lower()
    for banned in ("no sofa", "false", "absent", "not present", "does not have"):
        assert banned not in serialized
    for entries in features_doc["cabins"].values():
        assert entries, "an empty list would read as an explicit denial"


def test_frontend_features_are_geometry_free(features_doc):
    """Features are statements about a cabin, not properties of its envelope."""
    serialized = json.dumps(features_doc)
    for banned in ("normalized_bbox", "source_bbox", "navigation_graph",
                   "corridor", "transform_id", "meters", "metres"):
        assert banned not in serialized
