import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from timonelo.knowledge_pack.codec import load_pack
from timonelo.knowledge_pack.persistence import (
    KnowledgePackRepository,
    PersistenceConflictError,
)
from timonelo.knowledge_pack.validation import validate_pack


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = REPOSITORY_ROOT / "data" / "ships" / "msc-bellissima" / "knowledge-pack.json"


class CruiseKnowledgePackTest(unittest.TestCase):
    def test_reference_pack_has_valid_bounded_inventory(self) -> None:
        pack = load_pack(PACK_PATH)

        self.assertEqual(pack.ship.name, "MSC Bellissima")
        self.assertEqual(len(pack.decks), 15)
        self.assertEqual(len(pack.cabin_categories), 20)
        self.assertEqual(len(pack.cabins), 7)
        self.assertEqual(len(pack.public_areas), 14)
        self.assertEqual(len(pack.relationships), 15)
        self.assertEqual(len(pack.claims), 4)
        self.assertEqual(validate_pack(pack), ())

    def test_unknowns_are_not_filled_by_inference(self) -> None:
        pack = load_pack(PACK_PATH)
        cabins = {cabin.number: cabin for cabin in pack.cabins}

        self.assertIsNone(cabins["13245"].category_id)
        self.assertTrue(any("unknown" in limitation.lower() for limitation in cabins["13245"].limitations))
        self.assertEqual(cabins["16018"].category_id, "cabin-category:msc-bellissima:yc1")

    def test_every_material_record_has_provenance_and_locator(self) -> None:
        pack = load_pack(PACK_PATH)

        self.assertTrue(all(entity.source_ids for entity in pack.entities()))
        self.assertTrue(pack.ship.source_locator)
        self.assertTrue(all(deck.source_locator for deck in pack.decks))
        self.assertTrue(all(category.source_locator for category in pack.cabin_categories))
        self.assertTrue(all(cabin.source_locator for cabin in pack.cabins))
        self.assertTrue(all(area.source_locator for area in pack.public_areas))
        self.assertTrue(all(item.source_ids and item.source_locator for item in pack.relationships))
        self.assertTrue(all(item.source_ids and item.source_locator for item in pack.claims))

    def test_invalid_reference_is_rejected_before_persistence(self) -> None:
        pack = load_pack(PACK_PATH)
        invalid_cabin = replace(pack.cabins[0], deck_id="deck:msc-bellissima:missing")
        invalid_pack = replace(pack, cabins=(invalid_cabin, *pack.cabins[1:]))

        issue_codes = {issue.code for issue in validate_pack(invalid_pack)}

        self.assertIn("DECK_REFERENCE", issue_codes)

    def test_import_is_transactional_queryable_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "knowledge.sqlite"
            repository = KnowledgePackRepository(database)

            first = repository.import_path(PACK_PATH)
            second = repository.import_path(PACK_PATH)
            summary = repository.summary(first.pack_id, first.version)

            self.assertTrue(first.inserted)
            self.assertFalse(second.inserted)
            self.assertEqual(first.content_sha256, second.content_sha256)
            self.assertEqual(summary["decks"], 15)
            self.assertEqual(summary["cabins"], 7)
            self.assertEqual(summary["public_areas"], 14)
            self.assertEqual(len(repository.provenance_for(first.pack_id, first.version, "cabin:msc-bellissima:16018")), 1)
            with closing(repository.connect()) as connection:
                self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                yc1_decks = connection.execute(
                    "SELECT COUNT(*) FROM cabin_category_decks WHERE category_entity_id = ?",
                    ("cabin-category:msc-bellissima:yc1",),
                ).fetchone()[0]
                bunk_bed_cabins = connection.execute(
                    "SELECT COUNT(*) FROM cabin_features WHERE feature_code = 'bunk-bed-only'"
                ).fetchone()[0]
                self.assertEqual(yc1_decks, 4)
                self.assertEqual(bunk_bed_cabins, 4)

    def test_existing_version_rejects_different_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "knowledge.sqlite"
            changed_pack = root / "changed.json"
            document = json.loads(PACK_PATH.read_text(encoding="utf-8"))
            document["status"] = "superseded"
            changed_pack.write_text(json.dumps(document), encoding="utf-8")
            repository = KnowledgePackRepository(database)
            repository.import_path(PACK_PATH)

            with self.assertRaises(PersistenceConflictError):
                repository.import_path(changed_pack)

            with closing(sqlite3.connect(database)) as connection:
                count = connection.execute("SELECT COUNT(*) FROM knowledge_pack_versions").fetchone()[0]
            self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
