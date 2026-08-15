"""
Unit tests for Knowledge Factory Automated Pipeline (ADR-0001).
Tests ManifestImporter, CorridorMeshGenerator, SpatialIntegrityValidator, and Compiler.
"""

import unittest
from pathlib import Path
from timonelo.factory.manifest_importer import ManifestImporter, CabinManifestRecord
from timonelo.factory.corridor_generator import CorridorMeshGenerator
from timonelo.factory.validator import SpatialIntegrityValidator
from timonelo.factory.compiler import KnowledgeFactoryCompiler
from timonelo.factory.patch_engine import ShipPatchEngine
from timonelo.ontology.bellissima import create_bellissima_ontology
from timonelo.ontology.models import HullSide, BalconyType, EvidenceLink


class TestKnowledgeFactory(unittest.TestCase):
    def setUp(self):
        self.ontology = create_bellissima_ontology()
        self.dummy_evidence = [
            EvidenceLink(
                source_id="EVID-TEST-01",
                sha256="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                locator="Test_Locator_GA",
            )
        ]

    def test_manifest_importer_row_parsing(self):
        row = {
            "cabin_number": "14122",
            "deck_number": "14",
            "hull_side": "STARBOARD",
            "category_code": "BA",
            "square_meters": "19.0",
            "balcony_type": "UNOBSTRUCTED",
            "connecting_cabin": "14120",
            "is_accessible": "false",
            "door_clear_width_mm": "850",
            "bed_near_balcony": "true",
            "eu_sockets": "2",
            "us_sockets": "2",
            "usb_a_sockets": "2",
            "usb_c_sockets": "1",
            "bedside_usb": "true",
            "station_x_fraction": "0.28",
        }
        rec = ManifestImporter._row_to_record(row)
        self.assertEqual(rec.cabin_number, "14122")
        self.assertEqual(rec.deck_number, 14)
        self.assertEqual(rec.hull_side, HullSide.STARBOARD)
        self.assertEqual(rec.door_clear_width_mm, 850)
        self.assertTrue(rec.bed_near_balcony)
        self.assertEqual(rec.connecting_cabin, "14120")

    def test_corridor_mesh_generator(self):
        rec1 = CabinManifestRecord(
            cabin_number="12122",
            deck_number=12,
            hull_side=HullSide.STARBOARD,
            category_code="BA",
            square_meters=19.0,
            balcony_type=BalconyType.UNOBSTRUCTED,
            connecting_cabin="12120",
            is_accessible=False,
            door_clear_width_mm=850,
            bed_near_balcony=True,
            eu_sockets=2,
            us_sockets=2,
            usb_a_sockets=2,
            usb_c_sockets=1,
            bedside_usb=True,
            station_x_fraction=0.28,
        )
        cabins, nodes, edges = CorridorMeshGenerator.generate_deck_topology(
            deck_number=12,
            records=[rec1],
            evidence=self.dummy_evidence,
        )
        self.assertIn("12122", cabins)
        self.assertIn("D12_AFT_LIFT", nodes)
        self.assertIn("D12_AFT_CORR_STBD_1", nodes)
        self.assertEqual(cabins["12122"].door.corridor_snap_node_id, "D12_AFT_CORR_STBD_1")
        self.assertTrue(len(edges) >= 3)

    def test_spatial_integrity_validator(self):
        report = SpatialIntegrityValidator.audit_vessel(self.ontology)
        self.assertTrue(report.is_valid, f"Validation failed with issues: {report.issues}")
        self.assertEqual(report.orphaned_doors_count, 0)
        self.assertEqual(report.missing_evidence_count, 0)
        self.assertIn("GATE_1_PROVENANCE_SATISFIED", report.quality_gates_passed)
        self.assertIn("GATE_2_TOPOLOGY_ZERO_ORPHANS", report.quality_gates_passed)
        self.assertIn("GATE_3_SANDWICH_INTEGRITY", report.quality_gates_passed)
        self.assertIn("GATE_4_CIRCULATION_CONNECTED", report.quality_gates_passed)

    def test_ship_patch_engine_meraviglia(self):
        patch_data = {
            "target_imo": "IMO9647710",
            "target_name": "MSC Meraviglia",
            "operations": [
                {
                    "op": "RENAME_VENUE",
                    "deck": 6,
                    "venue_id": "VENUE_THEATER",
                    "new_name": "Broadway Theatre (Lower Level)",
                },
                {
                    "op": "REPLACE_VENUE",
                    "deck": 7,
                    "venue_id": "VENUE_HOLA_TAPAS",
                    "replacement": {
                        "venue_id": "VENUE_EATALY",
                        "name": "Eataly Ristorante Italiano & Food Market",
                        "category": "DINING",
                    },
                },
            ],
        }
        derivative = ShipPatchEngine.apply_patch(self.ontology, patch_data)
        self.assertEqual(derivative.name, "MSC Meraviglia")
        self.assertEqual(derivative.imo_number, "IMO9647710")
        self.assertEqual(derivative.decks[6].venues["VENUE_THEATER"].name, "Broadway Theatre (Lower Level)")
        self.assertIn("VENUE_EATALY", derivative.decks[7].venues)
        self.assertNotIn("VENUE_HOLA_TAPAS", derivative.decks[7].venues)
        # Ensure baseline ontology was not mutated
        self.assertEqual(self.ontology.name, "MSC Bellissima")
        self.assertEqual(self.ontology.decks[6].venues["VENUE_THEATER"].name, "London Theatre (Lower Level)")


if __name__ == "__main__":
    unittest.main()


