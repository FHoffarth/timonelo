"""A compiler root that does not write into the repository.

`KnowledgeDBCompiler.compile()` writes `cruise_intelligence_db.json` and
`cruise_knowledge_graph.json` into `<root_dir>/data` on every call, and the
compiler exposes no output-path option. Any test constructing it with the
repository root therefore rewrites two tracked files as a side effect.

That matters beyond tidiness. Those artifacts are already known to be stale on
`develop` — regeneration produces a large diff unrelated to any current change
— so a test suite that silently rewrites them destroys the evidence of that
drift and makes `git status` after a test run meaningless.

`sandbox_root()` returns a temporary directory whose `knowledge` is a symlink
to the real corpus. The compiler reads the real data and writes its artifacts
into the sandbox. Nothing is restored afterwards, because nothing is modified:
restoring tracked files after mutating them is still mutation, and would mask
exactly the drift this helper protects.
"""

from __future__ import annotations

import pathlib
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def sandbox_root(cleanup_registry=None) -> str:
    """Return a compiler `root_dir` whose writes land outside the repository.

    `cleanup_registry`, if given, must have an `append` method; the
    `TemporaryDirectory` handle is appended to it so the caller can keep it
    alive for as long as the sandbox is needed. Without it the directory is
    removed when the handle is garbage collected, which for a `setUpClass`
    caller may be sooner than intended.
    """
    handle = tempfile.TemporaryDirectory(prefix="timonelo-compile-")
    root = pathlib.Path(handle.name)
    (root / "knowledge").symlink_to(REPO_ROOT / "knowledge")
    if cleanup_registry is not None:
        cleanup_registry.append(handle)
    else:
        # Attach to the returned path's owner so it outlives this call.
        sandbox_root._handles.append(handle)  # type: ignore[attr-defined]
    return str(root)


sandbox_root._handles = []  # type: ignore[attr-defined]
