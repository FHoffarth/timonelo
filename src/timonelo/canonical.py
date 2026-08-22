"""
Canonical serialization.

Governed by ADR-0003 §5.1.

Every JSON artifact the engine writes must be byte-reproducible. Before this
module existed, sixteen write sites called json.dump() without sort_keys, and
running the test suite produced a ~16,500-line diff against committed data with
zero semantic change: 1,195 paths differed in key ORDER only.

That is not cosmetic. It means git cannot distinguish a knowledge change from
formatting noise, so no diff of the knowledge base can be meaningfully
reviewed — and ADR-0003's determinism criterion fails before any engine code
is written.

All JSON writes go through this module. Nothing else may call json.dump().
"""

from __future__ import annotations
import json
import os
from typing import Any

INDENT = 2


def canonical_dumps(data: Any) -> str:
    """Serialize to canonical JSON: sorted keys, stable separators, UTF-8 text."""
    return json.dumps(
        data,
        indent=INDENT,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ": "),
    )


def canonical_dump(data: Any, path: str) -> None:
    """Write canonical JSON to `path`, creating parent directories as needed.

    Always terminates with a newline so the file is POSIX-clean and diffs do
    not report a missing final newline.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    # newline="\n" is not cosmetic. Python's default text mode rewrites "\n" to
    # the platform separator, so identical data written on Windows and on Linux
    # produces different BYTES — which defeats the byte-reproducibility this
    # module exists to guarantee, and makes any digest taken over engine output
    # a property of the machine that produced it rather than of the data.
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(canonical_dumps(data))
        f.write("\n")


def is_canonical(path: str) -> bool:
    """True if the file on disk is already in canonical form.

    Used by the regression test that guards ADR-0003 §5.1.
    """
    with open(path, "r", encoding="utf-8") as f:
        on_disk = f.read()
    try:
        data = json.loads(on_disk)
    except json.JSONDecodeError:
        return False
    expected = canonical_dumps(data)
    return on_disk in (expected, expected + "\n")
