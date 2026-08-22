"""Behavioral coverage for ArtifactRegistry SHA-vault compatibility."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from timonelo.evidence.editor import EditorError
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import EvidenceCondition


BELLISSIMA_SHA = (
    "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"
)
MERAVIGLIA_SHA = (
    "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"
)
REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_registry(root: Path, content: bytes, *, byte_size: int | None = None):
    digest = hashlib.sha256(content).hexdigest()
    return _write_registry_record(
        root,
        digest,
        len(content) if byte_size is None else byte_size,
    ), digest


def _write_registry_record(root: Path, digest: str, byte_size: int):
    artifact_root = root / "artifacts"
    artifact_root.mkdir(parents=True)
    (artifact_root / "index.json").write_text(
        json.dumps(
            {
                "ART-0001": {
                    "artifact_id": "ART-0001",
                    "sha256": digest,
                    "filename": "source.bin",
                    "document_class": "cruise_line_deck_plan",
                    "acquired_on": "2026-08-20",
                    "acquisition_method": "test fixture",
                    "byte_size": byte_size,
                }
            }
        ),
        encoding="utf-8",
    )
    return ArtifactRegistry(str(artifact_root))


def _vault_path(root: Path, digest: str, extension: str = ".bin") -> Path:
    path = root / "raw" / "sha256" / digest[:2] / f"{digest}{extension}"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


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


def test_canonical_sha_vault_resolves_and_verifies_without_copy(tmp_path):
    content = b"canonical source bytes"
    registry, digest = _write_registry(tmp_path, content)
    canonical = _vault_path(tmp_path, digest, ".source")
    canonical.write_bytes(content)

    assert Path(registry.resolve_path("ART-0001")) == canonical
    assert registry.verify("ART-0001") is True
    assert not Path(registry.blob_path("ART-0001")).exists()


def test_missing_canonical_and_legacy_content_fails_closed(tmp_path):
    registry, _ = _write_registry(tmp_path, b"missing")

    assert registry.resolve_path("ART-0001") is None
    assert registry.verify("ART-0001") is False


def test_wrong_hash_canonical_content_fails_without_legacy_fallback(tmp_path):
    content = b"registered bytes"
    registry, digest = _write_registry(tmp_path, content)
    _vault_path(tmp_path, digest).write_bytes(b"corrupt bytes")
    legacy = Path(registry.blob_path("ART-0001"))
    legacy.write_bytes(content)

    assert registry.resolve_path("ART-0001") is None
    assert registry.verify("ART-0001") is False


def test_wrong_authoritative_size_fails_closed(tmp_path):
    content = b"correct digest but registry size is wrong"
    registry, digest = _write_registry(tmp_path, content, byte_size=len(content) + 1)
    _vault_path(tmp_path, digest).write_bytes(content)

    assert registry.verify("ART-0001") is False


def test_valid_legacy_blob_remains_resolvable(tmp_path):
    content = b"legacy source bytes"
    registry, _ = _write_registry(tmp_path, content)
    legacy = Path(registry.blob_path("ART-0001"))
    legacy.write_bytes(content)

    assert Path(registry.resolve_path("ART-0001")) == legacy
    assert registry.verify("ART-0001") is True


def test_multiple_sha_vault_candidates_are_ambiguous_and_fail_closed(tmp_path):
    content = b"same bytes under ambiguous media extensions"
    registry, digest = _write_registry(tmp_path, content)
    _vault_path(tmp_path, digest, ".pdf").write_bytes(content)
    _vault_path(tmp_path, digest, ".bin").write_bytes(content)

    assert registry.resolve_path("ART-0001") is None
    assert registry.verify("ART-0001") is False


def test_registry_entry_with_nonexistent_sha_fails_closed(tmp_path):
    registry, digest = _write_registry(tmp_path, b"never stored")
    assert registry.get("ART-0001").sha256 == digest

    assert registry.verify("ART-0001") is False


@pytest.mark.parametrize(
    "malformed_digest",
    [
        "../../outside",
        "../outside",
        r"..\outside",
        "/absolute/path",
        r"C:\outside",
        r"\\server\share\outside",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        f"{'a' * 63} ",
        f"{'a' * 63}g",
    ],
)
def test_malformed_digest_is_rejected_before_any_storage_path(
    tmp_path, monkeypatch, malformed_digest
):
    registry = _write_registry_record(tmp_path, malformed_digest, 8)
    sentinel = tmp_path / "outside"
    sentinel.write_bytes(b"sentinel")
    inspected_paths = []

    def unexpected_path_construction(*_args, **_kwargs):
        raise AssertionError("Malformed digest reached storage path construction")

    def record_hash(path):
        inspected_paths.append(Path(path))
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    monkeypatch.setattr(registry, "_vault_candidates", unexpected_path_construction)
    monkeypatch.setattr(registry, "blob_path", unexpected_path_construction)
    monkeypatch.setattr("timonelo.evidence.registry.sha256_of_file", record_hash)

    assert registry._valid_digest(malformed_digest) is False
    assert registry.resolve_path("ART-0001") is None
    assert registry.verify("ART-0001") is False
    assert inspected_paths == []
    assert sentinel.read_bytes() == b"sentinel"


def test_bellissima_art_0001_resolves_from_real_sha_vault():
    workspace = Workspace(str(REPO_ROOT / "evidence"))
    expected = (
        REPO_ROOT
        / "evidence"
        / "raw"
        / "sha256"
        / "08"
        / f"{BELLISSIMA_SHA}.pdf"
    )
    resolved = Path(workspace.registry.resolve_path("ART-0001"))

    assert resolved == expected
    assert resolved.stat().st_size == 1_970_414
    assert hashlib.sha256(resolved.read_bytes()).hexdigest() == BELLISSIMA_SHA
    assert workspace.registry.verify("ART-0001") is True


def test_meraviglia_sha_vault_artifact_remains_intact():
    path = (
        REPO_ROOT
        / "evidence"
        / "raw"
        / "sha256"
        / "77"
        / f"{MERAVIGLIA_SHA}.pdf"
    )

    assert path.is_file()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == MERAVIGLIA_SHA


def test_verified_artifact_does_not_bypass_bellissima_claim_quarantine():
    workspace = Workspace(str(REPO_ROOT / "evidence"))
    statements = [
        s for s in workspace.statements_for_artifact("ART-0001")
        if s.statement_type not in _FEATURE_TYPES
    ]

    assert workspace.registry.verify("ART-0001") is True
    assert len(statements) == 113
    assert all(s.condition is EvidenceCondition.UNKNOWN for s in statements)
    for statement in statements:
        assert workspace.engine.answer(statement.entity_id, statement.question_id).known is False

    try:
        workspace.publish_statement(
            "STM-0001", actor="resolver.test", occurred_on="2026-08-20"
        )
    except EditorError as exc:
        assert "Evidence condition must be SUPPORTED" in str(exc)
    else:
        raise AssertionError("Unresolved ART-0001 statement bypassed publication gate")
