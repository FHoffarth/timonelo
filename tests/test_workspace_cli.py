"""
Sprint 0008 — Evidence Workspace.

Proves a curator can carry a real document through the whole manual workflow
using only the CLI, and that every answer traces back to the file on disk.
"""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.cli import main
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.workspace import Workspace
from timonelo.evidence.models import PublishStatus

from tests.evidence_fixtures import back_with_evidence
from tests.test_ground_truth_pipeline import _write_pdf

CLASS = "workspace_fixture"


class WorkspaceCase(unittest.TestCase):

    def setUp(self):
        # authority.AUTHORITY and DOCUMENT_CLASSES are module-global and are
        # mutated by workspace loading. Without snapshot/restore, fixtures from
        # one test file silently overwrite another's entries.
        self._AUTH_SNAPSHOT = dict(authority.AUTHORITY)
        self._CLASS_SNAPSHOT = dict(authority.DOCUMENT_CLASSES)
        self.root = tempfile.mkdtemp()
        for d in ("artifacts/blobs", "statements", "reviews", "registry", "documents"):
            os.makedirs(os.path.join(self.root, d), exist_ok=True)
        self.pdf = _write_pdf(os.path.join(self.root, "documents", "fix.pdf"))

        canonical_dump({
            "document_classes": {CLASS: {
                "label": "Workspace fixture", "reliability": 0.80,
                "validity_scope": "STRUCTURAL", "acquisition": "PUBLIC",
                "use_permission": "CITE_AND_STORE"}},
            "authority": {"fixture.deck": [CLASS],
                          "fixture.area": ["shipyard_general_arrangement"]},
        }, os.path.join(self.root, "registry", "document_classes.json"))

        authority.DOCUMENT_CLASSES.pop(CLASS, None)
        r = QuestionRegistry("test")
        r.register(Question("Q-0001", "fixture", statement_type="fixture.deck",
                            labels={"en": "Which deck?"},
                            unknown_guidance="Check your booking."))
        r.register(Question("Q-0002", "fixture", statement_type="fixture.area",
                            labels={"en": "Floor area?"},
                            unknown_guidance="No dimensioned drawing held."))
        r.save(os.path.join(self.root, "registry", "questions.json"))

    def tearDown(self):
        authority.AUTHORITY.clear(); authority.AUTHORITY.update(self._AUTH_SNAPSHOT)
        authority.DOCUMENT_CLASSES.clear()
        authority.DOCUMENT_CLASSES.update(self._CLASS_SNAPSHOT)
        shutil.rmtree(self.root, ignore_errors=True)
        authority.DOCUMENT_CLASSES.pop(CLASS, None)

    def run_cli(self, *args) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", self.root, *args])
        self.assertEqual(code, 0, buf.getvalue())
        return buf.getvalue()

    def cli_fails(self, *args) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["--root", self.root, *args]), 1)

    def _import(self):
        return self.run_cli(
            "artifact-create", self.pdf, "--document-class", CLASS,
            "--acquired-on", "2026-08-17", "--acquisition-method", "test",
            "--publisher", "Timonelo", "--published-on", "2026-08-17",
            "--version", "1", "--language", "en")

    def _statement(self, locator="Page 1, cabin table, top right"):
        return self.run_cli(
            "statement-create", "--entity", "fixture:1", "--question", "Q-0001",
            "--statement-type", "fixture.deck", "--value", "14",
            "--artifact", "ART-0001", "--page", "1", "--locator", locator,
            "--read-by", "curator.one", "--read-on", "2026-08-17")

    def _publish(self):
        # Publication requires evidence. The CLI has no command to record an
        # observation, so the fixture records a real one directly against the
        # artifact the statement already cites.
        ws = Workspace(self.root)
        statement = ws.editor.get("STM-0001")
        back_with_evidence(
            ws, statement,
            # The literal the fixture document carries, not a copy of the
            # claim under test.
            observed_value=14,
            locator="fixture document, page 1",
        )
        self.run_cli("verify-evidence", "STM-0001", "--condition", "SUPPORTED", "--actor", "reviewer.two", "--on", "2026-08-17")
        self.run_cli("submit", "STM-0001", "--actor", "curator.one", "--on", "2026-08-17")
        self.run_cli("approve", "STM-0001", "--actor", "reviewer.two", "--on", "2026-08-18")
        self.run_cli("publish", "STM-0001", "--actor", "reviewer.two", "--on", "2026-08-18")


class TestEmptyWorkspace(WorkspaceCase):

    def test_lists_are_empty(self):
        self.assertIn("empty", self.run_cli("artifact-list").lower())
        self.assertIn("No statements", self.run_cli("statement-list"))

    def test_answer_is_unknown(self):
        self.assertIn("UNKNOWN", self.run_cli(
            "answer", "--entity", "fixture:1", "--question", "Q-0001"))


class TestWorkspaceClasses(WorkspaceCase):

    def test_workspace_class_is_loaded(self):
        Workspace(self.root)
        self.assertIn(CLASS, authority.DOCUMENT_CLASSES)

    def test_workspace_may_not_redefine_curated_class(self):
        canonical_dump({"document_classes": {"cruise_line_deck_plan": {
            "label": "hijacked", "reliability": 0.99,
            "validity_scope": "STRUCTURAL", "acquisition": "PUBLIC",
            "use_permission": "CITE_AND_STORE"}}, "authority": {}},
            os.path.join(self.root, "registry", "document_classes.json"))
        with self.assertRaises(authority.AuthorityError):
            Workspace(self.root)


class TestCuratorWorkflow(WorkspaceCase):

    def test_import_reports_real_digest(self):
        import hashlib
        out = self._import()
        with open(self.pdf, "rb") as f:
            self.assertIn(hashlib.sha256(f.read()).hexdigest(), out)

    def test_statement_starts_unanswerable(self):
        self._import()
        self._statement()
        self.assertIn("UNKNOWN", self.run_cli(
            "answer", "--entity", "fixture:1", "--question", "Q-0001"))

    def test_full_workflow_yields_an_answer(self):
        self._import()
        self._statement()
        self._publish()
        out = self.run_cli("answer", "--entity", "fixture:1", "--question", "Q-0001")
        self.assertIn("14", out)
        self.assertIn("fix.pdf", out)

    def test_cannot_publish_without_review(self):
        self._import()
        self._statement()
        self.cli_fails("publish", "STM-0001", "--actor", "x", "--on", "2026-08-18")

    def test_authority_blocks_wrong_document_class(self):
        self._import()
        self.cli_fails(
            "statement-create", "--entity", "fixture:1", "--question", "Q-0002",
            "--statement-type", "fixture.area", "--value", "19",
            "--artifact", "ART-0001", "--locator", "p1",
            "--read-by", "c", "--read-on", "2026-08-17")


class TestInspection(WorkspaceCase):

    def test_artifact_inspection_shows_everything_needed(self):
        self._import()
        self._statement()
        out = self.run_cli("artifact-inspect", "ART-0001")
        for expected in ("sha256", "INTACT", "DOCUMENT COVERAGE",
                         "LINKED STATEMENTS", "STM-0001", "Timonelo"):
            self.assertIn(expected, out)

    def test_statement_inspection_shows_review_and_derivation(self):
        self._import()
        self._statement()
        self._publish()
        out = self.run_cli("statement-inspect", "STM-0001")
        for expected in ("REVIEW HISTORY", "DERIVATION", "curator.one",
                         "reviewer.two", "passenger sees  YES"):
            self.assertIn(expected, out)

    def test_draft_statement_is_marked_not_visible(self):
        self._import()
        self._statement()
        self.assertIn("passenger sees  NO",
                      self.run_cli("statement-inspect", "STM-0001"))


class TestManualLocators(WorkspaceCase):

    def test_free_text_locators_survive_verbatim(self):
        self._import()
        for locator in ("Page 12", "Cabin table", "Top right",
                        "Legend symbol B", "Deck 14 plan, grid C4"):
            self.assertIn(locator, self._statement(locator))


class TestDocumentCoverage(WorkspaceCase):

    def test_coverage_excludes_questions_the_class_cannot_answer(self):
        """Q-0002 needs a GA drawing; this class is not responsible for it."""
        self._import()
        out = self.run_cli("artifact-coverage", "ART-0001")
        self.assertIn("Questions supported:  1", out)

    def test_coverage_rises_only_after_approval(self):
        self._import()
        self._statement()
        self.assertIn("Coverage:             0.0%",
                      self.run_cli("artifact-coverage", "ART-0001"))
        self._publish()
        self.assertIn("Coverage:             100.0%",
                      self.run_cli("artifact-coverage", "ART-0001"))


class TestProvenanceTrace(WorkspaceCase):

    def test_trace_contains_the_whole_chain(self):
        self._import()
        self._statement()
        self._publish()
        out = self.run_cli("trace", "--entity", "fixture:1", "--question", "Q-0001")
        for section in ("PASSENGER ANSWER", "STATEMENT", "ARTIFACT", "SHA-256",
                        "PAGE", "LOCATOR", "REVIEW", "PUBLISHER"):
            self.assertIn(section, out)
        self.assertIn("integrity INTACT", out)

    def test_tampering_withdraws_the_published_answer(self):
        """Substituted bytes must stop the claim being served.

        This previously asserted that `trace` printed FAILED while the
        statement stayed published. Publication admission is now re-checked on
        load, so a statement whose artifact no longer matches its digest is
        demoted before any reader sees it: the tampering is caught earlier and
        the claim is withdrawn rather than reported-but-still-served.
        """
        self._import()
        self._statement()
        self._publish()
        ws = Workspace(self.root)
        self.assertEqual(ws.editor.demoted_on_load, [])

        with open(ws.registry.blob_path("ART-0001"), "w") as f:
            f.write("substituted")

        tampered = Workspace(self.root)
        self.assertIn("STM-0001", tampered.editor.demoted_on_load)
        self.assertIs(
            tampered.editor.get("STM-0001").publish_status,
            PublishStatus.PUBLISH_BLOCKED,
        )
        out = self.run_cli("trace", "--entity", "fixture:1", "--question", "Q-0001")
        self.assertIn("UNKNOWN", out)

    def test_unknown_trace_says_there_is_nothing_to_trace(self):
        out = self.run_cli("trace", "--entity", "fixture:1", "--question", "Q-0002")
        self.assertIn("UNKNOWN", out)
        self.assertIn("nothing to trace", out)


if __name__ == "__main__":
    unittest.main()


class TestInspectionAPIs(WorkspaceCase):
    """Structured APIs. Same records as the formatters, different projection."""

    def test_empty_store_reports_honestly(self):
        ws = Workspace(self.root)
        self.assertEqual(ws.artifacts_api.integrity_report()["artifacts"], 0)
        self.assertEqual(ws.statements_api.query(), [])
        self.assertEqual(ws.statements_api.pending_review(), [])

    def test_artifact_inspection_returns_structured_fields(self):
        self._import()
        insp = Workspace(self.root).artifacts_api.inspect("ART-0001")
        self.assertEqual(insp.artifact_id, "ART-0001")
        self.assertTrue(insp.integrity_ok)
        self.assertTrue(insp.document_class_declared)
        self.assertEqual(insp.reliability, 0.80)
        self.assertEqual(insp.publisher, "Timonelo")
        self.assertIn("fixture.deck", insp.supported_statement_types)
        self.assertNotIn("fixture.area", insp.supported_statement_types)

    def test_inspection_is_json_serialisable(self):
        self._import()
        self._statement()
        json.dumps(Workspace(self.root).artifacts_api.inspect("ART-0001").to_dict())

    def test_statement_query_filters(self):
        self._import()
        self._statement()
        api = Workspace(self.root).statements_api
        self.assertEqual(len(api.query(entity_id="fixture:1")), 1)
        self.assertEqual(len(api.query(entity_id="other")), 0)
        self.assertEqual(len(api.query(answerable_only=True)), 0)

    def test_pending_review_is_the_curator_queue(self):
        self._import()
        self._statement()
        api = Workspace(self.root).statements_api
        self.assertEqual(len(api.pending_review()), 1)
        self._publish()
        self.assertEqual(len(Workspace(self.root).statements_api.pending_review()), 0)

    def test_counts_by_state(self):
        self._import()
        self._statement()
        self._publish()
        counts = Workspace(self.root).statements_api.counts_by_state()
        self.assertEqual(counts["APPROVED"], 1)
        self.assertEqual(counts["DRAFT"], 0)

    def test_statement_api_cannot_mutate(self):
        api = Workspace(self.root).statements_api
        for forbidden in ("create", "transition", "approve", "publish", "delete"):
            self.assertFalse(hasattr(api, forbidden), forbidden)

    def test_integrity_report_catches_substitution(self):
        self._import()
        ws = Workspace(self.root)
        with open(ws.registry.blob_path("ART-0001"), "w") as f:
            f.write("substituted")
        report = ws.artifacts_api.integrity_report()
        self.assertFalse(report["all_intact"])
        self.assertEqual(report["failed"], ["ART-0001"])
