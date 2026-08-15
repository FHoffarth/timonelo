"""Command-line interface for validating and importing cruise knowledge packs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .codec import KnowledgePackFormatError, load_pack
from .persistence import KnowledgePackRepository, PersistenceConflictError
from .validation import PackValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a canonical pack without persistence")
    validate_parser.add_argument("pack", type=Path)

    import_parser = subparsers.add_parser("import", help="validate and transactionally project a pack into SQLite")
    import_parser.add_argument("pack", type=Path)
    import_parser.add_argument("--database", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            pack = load_pack(args.pack)
            print(json.dumps({
                "status": "valid",
                "pack_id": pack.pack_id,
                "version": pack.version,
                "ship": pack.ship.name,
                "entities": len(pack.entities()),
            }, indent=2))
            return 0

        repository = KnowledgePackRepository(args.database)
        result = repository.import_path(args.pack)
        print(json.dumps({
            "status": "imported" if result.inserted else "unchanged",
            "pack_id": result.pack_id,
            "version": result.version,
            "pack_version_id": result.pack_version_id,
            "content_sha256": result.content_sha256,
        }, indent=2))
        return 0
    except (KnowledgePackFormatError, PackValidationError, PersistenceConflictError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
