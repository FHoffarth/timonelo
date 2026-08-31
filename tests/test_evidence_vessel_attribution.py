"""
Guards the registry-side vessel attribution primitive.

Spatial admission needs to answer one question before it can admit any vessel
geometry: does this document actually speak for this ship? Nothing in the
repository could answer it. Filenames, publishers and free-text notes all name
vessels, and all of them are exactly the kind of string the sister-ship
confusion is made of — `data/ships/msc-grandiosa/knowledge-pack.json` carries
`EVID-GA-BELLISSIMA-REV4` under Grandiosa's IMO precisely because no mechanism
ever checked.

The attribution therefore lives on the registry record, beside the digest, and
is reachable only through a registered artifact ID. A caller assembling an
`EvidenceLink` or a `VesselSpatialOntology` can choose which artifact to cite;
it cannot change what that artifact is attributed to.

Absence of attribution is UNKNOWN and answers False. It never means "any
vessel".
"""

from __future__ import annotations

import json
import pathlib

import pytest

from timonelo.evidence.registry import (
    Artifact,
    ArtifactRegistry,
    RegistryError,
    normalize_subject_vessels,
    normalize_vessel_imo,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = REPO_ROOT / "evidence" / "artifacts"
INDEX_PATH = ARTIFACTS_ROOT / "index.json"

BELLISSIMA_IMO = "IMO9766205"
GRANDIOSA_IMO = "IMO9803613"

#: The two artifacts whose own cover page names their subject vessel.
ATTRIBUTED = {"ART-0001", "ART-0002"}


@pytest.fixture()
def registry() -> ArtifactRegistry:
    return ArtifactRegistry(str(ARTIFACTS_ROOT))


def _artifact(**overrides) -> Artifact:
    base = dict(
        artifact_id="ART-TEST",
        sha256="a" * 64,
        filename="fixture.pdf",
        document_class="cruise_line_deck_plan",
        acquired_on="2026-08-25",
        acquisition_method="fixture",
    )
    base.update(overrides)
    return Artifact(**base)


# -- 1. correctly attributed artifact -> true for the correct vessel ---------

def test_attributed_artifact_establishes_its_own_vessel(registry):
    assert registry.artifact_establishes_vessel("ART-0001", BELLISSIMA_IMO) is True
    assert registry.artifact_establishes_vessel("ART-0002", BELLISSIMA_IMO) is True
    assert registry.vessels_established_by("ART-0001") == (BELLISSIMA_IMO,)


# -- 2. THE COUNTEREXAMPLE: same artifact -> false for a sister vessel -------

def test_bellissima_artifact_cannot_establish_grandiosa(registry):
    """The sister-ship trust boundary, stated on stable IMO identities.

    ART-0001 is the MSC Bellissima deck plan. MSC Grandiosa is a Meraviglia-class
    sister: same yard, same general arrangement, different hull. The existing
    Grandiosa knowledge pack cites Bellissima's GA drawing, which is the defect
    this primitive exists to make impossible to repeat silently.
    """
    assert BELLISSIMA_IMO != GRANDIOSA_IMO
    assert registry.artifact_establishes_vessel("ART-0001", BELLISSIMA_IMO) is True
    assert registry.artifact_establishes_vessel("ART-0001", GRANDIOSA_IMO) is False
    assert registry.artifact_establishes_vessel("ART-0002", GRANDIOSA_IMO) is False
    assert GRANDIOSA_IMO not in registry.vessels_established_by("ART-0001")


def test_the_grandiosa_pack_still_cites_a_bellissima_artifact(registry):
    """The live counterexample, so the regression is anchored to real data."""
    pack = REPO_ROOT / "data/ships/msc-grandiosa/knowledge-pack.json"
    if not pack.is_file():
        pytest.skip("legacy Grandiosa derivative has been quarantined elsewhere")
    document = json.loads(pack.read_text(encoding="utf-8"))
    assert document["imo"] == GRANDIOSA_IMO
    cited = {
        link["source_id"]
        for cabin in document["cabins"].values()
        for link in cabin.get("evidence", [])
    }
    assert any("BELLISSIMA" in source_id.upper() for source_id in cited), (
        "expected the legacy derivative to cite Bellissima evidence"
    )
    # Whatever it cites, it cannot be attributed to Grandiosa through the
    # registry, which is the whole point.
    for artifact_id in ATTRIBUTED:
        assert registry.artifact_establishes_vessel(artifact_id, GRANDIOSA_IMO) is False


# -- 3. unattributed artifact -> false --------------------------------------

def test_unattributed_artifacts_answer_false(registry):
    for artifact_id in ("ART-0003", "ART-0004", "ART-0005", "ART-0006", "ART-0007"):
        assert registry.vessels_established_by(artifact_id) == ()
        assert registry.artifact_establishes_vessel(artifact_id, BELLISSIMA_IMO) is False
        assert registry.artifact_establishes_vessel(artifact_id, GRANDIOSA_IMO) is False


def test_unheld_private_artifact_is_not_attributed(registry):
    """ART-0007's filename names Bellissima; its bytes are not held.

    Filename inference is exactly what this primitive refuses, so an artifact
    whose content cannot be inspected stays UNKNOWN however suggestive its
    name is.
    """
    artifact = registry.get("ART-0007")
    assert "BELLISSIMA" in artifact.filename.upper()
    assert artifact.private_source is True
    assert registry.resolve_path("ART-0007") is None
    assert registry.artifact_establishes_vessel("ART-0007", BELLISSIMA_IMO) is False


# -- 4. unknown artifact -> fail closed -------------------------------------

def test_unknown_artifact_fails_closed(registry):
    for unknown in ("ART-9999", "", "not-an-id", "0" * 64):
        assert registry.artifact_establishes_vessel(unknown, BELLISSIMA_IMO) is False
        assert registry.vessels_established_by(unknown) == ()
    # The stricter lookup still raises; only the trust gate softens to False.
    with pytest.raises(RegistryError):
        registry.get("ART-9999")


# -- 5. multiple explicitly attributed vessels ------------------------------

def test_multiple_attribution_is_supported_and_exact():
    artifact = _artifact(subject_vessels=[GRANDIOSA_IMO, BELLISSIMA_IMO])
    assert artifact.establishes_vessel(BELLISSIMA_IMO) is True
    assert artifact.establishes_vessel(GRANDIOSA_IMO) is True
    # Still exact: a third vessel is not implied by breadth.
    assert artifact.establishes_vessel("IMO9895609") is False


# -- 6. the caller cannot override attribution ------------------------------

def test_evidence_link_cannot_carry_or_override_vessel_attribution(registry):
    """Attribution is reachable only through the registry record."""
    from timonelo.ontology.models import EvidenceLink

    link = EvidenceLink(
        source_id="ART-0001",
        locator="Cover page 1",
        sha256=registry.get("ART-0001").sha256,
    )
    # There is no vessel-bearing field to set.
    assert not hasattr(link, "subject_vessels")
    assert not hasattr(link, "vessel_imo")
    assert not any("vessel" in f or "imo" in f for f in vars(link))

    # And the registry's answer is unchanged by anything the caller holds.
    assert registry.artifact_establishes_vessel(link.source_id, GRANDIOSA_IMO) is False
    assert registry.artifact_establishes_vessel(link.source_id, BELLISSIMA_IMO) is True


def test_mutating_a_returned_artifact_cannot_widen_attribution(registry):
    artifact = registry.get("ART-0001")
    with pytest.raises(Exception):
        artifact.subject_vessels = (BELLISSIMA_IMO, GRANDIOSA_IMO)  # type: ignore[misc]
    # A caller may build its own copy, but that copy is not the registry.
    assert registry.artifact_establishes_vessel("ART-0001", GRANDIOSA_IMO) is False


def test_ontology_identity_does_not_influence_the_answer(registry):
    """Asking on behalf of Grandiosa does not make the answer Grandiosa."""
    for asking_vessel in (GRANDIOSA_IMO, BELLISSIMA_IMO):
        answer = registry.artifact_establishes_vessel("ART-0001", asking_vessel)
        assert answer is (asking_vessel == BELLISSIMA_IMO)


# -- 7. malformed / invalid IMO rejected ------------------------------------

def test_invalid_imo_identities_are_rejected():
    # IMO9766206 is IMO9766205 with a broken check digit.
    for bad in ("IMO9766206", "IMO123", "", "MSC Bellissima", "msc-bellissima",
                "IMO97662050", "IMOABCDEFG", "9766206"):
        with pytest.raises(RegistryError):
            normalize_vessel_imo(bad)


def test_eni_river_identity_is_refused_rather_than_half_trusted():
    """MS Andorinha is ENI02338573; ENI carries no check digit."""
    with pytest.raises(RegistryError):
        normalize_vessel_imo("ENI02338573")


def test_attribution_with_an_invalid_identity_fails_construction():
    with pytest.raises(RegistryError):
        _artifact(subject_vessels=["IMO9766206"])
    with pytest.raises(RegistryError):
        # A bare string is a common mistake and would silently attribute
        # per-character if iterated.
        _artifact(subject_vessels=BELLISSIMA_IMO)


def test_a_malformed_query_answers_false_rather_than_raising(registry):
    for bad in ("IMO9766206", "MSC Bellissima", "", "ENI02338573"):
        assert registry.artifact_establishes_vessel("ART-0001", bad) is False


# -- 8. duplicates handled deterministically --------------------------------

def test_duplicate_and_unordered_attribution_normalizes_deterministically():
    a = _artifact(subject_vessels=[BELLISSIMA_IMO, BELLISSIMA_IMO, GRANDIOSA_IMO])
    b = _artifact(subject_vessels=[GRANDIOSA_IMO, BELLISSIMA_IMO])
    c = _artifact(subject_vessels=["9766205", "imo 9803613"])
    assert a.subject_vessels == b.subject_vessels == c.subject_vessels
    assert a.subject_vessels == (BELLISSIMA_IMO, GRANDIOSA_IMO)  # sorted
    assert normalize_subject_vessels(None) == ()
    assert normalize_subject_vessels([]) == ()


# -- 9. registry loading remains deterministic ------------------------------

def test_registry_loading_is_deterministic_and_round_trips(registry):
    again = ArtifactRegistry(str(ARTIFACTS_ROOT))
    for artifact in registry.list_all():
        assert again.get(artifact.artifact_id).subject_vessels == artifact.subject_vessels
        assert Artifact.from_dict(artifact.to_dict()) == artifact


def test_unattributed_records_carry_no_empty_assertion(registry):
    """UNKNOWN is the absence of a key, not an empty list in the index."""
    raw = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    for artifact_id, record in raw.items():
        if artifact_id in ATTRIBUTED:
            assert record["subject_vessels"] == [BELLISSIMA_IMO]
        else:
            assert "subject_vessels" not in record
    assert set(raw) == {f"ART-{n:04d}" for n in range(1, 8)}


def test_only_evidenced_artifacts_are_attributed(registry):
    """Every attributed artifact is held, verifiable and names its own subject."""
    for artifact_id in sorted(ATTRIBUTED):
        assert registry.resolve_path(artifact_id) is not None
        assert registry.verify(artifact_id) is True
        assert registry.vessels_established_by(artifact_id) == (BELLISSIMA_IMO,)


# -- 10. existing SHA verification behaviour unchanged ----------------------

def test_digest_verification_is_untouched_by_attribution(registry):
    from timonelo.evidence.registry import sha256_of_file

    for artifact_id in ("ART-0001", "ART-0002", "ART-0003"):
        path = registry.resolve_path(artifact_id)
        assert path is not None
        assert sha256_of_file(path) == registry.get(artifact_id).sha256
        assert registry.verify(artifact_id) is True
        assert registry.verification_status(artifact_id) == "PUBLIC_ARTIFACT_SHA_VERIFIED"

    # ART-0007 is private and its bytes are not held, so it was already the one
    # failure before attribution existed. Attribution neither adds to nor
    # removes from that set.
    assert registry.verify_all() == ["ART-0007"]
    assert registry.verify_all(include_private=False) == []


def test_attribution_does_not_substitute_for_possession():
    """An attributed artifact whose bytes are absent is still unverified.

    Attribution answers "whose ship?", never "do we hold it?". Keeping them
    separate is what stops a curated label standing in for evidence.
    """
    artifact = _artifact(subject_vessels=[BELLISSIMA_IMO], sha256="b" * 64)
    assert artifact.establishes_vessel(BELLISSIMA_IMO) is True
    assert artifact.sha256 == "b" * 64  # nothing about attribution touched it
