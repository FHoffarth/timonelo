# TIMONELO — Repository Canon Drift Audit Report
**Date**: 2026-08-18
**Branch**: `hardening/repository-canon-truth-path`
**Author**: Timonelo Architecture Hardening Sprint (Phase 1)
**Status**: CANONICAL CONSOLIDATION COMPLETE

---

## 1. Executive Summary & Product Framing

During repository evolution, divergent claims regarding product classification, epistemic truth, spatial geometry, and publication authority emerged across documentation, backend engines, and frontend pipelines.

### Canonical Product Framing
> **Timonelo is a Cruise Intelligence Platform.**
> Its purpose is to provide explainable, evidence-based answers about ships, cabins, routes, and ports.

All competing descriptions (e.g., "Digital Twin", "Travel App", "Knowledge Platform", "Personal Cruise Operating System", "Decision Intelligence Platform") are formally superseded or subordinated under the single umbrella: **Cruise Intelligence Platform**.

---

## 2. Comprehensive Canon Conflicts & Resolution Matrix

| Document / Code Location | Current Claim | Actual Implementation Behavior | Canonical Decision | Required Action |
|---|---|---|---|---|
| `README.md` (L11-14) | "not a travel app, and not a knowledge platform. It is a digital twin of a ship..." | Mixed claims across repo; UI presents Cruise Intelligence Platform | Timonelo is a **Cruise Intelligence Platform**. | **UPDATE** |
| `pyproject.toml` (L8, 22) | "Personal cruise operating system... bridge-officer-tim" | Keyword bloat and unbacked claims | Align with Cruise Intelligence Platform description | **UPDATE** |
| `AGENTS.md` (L51) | Lists `[KNOWN]`, `[DERIVED]`, `[VERIFIED]`, `[LIKELY]` as epistemic calculus | Collapses method, derivation, and review state into single flat tags | Adopt ADR-0002 two-axis model: Method (DIRECT/CALCULATED/INFERRED) + Derivation (LOCAL/SISTER_SHIP/REFERENCE_MODEL/GENERATED) | **UPDATE** |
| `docs/00_READ_FIRST.md` | "Scientific Cruise Intelligence Platform" with mixed truth claims | Good baseline, but contains legacy Bridge Officer authority citations | Align reading order, binding ADR list, and remove truth-authoring role from Bridge Officer | **UPDATE** |
| `docs/03_TRUTH_ENGINE.md` | Flat `VERIFIED/KNOWN/DERIVED/LIKELY/UNKNOWN` confidence literals | Disagrees with ADR-0002 invariant I1 (confidence is never stored) | Supersede flat literals with computed confidence over min-lattice | **SUPERSEDE** |
| `src/timonelo/factory/archetype_generator.py` | Generates 2,217 cabins arithmetically with `evidence_links` | Generates unverified synthetic staterooms and attaches unheld GA evidence links | Arithmetic generators produce **Hypothesis Store** data only; prohibited from Ground Truth | **QUARANTINE** |
| `src/timonelo/factory/patch_engine.py` | SPEC-008 delta overlays with silent `continue`, borrowed evidence, default SHA | Silent failure on missing deck; venue replacement inherits base evidence links; 64-zero SHA | Hard failures on invalid targets; no borrowed evidence; no synthetic Ground Truth | **QUARANTINE** |
| `src/timonelo/ontology/bellissima.py` | "Double-Verified Onboard Physical Surveys" | Calls archetype generator with `sha256=None` and unheld evidence IDs | Isolate as legacy fixture / test double; cannot write canonical ground truth | **QUARANTINE** |
| `src/timonelo/database/bridge_officer.py` | `confidence_score: float = 99.5` | Hardcoded confidence literal | Remove hardcoded confidence literal; Bridge Officer Tim is orchestrator only | **UPDATE** |
| `frontend/src/knowledge/pipeline/ConflictResolver.ts` | Auto-supersedes if `new_confidence > old_confidence`; sets `approved_by: "Bridge Officer Tim"` | Auto-resolves conflicts by comparing confidence; officer automatically approves | Conflicts must NOT auto-resolve solely by confidence; Bridge Officer cannot approve canonical truth | **UPDATE** |
| `frontend/src/knowledge/pipeline/KnowledgePublisher.ts` | 4 hardcoded validation gates with `passed: true`, `release_id: REL-...-Date.now()` | Hardcoded passing validation; non-deterministic release ID | Implement real validation gate check against Evidence Gatekeeper; deterministic release ID | **UPDATE** |
| `frontend/src/twin/` & `frontend/src/semantic-deck/` | Legacy prototype implementations | Contain TypeScript compilation errors and obsolete truth assumptions | Quarantine legacy modules and ensure strict typecheck passes | **QUARANTINE** |
| `.github/workflows/ci.yml` | `on: [main, master]` only, runs `python -m unittest discover` (claims "136+ Unit Tests") | Does not run on `develop` or PRs; uses unittest instead of pytest; skips typecheck validation in develop PRs | Update CI to run pytest on all branches, run strict typecheck + build, and remove obsolete test counts | **UPDATE** |
| `pyproject.toml` (L24) | `dependencies = []` | Runtime modules import standard and core packages | Declare actual runtime and test dependencies | **UPDATE** |

---

## 3. Epistemic Model Realignment Plan

1. **Orthogonal Separation**:
   - **Method**: `DIRECT` (read from primary source) \| `CALCULATED` (truth-preserving derivation) \| `INFERRED` (defeasible rule).
   - **Derivation**: `LOCAL` (observed on this vessel) \| `SISTER_SHIP` (observed on sister ship) \| `REFERENCE_MODEL` (class model) \| `GENERATED` (hypothesis/synthetic).
   - **Review State**: `DRAFT`, `SUBMITTED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`, `REJECTED` (independent of method).
   - **Conflict**: Stored independently as `ConflictDecision` without silent auto-resolution.
   - **UNKNOWN**: Computed dynamically when no satisfying statement exists for a registered question (Invariant I3).
   - **Geometry Provenance**: `DIRECT_SOURCE_GEOMETRY` \| `TRANSFORMED_SOURCE_GEOMETRY` \| `DERIVED_GEOMETRY` \| `SYNTHETIC_GEOMETRY` \| `UNKNOWN_PROVENANCE`.

2. **Confidence Computation**:
   - Never stored as a writable canonical field (Invariant I1).
   - Computed dynamically via min-lattice propagation:
     - `DIRECT` $\rightarrow$ source reliability
     - `CALCULATED` $\rightarrow \min(\text{inputs})$
     - `INFERRED` $\rightarrow \min(\text{inputs}) \times \text{rule.defeasibility}$

---

## 4. Quarantine Boundaries

1. **Hypothesis Store vs. Ground Truth**:
   - `archetype_generator.py` and `patch_engine.py` are explicitly marked as legacy hypothesis tools.
   - Any data generated by these engines is tagged `DERIVATION = GENERATED` and stored strictly in the Hypothesis Store (`data/hypotheses/`).
   - Canonical Ground Truth (`knowledge/ships/`) accepts only verified physical evidence events.

2. **Legacy Ontology Quarantine**:
   - `src/timonelo/ontology/bellissima.py` and `andorinha.py` are preserved for test fixtures only and prohibited from writing to `data/cruise_intelligence_db.json`.

3. **Frontend Type & Pipeline Quarantine**:
   - `frontend/src/twin/` and `src/semantic-deck/` are quarantined or type-repaired so `tsc --noEmit` is 100% clean.
   - `KnowledgePublisher` and `ConflictResolver` are stripped of fake auto-approval and hardcoded gates.

---

## 5. Next Steps for Hardening
- Execute Phase 2: Epistemic models update in Python and TypeScript.
- Execute Phase 3 & 4: Code quarantine and Bridge Officer governance.
- Execute Phase 5: Gatekeeper consolidation.
- Execute Phase 6 & 7: CI and packaging hardening.
- Execute Phase 8: Second repository audit report.
- Execute Phase 9 & 10: Canonical documentation and test verification.
