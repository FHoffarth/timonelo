from pathlib import Path

import pytest

from timonelo.factory.compiler import KnowledgeFactoryCompiler
from timonelo.factory.patch_engine import (
    HypothesisPublicationBlocked,
    ShipPatchEngine,
)
from timonelo.ontology.bellissima import create_bellissima_ontology


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sister_ship_hypothesis_cannot_write_canonical_or_frontend_assets(tmp_path):
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
            hypothesis,
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
