# AGENTS.md — Mandatory Instructions for All Autonomous Coding Agents

> **CRITICAL MANDATE FOR ALL AI AGENTS & CONTRIBUTORS:**
> You are operating within the canonical **Timonelo** repository.
> Timonelo is a **Cruise Intelligence Platform** providing explainable, evidence-based answers about ships, cabins, routes and ports.
> The following rules are absolute, non-negotiable, and must be followed on every interaction.

---

### 1. Mandatory Entry Point

Every coding agent MUST read:
```
/docs/00_READ_FIRST.md
/docs/adr/ADR-0002.md
```
before modifying or creating any code in this repository.

---

### 2. Core Epistemic Principles

1. **Evidence First**: Timonelo must be able to say “we do not know” before it is allowed to say “this is true.”
2. **One Canonical Architecture**:
   `Evidence → Knowledge → Geometry → Graph → Intelligence → Explainability → User`
3. **No Silent Truth Fabrication**:
   - `UNKNOWN` is a computed absence of satisfying published statements, not a stored literal.
   - Confidence is computed from the evidence derivation graph, never stored as a canonical truth float.
   - Physical artifacts must be verified with real SHA-256 hashes of disk bytes.
4. **Bridge Officer Tim Governance**:
   - Bridge Officer Tim is an orchestrator only.
   - It may NEVER declare facts true, approve conflicts unilaterally, or publish canonical knowledge.

---

### 3. Core Behavioral Constraints

* **Never overwrite existing pages or replace entire components.**
* **Never regenerate `App.tsx` or router from scratch.**
* **Keep unrelated git diff at zero.**
* **Quarantined hypothesis tools** (`patch_engine.py`, `archetype_generator.py`) must NEVER write to canonical `knowledge/ships/`.
* **Default behavior is:**
  * **extend**
  * **never**
  * **replace.**

---

### 4. Verification Checklist Before Marking Work Complete

1. `python -m pytest tests/ -q` must be **100% green**.
2. `npm.cmd --prefix frontend run typecheck` must finish with **0 errors**.
3. `npm.cmd --prefix frontend run build` must build successfully.
4. No forbidden truth shortcuts (`"passed: true"`, hardcoded confidence floats, unquarantined mock hashes).
