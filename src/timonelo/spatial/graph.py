"""
Evidence-gated spatial graph (Timonelo first routable slice).

This module is the trust boundary between *drawn* geometry and *routable* truth.

It exists because the repository already contains a spatial router
(`timonelo.calculus.router.DeterministicSpatialRouter`) that consumes
`VesselSpatialOntology` corridor nodes/edges. That router is mathematically
correct but epistemically unguarded: every edge it receives already carries a
`distance_meters` float and an `is_step_free=True` default, so it can neither
detect nor report that its inputs were synthesised. The generator that produced
`geometry/deck*.geometry.json` lays cabins out on an evenly spaced synthetic
strip and hardcodes lift/corridor polygons; only the cabin *number* is read
from the source PDF. That geometry is therefore SYNTHETIC_GEOMETRY and must
never become route truth.

The types here are deliberately *narrower* than the canonical ontology models:
- an edge has NO default distance (`length_meters` is Optional, default None),
- an edge has NO default accessibility (`step_free` is Optional, default None
  meaning UNKNOWN — never False, never True by omission),
- every node and edge must carry provenance, evidence condition, review state
  and publish status explicitly. There are no fail-open defaults.

Canonical enums (`Method`, `Derivation`, `EvidenceCondition`,
`HumanReviewState`, `PublishStatus`, `GeometryProvenance`, `EvidenceLink`) are
imported from `timonelo.ontology.models` and are NOT redefined here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    EvidenceLink,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)


class SpatialNodeType(str, Enum):
    """Kinds of place a route may pass through.

    Scope note: this slice only ever instantiates CABIN. The remaining members
    are declared so that admitting a corridor point or a lift later is a data
    change, not a schema change — they are NOT a claim that such nodes are
    evidenced today.
    """
    CABIN = "CABIN"
    CORRIDOR_POINT = "CORRIDOR_POINT"
    INTERSECTION = "INTERSECTION"
    LIFT = "LIFT"
    STAIRS = "STAIRS"
    VENUE = "VENUE"
    MANUAL_POSITION = "MANUAL_POSITION"


class SpatialEdgeType(str, Enum):
    """Kinds of traversable connection between two spatial nodes."""
    WALKABLE = "WALKABLE"
    ENTER = "ENTER"
    EXIT = "EXIT"
    LIFT_TRANSFER = "LIFT_TRANSFER"
    STAIR_TRANSFER = "STAIR_TRANSFER"


class AdmissionRejection(str, Enum):
    """Why a node or edge was refused entry to the routable graph."""
    EVIDENCE_NOT_SUPPORTED = "EVIDENCE_NOT_SUPPORTED"
    PUBLISH_BLOCKED = "PUBLISH_BLOCKED"
    REVIEW_NOT_ACCEPTED = "REVIEW_NOT_ACCEPTED"
    SYNTHETIC_GEOMETRY = "SYNTHETIC_GEOMETRY"
    UNKNOWN_GEOMETRY_PROVENANCE = "UNKNOWN_GEOMETRY_PROVENANCE"
    GENERATED_DERIVATION = "GENERATED_DERIVATION"
    INFERRED_METHOD = "INFERRED_METHOD"
    NO_EVIDENCE_LINK = "NO_EVIDENCE_LINK"
    ENDPOINT_NOT_ADMITTED = "ENDPOINT_NOT_ADMITTED"


#: Geometry provenance values that may carry a metric claim. Synthetic and
#: unknown-provenance geometry may not, and neither may an absent value.
METRIC_QUALIFIED_PROVENANCE = frozenset({
    GeometryProvenance.DIRECT_SOURCE_GEOMETRY,
    GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY,
    GeometryProvenance.DERIVED_GEOMETRY,
})

#: Review states under which a curated element may be traversed. DRAFT,
#: UNDER_REVIEW, REJECTED and SUPERSEDED are all refused.
ROUTE_ACCEPTED_REVIEW_STATES = frozenset({HumanReviewState.APPROVED})


@dataclass(frozen=True)
class EvidenceStance:
    """The four orthogonal axes every routable element must state explicitly.

    Kept as one value object so that a node and an edge cannot drift apart in
    how they express trust, and so no axis can be silently omitted.
    """
    evidence_condition: EvidenceCondition
    human_review_state: HumanReviewState
    publish_status: PublishStatus
    geometry_provenance: GeometryProvenance
    method: Method
    derivation: Derivation
    evidence_links: Tuple[EvidenceLink, ...] = ()

    def reject_reasons(self) -> Tuple[AdmissionRejection, ...]:
        """Returns every reason this stance is unfit for routing (may be empty).

        UNKNOWN_PROVENANCE is deliberately absent from this list. An entity
        whose existence is evidenced but whose geometry has never been
        measured is a legitimate graph vertex — it simply cannot back a
        distance. That is handled by `is_metric_qualified`, not here.
        Synthetic geometry is different in kind: it is a fabricated shape
        asserting a position that was never observed, so it is refused
        outright and can never appear on a route.
        """
        reasons: List[AdmissionRejection] = []
        if self.evidence_condition != EvidenceCondition.SUPPORTED:
            reasons.append(AdmissionRejection.EVIDENCE_NOT_SUPPORTED)
        if self.publish_status == PublishStatus.PUBLISH_BLOCKED:
            reasons.append(AdmissionRejection.PUBLISH_BLOCKED)
        if self.human_review_state not in ROUTE_ACCEPTED_REVIEW_STATES:
            reasons.append(AdmissionRejection.REVIEW_NOT_ACCEPTED)
        if self.geometry_provenance == GeometryProvenance.SYNTHETIC_GEOMETRY:
            reasons.append(AdmissionRejection.SYNTHETIC_GEOMETRY)
        if self.derivation == Derivation.GENERATED:
            reasons.append(AdmissionRejection.GENERATED_DERIVATION)
        if self.method == Method.INFERRED:
            reasons.append(AdmissionRejection.INFERRED_METHOD)
        if not self.evidence_links:
            reasons.append(AdmissionRejection.NO_EVIDENCE_LINK)
        return tuple(reasons)

    @property
    def is_route_qualified(self) -> bool:
        return not self.reject_reasons()

    def metric_reject_reasons(self) -> Tuple[AdmissionRejection, ...]:
        """Returns every reason this stance may not back a distance claim."""
        reasons = list(self.reject_reasons())
        if self.geometry_provenance == GeometryProvenance.UNKNOWN_PROVENANCE:
            reasons.append(AdmissionRejection.UNKNOWN_GEOMETRY_PROVENANCE)
        elif self.geometry_provenance not in METRIC_QUALIFIED_PROVENANCE:
            reasons.append(AdmissionRejection.SYNTHETIC_GEOMETRY)
        return tuple(reasons)

    @property
    def is_metric_qualified(self) -> bool:
        """Whether this stance may back a distance claim at all."""
        return not self.metric_reject_reasons()


@dataclass(frozen=True)
class SpatialNode:
    node_id: str
    node_type: SpatialNodeType
    vessel_id: str
    deck_number: int
    stance: EvidenceStance
    label: Optional[str] = None

    @property
    def is_route_qualified(self) -> bool:
        return self.stance.is_route_qualified


@dataclass(frozen=True)
class SpatialEdge:
    """A traversable connection.

    `length_meters` defaults to None and stays None unless a metric-qualified
    geometry actually supports it. `step_free` is tri-state: None means the
    accessibility of this connection is UNKNOWN, which is not the same as False
    and must never be read as True.
    """
    edge_id: str
    edge_type: SpatialEdgeType
    from_node_id: str
    to_node_id: str
    stance: EvidenceStance
    length_meters: Optional[float] = None
    step_free: Optional[bool] = None
    bidirectional: bool = True

    def __post_init__(self) -> None:
        if self.length_meters is not None and not self.stance.is_metric_qualified:
            raise ValueError(
                f"Edge {self.edge_id} claims length_meters={self.length_meters} but its "
                f"geometry provenance ({self.stance.geometry_provenance.value}) cannot "
                "support a metric claim."
            )
        if self.length_meters is not None and self.length_meters < 0:
            raise ValueError(f"Edge {self.edge_id} has negative length_meters.")

    @property
    def is_route_qualified(self) -> bool:
        return self.stance.is_route_qualified

    @property
    def has_metric_length(self) -> bool:
        return self.length_meters is not None


@dataclass(frozen=True)
class AdmissionReport:
    """What the graph accepted, what it refused, and why."""
    admitted_node_ids: Tuple[str, ...]
    admitted_edge_ids: Tuple[str, ...]
    rejected_nodes: Dict[str, Tuple[AdmissionRejection, ...]] = field(default_factory=dict)
    rejected_edges: Dict[str, Tuple[AdmissionRejection, ...]] = field(default_factory=dict)


class SpatialGraph:
    """Holds every submitted node/edge, but exposes only the route-qualified ones.

    Nothing is dropped: rejected elements stay queryable through
    `admission_report()` so that an unroutable answer can explain itself.
    """

    def __init__(
        self,
        nodes: Iterable[SpatialNode] = (),
        edges: Iterable[SpatialEdge] = (),
    ) -> None:
        self._nodes: Dict[str, SpatialNode] = {}
        self._edges: Dict[str, SpatialEdge] = {}
        self._rejected_nodes: Dict[str, Tuple[AdmissionRejection, ...]] = {}
        self._rejected_edges: Dict[str, Tuple[AdmissionRejection, ...]] = {}
        self._adjacency: Dict[str, List[Tuple[str, str]]] = {}
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def add_node(self, node: SpatialNode) -> bool:
        if node.node_id in self._nodes or node.node_id in self._rejected_nodes:
            raise ValueError(f"Duplicate spatial node id {node.node_id}")
        reasons = node.stance.reject_reasons()
        if reasons:
            self._rejected_nodes[node.node_id] = reasons
            return False
        self._nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, [])
        return True

    def add_edge(self, edge: SpatialEdge) -> bool:
        if edge.edge_id in self._edges or edge.edge_id in self._rejected_edges:
            raise ValueError(f"Duplicate spatial edge id {edge.edge_id}")
        reasons = list(edge.stance.reject_reasons())
        if edge.from_node_id not in self._nodes or edge.to_node_id not in self._nodes:
            reasons.append(AdmissionRejection.ENDPOINT_NOT_ADMITTED)
        if reasons:
            self._rejected_edges[edge.edge_id] = tuple(reasons)
            return False
        self._edges[edge.edge_id] = edge
        self._adjacency[edge.from_node_id].append((edge.to_node_id, edge.edge_id))
        if edge.bidirectional:
            self._adjacency[edge.to_node_id].append((edge.from_node_id, edge.edge_id))
        return True

    # --- read side -------------------------------------------------------

    def node(self, node_id: str) -> Optional[SpatialNode]:
        return self._nodes.get(node_id)

    def edge(self, edge_id: str) -> Optional[SpatialEdge]:
        return self._edges.get(edge_id)

    @property
    def node_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._nodes))

    @property
    def edge_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._edges))

    def neighbours(self, node_id: str) -> Sequence[Tuple[str, str]]:
        """Deterministically ordered (neighbour_node_id, edge_id) pairs."""
        return tuple(sorted(self._adjacency.get(node_id, [])))

    def node_rejection(self, node_id: str) -> Tuple[AdmissionRejection, ...]:
        return self._rejected_nodes.get(node_id, ())

    def edge_rejection(self, edge_id: str) -> Tuple[AdmissionRejection, ...]:
        return self._rejected_edges.get(edge_id, ())

    @property
    def all_admitted_edges_have_metric_length(self) -> bool:
        return bool(self._edges) and all(e.has_metric_length for e in self._edges.values())

    def admission_report(self) -> AdmissionReport:
        return AdmissionReport(
            admitted_node_ids=self.node_ids,
            admitted_edge_ids=self.edge_ids,
            rejected_nodes=dict(self._rejected_nodes),
            rejected_edges=dict(self._rejected_edges),
        )
