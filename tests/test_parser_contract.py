"""
Sprint 0010 — parser contract and inspection APIs.

Tests the CONTRACT, not extraction. The stub parser here returns no candidates;
its purpose is to prove the interface forbids what it must forbid.
"""

import unittest

from timonelo.evidence.parsers import (
    DocumentParser, ExtractionCandidate, Modality, ParserRegistry, ParserResult,
)


class StubParser(DocumentParser):
    """Minimal conforming parser. Extracts nothing, by design."""

    parser_id = "stub"
    parser_version = "0.0.0"
    modality = Modality.VECTOR_TEXT

    def can_read(self, path: str) -> bool:
        return path.endswith(".pdf")

    def supported_statement_types(self):
        return ["cabin.deck"]

    def parse(self, path: str, artifact_id: str) -> ParserResult:
        return ParserResult(
            artifact_id=artifact_id,
            parser_id=self.parser_id,
            parser_version=self.parser_version,
            unreadable_regions=["entire document — no extraction implemented"],
        )


class TestParserContract(unittest.TestCase):

    def test_contract_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            DocumentParser()

    def test_candidate_requires_a_locator(self):
        with self.assertRaises(ValueError):
            ExtractionCandidate(
                artifact_id="ART-0001", statement_type="cabin.deck", value=14,
                page=1, locator="", modality=Modality.VECTOR_TEXT,
                parser_id="stub", parser_version="0.0.0")

    def test_candidate_must_name_its_parser(self):
        with self.assertRaises(ValueError):
            ExtractionCandidate(
                artifact_id="ART-0001", statement_type="cabin.deck", value=14,
                page=1, locator="p1", modality=Modality.VECTOR_TEXT,
                parser_id="", parser_version="")

    def test_candidate_always_requires_human_confirmation(self):
        c = ExtractionCandidate(
            artifact_id="ART-0001", statement_type="cabin.deck", value=14,
            page=1, locator="p1", modality=Modality.VECTOR_TEXT,
            parser_id="stub", parser_version="0.0.0")
        self.assertTrue(c.requires_human_confirmation)

    def test_candidate_is_not_a_statement(self):
        """No promotion path exists on the candidate itself."""
        c = ExtractionCandidate(
            artifact_id="ART-0001", statement_type="cabin.deck", value=14,
            page=1, locator="p1", modality=Modality.VECTOR_TEXT,
            parser_id="stub", parser_version="0.0.0")
        for forbidden in ("to_statement", "publish", "approve", "promote"):
            self.assertFalse(hasattr(c, forbidden), forbidden)

    def test_parser_module_touches_no_writable_component(self):
        """A parser must not be able to reach the store."""
        import timonelo.evidence.parsers.base as base
        source = open(base.__file__, encoding="utf-8").read()
        for forbidden in ("StatementEditor", "ArtifactRegistry", "ReviewLog",
                          "TruthEngine"):
            self.assertNotIn(
                f"import {forbidden}", source,
                f"parser contract imports {forbidden}")

    def test_no_extraction_is_implemented(self):
        """Sprint 0010 defines the contract only."""
        import timonelo.evidence.parsers as pkg
        implementations = [
            n for n in dir(pkg)
            if n.endswith("Parser") and n not in ("DocumentParser",)
        ]
        self.assertEqual(implementations, [])


class TestParserRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ParserRegistry()
        self.parser = StubParser()
        self.registry.register(self.parser)

    def test_registration_and_lookup(self):
        self.assertEqual(len(self.registry), 1)
        self.assertIs(self.registry.get("stub", "0.0.0"), self.parser)

    def test_duplicate_registration_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.register(StubParser())

    def test_selection_by_file(self):
        self.assertEqual(len(self.registry.candidates_for("x.pdf")), 1)
        self.assertEqual(len(self.registry.candidates_for("x.png")), 0)

    def test_selection_by_statement_type(self):
        self.assertEqual(len(self.registry.for_statement_type("cabin.deck")), 1)
        self.assertEqual(len(self.registry.for_statement_type("cabin.area_sqm")), 0)

    def test_result_reports_what_it_could_not_read(self):
        result = self.parser.parse("x.pdf", "ART-0001")
        self.assertEqual(list(result.candidates), [])
        self.assertTrue(result.unreadable_regions)


class TestModalitiesAreAlternatives(unittest.TestCase):

    def test_modalities_are_flat_not_a_hierarchy(self):
        """Raster is not a specialisation of vector; they fail differently."""
        self.assertEqual(len(set(Modality)), 5)
        for m in Modality:
            self.assertIsInstance(m.value, str)


if __name__ == "__main__":
    unittest.main()
