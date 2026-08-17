"""
Sprint 0010 — Truth Conflict Engine.

detect -> record -> mark both -> require review -> publish resolution.
Nothing is overwritten and nothing disappears.
"""

import os
import shutil
import tempfile
import unittest

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.conflicts import ConflictError, ConflictStatus, values_disagree
from timonelo.evidence.review import ReviewError, ReviewState
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.workspace import Workspace
from tests.test_ground_truth_pipeline import _write_pdf

CLASS = "conflict_fixture"


class ConflictCase(unittest.TestCase):

    def setUp(self):
        # authority.AUTHORITY and DOCUMENT_CLASSES are module-global and are
        # mutated by workspace loading. Without snapshot/restore, fixtures from
        # one test file silently overwrite another's entries.
        self._AUTH_SNAPSHOT = dict(authority.AUTHORITY)
        self._CLASS_SNAPSHOT = dict(authority.DOCUMENT_CLASSES)
        self.root = tempfile.mkdtemp()
        for d in ("artifacts/blobs", "statements", "reviews", "registry", "documents"):
            os.makedirs(os.path.join(self.root, d), exist_ok=True)
        self.pdf_a = _write_pdf(os.path.join(self.root, "documents", "a.pdf"), "SOURCE A")
        self.pdf_b = _write_pdf(os.path.join(self.root, "documents", "b.pdf"), "SOURCE B")
        canonical_dump({
            "document_classes": {CLASS: {
                "label": "Conflict fixture", "reliability": 0.80,
                "validity_scope": "STRUCTURAL", "acquisition": "PUBLIC",
                "use_permission": "CITE_AND_STORE"}},
            "authority": {"fixture.deck": [CLASS]},
        }, os.path.join(self.root, "registry", "document_classes.json"))
        authority.DOCUMENT_CLASSES.pop(CLASS, None)
        r = QuestionRegistry("test")
        r.register(Question("Q-0001", "cabin", statement_type="fixture.deck",
                            labels={"en": "Which deck?"},
                            unknown_guidance="Not sourced."))
        r.save(os.path.join(self.root, "registry", "questions.json"))
        self.ws = Workspace(self.root)
        self.a = self.ws.import_artifact(
            self.pdf_a, document_class=CLASS, acquired_on="2026-08-17",
            acquisition_method="test")
        self.b = self.ws.import_artifact(
            self.pdf_b, document_class=CLASS, acquired_on="2026-08-17",
            acquisition_method="test")

    def tearDown(self):
        authority.AUTHORITY.clear(); authority.AUTHORITY.update(self._AUTH_SNAPSHOT)
        authority.DOCUMENT_CLASSES.clear()
        authority.DOCUMENT_CLASSES.update(self._CLASS_SNAPSHOT)
        shutil.rmtree(self.root, ignore_errors=True)
        authority.DOCUMENT_CLASSES.pop(CLASS, None)

    def _stmt(self, value, artifact, reader="reader.one", on="2026-08-17"):
        return self.ws.create_statement(
            entity_id="cabin:1", question_id="Q-0001",
            statement_type="fixture.deck", value=value,
            artifact_id=artifact.artifact_id, page=1, locator="p1",
            read_by=reader, read_on=on)

    def _publish(self, s, actor="reviewer.two"):
        self.ws.transition(s.statement_id, ReviewState.UNDER_REVIEW, s.read_by, "2026-08-17")
        self.ws.transition(s.statement_id, ReviewState.APPROVED, actor, "2026-08-17")
        return self.ws.transition(s.statement_id, ReviewState.PUBLISHED, actor, "2026-08-17")


class TestDetection(ConflictCase):

    def test_no_conflict_against_a_draft(self):
        """A disagreement with an unpublished draft is not yet a contradiction."""
        self._stmt(14, self.a)
        self._stmt(15, self.b)
        self.assertEqual(len(self.ws.conflicts), 0)

    def test_conflict_detected_against_published(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        self.assertEqual(len(self.ws.conflicts), 1)
        c = self.ws.conflicts.all()[0]
        self.assertEqual(c.incumbent_value, 14)
        self.assertEqual(c.challenger_value, 15)
        self.assertTrue(c.is_open)

    def test_agreement_is_not_a_conflict(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(14, self.b, reader="reader.two")
        self.assertEqual(len(self.ws.conflicts), 0)

    def test_detection_is_blunt_by_design(self):
        """"14" and 14 are a conflict. A curator decides whether they agree."""
        self.assertTrue(values_disagree("14", 14))
        self.assertTrue(values_disagree("none", "none marked"))
        self.assertFalse(values_disagree(14, 14))

    def test_nothing_is_overwritten_on_detection(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        self.assertEqual(self.ws.editor.get(s1.statement_id).value, 14)
        self.assertEqual(self.ws.editor.get(s2.statement_id).value, 15)
        self.assertEqual(self.ws.editor.get(s1.statement_id).state, ReviewState.PUBLISHED)


class TestPassengerView(ConflictCase):

    def test_passenger_still_sees_published_value(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        ans = self.ws.engine.answer("cabin:1", "Q-0001")
        self.assertTrue(ans.known)
        self.assertEqual(ans.value, 14)

    def test_answer_is_flagged_contested(self):
        """Serving a contested value as uncontested would strengthen it."""
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        ans = self.ws.engine.answer("cabin:1", "Q-0001")
        self.assertTrue(ans.contested)
        self.assertEqual(len(ans.conflict_ids), 1)

    def test_trace_discloses_the_contest(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        trace = self.ws.format_trace(self.ws.engine.answer("cabin:1", "Q-0001"))
        self.assertIn("CONTESTED", trace)

    def test_uncontested_answer_is_not_flagged(self):
        self._publish(self._stmt(14, self.a))
        self.assertFalse(self.ws.engine.answer("cabin:1", "Q-0001").contested)


class TestResolution(ConflictCase):

    def setUp(self):
        super().setUp()
        self.s1 = self._publish(self._stmt(14, self.a))
        self.s2 = self._stmt(15, self.b, reader="reader.two")
        self.conflict = self.ws.conflicts.all()[0]

    def test_resolution_requires_a_reason(self):
        with self.assertRaises(ConflictError):
            self.ws.editor.resolve_conflict(
                self.conflict.conflict_id, self.s2.statement_id,
                "reviewer.two", "2026-08-18", "")

    def test_winner_must_be_party_to_the_conflict(self):
        other = self._stmt(99, self.a, reader="reader.three")
        with self.assertRaises(ConflictError):
            self.ws.editor.resolve_conflict(
                self.conflict.conflict_id, other.statement_id,
                "reviewer.two", "2026-08-18", "because")

    def test_challenger_wins_and_incumbent_is_superseded(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s2.statement_id,
            "reviewer.two", "2026-08-18", "source B is the later edition")
        self.assertEqual(self.ws.editor.get(self.s2.statement_id).state,
                         ReviewState.PUBLISHED)
        self.assertEqual(self.ws.editor.get(self.s1.statement_id).state,
                         ReviewState.SUPERSEDED)
        self.assertEqual(self.ws.engine.answer("cabin:1", "Q-0001").value, 15)

    def test_loser_always_reaches_a_terminal_state(self):
        """A losing DRAFT left alive could be published later and recreate
        the same conflict."""
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s1.statement_id,
            "reviewer.two", "2026-08-18", "incumbent reading confirmed")
        self.assertEqual(self.ws.editor.get(self.s2.statement_id).state,
                         ReviewState.SUPERSEDED)

    def test_superseded_is_terminal(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s1.statement_id,
            "reviewer.two", "2026-08-18", "confirmed")
        with self.assertRaises(ReviewError):
            self.ws.transition(self.s2.statement_id, ReviewState.PUBLISHED,
                               "reviewer.two", "2026-08-19")

    def test_both_rejected_returns_the_question_to_unknown(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, None,
            "reviewer.two", "2026-08-18", "neither reading is legible")
        self.assertFalse(self.ws.engine.answer("cabin:1", "Q-0001").known)

    def test_resolution_clears_the_contested_flag(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s1.statement_id,
            "reviewer.two", "2026-08-18", "confirmed")
        self.assertFalse(self.ws.engine.answer("cabin:1", "Q-0001").contested)

    def test_resolved_conflict_cannot_be_reopened(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s1.statement_id,
            "reviewer.two", "2026-08-18", "confirmed")
        with self.assertRaises(ConflictError):
            self.ws.editor.resolve_conflict(
                self.conflict.conflict_id, self.s2.statement_id,
                "reviewer.two", "2026-08-19", "changed my mind")


class TestHistoryIsPreserved(ConflictCase):

    def test_no_statement_disappears(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s2.statement_id,
                                        "reviewer.two", "2026-08-18", "later edition")
        ids = {s.statement_id for s in self.ws.editor.all()}
        self.assertIn(s1.statement_id, ids)
        self.assertIn(s2.statement_id, ids)

    def test_superseded_value_is_still_readable(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s2.statement_id,
                                        "reviewer.two", "2026-08-18", "later edition")
        self.assertEqual(self.ws.editor.get(s1.statement_id).value, 14)

    def test_conflict_history_records_detection_and_resolution(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s1.statement_id,
                                        "reviewer.two", "2026-08-18", "confirmed")
        events = [h["event"] for h in self.ws.conflicts.history(c.conflict_id)]
        self.assertEqual(events, ["DETECTED", "RESOLVED"])

    def test_review_log_records_the_supersession(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s1.statement_id,
                                        "reviewer.two", "2026-08-18", "confirmed")
        hist = self.ws.reviews.history(s2.statement_id)
        self.assertEqual(hist[-1].to_state, "SUPERSEDED")
        self.assertIn("CFL-", hist[-1].note)

    def test_resolution_reason_is_retained(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        reason = "source B is the November 2025 edition; source A is 2023"
        self.ws.editor.resolve_conflict(c.conflict_id, c.challenger_statement_id,
                                        "reviewer.two", "2026-08-18", reason)
        self.assertEqual(self.ws.conflicts.get(c.conflict_id).resolution_note, reason)


if __name__ == "__main__":
    unittest.main()
