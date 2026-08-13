import tempfile
import unittest
from pathlib import Path

from knowledge.loader import KnowledgeLoader


class KnowledgeLoaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for folder in ("ships", "cruise-lines", "sources"):
            (self.root / folder).mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, metadata: str) -> None:
        path = self.root / relative
        path.write_text(f"# Record\n\n## Metadata\n\n{metadata}\n\n## Body\nIgnored.\n", encoding="utf-8")

    def test_successful_loading_and_resolution(self) -> None:
        self.write("sources/source.md", "- Source ID: SRC-1\n- Title: Source\n- Publisher: Publisher\n- URL: https://example.test\n- Published date: 2026-01-01\n- Accessed date: 2026-08-13\n- Source type: web\n- Review status: reviewed")
        self.write("cruise-lines/line.md", "- Entity ID: CL-1\n- Canonical name: Line\n- Entity type: CruiseLine\n- Status: reviewed\n- Last reviewed: 2026-08-13")
        self.write("ships/ship.md", "- Entity ID: SHIP-1\n- Canonical name: Ship\n- Entity type: Ship\n- Status: reviewed\n- Last reviewed: 2026-08-13\n- Aliases: ship-one\n- Related IDs: CL-1\n- Source IDs: SRC-1")

        registry = KnowledgeLoader(self.root).load()

        self.assertTrue(registry.validation.is_valid)
        self.assertEqual(registry.resolve("ship-one").knowledge_id, "SHIP-1")
        self.assertEqual(registry.resolve_record("CL-1").title, "Line")
        self.assertEqual(registry.resolve_source("SRC-1").title, "Source")

    def test_duplicate_id_detection(self) -> None:
        metadata = "- Entity ID: DUP-1\n- Canonical name: Duplicate\n- Entity type: Ship\n- Status: draft\n- Last reviewed: 2026-08-13"
        self.write("ships/one.md", metadata)
        self.write("cruise-lines/two.md", metadata.replace("Entity type: Ship", "Entity type: CruiseLine"))

        result = KnowledgeLoader(self.root).load().validation

        self.assertEqual(len(result.by_code("DUPLICATE_ID")), 2)
        self.assertIsNone(KnowledgeLoader(self.root).load().resolve("DUP-1"))

    def test_missing_metadata(self) -> None:
        self.write("ships/incomplete.md", "- Entity ID: SHIP-1\n- Canonical name:\n- Status:")

        result = KnowledgeLoader(self.root).load().validation

        self.assertGreaterEqual(len(result.by_code("MISSING_METADATA")), 3)

    def test_missing_references(self) -> None:
        self.write("ships/ship.md", "- Entity ID: SHIP-1\n- Canonical name: Ship\n- Entity type: Ship\n- Status: draft\n- Last reviewed: 2026-08-13\n- Related IDs: CL-404\n- Source IDs: SRC-404")

        result = KnowledgeLoader(self.root).load().validation

        self.assertEqual(len(result.by_code("MISSING_RELATED_RECORD")), 1)
        self.assertEqual(len(result.by_code("MISSING_SOURCE_RECORD")), 1)


if __name__ == "__main__":
    unittest.main()
