"""
Evidence-gated spatial router (Timonelo first routable slice).

Contrast with `timonelo.calculus.router.DeterministicSpatialRouter`, which is
kept unchanged: that router answers "what is the shortest path" and always
produces metres, seconds and a step count. This router answers the prior
question — "may I claim a path at all, and what of it do I actually know" —
and is allowed to answer NOT_ROUTABLE or INSUFFICIENT_EVIDENCE.

Guarantees:
- No route is returned unless every node and edge on it passed the graph's
  admission gate (see `spatial.graph`).
- `total_distance_meters` is populated only when EVERY edge on the path
  carries a metric-qualified length. One missing length collapses the whole
  distance to UNKNOWN — partial sums are not reported.
- Walking time is never produced. Distance alone does not license it; no
  evidenced walking-speed model exists in this repository.
- Accessibility is tri-state. `step_free` is True only when every edge on the
  path is explicitly step-free; a single UNKNOWN edge makes the route's
  accessibility UNKNOWN, never False and never True.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from timonelo.ontology.models import EvidenceLink, GeometryProvenance
from timonelo.spatial.graph import (
    AdmissionRejection,
    SpatialEdge,
    SpatialGraph,
    SpatialNode,
)


class RouteStatus(str, Enum):
    """Outcome of a routing request.

    ROUTABLE               a path exists across admitted nodes and edges
    NOT_ROUTABLE           both endpoints are admitted, but no admitted path connects them
    INSUFFICIENT_EVIDENCE  an endpoint is unknown or was refused admission
    """
    ROUTABLE = "ROUTABLE"
    NOT_ROUTABLE = "NOT_ROUTABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RouteUnknown(str, Enum):
    """Named facts the router refuses to assert about a returned route."""
    METRIC_DISTANCE = "METRIC_DISTANCE"
    STEP_FREE_ACCESSIBILITY = "STEP_FREE_ACCESSIBILITY"
    WALKING_TIME = "WALKING_TIME"


class CostBasis(str, Enum):
    """What the traversal minimised.

    METRIC_METERS  every admitted edge had an evidenced length; the path is
                   shortest by distance
    EDGE_COUNT     at least one admitted edge had no length; the path is
                   shortest by number of connections and carries NO distance
    """
    METRIC_METERS = "METRIC_METERS"
    EDGE_COUNT = "EDGE_COUNT"


@dataclass(frozen=True)
class RouteEvidence:
    """Provenance carried out of the route, per component that produced it."""
    component_id: str
    component_kind: str  # "NODE" | "EDGE"
    geometry_provenance: GeometryProvenance
    evidence_links: Tuple[EvidenceLink, ...]


@dataclass(frozen=True)
class RouteResult:
    status: RouteStatus
    start_node_id: str
    destination_node_id: str
    node_ids: Tuple[str, ...] = ()
    edge_ids: Tuple[str, ...] = ()
    distance_known: bool = False
    total_distance_meters: Optional[float] = None
    step_free: Optional[bool] = None
    cost_basis: Optional[CostBasis] = None
    unknowns: Tuple[RouteUnknown, ...] = ()
    evidence: Tuple[RouteEvidence, ...] = ()
    blocking_reasons: Tuple[str, ...] = ()

    @property
    def is_routable(self) -> bool:
        return self.status == RouteStatus.ROUTABLE


class EvidenceGatedRouter:
    """Deterministic traversal over a `SpatialGraph`, with explicit unknowns."""

    def __init__(self, graph: SpatialGraph) -> None:
        self.graph = graph

    def route(
        self,
        start_node_id: str,
        destination_node_id: str,
        require_step_free: bool = False,
    ) -> RouteResult:
        """Finds a route, or explains why it will not claim one.

        `require_step_free=True` traverses only edges explicitly marked
        step-free. Edges whose accessibility is UNKNOWN are excluded rather
        than optimistically included — an unevidenced connection may not
        become an accessible one.
        """
        endpoint_problems = self._endpoint_problems(start_node_id, destination_node_id)
        if endpoint_problems:
            return RouteResult(
                status=RouteStatus.INSUFFICIENT_EVIDENCE,
                start_node_id=start_node_id,
                destination_node_id=destination_node_id,
                unknowns=(
                    RouteUnknown.METRIC_DISTANCE,
                    RouteUnknown.STEP_FREE_ACCESSIBILITY,
                    RouteUnknown.WALKING_TIME,
                ),
                blocking_reasons=endpoint_problems,
            )

        usable_edge_ids = self._usable_edge_ids(require_step_free)
        cost_basis = (
            CostBasis.METRIC_METERS
            if usable_edge_ids
            and all(self.graph.edge(eid).has_metric_length for eid in usable_edge_ids)
            else CostBasis.EDGE_COUNT
        )

        path = self._search(start_node_id, destination_node_id, usable_edge_ids, cost_basis)
        if path is None:
            return RouteResult(
                status=RouteStatus.NOT_ROUTABLE,
                start_node_id=start_node_id,
                destination_node_id=destination_node_id,
                unknowns=(
                    RouteUnknown.METRIC_DISTANCE,
                    RouteUnknown.STEP_FREE_ACCESSIBILITY,
                    RouteUnknown.WALKING_TIME,
                ),
                blocking_reasons=(
                    "NO_ADMITTED_CONNECTIVITY: no evidenced walkable connection joins "
                    f"{start_node_id} to {destination_node_id}",
                ),
            )

        node_ids, edge_ids = path
        edges = [self.graph.edge(eid) for eid in edge_ids]
        return self._assemble(start_node_id, destination_node_id, node_ids, edge_ids, edges, cost_basis)

    # --- internals -------------------------------------------------------

    def _endpoint_problems(self, start_node_id: str, destination_node_id: str) -> Tuple[str, ...]:
        problems: List[str] = []
        for label, node_id in (("START", start_node_id), ("DESTINATION", destination_node_id)):
            if self.graph.node(node_id) is not None:
                continue
            rejection = self.graph.node_rejection(node_id)
            if rejection:
                reasons = ", ".join(r.value for r in rejection)
                problems.append(f"{label}_NODE_NOT_ADMITTED: {node_id} ({reasons})")
            else:
                problems.append(f"{label}_NODE_UNKNOWN: {node_id} is not an evidenced spatial node")
        return tuple(problems)

    def _usable_edge_ids(self, require_step_free: bool) -> Tuple[str, ...]:
        if not require_step_free:
            return self.graph.edge_ids
        return tuple(
            eid for eid in self.graph.edge_ids if self.graph.edge(eid).step_free is True
        )

    def _search(
        self,
        start_node_id: str,
        destination_node_id: str,
        usable_edge_ids: Tuple[str, ...],
        cost_basis: CostBasis,
    ) -> Optional[Tuple[Tuple[str, ...], Tuple[str, ...]]]:
        """Dijkstra over metres, or uniform-cost search over edge count.

        Ties are broken on node id then edge id, so the result is stable
        regardless of insertion order.
        """
        usable = set(usable_edge_ids)
        if start_node_id == destination_node_id:
            return (start_node_id,), ()

        best: Dict[str, float] = {start_node_id: 0.0}
        # (cost, node_id, node_path, edge_path)
        queue: List[Tuple[float, str, Tuple[str, ...], Tuple[str, ...]]] = [
            (0.0, start_node_id, (start_node_id,), ())
        ]
        settled: set = set()

        while queue:
            cost, current, node_path, edge_path = heapq.heappop(queue)
            if current in settled:
                continue
            settled.add(current)
            if current == destination_node_id:
                return node_path, edge_path

            for neighbour, edge_id in self.graph.neighbours(current):
                if edge_id not in usable or neighbour in settled:
                    continue
                edge = self.graph.edge(edge_id)
                step_cost = (
                    edge.length_meters
                    if cost_basis == CostBasis.METRIC_METERS
                    else 1.0
                )
                new_cost = cost + step_cost
                if neighbour in best and new_cost >= best[neighbour]:
                    continue
                best[neighbour] = new_cost
                heapq.heappush(
                    queue,
                    (new_cost, neighbour, node_path + (neighbour,), edge_path + (edge_id,)),
                )
        return None

    def _assemble(
        self,
        start_node_id: str,
        destination_node_id: str,
        node_ids: Tuple[str, ...],
        edge_ids: Tuple[str, ...],
        edges: List[SpatialEdge],
        cost_basis: CostBasis,
    ) -> RouteResult:
        unknowns: List[RouteUnknown] = []

        # Distance: all-or-nothing. A partial sum would understate the true walk.
        distance_known = bool(edges) and all(e.has_metric_length for e in edges)
        total_distance = (
            round(sum(e.length_meters for e in edges), 3) if distance_known else None
        )
        if not distance_known:
            unknowns.append(RouteUnknown.METRIC_DISTANCE)

        # Accessibility: True only if every edge says so explicitly.
        if edges and all(e.step_free is True for e in edges):
            step_free: Optional[bool] = True
        elif any(e.step_free is False for e in edges):
            step_free = False
        else:
            step_free = None
            unknowns.append(RouteUnknown.STEP_FREE_ACCESSIBILITY)

        # Walking time is always unknown: no evidenced speed model exists.
        unknowns.append(RouteUnknown.WALKING_TIME)

        evidence: List[RouteEvidence] = []
        for node_id in node_ids:
            node: SpatialNode = self.graph.node(node_id)
            evidence.append(
                RouteEvidence(
                    component_id=node_id,
                    component_kind="NODE",
                    geometry_provenance=node.stance.geometry_provenance,
                    evidence_links=node.stance.evidence_links,
                )
            )
        for edge in edges:
            evidence.append(
                RouteEvidence(
                    component_id=edge.edge_id,
                    component_kind="EDGE",
                    geometry_provenance=edge.stance.geometry_provenance,
                    evidence_links=edge.stance.evidence_links,
                )
            )

        return RouteResult(
            status=RouteStatus.ROUTABLE,
            start_node_id=start_node_id,
            destination_node_id=destination_node_id,
            node_ids=node_ids,
            edge_ids=edge_ids,
            distance_known=distance_known,
            total_distance_meters=total_distance,
            step_free=step_free,
            cost_basis=cost_basis,
            unknowns=tuple(unknowns),
            evidence=tuple(evidence),
        )
