"""
Knowledge Factory SPEC-008: Non-Destructive Ship Patch & Delta Compilation Engine.
Inherits 100% of immutable reference vessel geometry and applies surgical delta overlays.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import replace
from timonelo.ontology.models import (
    VesselSpatialOntology,
    Deck,
    Cabin,
    Venue,
    CorridorNode,
    CorridorEdge,
    DoorNode,
    Coordinate2D,
    HullSide,
    DeckVerticalZone,
    VenueCategory,
    BalconyType,
    PowerSocketMatrix,
    EvidenceLink,
)


class ShipPatchEngine:
    """Applies non-destructive SPEC-008 delta operations onto a base vessel ontology."""

    @staticmethod
    def apply_patch(base_ontology: VesselSpatialOntology, patch_data: Dict[str, Any]) -> VesselSpatialOntology:
        """
        Creates a new derivative vessel ontology by applying patch operations
        onto the immutable base ontology without mutating the baseline.
        """
        target_imo = patch_data.get("target_imo", base_ontology.imo_number)
        target_name = patch_data.get("target_name", base_ontology.name)
        target_class = patch_data.get("ship_class", base_ontology.ship_class)

        # Deep copy decks dictionary with new Deck objects
        new_decks: Dict[int, Deck] = {}
        for deck_num, deck in base_ontology.decks.items():
            new_cabins = dict(deck.cabins)
            new_venues = dict(deck.venues)
            new_nodes = dict(deck.corridor_nodes)
            new_edges = list(deck.corridor_edges)

            new_decks[deck_num] = Deck(
                deck_number=deck.deck_number,
                name=deck.name,
                elevation_meters=deck.elevation_meters,
                perimeter_polygon=list(deck.perimeter_polygon),
                zone=deck.zone,
                cabins=new_cabins,
                venues=new_venues,
                corridor_nodes=new_nodes,
                corridor_edges=new_edges,
            )

        # Execute Operations sequentially
        for op in patch_data.get("operations", []):
            op_type = op.get("op")
            deck_num = op.get("deck")

            if deck_num not in new_decks:
                continue
            target_deck = new_decks[deck_num]

            if op_type == "RENAME_VENUE":
                venue_id = op.get("venue_id")
                new_name = op.get("new_name")
                if venue_id in target_deck.venues:
                    old_v = target_deck.venues[venue_id]
                    target_deck.venues[venue_id] = Venue(
                        venue_id=old_v.venue_id,
                        name=new_name,
                        deck_number=old_v.deck_number,
                        category=old_v.category,
                        boundary_polygon=old_v.boundary_polygon,
                        entrance_node_ids=old_v.entrance_node_ids,
                        is_noise_generator=old_v.is_noise_generator,
                        is_open_deck=old_v.is_open_deck,
                        evidence_links=old_v.evidence_links,
                    )

            elif op_type == "REPLACE_VENUE":
                venue_id = op.get("venue_id")
                rep = op.get("replacement", {})
                if venue_id in target_deck.venues:
                    old_v = target_deck.venues[venue_id]
                    cat_str = rep.get("category", old_v.category.name)
                    cat_enum = VenueCategory[cat_str] if hasattr(VenueCategory, cat_str) else old_v.category
                    new_v_id = rep.get("venue_id", venue_id)

                    del target_deck.venues[venue_id]
                    target_deck.venues[new_v_id] = Venue(
                        venue_id=new_v_id,
                        name=rep.get("name", old_v.name),
                        deck_number=old_v.deck_number,
                        category=cat_enum,
                        boundary_polygon=rep.get("boundary_polygon", old_v.boundary_polygon),
                        entrance_node_ids=old_v.entrance_node_ids,
                        is_noise_generator=rep.get("is_noise_generator", old_v.is_noise_generator),
                        is_open_deck=rep.get("is_open_deck", old_v.is_open_deck),
                        evidence_links=old_v.evidence_links,
                    )

            elif op_type == "ADD_VENUE":
                venue_data = op.get("venue", {})
                v_id = venue_data.get("venue_id")
                cat_str = venue_data.get("category", "BAR_LOUNGE")
                cat_enum = VenueCategory[cat_str] if hasattr(VenueCategory, cat_str) else VenueCategory.BAR_LOUNGE
                poly_coords = [Coordinate2D(pt[0], pt[1]) for pt in venue_data.get("boundary_polygon", [])]
                ev_links = [
                    EvidenceLink(source_id=e.get("source_id", "EVID-GA-PLUS"), sha256=e.get("sha256"), locator=e.get("locator", "GA_Plus"))
                    for e in venue_data.get("evidence_links", [])
                ] or list(next(iter(target_deck.venues.values())).evidence_links if target_deck.venues else [])

                target_deck.venues[v_id] = Venue(
                    venue_id=v_id,
                    name=venue_data.get("name", v_id),
                    deck_number=deck_num,
                    category=cat_enum,
                    boundary_polygon=poly_coords or [Coordinate2D(0.5, -0.3), Coordinate2D(0.6, -0.3), Coordinate2D(0.6, 0.3), Coordinate2D(0.5, 0.3)],
                    entrance_node_ids=venue_data.get("entrance_node_ids", [f"D{deck_num:02d}_MID_LIFT"]),
                    is_noise_generator=venue_data.get("is_noise_generator", False),
                    is_open_deck=venue_data.get("is_open_deck", False),
                    evidence_links=ev_links,
                )

            elif op_type == "RENAME_DECK":
                new_deck_name = op.get("new_name")
                new_decks[deck_num] = Deck(
                    deck_number=target_deck.deck_number,
                    name=new_deck_name,
                    elevation_meters=target_deck.elevation_meters,
                    perimeter_polygon=target_deck.perimeter_polygon,
                    zone=target_deck.zone,
                    cabins=target_deck.cabins,
                    venues=target_deck.venues,
                    corridor_nodes=target_deck.corridor_nodes,
                    corridor_edges=target_deck.corridor_edges,
                )

        target_loa = patch_data.get("length_overall_meters", base_ontology.length_overall_meters)
        target_beam = patch_data.get("beam_meters", base_ontology.beam_meters)
        target_total_decks = patch_data.get("total_decks", base_ontology.total_decks)

        return VesselSpatialOntology(
            imo_number=target_imo,
            name=target_name,
            ship_class=target_class,
            length_overall_meters=target_loa,
            beam_meters=target_beam,
            total_decks=target_total_decks,
            decks=new_decks,
        )
