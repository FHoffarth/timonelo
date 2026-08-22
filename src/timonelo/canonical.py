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


def deterministic_dumps(data: Any, *, sort_keys: bool = True) -> str:
    """Serialize deterministically. `sort_keys=False` keeps the mapping's own order.

    Order-preserving output is still deterministic: Python dicts preserve
    insertion order, so the same builder run twice produces the same string.
    What it is NOT is *canonical* — two builders that construct equal data in
    different orders would disagree. Prefer `canonical_dumps`.
    """
    return json.dumps(
        data,
        indent=INDENT,
        sort_keys=sort_keys,
        ensure_ascii=False,
        separators=(",", ": "),
    )


def deterministic_dump(
    data: Any,
    path: str,
    *,
    sort_keys: bool = True,
    trailing_newline: bool = True,
) -> None:
    """Write JSON to `path` with platform-independent bytes.

    The single write implementation for this module. `canonical_dump` is this
    function with the canonical defaults; the keyword arguments exist only for
    artifacts committed before the canonical form was settled, whose bytes are
    asserted by digest and therefore may not be silently reordered or given a
    trailing newline. See `scripts/extract_spatial_geometry.py`.

    newline="\\n" is not cosmetic. Python's default text mode rewrites "\\n" to
    the platform separator, so identical data written on Windows and on Linux
    produces different BYTES — which defeats the byte-reproducibility this
    module exists to guarantee, and makes any digest taken over engine output a
    property of the machine that produced it rather than of the data.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(deterministic_dumps(data, sort_keys=sort_keys))
        if trailing_newline:
            f.write("\n")


def canonical_dump(data: Any, path: str) -> None:
    """Write canonical JSON to `path`, creating parent directories as needed.

    Always terminates with a newline so the file is POSIX-clean and diffs do
    not report a missing final newline.
    """
    deterministic_dump(data, path, sort_keys=True, trailing_newline=True)


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
