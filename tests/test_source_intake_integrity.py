"""Source attribution comes from held document pages, never request labels."""
from pathlib import Path

import fitz
import pytest

from timonelo.evidence.importer import import_pdf
from timonelo.evidence.registry import ArtifactRegistry, RegistryError

BELLISSIMA = "IMO9760524"
GRANDIOSA = "IMO9803613"


def pdf(tmp_path, text, name="source.pdf"):
    path = tmp_path / name
    with fitz.open() as doc:
        doc.new_page().insert_text((40, 40), text)
        doc.save(path)
    return str(path)


def register(registry, path, **kwargs):
    return registry.register(path, "cruise_line_deck_plan", "2026-08-30", "test fixture", **kwargs)


def intake(registry, path, **kwargs):
    return import_pdf(registry, path, "cruise_line_deck_plan", "2026-08-30", "test fixture", **kwargs)


def test_register_duplicate_refuses_changed_or_removed_attribution(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "MSC Bellissima")
    original = register(registry, path, subject_vessels=[BELLISSIMA])
    before = Path(registry.index_path).read_bytes()
    for subjects in ([GRANDIOSA], [], [BELLISSIMA, GRANDIOSA]):
        with pytest.raises(RegistryError, match="attribution"):
            register(registry, path, subject_vessels=subjects)
    assert Path(registry.index_path).read_bytes() == before
    assert register(registry, path, subject_vessels=[BELLISSIMA]) == original
    assert register(registry, path) == original


def test_registration_stores_one_verified_sha_vault_copy(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "source")
    art = register(registry, path)
    expected = tmp_path / "raw" / "sha256" / art.sha256[:2] / f"{art.sha256}.pdf"
    assert Path(registry.resolve_path(art.artifact_id)) == expected
    assert expected.read_bytes() == Path(path).read_bytes()
    assert not Path(registry.blob_path(art.artifact_id)).exists()


def test_import_preserves_verified_document_subject(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    art = intake(registry, pdf(tmp_path, "MSC Bellissima"), subject_vessels=[BELLISSIMA], source_identity_pages={BELLISSIMA: 1})
    assert art.subject_vessels == (BELLISSIMA,)
    assert ArtifactRegistry(registry.root).get(art.artifact_id).subject_vessels == (BELLISSIMA,)
    assert registry.verify(art.artifact_id)


@pytest.mark.parametrize("text,subjects,pages", [
    ("MSC Grandiosa", [BELLISSIMA], {BELLISSIMA: 1}),
    ("MSC Bellissima", [BELLISSIMA], None),
    ("MSC Bellissima", [BELLISSIMA], {BELLISSIMA: 2}),
    ("MSC Bellissima", [BELLISSIMA], {GRANDIOSA: 1}),
    ("MSC Bellissima and MSC Grandiosa", [BELLISSIMA, GRANDIOSA], {BELLISSIMA: 1, GRANDIOSA: 1}),
])
def test_intake_rejects_unproven_or_ungoverned_subject_before_registration(tmp_path, text, subjects, pages):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    with pytest.raises(RegistryError):
        intake(registry, pdf(tmp_path, text, "MSC-Bellissima.pdf"), subject_vessels=subjects, source_identity_pages=pages)
    assert len(registry) == 0
    assert not list((tmp_path / "raw").rglob("*"))


def test_bad_attribution_does_not_relabel_existing_digest(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "MSC Bellissima")
    first = intake(registry, path)
    with pytest.raises(RegistryError, match="attribution"):
        intake(registry, path, subject_vessels=[BELLISSIMA], source_identity_pages={BELLISSIMA: 1})
    assert registry.get(first.artifact_id).subject_vessels == ()

def test_existing_corrupt_vault_copy_is_refused_without_overwrite(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "source")
    art = register(registry, path)
    held = Path(registry.resolve_path(art.artifact_id))
    held.write_bytes(b"corrupt")
    before = Path(registry.index_path).read_bytes()
    with pytest.raises(RegistryError, match="corrupt"):
        register(registry, path)
    assert held.read_bytes() == b"corrupt"
    assert Path(registry.index_path).read_bytes() == before


def test_import_identity_and_retained_bytes_share_one_snapshot(tmp_path, monkeypatch):
    import timonelo.evidence.importer as importer
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "MSC Bellissima")
    original = Path(path).read_bytes()
    original_check = importer._verify_source_identity

    def verify_then_replace(snapshot, subjects, pages):
        original_check(snapshot, subjects, pages)
        Path(path).write_bytes(b"%PDF- wrong vessel replacement")

    monkeypatch.setattr(importer, "_verify_source_identity", verify_then_replace)
    artifact = intake(registry, path, subject_vessels=[BELLISSIMA], source_identity_pages={BELLISSIMA: 1})
    assert Path(registry.resolve_path(artifact.artifact_id)).read_bytes() == original


@pytest.mark.parametrize("slug,name,subject", [
    ("msc-meraviglia", "MSC Meraviglia", "IMO9660463"),
    ("msc-seascape", "MSC Seascape", "IMO9805348"),
    ("msc-seashore", "MSC Seashore", "IMO9805336"),
])
def test_quarantined_identity_allows_documentary_preparation_without_authority(tmp_path, slug, name, subject):
    from timonelo.evidence.vessel_ownership import canonical_vessel, validate_ownership
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    with pytest.raises(ValueError, match="QUARANTINED"):
        canonical_vessel(slug)
    artifact = intake(registry, pdf(tmp_path, name), subject_vessels=[subject], source_identity_pages={subject: 1})
    assert artifact.subject_vessels == (subject,)
    assert registry.verify(artifact.artifact_id)
    # Source collection alone is not canonical ownership or identity approval.
    with pytest.raises(ValueError, match="QUARANTINED"):
        validate_ownership("ship:" + slug, artifact)
    with pytest.raises(ValueError, match="QUARANTINED"):
        canonical_vessel(slug)


def test_quarantined_conflicting_document_identity_can_only_be_held_unattributed(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "MSC Meraviglia IMO 9760512")
    with pytest.raises(RegistryError, match="conflicting"):
        intake(registry, path, subject_vessels=["IMO9660463"], source_identity_pages={"IMO9660463": 1})
    assert len(registry) == 0
    # Candidate IMO is not an independently approved canonical identity either.
    with pytest.raises(RegistryError, match="canonical identity catalog"):
        intake(registry, path, subject_vessels=["IMO9760512"], source_identity_pages={"IMO9760512": 1})
    assert len(registry) == 0
    artifact = intake(registry, path)
    assert artifact.subject_vessels == ()
    assert registry.verify(artifact.artifact_id)

def test_duplicate_private_artifact_does_not_publish_bytes_to_public_vault(tmp_path):
    import hashlib
    import json
    root = tmp_path / "artifacts"
    root.mkdir()
    path = pdf(tmp_path, "private source")
    content = Path(path).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    record = {
        "artifact_id": "ART-0001", "sha256": digest, "filename": "private.pdf",
        "document_class": "cruise_line_deck_plan", "acquired_on": "2026-08-30",
        "acquisition_method": "test fixture", "private_source": True,
        "byte_size": len(content),
    }
    (root / "index.json").write_text(json.dumps({"ART-0001": record}), encoding="utf-8")
    registry = ArtifactRegistry(str(root))
    assert register(registry, path).private_source
    assert not (tmp_path / "raw").exists()

def test_source_identity_page_with_conflicting_printed_imo_is_refused(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path = pdf(tmp_path, "MSC Bellissima IMO 9803613")
    with pytest.raises(RegistryError, match="conflicting"):
        intake(registry, path, subject_vessels=[BELLISSIMA], source_identity_pages={BELLISSIMA: 1})
    assert len(registry) == 0


def shared_fixture(tmp_path):
    """Fictional decisions used only inside an isolated temporary registry."""
    import hashlib
    import json
    path = tmp_path / "shared.pdf"
    with fitz.open() as doc:
        doc.new_page().insert_text((40, 40), "MSC Bellissima IMO 9760524")
        doc.new_page().insert_text((40, 40), "MSC Grandiosa IMO 9803613")
        doc.save(path)
    pages = {BELLISSIMA: 1, GRANDIOSA: 2}
    record = {
        "schema": "timonelo.shared-document-intake.v1", "decision": "APPROVE",
        "actor": "fixture reviewer", "occurred_on": "2026-08-30", "note": "Fixture only; no production authority.",
        "artifact_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "subject_vessels": [BELLISSIMA, GRANDIOSA], "source_identity_pages": pages,
    }
    decision = tmp_path / "fixture-decision.json"
    decision.write_text(json.dumps(record), encoding="utf8")
    kwargs = dict(subject_vessels=[BELLISSIMA, GRANDIOSA], source_identity_pages=pages,
                  shared_document_decision_path=str(decision),
                  shared_document_decision_sha256=hashlib.sha256(decision.read_bytes()).hexdigest())
    return str(path), decision, record, kwargs


def test_governed_shared_intake_retains_both_subjects_and_pinned_decision(tmp_path):
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path, _, _, kwargs = shared_fixture(tmp_path)
    artifact = intake(registry, path, **kwargs)
    assert artifact.subject_vessels == (BELLISSIMA, GRANDIOSA)
    assert kwargs["shared_document_decision_sha256"] in artifact.notes
    assert ArtifactRegistry(registry.root).get(artifact.artifact_id) == artifact
    assert registry.verify(artifact.artifact_id)


@pytest.mark.parametrize("change", ["pin", "record", "digest", "vessels", "pages", "decision", "actor", "occurred_on", "note", "schema"])
def test_shared_intake_refuses_unbound_or_incomplete_decision(tmp_path, change):
    import hashlib
    import json
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path, decision, record, kwargs = shared_fixture(tmp_path)
    if change == "pin":
        kwargs["shared_document_decision_sha256"] = None
    elif change == "record":
        decision.write_text("{}", encoding="utf8")  # retained bytes changed after review
    else:
        key = {"digest": "artifact_sha256", "vessels": "subject_vessels", "pages": "source_identity_pages"}.get(change, change)
        record[key] = {"digest": "0" * 64, "vessels": [BELLISSIMA], "pages": {BELLISSIMA: 2, GRANDIOSA: 1}}.get(change, "")
        decision.write_text(json.dumps(record), encoding="utf8")
        kwargs["shared_document_decision_sha256"] = hashlib.sha256(decision.read_bytes()).hexdigest()
    with pytest.raises(RegistryError):
        intake(registry, path, **kwargs)
    assert len(registry) == 0
    assert not (tmp_path / "raw").exists()


def test_shared_decision_never_overrides_actual_source_page_identity(tmp_path):
    import hashlib
    import json
    registry = ArtifactRegistry(str(tmp_path / "artifacts"))
    path, decision, record, kwargs = shared_fixture(tmp_path)
    # Even a pinned record cannot turn Bellissima's page into Grandiosa's.
    record["source_identity_pages"] = kwargs["source_identity_pages"] = {BELLISSIMA: 1, GRANDIOSA: 1}
    decision.write_text(json.dumps(record), encoding="utf8")
    kwargs["shared_document_decision_sha256"] = hashlib.sha256(decision.read_bytes()).hexdigest()
    with pytest.raises(RegistryError, match="does not establish"):
        intake(registry, path, **kwargs)
    assert len(registry) == 0
