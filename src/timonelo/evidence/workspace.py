"""
Evidence Workspace — the curator's view of the store.

Governed by ADR-0002. Adds no new model: it binds the registry, editor, review
log, question registry and truth engine to one directory, and formats them for
a human who has to decide whether a statement is trustworthy.

Everything here is read-and-format except the thin create/transition wrappers,
which delegate to the components that own those rights.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from timonelo.evidence import authority
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.models import Statement
from timonelo.evidence.events import EvidenceEventLog
from timonelo.evidence.importer import import_pdf
from timonelo.evidence.questions import QuestionRegistry
from timonelo.evidence.registry import Artifact, ArtifactRegistry
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.review import ReviewLog
from timonelo.evidence.truth import Answer, TruthEngine
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus

DEFAULT_ROOT = "evidence"


class Workspace:
    """One evidence store on disk."""

    def __init__(self, root: str = DEFAULT_ROOT):
        self.root = root
        # Workspace-declared document classes load before anything reads the
        # matrix, so a curator can add a class without editing source.
        authority.load_workspace_classes(
            os.path.join(root, "registry", "document_classes.json"))
        self.registry = ArtifactRegistry(os.path.join(root, "artifacts"))
        self.reviews = ReviewLog(os.path.join(root, "reviews", "log.json"))
        self.conflicts = ConflictLog(os.path.join(root, "reviews", "conflicts.json"))
        self.questions = QuestionRegistry.load(
            os.path.join(root, "registry", "questions.json"))
        events_path = os.path.join(root, "events", "events.json")
        self.events = EvidenceEventLog(events_path, self.registry, self.questions)
        # The editor is constructed after the question registry and the event
        # log because publication admission needs both; an editor without them
        # cannot prove backing and so cannot publish.
        self.editor = StatementEditor(
            os.path.join(root, "statements", "statements.json"),
            self.registry, self.reviews, self.conflicts,
            events=self.events, questions=self.questions)
        self.engine = TruthEngine(self.questions, self.editor, self.registry,
                                  self.conflicts)

    # -- structured APIs ------------------------------------------------------

    @property
    def artifacts_api(self):
        from timonelo.evidence.api import ArtifactInspectionAPI
        return ArtifactInspectionAPI(self)

    @property
    def statements_api(self):
        from timonelo.evidence.api import StatementRegistryAPI
        return StatementRegistryAPI(self)

    # -- artifacts ------------------------------------------------------------

    def import_artifact(self, path: str, **kwargs) -> Artifact:
        return import_pdf(self.registry, path, **kwargs)

    def list_artifacts(self) -> List[Artifact]:
        return self.registry.list_all()

    def statements_for_artifact(self, artifact_id: str) -> List[Statement]:
        return [s for s in self.editor.all() if s.artifact_id == artifact_id]

    def document_coverage(self, artifact_id: str) -> Dict[str, Any]:
        """Coverage OF ONE DOCUMENT, not of a ship.

        Supported = questions whose statement type this document's class has
        authority over. Answered = of those, the ones this document has an
        answerable statement for. A document is not responsible for questions
        it could never answer, so those are excluded rather than counted
        against it.
        """
        artifact = self.registry.get(artifact_id)
        cls = artifact.document_class

        supported = [
            q for q in self.questions.all()
            if q.statement_type is not None
            and cls in authority.AUTHORITY.get(q.statement_type, ())
        ]
        mine = self.statements_for_artifact(artifact_id)
        # "Answered" has to mean answerable now. Read off stored axes, this
        # number kept counting questions whose supporting evidence had been
        # superseded, and it is inherited wholesale by every artifact summary
        # -- so one stale statement quietly inflated the coverage of the
        # document it came from. `questions_supported` is unaffected: which
        # questions a document class *could* answer is a fact about the class,
        # not about any statement, and stays structural.
        answered_ids = {
            s.question_id for s in mine
            if self.editor.is_currently_authoritative(s)
        }
        answered = [q for q in supported if q.question_id in answered_ids]
        unknown = [q for q in supported if q.question_id not in answered_ids]
        return {
            "artifact_id": artifact_id,
            "document_class": cls,
            "questions_supported": len(supported),
            "questions_answered": len(answered),
            "questions_unknown": len(unknown),
            "coverage_pct": round(100 * len(answered) / len(supported), 1) if supported else 0.0,
            "unknown_question_ids": sorted(q.question_id for q in unknown),
        }

    # -- statements -----------------------------------------------------------

    def create_statement(self, **kwargs) -> Statement:
        return self.editor.create(**kwargs)

    def set_evidence_condition(self, statement_id: str, condition: EvidenceCondition,
                               actor: str, occurred_on: str, note: str = "") -> Statement:
        return self.editor.set_evidence_condition(statement_id, condition, actor, occurred_on, note)

    def transition(self, statement_id: str, to_state: HumanReviewState,
                   actor: str, occurred_on: str, note: str = "") -> Statement:
        return self.editor.transition(statement_id, to_state, actor, occurred_on, note)

    def publish_statement(self, statement_id: str, actor: str,
                          occurred_on: str, note: str = "") -> Statement:
        return self.editor.publish(statement_id, actor, occurred_on, note)

    def list_statements(self) -> List[Statement]:
        return self.editor.all()

    # -- formatting -----------------------------------------------------------

    def format_artifact(self, artifact_id: str) -> str:
        a = self.registry.get(artifact_id)
        intact = self.registry.verify(artifact_id)
        cls = authority.DOCUMENT_CLASSES.get(a.document_class)
        cov = self.document_coverage(artifact_id)
        stmts = self.statements_for_artifact(artifact_id)

        lines = [
            f"ARTIFACT {a.artifact_id}",
            f"  filename            {a.filename}",
            f"  document class      {a.document_class}"
            + (f"  ({cls.label})" if cls else "  [UNDECLARED]"),
            f"  sha256              {a.sha256}",
            f"  integrity           {'INTACT' if intact else 'FAILED — bytes differ'}",
            f"  size                {a.byte_size} bytes",
            f"  publisher           {a.publisher or 'UNKNOWN'}",
            f"  published on        {a.published_on or 'UNKNOWN'}",
            f"  version             {a.version or 'UNKNOWN'}",
            f"  language            {a.language or 'UNKNOWN'}",
            f"  acquired on         {a.acquired_on}",
            f"  acquisition method  {a.acquisition_method}",
        ]
        if cls:
            lines += [
                f"  reliability         {cls.reliability}",
                f"  validity scope      {cls.validity_scope.value}",
                f"  use permission      {cls.use_permission.value}",
            ]
        if a.notes:
            lines.append(f"  notes               {a.notes}")

        lines.append("")
        lines.append(f"  DOCUMENT COVERAGE")
        lines.append(f"    Questions supported   {cov['questions_supported']}")
        lines.append(f"    Questions answered    {cov['questions_answered']}")
        lines.append(f"    Questions UNKNOWN     {cov['questions_unknown']}")
        lines.append(f"    Coverage              {cov['coverage_pct']}%")
        if cov["unknown_question_ids"]:
            lines.append(f"    Unanswered            {', '.join(cov['unknown_question_ids'])}")

        lines.append("")
        lines.append(f"  LINKED STATEMENTS ({len(stmts)})")
        if not stmts:
            lines.append("    none")
        for s in stmts:
            lines.append(
                f"    {s.statement_id}  {s.review_state:<13} "
                f"{s.question_id}  {s.statement_type} = {s.value}")
        return "\n".join(lines)

    def format_statement(self, statement_id: str) -> str:
        s = self.editor.get(statement_id)
        a = self.registry.get(s.artifact_id)
        q = self.questions.get(s.question_id)
        cls = authority.DOCUMENT_CLASSES.get(a.document_class)
        # "passenger sees" is a claim about what the system will show a real
        # person, so it must be the current verdict and not the stored one.
        # `workflow state` below is deliberately still the stored axis: that
        # line is reporting review history, which is exactly what it should
        # report.
        answerable = self.editor.is_currently_authoritative(s)

        lines = [
            f"STATEMENT {s.statement_id}",
            f"  question        {s.question_id}  {q.labels.get('en', '')}",
            f"  statement type  {s.statement_type}",
            f"  answer          {s.value}",
            "",
            f"  artifact        {a.artifact_id}  {a.filename}",
            f"  document class  {a.document_class}",
            f"  page            {s.page if s.page is not None else 'UNKNOWN'}",
            f"  locator         {s.locator}",
            f"  read by         {s.read_by} on {s.read_on}",
            f"  method          {s.method}",
        ]
        if s.valid_from or s.valid_until:
            lines.append(
                f"  validity        {s.valid_from or 'open'} .. {s.valid_until or 'open'}")
        if s.note:
            lines.append(f"  note            {s.note}")

        lines += [
            "",
            f"  workflow state  {s.review_state}",
            f"  passenger sees  {'YES' if answerable else 'NO — not answerable in this state'}",
        ]
        if cls:
            lines.append(f"  confidence      {cls.reliability} (computed from {a.document_class})")

        history = self.reviews.history(statement_id)
        lines.append("")
        lines.append(f"  REVIEW HISTORY ({len(history)})")
        if not history:
            lines.append("    none — statement has not left DRAFT")
        for h in history:
            lines.append(
                f"    {h.occurred_on}  {h.from_state} -> {h.to_state}  by {h.actor}"
                + (f"  ({h.note})" if h.note else ""))

        lines += [
            "",
            "  DERIVATION",
            f"    {s.value}",
            f"      read from {a.filename}"
            + (f", page {s.page}" if s.page is not None else "")
            + f", {s.locator}",
            f"      method {s.method}"
            + (f" — {s.derivation_note}" if s.derivation_note else ""),
            f"      artifact {a.artifact_id}, sha256 {a.sha256[:16]}...",
            f"      {a.publisher or 'UNKNOWN publisher'}"
            + (f", {a.published_on}" if a.published_on else "")
            + (f", version {a.version}" if a.version else ""),
        ]
        return "\n".join(lines)

    def format_conflict(self, conflict_id: str) -> str:
        c = self.conflicts.get(conflict_id)
        lines = [
            f"CONFLICT {c.conflict_id}  [{c.status}]",
            f"  entity        {c.entity_id}",
            f"  question      {c.question_id}  ({c.statement_type})",
            f"  detected on   {c.detected_on}",
            "",
            "  INCUMBENT (was answerable when the challenge arrived)",
        ]
        for role, sid, val in (
            ("INCUMBENT", c.incumbent_statement_id, c.incumbent_value),
            ("CHALLENGER", c.challenger_statement_id, c.challenger_value),
        ):
            s = self.editor.get(sid)
            a = self.registry.get(s.artifact_id)
            if role == "CHALLENGER":
                lines += ["", "  CHALLENGER"]
            lines += [
                f"    {sid}  = {val!r}   [{s.review_state}]",
                f"      {a.artifact_id} {a.filename}"
                + (f" p.{s.page}" if s.page is not None else ""),
                f"      {s.locator}",
                f"      read by {s.read_by} on {s.read_on}, method {s.method}",
            ]
        if c.status != "OPEN":
            lines += [
                "",
                f"  RESOLUTION    {c.status}",
                f"    winner      {c.resolved_statement_id or 'none — both rejected'}",
                f"    by          {c.resolved_by} on {c.resolved_on}",
                f"    reason      {c.resolution_note}",
            ]
        else:
            lines += ["", "  UNRESOLVED — awaiting curator review.",
                      "  The passenger continues to see the published statement,",
                      "  flagged as contested."]
        return "\n".join(lines)

    def format_trace(self, answer: Answer) -> str:
        """The complete chain behind one passenger answer."""
        if not answer.known:
            return "\n".join([
                "PASSENGER ANSWER",
                f"  {answer.question_id} for {answer.entity_id}",
                "  UNKNOWN",
                "",
                f"  {answer.unknown_guidance or 'No source held for this question.'}",
                "",
                "  No statement satisfies this question. There is nothing to trace.",
            ])

        p = answer.provenance
        s = self.editor.get(p.statement_id)
        contest_lines = []
        if answer.contested:
            contest_lines = [
                "",
                f"  *** CONTESTED — open conflict(s): {', '.join(answer.conflict_ids)}",
                "  This value is still the published one, but a competing "
                "reading exists and has not been resolved.",
            ]
        history = self.reviews.history(p.statement_id)
        intact = self.registry.verify(p.artifact_id)
        cls = authority.DOCUMENT_CLASSES.get(p.document_class)

        lines = [
            "PASSENGER ANSWER",
            f"  {answer.value}",
            f"    ({answer.question_id} for {answer.entity_id})",
            "   |",
            "STATEMENT",
            f"  {p.statement_id}  state {s.review_state}",
            "   |",
            "ARTIFACT",
            f"  {p.artifact_id}  {p.filename}",
            f"  class {p.document_class}"
            + (f"  reliability {cls.reliability}" if cls else ""),
            "   |",
            "SHA-256",
            f"  {self.registry.get(p.artifact_id).sha256}",
            f"  integrity {'INTACT' if intact else 'FAILED — stored bytes differ'}",
            "   |",
            "PAGE",
            f"  {p.page if p.page is not None else 'UNKNOWN'}",
            "   |",
            "LOCATOR",
            f"  {p.locator}",
            f"  read by {p.read_by} on {p.read_on}",
            "   |",
            "REVIEW",
        ]
        for h in history:
            lines.append(f"  {h.occurred_on}  {h.from_state} -> {h.to_state}  by {h.actor}")
        if not history:
            lines.append("  none")
        lines += [
            "   |",
            "PUBLISHER",
            f"  {p.publisher or 'UNKNOWN'}"
            + (f",  published {p.published_on}" if p.published_on else "")
            + (f",  version {p.version}" if p.version else ""),
        ] + contest_lines
        return "\n".join(lines)
