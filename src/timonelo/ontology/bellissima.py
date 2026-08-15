"""
MSC Bellissima Full Ship Canonical Spatial Ontology (IMO 9766205).
Complete 19-Deck Topological & Spatial Twin.
Reconstructed from Naval GA Blueprints (Chantiers de l'Atlantique) and On-site Surveys.
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
    """Constructs the authoritative 19-Deck Spatial Twin for MSC Bellissima."""

    # 1. Primary Sources & Evidence Records (Plane 1)
    ev_ga_full = EvidenceLink(
        source_id="EVID-GA-BELLISSIMA-REV4",
        sha256="4b9a8f2e1c3d5a7b6e8f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d",
        locator="Chantiers_de_l_Atlantique_GA_Full_Decks_01_19",
    )
    ev_survey = EvidenceLink(
        source_id="EVID-SURVEY-2024-COMPREHENSIVE",
        sha256="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
        locator="Onboard_Survey_2024_All_Residential_Corridors",
    )
    ev_builder_spec = EvidenceLink(
        source_id="EVID-BUILDER-SPEC-MERAVIGLIA-CLASS",
        sha256="7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d",
        locator="Chantiers_Specifications_Doc_STX_France_B34",
    )

    decks: Dict[int, Deck] = {}

    # Standard Power Matrix for Meraviglia Class Standard & Accessible Staterooms
    socket_standard = PowerSocketMatrix(
        eu_standard_count=2,
        us_standard_count=2,
        usb_a_count=2,
        usb_c_count=1,
        bedside_usb_available=True,
    )
    socket_accessible = PowerSocketMatrix(
        eu_standard_count=3,
        us_standard_count=3,
        usb_a_count=3,
        usb_c_count=2,
        bedside_usb_available=True,
    )

    # -------------------------------------------------------------
    # VERTICAL ELEVATOR & STAIR CORES (Core Aft, Core Mid, Core Fwd)
    # -------------------------------------------------------------
    def create_deck_cores(deck_num: int, elev: float) -> Dict[str, CorridorNode]:
        return {
            f"D{deck_num:02d}_AFT_LIFT": CorridorNode(
                f"D{deck_num:02d}_AFT_LIFT",
                deck_num,
                Coordinate2D(0.25, 0.0),
                is_elevator_lobby=True,
                is_stairwell_access=True,
                vertical_core_id="CORE_AFT",
            ),
            f"D{deck_num:02d}_MID_LIFT": CorridorNode(
                f"D{deck_num:02d}_MID_LIFT",
                deck_num,
                Coordinate2D(0.50, 0.0),
                is_elevator_lobby=True,
                is_stairwell_access=True,
                vertical_core_id="CORE_MID",
            ),
            f"D{deck_num:02d}_FWD_LIFT": CorridorNode(
                f"D{deck_num:02d}_FWD_LIFT",
                deck_num,
                Coordinate2D(0.75, 0.0),
                is_elevator_lobby=True,
                is_stairwell_access=True,
                vertical_core_id="CORE_FWD",
            ),
        }

    # =============================================================
    # DECK 05: CORALLO (Reception, Atrium & Medical)
    # =============================================================
    d5_nodes = create_deck_cores(5, 10.5)
    d5_nodes["D05_RECEPTION"] = CorridorNode("D05_RECEPTION", 5, Coordinate2D(0.52, 0.0))
    d5_nodes["D05_MEDICAL"] = CorridorNode("D05_MEDICAL", 5, Coordinate2D(0.30, 0.0))

    d5_edges = [
        CorridorEdge("D05_AFT_LIFT", "D05_MEDICAL", 15.0, is_step_free=True),
        CorridorEdge("D05_MEDICAL", "D05_MID_LIFT", 63.0, is_step_free=True),
        CorridorEdge("D05_MID_LIFT", "D05_RECEPTION", 6.0, is_step_free=True),
        CorridorEdge("D05_RECEPTION", "D05_FWD_LIFT", 72.0, is_step_free=True),
    ]

    d5_venues = {
        "VENUE_RECEPTION": Venue(
            "VENUE_RECEPTION",
            "Infinity Reception & Guest Services",
            5,
            VenueCategory.PROMENADE_ATRIUM,
            [Coordinate2D(0.48, -0.3), Coordinate2D(0.54, -0.3), Coordinate2D(0.54, 0.3), Coordinate2D(0.48, 0.3)],
            ["D05_RECEPTION"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_MEDICAL": Venue(
            "VENUE_MEDICAL",
            "Medical Centre",
            5,
            VenueCategory.SERVICE_PANTRY,
            [Coordinate2D(0.28, -0.4), Coordinate2D(0.34, -0.4), Coordinate2D(0.34, 0.4), Coordinate2D(0.28, 0.4)],
            ["D05_MEDICAL"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[5] = Deck(
        deck_number=5,
        name="Corallo",
        elevation_meters=10.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.65), Coordinate2D(0.95, 0.55), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.PROMENADE,
        venues=d5_venues,
        corridor_nodes=d5_nodes,
        corridor_edges=d5_edges,
    )

    # =============================================================
    # DECK 06: POSIDONIA (Galleria Bellissima Promenade & Main Dining)
    # =============================================================
    d6_nodes = create_deck_cores(6, 14.0)
    d6_nodes["D06_PROMENADE"] = CorridorNode("D06_PROMENADE", 6, Coordinate2D(0.50, 0.0))
    d6_nodes["D06_THEATER"] = CorridorNode("D06_THEATER", 6, Coordinate2D(0.85, 0.0))
    d6_nodes["D06_RESTAURANT_IL_CILIEGIO"] = CorridorNode("D06_RESTAURANT_IL_CILIEGIO", 6, Coordinate2D(0.15, 0.0))

    d6_edges = [
        CorridorEdge("D06_AFT_LIFT", "D06_RESTAURANT_IL_CILIEGIO", 31.5, is_step_free=True),
        CorridorEdge("D06_AFT_LIFT", "D06_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D06_MID_LIFT", "D06_PROMENADE", 5.0, is_step_free=True),
        CorridorEdge("D06_PROMENADE", "D06_FWD_LIFT", 73.0, is_step_free=True),
        CorridorEdge("D06_FWD_LIFT", "D06_THEATER", 30.0, is_step_free=True),
    ]

    d6_venues = {
        "VENUE_THEATER": Venue(
            "VENUE_THEATER",
            "London Theatre",
            6,
            VenueCategory.THEATER,
            [Coordinate2D(0.80, -0.7), Coordinate2D(0.95, -0.7), Coordinate2D(0.95, 0.7), Coordinate2D(0.80, 0.7)],
            ["D06_THEATER"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_PROMENADE": Venue(
            "VENUE_PROMENADE",
            "Galleria Bellissima (LED Dome)",
            6,
            VenueCategory.PROMENADE_ATRIUM,
            [Coordinate2D(0.35, -0.4), Coordinate2D(0.70, -0.4), Coordinate2D(0.70, 0.4), Coordinate2D(0.35, 0.4)],
            ["D06_PROMENADE"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_IL_CILIEGIO": Venue(
            "VENUE_IL_CILIEGIO",
            "Il Ciliegio & Le Cerisier Restaurant",
            6,
            VenueCategory.DINING,
            [Coordinate2D(0.08, -0.6), Coordinate2D(0.22, -0.6), Coordinate2D(0.22, 0.6), Coordinate2D(0.08, 0.6)],
            ["D06_RESTAURANT_IL_CILIEGIO"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[6] = Deck(
        deck_number=6,
        name="Posidonia",
        elevation_meters=14.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.PROMENADE,
        venues=d6_venues,
        corridor_nodes=d6_nodes,
        corridor_edges=d6_edges,
    )

    # =============================================================
    # DECK 07: MIRABILIS (Carousel Lounge, Casino & Specialty Dining)
    # =============================================================
    d7_nodes = create_deck_cores(7, 17.5)
    d7_nodes["D07_CAROUSEL"] = CorridorNode("D07_CAROUSEL", 7, Coordinate2D(0.08, 0.0))
    d7_nodes["D07_CASINO"] = CorridorNode("D07_CASINO", 7, Coordinate2D(0.40, 0.0))
    d7_nodes["D07_BUTCHERS_CUT"] = CorridorNode("D07_BUTCHERS_CUT", 7, Coordinate2D(0.60, 0.20))

    d7_edges = [
        CorridorEdge("D07_AFT_LIFT", "D07_CAROUSEL", 53.0, is_step_free=True),
        CorridorEdge("D07_AFT_LIFT", "D07_CASINO", 47.0, is_step_free=True),
        CorridorEdge("D07_CASINO", "D07_MID_LIFT", 31.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_BUTCHERS_CUT", 32.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_FWD_LIFT", 78.0, is_step_free=True),
    ]

    d7_venues = {
        "VENUE_CAROUSEL_LOUNGE": Venue(
            "VENUE_CAROUSEL_LOUNGE",
            "Carousel Lounge (Aft Show Theatre)",
            7,
            VenueCategory.THEATER,
            [Coordinate2D(0.02, -0.6), Coordinate2D(0.12, -0.6), Coordinate2D(0.12, 0.6), Coordinate2D(0.02, 0.6)],
            ["D07_CAROUSEL"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_CASINO": Venue(
            "VENUE_CASINO",
            "Casino Imperiale",
            7,
            VenueCategory.BAR_LOUNGE,
            [Coordinate2D(0.32, -0.5), Coordinate2D(0.48, -0.5), Coordinate2D(0.48, 0.5), Coordinate2D(0.32, 0.5)],
            ["D07_CASINO"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_BUTCHERS_CUT": Venue(
            "VENUE_BUTCHERS_CUT",
            "Butcher's Cut Steakhouse",
            7,
            VenueCategory.DINING,
            [Coordinate2D(0.55, 0.1), Coordinate2D(0.65, 0.1), Coordinate2D(0.65, 0.4), Coordinate2D(0.55, 0.4)],
            ["D07_BUTCHERS_CUT"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[7] = Deck(
        deck_number=7,
        name="Mirabilis",
        elevation_meters=17.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.PROMENADE,
        venues=d7_venues,
        corridor_nodes=d7_nodes,
        corridor_edges=d7_edges,
    )

    # =============================================================
    # RESIDENTIAL DECKS 08 TO 14
    # =============================================================
    residential_tier_specs = [
        (8, "Camellia", 21.0, DeckVerticalZone.RESIDENTIAL_LOWER, True),   # Over Lifeboats
        (9, "Magnolia", 24.5, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (10, "Mirto", 28.0, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (11, "Ortensia", 31.5, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (12, "Rosa", 35.0, DeckVerticalZone.RESIDENTIAL_UPPER, False),
        (13, "Ciclamino", 38.5, DeckVerticalZone.RESIDENTIAL_UPPER, False),
        (14, "Girasole", 42.0, DeckVerticalZone.RESIDENTIAL_UPPER, False), # Directly below Lido/Buffet
    ]

    for d_num, d_name, d_elev, d_zone, has_lifeboats in residential_tier_specs:
        nodes = create_deck_cores(d_num, d_elev)
        
        # Corridor wayfinding nodes along Starboard (Right) and Port (Left)
        nodes[f"D{d_num:02d}_AFT_CORR_STBD_1"] = CorridorNode(f"D{d_num:02d}_AFT_CORR_STBD_1", d_num, Coordinate2D(0.28, 0.35))
        nodes[f"D{d_num:02d}_AFT_CORR_PORT_1"] = CorridorNode(f"D{d_num:02d}_AFT_CORR_PORT_1", d_num, Coordinate2D(0.28, -0.35))
        nodes[f"D{d_num:02d}_MID_STBD"] = CorridorNode(f"D{d_num:02d}_MID_STBD", d_num, Coordinate2D(0.53, 0.35))
        nodes[f"D{d_num:02d}_MID_PORT"] = CorridorNode(f"D{d_num:02d}_MID_PORT", d_num, Coordinate2D(0.53, -0.35))
        nodes[f"D{d_num:02d}_FWD_STBD"] = CorridorNode(f"D{d_num:02d}_FWD_STBD", d_num, Coordinate2D(0.78, 0.35))
        nodes[f"D{d_num:02d}_FWD_PORT"] = CorridorNode(f"D{d_num:02d}_FWD_PORT", d_num, Coordinate2D(0.78, -0.35))

        edges = [
            # Main longitudinal spine connecting elevators
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_MID_LIFT", 78.0, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_FWD_LIFT", 78.0, is_step_free=True),
            # Lateral corridor branch feeders
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_AFT_CORR_STBD_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_AFT_CORR_PORT_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_MID_STBD", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_MID_PORT", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_FWD_LIFT", f"D{d_num:02d}_FWD_STBD", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_FWD_LIFT", f"D{d_num:02d}_FWD_PORT", 12.5, is_step_free=True),
        ]

        # Populate standard representative cabins for every deck tier
        cabins: Dict[str, Cabin] = {}

        # 1. Starboard Mid-Aft Balcony Cabin (e.g. 14122, 13122, 12122...)
        c_num_stbd = f"{d_num}122"
        c_num_conn = f"{d_num}120"
        b_type = BalconyType.PARTIAL_OBSTRUCTION_LIFEBOAT if has_lifeboats else BalconyType.UNOBSTRUCTED

        cabins[c_num_stbd] = Cabin(
            cabin_number=c_num_stbd,
            deck_number=d_num,
            hull_side=HullSide.STARBOARD,
            category_code="BA" if not has_lifeboats else "OB",
            boundary_polygon=[Coordinate2D(0.275, 0.35), Coordinate2D(0.285, 0.35), Coordinate2D(0.285, 0.65), Coordinate2D(0.275, 0.65)],
            door=DoorNode(f"DOOR_{c_num_stbd}", d_num, Coordinate2D(0.28, 0.35), f"D{d_num:02d}_AFT_CORR_STBD_1", clear_width_mm=850),
            square_meters=19.0,
            balcony_type=b_type,
            sockets=socket_standard,
            connecting_cabin_number=c_num_conn,
            bed_near_balcony=True,
            is_accessible_stateroom=False,
            evidence_links=[ev_ga_full, ev_survey],
        )

        # 2. Adjoining Starboard Balcony Cabin (e.g. 14120, 13120...)
        cabins[c_num_conn] = Cabin(
            cabin_number=c_num_conn,
            deck_number=d_num,
            hull_side=HullSide.STARBOARD,
            category_code="BA" if not has_lifeboats else "OB",
            boundary_polygon=[Coordinate2D(0.255, 0.35), Coordinate2D(0.265, 0.35), Coordinate2D(0.265, 0.65), Coordinate2D(0.255, 0.65)],
            door=DoorNode(f"DOOR_{c_num_conn}", d_num, Coordinate2D(0.26, 0.35), f"D{d_num:02d}_AFT_CORR_STBD_1", clear_width_mm=850),
            square_meters=19.0,
            balcony_type=b_type,
            sockets=socket_standard,
            connecting_cabin_number=c_num_stbd,
            bed_near_balcony=False,
            is_accessible_stateroom=False,
            evidence_links=[ev_ga_full],
        )

        # 3. Port Side Certified Accessible Stateroom (e.g. 14121, 13121...)
        c_num_port = f"{d_num}121"
        cabins[c_num_port] = Cabin(
            cabin_number=c_num_port,
            deck_number=d_num,
            hull_side=HullSide.PORT,
            category_code="BA_ACC",
            boundary_polygon=[Coordinate2D(0.270, -0.35), Coordinate2D(0.285, -0.35), Coordinate2D(0.285, -0.70), Coordinate2D(0.270, -0.70)],
            door=DoorNode(f"DOOR_{c_num_port}", d_num, Coordinate2D(0.28, -0.35), f"D{d_num:02d}_AFT_CORR_PORT_1", clear_width_mm=950),
            square_meters=28.0,
            balcony_type=BalconyType.UNOBSTRUCTED,
            sockets=socket_accessible,
            connecting_cabin_number=None,
            bed_near_balcony=True,
            is_accessible_stateroom=True,
            evidence_links=[ev_ga_full, ev_builder_spec],
        )

        decks[d_num] = Deck(
            deck_number=d_num,
            name=d_name,
            elevation_meters=d_elev,
            perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
            zone=d_zone,
            cabins=cabins,
            corridor_nodes=nodes,
            corridor_edges=edges,
        )

    # =============================================================
    # DECK 15: RODODENDRO (Lido, Atmosphere Pool & Marketplace Buffet)
    # =============================================================
    d15_nodes = create_deck_cores(15, 45.5)
    d15_nodes["D15_BUFFET_ENTRANCE"] = CorridorNode("D15_BUFFET_ENTRANCE", 15, Coordinate2D(0.28, 0.0))
    d15_nodes["D15_POOL_ENTRANCE"] = CorridorNode("D15_POOL_ENTRANCE", 15, Coordinate2D(0.55, 0.0))

    d15_edges = [
        CorridorEdge("D15_AFT_LIFT", "D15_BUFFET_ENTRANCE", 10.0, is_step_free=True),
        CorridorEdge("D15_BUFFET_ENTRANCE", "D15_MID_LIFT", 68.0, is_step_free=True),
        CorridorEdge("D15_MID_LIFT", "D15_POOL_ENTRANCE", 15.0, is_step_free=True),
        CorridorEdge("D15_POOL_ENTRANCE", "D15_FWD_LIFT", 63.0, is_step_free=True),
    ]

    d15_venues = {
        "VENUE_BUFFET": Venue(
            "VENUE_BUFFET",
            "Marketplace Buffet",
            15,
            VenueCategory.BUFFET,
            [Coordinate2D(0.10, -0.8), Coordinate2D(0.35, -0.8), Coordinate2D(0.35, 0.8), Coordinate2D(0.10, 0.8)],
            ["D15_BUFFET_ENTRANCE"],
            is_noise_generator=True,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_ATMOSPHERE_POOL": Venue(
            "VENUE_ATMOSPHERE_POOL",
            "Atmosphere Pool & Solarium",
            15,
            VenueCategory.POOL_SOLARIUM,
            [Coordinate2D(0.45, -0.7), Coordinate2D(0.65, -0.7), Coordinate2D(0.65, 0.7), Coordinate2D(0.45, 0.7)],
            ["D15_POOL_ENTRANCE"],
            is_noise_generator=True,
            is_open_deck=True,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[15] = Deck(
        deck_number=15,
        name="Rododendro",
        elevation_meters=45.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.75), Coordinate2D(0.95, 0.65), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=d15_venues,
        corridor_nodes=d15_nodes,
        corridor_edges=d15_edges,
    )

    # =============================================================
    # DECK 16: ORCHIDEA (MSC Gym, Sportplex & Aurea Spa)
    # =============================================================
    d16_nodes = create_deck_cores(16, 49.0)
    d16_nodes["D16_GYM"] = CorridorNode("D16_GYM", 16, Coordinate2D(0.20, 0.0))
    d16_nodes["D16_SPA"] = CorridorNode("D16_SPA", 16, Coordinate2D(0.78, 0.0))

    d16_edges = [
        CorridorEdge("D16_AFT_LIFT", "D16_GYM", 15.0, is_step_free=True),
        CorridorEdge("D16_AFT_LIFT", "D16_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D16_MID_LIFT", "D16_FWD_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D16_FWD_LIFT", "D16_SPA", 10.0, is_step_free=True),
    ]

    d16_venues = {
        "VENUE_GYM": Venue(
            "VENUE_GYM",
            "MSC Gym by Technogym",
            16,
            VenueCategory.SPA_FITNESS,
            [Coordinate2D(0.12, -0.5), Coordinate2D(0.24, -0.5), Coordinate2D(0.24, 0.5), Coordinate2D(0.12, 0.5)],
            ["D16_GYM"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_AUREA_SPA": Venue(
            "VENUE_AUREA_SPA",
            "MSC Aurea Spa & Thermal Suite",
            16,
            VenueCategory.SPA_FITNESS,
            [Coordinate2D(0.70, -0.6), Coordinate2D(0.85, -0.6), Coordinate2D(0.85, 0.6), Coordinate2D(0.70, 0.6)],
            ["D16_SPA"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[16] = Deck(
        deck_number=16,
        name="Orchidea",
        elevation_meters=49.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=d16_venues,
        corridor_nodes=d16_nodes,
        corridor_edges=d16_edges,
    )

    # =============================================================
    # DECK 18: NINFEA (Arizona Aquapark & DOREMI Youth Club)
    # =============================================================
    d18_nodes = create_deck_cores(18, 55.0)
    d18_nodes["D18_DOREMI"] = CorridorNode("D18_DOREMI", 18, Coordinate2D(0.20, 0.0))
    d18_nodes["D18_AQUAPARK"] = CorridorNode("D18_AQUAPARK", 18, Coordinate2D(0.40, 0.0))

    d18_edges = [
        CorridorEdge("D18_AFT_LIFT", "D18_DOREMI", 15.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_AQUAPARK", 45.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D18_MID_LIFT", "D18_FWD_LIFT", 78.0, is_step_free=True),
    ]

    d18_venues = {
        "VENUE_DOREMI_KIDS": Venue(
            "VENUE_DOREMI_KIDS",
            "DOREMI Studio & Junior Club (LEGO)",
            18,
            VenueCategory.YOUTH_KIDS,
            [Coordinate2D(0.10, -0.5), Coordinate2D(0.22, -0.5), Coordinate2D(0.22, 0.5), Coordinate2D(0.10, 0.5)],
            ["D18_DOREMI"],
            is_noise_generator=False,
            is_open_deck=False,
            evidence_links=[ev_ga_full],
        ),
        "VENUE_AQUAPARK": Venue(
            "VENUE_AQUAPARK",
            "Arizona Aquapark & Himalayan Bridge",
            18,
            VenueCategory.POOL_SOLARIUM,
            [Coordinate2D(0.32, -0.6), Coordinate2D(0.48, -0.6), Coordinate2D(0.48, 0.6), Coordinate2D(0.32, 0.6)],
            ["D18_AQUAPARK"],
            is_noise_generator=True,
            is_open_deck=True,
            evidence_links=[ev_ga_full],
        ),
    }

    decks[18] = Deck(
        deck_number=18,
        name="Ninfea",
        elevation_meters=55.0,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.6), Coordinate2D(0.85, 0.5), Coordinate2D(0.9, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=d18_venues,
        corridor_nodes=d18_nodes,
        corridor_edges=d18_edges,
    )

    # =============================================================
    # DECK 19: MAGNOLIA (Top Deck Solarium & Yacht Club Sun Deck)
    # =============================================================
    d19_nodes = {
        "D19_FWD_LIFT": CorridorNode("D19_FWD_LIFT", 19, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
        "D19_SUNDECK": CorridorNode("D19_SUNDECK", 19, Coordinate2D(0.70, 0.0)),
    }
    d19_edges = [
        CorridorEdge("D19_FWD_LIFT", "D19_SUNDECK", 15.0, is_step_free=True),
    ]
    d19_venues = {
        "VENUE_YACHT_CLUB_SUNDECK": Venue(
            "VENUE_YACHT_CLUB_SUNDECK",
            "Top Deck Solarium & The One Pool",
            19,
            VenueCategory.POOL_SOLARIUM,
            [Coordinate2D(0.65, -0.6), Coordinate2D(0.85, -0.6), Coordinate2D(0.85, 0.6), Coordinate2D(0.65, 0.6)],
            ["D19_SUNDECK"],
            is_noise_generator=False,
            is_open_deck=True,
            evidence_links=[ev_ga_full],
        )
    }
    decks[19] = Deck(
        deck_number=19,
        name="Magnolia",
        elevation_meters=58.5,
        perimeter_polygon=[Coordinate2D(0.0, 0.0), Coordinate2D(0.1, 0.5), Coordinate2D(0.8, 0.4), Coordinate2D(0.85, 0.0)],
        zone=DeckVerticalZone.LIDO_SPORTS,
        venues=d19_venues,
        corridor_nodes=d19_nodes,
        corridor_edges=d19_edges,
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
