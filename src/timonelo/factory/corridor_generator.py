"""
Knowledge Factory Stage 03/04: Algorithmic Corridor Mesh & Geometry Generator.
Generates non-overlapping cabin boundary polygons and snaps stateroom doors into the circulation graph.
"""

from typing import Dict, List, Tuple
from timonelo.ontology.models import (
    Cabin,
    Coordinate2D,
    DoorNode,
    CorridorNode,
    CorridorEdge,
    HullSide,
    PowerSocketMatrix,
    EvidenceLink,
)
from .manifest_importer import CabinManifestRecord


class CorridorMeshGenerator:
    """Algorithmic spatial generator for residential corridor topologies."""

    @staticmethod
    def generate_deck_topology(
        deck_number: int,
        records: List[CabinManifestRecord],
        evidence: List[EvidenceLink],
    ) -> Tuple[Dict[str, Cabin], Dict[str, CorridorNode], List[CorridorEdge]]:
        """
        Synthesizes verified cabins, corridor nodes, and walkable graph edges for a residential deck.
        """
        cabins: Dict[str, Cabin] = {}
        nodes: Dict[str, CorridorNode] = {}
        edges: List[CorridorEdge] = []

        # 1. Base Vertical Cores (Aft, Mid, Fwd)
        core_aft = f"D{deck_number:02d}_AFT_LIFT"
        core_mid = f"D{deck_number:02d}_MID_LIFT"
        core_fwd = f"D{deck_number:02d}_FWD_LIFT"

        nodes[core_aft] = CorridorNode(core_aft, deck_number, Coordinate2D(0.25, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_AFT")
        nodes[core_mid] = CorridorNode(core_mid, deck_number, Coordinate2D(0.50, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_MID")
        nodes[core_fwd] = CorridorNode(core_fwd, deck_number, Coordinate2D(0.75, 0.0), is_elevator_lobby=True, is_stairwell_access=True, vertical_core_id="CORE_FWD")

        # Longitudinal elevator connections
        edges.append(CorridorEdge(core_aft, core_mid, 78.0, is_step_free=True))
        edges.append(CorridorEdge(core_mid, core_fwd, 78.0, is_step_free=True))

        # 2. Group cabins by HullSide and Station
        for rec in records:
            if rec.deck_number != deck_number:
                continue

            side_sign = 1.0 if rec.hull_side == HullSide.STARBOARD else -1.0
            
            # Determine nearest elevator core
            if rec.station_x_fraction < 0.38:
                assigned_core = core_aft
                corr_station = 0.28
                branch_node_id = f"D{deck_number:02d}_AFT_CORR_STBD_1" if rec.hull_side == HullSide.STARBOARD else f"D{deck_number:02d}_AFT_CORR_PORT_1"
            elif rec.station_x_fraction < 0.63:
                assigned_core = core_mid
                corr_station = 0.53
                branch_node_id = f"D{deck_number:02d}_MID_STBD" if rec.hull_side == HullSide.STARBOARD else f"D{deck_number:02d}_MID_PORT"
            else:
                assigned_core = core_fwd
                corr_station = 0.78
                branch_node_id = f"D{deck_number:02d}_FWD_STBD" if rec.hull_side == HullSide.STARBOARD else f"D{deck_number:02d}_FWD_PORT"

            # Create branch corridor node if not exists
            if branch_node_id not in nodes:
                nodes[branch_node_id] = CorridorNode(
                    branch_node_id,
                    deck_number,
                    Coordinate2D(corr_station, 0.35 * side_sign),
                )
                # Link branch node to elevator core
                edges.append(CorridorEdge(assigned_core, branch_node_id, 12.5, is_step_free=True))

            # 3. Construct Boundary Polygon & Door Node
            x_min = rec.station_x_fraction - 0.005
            x_max = rec.station_x_fraction + 0.005
            y_inner = 0.35 * side_sign
            y_outer = (0.35 + 0.30) * side_sign

            poly = [
                Coordinate2D(x_min, min(y_inner, y_outer)),
                Coordinate2D(x_max, min(y_inner, y_outer)),
                Coordinate2D(x_max, max(y_inner, y_outer)),
                Coordinate2D(x_min, max(y_inner, y_outer)),
            ]

            door_id = f"DOOR_{rec.cabin_number}"
            door_node = DoorNode(
                door_id=door_id,
                deck_number=deck_number,
                coordinate=Coordinate2D(rec.station_x_fraction, y_inner),
                corridor_snap_node_id=branch_node_id,
                clear_width_mm=rec.door_clear_width_mm,
            )

            sockets = PowerSocketMatrix(
                eu_standard_count=rec.eu_sockets,
                us_standard_count=rec.us_sockets,
                usb_a_count=rec.usb_a_sockets,
                usb_c_count=rec.usb_c_sockets,
                bedside_usb_available=rec.bedside_usb,
            )

            cabins[rec.cabin_number] = Cabin(
                cabin_number=rec.cabin_number,
                deck_number=deck_number,
                hull_side=rec.hull_side,
                category_code=rec.category_code,
                boundary_polygon=poly,
                door=door_node,
                square_meters=rec.square_meters,
                balcony_type=rec.balcony_type,
                sockets=sockets,
                connecting_cabin_number=rec.connecting_cabin,
                bed_near_balcony=rec.bed_near_balcony,
                is_accessible_stateroom=rec.is_accessible,
                evidence_links=evidence,
            )

        return cabins, nodes, edges
