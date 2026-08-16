# Knowledge Validation

The knowledge validator checks repository records without modifying them.

## Run

From the repository root:

```bash
python tools/knowledge_validator.py
```

Validate another knowledge directory with `--knowledge-dir PATH`.

## Checks

The command detects duplicate record and source IDs, incomplete metadata, invalid filenames, invalid folder placement, missing mandatory headings, and malformed Markdown structure. Templates, directory READMEs, and repository guidance are checked for Markdown structure but are not treated as knowledge records.

## Result

Successful validation prints `Knowledge validation: PASS` and exits with code `0`. Failed validation prints `Knowledge validation: FAIL`, a detailed finding for every detected issue, and exits with code `1`.
