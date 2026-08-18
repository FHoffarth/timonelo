# 08_GIT_WORKFLOW — Branching Strategy & Staging Deployment

## 1. The Environment Hierarchy

```
feature/<ticket-id> (e.g. feature/FE-019-route-waypoints)
       │
       ▼ Local Verification (Build & Pytest 100% Green)
develop (Staging Environment -> staging.timonelo.com)
       │
       ▼ Staging Approval & Final Validation
main (Production Environment -> timonelo.com)
```

---

## 2. Mandatory Rules

1. **`main` is Production & Protected**:
   - Never commit directly to `main`.
   - `main` is updated exclusively via PR from `develop`.
2. **`develop` is Staging**:
   - All feature PRs merge into `develop`.
   - Every merge to `develop` automatically deploys to the staging environment for review.
3. **Feature Branches**:
   - Branch naming format: `feature/<ticket-id>-<short-description>` (e.g. `feature/FE-014-cruise-math-calc`).
   - Keep branch lifetimes short (1 feature or 1 page per branch).
   - Target PR size: **200–600 LOC**.

---

## 3. Pull Request Checklist

Before submitting a Pull Request:
- [x] Branch branched from up-to-date `develop`.
- [x] `python -m pytest tests/ -q` passes with 0 failures.
- [x] `npx vite build` completes with 0 errors.
- [x] No unrelated files modified in `git diff`.
- [x] Design Freeze v1 visual tokens preserved.
- [x] Documentation updated if new architecture was introduced.
