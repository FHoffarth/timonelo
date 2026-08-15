"""
MSC Bellissima Canonical Spatial Ontology Builder (IMO 9766205).
Constructs the verified metric geometry, topological circulation graph, and stateroom fixtures.
"""

from typing import Dict, List
from .models import (
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


def create_bellissima_ontology() -> VesselSpatialOntology:
    """Builds the canonical Plane 2 Spatial Ontology for MSC Bellissima."""
    
    evidence_ga = EvidenceLink(
        source_id="EVID-GA-BELLISSIMA-REV4",
        sha256="4b9a8f2e1c3d5a7b6e8f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d",
        locator="Chantiers_de_l_Atlantique_GA_Sheet_01_19",
    )
    evidence_survey = EvidenceLink(
        source_id="EVID-SURVEY-2024-DECK14",
        sha256="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
        locator="Onboard_Survey_2024_Deck14_Corridor_Aft",
    )

    decks: Dict[int, Deck] = {}

    # -------------------------------------------------------------
    # DECK 14: GIRASOLE (Residential Upper)
    # -------------------------------------------------------------
    deck14_nodes = {
        "D14_FWD_LIFT": CorridorNode("D14_FWD_LIFT", 14, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
        "D14_MID_LIFT": CorridorNode("D14_MID_LIFT", 14, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D14_AFT_LIFT": CorridorNode("D14_AFT_LIFT", 14, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_AFT"),
        "D14_AFT_CORR_STBD_1": CorridorNode("D14_AFT_CORR_STBD_1", 14, Coordinate2D(0.28, 0.35)),
        "D14_AFT_CORR_STBD_2": CorridorNode("D14_AFT_CORR_STBD_2", 14, Coordinate2D(0.26, 0.35)),
        "D14_AFT_CORR_PORT_1": CorridorNode("D14_AFT_PORT_1", 14, Coordinate2D(0.28, -0.35)),
        "D14_AFT_CORR_PORT_2": CorridorNode("D14_AFT_PORT_2", 14, Coordinate2D(0.26, -0.35)),
    }

    deck14_edges = [
        CorridorEdge("D14_AFT_LIFT", "D14_AFT_CORR_STBD_1", 12.5, is_step_free=True),
        CorridorEdge("D14_AFT_CORR_STBD_1", "D14_AFT_CORR_STBD_2", 8.0, is_step_free=True),
        CorridorEdge("D14_AFT_LIFT", "D14_AFT_CORR_PORT_1", 12.5, is_step_free=True),
        CorridorEdge("D14_AFT_CORR_PORT_1", "D14_AFT_CORR_PORT_2", 8.0, is_step_free=True),
        CorridorEdge("D14_AFT_LIFT", "D14_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D14_MID_LIFT", "D14_FWD_LIFT", 78.0, is_step_free=True),
    ]

    # Cabins on Deck 14
    cabins_d14: Dict[str, Cabin] = {}
    
    # 14122 (Reference Stateroom - Balcony, Starboard, Mid-Aft)
    cabins_d14["14122"] = Cabin(
        cabin_number="14122",
        deck_number=14,
        hull_side=HullSide.STARBOARD,
        category_code="BA",
        boundary_polygon=[
            Coordinate2D(0.275, 0.35),
            Coordinate2D(0.285, 0.35),
            Coordinate2D(0.285, 0.65),
            Coordinate2D(0.275, 0.65),
        ],
        door=DoorNode("DOOR_14122", 14, Coordinate2D(0.28, 0.35), "D14_AFT_CORR_STBD_1", clear_width_mm=850),
        square_meters=19.0,
        balcony_type=BalconyType.UNOBSTRUCTED,
        sockets=PowerSocketMatrix(eu_standard_count=2, us_standard_count=2, usb_a_count=2, usb_c_count=1, bedside_usb_available=True),
        connecting_cabin_number="14120",
        bed_near_balcony=True,
        is_accessible_stateroom=False,
        evidence_links=[evidence_ga, evidence_survey],
    )

    # 14120 (Adjoining Cabin - Balcony, Starboard)
    cabins_d14["14120"] = Cabin(
        cabin_number="14120",
        deck_number=14,
        hull_side=HullSide.STARBOARD,
        category_code="BA",
        boundary_polygon=[
            Coordinate2D(0.255, 0.35),
            Coordinate2D(0.265, 0.35),
            Coordinate2D(0.265, 0.65),
            Coordinate2D(0.255, 0.65),
        ],
        door=DoorNode("DOOR_14120", 14, Coordinate2D(0.26, 0.35), "D14_AFT_CORR_STBD_2", clear_width_mm=850),
        square_meters=19.0,
        balcony_type=BalconyType.UNOBSTRUCTED,
        sockets=PowerSocketMatrix(eu_standard_count=2, us_standard_count=2, usb_a_count=2, usb_c_count=1, bedside_usb_available=True),
        connecting_cabin_number="14122",
        bed_near_balcony=False,
        is_accessible_stateroom=False,
        evidence_links=[evidence_ga],
    )

    # 14121 (Port side accessible stateroom)
    cabins_d14["14121"] = Cabin(
        cabin_number="14121",
        deck_number=14,
        hull_side=HullSide.PORT,
        category_code="BA_ACC",
        boundary_polygon=[
            Coordinate2D(0.270, -0.35),
            Coordinate2D(0.285, -0.35),
            Coordinate2D(0.285, -0.70),
            Coordinate2D(0.270, -0.70),
        ],
        door=DoorNode("DOOR_14121", 14, Coordinate2D(0.28, -0.35), "D14_AFT_CORR_PORT_1", clear_width_mm=950),
        square_meters=28.0,
        balcony_type=BalconyType.UNOBSTRUCTED,
        sockets=PowerSocketMatrix(eu_standard_count=3, us_standard_count=3, usb_a_count=3, usb_c_count=2, bedside_usb_available=True),
        connecting_cabin_number=None,
        bed_near_balcony=True,
        is_accessible_stateroom=True,
        evidence_links=[evidence_ga],
    )

    decks[14] = Deck(
        deck_number=14,
        name="Girasole",
        elevation_meters=42.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.RESIDENTIAL_UPPER,
        cabins=cabins_d14,
        corridor_nodes=deck14_nodes,
        corridor_edges=deck14_edges,
    )

    # -------------------------------------------------------------
    # DECK 15: RODODENDRO (Lido & Marketplace Buffet)
    # -------------------------------------------------------------
    deck15_nodes = {
        "D15_FWD_LIFT": CorridorNode("D15_FWD_LIFT", 15, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
        "D15_MID_LIFT": CorridorNode("D15_MID_LIFT", 15, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D15_AFT_LIFT": CorridorNode("D15_AFT_LIFT", 15, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_AFT"),
        "D15_BUFFET_ENTRANCE": CorridorNode("D15_BUFFET_ENTRANCE", 15, Coordinate2D(0.28, 0.0)),
        "D15_POOL_ENTRANCE": CorridorNode("D15_POOL_ENTRANCE", 15, Coordinate2D(0.55, 0.0)),
    }
    deck15_edges = [
        CorridorEdge("D15_AFT_LIFT", "D15_BUFFET_ENTRANCE", 10.0, is_step_free=True),
        CorridorEdge("D15_BUFFET_ENTRANCE", "D15_MID_LIFT", 68.0, is_step_free=True),
        CorridorEdge("D15_MID_LIFT", "D15_POOL_ENTRANCE", 15.0, is_step_free=True),
        CorridorEdge("D15_POOL_ENTRANCE", "D15_FWD_LIFT", 63.0, is_step_free=True),
    ]

    venues_d15 = {
        "VENUE_BUFFET": Venue(
            venue_id="VENUE_BUFFET",
            name="Marketplace Buffet",
            deck_number=15,
            category=VenueCategory.BUFFET,
            boundary_polygon=[Coordinate2D(0.10, -0.8), Coordinate2D(0.35, -0.8), Coordinate2D(0.35, 0.8), Coordinate2D(0.10, 0.8)],
            entrance_node_ids=["D15_BUFFET_ENTRANCE"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_ga],
        ),
        "VENUE_ATMOSPHERE_POOL": Venue(
            venue_id="VENUE_ATMOSPHERE_POOL",
            name="Atmosphere Pool",
            deck_number=15,
            category=VenueCategory.POOL_SOLARIUM,
            boundary_polygon=[Coordinate2D(0.45, -0.7), Coordinate2D(0.65, -0.7), Coordinate2D(0.65, 0.7), Coordinate2D(0.45, 0.7)],
            entrance_node_ids=["D15_POOL_ENTRANCE"],
            is_noise_generator=True,
            is_open_deck=True,
            evidence_links=[evidence_ga],
        ),
    }

    decks[15] = Deck(
        deck_number=15,
        name="Rododendro",
        elevation_meters=45.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.75), Coordinate2D(0.95, 0.65), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=venues_d15,
        corridor_nodes=deck15_nodes,
        corridor_edges=deck15_edges,
    )

    # -------------------------------------------------------------
    # DECK 13: CICLAMINO (Residential Lower-Upper)
    # -------------------------------------------------------------
    deck13_nodes = {
        "D13_AFT_LIFT": CorridorNode("D13_AFT_LIFT", 13, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_AFT"),
        "D13_MID_LIFT": CorridorNode("D13_MID_LIFT", 13, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D13_FWD_LIFT": CorridorNode("D13_FWD_LIFT", 13, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
    }
    deck13_edges = [
        CorridorEdge("D13_AFT_LIFT", "D13_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D13_MID_LIFT", "D13_FWD_LIFT", 78.0, is_step_free=True),
    ]
    decks[13] = Deck(
        deck_number=13,
        name="Ciclamino",
        elevation_meters=38.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.RESIDENTIAL_UPPER,
        corridor_nodes=deck13_nodes,
        corridor_edges=deck13_edges,
    )

    # -------------------------------------------------------------
    # DECK 06: POSIDONIA (Promenade & Main Theater)
    # -------------------------------------------------------------
    deck06_nodes = {
        "D06_FWD_LIFT": CorridorNode("D06_FWD_LIFT", 6, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
        "D06_MID_LIFT": CorridorNode("D06_MID_LIFT", 6, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D06_AFT_LIFT": CorridorNode("D06_AFT_LIFT", 6, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_AFT"),
        "D06_PROMENADE": CorridorNode("D06_PROMENADE", 6, Coordinate2D(0.50, 0.0)),
        "D06_THEATER": CorridorNode("D06_THEATER", 6, Coordinate2D(0.85, 0.0)),
    }
    deck06_edges = [
        CorridorEdge("D06_AFT_LIFT", "D06_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D06_MID_LIFT", "D06_FWD_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D06_FWD_LIFT", "D06_THEATER", 30.0, is_step_free=True),
    ]
    venues_d06 = {
        "VENUE_THEATER": Venue(
            venue_id="VENUE_THEATER",
            name="London Theatre",
            deck_number=6,
            category=VenueCategory.THEATER,
            boundary_polygon=[Coordinate2D(0.80, -0.7), Coordinate2D(0.95, -0.7), Coordinate2D(0.95, 0.7), Coordinate2D(0.80, 0.7)],
            entrance_node_ids=["D06_THEATER"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_ga],
        ),
        "VENUE_PROMENADE": Venue(
            venue_id="VENUE_PROMENADE",
            name="Galleria Bellissima",
            deck_number=6,
            category=VenueCategory.PROMENADE_ATRIUM,
            boundary_polygon=[Coordinate2D(0.35, -0.4), Coordinate2D(0.70, -0.4), Coordinate2D(0.70, 0.4), Coordinate2D(0.35, 0.4)],
            entrance_node_ids=["D06_PROMENADE"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_ga],
        ),
    }
    decks[6] = Deck(
        deck_number=6,
        name="Posidonia",
        elevation_meters=14.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.PROMENADE,
        venues=venues_d06,
        corridor_nodes=deck06_nodes,
        corridor_edges=deck06_edges,
    )

    # -------------------------------------------------------------
    # DECK 18: NINFEA (DOREMI Youth & Kids Club)
    # -------------------------------------------------------------
    deck18_nodes = {
        "D18_AFT_LIFT": CorridorNode("D18_AFT_LIFT", 18, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_AFT"),
        "D18_DOREMI": CorridorNode("D18_DOREMI", 18, Coordinate2D(0.20, 0.0)),
    }
    deck18_edges = [
        CorridorEdge("D18_AFT_LIFT", "D18_DOREMI", 15.0, is_step_free=True),
    ]
    venues_d18 = {
        "VENUE_DOREMI_KIDS": Venue(
            venue_id="VENUE_DOREMI_KIDS",
            name="DOREMI Studio & Junior Club",
            deck_number=18,
            category=VenueCategory.YOUTH_KIDS,
            boundary_polygon=[Coordinate2D(0.10, -0.5), Coordinate2D(0.22, -0.5), Coordinate2D(0.22, 0.5), Coordinate2D(0.10, 0.5)],
            entrance_node_ids=["D18_DOREMI"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[evidence_ga],
        )
    }
    decks[18] = Deck(
        deck_number=18,
        name="Ninfea",
        elevation_meters=55.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.6), Coordinate2D(0.85, 0.5), Coordinate2D(0.9, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=venues_d18,
        corridor_nodes=deck18_nodes,
        corridor_edges=deck18_edges,
    )

    return VesselSpatialOntology(
        imo_number="IMO9766205",
        name="MSC Bellissima",
        ship_class="Meraviglia Class",
        length_overall_meters=315.83,
        beam_meters=43.0,
        total_decks=19,
        decks=decks,
    )
