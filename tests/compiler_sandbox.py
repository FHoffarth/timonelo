"""A compiler root that does not write into the repository.

`KnowledgeDBCompiler.compile()` writes `cruise_intelligence_db.json` and
`cruise_knowledge_graph.json` into `<root_dir>/data` on every call, and the
compiler exposes no output-path option. Any test constructing it with the
repository root therefore rewrites two tracked files as a side effect.

That matters beyond tidiness. Those artifacts are already known to be stale on
`develop` — regeneration produces a large diff unrelated to any current change
— so a test suite that silently rewrites them destroys the evidence of that
drift and makes `git status` after a test run meaningless.

`sandbox_root()` returns a temporary directory that exposes the real corpus at
`knowledge`. The compiler reads the real data and writes its artifacts into the
sandbox. Nothing is restored afterwards, because nothing is modified: restoring
tracked files after mutating them is still mutation, and would mask exactly the
drift this helper protects.

A symlink is the cheap way to expose the corpus, but it is not portable: on
Windows `os.symlink` needs SeCreateSymbolicLinkPrivilege, which an ordinary
account without Developer Mode does not hold, and the call fails with
WinError 1314. Copying is the fallback rather than a skip, because the point of
these tests is to exercise the real corpus — skipping them on the platform this
repository is developed on would remove the coverage exactly where a regression
would land first. The corpus is ~2 MB across ~450 files, so the copy is cheap.

Either way the compiler only reads the corpus, so the repository copy is
untouched in both modes.
"""

from __future__ import annotations

import pathlib
import shutil
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def expose_knowledge(root: pathlib.Path) -> str:
    """Make the real corpus readable at ``<root>/knowledge``.

    Returns the mechanism used, ``"symlink"`` or ``"copy"``, so a caller can
    assert on it if it cares. `FileExistsError` is deliberately not caught: it
    means the caller passed a root that is already populated, which is a bug in
    the test rather than a platform limitation, and copying over it would hide
    that.
    """
    target = root / "knowledge"
    source = REPO_ROOT / "knowledge"
    try:
        target.symlink_to(source, target_is_directory=True)
        return "symlink"
    except FileExistsError:
        raise
    except (OSError, NotImplementedError):
        # No symlink privilege (or no symlink support at all). Copy instead.
        shutil.copytree(source, target)
        return "copy"


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
    expose_knowledge(root)
    if cleanup_registry is not None:
        cleanup_registry.append(handle)
    else:
        # Attach to the returned path's owner so it outlives this call.
        sandbox_root._handles.append(handle)  # type: ignore[attr-defined]
    return str(root)


sandbox_root._handles = []  # type: ignore[attr-defined]
