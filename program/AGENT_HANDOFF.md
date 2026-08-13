# Agent Handoff Protocol

All handoffs reference a GitHub Issue and preserve scope, evidence, unresolved risks, and review state. Chat transcripts are supporting context, not the authoritative work record.

## Required handoff record

| Field | Requirement |
| --- | --- |
| Inputs | Issue, approved source material, constraints, dependencies, and current state |
| Outputs | Files, findings, decisions, validation evidence, and unresolved items |
| Expected Deliverables | Exact artifacts and reporting format required by the work order |
| Review Requirements | Reviewer role, checks, and approval conditions |
| Completion Criteria | Acceptance criteria met, blockers resolved, and board status updated |

## ChatGPT

Coordinates intent, clarifies scope, and prepares reviewable work orders. Handoffs must identify the authoritative Issue and separate confirmed requirements from discussion.

## Gemini

Provides bounded analysis or review against supplied inputs. Handoffs must cite examined artifacts, state assumptions, and classify findings by severity.

## Codex

Performs repository-scoped implementation and validation. Handoffs must include the exact diff scope, commands run, results, remaining risks, and Git state.

## Claude

Performs bounded drafting, analysis, or implementation when assigned. Handoffs must identify changed artifacts, verification performed, and any work requiring independent review.

## Transfer sequence

1. Outgoing agent updates the Issue with its deliverables and evidence.
2. Incoming agent verifies inputs before continuing.
3. Scope gaps or contradictions return to the owner for resolution.
4. Completion is recorded only after the required review.
