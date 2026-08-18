# Contributing to Timonelo

Thank you for contributing to **Timonelo** — the Scientific Cruise Intelligence Platform.

## 1. Mandatory First Step for All Contributors (Human & AI)

Before proposing, modifying, or implementing any changes in this repository, you **MUST** read:
👉 **[`docs/00_READ_FIRST.md`](./docs/00_READ_FIRST.md)**

The documentation in `/docs` defines the canonical product philosophy, spatial grammar, truth engine, and design freeze.

---

## 2. Fundamental Contributing Principles

1. **Documentation is Canonical**: Code must follow the documentation in `/docs`. Never introduce changes that contradict canonical architecture.
2. **Design Freeze v1 is Protected**: Do not redesign existing layouts, color tokens (`#FBF8F3`, `#0C1B2A`, `#C58A46`), or typography without explicit user instruction.
3. **Preserve the Truth Engine**: Never simplify or bypass epistemic provenance (`[KNOWN]`, `[DERIVED]`, `[VERIFIED]`). Knowledge certainty must always be grounded in evidence.
4. **Git Branching Strategy**:
   - Work on `feature/<ticket-id>-<description>` branches.
   - PR into `develop` (Staging).
   - `main` is reserved strictly for Production releases.

---

## 3. Pull Request Requirements

Every pull request must:
- [x] Have zero regressions across all 8 canonical page shells.
- [x] Pass `python -m pytest tests/ -q` with 100% green tests.
- [x] Pass `npx vite build` in `frontend/` with 0 errors.
- [x] Contain clean, targeted git diffs (no unrelated changes).
- [x] Keep PR size manageable (**200–600 LOC**).

For full engineering rules, refer to [`docs/07_IMPLEMENTATION_RULES.md`](./docs/07_IMPLEMENTATION_RULES.md).
