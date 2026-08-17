# Evidence store

Governed by ADR-0002 and ADR-0003.

This tree holds Timonelo's ground truth. It is **empty by design** until a real
source document is acquired. Nothing here may be populated with example,
placeholder or illustrative data — that is the defect the whole redesign exists
to remove.

```
evidence/
  artifacts/blobs/   content-addressed source documents (filename = sha256)
  artifacts/index.json  artifact registry
  documents/         working copies staged for import (not content-addressed)
  statements/        manually authored statements
  reviews/           review and publication history
  registry/          question registry
```

## Rules

- A file enters `artifacts/blobs/` only via the importer, which computes the
  digest from the bytes on disk. Digests are never typed by hand.
- `documents/` is a staging area. Files there are not evidence until imported.
- Nothing bypasses `Artifact -> Event -> Statement -> Review -> Published`.
- An empty store is a correct state. Coverage of zero is an honest measurement.
