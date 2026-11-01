from types import SimpleNamespace as N
import subprocess
import sys
from pathlib import Path
from timonelo.evidence.fleet_projection import project_fleet


CATALOG = [{"slug": "msc-bellissima", "label": "MSC Bellissima", "operatorId": "msc"},
           {"slug": "msc-meraviglia", "label": "MSC Meraviglia", "operatorId": "msc"}]


def test_unpublished_and_cross_vessel_claims_are_not_exported():
    s = N(statement_id="STM-X", entity_id="venue:MSC-BELLISSIMA:x", question_id="Q-X",
          statement_type="deck.venue_present", artifact_id="", value=[6])
    ws = N(editor=N(all=lambda: [s], is_currently_authoritative=lambda _: False),
           registry=N(list_all=lambda: []))
    data = project_fleet(ws, CATALOG, "2026-11-01")
    assert data["ships"]["msc-bellissima"]["candidate_count"] == 1
    assert data["ships"]["msc-bellissima"]["facts"] == []
    assert data["ships"]["msc-meraviglia"]["candidate_count"] == 0
    assert data["ships"]["msc-meraviglia"]["level"] == 0


def test_only_current_truth_engine_selection_with_reverifiable_nonprivate_provenance_is_exported():
    s = N(statement_id="STM-X", entity_id="venue:MSC-BELLISSIMA:x", question_id="Q-X",
          statement_type="deck.venue_present", artifact_id="ART-X", value=[6], page=4, locator="row X",
          evidence_event_ids=["EVT-X"], publish_status=N(value="PUBLISH_ALLOWED"))
    a = N(artifact_id="ART-X", sha256="a" * 64, filename="map.pdf", private_source=False)
    ws = N(editor=N(all=lambda: [s], is_currently_authoritative=lambda _: True),
           registry=N(list_all=lambda: [a], get=lambda _: a, verify=lambda _: True),
           events=N(all=lambda: [N(event_id="EVT-X", artifact_sha256="a" * 64)]),
           engine=N(answer=lambda *args, **kwargs: N(known=True, provenance=N(statement_id="STM-X"))))
    data = project_fleet(ws, CATALOG, "2026-11-01")
    assert len(data["ships"]["msc-bellissima"]["facts"]) == 1
    assert data["ships"]["msc-meraviglia"]["facts"] == []
    # Deck facts alone cannot manufacture a fully admitted identity or level 1.
    assert data["ships"]["msc-bellissima"]["level"] == 0
    a.private_source = True
    assert project_fleet(ws, CATALOG, "2026-11-01")["ships"]["msc-bellissima"]["facts"] == []
    a.private_source = False
    a.sha256 = "b" * 64
    assert project_fleet(ws, CATALOG, "2026-11-01")["ships"]["msc-bellissima"]["facts"] == []


def test_missing_store_removes_previous_snapshot_and_blocks_generation(tmp_path):
    output = tmp_path / "snapshot.json"
    output.write_text('{"old": true}', encoding="utf8")
    script = Path(__file__).resolve().parents[1] / "scripts/export_passenger_fleet.py"
    result = subprocess.run([sys.executable, "-B", str(script), "--evidence-root", str(tmp_path / "missing"),
                             "--output", str(output)], capture_output=True, text=True)
    assert result.returncode != 0
    assert not output.exists()
    assert "Evidence store unavailable" in result.stderr
