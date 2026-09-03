"""
Tests for Voyage Knowledge Factory v1 (ADR-0002).
Deterministic, automated voyage intake, canonical ship/port resolution, gap detection,
and passenger trip knowledge pack compilation.
"""

import json
import os
from pathlib import Path
import pytest

from timonelo.evidence.workspace import Workspace
from timonelo.factory.voyage import (
    AdmissionDecision,
    AdmissionStatus,
    DEFAULT_APPROVED_VOYAGE_PARSERS,
    ParsedVoyageClaim,
    PassengerTripKnowledgePack,
    UNLOCODE_LINKAGE_RULE_HASH,
    VoyageGapRecord,
    VoyageIntakeInput,
    VoyageKnowledgeFactory,
    VoyageKnowledgeResult,
    is_admitted_truth,
)
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "evidence"


@pytest.fixture
def workspace():
    return Workspace(str(EVIDENCE_DIR))


@pytest.fixture
def factory(workspace):
    return VoyageKnowledgeFactory(workspace)


@pytest.fixture
def bellissima_input():
    return VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-10-04",
        departure_location="Shanghai, China",
        arrival_date="2026-10-07",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        check_in_time="14:00",
    )



def seed_backed_statements(ws_dir: Path, statements: dict) -> None:
    """Write seed statements together with the evidence that supports them.

    These fixtures used to write `evidence_event_ids: ["EVT-001"]` against
    `artifact_id: "TEST-ART-01"` -- an event that was never recorded, citing an
    artifact that was never registered. Publication admission is now checked on
    load, so fabricated backing no longer survives, and it should not: a
    fixture asserting published truth from a phantom event proves nothing.

    Each statement gets its own event observing that statement's own entity,
    question and value, against a real registered artifact whose document class
    may answer the question.
    """
    from timonelo.evidence import authority
    from timonelo.evidence.registry import ArtifactRegistry

    for sub in ("artifacts", "statements", "events", "reviews", "registry"):
        (ws_dir / sub).mkdir(parents=True, exist_ok=True)

    registry = ArtifactRegistry(str(ws_dir / "artifacts"))
    events = []
    seeded = {}

    for index, (sid, raw) in enumerate(statements.items(), start=1):
        record = dict(raw)
        # Only statements that claim publication need backing. The negative
        # fixtures deliberately seed DRAFT, PUBLISH_BLOCKED or CONFLICTED
        # records to prove they cannot resolve; giving those evidence would
        # change what they are testing, and registering an artifact for each
        # would make the suite slow for no gain.
        if record.get("publish_status") != "PUBLISH_ALLOWED":
            seeded[sid] = record
            continue
        statement_type = record["statement_type"]
        classes = authority.AUTHORITY.get(statement_type)
        if not classes:
            # No declared authority for this type, so no document class can
            # honestly back it. Left as seeded; admission will judge it.
            seeded[sid] = record
            continue
        document_class = classes[0]

        source = ws_dir / f"seed_source_{index}.txt"
        source.write_text(
            f"{record['entity_id']} {record['question_id']} {record['value']}",
            encoding="utf-8",
        )
        artifact = registry.register(
            path=str(source),
            document_class=document_class,
            acquired_on="2026-08-23",
            acquisition_method="test fixture",
        )

        event_id = f"EVT-SEED-{index:03d}"
        events.append({
            "event_id": event_id,
            "artifact_sha256": artifact.sha256,
            "locator": record.get("locator") or f"seed source {index}",
            "entity_id": record["entity_id"],
            "question_id": record["question_id"],
            "observed_value": record["value"],
            "observed_by": "fixture.observer",
            "observed_on": "2026-08-23",
            "supersedes": None,
            "notes": "",
        })
        record["artifact_id"] = artifact.artifact_id
        record["evidence_event_ids"] = [event_id]
        seeded[sid] = record

    (ws_dir / "events" / "events.json").write_text(
        json.dumps(events, indent=2), encoding="utf-8")
    (ws_dir / "statements" / "statements.json").write_text(
        json.dumps(seeded, indent=2), encoding="utf-8")


def test_bellissima_golden_fixture_no_longer_compiles_canonical_truth(factory, bellissima_input):
    """
    Golden Fixture: the MSC Bellissima reference voyage stops resolving.

    Every one of its facts was read from ART-0007, a private booking
    confirmation the repository registers by digest and deliberately does not
    store. Nobody can open it, so no reader can check a single one of these
    claims against its source, and the two port linkages additionally cite a
    rule no rule store holds. The statements were published anyway because
    PUBLISH_ALLOWED was written down once and never questioned again.

    This is the sprint's cost, stated rather than hidden: the repository's only
    voyage is not publishable truth. What it demonstrates is that the boundary
    binds the evidence the project actually cares about, not just fixtures
    built to fail. Restoring it means public evidence for these facts, or a
    policy decision that private sources may back publication -- not a change
    to what PUBLISH_ALLOWED means.
    """
    res = factory.create_or_get_voyage(bellissima_input)

    assert res.voyage_entity == "voyage:msc-bellissima:20261004-shanghai-tokyo"
    assert res.vessel is None
    assert res.departure_port is None
    assert res.arrival_port is None
    assert res.departure_date is None
    assert res.arrival_date is None
    assert res.check_in_time is None

    # Terminal & berth remain strictly UNKNOWN, as they always did
    assert res.departure_terminal is None
    assert res.departure_berth is None
    assert res.arrival_terminal is None
    assert res.arrival_berth is None

    # Nothing is published, and the refusal is visible rather than silent.
    assert res.publishability != PublishStatus.PUBLISH_ALLOWED
    assert res.known_facts == []
    assert res.gaps


def test_new_voyage_intake_in_isolated_workspace_with_parsed_claims(tmp_path):
    """
    Scaling Test: Ingesting a brand new synthetic voyage into an isolated workspace
    with verified ParsedVoyageClaims creates canonical EvidenceEvents, Statements,
    and INFERRED port linkages without hardcoding.
    """
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    # Seed reusable port statements (CNSGH, JPTYO) and reusable ship knowledge
    seed_statements = {
        "STM-0395": {
            "statement_id": "STM-0395",
            "entity_id": "port:unlocode:CNSGH",
            "question_id": "Q-0023",
            "statement_type": "port.un_locode",
            "value": "CNSGH",
            "artifact_id": "TEST-ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "evidence_event_ids": ["EVT-001"],
            "method": "DIRECT",
        },
        "STM-0396": {
            "statement_id": "STM-0396",
            "entity_id": "port:unlocode:CNSGH",
            "question_id": "Q-0024",
            "statement_type": "port.official_name",
            "value": "Shanghai",
            "artifact_id": "TEST-ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "evidence_event_ids": ["EVT-001"],
            "method": "DIRECT",
        },
        "STM-0397": {
            "statement_id": "STM-0397",
            "entity_id": "port:unlocode:JPTYO",
            "question_id": "Q-0023",
            "statement_type": "port.un_locode",
            "value": "JPTYO",
            "artifact_id": "TEST-ART-01",
            "locator": "row 2",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "evidence_event_ids": ["EVT-001"],
            "method": "DIRECT",
        },
        "STM-0398": {
            "statement_id": "STM-0398",
            "entity_id": "port:unlocode:JPTYO",
            "question_id": "Q-0024",
            "statement_type": "port.official_name",
            "value": "Tokyo",
            "artifact_id": "TEST-ART-01",
            "locator": "row 2",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "evidence_event_ids": ["EVT-001"],
            "method": "DIRECT",
        },
        "STM-0399": {
            "statement_id": "STM-0399",
            "entity_id": "ship:MSC-BELLISSIMA",
            "question_id": "Q-0030",
            "statement_type": "voyage.vessel",
            "value": "MSC BELLISSIMA",
            "artifact_id": "TEST-ART-01",
            "locator": "spec",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "evidence_event_ids": ["EVT-001"],
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, seed_statements)

    isolated_ws = Workspace(str(ws_dir))

    sample_file = tmp_path / "test_booking.pdf"
    sample_file.write_bytes(b"%PDF-1.4 test booking confirmation")
    art = isolated_ws.registry.register(
        path=str(sample_file),
        document_class="official_cruise_operator_booking_confirmation",
        acquired_on="2026-08-23",
        acquisition_method="test_fixture",
        publisher="MSC Cruises",
    )

    claims = (
        ParsedVoyageClaim(
            question_id="Q-0030",
            statement_type="voyage.vessel",
            value="MSC BELLISSIMA",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 block header",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0031",
            statement_type="voyage.departure_date",
            value="2026-11-15",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 field dep_date",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0032",
            statement_type="voyage.departure_location",
            value="Shanghai, China",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 field dep_port",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0034",
            statement_type="voyage.arrival_date",
            value="2026-11-20",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 field arr_date",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0035",
            statement_type="voyage.arrival_location",
            value="Tokyo, Japan",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 field arr_port",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0037",
            statement_type="voyage.check_in_time",
            value="11:30",
            artifact_id=art.artifact_id,
            locator="TEST_FIXTURE page 1 field checkin_time",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
    )

    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-11-15",
        departure_location="Shanghai, China",
        arrival_date="2026-11-20",
        arrival_location="Tokyo, Japan",
        artifact_id=art.artifact_id,
        check_in_time="11:30",
        claims=claims,
    )

    # Injected test parser whitelist in test environment
    iso_factory = VoyageKnowledgeFactory(
        isolated_ws,
        approved_parsers={"test_booking_parser:v1"},
    )

    # First intake: creates events and statements
    res = iso_factory.create_or_get_voyage(intake)
    assert res.voyage_entity == "voyage:msc-bellissima:20261115-shanghai-tokyo"
    assert res.input_departure_location == "Shanghai, China"
    assert res.input_arrival_location == "Tokyo, Japan"
    assert res.admission_decision.status == AdmissionStatus.AUTO_ADMISSIBLE

    # Check that events and statements were created
    voyage_stmts = [s for s in isolated_ws.editor.all() if s.entity_id == res.voyage_entity]
    assert len(voyage_stmts) == 8

    # Check inferred port linkage statement properties
    dep_port_stm = next(s for s in voyage_stmts if s.question_id == "Q-0033")
    assert dep_port_stm.method == Method.INFERRED
    assert dep_port_stm.value == "port:unlocode:CNSGH"
    assert dep_port_stm.rule_hash == UNLOCODE_LINKAGE_RULE_HASH
    assert dep_port_stm.input_statement_ids[0] == "STM-0395"

    arr_port_stm = next(s for s in voyage_stmts if s.question_id == "Q-0036")
    assert arr_port_stm.method == Method.INFERRED
    assert arr_port_stm.value == "port:unlocode:JPTYO"

    # Second intake on identical input: STRICT IDEMPOTENCY
    events_count_before = len(isolated_ws.events.all())
    stmts_count_before = len(isolated_ws.editor.all())

    res2 = iso_factory.create_or_get_voyage(intake)

    events_count_after = len(isolated_ws.events.all())
    stmts_count_after = len(isolated_ws.editor.all())

    assert res == res2
    assert events_count_before == events_count_after
    assert stmts_count_before == stmts_count_after


def test_missing_parsed_claims_does_not_author_statements(factory):
    """
    Authoritative artifact + empty parsed claims results in REVIEW_REQUIRED
    and does NOT create EvidenceEvents or Statements.
    """
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2027-05-01",
        departure_location="Shanghai, China",
        arrival_date="2027-05-05",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        claims=(),  # No parsed claims
    )
    res = factory.create_or_get_voyage(intake)

    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("No parsed claims provided" in r for r in res.admission_decision.reasons)

    # Check that zero statements were authored for this new entity
    created = [s for s in factory.workspace.editor.all() if s.entity_id == res.voyage_entity]
    assert len(created) == 0


def test_claim_input_value_mismatch_triggers_review_required(factory):
    """
    Mismatch between intake value (2026-11-15) and parsed claim value (2026-11-16)
    triggers REVIEW_REQUIRED and blocks authoring.
    """
    claims = (
        ParsedVoyageClaim(
            question_id="Q-0030",
            statement_type="voyage.vessel",
            value="MSC BELLISSIMA",
            artifact_id="ART-0007",
            locator="line 1",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0031",
            statement_type="voyage.departure_date",
            value="2026-11-16",  # Mismatch with intake 2026-11-15
            artifact_id="ART-0007",
            locator="line 2",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0032",
            statement_type="voyage.departure_location",
            value="Shanghai, China",
            artifact_id="ART-0007",
            locator="line 3",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0034",
            statement_type="voyage.arrival_date",
            value="2026-11-20",
            artifact_id="ART-0007",
            locator="line 4",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
        ParsedVoyageClaim(
            question_id="Q-0035",
            statement_type="voyage.arrival_location",
            value="Tokyo, Japan",
            artifact_id="ART-0007",
            locator="line 5",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
    )

    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-11-15",
        departure_location="Shanghai, China",
        arrival_date="2026-11-20",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        claims=claims,
    )
    res = factory.create_or_get_voyage(intake)

    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("Claim value mismatch for Q-0031" in r for r in res.admission_decision.reasons)

    # Confirm no statements were authored
    created = [s for s in factory.workspace.editor.all() if s.entity_id == res.voyage_entity]
    assert len(created) == 0


def test_missing_locator_triggers_review_required(factory):
    """Parsed claim with an empty locator triggers REVIEW_REQUIRED."""
    claims = (
        ParsedVoyageClaim(
            question_id="Q-0030",
            statement_type="voyage.vessel",
            value="MSC BELLISSIMA",
            artifact_id="ART-0007",
            locator="",  # Empty locator
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
    )
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-11-15",
        departure_location="Shanghai, China",
        arrival_date="2026-11-20",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        claims=claims,
    )
    res = factory.create_or_get_voyage(intake)

    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("missing a source locator" in r for r in res.admission_decision.reasons)


def test_production_parser_policy_does_not_admit_test_booking_parser(factory):
    """Production parser policy contains only genuine parsers and rejects test_booking_parser."""
    assert "test_booking_parser" not in DEFAULT_APPROVED_VOYAGE_PARSERS
    assert "test_booking_parser:v1" not in DEFAULT_APPROVED_VOYAGE_PARSERS

    claims = (
        ParsedVoyageClaim(
            question_id="Q-0030",
            statement_type="voyage.vessel",
            value="MSC BELLISSIMA",
            artifact_id="ART-0007",
            locator="line 1",
            parser_id="test_booking_parser:v1",
            parser_version="1.0",
        ),
    )
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-11-15",
        departure_location="Shanghai, China",
        arrival_date="2026-11-20",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        claims=claims,
    )
    res = factory.create_or_get_voyage(intake)

    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("not an approved voyage parser" in r for r in res.admission_decision.reasons)


def test_isolated_test_policy_explicitly_allows_injected_parser(workspace):
    """Dependency injection allows tests to explicitly configure allowed parser whitelist."""
    custom_factory = VoyageKnowledgeFactory(
        workspace,
        approved_parsers={"custom_test_parser:v1"},
    )
    assert custom_factory.approved_parsers == {"custom_test_parser:v1"}


def test_contradiction_against_existing_truth_triggers_review_required(factory):
    """A claim conflicting with existing canonical truth triggers REVIEW_REQUIRED."""
    # Bellissima reference voyage has departure date 2026-10-04
    claims = (
        ParsedVoyageClaim(
            question_id="Q-0031",
            statement_type="voyage.departure_date",
            value="2026-10-05",  # Conflicts with existing approved 2026-10-04
            artifact_id="ART-0007",
            locator="line 2",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
    )
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-10-04",
        departure_location="Shanghai, China",
        arrival_date="2026-10-07",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
        claims=claims,
    )
    res = factory.create_or_get_voyage(intake)

    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("Contradiction detected" in r for r in res.admission_decision.reasons)


def test_collision_safe_event_id_allocation(factory):
    """Deterministic event ID generation handles sparse/non-sequential event numbers."""
    event_id = factory._next_event_id()
    assert event_id.startswith("EVT-VOYAGE-")
    num = int(event_id.split("-")[-1])
    assert num >= 1


# --- Explicit Resolution Trust Boundary Tests ---

def test_draft_port_official_name_cannot_resolve_port(tmp_path):
    """DRAFT port.official_name cannot participate in port resolution."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-P01": {
            "statement_id": "STM-P01",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0023",
            "statement_type": "port.un_locode",
            "value": "TESTPORT",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
        "STM-P02": {
            "statement_id": "STM-P02",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0024",
            "statement_type": "port.official_name",
            "value": "DraftCity",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "DRAFT",  # DRAFT -> Not admitted truth
            "publish_status": "PUBLISH_BLOCKED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    port_ent, unlocode, is_unique, stmt_id = f.resolve_port("DraftCity")
    assert is_unique is False
    assert port_ent is None


def test_publish_blocked_port_unlocode_cannot_resolve_port(tmp_path):
    """PUBLISH_BLOCKED port.un_locode cannot participate in port resolution."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-P01": {
            "statement_id": "STM-P01",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0023",
            "statement_type": "port.un_locode",
            "value": "TESTPORT",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_BLOCKED",  # BLOCKED -> Not admitted truth
            "method": "DIRECT",
        },
        "STM-P02": {
            "statement_id": "STM-P02",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0024",
            "statement_type": "port.official_name",
            "value": "BlockedCity",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    port_ent, unlocode, is_unique, stmt_id = f.resolve_port("BlockedCity")
    assert is_unique is False
    assert port_ent is None


def test_conflicted_reusable_port_evidence_cannot_resolve_port(tmp_path):
    """UNSUPPORTED or CONFLICTED reusable port evidence cannot resolve a port."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-P01": {
            "statement_id": "STM-P01",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0023",
            "statement_type": "port.un_locode",
            "value": "TESTPORT",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "UNSUPPORTED",  # UNSUPPORTED -> Not admitted truth
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
        "STM-P02": {
            "statement_id": "STM-P02",
            "entity_id": "port:unlocode:TESTPORT",
            "question_id": "Q-0024",
            "statement_type": "port.official_name",
            "value": "UnsupportedCity",
            "artifact_id": "ART-01",
            "locator": "row 1",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    port_ent, unlocode, is_unique, stmt_id = f.resolve_port("UnsupportedCity")
    assert is_unique is False
    assert port_ent is None


def test_draft_cabin_venue_existence_cannot_establish_ship_identity(tmp_path):
    """Storage presence of cabin/venue entities (even in DRAFT/APPROVED) cannot establish ship identity."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-C01": {
            "statement_id": "STM-C01",
            "entity_id": "cabin:GHOST-SHIP:14122",
            "question_id": "Q-0001",
            "statement_type": "cabin.exists",
            "value": "true",
            "artifact_id": "ART-01",
            "locator": "deck 14",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
        "STM-V01": {
            "statement_id": "STM-V01",
            "entity_id": "venue:GHOST-SHIP:atrium",
            "question_id": "Q-0010",
            "statement_type": "venue.name",
            "value": "Grand Atrium",
            "artifact_id": "ART-01",
            "locator": "deck 5",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    ship_ent, vessel_name, is_unique = f.resolve_ship_identity("Ghost Line", "Ghost Ship")
    assert is_unique is False
    assert ship_ent is None


def test_blocked_vessel_identity_cannot_establish_ship_identity(tmp_path):
    """A vessel identity statement that is PUBLISH_BLOCKED / DRAFT cannot establish ship identity."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-S01": {
            "statement_id": "STM-S01",
            "entity_id": "ship:BLOCKED-VESSEL",
            "question_id": "Q-0030",
            "statement_type": "voyage.vessel",
            "value": "BLOCKED VESSEL",
            "artifact_id": "ART-01",
            "locator": "spec",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "DRAFT",  # DRAFT -> Not admitted truth
            "publish_status": "PUBLISH_BLOCKED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    ship_ent, vessel_name, is_unique = f.resolve_ship_identity("Test Line", "Blocked Vessel")
    assert is_unique is False
    assert ship_ent is None


def test_approved_supported_publish_allowed_reusable_facts_resolve_normally(factory):
    """Approved, supported, publish-allowed reusable facts resolve normally."""
    port_ent, unlocode, is_unique, stmt_id = factory.resolve_port("Shanghai, China")
    assert is_unique is True
    assert port_ent == "port:unlocode:CNSGH"
    assert unlocode == "CNSGH"
    assert stmt_id == "STM-0395"

    # Ship identity does not resolve, and for a different reason than the ports
    # above: the only statement naming this vessel is STM-0403, read from the
    # private booking confirmation. The public UN/LOCODE facts are unaffected,
    # which is the point -- authority is withdrawn from the claims whose
    # evidence cannot be re-read, not from the workspace.
    ship_ent, vessel_name, is_unique_ship = factory.resolve_ship_identity("MSC Cruises", "MSC Bellissima")
    assert is_unique_ship is False
    assert ship_ent is None
    assert vessel_name is None


def test_blocked_terminal_infrastructure_never_reaches_passenger_pack(tmp_path):
    """PUBLISH_BLOCKED cruise terminal statement never appears in PassengerTripKnowledgePack."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-T01": {
            "statement_id": "STM-T01",
            "entity_id": "terminal:JPTYO:draft-terminal",
            "question_id": "Q-0025",
            "statement_type": "cruise_terminal.official_name",
            "value": "Draft Terminal Facility",
            "artifact_id": "ART-01",
            "locator": "directory",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_BLOCKED",  # BLOCKED -> Must NOT appear in pack
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    pack = f.build_passenger_pack(
        voyage_entity="voyage:test:20261004-test-test",
        arr_port_entity="port:unlocode:JPTYO",
        gaps=[],
    )
    assert len(pack.known_generic_infrastructure) == 0


def test_approved_but_unsupported_terminal_infrastructure_never_reaches_passenger_pack(tmp_path):
    """Approved but UNSUPPORTED cruise terminal statement never appears in PassengerTripKnowledgePack."""
    ws_dir = tmp_path / "evidence"
    ws_dir.mkdir(parents=True)
    (ws_dir / "artifacts").mkdir()
    (ws_dir / "events").mkdir()
    (ws_dir / "statements").mkdir()
    (ws_dir / "registry").mkdir()
    (ws_dir / "raw" / "sha256").mkdir(parents=True)

    import shutil
    shutil.copy2(EVIDENCE_DIR / "registry" / "questions.json", ws_dir / "registry" / "questions.json")
    shutil.copy2(EVIDENCE_DIR / "registry" / "document_classes.json", ws_dir / "registry" / "document_classes.json")
    (ws_dir / "events" / "events.json").write_text("[]", encoding="utf-8")
    (ws_dir / "artifacts" / "index.json").write_text("{}", encoding="utf-8")

    stmts = {
        "STM-T01": {
            "statement_id": "STM-T01",
            "entity_id": "terminal:JPTYO:unsupported-terminal",
            "question_id": "Q-0025",
            "statement_type": "cruise_terminal.official_name",
            "value": "Unsupported Terminal Facility",
            "artifact_id": "ART-01",
            "locator": "directory",
            "read_by": "test",
            "read_on": "2026-08-23",
            "evidence_condition": "UNSUPPORTED",  # UNSUPPORTED -> Must NOT appear in pack
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_ALLOWED",
            "method": "DIRECT",
        },
    }
    seed_backed_statements(ws_dir, stmts)

    ws = Workspace(str(ws_dir))
    f = VoyageKnowledgeFactory(ws)
    pack = f.build_passenger_pack(
        voyage_entity="voyage:test:20261004-test-test",
        arr_port_entity="port:unlocode:JPTYO",
        gaps=[],
    )
    assert len(pack.known_generic_infrastructure) == 0


def test_unknown_ship_triggers_review_required(factory):
    """Unknown or unmapped ship names trigger REVIEW_REQUIRED."""
    intake = VoyageIntakeInput(
        cruise_line="Virgin Voyages",
        ship_name="Scarlet Lady",
        departure_date="2026-10-04",
        departure_location="Shanghai, China",
        arrival_date="2026-10-07",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0007",
    )
    res = factory.create_or_get_voyage(intake)
    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("Unknown or unmapped ship" in r for r in res.admission_decision.reasons)


def test_missing_artifact_triggers_review_required(factory):
    """Naked user input without an authoritative source artifact triggers REVIEW_REQUIRED."""
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-10-04",
        departure_location="Shanghai, China",
        arrival_date="2026-10-07",
        arrival_location="Tokyo, Japan",
        artifact_id=None,
    )
    res = factory.create_or_get_voyage(intake)
    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("No authoritative source artifact" in r for r in res.admission_decision.reasons)


def test_unsupported_document_class_triggers_review_required(factory, workspace):
    """An artifact with a document class not authoritative for voyage facts triggers REVIEW_REQUIRED."""
    claims = (
        ParsedVoyageClaim(
            question_id="Q-0030",
            statement_type="voyage.vessel",
            value="MSC BELLISSIMA",
            artifact_id="ART-0002",
            locator="deck map title",
            parser_id="msc_booking_pdf_parser:v1",
            parser_version="1.0",
        ),
    )
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2026-10-04",
        departure_location="Shanghai, China",
        arrival_date="2026-10-07",
        arrival_location="Tokyo, Japan",
        artifact_id="ART-0002",  # official_ship_map
        claims=claims,
    )
    res = factory.create_or_get_voyage(intake)
    assert res.admission_decision.status == AdmissionStatus.REVIEW_REQUIRED
    assert any("has no authority over" in r for r in res.admission_decision.reasons)


def test_passenger_pack_and_result_trust_boundary(factory):
    """
    PassengerTripKnowledgePack and VoyageKnowledgeResult expose only truth-verified values,
    leaving unverified fields as None / UNVERIFIED while preserving input intent.
    """
    intake = VoyageIntakeInput(
        cruise_line="MSC Cruises",
        ship_name="MSC Bellissima",
        departure_date="2027-01-01",  # Unverified future sailing
        departure_location="Fictional Port, Wonderland",
        arrival_date="2027-01-05",
        arrival_location="Imaginary Harbor, Atlantis",
        artifact_id=None,
    )
    res = factory.create_or_get_voyage(intake)

    # Input intent is captured
    assert res.input_vessel == "MSC BELLISSIMA"
    assert res.input_departure_date == "2027-01-01"

    # Truth-derived canonical fields are None (unverified)
    assert res.vessel is None
    assert res.departure_date is None
    assert res.departure_location is None
    assert res.departure_port is None
    assert res.arrival_date is None
    assert res.arrival_location is None
    assert res.arrival_port is None

    # Passenger pack reflects UNVERIFIED
    pack = res.passenger_pack
    assert pack.departure_date == "UNVERIFIED"
    assert pack.departure_location == "UNVERIFIED"
    assert pack.departure_port_unlocode is None
    assert pack.arrival_date == "UNVERIFIED"
    assert pack.arrival_location == "UNVERIFIED"
    assert pack.arrival_port_unlocode is None


def test_generic_infrastructure_is_dynamically_discovered(factory, bellissima_input):
    """
    Generic infrastructure for destination port (Tokyo) is discovered dynamically
    from approved workspace statements without hardcoded location checks.
    """
    res = factory.create_or_get_voyage(bellissima_input)
    infra = res.passenger_pack.known_generic_infrastructure

    assert len(infra) >= 1
    assert any("東京国際クルーズターミナル" in item["name"] for item in infra)
    for item in infra:
        assert "unconfirmed" in item["notice"].lower()


def test_first_class_gaps_representation(factory, bellissima_input):
    """Gaps (Q-0038..Q-0041) are first-class records, not pipeline failures."""
    res = factory.create_or_get_voyage(bellissima_input)
    assert len(res.gaps) == 4
    gap_qids = {g.question_id for g in res.gaps}
    assert gap_qids == {"Q-0038", "Q-0039", "Q-0040", "Q-0041"}
    for gap in res.gaps:
        assert gap.status == "UNKNOWN"
        assert gap.needed_source_class == "port_authority_berth_directory"
