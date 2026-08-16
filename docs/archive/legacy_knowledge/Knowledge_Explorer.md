# Knowledge Explorer

The Knowledge Explorer is internal developer tooling that discovers and validates Markdown records under `knowledge/`. It does not participate in the Timonelo product runtime.

## Architecture

`tools/knowledge_explorer.py` reads each record's `## Metadata`, `## Relationships`, and `## Sources` sections. It builds one in-memory record collection, validates its references, and deterministically generates `knowledge/INDEX.md` and `knowledge/GRAPH.md`. The existing index-generator command remains available as a compatibility entrypoint.

## Usage

Generate both artifacts from the repository root:

```bash
python tools/knowledge_explorer.py
```

Run `python tools/knowledge_explorer.py --check` to detect stale generated files without rewriting them. A successful run exits `0`; validation findings or stale output exit `1` with details.

## Maintenance

Do not edit `INDEX.md` or `GRAPH.md` manually. Add relationships and source IDs as Markdown list entries in their named record sections, then rerun the explorer. Record IDs are matched case-insensitively; related IDs must resolve to any discovered record, while source IDs must resolve specifically to a Source record. Non-source records with no incoming or outgoing relationship are reported as orphans.
