# Second Repository Consolidation Audit
**Target Repository**: `FHoffarth/timonelo-knowledge-factory`
**Inspected Path**: `C:\Users\Flo\Desktop\energyradar\timonelo-knowledge-factory`
**Date**: 2026-08-18
**Audit Purpose**: Inventory and classify all components of the secondary repository for consolidation into the canonical Timonelo monorepo.

---

## 1. Executive Summary

The `timonelo-knowledge-factory` repository was established as an experimental/companion repository focusing on pipeline connectors, coverage planning, and JSON Schema definitions for artifact candidates.

While it shares the same epistemic lineage (ADR-0001, ADR-0002), having two separate repositories creates split-brain risks regarding:
1. Authority schemas and artifact models
2. Candidate registration vs. physical byte verification
3. Epistemic governance and CI enforcement

**Canonical Recommendation**:
- **Consolidate** all valid planning schemas and deterministic coverage planning logic directly into `timonelo` (`src/timonelo/evidence/` and `src/timonelo/planning/`).
- **Eliminate** hazardous fallbacks (such as candidate JSON fingerprinting masquerading as artifact SHA-256).
- **Archive** the standalone `timonelo-knowledge-factory` repository to preserve ONE single repository of truth.

---

## 2. Component Inventory & Action Matrix

| Component Path | Description | Classification | Rationale & Action Required |
| :--- | :--- | :--- | :--- |
| `src/connectors/truth_engine_bridge.py` | Bridges external candidates to Truth Engine. | **ADAPT** | Candidate registration is clean, but lines 83–85 contain a dangerous fallback (`json.dumps(candidate) -> sha256`), masquerading a JSON dict fingerprint as an artifact SHA-256. Adapt into `timonelo.evidence.candidate_bridge` with strict separation between `candidate_fingerprint` and `artifact_sha256`. |
| `src/agents/coverage_planner.py` | Generates evidence acquisition plans from unknown register. | **ADAPT** | Deterministic planner with `authority_matrix` lookup. Highly compatible with Timonelo evidence collection. Adapt into `timonelo.planning.coverage_planner`. |
| `schemas/artifact-candidate.schema.json` | Draft 2020-12 schema for unverified candidate inputs. | **MIGRATE** | Clean schema. Move to `schemas/artifact-candidate.schema.json` in canonical repo. |
| `schemas/evidence-acquisition-plan.schema.json` | Schema for structured acquisition tasks. | **MIGRATE** | Clean schema. Move to `schemas/evidence-acquisition-plan.schema.json`. |
| `schemas/coverage-plan-request.schema.json` | Request schema for coverage planning agent. | **MIGRATE** | Clean schema. Move to `schemas/coverage-plan-request.schema.json`. |
| `schemas/artifact.schema.json` | Schema for source artifacts. | **ALREADY SUPERSEDED** | Canonical repo has richer, verified `schemas/artifact.schema.json` with physical provenance constraints. |
| `schemas/statement.schema.json` | Schema for fact statements. | **ALREADY SUPERSEDED** | Canonical repo `schemas/statement.schema.json` contains full multi-axial epistemic fields (ADR-0002). |
| `docs/adr/ADR-0001-two-tier-source-hierarchy.md` | ADR defining Tier-1 vs Tier-2 sources. | **ALREADY SUPERSEDED** | Fully integrated in `timonelo/docs/adr/ADR-0001.md`. |
| `docs/adr/ADR-0002-four-level-epistemic-status.md` | ADR defining epistemic model. | **ALREADY SUPERSEDED** | Fully integrated and expanded in `timonelo/docs/adr/ADR-0002.md`. |
| `docs/SYSTEM_SUMMARY.md` | High-level system overview. | **ARCHIVE ONLY** | Superseded by canonical `README.md` and `docs/00_READ_FIRST.md`. |
| `tests/test_truth_engine_bridge.py` | Tests for candidate registration. | **ADAPT** | Adapt to test adapted candidate bridge in `tests/test_candidate_bridge.py`. |
| `tests/test_coverage_planner.py` | Tests for coverage planner. | **ADAPT** | Adapt to test coverage planner in `tests/test_coverage_planner.py`. |

---

## 3. Specific Hazard Analysis & Quarantine Points

### Hazard: Artifact SHA vs. Candidate Fingerprint
In `timonelo-knowledge-factory/src/connectors/truth_engine_bridge.py` (lines 83–86):
```python
# HAZARDOUS CODE in legacy knowledge-factory:
if not sha256:
    sha256 = hashlib.sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest()
```
**Why this violates Timonelo Canon**:
- A SHA-256 on an artifact MUST represent the SHA-256 of real, immutable physical bytes on disk (or HTTP payload).
- Computing a SHA-256 of a JSON dictionary creates a pseudo-hash that looks like a cryptographic artifact hash but verifies nothing.
- **Resolution**: Candidates without verified file bytes must have `artifact_sha256: null` and an explicit `candidate_fingerprint: "fp_sha256_..."` with status `UNVERIFIED_CANDIDATE`.

---

## 4. Consolidation Execution Plan

1. **Step 1**: Ensure canonical `timonelo` repository contains all active evidence, graph, and geometry capabilities.
2. **Step 2**: Import candidate planning schemas into `timonelo/schemas/`.
3. **Step 3**: Port `CoveragePlanner` into `src/timonelo/planning/`.
4. **Step 4**: Archive `FHoffarth/timonelo-knowledge-factory` repository with a pointer to `timonelo`.
