# Architecture Decision Records (ADRs)

---

## 1. What are Architecture Decision Records?

Architecture Decision Records (ADRs) capture significant, sovereign architectural choices made in the Timonelo platform. They record the **context**, **problem statement**, **decision**, **alternatives considered**, and **consequences** of foundational design choices.

---

## 2. Why ADRs Exist

- **Institutional Continuity**: Preserves the structural rationale behind core boundaries, preventing cycles of re-debating settled architectural decisions.
- **Epistemic Hygiene**: Ensures every architectural boundary has an explicit, documented purpose and clear separation of concerns.
- **Evolutionary Discipline**: Any future proposal to alter core layers or data models must reference and supersede an existing ADR.

---

## 3. ADR Index

| ADR | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| **[ADR-0001](ADR-0001.md)** | Adopt the Five-Plane Spatial Architecture | **Approved** | 2026-08-15 |

---

## 4. How New ADRs are Created

1. Propose a new numbered document (e.g., `ADR-0002.md`) following the canonical template (Status, Context, Decision, Consequences).
2. Ensure the proposal adheres to the [Epistemic Canon](../CANON.md) and [Engineering Principles](../ENGINEERING_PRINCIPLES.md).
3. Submit a Pull Request for maintainer review and approval.
