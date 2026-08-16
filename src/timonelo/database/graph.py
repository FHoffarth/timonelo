"""
Cruise Knowledge Graph Engine.
Constructs, indexes, validates, and queries the multi-layer maritime knowledge graph.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple
import json
import os


class RelationType(str, Enum):
    # Structural & Hierarchical
    BELONGS_TO = "BELONGS_TO"
    PART_OF = "PART_OF"
    CONTAINS = "CONTAINS"
    LOCATED_ON = "LOCATED_ON"
    CONNECTED_TO = "CONNECTED_TO"
    
    # Spatial & Adjacency
    NEXT_TO = "NEXT_TO"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    NEAREST_TO = "NEAREST_TO"
    SERVED_BY = "SERVED_BY"
    SERVES = "SERVES"
    
    # Itinerary & Maritime Logistics
    CALLS_AT = "CALLS_AT"
    STARTS_AT = "STARTS_AT"
    ENDS_AT = "ENDS_AT"
    OPERATED_BY = "OPERATED_BY"
    BUILT_BY = "BUILT_BY"
    SISTER_OF = "SISTER_OF"
    SUBCLASS_OF = "SUBCLASS_OF"
    HAS_PARENT_CLASS = "HAS_PARENT_CLASS"
    HAS_CHILD_CLASS = "HAS_CHILD_CLASS"
    
    # Sensory & Accessibility Profiles
    HAS_VIEW = "HAS_VIEW"
    HAS_NOISE_PROFILE = "HAS_NOISE_PROFILE"
    HAS_ACCESSIBILITY = "HAS_ACCESSIBILITY"
    
    # Operational & Dynamic Fleet Logistics
    OPERATES_IN = "OPERATES_IN"
    DEPLOYED_TO = "DEPLOYED_TO"
    VISITS = "VISITS"
    CURRENTLY_AT = "CURRENTLY_AT"
    NEXT_CALL = "NEXT_CALL"
    STARTS_VOYAGE = "STARTS_VOYAGE"
    ENDS_VOYAGE = "ENDS_VOYAGE"
    TURNAROUND_AT = "TURNAROUND_AT"

    # Provenance & Trust
    HAS_SOURCE = "HAS_SOURCE"
    VERIFIED_BY = "VERIFIED_BY"


@dataclass(frozen=True)
class GraphNode:
    id: str
    node_type: str  # "Ship", "ShipClass", "Deck", "Cabin", "Venue", "Port", "Terminal", "Route", "Source"
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    semantic_tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    relation: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    trust_level: str = "OFFICIAL"
    source_ref: Optional[str] = None


class CruiseKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adj_out: Dict[str, List[GraphEdge]] = {}
        self._adj_in: Dict[str, List[GraphEdge]] = {}
        self._inverted_semantic_index: Dict[str, Set[str]] = {}

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node
        if node.id not in self._adj_out:
            self._adj_out[node.id] = []
        if node.id not in self._adj_in:
            self._adj_in[node.id] = []
        
        # Index semantic tags
        for tag in node.semantic_tags:
            t = tag.lower().strip()
            if t not in self._inverted_semantic_index:
                self._inverted_semantic_index[t] = set()
            self._inverted_semantic_index[t].add(node.id)

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)
        if edge.source_id not in self._adj_out:
            self._adj_out[edge.source_id] = []
        self._adj_out[edge.source_id].append(edge)

        if edge.target_id not in self._adj_in:
            self._adj_in[edge.target_id] = []
        self._adj_in[edge.target_id].append(edge)

    def get_outgoing_edges(self, node_id: str, relation: Optional[RelationType] = None) -> List[GraphEdge]:
        edges = self._adj_out.get(node_id, [])
        if relation is None:
            return edges
        return [e for e in edges if e.relation == relation]

    def get_incoming_edges(self, node_id: str, relation: Optional[RelationType] = None) -> List[GraphEdge]:
        edges = self._adj_in.get(node_id, [])
        if relation is None:
            return edges
        return [e for e in edges if e.relation == relation]

    def semantic_search(self, query: str) -> List[GraphNode]:
        tokens = query.lower().strip().split()
        matched_ids: Set[str] = set()
        for token in tokens:
            for tag, node_ids in self._inverted_semantic_index.items():
                if token in tag:
                    matched_ids.update(node_ids)
        return [self.nodes[nid] for nid in matched_ids if nid in self.nodes]

    def validate_integrity(self) -> Tuple[List[str], List[str]]:
        """Validate that all edge endpoints exist and no orphaned links exist."""
        errors: List[str] = []
        warnings: List[str] = []

        for edge in self.edges:
            if edge.source_id not in self.nodes:
                errors.append(f"Broken edge source: '{edge.source_id}' does not exist in graph nodes.")
            if edge.target_id not in self.nodes:
                errors.append(f"Broken edge target: '{edge.target_id}' does not exist in graph nodes.")

        # Check for isolated nodes
        for nid, node in self.nodes.items():
            deg_out = len(self._adj_out.get(nid, []))
            deg_in = len(self._adj_in.get(nid, []))
            if deg_out == 0 and deg_in == 0 and node.node_type != "Source":
                warnings.append(f"Isolated node in graph: '{nid}' ({node.node_type}) has zero relationships.")

        return errors, warnings

    def export_graph_json(self) -> Dict[str, Any]:
        """Export serialized graph structure and topological metrics."""
        return {
            "statistics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": self._count_node_types(),
                "relation_types": self._count_relation_types(),
            },
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type,
                    "label": n.label,
                    "attributes": n.attributes,
                    "semantic_tags": n.semantic_tags,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "relation": e.relation.value,
                    "weight": e.weight,
                    "trust_level": e.trust_level,
                    "source_ref": e.source_ref,
                }
                for e in self.edges
            ],
        }

    def _count_node_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for n in self.nodes.values():
            counts[n.node_type] = counts.get(n.node_type, 0) + 1
        return counts

    def _count_relation_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.edges:
            counts[e.relation.value] = counts.get(e.relation.value, 0) + 1
        return counts


class KnowledgeGraphBuilder:
    """Builds the interconnected multi-plane knowledge graph from compiled database."""

    def __init__(self, raw_db: Dict[str, Any]):
        self.raw_db = raw_db
        self.graph = CruiseKnowledgeGraph()

    def build(self) -> CruiseKnowledgeGraph:
        self._build_source_nodes()
        self._build_shipyard_nodes()
        self._build_region_nodes()
        self._build_class_nodes()
        self._build_ship_nodes()
        self._build_port_nodes()
        self._build_route_nodes()
        self._build_venue_nodes()
        self._build_deck_and_cabin_nodes()
        return self.graph

    def _build_source_nodes(self):
        for sid, src in self.raw_db.get("sources", {}).items():
            self.graph.add_node(
                GraphNode(
                    id=sid,
                    node_type="Source",
                    label=src.get("title", sid),
                    attributes=src,
                    semantic_tags=["source", src.get("category", "").lower()],
                )
            )

    def _build_shipyard_nodes(self):
        for yid, yard in self.raw_db.get("shipyards", {}).items():
            self.graph.add_node(
                GraphNode(
                    id=f"yard:{yid}",
                    node_type="Shipyard",
                    label=yard.get("name", yid),
                    attributes=yard,
                    semantic_tags=["shipyard", "builder", yard.get("name", "").lower(), yard.get("country", "").lower()],
                )
            )

    def _build_region_nodes(self):
        for rid, reg in self.raw_db.get("regions", {}).items():
            self.graph.add_node(
                GraphNode(
                    id=f"region:{rid}",
                    node_type="Region",
                    label=reg.get("name", rid),
                    attributes=reg,
                    semantic_tags=["region", "destination", reg.get("name", "").lower()],
                )
            )

    def _build_class_nodes(self):
        for cid, sclass in self.raw_db.get("ship_classes", {}).items():
            node_id = f"class:{cid}"
            self.graph.add_node(
                GraphNode(
                    id=node_id,
                    node_type="ShipClass",
                    label=sclass.get("name", cid),
                    attributes=sclass,
                    semantic_tags=[
                        "class",
                        sclass.get("name", "").lower(),
                        sclass.get("operator", "").lower(),
                        sclass.get("category", "").lower(),
                    ],
                )
            )

    def _build_ship_nodes(self):
        for sid, ship in self.raw_db.get("ships", {}).items():
            ship_id = f"ship:{sid}"
            name_val = ship.get("name", {}).get("value") if isinstance(ship.get("name"), dict) else ship.get("name", sid)
            operator_val = ship.get("operator", {}).get("value") if isinstance(ship.get("operator"), dict) else ship.get("operator", "")
            class_id = ship.get("class_id") or ship.get("ship_class")

            self.graph.add_node(
                GraphNode(
                    id=ship_id,
                    node_type="Ship",
                    label=name_val,
                    attributes=ship,
                    semantic_tags=[
                        "ship",
                        "vessel",
                        name_val.lower(),
                        operator_val.lower(),
                        sid.lower(),
                    ],
                )
            )

            # Link Ship -> Class
            if class_id:
                class_node_id = f"class:{class_id}"
                if class_node_id in self.graph.nodes:
                    self.graph.add_edge(
                        GraphEdge(source_id=ship_id, target_id=class_node_id, relation=RelationType.BELONGS_TO)
                    )

            # Link Ship -> Calling Ports
            for port_slug in ship.get("homeports", []):
                port_node_id = f"port:{port_slug}"
                self.graph.add_edge(
                    GraphEdge(source_id=ship_id, target_id=port_node_id, relation=RelationType.CALLS_AT)
                )

    def _build_port_nodes(self):
        for pid, port in self.raw_db.get("ports", {}).items():
            port_id = f"port:{pid}"
            name = port.get("name", pid)
            country = port.get("country", "")
            un_locode = port.get("un_locode", "")

            self.graph.add_node(
                GraphNode(
                    id=port_id,
                    node_type="Port",
                    label=name,
                    attributes=port,
                    semantic_tags=[
                        "port",
                        "destination",
                        "terminal",
                        name.lower(),
                        country.lower(),
                        un_locode.lower(),
                        pid.lower(),
                    ],
                )
            )

            # Terminals inside port
            for idx, term in enumerate(port.get("terminals", [])):
                term_id = f"terminal:{pid}:{idx}"
                self.graph.add_node(
                    GraphNode(
                        id=term_id,
                        node_type="Terminal",
                        label=term.get("name", f"{name} Terminal"),
                        attributes=term,
                        semantic_tags=["terminal", "quay", "berth", "gangway", name.lower()],
                    )
                )
                self.graph.add_edge(
                    GraphEdge(source_id=term_id, target_id=port_id, relation=RelationType.LOCATED_ON)
                )

    def _build_route_nodes(self):
        for rid, route in self.raw_db.get("routes", {}).items():
            route_id = f"route:{rid}"
            title = route.get("title", rid)

            self.graph.add_node(
                GraphNode(
                    id=route_id,
                    node_type="Route",
                    label=title,
                    attributes=route,
                    semantic_tags=["route", "itinerary", "cruise", title.lower(), rid.lower()],
                )
            )

            for entry in route.get("ports_sequence", []):
                pslug = entry.get("port_slug")
                if pslug and pslug != "sea-day":
                    port_node_id = f"port:{pslug}"
                    self.graph.add_edge(
                        GraphEdge(source_id=route_id, target_id=port_node_id, relation=RelationType.CALLS_AT)
                    )

    def _build_venue_nodes(self):
        for vid, venue in self.raw_db.get("venues", {}).items():
            venue_id = f"venue:{vid}"
            vname = venue.get("name", vid)
            ship_slug = venue.get("ship_slug")

            tags = ["venue", vname.lower(), venue.get("venue_type", "").lower()]
            for feat in venue.get("features", []):
                tags.append(feat.lower())

            self.graph.add_node(
                GraphNode(
                    id=venue_id,
                    node_type="Venue",
                    label=vname,
                    attributes=venue,
                    semantic_tags=tags,
                )
            )

            if ship_slug:
                ship_node_id = f"ship:{ship_slug}"
                self.graph.add_edge(
                    GraphEdge(source_id=venue_id, target_id=ship_node_id, relation=RelationType.LOCATED_ON)
                )

    def _build_deck_and_cabin_nodes(self):
        """Construct vertical deck stack and sample stateroom nodes for reference flagship."""
        ship_id = "ship:msc-bellissima"
        if ship_id not in self.graph.nodes:
            return

        # Decks 4 through 19 on MSC Bellissima
        deck_names = {
            4: "Dante", 5: "Corbett", 6: "Leonardo da Vinci", 7: "Michelangelo",
            8: "Raffaello", 9: "Botticelli", 10: "Arcimboldo", 11: "Caravaggio",
            12: "Giotto", 13: "Piero della Francesca", 14: "Tiziano", 15: "Tintoretto",
            16: "Tiepolo", 18: "Canaletto", 19: "London"
        }

        prev_deck_id = None
        for dnum, dname in deck_names.items():
            deck_id = f"deck:msc-bellissima:{dnum}"
            self.graph.add_node(
                GraphNode(
                    id=deck_id,
                    node_type="Deck",
                    label=f"Deck {dnum} · {dname}",
                    attributes={"deck_number": dnum, "deck_name": dname, "ship_slug": "msc-bellissima"},
                    semantic_tags=["deck", f"deck {dnum}", dname.lower(), "msc bellissima"],
                )
            )
            self.graph.add_edge(
                GraphEdge(source_id=deck_id, target_id=ship_id, relation=RelationType.PART_OF)
            )

            # Vertical adjacency edge
            if prev_deck_id:
                self.graph.add_edge(
                    GraphEdge(source_id=deck_id, target_id=prev_deck_id, relation=RelationType.ABOVE)
                )
                self.graph.add_edge(
                    GraphEdge(source_id=prev_deck_id, target_id=deck_id, relation=RelationType.BELOW)
                )
            prev_deck_id = deck_id

        # Flagship Stateroom Cabin 14122
        cabin_id = "cabin:msc-bellissima:14122"
        deck_14_id = "deck:msc-bellissima:14"
        self.graph.add_node(
            GraphNode(
                id=cabin_id,
                node_type="Cabin",
                label="Cabin 14122 (Balcony Stateroom)",
                attributes={
                    "cabin_number": "14122",
                    "deck_number": 14,
                    "deck_name": "Tiziano",
                    "category": "Balcony Deluxe",
                    "hull_side": "STARBOARD",
                    "zone": "AFT",
                    "square_meters": 19.0,
                    "nearest_elevator_m": 25.0,
                },
                semantic_tags=["cabin", "stateroom", "14122", "balcony", "deck 14", "starboard", "aft"],
            )
        )
        self.graph.add_edge(
            GraphEdge(source_id=cabin_id, target_id=deck_14_id, relation=RelationType.LOCATED_ON)
        )
        self.graph.add_edge(
            GraphEdge(source_id=cabin_id, target_id=ship_id, relation=RelationType.BELONGS_TO)
        )
