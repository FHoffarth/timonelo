# MSC Bellissima Knowledge Pack

This directory contains the canonical, immutable MSC Bellissima reference pack. Version `2022.10.0` represents the configuration snapshot documented in the official MSC technical sheet marked October 2022.

The inventory is intentionally evidence-bounded. It proves the complete model and import path with a small set of individually verifiable cabins and public areas; it does not claim to enumerate every cabin. Unknown category assignments remain explicit.

Validate the pack:

```console
timonelo-knowledge-pack validate data/ships/msc-bellissima/knowledge-pack.json
```

Create a reproducible SQLite projection:

```console
timonelo-knowledge-pack import data/ships/msc-bellissima/knowledge-pack.json --database data/processed/msc-bellissima.sqlite
```

Generated databases belong in `data/processed/` and are not canonical source artifacts.
