"""
MSC Bellissima Full Ship Knowledge Pack & Spatial Twin Generator.
Exports canonical JSON for the Cruise Explorer runtime (Plane 5).
Includes all passenger residential tiers (Decks 08-14), Lido (Deck 15), Promenade (Deck 06), Youth (Deck 18).
"""

import json
from pathlib import Path
from src.timonelo.ontology.bellissima import create_bellissima_ontology
from src.timonelo.calculus.router import DeterministicSpatialRouter
from src.timonelo.calculus.sandwich import DeterministicSandwichResolver
from src.timonelo.calculus.sightlines import DeterministicSightlineCalculator
from src.timonelo.lenses.accessibility import AccessibilityLens
from src.timonelo.lenses.family import FamilyLens
from src.timonelo.lenses.quiet import QuietCabinLens


def generate_explorer_pack():
    ontology = create_bellissima_ontology()
    router = DeterministicSpatialRouter(ontology)
    sandwich_resolver = DeterministicSandwichResolver(ontology)
    sightline_calc = DeterministicSightlineCalculator(ontology)

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

    # Populate Decks and Venues
    for deck_num, deck in ontology.decks.items():
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

        # Populate Cabins
        for cabin_num, cabin in deck.cabins.items():
            # Spatial Calculus derivations
            sandwich = sandwich_resolver.resolve_cabin_sandwich(cabin_num)
            sightline = sightline_calc.calculate_sightline(cabin_num)
            
            # Contextual Lens evaluations
            lens_acc = AccessibilityLens.evaluate(ontology, router, cabin_num)
            lens_fam = FamilyLens.evaluate(ontology, router, cabin_num)
            lens_quiet = QuietCabinLens.evaluate(ontology, sandwich_resolver, router, cabin_num)

            # Nearest Venues / Key Distances
            distances = {}
            # Buffet (Deck 15)
            buffet_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, "D15_BUFFET_ENTRANCE")
            if buffet_route:
                distances["buffet"] = {
                    "meters": buffet_route.total_distance_meters,
                    "seconds": buffet_route.estimated_walking_seconds,
                    "steps": buffet_route.estimated_step_count,
                    "step_free": buffet_route.is_fully_step_free,
                }

            # Main Theater (Deck 06)
            theater_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, "D06_THEATER")
            if theater_route:
                distances["theater"] = {
                    "meters": theater_route.total_distance_meters,
                    "seconds": theater_route.estimated_walking_seconds,
                    "steps": theater_route.estimated_step_count,
                    "step_free": theater_route.is_fully_step_free,
                }

            # Nearest Elevator on same deck
            nearest_lift_node = f"D{cabin.deck_number:02d}_AFT_LIFT"
            lift_route = router.find_shortest_path(cabin.door.corridor_snap_node_id, nearest_lift_node)
            if lift_route:
                distances["elevator"] = {
                    "meters": lift_route.total_distance_meters,
                    "seconds": lift_route.estimated_walking_seconds,
                    "steps": lift_route.estimated_step_count,
                    "step_free": lift_route.is_fully_step_free,
                }

            ship_data["cabins"][cabin_num] = {
                "cabin_number": cabin.cabin_number,
                "deck_number": cabin.deck_number,
                "deck_name": deck.name,
                "hull_side": cabin.hull_side.value,
                "zone": "Midship-Aft",
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

    # Write to frontend public and data ships directory
    out_path_frontend = Path("frontend/public/data/msc-bellissima.json")
    out_path_frontend.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path_frontend, "w", encoding="utf-8") as f:
        json.dump(ship_data, f, indent=2)

    out_path_data = Path("data/ships/msc-bellissima/knowledge-pack.json")
    out_path_data.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path_data, "w", encoding="utf-8") as f:
        json.dump(ship_data, f, indent=2)

    print(f"Generated explorer pack successfully at {out_path_frontend}")


if __name__ == "__main__":
    generate_explorer_pack()
