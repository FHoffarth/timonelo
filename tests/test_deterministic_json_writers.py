"""
Byte-determinism guards for the hardened JSON writers (Phase 1-3).

The failure these prevent is subtle: identical data written on Windows and on
Linux produced different BYTES, because Python's default text mode rewrites
"\n" to the platform separator. Any digest taken over such a file then measures
the machine that produced it rather than the data — which is exactly how
`develop` came to hold fifteen geometry hashes that could only pass on a CRLF
checkout.

These tests pin two separate things:

  1. the writers emit LF and are deterministic, on any platform;
  2. the hardened writers still reproduce the COMMITTED bytes exactly, so the
     existing SHA-256 expectations remain valid and no artifact is silently
     reordered or given a trailing newline it did not have.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from timonelo.canonical import (
    canonical_dump,
    canonical_dumps,
    deterministic_dump,
    deterministic_dumps,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Artifacts committed before the canonical form was settled. They are stored
#: in insertion-key order with no trailing newline, and their bytes are asserted
#: by digest elsewhere, so their writers must not reorder or append.
LEGACY_BYTE_CONTRACT_FILES = sorted(
    [p for p in (REPO_ROOT / "geometry").glob("deck*.geometry.json")]
    + [
        REPO_ROOT / "knowledge" / "ships" / "msc-meraviglia" / name
        for name in (
            "bars.json", "cabins.json", "decks.json", "entertainment.json",
            "extraction_manifest.json", "lounges.json", "pools.json",
            "public_areas.json", "restaurants.json", "spa.json", "sports.json",
            "technical.json",
        )
    ]
)


def _ids(paths):
    return [p.relative_to(REPO_ROOT).as_posix() for p in paths]


# --- writer primitives ----------------------------------------------------


def test_deterministic_dump_writes_lf_on_every_platform(tmp_path):
    target = tmp_path / "out.json"
    deterministic_dump({"b": 1, "a": ["x", "y"]}, str(target))
    raw = target.read_bytes()

    assert b"\r\n" not in raw, "platform newline leaked into the output"
    assert raw.count(b"\n") > 1, "expected a multi-line indented document"
    assert raw.endswith(b"\n")


def test_canonical_dump_is_deterministic_dump_with_canonical_defaults(tmp_path):
    data = {"z": 1, "a": {"n": [1, 2, 3]}}
    a, b = tmp_path / "a.json", tmp_path / "b.json"

    canonical_dump(data, str(a))
    deterministic_dump(data, str(b), sort_keys=True, trailing_newline=True)

    assert a.read_bytes() == b.read_bytes()
    assert a.read_bytes() == canonical_dumps(data).encode("utf-8") + b"\n"


def test_sort_keys_flag_controls_ordering_and_nothing_else():
    data = {"z": 1, "a": 2, "m": 3}

    ordered = deterministic_dumps(data, sort_keys=False)
    sorted_ = deterministic_dumps(data, sort_keys=True)

    assert list(json.loads(ordered)) == ["z", "a", "m"]
    assert list(json.loads(sorted_)) == ["a", "m", "z"]
    # Same data either way: ordering is presentation, not content.
    assert json.loads(ordered) == json.loads(sorted_)


def test_trailing_newline_flag_is_the_only_difference_it_makes(tmp_path):
    data = {"a": 1}
    with_nl, without = tmp_path / "w.json", tmp_path / "n.json"

    deterministic_dump(data, str(with_nl), trailing_newline=True)
    deterministic_dump(data, str(without), trailing_newline=False)

    assert with_nl.read_bytes() == without.read_bytes() + b"\n"


def test_writes_are_reproducible(tmp_path):
    data = {"b": [3, 2, 1], "a": {"nested": "válue"}}
    first, second = tmp_path / "1.json", tmp_path / "2.json"

    deterministic_dump(data, str(first))
    deterministic_dump(data, str(second))

    assert first.read_bytes() == second.read_bytes()
    # Non-ASCII survives verbatim rather than being escaped.
    assert "válue" in first.read_text(encoding="utf-8")


# --- committed artifacts keep their exact bytes ---------------------------


@pytest.mark.parametrize(
    "path", LEGACY_BYTE_CONTRACT_FILES, ids=_ids(LEGACY_BYTE_CONTRACT_FILES)
)
def test_legacy_artifact_round_trips_byte_for_byte(path):
    """The hardened writer reproduces each committed file exactly.

    This is what keeps `EXPECTED_SYNTHETIC_HASHES` valid: re-running the
    geometry or Meraviglia writers cannot change a single byte.
    """
    raw = path.read_bytes()
    data = json.loads(raw)

    rewritten = deterministic_dumps(data, sort_keys=False).encode("utf-8")

    assert rewritten == raw, f"{path.name} would be rewritten by its own writer"
    assert not raw.endswith(b"\n"), "this artifact's contract has no final newline"
    assert b"\r\n" not in raw


@pytest.mark.parametrize(
    "path", LEGACY_BYTE_CONTRACT_FILES, ids=_ids(LEGACY_BYTE_CONTRACT_FILES)
)
def test_legacy_artifact_worktree_matches_committed_blob(path):
    """Worktree bytes equal the blob, so digests are a property of the commit."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    blob = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        capture_output=True,
        cwd=REPO_ROOT,
        check=True,
    ).stdout
    assert path.read_bytes() == blob


def test_canonical_dump_would_change_these_files_which_is_why_it_is_not_used():
    """Documents the reason the legacy flags exist, so nobody 'tidies' them.

    If this ever stops holding, the artifacts have been regenerated in
    canonical form and the legacy flags can be dropped.
    """
    sample = REPO_ROOT / "geometry" / "deck14.geometry.json"
    raw = sample.read_bytes()
    data = json.loads(raw)

    canonical = canonical_dumps(data).encode("utf-8") + b"\n"

    assert canonical != raw
    assert json.loads(canonical) == json.loads(raw), "content must be identical"


# --- compiler writer swap is byte-equivalent apart from the newline -------


def test_compiler_writer_swap_preserves_bytes_apart_from_trailing_newline(tmp_path):
    """`json.dump(..., indent=2, sort_keys=True, ensure_ascii=False)` -> canonical_dump.

    The compiler already sorted keys, so the swap changes exactly one byte at
    the end of the file and nothing else.
    """
    data = {
        "version": "2.0.0",
        "statistics": {"total_ships": 2, "total_ports": 3},
        "ships": {"b-ship": {"slug": "b-ship"}, "a-ship": {"slug": "a-ship"}},
    }

    legacy = tmp_path / "legacy.json"
    with open(legacy, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True, ensure_ascii=False)

    modern = tmp_path / "modern.json"
    canonical_dump(data, str(modern))

    assert modern.read_bytes() == legacy.read_bytes() + b"\n"
    assert json.loads(modern.read_text(encoding="utf-8")) == json.loads(
        legacy.read_text(encoding="utf-8")
    )
