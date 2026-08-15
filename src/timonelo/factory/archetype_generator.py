"""
Knowledge Factory Stage 03/04: Industrial-Scale Stateroom Archetype Generator.
Generates fully classified, non-overlapping staterooms across all decks of Meraviglia-class vessels.
Follows naval architectural rules defined in docs/BELLISSIMA_NUMBERING.md.
"""

from typing import Dict, List, Tuple, Optional
from timonelo.ontology.models import (
    Cabin,
    Coordinate2D,
    DoorNode,
    CorridorNode,
    CorridorEdge,
    HullSide,
    BalconyType,
    PowerSocketMatrix,
    EvidenceLink,
)


class StateroomArchetypeGenerator:
    """Industrial generator for ship-scale stateroom ontologies."""

    @staticmethod
    def generate_full_deck_staterooms(
        deck_number: int,
        evidence_links: List[EvidenceLink],
    ) -> Tuple[Dict[str, Cabin], Dict[str, CorridorNode], List[CorridorEdge]]:
        """
        Generates staterooms and circulation graph for a residential deck tier.
        Covers Forward (Bow), Midship, and Aft corridor stations.
        """
        cabins: Dict[str, Cabin] = {}
        nodes: Dict[str, CorridorNode] = {}
        edges: List[CorridorEdge] = []

        # 1. Base Vertical Elevator Cores (Aft, Mid, Forward)
        core_aft = f"D{deck_number:02d}_AFT_LIFT"
        core_mid = f"D{deck_number:02d}_MID_LIFT"
        core_fwd = f"D{deck_number:02d}_FWD_LIFT"

        nodes[core_aft] = CorridorNode(core_aft, deck_number, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_AFT")
        nodes[core_mid] = CorridorNode(core_mid, deck_number, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_MID")
        nodes[core_fwd] = CorridorNode(core_fwd, deck_number, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_FWD")

        # Longitudinal elevator connections
        edges.append(CorridorEdge(core_aft, core_mid, 78.0, is_step_free=True))
        edges.append(CorridorEdge(core_mid, core_fwd, 78.0, is_step_free=True))

        # 2. Establish Corridor Wayfinding Nodes
        corr_stbd_aft = f"D{deck_number:02d}_AFT_CORR_STBD_1"
        corr_port_aft = f"D{deck_number:02d}_AFT_CORR_PORT_1"
        corr_stbd_mid = f"D{deck_number:02d}_MID_CORR_STBD_1"
        corr_port_mid = f"D{deck_number:02d}_MID_CORR_PORT_1"
        corr_stbd_fwd = f"D{deck_number:02d}_FWD_CORR_STBD_1"
        corr_port_fwd = f"D{deck_number:02d}_FWD_CORR_PORT_1"

        nodes[corr_stbd_aft] = CorridorNode(corr_stbd_aft, deck_number, Coordinate2D(0.28, 0.35))
        nodes[corr_port_aft] = CorridorNode(corr_port_aft, deck_number, Coordinate2D(0.28, -0.35))
        nodes[corr_stbd_mid] = CorridorNode(corr_stbd_mid, deck_number, Coordinate2D(0.53, 0.35))
        nodes[corr_port_mid] = CorridorNode(corr_port_mid, deck_number, Coordinate2D(0.53, -0.35))
        nodes[corr_stbd_fwd] = CorridorNode(corr_stbd_fwd, deck_number, Coordinate2D(0.78, 0.35))
        nodes[corr_port_fwd] = CorridorNode(corr_port_fwd, deck_number, Coordinate2D(0.78, -0.35))

        edges.extend([
            CorridorEdge(core_aft, corr_stbd_aft, 12.5, is_step_free=True),
            CorridorEdge(core_aft, corr_port_aft, 12.5, is_step_free=True),
            CorridorEdge(core_mid, corr_stbd_mid, 12.5, is_step_free=True),
            CorridorEdge(core_mid, corr_port_mid, 12.5, is_step_free=True),
            CorridorEdge(core_fwd, corr_stbd_fwd, 12.5, is_step_free=True),
            CorridorEdge(core_fwd, corr_port_fwd, 12.5, is_step_free=True),
        ])

        # Standard Power Matrices
        socket_std = PowerSocketMatrix(eu_standard_count=2, us_standard_count=2, usb_a_count=2, usb_c_count=1, bedside_usb_available=True)
        socket_acc = PowerSocketMatrix(eu_standard_count=3, us_standard_count=3, usb_a_count=3, usb_c_count=2, bedside_usb_available=True)
        socket_suite = PowerSocketMatrix(eu_standard_count=4, us_standard_count=4, usb_a_count=4, usb_c_count=2, bedside_usb_available=True)

        has_lifeboats = (deck_number == 8)
        default_balcony = BalconyType.PARTIAL_OBSTRUCTION_LIFEBOAT if has_lifeboats else BalconyType.UNOBSTRUCTED

        # 3. Generate Staterooms across Station Ranges
        # Ranges: Forward (002-046), Mid (048-120), Aft (122-250)
        station_configs = [
            # Zone 1: Forward (Bow) -> Snaps to FWD lift
            ("FWD", 2, 48, corr_stbd_fwd, corr_port_fwd, 0.72, 0.90),
            # Zone 2: Midship -> Snaps to MID lift
            ("MID", 48, 120, corr_stbd_mid, corr_port_mid, 0.38, 0.71),
            # Zone 3: Aft (Stern) -> Snaps to AFT lift
            ("AFT", 120, 252, corr_stbd_aft, corr_port_aft, 0.15, 0.38),
        ]

        # Specific Accessible numbers per Meraviglia GA layout
        accessible_staterooms = {
            f"{deck_number}006", f"{deck_number}008", f"{deck_number}010",
            f"{deck_number}121", f"{deck_number}123", f"{deck_number}125",
            f"{deck_number}216", f"{deck_number}218"
        }

        # Specific Connecting Pairs
        connecting_pairs = [
            (f"{deck_number}088", f"{deck_number}090"),
            (f"{deck_number}089", f"{deck_number}091"),
            (f"{deck_number}120", f"{deck_number}122"),
            (f"{deck_number}119", f"{deck_number}121"),
            (f"{deck_number}180", f"{deck_number}182"),
            (f"{deck_number}179", f"{deck_number}181"),
        ]
        conn_map = {}
        for c1, c2 in connecting_pairs:
            conn_map[c1] = c2
            conn_map[c2] = c1

        for zone_name, start_idx, end_idx, stbd_corr, port_corr, x_min, x_max in station_configs:
            step_count = (end_idx - start_idx) // 2
            x_delta = (x_max - x_min) / max(step_count, 1)

            # Generate Starboard (Even) and Port (Odd) cabins
            for idx in range(start_idx, end_idx, 2):
                fraction_idx = (idx - start_idx) // 2
                x_pos = x_min + (fraction_idx * x_delta)

                # --- STARBOARD (EVEN) ---
                c_num_stbd = f"{deck_number}{idx:03d}"
                is_acc_stbd = c_num_stbd in accessible_staterooms
                is_suite_stbd = (idx <= 12)
                cat_stbd = "SL1" if is_suite_stbd else ("BA_ACC" if is_acc_stbd else ("OB" if has_lifeboats else "BA"))
                area_stbd = 27.0 if is_suite_stbd else (28.0 if is_acc_stbd else 19.0)
                width_stbd = 950 if is_acc_stbd else (900 if is_suite_stbd else 850)
                socket_m_stbd = socket_acc if is_acc_stbd else (socket_suite if is_suite_stbd else socket_std)

                poly_stbd = [
                    Coordinate2D(x_pos - 0.003, 0.35),
                    Coordinate2D(x_pos + 0.003, 0.35),
                    Coordinate2D(x_pos + 0.003, 0.65),
                    Coordinate2D(x_pos - 0.003, 0.65),
                ]
                door_stbd = DoorNode(
                    door_id=f"DOOR_{c_num_stbd}",
                    deck_number=deck_number,
                    coordinate=Coordinate2D(x_pos, 0.35),
                    corridor_snap_node_id=stbd_corr,
                    clear_width_mm=width_stbd,
                )
                cabins[c_num_stbd] = Cabin(
                    cabin_number=c_num_stbd,
                    deck_number=deck_number,
                    hull_side=HullSide.STARBOARD,
                    category_code=cat_stbd,
                    boundary_polygon=poly_stbd,
                    door=door_stbd,
                    square_meters=area_stbd,
                    balcony_type=default_balcony,
                    sockets=socket_m_stbd,
                    connecting_cabin_number=conn_map.get(c_num_stbd),
                    bed_near_balcony=(idx % 4 == 2),
                    is_accessible_stateroom=is_acc_stbd,
                    evidence_links=evidence_links,
                )

                # --- PORT (ODD) ---
                port_idx = idx - 1 if idx > start_idx else idx + 1
                c_num_port = f"{deck_number}{port_idx:03d}"
                is_acc_port = c_num_port in accessible_staterooms
                is_suite_port = (port_idx <= 11)
                cat_port = "SL1" if is_suite_port else ("BA_ACC" if is_acc_port else ("OB" if has_lifeboats else "BA"))
                area_port = 27.0 if is_suite_port else (28.0 if is_acc_port else 19.0)
                width_port = 950 if is_acc_port else (900 if is_suite_port else 850)
                socket_m_port = socket_acc if is_acc_port else (socket_suite if is_suite_port else socket_std)

                poly_port = [
                    Coordinate2D(x_pos - 0.003, -0.65),
                    Coordinate2D(x_pos + 0.003, -0.65),
                    Coordinate2D(x_pos + 0.003, -0.35),
                    Coordinate2D(x_pos - 0.003, -0.35),
                ]
                door_port = DoorNode(
                    door_id=f"DOOR_{c_num_port}",
                    deck_number=deck_number,
                    coordinate=Coordinate2D(x_pos, -0.35),
                    corridor_snap_node_id=port_corr,
                    clear_width_mm=width_port,
                )
                cabins[c_num_port] = Cabin(
                    cabin_number=c_num_port,
                    deck_number=deck_number,
                    hull_side=HullSide.PORT,
                    category_code=cat_port,
                    boundary_polygon=poly_port,
                    door=door_port,
                    square_meters=area_port,
                    balcony_type=default_balcony,
                    sockets=socket_m_port,
                    connecting_cabin_number=conn_map.get(c_num_port),
                    bed_near_balcony=(port_idx % 4 == 1),
                    is_accessible_stateroom=is_acc_port,
                    evidence_links=evidence_links,
                )

        return cabins, nodes, edges
