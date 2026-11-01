"""Generate the static passenger snapshot; no source bytes or private records exported."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from timonelo.evidence.workspace import Workspace
from timonelo.evidence.fleet_projection import project_fleet
from timonelo.evidence.publication_snapshot import make_snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, default=ROOT / 'evidence')
    parser.add_argument('--output', type=Path, default=ROOT / 'frontend/public/data/fleet.publication.json')
    parser.add_argument('--block', action='store_true', help='Write an explicit empty revocation snapshot; no evidence store needed')
    args = parser.parse_args()
    # Remove any prior snapshot before evaluating: errors must not preserve old output.
    args.output.unlink(missing_ok=True)
    if not args.block and not (args.evidence_root / 'statements/statements.json').is_file():
        raise ValueError('Evidence store unavailable; refusing to build a publication snapshot')
    catalog = json.loads((ROOT / 'frontend/src/passenger/fleetCatalog.json').read_text(encoding='utf8'))
    as_of = datetime.now(timezone.utc).date().isoformat()
    if args.block:
        data = {'schema': 'timonelo.fleet.v1', 'as_of': as_of, 'ships': {
            ship['slug']: {'candidate_count': 0, 'level': 0, 'facts': [], 'sources': []} for ship in catalog}}
    else:
        data = project_fleet(Workspace(str(args.evidence_root)), catalog, as_of)
    snapshot = make_snapshot(data, blocked=args.block)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + '.tmp')
    try:
        temporary.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding='utf8')
        os.replace(temporary, args.output)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Snapshot {snapshot['revision']} blocked={snapshot['blocked']} expires={snapshot['expires_at']}")
    for slug, profile in data['ships'].items():
        print(f"{slug}: {len(profile['facts'])} exported / {profile['candidate_count']} candidates; level {profile['level']}")


if __name__ == '__main__':
    main()
