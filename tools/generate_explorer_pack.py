"""
MSC Bellissima Cruise Explorer pack generator.

This tool no longer serializes governed spatial truth itself. It used to build
the canonical knowledge pack independently and write both
`data/ships/msc-bellissima/knowledge-pack.json` and
`frontend/public/data/msc-bellissima.json` directly, which meant a second
writer of canonical and public spatial output with its own idea of what was
publishable -- in practice, no idea at all. It called
`create_bellissima_ontology()` and wrote the result.

Two writers cannot share a trust boundary if only one of them consults it. So
this is now a thin entry point onto `KnowledgeFactoryCompiler`, which admits
spatial state through `timonelo.spatial.admission` before creating any
directory or writing any byte. If admission fails, nothing is written and this
tool exits non-zero.

Keeping the entry point rather than deleting it is deliberate: the command is
referenced by habit and by history, and a script that silently disappears gets
reinvented. One that refuses, and says why, does not.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from timonelo.factory.compiler import KnowledgeFactoryCompiler  # noqa: E402
from timonelo.ontology.bellissima import create_bellissima_ontology  # noqa: E402


def generate_explorer_pack(root_dir: Path = ROOT_DIR) -> bool:
    """Compile the explorer pack through the governed admission boundary.

    Returns True only if spatial canonical admission succeeded and the pack was
    written. Never writes canonical or public output on refusal.
    """
    return KnowledgeFactoryCompiler.compile_vessel(
        ontology=create_bellissima_ontology(),
        output_data_dir=root_dir,
        output_frontend_dir=root_dir / "frontend",
    )


def main() -> int:
    if generate_explorer_pack():
        return 0
    print(
        "Explorer pack NOT generated: the spatial state did not pass canonical "
        "admission. No canonical or public output was written.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
