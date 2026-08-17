"""
Evidence Event Log — append-only record of observations.

Governed by ADR-0002 §1, §5.

An evidence event states that an observation OCCURRED: who observed what, in
which artifact, at which locator, on which date. It is never an attribute
attached to a value.

The log is append-only. Corrections are new events, never edits — which makes
"what did we believe on date D" a fold truncated at D rather than an
archaeology project.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from timonelo.canonical import canonical_dump
from timonelo.evidence.artifacts import ArtifactStore


@dataclass(frozen=True)
class EvidenceEvent:
    """One observation, tied to a possessed artifact."""
    event_id: str
    artifact_sha256: str      # must exist in the ArtifactStore
    locator: str              # page/sheet/region within the artifact
    entity_id: str            # e.g. "cabin:MSC-BELLISSIMA:14122"
    question_id: str          # which registered question this answers
    observed_value: Any
    observed_by: str          # named human or instrument
    observed_on: str          # ISO date
    supersedes: Optional[str] = None   # event_id this corrects
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "artifact_sha256": self.artifact_sha256,
            "locator": self.locator,
            "entity_id": self.entity_id,
            "question_id": self.question_id,
            "observed_value": self.observed_value,
            "observed_by": self.observed_by,
            "observed_on": self.observed_on,
            "supersedes": self.supersedes,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "EvidenceEvent":
        return EvidenceEvent(**d)  # type: ignore[arg-type]


class EvidenceEventLog:
    """Append-only log. Validates every event against the artifact store."""

    def __init__(self, path: str, store: ArtifactStore, registry=None):
        self.path = path
        self.store = store
        self.registry = registry
        self._events: List[EvidenceEvent] = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self._events = [EvidenceEvent.from_dict(e) for e in json.load(f)]

    def append(self, event: EvidenceEvent) -> EvidenceEvent:
        if any(e.event_id == event.event_id for e in self._events):
            raise ValueError(f"Duplicate event_id {event.event_id!r}")

        # An event may only cite an artifact we actually hold.
        if not self.store.has(event.artifact_sha256):
            raise ValueError(
                f"Event {event.event_id!r} cites artifact "
                f"{event.artifact_sha256[:12]}... which is not in the store. "
                "Evidence may only reference documents actually possessed."
            )
        if not event.locator:
            raise ValueError(
                f"Event {event.event_id!r} has no locator. An observation must "
                "state WHERE in the artifact it was made."
            )
        if not event.observed_by:
            raise ValueError(f"Event {event.event_id!r} has no observer.")

        # A document may only support the claims it is capable of supporting.
        if self.registry is not None:
            question = self.registry.get(event.question_id)
            artifact = self.store.get(event.artifact_sha256)
            if not question.can_be_supported_by(artifact.document_class):
                raise ValueError(
                    f"Artifact class {artifact.document_class!r} cannot support "
                    f"question {event.question_id!r}. A document may only "
                    "support the claims it is actually capable of supporting."
                )

        self._events.append(event)
        self._flush()
        return event

    def all(self, as_of: Optional[str] = None) -> List[EvidenceEvent]:
        """Events, optionally folded to a point in time (ADR-0002 §4.1)."""
        events = self._events
        if as_of is not None:
            events = [e for e in events if e.observed_on <= as_of]
        superseded = {e.supersedes for e in events if e.supersedes}
        return [e for e in events if e.event_id not in superseded]

    def for_entity(self, entity_id: str, as_of: Optional[str] = None) -> List[EvidenceEvent]:
        return [e for e in self.all(as_of) if e.entity_id == entity_id]

    def __len__(self) -> int:
        return len(self._events)

    def _flush(self) -> None:
        canonical_dump([e.to_dict() for e in self._events], self.path)
