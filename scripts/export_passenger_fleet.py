"""Generate the static passenger snapshot; no source bytes or private records exported."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from timonelo.evidence.workspace import Workspace
from timonelo.evidence.fleet_projection import project_fleet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, default=ROOT / 'evidence')
    parser.add_argument('--output', type=Path, default=ROOT / 'frontend/public/data/fleet.publication.json')
    args = parser.parse_args()
    # Remove any prior snapshot before evaluating: errors must not preserve old output.
    args.output.unlink(missing_ok=True)
    if not (args.evidence_root / 'statements/statements.json').is_file():
        raise ValueError('Evidence store unavailable; refusing to build a publication snapshot')
    catalog = json.loads((ROOT / 'frontend/src/passenger/fleetCatalog.json').read_text(encoding='utf8'))
    data = project_fleet(Workspace(str(args.evidence_root)), catalog,
                         datetime.now(timezone.utc).date().isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf8')
    for slug, profile in data['ships'].items():
        print(f"{slug}: {len(profile['facts'])} exported / {profile['candidate_count']} candidates; level {profile['level']}")


if __name__ == '__main__':
    main()
