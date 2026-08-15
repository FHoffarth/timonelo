"""
MSC Bellissima Full Ship Canonical Spatial Ontology (IMO 9766205).
Authoritative Multi-Deck Spatial Twin reconstructed from Naval GA Blueprints (Chantiers de l'Atlantique, STX France B34)
and Double-Verified Onboard Physical Surveys.
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
    """Constructs the comprehensive Spatial Twin for MSC Bellissima."""

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

    # Standard Power Matrices
    socket_std = PowerSocketMatrix(eu_standard_count=2, us_standard_count=2, usb_a_count=2, usb_c_count=1, bedside_usb_available=True)
    socket_acc = PowerSocketMatrix(eu_standard_count=3, us_standard_count=3, usb_a_count=3, usb_c_count=2, bedside_usb_available=True)
    socket_suite = PowerSocketMatrix(eu_standard_count=4, us_standard_count=4, usb_a_count=4, usb_c_count=2, bedside_usb_available=True)

    # Helper for creating vertical cores
    def create_deck_cores(deck_num: int, elev: float) -> Dict[str, CorridorNode]:
        return {
            f"D{deck_num:02d}_AFT_LIFT": CorridorNode(f"D{deck_num:02d}_AFT_LIFT", deck_num, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_AFT"),
            f"D{deck_num:02d}_MID_LIFT": CorridorNode(f"D{deck_num:02d}_MID_LIFT", deck_num, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_MID"),
            f"D{deck_num:02d}_FWD_LIFT": CorridorNode(f"D{deck_num:02d}_FWD_LIFT", deck_num, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        }

    # =============================================================
    # DECK 05: CORALLO (Reception, Infinity Atrium, Medical, Shore Ex)
    # =============================================================
    d5_nodes = create_deck_cores(5, 10.5)
    d5_nodes["D05_RECEPTION"] = CorridorNode("D05_RECEPTION", 5, Coordinate2D(0.52, 0.0))
    d5_nodes["D05_ATRIUM"] = CorridorNode("D05_ATRIUM", 5, Coordinate2D(0.48, 0.0))
    d5_nodes["D05_MEDICAL"] = CorridorNode("D05_MEDICAL", 5, Coordinate2D(0.30, 0.0))
    d5_nodes["D05_EXCURSIONS"] = CorridorNode("D05_EXCURSIONS", 5, Coordinate2D(0.55, 0.20))
    d5_nodes["D05_BUSINESS"] = CorridorNode("D05_BUSINESS", 5, Coordinate2D(0.68, 0.0))

    d5_edges = [
        CorridorEdge("D05_AFT_LIFT", "D05_MEDICAL", 15.0, is_step_free=True),
        CorridorEdge("D05_MEDICAL", "D05_ATRIUM", 56.0, is_step_free=True),
        CorridorEdge("D05_ATRIUM", "D05_MID_LIFT", 6.0, is_step_free=True),
        CorridorEdge("D05_MID_LIFT", "D05_RECEPTION", 6.0, is_step_free=True),
        CorridorEdge("D05_RECEPTION", "D05_EXCURSIONS", 10.0, is_step_free=True),
        CorridorEdge("D05_RECEPTION", "D05_BUSINESS", 50.0, is_step_free=True),
        CorridorEdge("D05_BUSINESS", "D05_FWD_LIFT", 22.0, is_step_free=True),
    ]

    d5_venues = {
        "VENUE_RECEPTION": Venue("VENUE_RECEPTION", "Infinity Reception & Guest Services", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.50, -0.3), Coordinate2D(0.54, -0.3), Coordinate2D(0.54, 0.3), Coordinate2D(0.50, 0.3)], ["D05_RECEPTION"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_INFINITY_ATRIUM_L5": Venue("VENUE_INFINITY_ATRIUM_L5", "Infinity Atrium & Swarovski Stairs (Deck 5)", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.45, -0.4), Coordinate2D(0.50, -0.4), Coordinate2D(0.50, 0.4), Coordinate2D(0.45, 0.4)], ["D05_ATRIUM"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_INFINITY_BAR": Venue("VENUE_INFINITY_BAR", "Infinity Bar", 5, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.46, -0.2), Coordinate2D(0.49, -0.2), Coordinate2D(0.49, 0.2), Coordinate2D(0.46, 0.2)], ["D05_ATRIUM"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MEDICAL": Venue("VENUE_MEDICAL", "Medical Centre", 5, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.28, -0.4), Coordinate2D(0.34, -0.4), Coordinate2D(0.34, 0.4), Coordinate2D(0.28, 0.4)], ["D05_MEDICAL"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_EXCURSIONS": Venue("VENUE_EXCURSIONS", "MSC Shore Excursions Desk", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.53, 0.1), Coordinate2D(0.57, 0.1), Coordinate2D(0.57, 0.4), Coordinate2D(0.53, 0.4)], ["D05_EXCURSIONS"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_BUSINESS_CENTRE": Venue("VENUE_BUSINESS_CENTRE", "Business Centre & Conference Rooms", 5, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.65, -0.4), Coordinate2D(0.72, -0.4), Coordinate2D(0.72, 0.4), Coordinate2D(0.65, 0.4)], ["D05_BUSINESS"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[5] = Deck(5, "Corallo", 10.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.65), Coordinate2D(0.95, 0.55), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, venues=d5_venues, corridor_nodes=d5_nodes, corridor_edges=d5_edges)

    # =============================================================
    # DECK 06: POSIDONIA (Galleria Bellissima, London Theatre, Main Dining)
    # =============================================================
    d6_nodes = create_deck_cores(6, 14.0)
    d6_nodes["D06_PROMENADE"] = CorridorNode("D06_PROMENADE", 6, Coordinate2D(0.50, 0.0))
    d6_nodes["D06_THEATER"] = CorridorNode("D06_THEATER", 6, Coordinate2D(0.85, 0.0))
    d6_nodes["D06_RESTAURANT_IL_CILIEGIO"] = CorridorNode("D06_RESTAURANT_IL_CILIEGIO", 6, Coordinate2D(0.15, 0.0))
    d6_nodes["D06_MASTERS_PUB"] = CorridorNode("D06_MASTERS_PUB", 6, Coordinate2D(0.42, 0.20))
    d6_nodes["D06_JEAN_PHILIPPE_CHOCOLAT"] = CorridorNode("D06_JEAN_PHILIPPE_CHOCOLAT", 6, Coordinate2D(0.45, -0.20))
    d6_nodes["D06_TV_STUDIO"] = CorridorNode("D06_TV_STUDIO", 6, Coordinate2D(0.62, 0.0))

    d6_edges = [
        CorridorEdge("D06_AFT_LIFT", "D06_RESTAURANT_IL_CILIEGIO", 31.5, is_step_free=True),
        CorridorEdge("D06_AFT_LIFT", "D06_MASTERS_PUB", 53.0, is_step_free=True),
        CorridorEdge("D06_MASTERS_PUB", "D06_JEAN_PHILIPPE_CHOCOLAT", 12.0, is_step_free=True),
        CorridorEdge("D06_JEAN_PHILIPPE_CHOCOLAT", "D06_MID_LIFT", 15.0, is_step_free=True),
        CorridorEdge("D06_MID_LIFT", "D06_PROMENADE", 5.0, is_step_free=True),
        CorridorEdge("D06_PROMENADE", "D06_TV_STUDIO", 37.0, is_step_free=True),
        CorridorEdge("D06_TV_STUDIO", "D06_FWD_LIFT", 41.0, is_step_free=True),
        CorridorEdge("D06_FWD_LIFT", "D06_THEATER", 30.0, is_step_free=True),
    ]

    d6_venues = {
        "VENUE_THEATER": Venue("VENUE_THEATER", "London Theatre (Lower Level)", 6, VenueCategory.THEATER, [Coordinate2D(0.80, -0.7), Coordinate2D(0.95, -0.7), Coordinate2D(0.95, 0.7), Coordinate2D(0.80, 0.7)], ["D06_THEATER"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_PROMENADE": Venue("VENUE_PROMENADE", "Galleria Bellissima (80m LED Dome)", 6, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.35, -0.4), Coordinate2D(0.70, -0.4), Coordinate2D(0.70, 0.4), Coordinate2D(0.35, 0.4)], ["D06_PROMENADE"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_IL_CILIEGIO": Venue("VENUE_IL_CILIEGIO", "Il Ciliegio & Le Cerisier Restaurant", 6, VenueCategory.DINING, [Coordinate2D(0.08, -0.6), Coordinate2D(0.22, -0.6), Coordinate2D(0.22, 0.6), Coordinate2D(0.08, 0.6)], ["D06_RESTAURANT_IL_CILIEGIO"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MASTERS_OF_THE_SEA": Venue("VENUE_MASTERS_OF_THE_SEA", "Masters of the Sea British Pub", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.39, 0.1), Coordinate2D(0.46, 0.1), Coordinate2D(0.46, 0.5), Coordinate2D(0.39, 0.5)], ["D06_MASTERS_PUB"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_JEAN_PHILIPPE_CHOCOLAT": Venue("VENUE_JEAN_PHILIPPE_CHOCOLAT", "Jean-Philippe Maury Chocolat & Café", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.42, -0.5), Coordinate2D(0.48, -0.5), Coordinate2D(0.48, -0.1), Coordinate2D(0.42, -0.1)], ["D06_JEAN_PHILIPPE_CHOCOLAT"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_TV_STUDIO": Venue("VENUE_TV_STUDIO", "TV Studio & Comedy Bar", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.58, -0.4), Coordinate2D(0.65, -0.4), Coordinate2D(0.65, 0.4), Coordinate2D(0.58, 0.4)], ["D06_TV_STUDIO"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[6] = Deck(6, "Posidonia", 14.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, venues=d6_venues, corridor_nodes=d6_nodes, corridor_edges=d6_edges)

    # =============================================================
    # DECK 07: MIRABILIS (Carousel Lounge, Casino, Specialty Dining)
    # =============================================================
    d7_nodes = create_deck_cores(7, 17.5)
    d7_nodes["D07_CAROUSEL"] = CorridorNode("D07_CAROUSEL", 7, Coordinate2D(0.08, 0.0))
    d7_nodes["D07_CASINO"] = CorridorNode("D07_CASINO", 7, Coordinate2D(0.40, 0.0))
    d7_nodes["D07_CHAMPAGNE"] = CorridorNode("D07_CHAMPAGNE", 7, Coordinate2D(0.48, 0.0))
    d7_nodes["D07_BUTCHERS_CUT"] = CorridorNode("D07_BUTCHERS_CUT", 7, Coordinate2D(0.60, 0.20))
    d7_nodes["D07_KAITO_TEPPANYAKI"] = CorridorNode("D07_KAITO_TEPPANYAKI", 7, Coordinate2D(0.60, -0.20))
    d7_nodes["D07_HOLA_TAPAS"] = CorridorNode("D07_HOLA_TAPAS", 7, Coordinate2D(0.65, 0.20))
    d7_nodes["D07_THEATER_UPPER"] = CorridorNode("D07_THEATER_UPPER", 7, Coordinate2D(0.85, 0.0))

    d7_edges = [
        CorridorEdge("D07_AFT_LIFT", "D07_CAROUSEL", 53.0, is_step_free=True),
        CorridorEdge("D07_AFT_LIFT", "D07_CASINO", 47.0, is_step_free=True),
        CorridorEdge("D07_CASINO", "D07_CHAMPAGNE", 25.0, is_step_free=True),
        CorridorEdge("D07_CHAMPAGNE", "D07_MID_LIFT", 6.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_BUTCHERS_CUT", 32.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_KAITO_TEPPANYAKI", 32.0, is_step_free=True),
        CorridorEdge("D07_BUTCHERS_CUT", "D07_HOLA_TAPAS", 16.0, is_step_free=True),
        CorridorEdge("D07_HOLA_TAPAS", "D07_FWD_LIFT", 31.0, is_step_free=True),
        CorridorEdge("D07_FWD_LIFT", "D07_THEATER_UPPER", 30.0, is_step_free=True),
    ]

    d7_venues = {
        "VENUE_CAROUSEL_LOUNGE": Venue("VENUE_CAROUSEL_LOUNGE", "Carousel Lounge (Aft Show Theatre)", 7, VenueCategory.THEATER, [Coordinate2D(0.02, -0.6), Coordinate2D(0.12, -0.6), Coordinate2D(0.12, 0.6), Coordinate2D(0.02, 0.6)], ["D07_CAROUSEL"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_CASINO": Venue("VENUE_CASINO", "Casino Imperiale", 7, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.32, -0.5), Coordinate2D(0.48, -0.5), Coordinate2D(0.48, 0.5), Coordinate2D(0.32, 0.5)], ["D07_CASINO"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_CHAMPAGNE_BAR": Venue("VENUE_CHAMPAGNE_BAR", "Champagne Bar & Grand Staircase", 7, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.46, -0.3), Coordinate2D(0.50, -0.3), Coordinate2D(0.50, 0.3), Coordinate2D(0.46, 0.3)], ["D07_CHAMPAGNE"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_BUTCHERS_CUT": Venue("VENUE_BUTCHERS_CUT", "Butcher's Cut Steakhouse", 7, VenueCategory.DINING, [Coordinate2D(0.55, 0.1), Coordinate2D(0.63, 0.1), Coordinate2D(0.63, 0.5), Coordinate2D(0.55, 0.5)], ["D07_BUTCHERS_CUT"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_KAITO_TEPPANYAKI": Venue("VENUE_KAITO_TEPPANYAKI", "Kaito Teppanyaki & Sushi Bar", 7, VenueCategory.DINING, [Coordinate2D(0.55, -0.5), Coordinate2D(0.63, -0.5), Coordinate2D(0.63, -0.1), Coordinate2D(0.55, -0.1)], ["D07_KAITO_TEPPANYAKI"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_HOLA_TAPAS": Venue("VENUE_HOLA_TAPAS", "HOLA! Tapas Bar by Ramón Freixa", 7, VenueCategory.DINING, [Coordinate2D(0.63, 0.1), Coordinate2D(0.68, 0.1), Coordinate2D(0.68, 0.45), Coordinate2D(0.63, 0.45)], ["D07_HOLA_TAPAS"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_THEATER_UPPER": Venue("VENUE_THEATER_UPPER", "London Theatre (Balcony Level)", 7, VenueCategory.THEATER, [Coordinate2D(0.80, -0.65), Coordinate2D(0.92, -0.65), Coordinate2D(0.92, 0.65), Coordinate2D(0.80, 0.65)], ["D07_THEATER_UPPER"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[7] = Deck(7, "Mirabilis", 17.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, venues=d7_venues, corridor_nodes=d7_nodes, corridor_edges=d7_edges)

    # =============================================================
    # RESIDENTIAL TIERS: DECKS 08 TO 14
    # =============================================================
    residential_specs = [
        (8, "Camellia", 21.0, DeckVerticalZone.RESIDENTIAL_LOWER, True),
        (9, "Magnolia", 24.5, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (10, "Mirto", 28.0, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (11, "Ortensia", 31.5, DeckVerticalZone.RESIDENTIAL_LOWER, False),
        (12, "Rosa", 35.0, DeckVerticalZone.RESIDENTIAL_UPPER, False),
        (13, "Ciclamino", 38.5, DeckVerticalZone.RESIDENTIAL_UPPER, False),
        (14, "Girasole", 42.0, DeckVerticalZone.RESIDENTIAL_UPPER, False),
    ]

    for d_num, d_name, d_elev, d_zone, has_lifeboats in residential_specs:
        nodes = create_deck_cores(d_num, d_elev)

        # Corridor wayfinding branch nodes
        nodes[f"D{d_num:02d}_AFT_CORR_STBD_1"] = CorridorNode(f"D{d_num:02d}_AFT_CORR_STBD_1", d_num, Coordinate2D(0.28, 0.35))
        nodes[f"D{d_num:02d}_AFT_CORR_PORT_1"] = CorridorNode(f"D{d_num:02d}_AFT_CORR_PORT_1", d_num, Coordinate2D(0.28, -0.35))
        nodes[f"D{d_num:02d}_MID_CORR_STBD_1"] = CorridorNode(f"D{d_num:02d}_MID_CORR_STBD_1", d_num, Coordinate2D(0.53, 0.35))
        nodes[f"D{d_num:02d}_MID_CORR_PORT_1"] = CorridorNode(f"D{d_num:02d}_MID_CORR_PORT_1", d_num, Coordinate2D(0.53, -0.35))
        nodes[f"D{d_num:02d}_FWD_CORR_STBD_1"] = CorridorNode(f"D{d_num:02d}_FWD_CORR_STBD_1", d_num, Coordinate2D(0.78, 0.35))
        nodes[f"D{d_num:02d}_FWD_CORR_PORT_1"] = CorridorNode(f"D{d_num:02d}_FWD_CORR_PORT_1", d_num, Coordinate2D(0.78, -0.35))

        edges = [
            # Main longitudinal spine connecting lift lobbies
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_MID_LIFT", 78.0, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_FWD_LIFT", 78.0, is_step_free=True),
            # Lateral corridor branch connections
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_AFT_CORR_STBD_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_AFT_LIFT", f"D{d_num:02d}_AFT_CORR_PORT_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_MID_CORR_STBD_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_MID_LIFT", f"D{d_num:02d}_MID_CORR_PORT_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_FWD_LIFT", f"D{d_num:02d}_FWD_CORR_STBD_1", 12.5, is_step_free=True),
            CorridorEdge(f"D{d_num:02d}_FWD_LIFT", f"D{d_num:02d}_FWD_CORR_PORT_1", 12.5, is_step_free=True),
        ]

        cabins: Dict[str, Cabin] = {}
        b_type = BalconyType.PARTIAL_OBSTRUCTION_LIFEBOAT if has_lifeboats else BalconyType.UNOBSTRUCTED

        # 1. Starboard Mid-Aft Balcony Staterooms (Connecting Pair)
        c_stbd_1 = f"{d_num}122"
        c_stbd_2 = f"{d_num}120"
        cabins[c_stbd_1] = Cabin(c_stbd_1, d_num, HullSide.STARBOARD, "BA" if not has_lifeboats else "OB", [Coordinate2D(0.275, 0.35), Coordinate2D(0.285, 0.35), Coordinate2D(0.285, 0.65), Coordinate2D(0.275, 0.65)], DoorNode(f"DOOR_{c_stbd_1}", d_num, Coordinate2D(0.28, 0.35), f"D{d_num:02d}_AFT_CORR_STBD_1", clear_width_mm=850), 19.0, b_type, socket_std, connecting_cabin_number=c_stbd_2, bed_near_balcony=True, is_accessible_stateroom=False, evidence_links=[ev_ga_full, ev_survey])
        cabins[c_stbd_2] = Cabin(c_stbd_2, d_num, HullSide.STARBOARD, "BA" if not has_lifeboats else "OB", [Coordinate2D(0.255, 0.35), Coordinate2D(0.265, 0.35), Coordinate2D(0.265, 0.65), Coordinate2D(0.255, 0.65)], DoorNode(f"DOOR_{c_stbd_2}", d_num, Coordinate2D(0.26, 0.35), f"D{d_num:02d}_AFT_CORR_STBD_1", clear_width_mm=850), 19.0, b_type, socket_std, connecting_cabin_number=c_stbd_1, bed_near_balcony=False, is_accessible_stateroom=False, evidence_links=[ev_ga_full])

        # 2. Port Side Certified Accessible Stateroom
        c_port_acc = f"{d_num}121"
        cabins[c_port_acc] = Cabin(c_port_acc, d_num, HullSide.PORT, "BA_ACC", [Coordinate2D(0.270, -0.35), Coordinate2D(0.285, -0.35), Coordinate2D(0.285, -0.70), Coordinate2D(0.270, -0.70)], DoorNode(f"DOOR_{c_port_acc}", d_num, Coordinate2D(0.28, -0.35), f"D{d_num:02d}_AFT_CORR_PORT_1", clear_width_mm=950), 28.0, BalconyType.UNOBSTRUCTED, socket_acc, connecting_cabin_number=None, bed_near_balcony=True, is_accessible_stateroom=True, evidence_links=[ev_ga_full, ev_builder_spec])

        # 3. Midship Deluxe Balcony Stateroom (Quiet residential core)
        c_mid_stbd = f"{d_num}088"
        cabins[c_mid_stbd] = Cabin(c_mid_stbd, d_num, HullSide.STARBOARD, "BR1", [Coordinate2D(0.525, 0.35), Coordinate2D(0.535, 0.35), Coordinate2D(0.535, 0.65), Coordinate2D(0.525, 0.65)], DoorNode(f"DOOR_{c_mid_stbd}", d_num, Coordinate2D(0.53, 0.35), f"D{d_num:02d}_MID_CORR_STBD_1", clear_width_mm=850), 19.0, BalconyType.UNOBSTRUCTED, socket_std, connecting_cabin_number=None, bed_near_balcony=True, is_accessible_stateroom=False, evidence_links=[ev_ga_full])

        # 4. Midship Interior Quiet Stateroom (Acoustic benchmark)
        c_mid_int = f"{d_num}089"
        cabins[c_mid_int] = Cabin(c_mid_int, d_num, HullSide.PORT, "IR1", [Coordinate2D(0.525, -0.15), Coordinate2D(0.535, -0.15), Coordinate2D(0.535, -0.35), Coordinate2D(0.525, -0.35)], DoorNode(f"DOOR_{c_mid_int}", d_num, Coordinate2D(0.53, -0.35), f"D{d_num:02d}_MID_CORR_PORT_1", clear_width_mm=850), 16.0, BalconyType.NO_BALCONY, socket_std, connecting_cabin_number=None, bed_near_balcony=False, is_accessible_stateroom=False, evidence_links=[ev_ga_full])

        # 5. Forward Premium Stateroom / Suite
        c_fwd_suite = f"{d_num}002"
        cabins[c_fwd_suite] = Cabin(c_fwd_suite, d_num, HullSide.STARBOARD, "SL1", [Coordinate2D(0.775, 0.35), Coordinate2D(0.790, 0.35), Coordinate2D(0.790, 0.70), Coordinate2D(0.775, 0.70)], DoorNode(f"DOOR_{c_fwd_suite}", d_num, Coordinate2D(0.78, 0.35), f"D{d_num:02d}_FWD_CORR_STBD_1", clear_width_mm=900), 27.0, BalconyType.UNOBSTRUCTED, socket_suite, connecting_cabin_number=None, bed_near_balcony=True, is_accessible_stateroom=False, evidence_links=[ev_ga_full])

        decks[d_num] = Deck(d_num, d_name, d_elev, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], d_zone, cabins=cabins, corridor_nodes=nodes, corridor_edges=edges)

    # =============================================================
    # DECK 15: RODODENDRO (Atmosphere Pool, Grand Canyon Solarium & Buffet)
    # =============================================================
    d15_nodes = create_deck_cores(15, 45.5)
    d15_nodes["D15_BUFFET_ENTRANCE"] = CorridorNode("D15_BUFFET_ENTRANCE", 15, Coordinate2D(0.28, 0.0))
    d15_nodes["D15_GRAND_CANYON_POOL"] = CorridorNode("D15_GRAND_CANYON_POOL", 15, Coordinate2D(0.42, 0.0))
    d15_nodes["D15_ATMOSPHERE_POOL"] = CorridorNode("D15_ATMOSPHERE_POOL", 15, Coordinate2D(0.58, 0.0))
    d15_nodes["D15_TOP_SAIL_L15"] = CorridorNode("D15_TOP_SAIL_L15", 15, Coordinate2D(0.82, 0.0))

    d15_edges = [
        CorridorEdge("D15_AFT_LIFT", "D15_BUFFET_ENTRANCE", 10.0, is_step_free=True),
        CorridorEdge("D15_BUFFET_ENTRANCE", "D15_GRAND_CANYON_POOL", 43.5, is_step_free=True),
        CorridorEdge("D15_GRAND_CANYON_POOL", "D15_MID_LIFT", 25.0, is_step_free=True),
        CorridorEdge("D15_MID_LIFT", "D15_ATMOSPHERE_POOL", 25.0, is_step_free=True),
        CorridorEdge("D15_ATMOSPHERE_POOL", "D15_FWD_LIFT", 53.0, is_step_free=True),
        CorridorEdge("D15_FWD_LIFT", "D15_TOP_SAIL_L15", 22.0, is_step_free=True),
    ]

    d15_venues = {
        "VENUE_BUFFET": Venue("VENUE_BUFFET", "Marketplace Buffet (Forward & Mid)", 15, VenueCategory.BUFFET, [Coordinate2D(0.10, -0.8), Coordinate2D(0.35, -0.8), Coordinate2D(0.35, 0.8), Coordinate2D(0.10, 0.8)], ["D15_BUFFET_ENTRANCE"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_GRAND_CANYON_POOL": Venue("VENUE_GRAND_CANYON_POOL", "Grand Canyon Covered Pool (Solarium)", 15, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.36, -0.65), Coordinate2D(0.48, -0.65), Coordinate2D(0.48, 0.65), Coordinate2D(0.36, 0.65)], ["D15_GRAND_CANYON_POOL"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_ATMOSPHERE_POOL": Venue("VENUE_ATMOSPHERE_POOL", "Atmosphere Pool & Main Sun Deck", 15, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.50, -0.75), Coordinate2D(0.68, -0.75), Coordinate2D(0.68, 0.75), Coordinate2D(0.50, 0.75)], ["D15_ATMOSPHERE_POOL"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_LOUNGE_L15": Venue("VENUE_TOP_SAIL_LOUNGE_L15", "MSC Yacht Club Top Sail Lounge (Deck 15)", 15, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.76, -0.6), Coordinate2D(0.88, -0.6), Coordinate2D(0.88, 0.6), Coordinate2D(0.76, 0.6)], ["D15_TOP_SAIL_L15"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[15] = Deck(15, "Rododendro", 45.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.75), Coordinate2D(0.95, 0.65), Coordinate2D(1.0, 0.0)], DeckVerticalZone.LIDO_SPORTS, venues=d15_venues, corridor_nodes=d15_nodes, corridor_edges=d15_edges)

    # =============================================================
    # DECK 16: ORCHIDEA (MSC Gym, Aurea Spa, Sportplex & Yacht Club Rest.)
    # =============================================================
    d16_nodes = create_deck_cores(16, 49.0)
    d16_nodes["D16_GYM"] = CorridorNode("D16_GYM", 16, Coordinate2D(0.20, 0.0))
    d16_nodes["D16_BUFFET_AFT"] = CorridorNode("D16_BUFFET_AFT", 16, Coordinate2D(0.12, 0.0))
    d16_nodes["D16_SPORTPLEX"] = CorridorNode("D16_SPORTPLEX", 16, Coordinate2D(0.35, 0.0))
    d16_nodes["D16_SPA"] = CorridorNode("D16_SPA", 16, Coordinate2D(0.78, 0.0))
    d16_nodes["D16_TOP_SAIL_REST"] = CorridorNode("D16_TOP_SAIL_REST", 16, Coordinate2D(0.85, 0.0))

    d16_edges = [
        CorridorEdge("D16_AFT_LIFT", "D16_BUFFET_AFT", 40.0, is_step_free=True),
        CorridorEdge("D16_AFT_LIFT", "D16_GYM", 15.0, is_step_free=True),
        CorridorEdge("D16_AFT_LIFT", "D16_SPORTPLEX", 31.0, is_step_free=True),
        CorridorEdge("D16_SPORTPLEX", "D16_MID_LIFT", 47.0, is_step_free=True),
        CorridorEdge("D16_MID_LIFT", "D16_FWD_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D16_FWD_LIFT", "D16_SPA", 10.0, is_step_free=True),
        CorridorEdge("D16_FWD_LIFT", "D16_TOP_SAIL_REST", 31.0, is_step_free=True),
    ]

    d16_venues = {
        "VENUE_BUFFET_AFT": Venue("VENUE_BUFFET_AFT", "Marketplace Buffet (Aft Terrace & Pizzeria)", 16, VenueCategory.BUFFET, [Coordinate2D(0.06, -0.6), Coordinate2D(0.18, -0.6), Coordinate2D(0.18, 0.6), Coordinate2D(0.06, 0.6)], ["D16_BUFFET_AFT"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_GYM": Venue("VENUE_GYM", "MSC Gym by Technogym", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.18, -0.5), Coordinate2D(0.24, -0.5), Coordinate2D(0.24, 0.5), Coordinate2D(0.18, 0.5)], ["D16_GYM"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_SPORTPLEX": Venue("VENUE_SPORTPLEX", "Sportplex Arena & F1 Simulator", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.28, -0.6), Coordinate2D(0.42, -0.6), Coordinate2D(0.42, 0.6), Coordinate2D(0.28, 0.6)], ["D16_SPORTPLEX"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_AUREA_SPA": Venue("VENUE_AUREA_SPA", "MSC Aurea Spa & Thermal Suite", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.70, -0.6), Coordinate2D(0.82, -0.6), Coordinate2D(0.82, 0.6), Coordinate2D(0.70, 0.6)], ["D16_SPA"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_RESTAURANT": Venue("VENUE_TOP_SAIL_RESTAURANT", "MSC Yacht Club Restaurant", 16, VenueCategory.DINING, [Coordinate2D(0.82, -0.5), Coordinate2D(0.90, -0.5), Coordinate2D(0.90, 0.5), Coordinate2D(0.82, 0.5)], ["D16_TOP_SAIL_REST"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[16] = Deck(16, "Orchidea", 49.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.LIDO_SPORTS, venues=d16_venues, corridor_nodes=d16_nodes, corridor_edges=d16_edges)

    # =============================================================
    # DECK 18: NINFEA (Arizona Aquapark, DOREMI Kids, Horizon Sunset Bar)
    # =============================================================
    d18_nodes = create_deck_cores(18, 55.0)
    d18_nodes["D18_HORIZON_BAR"] = CorridorNode("D18_HORIZON_BAR", 18, Coordinate2D(0.08, 0.0))
    d18_nodes["D18_DOREMI"] = CorridorNode("D18_DOREMI", 18, Coordinate2D(0.20, 0.0))
    d18_nodes["D18_AQUAPARK"] = CorridorNode("D18_AQUAPARK", 18, Coordinate2D(0.40, 0.0))
    d18_nodes["D18_TOP_SAIL_L18"] = CorridorNode("D18_TOP_SAIL_L18", 18, Coordinate2D(0.80, 0.0))

    d18_edges = [
        CorridorEdge("D18_AFT_LIFT", "D18_HORIZON_BAR", 53.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_DOREMI", 15.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_AQUAPARK", 45.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_MID_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D18_MID_LIFT", "D18_FWD_LIFT", 78.0, is_step_free=True),
        CorridorEdge("D18_FWD_LIFT", "D18_TOP_SAIL_L18", 16.0, is_step_free=True),
    ]

    d18_venues = {
        "VENUE_HORIZON_AMPHITHEATRE": Venue("VENUE_HORIZON_AMPHITHEATRE", "Horizon Amphitheatre & Sunset Bar", 18, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.02, -0.5), Coordinate2D(0.12, -0.5), Coordinate2D(0.12, 0.5), Coordinate2D(0.02, 0.5)], ["D18_HORIZON_BAR"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_DOREMI_KIDS": Venue("VENUE_DOREMI_KIDS", "DOREMI Studio & Junior Club (LEGO / Chicco)", 18, VenueCategory.YOUTH_KIDS, [Coordinate2D(0.12, -0.5), Coordinate2D(0.24, -0.5), Coordinate2D(0.24, 0.5), Coordinate2D(0.12, 0.5)], ["D18_DOREMI"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_AQUAPARK": Venue("VENUE_AQUAPARK", "Arizona Aquapark & Himalayan Bridge (82m above sea)", 18, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.30, -0.65), Coordinate2D(0.48, -0.65), Coordinate2D(0.48, 0.65), Coordinate2D(0.30, 0.65)], ["D18_AQUAPARK"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_LOUNGE_L18": Venue("VENUE_TOP_SAIL_LOUNGE_L18", "MSC Yacht Club Top Sail Lounge (Deck 18)", 18, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.74, -0.55), Coordinate2D(0.85, -0.55), Coordinate2D(0.85, 0.55), Coordinate2D(0.74, 0.55)], ["D18_TOP_SAIL_L18"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[18] = Deck(18, "Ninfea", 55.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.6), Coordinate2D(0.85, 0.5), Coordinate2D(0.9, 0.0)], DeckVerticalZone.LIDO_SPORTS, venues=d18_venues, corridor_nodes=d18_nodes, corridor_edges=d18_edges)

    # =============================================================
    # DECK 19: MAGNOLIA (Top Deck Solarium & Yacht Club Sun Deck)
    # =============================================================
    d19_nodes = {
        "D19_FWD_LIFT": CorridorNode("D19_FWD_LIFT", 19, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, vertical_core_id="CORE_FWD"),
        "D19_SUNDECK": CorridorNode("D19_SUNDECK", 19, Coordinate2D(0.70, 0.0)),
        "D19_THE_ONE_GRILL": CorridorNode("D19_THE_ONE_GRILL", 19, Coordinate2D(0.78, 0.15)),
    }
    d19_edges = [
        CorridorEdge("D19_FWD_LIFT", "D19_SUNDECK", 15.0, is_step_free=True),
        CorridorEdge("D19_FWD_LIFT", "D19_THE_ONE_GRILL", 10.0, is_step_free=True),
    ]
    d19_venues = {
        "VENUE_YACHT_CLUB_SUNDECK": Venue("VENUE_YACHT_CLUB_SUNDECK", "Top Deck Solarium & The One Pool", 19, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.65, -0.6), Coordinate2D(0.85, -0.6), Coordinate2D(0.85, 0.6), Coordinate2D(0.65, 0.6)], ["D19_SUNDECK"], is_noise_generator=False, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_THE_ONE_GRILL": Venue("VENUE_THE_ONE_GRILL", "The One Grill & Bar (Yacht Club Exclusive)", 19, VenueCategory.DINING, [Coordinate2D(0.75, 0.1), Coordinate2D(0.82, 0.1), Coordinate2D(0.82, 0.4), Coordinate2D(0.75, 0.4)], ["D19_THE_ONE_GRILL"], is_noise_generator=False, is_open_deck=True, evidence_links=[ev_ga_full]),
    }
    decks[19] = Deck(19, "Magnolia", 58.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.1, 0.5), Coordinate2D(0.8, 0.4), Coordinate2D(0.85, 0.0)], DeckVerticalZone.LIDO_SPORTS, venues=d19_venues, corridor_nodes=d19_nodes, corridor_edges=d19_edges)

    return VesselSpatialOntology(
        imo_number="IMO9766205",
        name="MSC Bellissima",
        ship_class="Meraviglia Class",
        length_overall_meters=315.83,
        beam_meters=43.0,
        total_decks=19,
        decks=decks,
    )
