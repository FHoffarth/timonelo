"""
Evidence-gated spatial graph and router (first routable slice).

Sits between the evidence plane and the existing spatial calculus: a graph
that admits only evidence-qualified nodes and edges, and a router that is
permitted to answer NOT_ROUTABLE or INSUFFICIENT_EVIDENCE instead of
manufacturing a path, a distance or an accessibility claim.

"Evidence-qualified" means both that the declared axes permit routing and that
every cited artifact currently resolves against bytes the repository holds.
A `SpatialGraph` needs a `SpatialEvidenceVerifier` to establish the second;
without one it admits nothing.
"""

from timonelo.spatial.graph import (
    METRIC_QUALIFIED_PROVENANCE,
    NO_VERIFICATION,
    ROUTE_ACCEPTED_REVIEW_STATES,
    AdmissionRejection,
    AdmissionReport,
    EvidenceStance,
    SpatialEvidenceVerifier,
    SpatialEdge,
    SpatialEdgeType,
    SpatialGraph,
    SpatialNode,
    SpatialNodeType,
)
from timonelo.spatial.router import (
    CostBasis,
    EvidenceGatedRouter,
    RouteEvidence,
    RouteResult,
    RouteStatus,
    RouteUnknown,
)

__all__ = [
    "METRIC_QUALIFIED_PROVENANCE",
    "NO_VERIFICATION",
    "ROUTE_ACCEPTED_REVIEW_STATES",
    "AdmissionRejection",
    "AdmissionReport",
    "EvidenceStance",
    "SpatialEvidenceVerifier",
    "SpatialEdge",
    "SpatialEdgeType",
    "SpatialGraph",
    "SpatialNode",
    "SpatialNodeType",
    "CostBasis",
    "EvidenceGatedRouter",
    "RouteEvidence",
    "RouteResult",
    "RouteStatus",
    "RouteUnknown",
]
