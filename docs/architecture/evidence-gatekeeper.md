# Architecture Specification: Evidence Gatekeeper v1

**Document ID**: `TIM-ARCH-EVID-001`  
**Status**: `CANONICAL`  
**Version**: `1.0.0`  
**Date**: `2026-08-18`  
**Governing ADRs**: `ADR-0002 (Ground Truth Epistemology)`, `ADR-0003 (Content Addressing)`

---

## 1. Executive Summary & Purpose

The **Evidence Gatekeeper v1** is the foundational epistemic trust infrastructure of Timonelo. It guarantees that no knowledge pack, spatial geometry polygon, or semantic graph relation can be certified as `CANONICAL`, `PUBLISHED`, or `DIRECT` without cryptographically verifiable, machine-evaluated primary source evidence.

### Core Principles
1. **No Evidence $\rightarrow$ No Canonical Truth**: Factual claims without verifiable primary sources cannot enter the canonical knowledge layer.
2. **Unverified $\neq$ False**: An unverified claim is simply unverified (`UNVERIFIED`), not discarded or fraudulently marked verified.
3. **Epistemic Ceiling**: A downstream or derived layer can never possess higher epistemic trust than its weakest upstream input.
4. **Epistemic Honesty**: Synthetic templates and programmatic coordinate approximations must be explicitly classified as `SYNTHETIC_GEOMETRY`.

---

## 2. Ingestion Pipeline & Epistemic Hierarchy

The Knowledge Factory enforces strict linear dependency order:

```
Physical Source Artifact (PDF / CAD / Official Register on Disk)
   ↓ (SHA-256 Byte Digest Verification)
SourceArtifactRecord (VERIFIED / MISSING / HASH_MISMATCH)
   ↓ (Page / Section / Visual Locator Binding)
FactEvidenceRecord (DIRECT / DERIVED / INFERRED / UNVERIFIED / CONFLICTED)
   ↓ (Vector Extraction vs. Synthetic Template)
GeometryProvenanceRecord (DIRECT_SOURCE / TRANSFORMED / DERIVED / SYNTHETIC)
   ↓ (W3C BOT Spatial Graph Raycasting)
SemanticGraphRelations (GROUNDED / DERIVED / SYNTHETIC)
   ↓ (Mathematical Ratio Metrics)
EpistemicCoverageEngine & ConflictGate
   ↓ (4-Tier Release Evaluator)
PublishGatekeeper (PUBLISH_ALLOWED / PUBLISH_WARNINGS / PUBLISH_BLOCKED)
```

---

## 3. Epistemic Status Models

### 3.1 Source Artifact Verification Status
- **`VERIFIED`**: Physical file exists on local storage, and its computed `sha256` byte digest matches the record.
- **`UNVERIFIED`**: Source metadata exists, but file has not been verified.
- **`MISSING`**: Referenced source file is absent from disk.
- **`HASH_MISMATCH`**: File exists, but calculated SHA-256 diverges from expected digest.

### 3.2 Fact Epistemic Classifications
- **`DIRECT`**: Grounded in a `VERIFIED` source artifact with a specific page/region locator.
- **`DERIVED`**: Mathematically or logically calculated from parent facts with explicit `parent_fact_ids`.
- **`INFERRED`**: Plausible industry/sister-ship analogy without direct local primary citation.
- **`UNVERIFIED`**: Unsubstantiated or unchecked claim.
- **`CONFLICTED`**: Two or more verified sources provide irreconcilable values (requires $\ge 2$ evidence locators).

### 3.3 Geometry Provenance Categories
1. **`DIRECT_SOURCE_GEOMETRY`**: Directly extracted from vector GA drawings without template approximations.
2. **`TRANSFORMED_SOURCE_GEOMETRY`**: Extracted from raster/CAD sources with documented, reproducible affine coordinate transforms.
3. **`DERIVED_GEOMETRY`**: Computed geometrically from verified adjacent structural elements.
4. **`SYNTHETIC_GEOMETRY`**: Programmatic mathematical grids, bounding box templates, or heuristic approximations (confidence bounded to $\le 0.60$).
5. **`UNKNOWN_PROVENANCE`**: Unattributed geometric coordinates.

---

## 4. Epistemic Ceiling Function

The central utility `compute_epistemic_ceiling(...)` restricts downstream claims:

$$\text{Trust}(\text{Target}) \le \min_{i \in \text{Dependencies}} \text{Trust}(i)$$

- If any upstream source is `MISSING` or `HASH_MISMATCH`, the fact status defaults to `UNVERIFIED`.
- If spatial geometry is `SYNTHETIC_GEOMETRY`, dependent graph edges cannot be promoted to `DIRECT` (ceiling is `INFERRED` / `DERIVED`).
- If an input fact is `CONFLICTED`, downstream intelligence scores must preserve the conflict warning.

---

## 5. Deterministic Coverage Calculation

Hardcoded coverage percentage strings are strictly banned. The `CoverageEngine` computes reproducible ratios:

| Metric | Formula | Description |
| :--- | :--- | :--- |
| **Source Coverage** | $\frac{\text{Verified Sources}}{\text{Total Sources}} \times 100$ | Ratio of physically validated artifacts. |
| **Fact Evidence Coverage** | $\frac{\text{Direct Facts} + \text{Derived Facts}}{\text{Total Facts}} \times 100$ | Proportion of grounded knowledge facts. |
| **Direct Evidence Coverage** | $\frac{\text{Direct Facts}}{\text{Total Facts}} \times 100$ | Proportion of primary-source facts. |
| **Geometry Provenance Coverage** | $\frac{\text{Direct} + \text{Transformed Geometry}}{\text{Total Geometry Objects}} \times 100$ | Proportion of blueprint-extracted geometry. |
| **Graph Provenance Coverage** | $\frac{\text{Grounded Relations}}{\text{Total Relations}} \times 100$ | Proportion of verified spatial connections. |

### Global Epistemic Score Formula:
$$\text{GlobalScore} = 0.30 \times \text{SourceCov} + 0.30 \times \text{FactCov} + 0.20 \times \text{GeomCov} + 0.20 \times \text{GraphCov}$$

---

## 6. Conflict Gate & Publish Gatekeeper

### Conflict Gate Rules:
- If conflict detection was not executed (`executed = false`), the system must output:  
  `"CONFLICT STATUS UNKNOWN (Conflict Detection not executed)"`
- Reports are forbidden from claiming `"0 conflicts"` without an executed resolver run.

### Publish Gate Decisions:
- **`PUBLISH_ALLOWED`**: All sources verified, zero schema/geometry violations, conflict detection executed, no unresolved P0s.
- **`PUBLISH_ALLOWED_WITH_WARNINGS`**: Allowed with minor non-blocking flags (e.g., lower non-critical coverage).
- **`PUBLISH_BLOCKED`**: Release rejected with explicit machine-readable blocker codes:
  - `PRIMARY_SOURCE_MISSING`
  - `SOURCE_HASH_MISMATCH`
  - `INVALID_FACT_EPISTEMIC_STATUS`
  - `GEOMETRY_PROVENANCE_VIOLATION`
  - `CONFLICT_DETECTION_NOT_EXECUTED`
  - `UNRESOLVED_CRITICAL_CONFLICTS`

---

## 7. Anti-Patterns & Banned Practices

| Anti-Pattern | Why It Is Forbidden | Correct Procedure |
| :--- | :--- | :--- |
| **Schema-valid $\neq$ Evidence-valid** | Valid JSON syntax does not mean the underlying statements are true. | Schema validation is Gate 1; Evidence verification is Gate 2. |
| **Synthetic Geometry as `DIRECT`** | Labeling a programmatic coordinate loop as direct blueprint observation falsifies provenance. | Label synthetic templates as `SYNTHETIC_GEOMETRY` with confidence $\le 0.60$. |
| **Hardcoded Report Strings** | Writing `"99.4% coverage"` into markdown without computation creates fake trust. | All coverage metrics must be dynamically calculated from model objects. |
| **Generated Reports as Evidence** | A generated report is not proof of the claims inside the report. | Only raw physical artifact byte digests constitute root evidence. |
| **Silent Overwrites** | Updating canonical JSON without logging the diff or preserving previous provenance destroys auditability. | Route all contradictions through `ConflictResolver.ts`. |
