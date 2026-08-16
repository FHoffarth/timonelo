# Knowledge Index

The generator builds `knowledge/INDEX.md` from repository records. The generated file must not be edited manually.

## Generator

`tools/generate_knowledge_index.py` reads record metadata and creates one deterministic row per knowledge record. Templates, guidance files, images, and the index itself are excluded.

## Usage

From the repository root:

```bash
python tools/generate_knowledge_index.py
```

Use `python tools/generate_knowledge_index.py --check` to verify that the committed index is current without rewriting it.

## Output

Each row contains Knowledge ID, title, category, status, folder, and the number of unique Markdown list entries under `## Sources`. Invalid records stop generation with a detailed error and leave the existing index unchanged.
