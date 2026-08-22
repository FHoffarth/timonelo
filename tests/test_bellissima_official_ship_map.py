"""
Evidence guards for the MSC Bellissima official ship map intake (ART-0002).

The source establishes which deck a venue is on, and nothing else. These tests
pin both halves of that: the deck facts are present with their page evidence,
and none of the spatial claims a thematic map cannot support have appeared.
"""

from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from pathlib import Path

import pytest

from timonelo.evidence import authority
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.registry import ArtifactRegistry, sha256_of_file
from timonelo.evidence.review import ReviewLog
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO_ROOT / "evidence" / "artifacts"
STATEMENTS_PATH = REPO_ROOT / "evidence" / "statements" / "statements.json"
QUESTIONS_PATH = REPO_ROOT / "evidence" / "registry" / "questions.json"

ARTIFACT_ID = "ART-0002"
DIGEST = "4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603"
BYTE_SIZE = 1177146
DOCUMENT_CLASS = "official_ship_map"
STATEMENT_TYPE = "deck.venue_present"
QUESTION_ID = "Q-0016"

ART_0001_DIGEST = "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"

VAULT_PATH = REPO_ROOT / "evidence" / "raw" / "sha256" / DIGEST[:2] / f"{DIGEST}.pdf"


def _statements() -> dict:
    return json.loads(STATEMENTS_PATH.read_text(encoding="utf-8"))


def _ship_map_statements() -> list:
    return [
        s for s in _statements().values() if s.get("artifact_id") == ARTIFACT_ID
    ]


def _by_slug(slug: str) -> dict:
    entity = f"venue:MSC-BELLISSIMA:{slug}"
    matches = [s for s in _ship_map_statements() if s["entity_id"] == entity]
    assert len(matches) == 1, f"expected exactly one statement for {slug}"
    return matches[0]


# --- 1. the exact artifact resolves from the canonical SHA vault -----------


#: Statement types introduced by the Deck 14 cabin-feature layer.
#:
#: The quarantine assertions below describe the claim set that existed when
#: ART-0001's source identity was repaired. Selecting purely on artifact_id now
#: also sweeps in the later feature statements, which are a different cohort
#: with a different lifecycle — DRAFT and PUBLISH_BLOCKED rather than APPROVED
#: and quarantined by evidence condition. Excluding them keeps these tests
#: about the thing they were written to protect.
_FEATURE_TYPES = {
    "cabin.sofa_bed",
    "cabin.sofa_bed_double",
    "cabin.sofa_bed_single",
    "cabin.third_bed",
    "cabin.third_and_fourth_bed",
    "cabin.bunk_or_convertible_sofa",
}


def test_art_0002_resolves_from_the_canonical_sha_vault():
    registry = ArtifactRegistry(str(ARTIFACTS))
    artifact = registry.get(ARTIFACT_ID)

    assert artifact.sha256 == DIGEST
    assert artifact.byte_size == BYTE_SIZE
    assert artifact.filename == "be_en-gb.pdf"
    assert artifact.document_class == DOCUMENT_CLASS
    assert artifact.publisher == "MSC Cruises"
    assert artifact.language == "en-GB"
    assert artifact.acquisition_method == (
        "supplied by project owner; obtained from the myMSC application"
    )

    resolved = registry.resolve_path(ARTIFACT_ID)
    assert resolved is not None
    assert Path(resolved).resolve() == VAULT_PATH.resolve()
    assert registry.verify(ARTIFACT_ID)

    # Bytes on disk reproduce the registered digest and length.
    assert sha256_of_file(str(VAULT_PATH)) == DIGEST
    assert VAULT_PATH.stat().st_size == BYTE_SIZE


def test_no_parallel_blob_store_was_created():
    """The legacy blob directory stays empty; the vault is the only store."""
    blobs = ARTIFACTS / "blobs"
    assert sorted(p.name for p in blobs.iterdir()) == [".gitkeep"]


def test_acquisition_note_claims_no_public_distribution_right():
    registry = ArtifactRegistry(str(ARTIFACTS))
    artifact = registry.get(ARTIFACT_ID)
    text = f"{artifact.acquisition_method} {artifact.notes}".lower()

    for overclaim in ("public", "publicly", "downloadable", "redistribut"):
        assert overclaim not in text

    cls = authority.DOCUMENT_CLASSES[DOCUMENT_CLASS]
    assert cls.acquisition is authority.Acquisition.REQUESTABLE
    assert cls.use_permission is authority.UsePermission.CITE_ONLY


# --- 2. duplicate source registration is idempotent -----------------------


def test_registering_the_same_bytes_again_issues_no_second_id(tmp_path):
    root = tmp_path / "artifacts"
    shutil.copytree(ARTIFACTS, root)
    registry = ArtifactRegistry(str(root))
    before = len(registry)

    again = registry.register(
        path=str(VAULT_PATH),
        document_class=DOCUMENT_CLASS,
        acquired_on="2026-09-01",
        acquisition_method="second attempt",
        publisher="MSC Cruises",
    )

    assert again.artifact_id == ARTIFACT_ID
    assert again.sha256 == DIGEST
    # Original acquisition metadata survives; the re-registration does not
    # overwrite how the first copy was obtained.
    assert again.acquired_on == "2026-08-22"
    assert len(registry) == before


# --- 3. explicit venue deck facts retain page evidence --------------------


def test_ship_map_statements_exist_and_are_gated():
    statements = _ship_map_statements()
    assert len(statements) == 87

    for statement in statements:
        assert statement["statement_type"] == STATEMENT_TYPE
        assert statement["question_id"] == QUESTION_ID
        assert statement["entity_id"].startswith("venue:MSC-BELLISSIMA:")
        # Nothing is promoted by an intake.
        assert statement["human_review_state"] == HumanReviewState.DRAFT.value
        assert statement["evidence_condition"] == EvidenceCondition.UNKNOWN.value
        assert statement["publish_status"] == PublishStatus.PUBLISH_BLOCKED.value


def test_every_fact_carries_its_source_page_and_locator():
    for statement in _ship_map_statements():
        assert statement["page"] in range(3, 11)
        locator = statement["locator"]
        assert locator.startswith(f"Page {statement['page']}, ")
        assert "index table" in locator
        assert "printed deck value" in locator
        assert statement["read_by"] and statement["read_on"]


@pytest.mark.parametrize(
    "slug,decks,page",
    [
        ("kaito-sushi-bar", [7], 4),
        ("marketplace-buffet", [15], 4),
        ("msc-gym-powered-by-technogym", [16], 8),
        ("arizona-aquapark", [19], 8),
        ("msc-yacht-club-restaurant", [18], 3),
        ("top-sail-lounge", [16], 3),
        ("posidonia-restaurant", [5], 4),
    ],
)
def test_named_venue_deck_assignments(slug, decks, page):
    statement = _by_slug(slug)
    assert statement["value"] == decks
    assert statement["page"] == page


def test_corroborating_pages_are_recorded_without_duplicating_the_claim():
    """A venue indexed on several pages is one claim observed several times."""
    aquapark = _by_slug("arizona-aquapark")
    assert aquapark["value"] == [19]
    assert aquapark["note"].startswith("Printed on page(s) 8, 9, 10.")
    assert 'page 9 table "Fun"' in aquapark["locator"]
    assert 'page 10 table "Family Areas"' in aquapark["locator"]

    # One statement per venue, never one per printing.
    entities = [s["entity_id"] for s in _ship_map_statements()]
    assert len(entities) == len(set(entities))


def test_question_registered_for_venue_entities():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))["questions"]
    question = questions[QUESTION_ID]

    assert question["entity_type"] == "venue"
    assert question["statement_type"] == STATEMENT_TYPE
    assert DOCUMENT_CLASS in authority.authoritative_classes(STATEMENT_TYPE)


# --- 4. multi-deck venues retain the full range ---------------------------


def test_multi_deck_venues_keep_every_deck():
    assert _by_slug("london-theatre")["value"] == [5, 6]
    assert _by_slug("galleria-bellissima")["value"] == [6, 7]
    assert _by_slug("msc-excursions")["value"] == [5, 6]


def test_deck_values_are_always_lists_so_a_range_cannot_collapse():
    for statement in _ship_map_statements():
        assert isinstance(statement["value"], list)
        assert statement["value"], "a deck list is never empty"
        assert all(isinstance(deck, int) for deck in statement["value"])
        assert statement["value"] == sorted(statement["value"])


def test_horizon_amphitheatre_range_excludes_the_deck_the_ship_does_not_have():
    """16-18 is not 16,17,18: this vessel's deck selector lists no Deck 17."""
    statement = _by_slug("horizon-amphitheatre")

    assert statement["value"] == [16, 18]
    assert 17 not in statement["value"]
    assert '"16-18"' in statement["locator"]
    # An expansion consults a second printed fact, so it is not DIRECT.
    assert statement["method"] == "CALCULATED"
    assert "deck selector" in statement["derivation_note"]
    assert "16-18" in statement["note"]


def test_declared_decks_do_not_include_deck_17():
    """Guards the premise of the range expansion against the real document."""
    fitz = pytest.importorskip("fitz")
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import ingest_bellissima_official_ship_map as ingest

    document = fitz.open(str(VAULT_PATH))
    try:
        decks = ingest.declared_decks(document)
    finally:
        document.close()

    assert decks == (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19)
    assert 17 not in decks


# --- 5/6/7. no geometry, no routing edges, no distance/time/accessibility --


def test_no_geometry_was_created_or_modified():
    """Deck geometry and the Deck 14 proof are untouched by this intake."""
    for path in sorted((REPO_ROOT / "geometry").glob("*.geometry.json")):
        assert DIGEST not in path.read_text(encoding="utf-8")

    proof = REPO_ROOT / "geometry" / "proofs" / "bellissima" / "deck14" / "deck14.proof.json"
    assert proof.exists()
    proof_text = proof.read_text(encoding="utf-8")
    assert DIGEST not in proof_text
    assert ARTIFACT_ID not in proof_text
    assert json.loads(proof_text)["source"]["artifact_sha256"] == ART_0001_DIGEST


def test_no_coordinate_or_polygon_appears_in_any_ship_map_statement():
    forbidden = (
        "polygon", "bbox", "centroid", "coordinate", "normalized",
        "x0", "y0", "\"x\"", "\"y\"",
    )
    for statement in _ship_map_statements():
        blob = json.dumps(statement).lower()
        for token in forbidden:
            assert token not in blob, f"{token} in {statement['statement_id']}"
        assert isinstance(statement["value"], list)


#: The fields that actually carry a claim. `note` and `locator` are prose and
#: legitimately name the things this source does NOT establish, so scanning
#: them for those words would flag the disclaimer itself.
CLAIM_FIELDS = ("entity_id", "question_id", "statement_type", "value")


def _claim_blob(statement: dict) -> str:
    return json.dumps({k: statement[k] for k in CLAIM_FIELDS}).lower()


def test_no_routing_edges_were_created():
    """The intake does not touch the spatial graph or the router."""
    source = (
        REPO_ROOT / "scripts" / "ingest_bellissima_official_ship_map.py"
    ).read_text(encoding="utf-8")

    assert "timonelo.spatial" not in source
    assert "SpatialEdge" not in source
    assert "SpatialGraph" not in source
    assert "DeterministicSpatialRouter" not in source

    # A venue name is arbitrary text ("EDGE - COCKTAIL BAR"), so the guard is
    # structural: the only claim shape produced is a deck list, and no
    # graph-shaped field exists to hold connectivity.
    for statement in _ship_map_statements():
        assert statement["statement_type"] == STATEMENT_TYPE
        assert set(statement) == set(_statements()["STM-0114"])
        for graph_field in (
            "from_node_id", "to_node_id", "edge_id", "edges", "nodes",
            "walkable", "connects_to", "adjacent_to",
        ):
            assert graph_field not in statement


def test_no_distance_walking_time_or_accessibility_claim_was_created():
    for statement in _ship_map_statements():
        blob = _claim_blob(statement)
        for token in (
            "distance", "metre", "meter", "walking_time", "walking time",
            "seconds", "step_free", "step-free", "accessib", "wheelchair",
        ):
            assert token not in blob, f"{token} in {statement['statement_id']}"
        # The only value ever carried is a list of deck numbers.
        assert isinstance(statement["value"], list)
        assert all(isinstance(deck, int) for deck in statement["value"])


def test_the_disclaimer_note_states_what_the_source_cannot_support():
    """The prose the previous two tests skip is checked here, positively."""
    for statement in _ship_map_statements():
        note = statement["note"].lower()
        assert "deck assignment only" in note
        for token in ("position", "distance", "adjacency", "door", "corridor"):
            assert token in note


def test_ship_map_has_no_authority_over_position_or_geometry():
    """The class may say which deck, never where on it."""
    assert DOCUMENT_CLASS not in authority.authoritative_classes("deck.venue_position")
    assert DOCUMENT_CLASS not in authority.authoritative_classes("cabin.area_sqm")
    assert DOCUMENT_CLASS not in authority.authoritative_classes("cabin.door_clear_width_mm")

    with pytest.raises(authority.AuthorityError):
        authority.check("deck.venue_position", DOCUMENT_CLASS)
    with pytest.raises(authority.AuthorityError):
        authority.check("cabin.deck", DOCUMENT_CLASS)


def test_callout_lines_and_silhouettes_are_documented_as_presentational():
    notes = authority.DOCUMENT_CLASSES[DOCUMENT_CLASS].notes.lower()
    assert "presentational" in notes
    for token in ("position", "distance", "adjacency", "door", "corridor", "connectivity"):
        assert token in notes


# --- 8. conflicting facts are surfaced, never overwritten -----------------


def test_a_disagreeing_venue_claim_is_logged_as_a_conflict_not_an_overwrite(tmp_path):
    root = tmp_path / "artifacts"
    shutil.copytree(ARTIFACTS, root)
    registry = ArtifactRegistry(str(root))
    conflicts = ConflictLog(str(tmp_path / "conflicts.json"))
    editor = StatementEditor(
        path=str(tmp_path / "statements.json"),
        registry=registry,
        review_log=ReviewLog(str(tmp_path / "reviews.json")),
        conflict_log=conflicts,
    )

    common = dict(
        entity_id="venue:MSC-BELLISSIMA:london-theatre",
        question_id=QUESTION_ID,
        statement_type=STATEMENT_TYPE,
        artifact_id=ARTIFACT_ID,
        read_by="test",
        read_on="2026-08-22",
        page=9,
    )
    incumbent = editor.create(value=[5, 6], locator="Page 9, Fun table", **common)
    challenger = editor.create(value=[5], locator="Page 9, disputed read", **common)

    # Both survive; neither is edited.
    assert incumbent.value == [5, 6]
    assert challenger.value == [5]
    assert incumbent.statement_id != challenger.statement_id

    logged = json.loads((tmp_path / "conflicts.json").read_text(encoding="utf-8"))
    assert json.dumps(logged).count(challenger.statement_id) >= 1


def test_the_ingested_document_disagrees_with_itself_nowhere():
    """Every venue is printed with one deck value across all category tables."""
    per_entity = Counter(s["entity_id"] for s in _ship_map_statements())
    assert set(per_entity.values()) == {1}


def test_legacy_unsourced_knowledge_is_preserved_and_not_promoted():
    """knowledge/ships files cite no registered artifact, so they are not evidence.

    They disagree with the ship map in places — venues.json puts the London
    Theatre on Deck 5 alone and the Galleria on Deck 6 alone — and are left
    exactly as they are. They are legacy/non-canonical, and they may not
    override an artifact-backed fact.
    """
    ships = REPO_ROOT / "knowledge" / "ships" / "msc-bellissima"
    venues = json.loads((ships / "venues.json").read_text(encoding="utf-8"))
    by_slug = {v["slug"]: v for v in venues}

    # Preserved unchanged, including the disagreements.
    assert by_slug["london-theatre"]["deck_number"] == 5
    assert by_slug["galleria-bellissima"]["deck_number"] == 6

    # And the registered facts are unaffected by them.
    assert _by_slug("london-theatre")["value"] == [5, 6]
    assert _by_slug("galleria-bellissima")["value"] == [6, 7]

    # None of these files cites a registered artifact.
    registry = ArtifactRegistry(str(ARTIFACTS))
    known = {registry.get(a).sha256 for a in ("ART-0001", ARTIFACT_ID)}
    for path in sorted(ships.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        assert not any(digest in text for digest in known)
        assert ARTIFACT_ID not in text


# --- 9. the new class stays distinct from the deck plan -------------------


def test_official_ship_map_is_a_distinct_class_from_cruise_line_deck_plan():
    assert DOCUMENT_CLASS in authority.DOCUMENT_CLASSES
    assert DOCUMENT_CLASS != "cruise_line_deck_plan"

    ship_map = authority.DOCUMENT_CLASSES[DOCUMENT_CLASS]
    deck_plan = authority.DOCUMENT_CLASSES["cruise_line_deck_plan"]
    assert ship_map.class_id != deck_plan.class_id
    assert ship_map.label != deck_plan.label

    # The deck plan keeps stateroom authority the ship map never gains.
    # (`cabin.deck` is in the curated source matrix; `cabin.exists` is declared
    # in the workspace file, so it is not resolvable without a Workspace.)
    assert "cruise_line_deck_plan" in authority.authoritative_classes("cabin.deck")
    assert DOCUMENT_CLASS not in authority.authoritative_classes("cabin.deck")


def test_art_0001_is_untouched_by_this_intake():
    registry = ArtifactRegistry(str(ARTIFACTS))
    art_0001 = registry.get("ART-0001")

    assert art_0001.document_class == "cruise_line_deck_plan"
    assert art_0001.sha256 == ART_0001_DIGEST
    assert art_0001.language == "de"
    assert registry.verify("ART-0001")

    raw = _statements()
    affected = [
        s for s in raw.values()
        if s["artifact_id"] == "ART-0001" and s["statement_type"] not in _FEATURE_TYPES
    ]
    assert len(affected) == 113
    # Still persisted in their original schema: rewriting them would be a
    # silent mutation of accepted facts.
    assert Counter(s["review_state"] for s in affected) == {
        "PUBLISHED": 112,
        "SUPERSEDED": 1,
    }


def test_the_two_bellissima_sources_are_separately_addressable():
    registry = ArtifactRegistry(str(ARTIFACTS))
    digests = {a: registry.get(a).sha256 for a in ("ART-0001", ARTIFACT_ID)}

    assert len(set(digests.values())) == 2
    assert all(registry.verify(a) for a in digests)
    assert os.path.exists(
        REPO_ROOT / "evidence" / "raw" / "sha256" / ART_0001_DIGEST[:2]
        / f"{ART_0001_DIGEST}.pdf"
    )


# --- intake record and report stay bound to the evidence -------------------

AUDIT_PATH = (
    REPO_ROOT / "evidence" / "audits" / "bellissima-official-ship-map-intake.json"
)
REPORT_PATH = (
    REPO_ROOT / "knowledge" / "reports" / "bellissima_official_ship_map_intake.md"
)


def test_audit_record_matches_the_registered_artifact_and_statements():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    artifact = audit["artifact"]
    assert artifact["artifact_id"] == ARTIFACT_ID
    assert artifact["sha256"] == DIGEST
    assert artifact["byte_size"] == BYTE_SIZE
    assert artifact["document_class"] == DOCUMENT_CLASS
    assert artifact["page_count"] == 10

    reconciliation = audit["reconciliation"]
    assert reconciliation["classification"] == "EXACT_MATCH"
    assert reconciliation["actual_sha256"] == reconciliation["claimed_sha256"] == DIGEST
    assert reconciliation["legacy_blob_store_used"] is False

    extraction = audit["extraction"]
    assert extraction["printed_table_rows_read"] == 115
    assert extraction["distinct_venue_deck_facts"] == 87
    assert extraction["corroborated_across_pages"] == 22
    assert extraction["intra_document_conflicts"] == 0
    assert extraction["range_collapse_performed"] is False
    assert 17 not in extraction["decks_declared_by_source"]
    assert len(extraction["multi_deck_facts"]) == 4

    statements = audit["statements"]
    assert statements["statements_created"] == len(_ship_map_statements())
    assert statements["human_review_state"] == ["DRAFT"]
    assert statements["evidence_condition"] == ["UNKNOWN"]
    assert statements["publish_status"] == ["PUBLISH_BLOCKED"]
    assert statements["method_counts"] == {"DIRECT": 83, "CALCULATED": 4}
    assert statements["art_0001_statements_modified"] is False

    assert audit["scope"] == {
        "accessibility_claims_created": False,
        "distance_claims_created": False,
        "geometry_created_or_modified": False,
        "position_inferred_from_callout_lines": False,
        "routing_edges_created": False,
        "venue_position_authority_granted": False,
        "walking_time_claims_created": False,
    }


def test_audit_multi_deck_entries_match_the_statements():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    for entry in audit["extraction"]["multi_deck_facts"]:
        slug = entry["venue"].lower().replace("&", " and ")
        slug = "-".join(part for part in slug.replace("'", "-").split() if part)
        statement = _by_slug(slug.replace("'", "-"))
        assert statement["value"] == entry["decks"]
        assert f'"{entry["printed_token"]}"' in statement["locator"]


def test_report_states_the_intake_facts():
    report = REPORT_PATH.read_text(encoding="utf-8")

    for fragment in (
        "ART-0002",
        DIGEST,
        "1 177 146",
        "official_ship_map",
        "MSC Cruises",
        "supplied by project owner; obtained from the myMSC application",
        "115",
        "87",
        "22",
        "`16-18`",
        "`[16, 18]`",
        "does not list a\nDeck 17",
        "Intra-document conflicts: 0",
        "London Theatre",
        "Galleria Bellissima",
        "no geometry",
        "no routing edges",
        "no distance, walking-time or accessibility claims",
        "`DRAFT`, `UNKNOWN`, `PUBLISH_BLOCKED`",
    ):
        assert fragment in report, f"report is missing: {fragment!r}"

    # 10 pages, and the report must not claim public distribution.
    assert "| Page count | 10 |" in report
    for overclaim in ("publicly available", "freely available", "may redistribute"):
        assert overclaim not in report
