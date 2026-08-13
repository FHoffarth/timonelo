# Timonelo Program

## Program purpose

The program framework coordinates scoped work across governance, knowledge, architecture, engineering, quality assurance, and operations. GitHub Issues and the Timonelo Program board are the operational system of record.

## Release philosophy

Releases group completed, reviewed work into explicit outcomes. Each release has a defined scope, known risks, deferred work, and an approval record. Work not meeting its acceptance criteria remains outside the release.

## Sprint philosophy

A sprint is a bounded work package with one owner, explicit inputs, constraints, deliverables, acceptance criteria, and a definition of done. Scope changes require a documented decision or a replacement work order.

## Issue-first workflow

1. Create or select a GitHub Issue before work begins.
2. Confirm owner, labels, priority, dependencies, and board status.
3. Prepare the sprint or work order from the relevant template.
4. Move the Issue to `In Progress` only when inputs are available.
5. Record deliverables against the Issue and move it to `Review`.
6. Move it to `Done` only after required review and acceptance.

Chat history may provide context but is not the program record.

## Review workflow

Reviews use [REVIEW_TEMPLATE.md](REVIEW_TEMPLATE.md) and distinguish blocking from non-blocking findings. Blocking findings return the Issue to `In Progress`. Approval requires verified acceptance criteria, complete deliverables, and no unresolved blocking issue. Decisions with lasting operational impact use [DECISION_TEMPLATE.md](DECISION_TEMPLATE.md).

## Operating references

- [Master backlog](MASTER_BACKLOG.md)
- [Sprint template](SPRINT_TEMPLATE.md)
- [Work order template](WORK_ORDER_TEMPLATE.md)
- [Release template](RELEASE_TEMPLATE.md)
- [Agent handoff protocol](AGENT_HANDOFF.md)
- [Agent roles](agents/)
