from pathlib import Path

import pytest

from timonelo.factory.compiler import KnowledgeFactoryCompiler
from timonelo.factory.patch_engine import (
    HypothesisPublicationBlocked,
    ShipPatchEngine,
)
from timonelo.ontology.bellissima import create_bellissima_ontology


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("unwrap", [False, True], ids=["wrapper", "inner-ontology"])
def test_sister_ship_hypothesis_cannot_write_canonical_or_frontend_assets(
    tmp_path, unwrap
):
    hypothesis = ShipPatchEngine.apply_patch(
        create_bellissima_ontology(),
        {
            "target_imo": "IMO9647710",
            "target_name": "MSC Meraviglia",
            "operations": [],
        },
    )

    with pytest.raises(HypothesisPublicationBlocked):
        KnowledgeFactoryCompiler.compile_vessel(
            hypothesis.ontology if unwrap else hypothesis,
            output_data_dir=tmp_path,
            output_frontend_dir=tmp_path / "frontend",
        )

    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "frontend").exists()


def test_fleet_compiler_has_no_sister_ship_publication_path():
    compiler = (REPO_ROOT / "src/timonelo/factory/compiler.py").read_text(encoding="utf-8")
    assert "ShipPatchEngine.apply_patch" not in compiler
    assert "deltas.json" not in compiler


def test_legacy_meraviglia_runtime_asset_is_not_public():
    public_asset = REPO_ROOT / "frontend/public/data/msc-meraviglia.json"
    quarantine_asset = REPO_ROOT / "data/hypotheses/legacy-runtime/msc-meraviglia.json"
    assert not public_asset.exists()
    assert quarantine_asset.exists()


def test_sister_ship_derivatives_are_outside_canonical_namespace():
    canonical_root = REPO_ROOT / "data/ships"
    canonical_paths = {
        path.relative_to(canonical_root).as_posix()
        for path in canonical_root.rglob("*")
        if path.is_file()
    }
    assert not any(path.startswith("msc-meraviglia/") for path in canonical_paths)

    quarantine_root = (
        REPO_ROOT / "data/hypotheses/legacy-derivatives/msc-meraviglia"
    )
    assert {
        path.name for path in quarantine_root.iterdir() if path.is_file()
    } == {"deltas.json", "knowledge-pack.json", "manifest.json"}


def test_grandiosa_legacy_derivative_is_not_public():
    public_asset = REPO_ROOT / "frontend/public/data/msc-grandiosa.json"
    quarantine_asset = (
        REPO_ROOT / "data/hypotheses/legacy-runtime/msc-grandiosa.json"
    )
    retained_hypothesis = (
        REPO_ROOT / "data/ships/msc-grandiosa/knowledge-pack.json"
    )
    assert not public_asset.exists()
    assert quarantine_asset.exists()
    assert quarantine_asset.read_bytes() == retained_hypothesis.read_bytes()


def test_legacy_publisher_is_not_reachable_from_production_navigation():
    app = (REPO_ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
    navigation = (REPO_ROOT / "frontend/src/components/ui/MainNavbar.tsx").read_text(
        encoding="utf-8"
    )
    publisher = (
        REPO_ROOT / "frontend/src/knowledge/pipeline/KnowledgePublisher.ts"
    ).read_text(encoding="utf-8")

    assert "KnowledgeDashboardPage" not in app
    assert "knowledge-factory" not in app
    assert "knowledge-factory" not in navigation
    assert "passed: true" not in publisher
    assert "LegacyPublisherQuarantinedError" in publisher
