#!/usr/bin/env python3
"""Compatibility entrypoint for the Knowledge Explorer index generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from knowledge_explorer import discover, render_index


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-dir", type=Path, default=repository_root / "knowledge")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if the existing index is stale")
    args = parser.parse_args(argv)

    knowledge_root = args.knowledge_dir.resolve()
    output = args.output.resolve() if args.output else knowledge_root / "INDEX.md"
    if not knowledge_root.is_dir():
        print(f"Knowledge index generation: FAIL\nKnowledge directory does not exist: {knowledge_root}")
        return 1

    try:
        records, errors = discover(knowledge_root)
    except (OSError, UnicodeError) as exc:
        print(f"Knowledge index generation: FAIL\nCannot read knowledge repository: {exc}")
        return 1
    if errors:
        print("Knowledge index generation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    content = render_index(records, errors)
    if args.check:
        current = output.read_text(encoding="utf-8") if output.exists() else ""
        if current != content:
            print("Knowledge index check: FAIL\nknowledge/INDEX.md is missing or stale.")
            return 1
        print(f"Knowledge index check: PASS\nIndexed {len(records)} record(s).")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"Knowledge index generation: PASS\nIndexed {len(records)} record(s) in {output}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
