"""
End-to-end evidence pipeline tests.

The artifact used here is a fixture file created by the test itself. It is
deliberately NOT a ship document: the digests are genuinely computed from real
bytes, while no claim about any real vessel is fabricated. When the first
Bellissima source document is acquired it is registered the same way, with no
code change.
"""

import os
import shutil
import tempfile
import unittest

from timonelo.evidence import (
    ArtifactStore, EvidenceEvent, EvidenceEventLog, Method, Derivation,
    Question, QuestionRegistry, Statement, TruthEngine, language,
)
from timonelo.ontology.models import HumanReviewState, PublishStatus

FIXTURE_CLASS = "test_fixture"

# Declared so the fixture class can carry weight. Deliberately mid-range: the
# fixture is not a real document and must not read as authoritative.
from timonelo.evidence.engine import SOURCE_RELIABILITY
SOURCE_RELIABILITY.setdefault(FIXTURE_CLASS, 0.80)


def build_registry() -> QuestionRegistry:
    r = QuestionRegistry(version="test-1")
    r.register(Question(
        question_id="Q-0001", entity_type="cabin",
        labels={"en": "Which deck is the cabin on?"},
        supportable_by=(FIXTURE_CLASS, "cruise_line_deck_plan",
                        "shipyard_general_arrangement"),
        unknown_guidance="Check your booking confirmation.",
    ))
    r.register(Question(
        question_id="Q-0002", entity_type="cabin",
        labels={"en": "What is the stateroom area?"},
        # A marketing deck plan cannot establish an area. Only a dimensioned
        # shipyard drawing can.
        supportable_by=("shipyard_general_arrangement",),
        unknown_guidance="Timonelo holds no dimensioned drawing for this vessel.",
    ))
    r.register(Question(
        question_id="Q-0003", entity_type="cabin",
        labels={"en": "Is morning noise likely?"},
        supportable_by=(FIXTURE_CLASS,),
        unknown_guidance="Deck contents above this stateroom are not yet sourced.",
    ))
    return r


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.doc = os.path.join(self.tmp, "fixture_document.txt")
        with open(self.doc, "w", encoding="utf-8") as f:
            f.write("Timonelo pipeline fixture. Not a ship document.\n")
        self.store = ArtifactStore(os.path.join(self.tmp, "artifacts"))
        self.registry = build_registry()
        self.log = EvidenceEventLog(
            os.path.join(self.tmp, "events.json"), self.store, self.registry
        )
        self.engine = TruthEngine(self.registry, self.log, self.store,
                                  rules={"rule:noise:v1": 0.7})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def register_artifact(self):
        return self.store.add(
            self.doc, document_class=FIXTURE_CLASS,
            obtained_on="2026-08-17", obtained_from="test fixture",
        )


class TestArtifactStore(PipelineTestCase):

    def test_digest_is_computed_from_real_bytes(self):
        import hashlib
        artifact = self.register_artifact()
        with open(self.doc, "rb") as f:
            expected = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(artifact.sha256, expected)

    def test_cannot_register_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.store.add(os.path.join(self.tmp, "nope.pdf"), FIXTURE_CLASS,
                           "2026-08-17", "nowhere")

    def test_store_starts_empty(self):
        self.assertEqual(len(self.store), 0)

    def test_verify_detects_substitution(self):
        artifact = self.register_artifact()
        blob = os.path.join(self.store.blobs, artifact.sha256)
        with open(blob, "w", encoding="utf-8") as f:
            f.write("substituted")
        self.assertFalse(self.store.verify(artifact.sha256))
        self.assertEqual(self.store.verify_all(), [artifact.sha256])


class TestEventLog(PipelineTestCase):

    def test_event_cannot_cite_unheld_artifact(self):
        with self.assertRaises(ValueError) as ctx:
            self.log.append(EvidenceEvent(
                event_id="E1", artifact_sha256="a" * 64, locator="p1",
                entity_id="cabin:X:1", question_id="Q-0001",
                observed_value=14, observed_by="tester", observed_on="2026-08-17",
            ))
        self.assertIn("not in the store", str(ctx.exception))

    def test_event_requires_locator(self):
        a = self.register_artifact()
        with self.assertRaises(ValueError):
            self.log.append(EvidenceEvent(
                event_id="E1", artifact_sha256=a.sha256, locator="",
                entity_id="cabin:X:1", question_id="Q-0001",
                observed_value=14, observed_by="tester", observed_on="2026-08-17",
            ))

    def test_document_cannot_support_claims_beyond_its_class(self):
        """The principle carried forward from the audit."""
        a = self.register_artifact()
        with self.assertRaises(ValueError) as ctx:
            self.log.append(EvidenceEvent(
                event_id="E1", artifact_sha256=a.sha256, locator="p1",
                entity_id="cabin:X:1", question_id="Q-0002",   # area
                observed_value=19.0, observed_by="tester", observed_on="2026-08-17",
            ))
        self.assertIn("cannot support", str(ctx.exception))

    def test_as_of_folds_the_log(self):
        a = self.register_artifact()
        self.log.append(EvidenceEvent(
            event_id="E1", artifact_sha256=a.sha256, locator="p1",
            entity_id="cabin:X:1", question_id="Q-0001",
            observed_value=14, observed_by="t", observed_on="2026-01-01",
        ))
        self.log.append(EvidenceEvent(
            event_id="E2", artifact_sha256=a.sha256, locator="p2",
            entity_id="cabin:X:1", question_id="Q-0001",
            observed_value=15, observed_by="t", observed_on="2026-06-01",
        ))
        self.assertEqual(len(self.log.all(as_of="2026-03-01")), 1)
        self.assertEqual(len(self.log.all()), 2)


class TestTruthEngine(PipelineTestCase):

    def seed_direct(self):
        a = self.register_artifact()
        self.log.append(EvidenceEvent(
            event_id="E1", artifact_sha256=a.sha256, locator="page 1",
            entity_id="cabin:X:1", question_id="Q-0001",
            observed_value=14, observed_by="tester", observed_on="2026-08-17",
        ))
        return self.engine.add_statement(Statement(
            statement_id="S1", entity_id="cabin:X:1", question_id="Q-0001",
            value=14, method=Method.DIRECT, derivation=Derivation.LOCAL,
            evidence_event_ids=("E1",),
        ))

    def test_unpublished_statement_is_unknown(self):
        self.seed_direct()
        ans = self.engine.answer("cabin:X:1", "Q-0001")
        self.assertFalse(ans.known)

    def test_cannot_publish_without_review(self):
        self.seed_direct()
        with self.assertRaises(ValueError):
            self.engine.publish("S1")

    def test_published_statement_is_answerable(self):
        self.seed_direct()
        self.engine.set_human_review_state("S1", HumanReviewState.APPROVED)
        self.engine.publish("S1")
        ans = self.engine.answer("cabin:X:1", "Q-0001")
        self.assertTrue(ans.known)
        self.assertEqual(ans.value, 14)

    def test_direct_statement_requires_evidence(self):
        with self.assertRaises(ValueError):
            self.engine.add_statement(Statement(
                statement_id="S9", entity_id="cabin:X:1", question_id="Q-0001",
                value=14, method=Method.DIRECT, derivation=Derivation.LOCAL,
            ))

    def test_inferred_statement_requires_rule_hash(self):
        self.seed_direct()
        with self.assertRaises(ValueError):
            self.engine.add_statement(Statement(
                statement_id="S2", entity_id="cabin:X:1", question_id="Q-0003",
                value=True, method=Method.INFERRED, derivation=Derivation.LOCAL,
                input_statement_ids=("S1",),
            ))

    def test_confidence_never_exceeds_premises(self):
        self.seed_direct()
        self.engine.add_statement(Statement(
            statement_id="S2", entity_id="cabin:X:1", question_id="Q-0003",
            value=True, method=Method.INFERRED, derivation=Derivation.LOCAL,
            input_statement_ids=("S1",), rule_hash="rule:noise:v1",
        ))
        base = self.engine.confidence("S1")
        derived = self.engine.confidence("S2")
        self.assertLess(derived, base)

    def test_confidence_is_not_stored_on_the_statement(self):
        self.seed_direct()
        self.assertFalse(hasattr(self.engine._statements["S1"], "confidence"))

    def test_unknown_question_reports_guidance(self):
        ans = self.engine.answer("cabin:X:1", "Q-0002")
        self.assertFalse(ans.known)
        self.assertIn("dimensioned", ans.unknown_guidance)

    def test_coverage_is_zero_on_empty_engine(self):
        cov = self.engine.coverage("cabin:X:1", "cabin")
        self.assertEqual(cov["questions_answerable"], 0)
        self.assertEqual(cov["coverage"], 0.0)
        self.assertEqual(len(cov["unknown_question_ids"]), 3)

    def test_unregistered_document_class_raises(self):
        """An undeclared class must not silently score zero."""
        from timonelo.evidence.engine import SOURCE_RELIABILITY
        saved = SOURCE_RELIABILITY.pop(FIXTURE_CLASS)
        try:
            self.seed_direct()
            with self.assertRaises(ValueError):
                self.engine.confidence("S1")
        finally:
            SOURCE_RELIABILITY[FIXTURE_CLASS] = saved

    def test_derivation_chain_names_the_real_source(self):
        self.seed_direct()
        node = self.engine.derivation_of("S1")
        self.assertEqual(node.sources, ("fixture_document.txt@page 1",))


class TestLanguageLayer(PipelineTestCase):

    def test_unknown_renders_explicitly(self):
        ans = self.engine.answer("cabin:X:1", "Q-0002")
        out = language.render(ans, "Stateroom area")
        self.assertIn("UNKNOWN", out)

    def test_confidence_is_never_rendered_as_a_number(self):
        a = self.register_artifact()
        self.log.append(EvidenceEvent(
            event_id="E1", artifact_sha256=a.sha256, locator="page 1",
            entity_id="cabin:X:1", question_id="Q-0001",
            observed_value=14, observed_by="t", observed_on="2026-08-17",
        ))
        self.engine.add_statement(Statement(
            statement_id="S1", entity_id="cabin:X:1", question_id="Q-0001",
            value=14, method=Method.DIRECT, derivation=Derivation.LOCAL,
            evidence_event_ids=("E1",),
        ))
        self.engine.set_human_review_state("S1", HumanReviewState.APPROVED)
        self.engine.publish("S1")
        ans = self.engine.answer("cabin:X:1", "Q-0001")
        out = language.render(ans, "Deck")
        self.assertNotIn(str(ans.confidence), out)
        self.assertNotIn("%", out)

    def test_low_confidence_claim_is_hedged(self):
        a = self.register_artifact()
        self.log.append(EvidenceEvent(
            event_id="E1", artifact_sha256=a.sha256, locator="page 1",
            entity_id="cabin:X:1", question_id="Q-0003",
            observed_value=True, observed_by="t", observed_on="2026-08-17",
        ))
        self.engine.add_statement(Statement(
            statement_id="S1", entity_id="cabin:X:1", question_id="Q-0003",
            value="buffet overhead", method=Method.DIRECT,
            derivation=Derivation.LOCAL, evidence_event_ids=("E1",),
        ))
        self.engine.add_statement(Statement(
            statement_id="S2", entity_id="cabin:X:1", question_id="Q-0003",
            value="morning noise likely", method=Method.INFERRED,
            derivation=Derivation.LOCAL, input_statement_ids=("S1",),
            rule_hash="rule:noise:v1",
        ))
        for sid in ("S2",):
            self.engine.set_human_review_state(sid, HumanReviewState.APPROVED)
            self.engine.publish(sid)
        ans = self.engine.answer("cabin:X:1", "Q-0003")
        out = language.render(ans, "Morning noise")
        self.assertIn("—", out)  # hedged, not a bare declarative


if __name__ == "__main__":
    unittest.main()


class TestStatementAuthority(unittest.TestCase):
    """The Statement Authority Matrix as a runtime layer."""

    def test_deck_plan_cannot_establish_area(self):
        from timonelo.evidence import authority
        with self.assertRaises(authority.AuthorityError):
            authority.check("cabin.area_sqm", "cruise_line_deck_plan")

    def test_deck_plan_can_establish_deck(self):
        from timonelo.evidence import authority
        authority.check("cabin.deck", "cruise_line_deck_plan")  # must not raise

    def test_undeclared_statement_type_is_not_permitted(self):
        """Absence is not permission."""
        from timonelo.evidence import authority
        with self.assertRaises(authority.AuthorityError):
            authority.authoritative_classes("cabin.feng_shui_rating")

    def test_undeclared_document_class_raises(self):
        from timonelo.evidence import authority
        with self.assertRaises(authority.AuthorityError):
            authority.reliability_of("passenger_blog")

    def test_authority_and_permission_are_independent(self):
        """A GA drawing is the top authority for area AND not publishable."""
        from timonelo.evidence import authority
        authority.check("cabin.area_sqm", "shipyard_general_arrangement")
        ok, reason = authority.is_publishable(
            "cabin.area_sqm", "shipyard_general_arrangement"
        )
        self.assertFalse(ok)
        self.assertIn("legal review", reason.lower())

    def test_safety_statements_are_never_publishable(self):
        from timonelo.evidence import authority
        authority.check("cabin.muster_station", "solas_placard")
        ok, _ = authority.is_publishable("cabin.muster_station", "solas_placard")
        self.assertFalse(ok)

    def test_reliability_never_reaches_certainty(self):
        from timonelo.evidence import authority
        for cls in authority.DOCUMENT_CLASSES.values():
            self.assertLess(cls.reliability, 1.0, cls.class_id)

    def test_day_scoped_class_declared_for_operations(self):
        """Opening hours must not be sourced from a class that never expires."""
        from timonelo.evidence import authority
        for cid in authority.authoritative_classes("venue.opening_hours"):
            self.assertEqual(
                authority.scope_of(cid), authority.ValidityScope.DAY_SCOPED
            )
