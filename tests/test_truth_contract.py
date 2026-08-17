"""
Truth contract regression tests.

These guard the invariants of ADR-0002 and ADR-0003. Each test corresponds to a
defect found by audit and fixed; each would have passed silently before the fix,
which is why they exist.

They are deliberately adversarial toward our own engine. If one of these starts
failing, the engine has begun manufacturing certainty again.
"""

import glob
import json
import os
import re
import unittest

from timonelo.canonical import canonical_dumps, is_canonical
from timonelo.ontology.bellissima import create_bellissima_ontology
from timonelo.ontology.models import EvidenceLink
from timonelo.intelligence.briefing import CruiseBriefingSynthesizer
from timonelo.intelligence.embarkation import EmbarkationIntelligenceEvaluator
from timonelo.calculus.sandwich import DeterministicSandwichResolver

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src")


class TestNoFabricatedProvenance(unittest.TestCase):
    """ADR-0002 §1 — evidence records events; it may not be invented."""

    def test_evidence_link_rejects_non_digest(self):
        with self.assertRaises(ValueError):
            EvidenceLink(source_id="X", locator="L", sha256="not-a-digest")

    def test_evidence_link_rejects_zero_placeholder(self):
        with self.assertRaises(ValueError):
            EvidenceLink(source_id="X", locator="L", sha256="0" * 64)

    def test_evidence_link_defaults_to_no_digest(self):
        """Absence of an artifact must be the default, not a filled-in value."""
        link = EvidenceLink(source_id="X", locator="L")
        self.assertIsNone(link.sha256)
        self.assertFalse(link.is_content_addressed)

    def test_no_hardcoded_digests_in_source(self):
        """No 64-hex literal may be assigned to sha256 anywhere in the tree.

        Every digest in the knowledge base was a hand-typed hex pattern; two
        values accounted for 15,048 of 15,090 evidence links. A digest may only
        be computed from bytes actually held.
        """
        pattern = re.compile(r'sha256\s*=\s*[\'"][0-9a-fA-F]{64}[\'"]')
        offenders = []
        for path in glob.glob(os.path.join(SRC, "**", "*.py"), recursive=True):
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        offenders.append(f"{os.path.relpath(path, REPO)}:{i}")
        self.assertEqual(offenders, [], f"Hardcoded digests found: {offenders}")

    def test_bellissima_links_declare_no_artifact(self):
        """Until a real document is acquired, no link may claim to be hashed."""
        ontology = create_bellissima_ontology()
        for deck in ontology.decks.values():
            for cabin in deck.cabins.values():
                for link in cabin.evidence_links or []:
                    self.assertIsNone(
                        link.sha256,
                        f"{link.source_id} claims a digest but no artifact is held",
                    )


class TestUnknownIsNeverSilentlyFilled(unittest.TestCase):
    """ADR-0002 §8 — missing data must never render as reassurance."""

    def setUp(self):
        self.ontology = create_bellissima_ontology()

    def test_unmodelled_deck_is_unknown_not_residential(self):
        """A deck with no venue coverage cannot be reported as quiet.

        Deck 13 has zero venues modelled. Before the fix, this returned
        is_residential_cabins_only=True — absence of data read as absence of
        noise.
        """
        resolver = DeterministicSandwichResolver(self.ontology)
        report = resolver.resolve_cabin_sandwich("14122")
        underfoot = report.underfoot_layer
        self.assertEqual(len(self.ontology.decks[13].venues), 0)
        self.assertIsNone(
            underfoot.is_residential_cabins_only,
            "Unmodelled deck must be UNKNOWN, never 'pure residential'",
        )

    def test_insulation_requires_positive_knowledge_both_sides(self):
        """UNKNOWN on either side must not satisfy an acoustic-comfort claim."""
        resolver = DeterministicSandwichResolver(self.ontology)
        report = resolver.resolve_cabin_sandwich("14122")
        self.assertFalse(report.is_acoustically_insulated_sandwich)

    def test_embarkation_absent_without_sourced_data(self):
        """SOLAS muster data may never be derived from generated geometry."""
        cabin = self.ontology.decks[14].cabins["14122"]
        self.assertIsNone(
            EmbarkationIntelligenceEvaluator.evaluate(self.ontology, cabin)
        )

    def test_embarkation_refuses_partial_data(self):
        cabin = self.ontology.decks[14].cabins["14122"]
        with self.assertRaises(ValueError):
            EmbarkationIntelligenceEvaluator.evaluate(
                self.ontology, cabin, terminal_override={"terminal_name": "X"}
            )


class TestLanguageLayerCannotStrengthenClaims(unittest.TestCase):
    """ADR-0002 §9 — the renderer may not compose claims independently.

    The defect this guards: briefing.py appended the literal string
    "(Pure residential buffer)" unconditionally, without consulting the
    sandwich resolver. Cabin 14122 sits directly beneath the Marketplace
    Buffet — the resolver had that fact, and the renderer overwrote it with
    reassurance.
    """

    def setUp(self):
        self.ontology = create_bellissima_ontology()
        self.briefing = CruiseBriefingSynthesizer.generate_briefing(
            self.ontology, "14122"
        )

    def test_noise_source_overhead_is_surfaced_not_suppressed(self):
        summary = self.briefing.cabin_intelligence.vertical_sandwich_status
        resolver = DeterministicSandwichResolver(self.ontology)
        overhead = resolver.resolve_cabin_sandwich("14122").overhead_layer
        self.assertTrue(
            overhead.intersecting_venues,
            "fixture invalid: expected a venue above 14122",
        )
        for venue in overhead.intersecting_venues:
            self.assertIn(
                venue,
                summary,
                f"Renderer suppressed a venue the engine resolved: {venue}",
            )

    def test_no_unconditional_reassurance_string(self):
        summary = self.briefing.cabin_intelligence.vertical_sandwich_status
        for banned in ("Pure residential buffer", "Residential Deck"):
            self.assertNotIn(banned, summary)

    def test_unknown_is_rendered_explicitly(self):
        """A gap must read as UNKNOWN, never as silence (ADR-0002 §9)."""
        summary = self.briefing.cabin_intelligence.vertical_sandwich_status
        self.assertIn("UNKNOWN", summary)

    def test_muster_gap_directs_passenger_to_real_source(self):
        decisions = self.briefing.decision_summary.core_decisions
        muster = [d for d in decisions if "Safety" in d.title]
        self.assertTrue(muster)
        text = muster[0].recommendation
        self.assertIn("UNKNOWN", text)
        self.assertIn("cabin card", text)


class TestNoAuthoredConfidence(unittest.TestCase):
    """ADR-0002 I1 — confidence is computed, never stored."""

    def test_evidence_field_is_deleted(self):
        """The dormant trust type must not come back (ADR-0002 §11.2)."""
        import timonelo.database.evidence as ev
        self.assertFalse(
            hasattr(ev, "EvidenceField"),
            "EvidenceField was deleted; its concepts live on EvidenceLink",
        )

    def test_audit_returns_no_confidence_score(self):
        from timonelo.database.evidence import EvidenceEngine
        metrics, _ = EvidenceEngine.audit_ship(
            {"slug": "t", "dimensions": {"loa": 315.0}, "cabins": []}
        )
        self.assertNotIn("confidence_score", metrics)
        self.assertIn("provenance_coverage", metrics)

    def test_cabins_are_not_counted_as_audited(self):
        """Counting cabin facts by assumption is what audit_ship used to do."""
        from timonelo.database.evidence import EvidenceEngine
        metrics, _ = EvidenceEngine.audit_ship(
            {"slug": "t", "dimensions": {}, "cabins": [{}] * 2217}
        )
        self.assertEqual(metrics["cabins_present"], 2217)
        self.assertEqual(metrics["cabins_audited"], 0)


class TestCanonicalSerialization(unittest.TestCase):
    """ADR-0003 §5.1 — artifacts must be byte-reproducible."""

    def test_canonical_dumps_is_order_independent(self):
        a = {"b": 1, "a": {"z": 2, "y": 3}}
        b = {"a": {"y": 3, "z": 2}, "b": 1}
        self.assertEqual(canonical_dumps(a), canonical_dumps(b))

    def test_committed_data_files_are_canonical(self):
        """Non-canonical data makes knowledge diffs unreviewable."""
        offenders = []
        for path in glob.glob(os.path.join(REPO, "data", "*.json")):
            if not is_canonical(path):
                offenders.append(os.path.relpath(path, REPO))
        self.assertEqual(offenders, [], f"Non-canonical files: {offenders}")

    def test_no_unsorted_json_dump_in_source(self):
        offenders = []
        for path in glob.glob(os.path.join(SRC, "**", "*.py"), recursive=True):
            rel = os.path.relpath(path, REPO)
            if rel.endswith("canonical.py"):
                continue
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if "json.dump(" in line and "sort_keys" not in line:
                        offenders.append(f"{rel}:{i}")
        self.assertEqual(offenders, [], f"Unsorted json.dump: {offenders}")


if __name__ == "__main__":
    unittest.main()
