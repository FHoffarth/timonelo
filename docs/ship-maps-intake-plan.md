# Ship Maps integration readiness — continued existing work

Implementation base: hardening `885e8a5dcd9eef1f910c35764fd988528801762d`
(PR64, not merged). Research input: exact remote
`983d97e18210a184290b16845985f19c3a62c306`; only its 14 ship-map report
files are carried over, byte-identical. No history merge or canonical overlay.

## Contract and implementation

- Add `factory/source_revision.py`: unknown printed edition stays null;
  explicit revision schema pins the entire document digest. Retrieval dates,
  Last-Modified and PDF production dates never become printed editions.
  Dated documents keep the exact existing version check. Unknown mode is
  restricted to the existing `official_ship_map` class.
- Reuse Claude's extractor, unchanged, in a source-readable factory module.
  Add `ship_map_reading.py` for byte, owner/title, exact table/text/locator,
  independent index and normalized value checks. Keep the Bellissima plan
  column validator unchanged for its original source layout.
- Add a private preparation CLI: verify the pinned input tree and reacquired
  source hashes; register sources only on a self-created disposable copy;
  emit proposed IDs/records conditional on the canonical index hash.
  Never record human decisions or run canonical apply.
- Generate one 56-record review packet from final candidate JSON bindings,
  explicit source revision and both reading locators. Keep 16 identity-gated
  observations separate from 40 machine-validated pending-review observations.
  Preserve all 558 unselected/single/conflicting observations outside the batch.

## Tests and boundaries

Use tests first for unknown/downgraded editions, digest mutation, wrong ship,
prose/value mismatches, source table/index disagreement and duplicate/conflict
selection. Run the complete relevant factory/backend regressions, retain all
418 Bellissima-baseline records and authority outcomes, ART-0002, existing
owner decisions and source bytes. No new human decisions or admissions.

Seven newly acquired PDFs remain outside Git and all public/build paths.
The three PDFs already tracked in develop remain untouched; public Git
visibility and CITE_ONLY redistribution concerns are a separate release finding.
No merge, deployment, public snapshot, source registration or silent identity
correction. Human source admission and claim review are the next owner gates.
