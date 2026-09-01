"""Shared helper for tests that need a genuinely publishable statement.

Publication requires evidence that supports the claim: an `EvidenceEvent` whose
entity, question and observed value match the statement's, citing an artifact
the workspace holds.

The first version of this helper manufactured that correspondence. It copied
`statement.value` into `observed_value` and `statement.locator` into `locator`,
so the "evidence" was the claim wearing a different hat, and every fixture
passed by construction whatever the cited artifact actually said. A test that
manufactures its own support demonstrates nothing.

`back_with_evidence` now requires the caller to state the observation
explicitly, and the artifact must genuinely be one that can answer the
question -- `EvidenceEventLog.append` enforces document class eligibility, so a
fixture citing an artifact that cannot support the claim fails loudly.

For suites that only need *a* published statement to exist -- conflict
detection, truth traversal, the curator CLI -- passing the value they already
asserted is legitimate: their artifact is a purpose-built fixture document
written for exactly that claim. What is no longer possible is doing it
silently, or doing it against an artifact that says something else.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

import hashlib

from timonelo.evidence import publication
from timonelo.evidence.events import EvidenceEvent

_counter = {"n": 0}


def _next_event_id() -> str:
    _counter["n"] += 1
    return f"EVT-FIXTURE-{_counter['n']:04d}"


def back_with_evidence(
    workspace: Any,
    statement: Any,
    *,
    observed_value: Any,
    locator: str,
    event_id: Optional[str] = None,
    observed_by: str = "fixture.observer",
    observed_on: str = "2026-08-17",
) -> Any:
    """Record an evidence event supporting `statement` and attach it.

    `observed_value` and `locator` are required and have no defaults on
    purpose: the caller must say what was observed and where, rather than the
    helper inferring it from the claim being supported.

    Returns the updated statement.
    """
    artifact = workspace.registry.get(statement.artifact_id)
    event_id = event_id or _next_event_id()
    workspace.events.append(EvidenceEvent(
        event_id=event_id,
        artifact_sha256=artifact.sha256,
        locator=locator,
        entity_id=statement.entity_id,
        question_id=statement.question_id,
        observed_value=observed_value,
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


class RuleStore:
    """A content-addressed rule store, for tests that need inference to work.

    ADR-0003 §3 makes a derived statement cite the hash of the rule it
    consumed, and publication admission now insists that hash resolve to
    something. The repository has no rule store, so INFERRED publication fails
    closed -- correct, and fatal to any test whose subject is further down the
    pipeline.

    This is the smallest thing that satisfies the ADR: rules keyed by the
    SHA-256 of their content, so editing a rule cannot help but change its
    hash. It exists so tests can reach their actual subject, and to prove the
    resolver seam is real rather than a place to hang an apology. It is not a
    proposal for the production store.
    """

    def __init__(self):
        self._by_hash = {}

    def add(self, content: bytes) -> str:
        digest = hashlib.sha256(content).hexdigest()
        self._by_hash[digest] = content
        return digest

    def remove(self, digest: str) -> None:
        self._by_hash.pop(digest, None)

    def trust(self, *rule_hashes: str) -> None:
        """Register hashes already cited by existing statements."""
        for digest in rule_hashes:
            if digest:
                self._by_hash[digest.lower()] = b"fixture rule"

    def resolve(self, digest):
        return self._by_hash.get((digest or "").lower())

    def install(self) -> "RuleStore":
        publication.set_rule_resolver(self.resolve)
        return self

    @staticmethod
    def uninstall() -> None:
        publication.set_rule_resolver(None)
