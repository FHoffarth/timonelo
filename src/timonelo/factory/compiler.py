"""
Knowledge Factory Stage 05/08: Master Production Compiler CLI.
Compiles verified Spatial Ontologies into sealed Knowledge Packs and Cruise Explorer runtime assets.
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Ensure src is in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from timonelo.ontology.models import VesselSpatialOntology
from timonelo.ontology.bellissima import create_bellissima_ontology
from timonelo.ontology.andorinha import create_andorinha_ontology
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.calculus.sandwich import DeterministicSandwichResolver
from timonelo.calculus.sightlines import DeterministicSightlineCalculator
from timonelo.lenses.accessibility import AccessibilityLens
from timonelo.lenses.family import FamilyLens
from timonelo.lenses.quiet import QuietCabinLens
from timonelo.factory.validator import SpatialIntegrityValidator
from timonelo.factory.patch_engine import (
    HypothesisPublicationBlocked,
    HypothesisVesselSpatialOntology,
)


class KnowledgeFactoryCompiler:
    """Master compilation pipeline executing Stages 01 through 08."""

    @staticmethod
    def compile_vessel(
        ontology: VesselSpatialOntology | HypothesisVesselSpatialOntology,
        output_data_dir: Path,
        output_frontend_dir: Optional[Path] = None,
    ) -> bool:
        if isinstance(ontology, HypothesisVesselSpatialOntology):
            raise HypothesisPublicationBlocked(
                "Quarantined sister-ship hypotheses cannot write canonical or passenger assets"
            )

        print(f"============================================================")
        print(f"KNOWLEDGE FACTORY COMPILER — {ontology.name} ({ontology.imo_number})")
        print(f"============================================================")

        # 1. Run Automated Quality Gate Audit (Stage 06 & 07)
        report = SpatialIntegrityValidator.audit_vessel(ontology)
        print("Stage 06/07 Quality Gates Audit:")
        for gate in report.quality_gates_passed:
            print(f"  [PASS] {gate}")

        if not report.is_valid:
            print(f"\n[FAIL] Quality Gates FAILED ({len(report.issues)} issue(s)):")
            for issue in report.issues:
                print(f"  [FAIL] {issue}")
            return False

        print("\n[OK] 100% Quality Gates Passed. Proceeding to Stage 05/08 Compilation...\n")

        # 2. Initialize Spatial Calculus Engines
        router = DeterministicSpatialRouter(ontology)
        sandwich_resolver = DeterministicSandwichResolver(ontology)
        sightline_calc = DeterministicSightlineCalculator(ontology)

        ship_slug = ontology.name.lower().replace(" ", "-")

        ship_data = {
            "imo": ontology.imo_number,
            "name": ontology.name,
            "ship_class": ontology.ship_class,
            "length_m": ontology.length_overall_meters,
            "beam_m": ontology.beam_meters,
            "total_decks": ontology.total_decks,
            "decks": {},
            "cabins": {},
        }

        # 3. Populate Decks & Venues
        for deck_num, deck in sorted(ontology.decks.items(), key=lambda x: x[0]):
            ship_data["decks"][str(deck_num)] = {
                "deck_number": deck.deck_number,
                "name": deck.name,
                "elevation_m": deck.elevation_meters,
                "zone": deck.zone.value,
                "venues": [
                    {
                        "id": v.venue_id,
                        "name": v.name,
                        "category": v.category.value,
                        "is_noise_generator": v.is_noise_generator,
                    }
                    for v in deck.venues.values()
                ],
            }

            # 4. Populate & Calculate All Staterooms
            for cabin_num, cabin in sorted(deck.cabins.items(), key=lambda x: x[0]):
                sandwich = sandwich_resolver.resolve_cabin_sandwich(cabin_num)
                sightline = sightline_calc.calculate_sightline(cabin_num)

                # Plane 4 Lenses
                lens_acc = AccessibilityLens.evaluate(ontology, router, cabin_num)
                lens_fam = FamilyLens.evaluate(ontology, router, cabin_num)
                lens_quiet = QuietCabinLens.evaluate(ontology, sandwich_resolver, router, cabin_num)

                # Key Wayfinding Targets
                distances = {}
                # Marketplace Buffet (Deck 15)
                buffet_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, "D15_BUFFET_ENTRANCE")
                if buffet_route:
                    distances["buffet"] = {
                        "meters": buffet_route.total_distance_meters,
                        "seconds": buffet_route.estimated_walking_seconds,
                        "steps": buffet_route.estimated_step_count,
                        "step_free": buffet_route.is_fully_step_free,
                    }

                # London Theatre (Deck 06)
                theater_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, "D06_THEATER")
                if theater_route:
                    distances["theater"] = {
                        "meters": theater_route.total_distance_meters,
                        "seconds": theater_route.estimated_walking_seconds,
                        "steps": theater_route.estimated_step_count,
                        "step_free": theater_route.is_fully_step_free,
                    }

                # Nearest Elevator on current deck
                nearest_lift_node = f"D{cabin.deck_number:02d}_AFT_LIFT"
                lift_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, nearest_lift_node)
                if lift_route:
                    distances["elevator"] = {
                        "meters": lift_route.total_distance_meters,
                        "seconds": lift_route.estimated_walking_seconds,
                        "steps": lift_route.estimated_step_count,
                        "step_free": lift_route.is_fully_step_free,
                    }

                # Determine zone label
                station = cabin.boundary_polygon[0].x
                if station < 0.38:
                    zone_label = "Midship-Aft"
                elif station < 0.63:
                    zone_label = "Midship"
                else:
                    zone_label = "Midship-Forward"

                ship_data["cabins"][cabin_num] = {
                    "cabin_number": cabin.cabin_number,
                    "deck_number": cabin.deck_number,
                    "deck_name": deck.name,
                    "hull_side": cabin.hull_side.value,
                    "zone": zone_label,
                    "category_code": cabin.category_code,
                    "square_meters": cabin.square_meters,
                    "balcony_type": cabin.balcony_type.value,
                    "connecting_cabin_number": cabin.connecting_cabin_number,
                    "bed_near_balcony": cabin.bed_near_balcony,
                    "is_accessible": cabin.is_accessible_stateroom,
                    "door_width_mm": cabin.door.clear_width_mm,
                    "sockets": {
                        "eu_count": cabin.sockets.eu_standard_count,
                        "us_count": cabin.sockets.us_standard_count,
                        "usb_a_count": cabin.sockets.usb_a_count,
                        "usb_c_count": cabin.sockets.usb_c_count,
                        "bedside_usb": cabin.sockets.bedside_usb_available,
                    },
                    "surroundings": {
                        "overhead": {
                            "deck_number": sandwich.overhead_layer.deck_number if sandwich and sandwich.overhead_layer else None,
                            "deck_name": sandwich.overhead_layer.deck_name if sandwich and sandwich.overhead_layer else None,
                            "venues": sandwich.overhead_layer.intersecting_venues if sandwich and sandwich.overhead_layer else [],
                            "is_residential": sandwich.overhead_layer.is_residential_cabins_only if sandwich and sandwich.overhead_layer else True,
                            "is_noise_generator": sandwich.overhead_layer.is_active_noise_generator if sandwich and sandwich.overhead_layer else False,
                        },
                        "underfoot": {
                            "deck_number": sandwich.underfoot_layer.deck_number if sandwich and sandwich.underfoot_layer else None,
                            "deck_name": sandwich.underfoot_layer.deck_name if sandwich and sandwich.underfoot_layer else None,
                            "venues": sandwich.underfoot_layer.intersecting_venues if sandwich and sandwich.underfoot_layer else [],
                            "is_residential": sandwich.underfoot_layer.is_residential_cabins_only if sandwich and sandwich.underfoot_layer else True,
                        },
                        "adjacent_connecting": cabin.connecting_cabin_number,
                    },
                    "sightlines": {
                        "horizon_angle_deg": sightline.horizon_view_angle_degrees,
                        "downward_angle_deg": sightline.downward_sea_view_angle_degrees,
                        "has_lifeboat_obstruction": sightline.has_lifeboat_obstruction,
                        "description": sightline.description,
                    },
                    "distances": distances,
                    "lenses": {
                        "accessibility": {
                            "is_certified": lens_acc.is_accessible_certified if lens_acc else False,
                            "summary": lens_acc.summary if lens_acc else "",
                            "lift_distance_m": lens_acc.nearest_elevator_distance_meters if lens_acc else 0,
                        },
                        "family": {
                            "is_optimized": lens_fam.is_family_optimized if lens_fam else False,
                            "has_connecting": lens_fam.has_connecting_door if lens_fam else False,
                            "connecting_cabin": lens_fam.connecting_cabin_number if lens_fam else None,
                            "kids_club_distance_m": lens_fam.kids_club_distance_meters if lens_fam else 0,
                            "summary": lens_fam.summary if lens_fam else "",
                        },
                        "quiet": {
                            "is_quiet_tier": lens_quiet.is_quiet_tier if lens_quiet else False,
                            "acoustic_flags": lens_quiet.acoustic_flags if lens_quiet else [],
                            "summary": lens_quiet.summary if lens_quiet else "",
                        },
                    },
                    "evidence": [
                        {
                            "source_id": e.source_id,
                            "sha256": e.sha256,
                            "locator": e.locator,
                        }
                        for e in cabin.evidence_links
                    ],
                }

        # 5. Write Canonical Knowledge Pack Artifacts
        vessel_data_dir = output_data_dir / f"data/ships/{ship_slug}"
        vessel_data_dir.mkdir(parents=True, exist_ok=True)
        canonical_file = vessel_data_dir / "knowledge-pack.json"
        with open(canonical_file, "w", encoding="utf-8") as f:
            json.dump(ship_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"  [EXPORT] Written Canonical Knowledge Pack: {canonical_file}")

        # 6. Write Frontend Runtime Asset
        if output_frontend_dir:
            frontend_public_dir = output_frontend_dir / "public/data"
            frontend_public_dir.mkdir(parents=True, exist_ok=True)
            frontend_file = frontend_public_dir / f"{ship_slug}.json"
            with open(frontend_file, "w", encoding="utf-8") as f:
                json.dump(ship_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            print(f"  [EXPORT] Written Cruise Explorer Pack:     {frontend_file}")

        print(f"\nCompilation SUCCESSFUL for {ontology.name}.\n")
        return True


def compile_fleet(root_dir: Path) -> bool:
    """Compile only evidence-bearing reference vessels.

    Historical sister-ship patches remain available to the hypothesis tool but
    are deliberately absent from this canonical/runtime writer.
    """
    compiler = KnowledgeFactoryCompiler()

    # 1. Compile Primary Ocean Baseline: MSC Bellissima
    print(">>> [1/FLEET] COMPILING PRIMARY OCEAN BASELINE: MSC BELLISSIMA (IMO 9766205)")
    bellissima_ontology = create_bellissima_ontology()
    ok_bellissima = compiler.compile_vessel(
        ontology=bellissima_ontology,
        output_data_dir=root_dir,
        output_frontend_dir=root_dir / "frontend",
    )
    if not ok_bellissima:
        return False

    # 2. Compile Primary River Baseline: MS Andorinha
    print("\n>>> [2/FLEET] COMPILING PRIMARY RIVER BASELINE: MS ANDORINHA (ENI 02338573)")
    andorinha_ontology = create_andorinha_ontology()
    ok_andorinha = compiler.compile_vessel(
        ontology=andorinha_ontology,
        output_data_dir=root_dir,
        output_frontend_dir=root_dir / "frontend",
    )
    if not ok_andorinha:
        return False

    return True


def main():
    root = Path(__file__).resolve().parent.parent.parent.parent
    success = compile_fleet(root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
