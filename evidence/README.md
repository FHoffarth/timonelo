# Evidence store

Governed by ADR-0002 and ADR-0003.

This tree holds Timonelo's ground truth. All claims are anchored to cryptographically verified primary source artifacts. Nothing here may be populated with example, placeholder or illustrative data — that is the defect the whole redesign exists to remove.

```
evidence/
  raw/sha256/<prefix>/  content-addressed primary source vault (filename = sha256.pdf)
  artifacts/index.json  canonical artifact registry (ART-XXXX -> SHA-256 & metadata)
  documents/            working copies staged for import (not content-addressed)
  statements/           canonical authored statements (statements.json)
  reviews/              review log (log.json) and conflict store (conflicts.json)
  registry/             document classes and question registries (questions.json)
```

## Rules

- Primary source artifacts are stored in `evidence/raw/sha256/<prefix>/<sha256>.pdf` addressed by their exact SHA-256 byte digest.
- `evidence/artifacts/index.json` assigns immutable artifact identifiers (e.g. `ART-0001`, `ART-0002`) bound to specific SHA-256 digests.
- `documents/` is a staging area. Files there are not evidence until registered.
- Nothing bypasses `Artifact -> Event -> Statement -> Review -> Published`.
- Statements and knowledge fields must cite verified artifact records with valid locators.
- Fail-closed: missing evidence or unresolved conflicts block publication.
