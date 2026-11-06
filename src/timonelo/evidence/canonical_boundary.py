"""Reader refusal while an offline multi-file apply is in progress.

This is a generation barrier, not a claim of filesystem-wide atomicity.
Retained readers must be reconstructed after either commit or rollback.
"""
from pathlib import Path


def repository_for_registry(registry):
    root = getattr(registry, 'root', None)
    if root is None:
        return None
    path = Path(root).resolve()
    return path.parent.parent if path.name == 'artifacts' and path.parent.name == 'evidence' else None


def generation(root):
    if root is None:
        return None
    path = Path(root) / '.canonical-generation'
    try:
        return path.read_bytes() if path.exists() else b''
    except OSError:
        raise ValueError('CANONICAL_GENERATION_UNAVAILABLE')


def require_available(root, expected):
    if root is not None and ((Path(root) / '.canonical-apply.lock').exists() or generation(root) != expected):
        raise ValueError('CANONICAL_APPLY_OR_STALE_READER: reload the complete workspace')


class CanonicalBoundary:
    """A reader/writer generation captured when a store is opened."""
    def __init__(self, root):
        self.root = root
        self.expected = generation(root)
        self.require()

    def require(self):
        require_available(self.root, self.expected)


def boundary_for_file(path):
    evidence = next((p for p in Path(path).resolve().parents if p.name == 'evidence'), None)
    return CanonicalBoundary(evidence.parent if evidence is not None else None)


def require_registry_available(registry):
    boundary = getattr(registry, '_writer_boundary', None)
    if boundary is not None:
        boundary.require()
    elif (root := repository_for_registry(registry)) is not None:
        # A registry without a captured generation cannot prove current state.
        raise ValueError('CANONICAL_REGISTRY_GENERATION_CONTEXT_MISSING')
