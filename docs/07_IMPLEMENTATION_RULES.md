# 07_IMPLEMENTATION_RULES — Engineering Safeguards & Code Modification Protocol

## 1. Strictly Forbidden Actions

When working on any future task or feature in this repository, **NEVER**:

1. ❌ **Regenerate or replace `App.tsx` wholesale.**
2. ❌ **Rewrite or wipe out global styling in `index.css`.**
3. ❌ **Recreate the routing mechanism from scratch.**
4. ❌ **Delete or alter reusable UI primitives in `components/ui/`.**
5. ❌ **Regenerate an entire page when only modifying one section or dataset.**
6. ❌ **Simplify the Truth Engine or discard epistemic provenance links.**
7. ❌ **Commit code with failing tests or broken TypeScript builds.**

---

## 2. Mandatory Workflow for Page Modifications

When asked to update a specific page (e.g. updating a section in `/cabin/:id`):

1. **Step 1: Check Git Status & Create Safety Backup**:
   ```bash
   git status
   git branch backup/YYYY-MM-DD-<ticket-name>
   ```
2. **Step 2: Inspect Target Components**:
   Identify the precise component file responsible for the section (e.g. `frontend/src/components/pages/CabinDeepDivePage.tsx`).
3. **Step 3: Make Surgical, Incremental Edits**:
   Use targeted string replacements or component composition. Do not wipe out unrelated sections.
4. **Step 4: Verify Zero Regressions**:
   - Run `npx vite build` in `frontend/` (0 errors).
   - Run `python -m pytest tests/ -q` in repo root (100% green).
   - Verify all other canonical pages (`/`, `/ships`, `/ports`, `/routes`, `/cruise-math`, `/travel-info`) remain functional.
5. **Step 5: Inspect Git Diff Before Committing**:
   ```bash
   git diff --stat
   ```
   Ensure **only expected files** are in the diff.

---

## 3. Component Composition Standard

Do not embed bespoke CSS or inline layouts directly inside page shells.

Always build or use reusable components:
- Need a section headline? Use `<SectionHeader title="..." eyebrow="..." />`.
- Need a facts breakdown? Use `<QuickFactsCard items={...} />`.
- Need an alert or notice? Use `<WarningCard title="..." message="..." />`.
- Need a route waypoint? Use `<TimelineCard stepLabel="..." title="..." subtitle="..." />`.
