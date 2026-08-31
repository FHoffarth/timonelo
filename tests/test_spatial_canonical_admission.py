"""
Guards the positive admission boundary for governed spatial state.

The defect this closes: `ShipPatchEngine` produces sister-ship hypotheses in a
`QuarantinedVesselSpatialOntology`, and the old gate rejected that by
`isinstance`. Copying the fields into a plain `VesselSpatialOntology` dropped
the marker and the gate opened -- same geometry, same borrowed evidence, no
quarantine. A marker a caller can drop is not a boundary.

So none of these tests assert on class identity, and the boundary does not read
it. Admission is computed from the evidence each fact carries, which survives
copying because it *is* the fact. The laundering test below copies a quarantined
ontology field-for-field into a plain one and expects rejection anyway.

The positive fixture is real: it cites ART-0001 by its actual vault digest,
recomputed from held bytes, with the registry's own Bellissima attribution. It
exists to prove the gate can be satisfied without being weakened -- every one of
the eight requirements is exercised, not stubbed.
"""

from __future__ import annotations

import json
import pathlib
from typing import List, Optional

import pytest

from timonelo.evidence.registry import ArtifactRegistry
from timonelo.factory.compiler import KnowledgeFactoryCompiler
from timonelo.ontology.models import (
    BalconyType,
    Cabin,
    Coordinate2D,
    CorridorNode,
    Deck,
    DeckVerticalZone,
    Derivation,
    DoorNode,
    EvidenceCondition,
    EvidenceLink,
    HullSide,
    HumanReviewState,
    Method,
    PowerSocketMatrix,
    QuarantinedVesselSpatialOntology,
    Venue,
    VenueCategory,
    VesselSpatialOntology,
)
from timonelo.spatial.admission import (
    AdmissionRejection,
    SpatialAdmissionError,
    evaluate_admission,
    require_admission,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = REPO_ROOT / "evidence" / "artifacts"

BELLISSIMA_IMO = "IMO9766205"
GRANDIOSA_IMO = "IMO9803613"
ANDORINHA_ENI = "ENI02338573"


@pytest.fixture(scope="module")
def registry() -> ArtifactRegistry:
    return ArtifactRegistry(str(ARTIFACTS_ROOT))


@pytest.fixture(scope="module")
def held_digest(registry) -> str:
    """ART-0001's real digest, as held in the SHA vault."""
    return registry.get("ART-0001").sha256


def admissible_link(held_digest: str, **overrides) -> EvidenceLink:
    """An link satisfying all eight requirements, before any override."""
    base = dict(
        source_id="ART-0001",
        locator="Page 5, Deck 14 (World Class) plan",
        sha256=held_digest,
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    base.update(overrides)
    return EvidenceLink(**base)


def build_ontology(
    links: Optional[List[EvidenceLink]],
    *,
    imo: str = BELLISSIMA_IMO,
    quarantined: bool = False,
    source_vessel_imo: str = "",
) -> VesselSpatialOntology:
    """One deck, one cabin, one venue -- the smallest governed spatial state."""
    polygon = [
        Coordinate2D(0.50, 0.10), Coordinate2D(0.52, 0.10),
        Coordinate2D(0.52, 0.20), Coordinate2D(0.50, 0.20),
    ]
    node = CorridorNode(
        node_id="D14_N1", deck_number=14,
        coordinate=Coordinate2D(0.50, 0.00), is_elevator_lobby=True,
    )
    cabin = Cabin(
        cabin_number="14001", deck_number=14, hull_side=HullSide.STARBOARD,
        category_code="BR2", boundary_polygon=polygon,
        door=DoorNode(
            door_id="D14_C1_DOOR", deck_number=14,
            coordinate=Coordinate2D(0.50, 0.05), corridor_snap_node_id="D14_N1",
        ),
        square_meters=18.0, balcony_type=BalconyType.UNOBSTRUCTED,
        sockets=PowerSocketMatrix(2, 2, 2, 1, True),
        evidence_links=list(links) if links is not None else [],
    )
    venue = Venue(
        venue_id="D14_V1", name="Fixture Lounge", deck_number=14,
        category=VenueCategory.BAR_LOUNGE, boundary_polygon=polygon,
        entrance_node_ids=["D14_N1"], is_noise_generator=False,
        is_open_deck=False,
        evidence_links=list(links) if links is not None else [],
    )
    deck = Deck(
        deck_number=14, name="World Class", elevation_meters=40.0,
        perimeter_polygon=polygon, zone=DeckVerticalZone.RESIDENTIAL_UPPER,
        cabins={"14001": cabin}, venues={"D14_V1": venue},
        corridor_nodes={"D14_N1": node}, corridor_edges=[],
    )
    kwargs = dict(
        imo_number=imo, name="Admission Fixture", ship_class="Fixture Class",
        length_overall_meters=100.0, beam_meters=20.0, total_decks=1,
        decks={14: deck},
    )
    if quarantined:
        return QuarantinedVesselSpatialOntology(
            source_vessel_imo=source_vessel_imo or BELLISSIMA_IMO, **kwargs
        )
    return VesselSpatialOntology(**kwargs)


def reasons_for(ontology, registry) -> set:
    return set(evaluate_admission(ontology, registry=registry).reason_codes)


# -- 1. the positive fixture -------------------------------------------------

def test_valid_fixture_is_admitted(registry, held_digest):
    result = evaluate_admission(
        build_ontology([admissible_link(held_digest)]), registry=registry
    )
    assert result.admitted is True
    assert result.rejections == []
    assert result.facts_examined == 2          # one cabin, one venue
    assert result.facts_admitted == 2
    assert result.links_examined == 2
    assert result.reason_codes == ()


def test_the_positive_fixture_is_not_a_stub(registry, held_digest):
    """Each of the eight requirements is really exercised, not bypassed."""
    from timonelo.evidence.registry import sha256_of_file

    link = admissible_link(held_digest)
    artifact = registry.get(link.source_id)                       # 1 registered
    assert link.is_content_addressed                              # 2 addressed
    path = registry.resolve_path(artifact.artifact_id)
    assert path is not None and sha256_of_file(path) == link.sha256   # 3 re-verified
    assert link.method is not None and link.derivation is not None    # 4 classified
    assert link.derivation is Derivation.LOCAL                        # 5 canonical
    assert link.evidence_condition is EvidenceCondition.SUPPORTED     # 6
    assert link.human_review_state is HumanReviewState.APPROVED       # 7
    assert registry.artifact_establishes_vessel(                      # 8 this vessel
        artifact.artifact_id, BELLISSIMA_IMO) is True


# -- 2..11 one requirement removed at a time --------------------------------

def test_missing_evidence_link_rejects(registry):
    assert AdmissionRejection.NO_EVIDENCE_LINK in reasons_for(
        build_ontology([]), registry)


def test_unknown_artifact_rejects(registry, held_digest):
    assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in reasons_for(
        build_ontology([admissible_link(held_digest, source_id="EVID-GA-BELLISSIMA-REV4")]),
        registry)


def test_artifact_not_held_rejects(registry):
    """ART-0007 is registered and private; its bytes are not in the vault."""
    assert registry.resolve_path("ART-0007") is None
    link = EvidenceLink(
        source_id="ART-0007", locator="booking confirmation",
        sha256="a" * 64, method=Method.DIRECT, derivation=Derivation.LOCAL,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    assert AdmissionRejection.ARTIFACT_NOT_HELD in reasons_for(
        build_ontology([link]), registry)


def test_missing_digest_rejects(registry, held_digest):
    assert AdmissionRejection.NOT_CONTENT_ADDRESSED in reasons_for(
        build_ontology([admissible_link(held_digest, sha256=None)]), registry)


def test_digest_mismatch_rejects(registry, held_digest):
    """A well-formed digest that is not this artifact's bytes."""
    wrong = "b" * 64
    assert wrong != held_digest
    assert AdmissionRejection.DIGEST_MISMATCH in reasons_for(
        build_ontology([admissible_link(held_digest, sha256=wrong)]), registry)


def test_unclassified_derivation_rejects(registry, held_digest):
    """Bellissima's real links look exactly like this: derivation is None."""
    assert AdmissionRejection.UNCLASSIFIED_PROVENANCE in reasons_for(
        build_ontology([admissible_link(held_digest, derivation=None)]), registry)
    assert AdmissionRejection.UNCLASSIFIED_PROVENANCE in reasons_for(
        build_ontology([admissible_link(held_digest, method=None)]), registry)


@pytest.mark.parametrize(
    "derivation",
    [Derivation.GENERATED, Derivation.SISTER_SHIP, Derivation.REFERENCE_MODEL],
)
def test_non_canonical_derivation_rejects(registry, held_digest, derivation):
    assert AdmissionRejection.DERIVATION_NOT_CANONICAL in reasons_for(
        build_ontology([admissible_link(held_digest, derivation=derivation)]), registry)


@pytest.mark.parametrize(
    "condition",
    [EvidenceCondition.UNKNOWN, EvidenceCondition.UNSUPPORTED, EvidenceCondition.CONFLICTED],
)
def test_condition_not_supported_rejects(registry, held_digest, condition):
    assert AdmissionRejection.EVIDENCE_NOT_SUPPORTED in reasons_for(
        build_ontology([admissible_link(held_digest, evidence_condition=condition)]),
        registry)


@pytest.mark.parametrize(
    "state",
    [HumanReviewState.DRAFT, HumanReviewState.UNDER_REVIEW,
     HumanReviewState.REJECTED, HumanReviewState.SUPERSEDED],
)
def test_review_not_approved_rejects(registry, held_digest, state):
    assert AdmissionRejection.REVIEW_NOT_APPROVED in reasons_for(
        build_ontology([admissible_link(held_digest, human_review_state=state)]),
        registry)


def test_sister_vessel_rejects(registry, held_digest):
    """The same admissible link, offered for Grandiosa instead."""
    admitted = evaluate_admission(
        build_ontology([admissible_link(held_digest)]), registry=registry)
    assert admitted.admitted is True

    sister = build_ontology([admissible_link(held_digest)], imo=GRANDIOSA_IMO)
    assert AdmissionRejection.ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL in reasons_for(
        sister, registry)


# -- 12. universal quantification -------------------------------------------

def test_one_good_link_cannot_mask_one_bad_link(registry, held_digest):
    """Adding evidence must never subtract scrutiny."""
    good = admissible_link(held_digest)
    bad = admissible_link(held_digest, derivation=Derivation.GENERATED)
    for links in ([good, bad], [bad, good]):
        result = evaluate_admission(build_ontology(links), registry=registry)
        assert result.admitted is False
        assert AdmissionRejection.DERIVATION_NOT_CANONICAL in set(result.reason_codes)


# -- 13. the laundering path ------------------------------------------------

def test_rewrapping_quarantined_state_into_a_plain_ontology_still_rejects(registry):
    """The original defect, reproduced end to end.

    A sister-ship hypothesis is copied field-for-field into a plain
    `VesselSpatialOntology`. The quarantine wrapper is gone; the evidence is
    not. Rejection must come from the evidence, so the assertions below check
    the *reason*, not merely that it failed.
    """
    hypothesis_link = EvidenceLink(
        source_id="ART-0001", locator="sister-ship hypothesis",
        sha256=registry.get("ART-0001").sha256,
        method=Method.INFERRED, derivation=Derivation.SISTER_SHIP,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    quarantined = build_ontology(
        [hypothesis_link], imo=GRANDIOSA_IMO,
        quarantined=True, source_vessel_imo=BELLISSIMA_IMO,
    )
    assert isinstance(quarantined, QuarantinedVesselSpatialOntology)

    # Launder: plain type, same fields, marker dropped.
    laundered = VesselSpatialOntology(
        imo_number=quarantined.imo_number, name=quarantined.name,
        ship_class=quarantined.ship_class,
        length_overall_meters=quarantined.length_overall_meters,
        beam_meters=quarantined.beam_meters, total_decks=quarantined.total_decks,
        decks=dict(quarantined.decks),
    )
    assert type(laundered) is VesselSpatialOntology
    assert not isinstance(laundered, QuarantinedVesselSpatialOntology)
    assert not hasattr(laundered, "source_vessel_imo")

    reasons = reasons_for(laundered, registry)
    assert AdmissionRejection.DERIVATION_NOT_CANONICAL in reasons
    assert AdmissionRejection.ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL in reasons


def test_deep_copied_and_reconstructed_state_rejects_identically(registry):
    import copy

    hypothesis_link = EvidenceLink(
        source_id="ART-0001", locator="hypothesis",
        sha256=registry.get("ART-0001").sha256,
        method=Method.INFERRED, derivation=Derivation.GENERATED,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    original = build_ontology([hypothesis_link])
    assert reasons_for(copy.deepcopy(original), registry) == reasons_for(original, registry)


def test_admission_does_not_consult_the_class(registry, held_digest):
    """A quarantined wrapper with admissible evidence is judged on evidence.

    This is the mirror of the laundering test, and it is what proves the gate
    is not the old isinstance check wearing a new name.
    """
    quarantined = build_ontology(
        [admissible_link(held_digest)], quarantined=True,
        source_vessel_imo="IMO9803613",
    )
    assert evaluate_admission(quarantined, registry=registry).admitted is True


# -- 14, 15, 19, 20. writer containment -------------------------------------

def test_compiler_refuses_and_writes_nothing(registry, tmp_path):
    ontology = build_ontology([admissible_link(registry.get("ART-0001").sha256,
                                               derivation=Derivation.GENERATED)])
    ok = KnowledgeFactoryCompiler.compile_vessel(
        ontology=ontology, output_data_dir=tmp_path,
        output_frontend_dir=tmp_path / "frontend",
    )
    assert ok is False
    assert list(tmp_path.rglob("*")) == [], "a refused compilation created output"


def test_admitted_fixture_reaches_both_sinks(registry, held_digest, tmp_path):
    ok = KnowledgeFactoryCompiler.compile_vessel(
        ontology=build_ontology([admissible_link(held_digest)]),
        output_data_dir=tmp_path, output_frontend_dir=tmp_path / "frontend",
    )
    assert ok is True
    canonical = tmp_path / "data/ships/admission-fixture/knowledge-pack.json"
    public = tmp_path / "frontend/public/data/admission-fixture.json"
    assert canonical.is_file() and public.is_file()
    assert json.loads(canonical.read_text(encoding="utf-8"))["imo"] == BELLISSIMA_IMO


def test_explorer_pack_cannot_bypass_admission():
    """It must route through the compiler, not serialize governed truth itself."""
    source = (REPO_ROOT / "tools/generate_explorer_pack.py").read_text(encoding="utf-8")
    assert "KnowledgeFactoryCompiler" in source
    # No independent serializer or writer of its own.
    assert "json.dump" not in source
    assert "open(" not in source
    assert "mkdir" not in source


def test_explorer_pack_refuses_on_the_real_ontology(tmp_path):
    """Run the tool for real: it must refuse and leave the sinks untouched."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "generate_explorer_pack_under_test",
        REPO_ROOT / "tools" / "generate_explorer_pack.py",
    )
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)

    assert tool.generate_explorer_pack(root_dir=tmp_path) is False
    assert list(tmp_path.rglob("*")) == [], "a refused generation created output"


# -- 16, 17, 18. the three live datasets ------------------------------------

def test_bellissima_fails_admission_on_unregistered_evidence(registry):
    """Attributing ART-0001 to Bellissima did not make its ontology admissible."""
    from timonelo.ontology.bellissima import create_bellissima_ontology

    result = evaluate_admission(create_bellissima_ontology(), registry=registry)
    assert result.admitted is False
    # Identity resolved, so evidence really was examined.
    assert result.vessel_imo == BELLISSIMA_IMO
    assert result.vessel_rejection is None
    assert result.links_examined > 5000
    assert set(result.reason_codes) == {AdmissionRejection.ARTIFACT_NOT_REGISTERED}


def test_andorinha_stops_at_the_identity_gate_not_on_its_evidence(registry):
    """Andorinha is ENI-identified, which the attribution primitive refuses.

    The distinction is recorded deliberately: its evidence was never evaluated,
    so reporting this as an evidence failure would misstate why it is out.
    """
    from timonelo.ontology.andorinha import create_andorinha_ontology

    ontology = create_andorinha_ontology()
    assert ontology.imo_number == ANDORINHA_ENI
    result = evaluate_admission(ontology, registry=registry)
    assert result.admitted is False
    assert result.vessel_rejection is AdmissionRejection.UNRESOLVABLE_VESSEL_IDENTITY
    assert result.links_examined == 0, "evidence must not be judged without an identity"
    assert result.rejections == []
    assert "no evidence was evaluated" in result.summary()


def test_grandiosa_legacy_derivative_gains_nothing_from_bellissima_evidence(registry):
    pack = REPO_ROOT / "data/hypotheses/legacy-derivatives/msc-grandiosa/knowledge-pack.json"
    document = json.loads(pack.read_text(encoding="utf-8"))
    assert document["imo"] == GRANDIOSA_IMO
    cited = {
        link["source_id"]
        for cabin in document["cabins"].values()
        for link in cabin.get("evidence", [])
    }
    assert any("BELLISSIMA" in source.upper() for source in cited)
    for source_id in cited:
        assert registry.artifact_establishes_vessel(source_id, GRANDIOSA_IMO) is False


# -- non-admitted output is not left in governed namespaces -----------------

def test_no_non_admitted_pack_remains_in_a_governed_namespace():
    canonical = REPO_ROOT / "data/ships"
    public = REPO_ROOT / "frontend/public/data"
    assert [p.name for p in canonical.rglob("*") if p.is_file()] == ["README.md"]
    assert not (public / "msc-bellissima.json").exists()
    assert not (public / "ms-andorinha.json").exists()
    assert not (public / "msc-grandiosa.json").exists()


def test_quarantined_packs_are_retained_not_destroyed():
    root = REPO_ROOT / "data/hypotheses"
    for relative in (
        "legacy-derivatives/msc-bellissima/knowledge-pack.json",
        "legacy-derivatives/ms-andorinha/knowledge-pack.json",
        "legacy-derivatives/msc-grandiosa/knowledge-pack.json",
        "legacy-runtime/msc-bellissima.json",
        "legacy-runtime/ms-andorinha.json",
    ):
        assert (root / relative).is_file(), f"{relative} was destroyed rather than quarantined"


# -- the gate raises for callers that are gates -----------------------------

def test_require_admission_raises_with_a_reason(registry, held_digest):
    with pytest.raises(SpatialAdmissionError) as excinfo:
        require_admission(
            build_ontology([admissible_link(held_digest, sha256=None)]), registry=registry)
    assert "NOT_CONTENT_ADDRESSED" in str(excinfo.value)


def test_empty_ontology_is_not_admitted_by_having_nothing_to_prove(registry):
    empty = VesselSpatialOntology(
        imo_number=BELLISSIMA_IMO, name="Empty", ship_class="X",
        length_overall_meters=1.0, beam_meters=1.0, total_decks=0, decks={},
    )
    result = evaluate_admission(empty, registry=registry)
    assert result.admitted is False
    assert result.vessel_rejection is AdmissionRejection.NO_GOVERNED_FACTS


def test_missing_vessel_identity_rejects(registry, held_digest):
    result = evaluate_admission(
        build_ontology([admissible_link(held_digest)], imo="   "), registry=registry)
    assert result.admitted is False
    assert result.vessel_rejection is AdmissionRejection.NO_VESSEL_IDENTITY
