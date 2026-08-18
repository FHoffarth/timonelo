# AGENTS.md — Mandatory Instructions for All Autonomous Coding Agents

> **CRITICAL RULE FOR ALL AI AGENTS:**  
> You are operating within the canonical **Timonelo** codebase.  
> The following rules are absolute, non-negotiable, and must be followed on every interaction.

---

Every coding agent MUST read

```
/docs/00_READ_FIRST.md
```

before generating code.

---

### Core Behavioral Constraints:

* **Never overwrite existing pages.**
* **Never regenerate App.tsx.**
* **Never replace router.**
* **Never replace components.**
* **Modify only requested scope.**

---

### Stop Condition:

If a prompt implies replacing an existing page,

# STOP

and ask for confirmation.

---

### Git & Code Hygiene:

* **Keep unrelated git diff at zero.**
* **Default behaviour is:**
  * **extend**
  * **never**
  * **replace.**

---

### Canonical Reference Checklist:
1. **Design Freeze v1**: The Figma prototype is canonical for presentation. Never redesign spacing, typography, or colors (`#FBF8F3`, `#0C1B2A`, `#C58A46`).
2. **Preserve Truth Engine**: Never simplify the epistemic calculus (`[KNOWN]`, `[DERIVED]`, `[VERIFIED]`, `[LIKELY]`).
3. **Preserve Living Deck**: The Living Deck models the passenger's topological mental model (4 parallel tracks, structural lift cores, vertical buffers). Never replace it with raster graphics.
4. **Pre-flight Checks**:
   - `python -m pytest tests/ -q` must be **100% green**.
   - `npx vite build` in `frontend/` must finish with **0 errors**.
