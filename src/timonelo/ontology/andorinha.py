"""
Universal River Vessel Ontology: MS Andorinha (ENI 02338573).
Custom-built Douro River luxury vessel operated by Tauck / Scylla AG.
Built 2020 by Vahali Shipyards.
LOA: 80.0m | Beam: 11.4m | Draft: 1.5m | Air Draft: 4.5m | 4 Decks | 42 Staterooms (84 guests).
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


def create_andorinha_ontology() -> VesselSpatialOntology:
    """Builds the complete General Arrangement ontology for MS Andorinha."""

    evidence_andorinha = EvidenceLink(
        source_id="EVID-ANDORINHA-GA-2020",
        sha256=None,
        locator="Tauck_MS_Andorinha_Douro_GA_Plan_Rev1",
    )

    decks: Dict[int, Deck] = {}

    # =========================================================================
    # DECK 01: EMERALD DECK (Lower Riverview Staterooms, Spa & Fitness)
    # =========================================================================
    d01_nodes = {
        "D01_STAIR_FWD": CorridorNode("D01_STAIR_FWD", 1, Coordinate2D(0.70, 0.0), is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        "D01_CORRIDOR_MID": CorridorNode("D01_CORRIDOR_MID", 1, Coordinate2D(0.50, 0.0)),
        "D01_ELEVATOR_MID": CorridorNode("D01_ELEVATOR_MID", 1, Coordinate2D(0.48, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D01_STAIR_AFT": CorridorNode("D01_STAIR_AFT", 1, Coordinate2D(0.30, 0.0), is_stairwell_access=True, vertical_core_id="CORE_AFT"),
    }
    d01_edges = [
        CorridorEdge("D01_STAIR_FWD", "D01_CORRIDOR_MID", 16.0),
        CorridorEdge("D01_CORRIDOR_MID", "D01_ELEVATOR_MID", 1.6),
        CorridorEdge("D01_CORRIDOR_MID", "D01_STAIR_AFT", 16.0),
    ]
    d01_venues = {
        "VENUE_FITNESS": Venue(
            venue_id="VENUE_FITNESS",
            name="Fitness Studio",
            deck_number=1,
            category=VenueCategory.SPA_FITNESS,
            boundary_polygon=[Coordinate2D(0.72, -0.4), Coordinate2D(0.82, -0.4), Coordinate2D(0.82, 0.4), Coordinate2D(0.72, 0.4)],
            entrance_node_ids=["D01_STAIR_FWD"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
        "VENUE_SPA": Venue(
            venue_id="VENUE_SPA",
            name="Wellness Spa & Massage",
            deck_number=1,
            category=VenueCategory.SPA_FITNESS,
            boundary_polygon=[Coordinate2D(0.20, -0.4), Coordinate2D(0.28, -0.4), Coordinate2D(0.28, 0.4), Coordinate2D(0.20, 0.4)],
            entrance_node_ids=["D01_STAIR_AFT"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
    }

    d01_cabins = {}
    # Emerald Deck Cabins: 101, 102, 103, 104 (Category ES, 14m²)
    emerald_specs = [
        ("101", 0.58, -0.28, HullSide.STARBOARD),
        ("102", 0.58, 0.28, HullSide.PORT),
        ("103", 0.42, -0.28, HullSide.STARBOARD),
        ("104", 0.42, 0.28, HullSide.PORT),
    ]
    for num, x, y, side in emerald_specs:
        poly = [Coordinate2D(x - 0.05, y - 0.12), Coordinate2D(x + 0.05, y - 0.12), Coordinate2D(x + 0.05, y + 0.12), Coordinate2D(x - 0.05, y + 0.12)]
        door = DoorNode(f"DOOR_{num}", 1, Coordinate2D(x, 0.0), corridor_snap_node_id="D01_CORRIDOR_MID", clear_width_mm=850)
        d01_cabins[num] = Cabin(
            cabin_number=num,
            deck_number=1,
            hull_side=side,
            category_code="ES",
            boundary_polygon=poly,
            door=door,
            square_meters=14.0,
            balcony_type=BalconyType.NO_BALCONY,
            sockets=PowerSocketMatrix(eu_standard_count=4, us_standard_count=2, usb_a_count=2, usb_c_count=2, bedside_usb_available=True),
            is_accessible_stateroom=False,
            evidence_links=[evidence_andorinha],
        )

    decks[1] = Deck(
        deck_number=1,
        name="Emerald Deck",
        elevation_meters=2.0,
        perimeter_polygon=[Coordinate2D(0.05, -0.5), Coordinate2D(0.95, -0.5), Coordinate2D(0.95, 0.5), Coordinate2D(0.05, 0.5)],
        zone=DeckVerticalZone.HULL_LOWER,
        cabins=d01_cabins,
        venues=d01_venues,
        corridor_nodes=d01_nodes,
        corridor_edges=d01_edges,
    )

    # =========================================================================
    # DECK 02: RUBY DECK (French Balcony Cabins 201–222 & Compass Rose Restaurant)
    # =========================================================================
    d02_nodes = {
        "D02_RESTAURANT_COMPASS": CorridorNode("D02_RESTAURANT_COMPASS", 2, Coordinate2D(0.78, 0.0)),
        "D02_STAIR_FWD": CorridorNode("D02_STAIR_FWD", 2, Coordinate2D(0.70, 0.0), is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        "D02_CORRIDOR_FWD": CorridorNode("D02_CORRIDOR_FWD", 2, Coordinate2D(0.60, 0.0)),
        "D02_ELEVATOR_MID": CorridorNode("D02_ELEVATOR_MID", 2, Coordinate2D(0.48, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D02_CORRIDOR_AFT": CorridorNode("D02_CORRIDOR_AFT", 2, Coordinate2D(0.38, 0.0)),
        "D02_STAIR_AFT": CorridorNode("D02_STAIR_AFT", 2, Coordinate2D(0.24, 0.0), is_stairwell_access=True, vertical_core_id="CORE_AFT"),
    }
    d02_edges = [
        CorridorEdge("D02_RESTAURANT_COMPASS", "D02_STAIR_FWD", 6.4),
        CorridorEdge("D02_STAIR_FWD", "D02_CORRIDOR_FWD", 8.0),
        CorridorEdge("D02_CORRIDOR_FWD", "D02_ELEVATOR_MID", 9.6),
        CorridorEdge("D02_ELEVATOR_MID", "D02_CORRIDOR_AFT", 8.0),
        CorridorEdge("D02_CORRIDOR_AFT", "D02_STAIR_AFT", 11.2),
    ]
    d02_venues = {
        "VENUE_COMPASS_ROSE": Venue(
            venue_id="VENUE_COMPASS_ROSE",
            name="The Compass Rose Restaurant",
            deck_number=2,
            category=VenueCategory.DINING,
            boundary_polygon=[Coordinate2D(0.72, -0.48), Coordinate2D(0.92, -0.48), Coordinate2D(0.92, 0.48), Coordinate2D(0.72, 0.48)],
            entrance_node_ids=["D02_RESTAURANT_COMPASS", "D02_STAIR_FWD"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
        "VENUE_GALLEY": Venue(
            venue_id="VENUE_GALLEY",
            name="Main Galley & Culinary Kitchen",
            deck_number=2,
            category=VenueCategory.SERVICE_PANTRY,
            boundary_polygon=[Coordinate2D(0.08, -0.48), Coordinate2D(0.22, -0.48), Coordinate2D(0.22, 0.48), Coordinate2D(0.08, 0.48)],
            entrance_node_ids=["D02_STAIR_AFT"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
    }

    d02_cabins = {}
    # Ruby Deck Cabins 201–222 (French Balcony, 21m²)
    ruby_pairs = [
        ("201", "202", 0.66, "D02_CORRIDOR_FWD"),
        ("203", "204", 0.62, "D02_CORRIDOR_FWD"),
        ("205", "206", 0.58, "D02_CORRIDOR_FWD"),
        ("207", "208", 0.54, "D02_CORRIDOR_FWD"),
        ("209", "210", 0.50, "D02_ELEVATOR_MID"),
        ("211", "212", 0.46, "D02_ELEVATOR_MID"),
        ("213", "214", 0.42, "D02_CORRIDOR_AFT"),
        ("215", "216", 0.38, "D02_CORRIDOR_AFT"),
        ("217", "218", 0.34, "D02_CORRIDOR_AFT"),
        ("219", "220", 0.30, "D02_STAIR_AFT"),
        ("221", "222", 0.26, "D02_STAIR_AFT"),
    ]
    for odd_num, even_num, x, snap in ruby_pairs:
        p_poly = [Coordinate2D(x - 0.018, 0.12), Coordinate2D(x + 0.018, 0.12), Coordinate2D(x + 0.018, 0.46), Coordinate2D(x - 0.018, 0.46)]
        p_door = DoorNode(f"DOOR_{odd_num}", 2, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=850)
        d02_cabins[odd_num] = Cabin(
            cabin_number=odd_num,
            deck_number=2,
            hull_side=HullSide.PORT,
            category_code="RFB",
            boundary_polygon=p_poly,
            door=p_door,
            square_meters=21.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=4, us_standard_count=2, usb_a_count=2, usb_c_count=2, bedside_usb_available=True),
            is_accessible_stateroom=False,
            evidence_links=[evidence_andorinha],
        )

        s_poly = [Coordinate2D(x - 0.018, -0.46), Coordinate2D(x + 0.018, -0.46), Coordinate2D(x + 0.018, -0.12), Coordinate2D(x - 0.018, -0.12)]
        s_door = DoorNode(f"DOOR_{even_num}", 2, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=850)
        d02_cabins[even_num] = Cabin(
            cabin_number=even_num,
            deck_number=2,
            hull_side=HullSide.STARBOARD,
            category_code="RFB",
            boundary_polygon=s_poly,
            door=s_door,
            square_meters=21.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=4, us_standard_count=2, usb_a_count=2, usb_c_count=2, bedside_usb_available=True),
            is_accessible_stateroom=False,
            evidence_links=[evidence_andorinha],
        )

    decks[2] = Deck(
        deck_number=2,
        name="Ruby Deck",
        elevation_meters=4.8,
        perimeter_polygon=[Coordinate2D(0.05, -0.5), Coordinate2D(0.95, -0.5), Coordinate2D(0.95, 0.5), Coordinate2D(0.05, 0.5)],
        zone=DeckVerticalZone.RESIDENTIAL_LOWER,
        cabins=d02_cabins,
        venues=d02_venues,
        corridor_nodes=d02_nodes,
        corridor_edges=d02_edges,
    )

    # =========================================================================
    # DECK 03: DIAMOND DECK (Suites 301–312, French Balcony 313–316, Panorama Lounge)
    # =========================================================================
    d03_nodes = {
        "D03_PANORAMA_LOUNGE": CorridorNode("D03_PANORAMA_LOUNGE", 3, Coordinate2D(0.82, 0.0)),
        "D03_ATRIUM_RECEPTION": CorridorNode("D03_ATRIUM_RECEPTION", 3, Coordinate2D(0.70, 0.0)),
        "D03_STAIR_FWD": CorridorNode("D03_STAIR_FWD", 3, Coordinate2D(0.68, 0.0), is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        "D03_CORRIDOR_FWD": CorridorNode("D03_CORRIDOR_FWD", 3, Coordinate2D(0.58, 0.0)),
        "D03_ELEVATOR_MID": CorridorNode("D03_ELEVATOR_MID", 3, Coordinate2D(0.48, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_MID"),
        "D03_CORRIDOR_AFT": CorridorNode("D03_CORRIDOR_AFT", 3, Coordinate2D(0.38, 0.0)),
        "D03_STAIR_AFT": CorridorNode("D03_STAIR_AFT", 3, Coordinate2D(0.24, 0.0), is_stairwell_access=True, vertical_core_id="CORE_AFT"),
    }
    d03_edges = [
        CorridorEdge("D03_PANORAMA_LOUNGE", "D03_ATRIUM_RECEPTION", 9.6),
        CorridorEdge("D03_ATRIUM_RECEPTION", "D03_STAIR_FWD", 1.6),
        CorridorEdge("D03_STAIR_FWD", "D03_CORRIDOR_FWD", 8.0),
        CorridorEdge("D03_CORRIDOR_FWD", "D03_ELEVATOR_MID", 8.0),
        CorridorEdge("D03_ELEVATOR_MID", "D03_CORRIDOR_AFT", 8.0),
        CorridorEdge("D03_CORRIDOR_AFT", "D03_STAIR_AFT", 11.2),
    ]
    d03_venues = {
        "VENUE_PANORAMA_LOUNGE": Venue(
            venue_id="VENUE_PANORAMA_LOUNGE",
            name="Panorama Lounge & Bar",
            deck_number=3,
            category=VenueCategory.BAR_LOUNGE,
            boundary_polygon=[Coordinate2D(0.72, -0.48), Coordinate2D(0.96, -0.48), Coordinate2D(0.96, 0.48), Coordinate2D(0.72, 0.48)],
            entrance_node_ids=["D03_PANORAMA_LOUNGE", "D03_ATRIUM_RECEPTION"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
        "VENUE_RECEPTION": Venue(
            venue_id="VENUE_RECEPTION",
            name="Reception Desk & Guest Services Atrium",
            deck_number=3,
            category=VenueCategory.PROMENADE_ATRIUM,
            boundary_polygon=[Coordinate2D(0.66, -0.40), Coordinate2D(0.72, -0.40), Coordinate2D(0.72, 0.40), Coordinate2D(0.66, 0.40)],
            entrance_node_ids=["D03_ATRIUM_RECEPTION"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
    }

    d03_cabins = {}
    # Diamond Deck: 12 Suites (301–312, 28m² Master Suites) + 4 French Balcony (313–316, 21m²)
    diamond_suite_pairs = [
        ("301", "302", 0.62, "D03_CORRIDOR_FWD"),
        ("303", "304", 0.56, "D03_CORRIDOR_FWD"),
        ("305", "306", 0.50, "D03_ELEVATOR_MID"),
        ("307", "308", 0.44, "D03_CORRIDOR_AFT"),
        ("309", "310", 0.38, "D03_CORRIDOR_AFT"),
        ("311", "312", 0.32, "D03_CORRIDOR_AFT"),
    ]
    for odd_num, even_num, x, snap in diamond_suite_pairs:
        p_poly = [Coordinate2D(x - 0.025, 0.12), Coordinate2D(x + 0.025, 0.12), Coordinate2D(x + 0.025, 0.48), Coordinate2D(x - 0.025, 0.48)]
        p_door = DoorNode(f"DOOR_{odd_num}", 3, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=950)
        d03_cabins[odd_num] = Cabin(
            cabin_number=odd_num,
            deck_number=3,
            hull_side=HullSide.PORT,
            category_code="DSU",
            boundary_polygon=p_poly,
            door=p_door,
            square_meters=28.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=6, us_standard_count=4, usb_a_count=4, usb_c_count=4, bedside_usb_available=True),
            is_accessible_stateroom=(odd_num == "301"),
            evidence_links=[evidence_andorinha],
        )

        s_poly = [Coordinate2D(x - 0.025, -0.48), Coordinate2D(x + 0.025, -0.48), Coordinate2D(x + 0.025, -0.12), Coordinate2D(x - 0.025, -0.12)]
        s_door = DoorNode(f"DOOR_{even_num}", 3, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=950)
        d03_cabins[even_num] = Cabin(
            cabin_number=even_num,
            deck_number=3,
            hull_side=HullSide.STARBOARD,
            category_code="DSU",
            boundary_polygon=s_poly,
            door=s_door,
            square_meters=28.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=6, us_standard_count=4, usb_a_count=4, usb_c_count=4, bedside_usb_available=True),
            is_accessible_stateroom=(even_num == "302"),
            evidence_links=[evidence_andorinha],
        )

    # 4 Diamond French Balcony Cabins: 313–316
    diamond_fb_pairs = [
        ("313", "314", 0.27, "D03_STAIR_AFT"),
        ("315", "316", 0.23, "D03_STAIR_AFT"),
    ]
    for odd_num, even_num, x, snap in diamond_fb_pairs:
        p_poly = [Coordinate2D(x - 0.018, 0.12), Coordinate2D(x + 0.018, 0.12), Coordinate2D(x + 0.018, 0.46), Coordinate2D(x - 0.018, 0.46)]
        p_door = DoorNode(f"DOOR_{odd_num}", 3, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=850)
        d03_cabins[odd_num] = Cabin(
            cabin_number=odd_num,
            deck_number=3,
            hull_side=HullSide.PORT,
            category_code="DFB",
            boundary_polygon=p_poly,
            door=p_door,
            square_meters=21.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=4, us_standard_count=2, usb_a_count=2, usb_c_count=2, bedside_usb_available=True),
            is_accessible_stateroom=False,
            evidence_links=[evidence_andorinha],
        )

        s_poly = [Coordinate2D(x - 0.018, -0.46), Coordinate2D(x + 0.018, -0.46), Coordinate2D(x + 0.018, -0.12), Coordinate2D(x - 0.018, -0.12)]
        s_door = DoorNode(f"DOOR_{even_num}", 3, Coordinate2D(x, 0.0), corridor_snap_node_id=snap, clear_width_mm=850)
        d03_cabins[even_num] = Cabin(
            cabin_number=even_num,
            deck_number=3,
            hull_side=HullSide.STARBOARD,
            category_code="DFB",
            boundary_polygon=s_poly,
            door=s_door,
            square_meters=21.0,
            balcony_type=BalconyType.GLASS_TRANSPARENT_RAILING,
            sockets=PowerSocketMatrix(eu_standard_count=4, us_standard_count=2, usb_a_count=2, usb_c_count=2, bedside_usb_available=True),
            is_accessible_stateroom=False,
            evidence_links=[evidence_andorinha],
        )

    decks[3] = Deck(
        deck_number=3,
        name="Diamond Deck",
        elevation_meters=7.6,
        perimeter_polygon=[Coordinate2D(0.05, -0.5), Coordinate2D(0.95, -0.5), Coordinate2D(0.95, 0.5), Coordinate2D(0.05, 0.5)],
        zone=DeckVerticalZone.RESIDENTIAL_UPPER,
        cabins=d03_cabins,
        venues=d03_venues,
        corridor_nodes=d03_nodes,
        corridor_edges=d03_edges,
    )

    # =========================================================================
    # DECK 04: SUN DECK (Open Air Solarium, Pool, Arthur's Bistro, Wheelhouse)
    # =========================================================================
    d04_nodes = {
        "D04_STAIR_FWD": CorridorNode("D04_STAIR_FWD", 4, Coordinate2D(0.68, 0.0), is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        "D04_SUN_DECK_MID": CorridorNode("D04_SUN_DECK_MID", 4, Coordinate2D(0.50, 0.0)),
        "D04_ARTHURS_BISTRO": CorridorNode("D04_ARTHURS_BISTRO", 4, Coordinate2D(0.32, 0.0)),
        "D04_STAIR_AFT": CorridorNode("D04_STAIR_AFT", 4, Coordinate2D(0.24, 0.0), is_stairwell_access=True, vertical_core_id="CORE_AFT"),
    }
    d04_edges = [
        CorridorEdge("D04_STAIR_FWD", "D04_SUN_DECK_MID", 14.4),
        CorridorEdge("D04_SUN_DECK_MID", "D04_ARTHURS_BISTRO", 14.4),
        CorridorEdge("D04_ARTHURS_BISTRO", "D04_STAIR_AFT", 6.4),
    ]
    d04_venues = {
        "VENUE_ARTHURS_BISTRO": Venue(
            venue_id="VENUE_ARTHURS_BISTRO",
            name="Arthur's Bistro & Open-Air Grill",
            deck_number=4,
            category=VenueCategory.DINING,
            boundary_polygon=[Coordinate2D(0.24, -0.45), Coordinate2D(0.38, -0.45), Coordinate2D(0.38, 0.45), Coordinate2D(0.24, 0.45)],
            entrance_node_ids=["D04_ARTHURS_BISTRO"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
        "VENUE_SUN_POOL": Venue(
            venue_id="VENUE_SUN_POOL",
            name="Sun Deck Pool & Balinese Day Beds",
            deck_number=4,
            category=VenueCategory.POOL_SOLARIUM,
            boundary_polygon=[Coordinate2D(0.42, -0.48), Coordinate2D(0.65, -0.48), Coordinate2D(0.65, 0.48), Coordinate2D(0.42, 0.48)],
            entrance_node_ids=["D04_SUN_DECK_MID"],
            is_noise_generator=True,
            is_open_deck=True,
            evidence_links=[evidence_andorinha],
        ),
        "VENUE_WHEELHOUSE": Venue(
            venue_id="VENUE_WHEELHOUSE",
            name="Navigation Bridge & Retractable Wheelhouse",
            deck_number=4,
            category=VenueCategory.SERVICE_PANTRY,
            boundary_polygon=[Coordinate2D(0.70, -0.30), Coordinate2D(0.78, -0.30), Coordinate2D(0.78, 0.30), Coordinate2D(0.70, 0.30)],
            entrance_node_ids=["D04_STAIR_FWD"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[evidence_andorinha],
        ),
    }

    decks[4] = Deck(
        deck_number=4,
        name="Sun Deck",
        elevation_meters=10.4,
        perimeter_polygon=[Coordinate2D(0.05, -0.5), Coordinate2D(0.95, -0.5), Coordinate2D(0.95, 0.5), Coordinate2D(0.05, 0.5)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        cabins={},
        venues=d04_venues,
        corridor_nodes=d04_nodes,
        corridor_edges=d04_edges,
    )

    return VesselSpatialOntology(
        imo_number="ENI02338573",
        name="MS Andorinha",
        ship_class="Douro River Class",
        length_overall_meters=80.0,
        beam_meters=11.4,
        total_decks=4,
        decks=decks,
    )
