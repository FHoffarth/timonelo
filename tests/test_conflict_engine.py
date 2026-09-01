"""Truth conflict detection and lifecycle-independent resolution tests."""

import os
import shutil
import tempfile
import unittest

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.conflicts import (
    ConflictError,
    ConflictStatus,
    validity_overlaps,
    values_disagree,
)
from timonelo.evidence.gatekeeper import EvidenceGatekeeper
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.workspace import Workspace

from tests.evidence_fixtures import back_with_evidence
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus
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

    def _stmt(
        self,
        value,
        artifact,
        reader="reader.one",
        on="2026-08-17",
        valid_from=None,
        valid_until=None,
    ):
        return self.ws.create_statement(
            entity_id="cabin:1", question_id="Q-0001",
            statement_type="fixture.deck", value=value,
            artifact_id=artifact.artifact_id, page=1, locator="p1",
            read_by=reader, read_on=on,
            valid_from=valid_from, valid_until=valid_until)

    def _publish(self, s, actor="reviewer.two"):
        # Publication requires evidence, so the fixture records a real event
        # against the artifact this statement already cites.
        back_with_evidence(
            self.ws, s,
            observed_value=s.value,
            locator="fixture document, deck value",
        )
        self.ws.set_evidence_condition(s.statement_id, EvidenceCondition.SUPPORTED, actor, "2026-08-17")
        self.ws.transition(s.statement_id, HumanReviewState.UNDER_REVIEW, s.read_by, "2026-08-17")
        self.ws.transition(s.statement_id, HumanReviewState.APPROVED, actor, "2026-08-17")
        return self.ws.publish_statement(s.statement_id, actor, "2026-08-17")


class TestDetection(ConflictCase):

    def test_non_overlapping_historical_values_are_not_live_conflict(self):
        self._publish(
            self._stmt(14, self.a, valid_from="2024-01-01", valid_until="2024-12-31")
        )
        self._stmt(
            15,
            self.b,
            reader="reader.two",
            valid_from="2025-01-01",
        )
        self.assertEqual(len(self.ws.conflicts), 0)


    def test_draft_vs_draft_incompatible_overlap_is_live_conflict(self):
        self._stmt(14, self.a)
        self._stmt(15, self.b)
        self.assertEqual(len(self.ws.conflicts), 1)

    def test_under_review_vs_draft_incompatible_overlap_is_live_conflict(self):
        incumbent = self._stmt(14, self.a)
        self.ws.transition(
            incumbent.statement_id,
            HumanReviewState.UNDER_REVIEW,
            incumbent.read_by,
            "2026-08-17",
        )
        self._stmt(15, self.b, reader="reader.two")
        self.assertEqual(len(self.ws.conflicts), 1)

    def test_conflict_detected_against_published(self):
        self._publish(self._stmt(14, self.a))
        self._stmt(15, self.b, reader="reader.two")
        self.assertEqual(len(self.ws.conflicts), 1)
        c = self.ws.conflicts.all()[0]
        self.assertEqual(c.incumbent_value, 14)
        self.assertEqual(c.challenger_value, 15)
        self.assertTrue(c.is_open)

    def test_agreement_is_not_a_conflict(self):
        self._stmt(14, self.a)
        self._stmt(14, self.b, reader="reader.two")
        self.assertEqual(len(self.ws.conflicts), 0)

    def test_inclusive_boundary_touch_is_live_conflict(self):
        self._stmt(14, self.a, valid_until="2025-01-01")
        self._stmt(15, self.b, reader="reader.two", valid_from="2025-01-01")
        self.assertEqual(len(self.ws.conflicts), 1)

    def test_validity_overlap_matrix(self):
        self.assertTrue(validity_overlaps(None, None, None, None))
        self.assertTrue(validity_overlaps("2025-01-01", None, None, "2025-02-01"))
        self.assertFalse(
            validity_overlaps("2024-01-01", "2024-12-31", "2025-01-01", None)
        )
        self.assertTrue(
            validity_overlaps(None, "2025-01-01", "2025-01-01", None)
        )
        self.assertTrue(
            validity_overlaps(
                "2025-01-01", "2025-01-02", "2025-01-02", "2025-01-03"
            )
        )

    def test_gatekeeper_derives_executed_zero_from_actual_detector_run(self):
        self._stmt(14, self.a)
        reloaded = type(self.ws.conflicts)(self.ws.conflicts.path)
        gatekeeper = EvidenceGatekeeper()
        gatekeeper.use_conflict_log(reloaded)
        result = gatekeeper.evaluate_publish_gate().conflict_gate
        self.assertTrue(result.executed)
        self.assertEqual(result.checked_entities, 1)
        self.assertEqual(result.conflicts_found, 0)
        self.assertEqual(result.unresolved_conflicts, 0)

    def test_gatekeeper_derives_open_conflict_from_actual_detector_run(self):
        self._stmt(14, self.a)
        self._stmt(15, self.b, reader="reader.two")
        gatekeeper = EvidenceGatekeeper()
        gatekeeper.use_conflict_log(self.ws.conflicts)
        result = gatekeeper.evaluate_publish_gate().conflict_gate
        self.assertTrue(result.executed)
        self.assertEqual(result.checked_entities, 2)
        self.assertEqual(result.conflicts_found, 1)
        self.assertEqual(result.unresolved_conflicts, 1)

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
        self.assertEqual(self.ws.editor.get(s1.statement_id).state, HumanReviewState.APPROVED)
        self.assertEqual(self.ws.editor.get(s1.statement_id).publishing, PublishStatus.PUBLISH_ALLOWED)


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

    def test_resolution_does_not_mutate_lifecycle_axes(self):
        self.ws.set_evidence_condition(self.s2.statement_id, EvidenceCondition.SUPPORTED,
                                       "reviewer.two", "2026-08-18")
        before_winner = self.ws.editor.get(self.s2.statement_id)
        before_loser = self.ws.editor.get(self.s1.statement_id)
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s2.statement_id,
            "reviewer.two", "2026-08-18", "source B is the later edition")
        self.assertEqual(self.ws.editor.get(self.s2.statement_id), before_winner)
        self.assertEqual(self.ws.editor.get(self.s1.statement_id), before_loser)

    def test_resolution_does_not_mark_winner_supported(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s2.statement_id,
            "reviewer.two", "2026-08-18", "preferred for conflict record")
        self.assertEqual(
            self.ws.editor.get(self.s2.statement_id).condition,
            EvidenceCondition.UNKNOWN,
        )

    def test_resolution_does_not_mark_loser_unsupported(self):
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, self.s1.statement_id,
            "reviewer.two", "2026-08-18", "confirmed")
        self.assertEqual(
            self.ws.editor.get(self.s2.statement_id).condition,
            EvidenceCondition.UNKNOWN,
        )

    def test_reject_both_decision_does_not_reject_statements(self):
        before = [self.ws.editor.get(sid) for sid in self.conflict.statement_ids()]
        self.ws.editor.resolve_conflict(
            self.conflict.conflict_id, None,
            "reviewer.two", "2026-08-18", "neither reading is legible")
        after = [self.ws.editor.get(sid) for sid in self.conflict.statement_ids()]
        self.assertEqual(after, before)

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
        self.ws.set_evidence_condition(s2.statement_id, EvidenceCondition.SUPPORTED,
                                       "reviewer.two", "2026-08-18")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s2.statement_id,
                                        "reviewer.two", "2026-08-18", "later edition")
        ids = {s.statement_id for s in self.ws.editor.all()}
        self.assertIn(s1.statement_id, ids)
        self.assertIn(s2.statement_id, ids)

    def test_superseded_value_is_still_readable(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        self.ws.set_evidence_condition(s2.statement_id, EvidenceCondition.SUPPORTED,
                                       "reviewer.two", "2026-08-18")
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

    def test_resolution_does_not_write_review_history(self):
        s1 = self._publish(self._stmt(14, self.a))
        s2 = self._stmt(15, self.b, reader="reader.two")
        c = self.ws.conflicts.all()[0]
        self.ws.editor.resolve_conflict(c.conflict_id, s1.statement_id,
                                        "reviewer.two", "2026-08-18", "confirmed")
        hist = self.ws.reviews.history(s2.statement_id)
        self.assertEqual(hist, [])

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
