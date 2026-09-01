"""Shared helper for tests that need a genuinely publishable statement.

Publication now requires evidence: a statement must cite at least one recorded
evidence event, resolving to an artifact the workspace holds. Before that gate
existed, fixtures could publish a statement that cited an artifact_id and
nothing else, because `publish()` never looked.

Most suites that call `publish()` are not testing publication -- they are
testing conflict detection, truth traversal, or the curator CLI, and simply
need a published statement to exist. `back_with_evidence` gives those fixtures
real backing rather than weakening the gate for them: it records an actual
`EvidenceEvent` against the artifact the statement already cites, and attaches
the event id to the statement.

The event goes through `EvidenceEventLog.append`, so it is validated exactly
like production evidence -- the artifact must be held, the locator real, and
the document class must be able to support the question. A fixture that cannot
satisfy that is telling you something true about the fixture.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

from timonelo.evidence.events import EvidenceEvent

_counter = {"n": 0}


def _next_event_id() -> str:
    _counter["n"] += 1
    return f"EVT-FIXTURE-{_counter['n']:04d}"


def back_with_evidence(
    workspace: Any,
    statement: Any,
    *,
    event_id: Optional[str] = None,
    observed_by: str = "fixture.observer",
    observed_on: str = "2026-08-17",
    locator: Optional[str] = None,
) -> Any:
    """Record a real evidence event for `statement` and attach it.

    Returns the updated statement. Safe to call more than once for the same
    statement; each call adds a further event.
    """
    artifact = workspace.registry.get(statement.artifact_id)
    event_id = event_id or _next_event_id()
    workspace.events.append(EvidenceEvent(
        event_id=event_id,
        artifact_sha256=artifact.sha256,
        locator=locator or (statement.locator or "fixture locator"),
        entity_id=statement.entity_id,
        question_id=statement.question_id,
        observed_value=statement.value,
        observed_by=observed_by,
        observed_on=observed_on,
    ))
    current = workspace.editor.get(statement.statement_id)
    updated = replace(
        current,
        evidence_event_ids=tuple(current.evidence_event_ids) + (event_id,),
    )
    workspace.editor._by_id[statement.statement_id] = updated
    workspace.editor._flush()
    return updated
