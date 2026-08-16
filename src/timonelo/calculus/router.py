"""
Spatial Calculus Router (Plane 3 per ADR-0001).
Deterministic multi-deck graph routing algorithm (Dijkstra) computing exact walking distances and transitions.
Zero subjective opinions, zero machine learning. Pure mathematics.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
import heapq
from ..ontology.models import VesselSpatialOntology, Deck, CorridorEdge, CorridorNode


@dataclass(frozen=True)
class RouteStep:
    from_node_id: str
    to_node_id: str
    distance_meters: float
    description: str
    is_vertical_transition: bool = False
    is_step_free: bool = True


@dataclass(frozen=True)
class WayfindingRoute:
    origin_node_id: str
    destination_node_id: str
    total_distance_meters: float
    estimated_walking_seconds: float
    estimated_step_count: int
    is_fully_step_free: bool
    steps: List[RouteStep]


class DeterministicSpatialRouter:
    """Computes exact, reproducible walking paths across contiguous and vertical ship nodes."""

    def __init__(self, ontology: VesselSpatialOntology, walking_speed_mps: float = 1.25, step_length_m: float = 0.75):
        self.ontology = ontology
        self.walking_speed_mps = walking_speed_mps
        self.step_length_m = step_length_m
        self._adjacency_map: Dict[str, List[Tuple[str, float, bool, bool]]] = {}
        self._node_deck_map: Dict[str, int] = {}
        self._node_core_map: Dict[str, Optional[str]] = {}
        self._build_graph()

    def _build_graph(self) -> None:
        """Constructs the unified topological graph including vertical cores across decks."""
        # 1. Add horizontal corridor edges
        for deck_num, deck in self.ontology.decks.items():
            for node_id, node in deck.corridor_nodes.items():
                self._node_deck_map[node_id] = deck_num
                self._node_core_map[node_id] = node.vertical_core_id
                if node_id not in self._adjacency_map:
                    self._adjacency_map[node_id] = []

            for edge in deck.corridor_edges:
                # Undirected walkable corridor
                self._adjacency_map[edge.from_node_id].append(
                    (edge.to_node_id, edge.distance_meters, edge.is_step_free, False)
                )
                self._adjacency_map[edge.to_node_id].append(
                    (edge.from_node_id, edge.distance_meters, edge.is_step_free, False)
                )

        # 2. Add vertical elevator / stair core connections between matching cores
        vertical_cores: Dict[str, List[str]] = {}
        for node_id, core_id in self._node_core_map.items():
            if core_id:
                vertical_cores.setdefault(core_id, []).append(node_id)

        for core_id, core_nodes in vertical_cores.items():
            for i in range(len(core_nodes)):
                for j in range(i + 1, len(core_nodes)):
                    n1 = core_nodes[i]
                    n2 = core_nodes[j]
                    d1 = self.ontology.decks[self._node_deck_map[n1]].elevation_meters
                    d2 = self.ontology.decks[self._node_deck_map[n2]].elevation_meters
                    vertical_dist = abs(d1 - d2)
                    # Elevator core: Step-free, weight equivalent to vertical distance
                    self._adjacency_map[n1].append((n2, vertical_dist, True, True))
                    self._adjacency_map[n2].append((n1, vertical_dist, True, True))

    def find_shortest_path(self, origin_node_id: str, destination_node_id: str, step_free_only: bool = False) -> Optional[WayfindingRoute]:
        """Executes deterministic Dijkstra shortest path algorithm."""
        if origin_node_id not in self._adjacency_map or destination_node_id not in self._adjacency_map:
            return None

        # Priority queue stores: (current_cost, current_node, path_steps)
        distances: Dict[str, float] = {origin_node_id: 0.0}
        pq: List[Tuple[float, str, List[RouteStep]]] = [(0.0, origin_node_id, [])]
        visited: Set[str] = set()

        while pq:
            cost, current, steps = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current == destination_node_id:
                total_dist = cost
                walking_secs = round(total_dist / self.walking_speed_mps, 1)
                steps_count = int(round(total_dist / self.step_length_m))
                is_step_free = all(s.is_step_free for s in steps)
                return WayfindingRoute(
                    origin_node_id=origin_node_id,
                    destination_node_id=destination_node_id,
                    total_distance_meters=round(total_dist, 2),
                    estimated_walking_seconds=walking_secs,
                    estimated_step_count=steps_count,
                    is_fully_step_free=is_step_free,
                    steps=steps,
                )

            for neighbor, weight, edge_step_free, is_vertical in self._adjacency_map.get(current, []):
                if step_free_only and not edge_step_free:
                    continue

                new_cost = cost + weight
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    desc = f"Vertical transit from Deck {self._node_deck_map[current]} to Deck {self._node_deck_map[neighbor]}" if is_vertical else f"Walk corridor from {current} to {neighbor} ({weight:.1f}m)"
                    new_step = RouteStep(
                        from_node_id=current,
                        to_node_id=neighbor,
                        distance_meters=weight,
                        description=desc,
                        is_vertical_transition=is_vertical,
                        is_step_free=edge_step_free,
                    )
                    heapq.heappush(pq, (new_cost, neighbor, steps + [new_step]))

        return None
