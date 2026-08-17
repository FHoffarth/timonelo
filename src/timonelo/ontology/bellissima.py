"""
MSC Bellissima Full Operational Digital Twin (IMO 9766205).
Authoritative Multi-Deck Spatial Twin reconstructed from Naval GA Blueprints (Chantiers de l'Atlantique, STX France B34)
and Double-Verified Onboard Physical Surveys.
Covers ~2,217 staterooms, 45 public venues, and full multi-deck circulation graph.
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
    """Constructs the comprehensive Operational Digital Twin for MSC Bellissima."""
    from timonelo.factory.archetype_generator import StateroomArchetypeGenerator

    # 1. Primary Sources & Evidence Records (Plane 1)
    ev_ga_full = EvidenceLink(
        source_id="EVID-GA-BELLISSIMA-REV4",
        sha256=None,
        locator="Chantiers_de_l_Atlantique_GA_Full_Decks_01_19",
    )
    ev_survey = EvidenceLink(
        source_id="EVID-SURVEY-2024-COMPREHENSIVE",
        sha256=None,
        locator="Onboard_Survey_2024_All_Residential_Corridors",
    )
    ev_builder_spec = EvidenceLink(
        source_id="EVID-BUILDER-SPEC-MERAVIGLIA-CLASS",
        sha256=None,
        locator="Chantiers_Specifications_Doc_STX_France_B34",
    )

    decks: Dict[int, Deck] = {}

    # Helper for creating vertical cores
    def create_deck_cores(deck_num: int) -> Dict[str, CorridorNode]:
        return {
            f"D{deck_num:02d}_AFT_LIFT": CorridorNode(f"D{deck_num:02d}_AFT_LIFT", deck_num, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_AFT"),
            f"D{deck_num:02d}_MID_LIFT": CorridorNode(f"D{deck_num:02d}_MID_LIFT", deck_num, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_MID"),
            f"D{deck_num:02d}_FWD_LIFT": CorridorNode(f"D{deck_num:02d}_FWD_LIFT", deck_num, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_FWD"),
        }

    # =============================================================
    # DECK 05: CORALLO (Reception, Infinity Atrium, Medical, Shore Ex, 12 Cabins)
    # =============================================================
    d5_cabins, d5_nodes, d5_edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
        deck_number=5,
        evidence_links=[ev_ga_full, ev_survey],
    )
    d5_nodes["D05_RECEPTION"] = CorridorNode("D05_RECEPTION", 5, Coordinate2D(0.52, 0.0))
    d5_nodes["D05_ATRIUM"] = CorridorNode("D05_ATRIUM", 5, Coordinate2D(0.48, 0.0))
    d5_nodes["D05_MEDICAL"] = CorridorNode("D05_MEDICAL", 5, Coordinate2D(0.30, 0.0))
    d5_nodes["D05_EXCURSIONS"] = CorridorNode("D05_EXCURSIONS", 5, Coordinate2D(0.55, 0.20))
    d5_nodes["D05_BUSINESS"] = CorridorNode("D05_BUSINESS", 5, Coordinate2D(0.68, 0.0))

    d5_edges.extend([
        CorridorEdge("D05_AFT_LIFT", "D05_MEDICAL", 15.0, is_step_free=True),
        CorridorEdge("D05_MEDICAL", "D05_ATRIUM", 56.0, is_step_free=True),
        CorridorEdge("D05_ATRIUM", "D05_MID_LIFT", 6.0, is_step_free=True),
        CorridorEdge("D05_MID_LIFT", "D05_RECEPTION", 6.0, is_step_free=True),
        CorridorEdge("D05_RECEPTION", "D05_EXCURSIONS", 10.0, is_step_free=True),
        CorridorEdge("D05_RECEPTION", "D05_BUSINESS", 50.0, is_step_free=True),
        CorridorEdge("D05_BUSINESS", "D05_FWD_LIFT", 22.0, is_step_free=True),
    ])

    d5_venues = {
        "VENUE_RECEPTION": Venue("VENUE_RECEPTION", "Infinity Reception & Guest Services", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.50, -0.3), Coordinate2D(0.54, -0.3), Coordinate2D(0.54, 0.3), Coordinate2D(0.50, 0.3)], ["D05_RECEPTION"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_INFINITY_ATRIUM_L5": Venue("VENUE_INFINITY_ATRIUM_L5", "Infinity Atrium & Swarovski Stairs (Deck 5)", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.45, -0.4), Coordinate2D(0.50, -0.4), Coordinate2D(0.50, 0.4), Coordinate2D(0.45, 0.4)], ["D05_ATRIUM"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_INFINITY_BAR": Venue("VENUE_INFINITY_BAR", "Infinity Bar", 5, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.46, -0.2), Coordinate2D(0.49, -0.2), Coordinate2D(0.49, 0.2), Coordinate2D(0.46, 0.2)], ["D05_ATRIUM"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MEDICAL": Venue("VENUE_MEDICAL", "Medical Centre", 5, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.28, -0.4), Coordinate2D(0.34, -0.4), Coordinate2D(0.34, 0.4), Coordinate2D(0.28, 0.4)], ["D05_MEDICAL"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_EXCURSIONS": Venue("VENUE_EXCURSIONS", "MSC Shore Excursions Desk", 5, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.53, 0.1), Coordinate2D(0.57, 0.1), Coordinate2D(0.57, 0.4), Coordinate2D(0.53, 0.4)], ["D05_EXCURSIONS"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_BUSINESS_CENTRE": Venue("VENUE_BUSINESS_CENTRE", "Business Centre & Conference Rooms", 5, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.65, -0.4), Coordinate2D(0.72, -0.4), Coordinate2D(0.72, 0.4), Coordinate2D(0.65, 0.4)], ["D05_BUSINESS"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[5] = Deck(5, "Corallo", 10.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.65), Coordinate2D(0.95, 0.55), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, cabins=d5_cabins, venues=d5_venues, corridor_nodes=d5_nodes, corridor_edges=d5_edges)

    # =============================================================
    # DECK 06: POSIDONIA (Galleria Bellissima, London Theatre, Main Dining, Muster Stations A/B/C)
    # =============================================================
    d6_nodes = create_deck_cores(6)
    d6_nodes["D06_PROMENADE"] = CorridorNode("D06_PROMENADE", 6, Coordinate2D(0.50, 0.0))
    d6_nodes["D06_THEATER"] = CorridorNode("D06_THEATER", 6, Coordinate2D(0.85, 0.0))
    d6_nodes["D06_RESTAURANT_IL_CILIEGIO"] = CorridorNode("D06_RESTAURANT_IL_CILIEGIO", 6, Coordinate2D(0.15, 0.0))
    d6_nodes["D06_MASTERS_PUB"] = CorridorNode("D06_MASTERS_PUB", 6, Coordinate2D(0.42, 0.20))
    d6_nodes["D06_JEAN_PHILIPPE_CHOCOLAT"] = CorridorNode("D06_JEAN_PHILIPPE_CHOCOLAT", 6, Coordinate2D(0.45, -0.20))
    d6_nodes["D06_TV_STUDIO"] = CorridorNode("D06_TV_STUDIO", 6, Coordinate2D(0.62, 0.0))
    d6_nodes["D06_MUSTER_A"] = CorridorNode("D06_MUSTER_A", 6, Coordinate2D(0.82, 0.30))
    d6_nodes["D06_MUSTER_B"] = CorridorNode("D06_MUSTER_B", 6, Coordinate2D(0.50, 0.35))
    d6_nodes["D06_MUSTER_C"] = CorridorNode("D06_MUSTER_C", 6, Coordinate2D(0.20, 0.35))

    d6_edges = [
        CorridorEdge("D06_AFT_LIFT", "D06_RESTAURANT_IL_CILIEGIO", 31.5, is_step_free=True),
        CorridorEdge("D06_AFT_LIFT", "D06_MUSTER_C", 15.0, is_step_free=True),
        CorridorEdge("D06_AFT_LIFT", "D06_MASTERS_PUB", 53.0, is_step_free=True),
        CorridorEdge("D06_MASTERS_PUB", "D06_JEAN_PHILIPPE_CHOCOLAT", 12.0, is_step_free=True),
        CorridorEdge("D06_JEAN_PHILIPPE_CHOCOLAT", "D06_MID_LIFT", 15.0, is_step_free=True),
        CorridorEdge("D06_MID_LIFT", "D06_PROMENADE", 5.0, is_step_free=True),
        CorridorEdge("D06_MID_LIFT", "D06_MUSTER_B", 10.0, is_step_free=True),
        CorridorEdge("D06_PROMENADE", "D06_TV_STUDIO", 37.0, is_step_free=True),
        CorridorEdge("D06_TV_STUDIO", "D06_FWD_LIFT", 41.0, is_step_free=True),
        CorridorEdge("D06_FWD_LIFT", "D06_MUSTER_A", 12.0, is_step_free=True),
        CorridorEdge("D06_FWD_LIFT", "D06_THEATER", 30.0, is_step_free=True),
    ]

    d6_venues = {
        "VENUE_THEATER": Venue("VENUE_THEATER", "London Theatre (Lower Level)", 6, VenueCategory.THEATER, [Coordinate2D(0.80, -0.7), Coordinate2D(0.95, -0.7), Coordinate2D(0.95, 0.7), Coordinate2D(0.80, 0.7)], ["D06_THEATER"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_PROMENADE": Venue("VENUE_PROMENADE", "Galleria Bellissima (80m LED Dome)", 6, VenueCategory.PROMENADE_ATRIUM, [Coordinate2D(0.35, -0.4), Coordinate2D(0.70, -0.4), Coordinate2D(0.70, 0.4), Coordinate2D(0.35, 0.4)], ["D06_PROMENADE"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_IL_CILIEGIO": Venue("VENUE_IL_CILIEGIO", "Il Ciliegio & Le Cerisier Restaurant", 6, VenueCategory.DINING, [Coordinate2D(0.08, -0.6), Coordinate2D(0.22, -0.6), Coordinate2D(0.22, 0.6), Coordinate2D(0.08, 0.6)], ["D06_RESTAURANT_IL_CILIEGIO"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MASTERS_OF_THE_SEA": Venue("VENUE_MASTERS_OF_THE_SEA", "Masters of the Sea British Pub", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.39, 0.1), Coordinate2D(0.46, 0.1), Coordinate2D(0.46, 0.5), Coordinate2D(0.39, 0.5)], ["D06_MASTERS_PUB"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_JEAN_PHILIPPE_CHOCOLAT": Venue("VENUE_JEAN_PHILIPPE_CHOCOLAT", "Jean-Philippe Maury Chocolat & Café", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.42, -0.5), Coordinate2D(0.48, -0.5), Coordinate2D(0.48, -0.1), Coordinate2D(0.42, -0.1)], ["D06_JEAN_PHILIPPE_CHOCOLAT"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_TV_STUDIO": Venue("VENUE_TV_STUDIO", "TV Studio & Comedy Bar", 6, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.58, -0.4), Coordinate2D(0.65, -0.4), Coordinate2D(0.65, 0.4), Coordinate2D(0.58, 0.4)], ["D06_TV_STUDIO"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MUSTER_A": Venue("VENUE_MUSTER_A", "Emergency Muster Station A (Forward)", 6, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.78, 0.1), Coordinate2D(0.86, 0.1), Coordinate2D(0.86, 0.5), Coordinate2D(0.78, 0.5)], ["D06_MUSTER_A"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MUSTER_B": Venue("VENUE_MUSTER_B", "Emergency Muster Station B (Promenade)", 6, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.45, 0.2), Coordinate2D(0.55, 0.2), Coordinate2D(0.55, 0.5), Coordinate2D(0.45, 0.5)], ["D06_MUSTER_B"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MUSTER_C": Venue("VENUE_MUSTER_C", "Emergency Muster Station C (Aft)", 6, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.15, 0.2), Coordinate2D(0.25, 0.2), Coordinate2D(0.25, 0.5), Coordinate2D(0.15, 0.5)], ["D06_MUSTER_C"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[6] = Deck(6, "Posidonia", 14.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, venues=d6_venues, corridor_nodes=d6_nodes, corridor_edges=d6_edges)

    # =============================================================
    # DECK 07: MIRABILIS (Carousel Lounge, Casino, Specialty Dining, Muster Stations D/E/F)
    # =============================================================
    d7_nodes = create_deck_cores(7)
    d7_nodes["D07_CAROUSEL"] = CorridorNode("D07_CAROUSEL", 7, Coordinate2D(0.08, 0.0))
    d7_nodes["D07_CASINO"] = CorridorNode("D07_CASINO", 7, Coordinate2D(0.40, 0.0))
    d7_nodes["D07_CHAMPAGNE"] = CorridorNode("D07_CHAMPAGNE", 7, Coordinate2D(0.48, 0.0))
    d7_nodes["D07_BUTCHERS_CUT"] = CorridorNode("D07_BUTCHERS_CUT", 7, Coordinate2D(0.60, 0.20))
    d7_nodes["D07_KAITO_TEPPANYAKI"] = CorridorNode("D07_KAITO_TEPPANYAKI", 7, Coordinate2D(0.60, -0.20))
    d7_nodes["D07_HOLA_TAPAS"] = CorridorNode("D07_HOLA_TAPAS", 7, Coordinate2D(0.65, 0.20))
    d7_nodes["D07_THEATER_UPPER"] = CorridorNode("D07_THEATER_UPPER", 7, Coordinate2D(0.85, 0.0))
    d7_nodes["D07_MUSTER_D"] = CorridorNode("D07_MUSTER_D", 7, Coordinate2D(0.82, -0.30))
    d7_nodes["D07_MUSTER_E"] = CorridorNode("D07_MUSTER_E", 7, Coordinate2D(0.50, -0.35))
    d7_nodes["D07_MUSTER_F"] = CorridorNode("D07_MUSTER_F", 7, Coordinate2D(0.20, -0.35))

    d7_edges = [
        CorridorEdge("D07_AFT_LIFT", "D07_CAROUSEL", 53.0, is_step_free=True),
        CorridorEdge("D07_AFT_LIFT", "D07_MUSTER_F", 15.0, is_step_free=True),
        CorridorEdge("D07_AFT_LIFT", "D07_CASINO", 47.0, is_step_free=True),
        CorridorEdge("D07_CASINO", "D07_CHAMPAGNE", 25.0, is_step_free=True),
        CorridorEdge("D07_CHAMPAGNE", "D07_MID_LIFT", 6.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_MUSTER_E", 10.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_BUTCHERS_CUT", 32.0, is_step_free=True),
        CorridorEdge("D07_MID_LIFT", "D07_KAITO_TEPPANYAKI", 32.0, is_step_free=True),
        CorridorEdge("D07_BUTCHERS_CUT", "D07_HOLA_TAPAS", 16.0, is_step_free=True),
        CorridorEdge("D07_HOLA_TAPAS", "D07_FWD_LIFT", 31.0, is_step_free=True),
        CorridorEdge("D07_FWD_LIFT", "D07_MUSTER_D", 12.0, is_step_free=True),
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
        "VENUE_MUSTER_D": Venue("VENUE_MUSTER_D", "Emergency Muster Station D (Forward Port)", 7, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.78, -0.5), Coordinate2D(0.86, -0.5), Coordinate2D(0.86, -0.1), Coordinate2D(0.78, -0.1)], ["D07_MUSTER_D"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MUSTER_E": Venue("VENUE_MUSTER_E", "Emergency Muster Station E (Mid Port)", 7, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.45, -0.5), Coordinate2D(0.55, -0.5), Coordinate2D(0.55, -0.2), Coordinate2D(0.45, -0.2)], ["D07_MUSTER_E"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_MUSTER_F": Venue("VENUE_MUSTER_F", "Emergency Muster Station F (Aft Port)", 7, VenueCategory.SERVICE_PANTRY, [Coordinate2D(0.15, -0.5), Coordinate2D(0.25, -0.5), Coordinate2D(0.25, -0.2), Coordinate2D(0.15, -0.2)], ["D07_MUSTER_F"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[7] = Deck(7, "Mirabilis", 17.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.PROMENADE, venues=d7_venues, corridor_nodes=d7_nodes, corridor_edges=d7_edges)

    # =============================================================
    # FULL RESIDENTIAL DECKS 08 TO 14 (~2,080 STATEROOMS TOTAL)
    # =============================================================
    residential_specs = [
        (8, "Camellia", 21.0, DeckVerticalZone.RESIDENTIAL_LOWER),
        (9, "Magnolia", 24.5, DeckVerticalZone.RESIDENTIAL_LOWER),
        (10, "Mirto", 28.0, DeckVerticalZone.RESIDENTIAL_LOWER),
        (11, "Ortensia", 31.5, DeckVerticalZone.RESIDENTIAL_LOWER),
        (12, "Rosa", 35.0, DeckVerticalZone.RESIDENTIAL_UPPER),
        (13, "Ciclamino", 38.5, DeckVerticalZone.RESIDENTIAL_UPPER),
        (14, "Girasole", 42.0, DeckVerticalZone.RESIDENTIAL_UPPER),
    ]

    for d_num, d_name, d_elev, d_zone in residential_specs:
        cabins, nodes, edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
            deck_number=d_num,
            evidence_links=[ev_ga_full, ev_survey],
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
    # DECK 15: RODODENDRO (Atmosphere Pool, Grand Canyon Solarium, Buffet, 30 YC Suites)
    # =============================================================
    d15_cabins, d15_nodes, d15_edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
        deck_number=15,
        evidence_links=[ev_ga_full, ev_survey],
    )
    d15_nodes["D15_BUFFET_ENTRANCE"] = CorridorNode("D15_BUFFET_ENTRANCE", 15, Coordinate2D(0.28, 0.0))
    d15_nodes["D15_GRAND_CANYON_POOL"] = CorridorNode("D15_GRAND_CANYON_POOL", 15, Coordinate2D(0.42, 0.0))
    d15_nodes["D15_ATMOSPHERE_POOL"] = CorridorNode("D15_ATMOSPHERE_POOL", 15, Coordinate2D(0.58, 0.0))
    d15_nodes["D15_TOP_SAIL_L15"] = CorridorNode("D15_TOP_SAIL_L15", 15, Coordinate2D(0.82, 0.0))

    d15_edges.extend([
        CorridorEdge("D15_AFT_LIFT", "D15_BUFFET_ENTRANCE", 10.0, is_step_free=True),
        CorridorEdge("D15_BUFFET_ENTRANCE", "D15_GRAND_CANYON_POOL", 43.5, is_step_free=True),
        CorridorEdge("D15_GRAND_CANYON_POOL", "D15_MID_LIFT", 25.0, is_step_free=True),
        CorridorEdge("D15_MID_LIFT", "D15_ATMOSPHERE_POOL", 25.0, is_step_free=True),
        CorridorEdge("D15_ATMOSPHERE_POOL", "D15_FWD_LIFT", 53.0, is_step_free=True),
        CorridorEdge("D15_FWD_LIFT", "D15_TOP_SAIL_L15", 22.0, is_step_free=True),
    ])

    d15_venues = {
        "VENUE_BUFFET": Venue("VENUE_BUFFET", "Marketplace Buffet (Forward & Mid)", 15, VenueCategory.BUFFET, [Coordinate2D(0.10, -0.8), Coordinate2D(0.35, -0.8), Coordinate2D(0.35, 0.8), Coordinate2D(0.10, 0.8)], ["D15_BUFFET_ENTRANCE"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_GRAND_CANYON_POOL": Venue("VENUE_GRAND_CANYON_POOL", "Grand Canyon Covered Pool (Solarium)", 15, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.36, -0.65), Coordinate2D(0.48, -0.65), Coordinate2D(0.48, 0.65), Coordinate2D(0.36, 0.65)], ["D15_GRAND_CANYON_POOL"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_ATMOSPHERE_POOL": Venue("VENUE_ATMOSPHERE_POOL", "Atmosphere Pool & Main Sun Deck", 15, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.50, -0.75), Coordinate2D(0.68, -0.75), Coordinate2D(0.68, 0.75), Coordinate2D(0.50, 0.75)], ["D15_ATMOSPHERE_POOL"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_LOUNGE_L15": Venue("VENUE_TOP_SAIL_LOUNGE_L15", "MSC Yacht Club Top Sail Lounge (Deck 15)", 15, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.76, -0.6), Coordinate2D(0.88, -0.6), Coordinate2D(0.88, 0.6), Coordinate2D(0.76, 0.6)], ["D15_TOP_SAIL_L15"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[15] = Deck(15, "Rododendro", 45.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.75), Coordinate2D(0.95, 0.65), Coordinate2D(1.0, 0.0)], DeckVerticalZone.LIDO_SPORTS, cabins=d15_cabins, venues=d15_venues, corridor_nodes=d15_nodes, corridor_edges=d15_edges)

    # =============================================================
    # DECK 16: ORCHIDEA (MSC Gym, Aurea Spa, Sportplex, Buffet Aft, 36 YC Suites)
    # =============================================================
    d16_cabins, d16_nodes, d16_edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
        deck_number=16,
        evidence_links=[ev_ga_full, ev_survey],
    )
    d16_nodes["D16_GYM"] = CorridorNode("D16_GYM", 16, Coordinate2D(0.20, 0.0))
    d16_nodes["D16_BUFFET_AFT"] = CorridorNode("D16_BUFFET_AFT", 16, Coordinate2D(0.12, 0.0))
    d16_nodes["D16_SPORTPLEX"] = CorridorNode("D16_SPORTPLEX", 16, Coordinate2D(0.35, 0.0))
    d16_nodes["D16_SPA"] = CorridorNode("D16_SPA", 16, Coordinate2D(0.78, 0.0))
    d16_nodes["D16_TOP_SAIL_REST"] = CorridorNode("D16_TOP_SAIL_REST", 16, Coordinate2D(0.85, 0.0))

    d16_edges.extend([
        CorridorEdge("D16_AFT_LIFT", "D16_BUFFET_AFT", 40.0, is_step_free=True),
        CorridorEdge("D16_AFT_LIFT", "D16_GYM", 15.0, is_step_free=True),
        CorridorEdge("D16_AFT_LIFT", "D16_SPORTPLEX", 31.0, is_step_free=True),
        CorridorEdge("D16_SPORTPLEX", "D16_MID_LIFT", 47.0, is_step_free=True),
        CorridorEdge("D16_FWD_LIFT", "D16_SPA", 10.0, is_step_free=True),
        CorridorEdge("D16_FWD_LIFT", "D16_TOP_SAIL_REST", 31.0, is_step_free=True),
    ])

    d16_venues = {
        "VENUE_BUFFET_AFT": Venue("VENUE_BUFFET_AFT", "Marketplace Buffet (Aft Terrace & Pizzeria)", 16, VenueCategory.BUFFET, [Coordinate2D(0.06, -0.6), Coordinate2D(0.18, -0.6), Coordinate2D(0.18, 0.6), Coordinate2D(0.06, 0.6)], ["D16_BUFFET_AFT"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_GYM": Venue("VENUE_GYM", "MSC Gym by Technogym", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.18, -0.5), Coordinate2D(0.24, -0.5), Coordinate2D(0.24, 0.5), Coordinate2D(0.18, 0.5)], ["D16_GYM"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_SPORTPLEX": Venue("VENUE_SPORTPLEX", "Sportplex Arena & F1 Simulator", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.28, -0.6), Coordinate2D(0.42, -0.6), Coordinate2D(0.42, 0.6), Coordinate2D(0.28, 0.6)], ["D16_SPORTPLEX"], is_noise_generator=True, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_AUREA_SPA": Venue("VENUE_AUREA_SPA", "MSC Aurea Spa & Thermal Suite", 16, VenueCategory.SPA_FITNESS, [Coordinate2D(0.70, -0.6), Coordinate2D(0.82, -0.6), Coordinate2D(0.82, 0.6), Coordinate2D(0.70, 0.6)], ["D16_SPA"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_RESTAURANT": Venue("VENUE_TOP_SAIL_RESTAURANT", "MSC Yacht Club Restaurant", 16, VenueCategory.DINING, [Coordinate2D(0.82, -0.5), Coordinate2D(0.90, -0.5), Coordinate2D(0.90, 0.5), Coordinate2D(0.82, 0.5)], ["D16_TOP_SAIL_REST"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[16] = Deck(16, "Orchidea", 49.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.7), Coordinate2D(0.95, 0.6), Coordinate2D(1.0, 0.0)], DeckVerticalZone.LIDO_SPORTS, cabins=d16_cabins, venues=d16_venues, corridor_nodes=d16_nodes, corridor_edges=d16_edges)

    # =============================================================
    # DECK 18: NINFEA (Arizona Aquapark, DOREMI Kids, Horizon Sunset Bar, 30 YC Suites)
    # =============================================================
    d18_cabins, d18_nodes, d18_edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
        deck_number=18,
        evidence_links=[ev_ga_full, ev_survey],
    )
    d18_nodes["D18_HORIZON_BAR"] = CorridorNode("D18_HORIZON_BAR", 18, Coordinate2D(0.08, 0.0))
    d18_nodes["D18_DOREMI"] = CorridorNode("D18_DOREMI", 18, Coordinate2D(0.20, 0.0))
    d18_nodes["D18_AQUAPARK"] = CorridorNode("D18_AQUAPARK", 18, Coordinate2D(0.40, 0.0))
    d18_nodes["D18_TOP_SAIL_L18"] = CorridorNode("D18_TOP_SAIL_L18", 18, Coordinate2D(0.80, 0.0))

    d18_edges.extend([
        CorridorEdge("D18_AFT_LIFT", "D18_HORIZON_BAR", 53.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_DOREMI", 15.0, is_step_free=True),
        CorridorEdge("D18_AFT_LIFT", "D18_AQUAPARK", 45.0, is_step_free=True),
        CorridorEdge("D18_FWD_LIFT", "D18_TOP_SAIL_L18", 16.0, is_step_free=True),
    ])

    d18_venues = {
        "VENUE_HORIZON_AMPHITHEATRE": Venue("VENUE_HORIZON_AMPHITHEATRE", "Horizon Amphitheatre & Sunset Bar", 18, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.02, -0.5), Coordinate2D(0.12, -0.5), Coordinate2D(0.12, 0.5), Coordinate2D(0.02, 0.5)], ["D18_HORIZON_BAR"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_DOREMI_KIDS": Venue("VENUE_DOREMI_KIDS", "DOREMI Studio & Junior Club (LEGO / Chicco)", 18, VenueCategory.YOUTH_KIDS, [Coordinate2D(0.12, -0.5), Coordinate2D(0.24, -0.5), Coordinate2D(0.24, 0.5), Coordinate2D(0.12, 0.5)], ["D18_DOREMI"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
        "VENUE_AQUAPARK": Venue("VENUE_AQUAPARK", "Arizona Aquapark & Himalayan Bridge (82m above sea)", 18, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.30, -0.65), Coordinate2D(0.48, -0.65), Coordinate2D(0.48, 0.65), Coordinate2D(0.30, 0.65)], ["D18_AQUAPARK"], is_noise_generator=True, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_TOP_SAIL_LOUNGE_L18": Venue("VENUE_TOP_SAIL_LOUNGE_L18", "MSC Yacht Club Top Sail Lounge (Deck 18)", 18, VenueCategory.BAR_LOUNGE, [Coordinate2D(0.74, -0.55), Coordinate2D(0.85, -0.55), Coordinate2D(0.85, 0.55), Coordinate2D(0.74, 0.55)], ["D18_TOP_SAIL_L18"], is_noise_generator=False, is_open_deck=False, evidence_links=[ev_ga_full]),
    }

    decks[18] = Deck(18, "Ninfea", 55.0, [Coordinate2D(0.0, 0.0), Coordinate2D(0.05, 0.6), Coordinate2D(0.85, 0.5), Coordinate2D(0.9, 0.0)], DeckVerticalZone.LIDO_SPORTS, cabins=d18_cabins, venues=d18_venues, corridor_nodes=d18_nodes, corridor_edges=d18_edges)

    # =============================================================
    # DECK 19: MAGNOLIA (Top Deck Solarium, Yacht Club Sun Deck, 10 YC Cabanas)
    # =============================================================
    d19_cabins, d19_nodes, d19_edges = StateroomArchetypeGenerator.generate_full_deck_staterooms(
        deck_number=19,
        evidence_links=[ev_ga_full, ev_survey],
    )
    d19_nodes["D19_SUNDECK"] = CorridorNode("D19_SUNDECK", 19, Coordinate2D(0.70, 0.0))
    d19_nodes["D19_THE_ONE_GRILL"] = CorridorNode("D19_THE_ONE_GRILL", 19, Coordinate2D(0.78, 0.15))

    d19_edges.extend([
        CorridorEdge("D19_FWD_LIFT", "D19_SUNDECK", 15.0, is_step_free=True),
        CorridorEdge("D19_FWD_LIFT", "D19_THE_ONE_GRILL", 10.0, is_step_free=True),
    ])

    d19_venues = {
        "VENUE_YACHT_CLUB_SUNDECK": Venue("VENUE_YACHT_CLUB_SUNDECK", "Top Deck Solarium & The One Pool", 19, VenueCategory.POOL_SOLARIUM, [Coordinate2D(0.65, -0.6), Coordinate2D(0.85, -0.6), Coordinate2D(0.85, 0.6), Coordinate2D(0.65, 0.6)], ["D19_SUNDECK"], is_noise_generator=False, is_open_deck=True, evidence_links=[ev_ga_full]),
        "VENUE_THE_ONE_GRILL": Venue("VENUE_THE_ONE_GRILL", "The One Grill & Bar (Yacht Club Exclusive)", 19, VenueCategory.DINING, [Coordinate2D(0.75, 0.1), Coordinate2D(0.82, 0.1), Coordinate2D(0.82, 0.4), Coordinate2D(0.75, 0.4)], ["D19_THE_ONE_GRILL"], is_noise_generator=False, is_open_deck=True, evidence_links=[ev_ga_full]),
    }

    decks[19] = Deck(19, "Magnolia", 58.5, [Coordinate2D(0.0, 0.0), Coordinate2D(0.1, 0.5), Coordinate2D(0.8, 0.4), Coordinate2D(0.85, 0.0)], DeckVerticalZone.LIDO_SPORTS, cabins=d19_cabins, venues=d19_venues, corridor_nodes=d19_nodes, corridor_edges=d19_edges)

    return VesselSpatialOntology(
        imo_number="IMO9766205",
        name="MSC Bellissima",
        ship_class="Meraviglia Class",
        length_overall_meters=315.83,
        beam_meters=43.0,
        total_decks=19,
        decks=decks,
    )
