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

Declared axes are not evidence
------------------------------
The six axes on `EvidenceStance` are caller-supplied, and for one release the
seventh field was only counted: `len(evidence_links) > 0` was the whole of
"this is evidenced". A stance asserting SUPPORTED / APPROVED / PUBLISH_ALLOWED
over a link naming an artifact that was never registered admitted its nodes,
admitted its edge, and returned ROUTABLE with a metric distance. So did a
stance whose links were themselves CONFLICTED and REJECTED, and so did one
whose "link" was a bare string.

Admission is therefore two questions, not one, and both must be answered:

  1. do the declared axes permit routing?  -- `EvidenceStance.reject_reasons`
  2. does the cited evidence currently resolve?  -- `SpatialEvidenceVerifier`

The second is asked of *every* link, on every read, against a registry the
verifier constructs itself at that moment. The verification context is an
evidence *root*, never a registry and never a factory: `ArtifactRegistry`
answers from the index it read at construction, so anything a caller can retain
-- an instance, or a closure over one -- would keep confirming deregistered
artifacts. Universal quantification is inherited from the canonical
admission boundary for the same reason it holds there: "some link resolves"
would let one real citation launder an unheld one beside it, so adding evidence
can never subtract scrutiny.

Verification is not cached in the graph. An artifact can be replaced or
deregistered after a graph is built, and a stored verdict would go on routing
across evidence the repository no longer has -- the same defect as a persisted
PUBLISH_ALLOWED, one layer down. `SpatialGraph` holds submitted elements and
re-derives their admission on every read, so the graph that was routable a
moment ago answers INSUFFICIENT_EVIDENCE the moment its evidence stops
resolving, with no reconstruction.

Canonical enums (`Method`, `Derivation`, `EvidenceCondition`,
`HumanReviewState`, `PublishStatus`, `GeometryProvenance`, `EvidenceLink`) are
imported from `timonelo.ontology.models` and are NOT redefined here. Artifact
resolution is imported from `timonelo.spatial.admission` and is not reimplemented
here either.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    EvidenceLink,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.spatial.admission import verify_link_artifact


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
    # --- current evidence resolution -------------------------------------
    NO_VERIFICATION_CONTEXT = "NO_VERIFICATION_CONTEXT"
    VERIFICATION_CONTEXT_UNAVAILABLE = "VERIFICATION_CONTEXT_UNAVAILABLE"
    MALFORMED_EVIDENCE_LINK = "MALFORMED_EVIDENCE_LINK"
    ARTIFACT_NOT_REGISTERED = "ARTIFACT_NOT_REGISTERED"
    NOT_CONTENT_ADDRESSED = "NOT_CONTENT_ADDRESSED"
    ARTIFACT_NOT_HELD = "ARTIFACT_NOT_HELD"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    STANCE_CONTRADICTS_LINK = "STANCE_CONTRADICTS_LINK"


#: P0's artifact-resolution codes, carried across into this enum by value. The
#: two enums are deliberately separate -- a canonical-sink rejection and a
#: routing rejection are different verdicts -- but the shared predicate must
#: report the same reason on both sides of the boundary.
_ARTIFACT_REJECTION_BY_VALUE: Dict[str, "AdmissionRejection"] = {
    r.value: r for r in (
        AdmissionRejection.ARTIFACT_NOT_REGISTERED,
        AdmissionRejection.NOT_CONTENT_ADDRESSED,
        AdmissionRejection.ARTIFACT_NOT_HELD,
        AdmissionRejection.DIGEST_MISMATCH,
    )
}


class SpatialEvidenceVerifier:
    """Resolves the evidence a stance cites, as the repository holds it *now*.

    `EvidenceStance` states six axes and carries evidence links. The axes are a
    caller's declaration and the links were, until this boundary existed, only
    counted: `len(evidence_links) > 0` was the whole of "this is evidenced". A
    stance naming an artifact that was never registered, or one whose bytes
    have since been replaced, routed a passenger exactly as well as a real one.

    So the links are resolved rather than counted, and resolved per question
    rather than once at construction. A cached admission is the same defect in
    smaller form: an artifact can be replaced or deregistered after a graph is
    built, and a graph that answered from a stored verdict would go on routing
    across evidence the repository no longer has.

    Being unable to check is not permission to skip the check. A verifier with
    no evidence root refuses every link and says why, so a caller who forgets
    the context gets an empty graph rather than an unguarded one.

    Why a root and not a registry, or a factory
    -------------------------------------------
    The context is a filesystem root, and the verifier constructs the registry
    itself. Neither an `ArtifactRegistry` nor a callable returning one may be
    supplied.

    `ArtifactRegistry` reads `index.json` once in `__init__` and answers every
    later `get` from that snapshot, so a verifier holding one instance keeps
    confirming artifacts that have since been deregistered: ROUTABLE,
    deregister, ROUTABLE. The first version of this class accepted either an
    instance or a factory and merely recommended the factory. The second
    rejected the instance and required a callable -- which closed the obvious
    path and left the real one open, because `lambda: retained_registry` is a
    perfectly good callable that returns the same stale snapshot every time. It
    reproduced the identical defect.

    An arbitrary callable is not evidence of freshness, and there is no way to
    inspect one and find out: a factory could return a cached instance, a
    memoised one, or a registry over an entirely different root. So the
    delegation is removed rather than validated. The caller supplies immutable
    configuration -- where the evidence lives -- and reconstruction is this
    class's own responsibility, on every authority-bearing evaluation. No
    caller can opt out of currentness because no caller is trusted with it.

    Refusing an unsupported context is preferable to accepting stale state.
    """

    def __init__(self, registry_root: Any = None) -> None:
        """`registry_root` is the artifact root directory. Nothing else.

        Anything that is not a path -- an `ArtifactRegistry`, a callable, a
        factory returning a registry -- raises. These are not adapted, because
        every adaptation preserves whatever snapshot the caller already had.
        """
        if registry_root is None:
            self._registry_root: Optional[str] = None
            return
        if isinstance(registry_root, (str, os.PathLike)):
            self._registry_root = os.fspath(registry_root)
            return
        raise TypeError(
            "SpatialEvidenceVerifier takes the artifact root directory, not "
            f"{type(registry_root).__name__}. A retained ArtifactRegistry answers "
            "from the index it was constructed with, and a callable returning one "
            "is no better -- `lambda: registry` returns the same stale snapshot "
            "every time. The verifier constructs a current registry itself; pass "
            "the root, e.g. SpatialEvidenceVerifier('evidence/artifacts')."
        )

    @property
    def has_context(self) -> bool:
        """Whether a root was configured. Not whether it is currently usable."""
        return self._registry_root is not None

    @property
    def registry_root(self) -> Optional[str]:
        return self._registry_root

    def current_registry(self) -> Optional[ArtifactRegistry]:
        """A registry built now, from the configured root, or None.

        A new instance every call. That is the whole mechanism: the index is
        re-read from disk each time, so registration and deregistration are
        both visible to a graph that already exists. Nothing is retained
        between calls, so there is no stale state to fall back to even in
        principle.

        None means current registry state could not be established -- the root
        is unset, is not a directory, or the registry could not be opened. Each
        is a refusal.
        """
        root = self._registry_root
        if root is None:
            return None
        # Checked before construction: `ArtifactRegistry.__init__` creates its
        # blobs directory, so building one over a mistyped root would silently
        # manufacture an empty evidence store and then answer from it.
        if not os.path.isdir(root):
            return None
        try:
            return ArtifactRegistry(root)
        except Exception:
            # Only registry acquisition is guarded, and only here -- an
            # unreadable or corrupt index means "current registry state cannot
            # be established", which is a verdict this boundary must be able to
            # return. Verification itself stays unguarded, so a genuine defect
            # in admission still surfaces as a crash rather than being
            # laundered into a refusal.
            return None

    def verify(self, link: Any) -> Tuple[AdmissionRejection, ...]:
        """Every reason this one link does not currently resolve."""
        if not self.has_context:
            return (AdmissionRejection.NO_VERIFICATION_CONTEXT,)
        if not isinstance(link, EvidenceLink):
            # Counting a container's members never asked what they were. A
            # bare string is a truthy member and used to qualify a route.
            # Checked before the registry is built: a malformed link is refused
            # on its own account and does not need one.
            return (AdmissionRejection.MALFORMED_EVIDENCE_LINK,)

        registry = self.current_registry()
        if registry is None:
            return (AdmissionRejection.VERIFICATION_CONTEXT_UNAVAILABLE,)

        reasons: List[AdmissionRejection] = [
            _ARTIFACT_REJECTION_BY_VALUE[r.value]
            for r in verify_link_artifact(link, registry)
        ]

        # The link's own axes bind the stance that carries it. A stance
        # declaring SUPPORTED/APPROVED over a link that is itself CONFLICTED,
        # REJECTED or merely DRAFT is a caller overruling its own evidence,
        # which is the one thing a declaration must never be able to do.
        if (
            link.evidence_condition is not EvidenceCondition.SUPPORTED
            or link.human_review_state is not HumanReviewState.APPROVED
        ):
            reasons.append(AdmissionRejection.STANCE_CONTRADICTS_LINK)
        return tuple(reasons)


#: The verifier used when a graph was given none. It has no evidence root,
#: so it refuses everything -- which is the right answer to "does this evidence
#: resolve?" asked by something that cannot look.
NO_VERIFICATION = SpatialEvidenceVerifier()


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
        """Every reason the *declared axes* are unfit for routing (may be empty).

        Declared axes only. An empty tuple here means the caller has asserted
        nothing disqualifying; it does not mean the cited evidence resolves,
        and it is not an admission verdict. `SpatialGraph` pairs this with
        `SpatialEvidenceVerifier` and admits on both. Nothing else should treat
        an empty result as permission to route.

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
        """Whether the declared axes permit routing. NOT an admission verdict.

        Kept because the axes are worth asking about on their own -- a reviewer
        wants to know what a record says. It answers that and nothing more: it
        has no registry and so cannot know whether the cited evidence exists.
        Ask `SpatialGraph` whether something may be routed.
        """
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
        """Declared axes only -- see `EvidenceStance.is_route_qualified`."""
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
        """Declared axes only -- see `EvidenceStance.is_route_qualified`."""
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
    """Holds every submitted node/edge, but exposes only the admitted ones.

    Admission is re-derived on every read, never stored. Two questions decide
    it: whether the declared axes permit routing, and whether every link the
    stance cites currently resolves against evidence the repository holds. The
    second is the reason nothing is cached -- an artifact can be replaced or
    deregistered at any time, and a graph answering from a stored verdict would
    keep routing across evidence that is gone.

    Nothing is dropped: rejected elements stay queryable through
    `node_rejection`, `edge_rejection` and `admission_report()` so that an
    unroutable answer can explain itself.

    A graph built without a `verifier` refuses every element with
    NO_VERIFICATION_CONTEXT. That is deliberate and is the reason the parameter
    is keyword-optional rather than absent: a caller who cannot supply evidence
    context gets an empty graph, not an unguarded one.
    """

    def __init__(
        self,
        nodes: Iterable[SpatialNode] = (),
        edges: Iterable[SpatialEdge] = (),
        *,
        verifier: Optional[SpatialEvidenceVerifier] = None,
    ) -> None:
        self.verifier = verifier if verifier is not None else NO_VERIFICATION
        self._submitted_nodes: Dict[str, SpatialNode] = {}
        self._submitted_edges: Dict[str, SpatialEdge] = {}
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    # --- admission (re-derived, never stored) ----------------------------

    def _stance_rejections(self, stance: EvidenceStance) -> Tuple[AdmissionRejection, ...]:
        """Declared axes, then current evidence resolution, for one stance.

        Every link is resolved, not merely the first that fails: a refusal that
        named one bad citation while others were equally unresolvable would
        under-report what is wrong. Universal quantification, as at the
        canonical admission boundary.
        """
        reasons: List[AdmissionRejection] = list(stance.reject_reasons())
        if reasons:
            # Already refused on what it declares about itself. Resolving its
            # evidence could only add reasons to a refusal, and resolution
            # re-hashes held bytes -- so a deck whose every object is
            # PUBLISH_BLOCKED is not paid for in megabytes of hashing to
            # confirm a verdict that cannot change.
            return tuple(reasons)

        seen = set()
        for link in stance.evidence_links:
            for reason in self.verifier.verify(link):
                if reason not in seen:
                    seen.add(reason)
                    reasons.append(reason)
        return tuple(reasons)

    def _node_rejections(self, node: SpatialNode) -> Tuple[AdmissionRejection, ...]:
        return self._stance_rejections(node.stance)

    def _edge_rejections(self, edge: SpatialEdge) -> Tuple[AdmissionRejection, ...]:
        reasons = list(self._stance_rejections(edge.stance))
        if not self._is_node_admitted(edge.from_node_id) or not self._is_node_admitted(
            edge.to_node_id
        ):
            reasons.append(AdmissionRejection.ENDPOINT_NOT_ADMITTED)
        return tuple(reasons)

    def _is_node_admitted(self, node_id: str) -> bool:
        node = self._submitted_nodes.get(node_id)
        return node is not None and not self._node_rejections(node)

    def _admitted_edges(self) -> Dict[str, SpatialEdge]:
        return {
            eid: e
            for eid, e in self._submitted_edges.items()
            if not self._edge_rejections(e)
        }

    # --- write side ------------------------------------------------------

    def add_node(self, node: SpatialNode) -> bool:
        """Submits a node. Returns whether it is admitted *at this moment*."""
        if node.node_id in self._submitted_nodes:
            raise ValueError(f"Duplicate spatial node id {node.node_id}")
        self._submitted_nodes[node.node_id] = node
        return not self._node_rejections(node)

    def add_edge(self, edge: SpatialEdge) -> bool:
        """Submits an edge. Returns whether it is admitted *at this moment*."""
        if edge.edge_id in self._submitted_edges:
            raise ValueError(f"Duplicate spatial edge id {edge.edge_id}")
        self._submitted_edges[edge.edge_id] = edge
        return not self._edge_rejections(edge)

    # --- read side -------------------------------------------------------

    def node(self, node_id: str) -> Optional[SpatialNode]:
        node = self._submitted_nodes.get(node_id)
        if node is None or self._node_rejections(node):
            return None
        return node

    def edge(self, edge_id: str) -> Optional[SpatialEdge]:
        edge = self._submitted_edges.get(edge_id)
        if edge is None or self._edge_rejections(edge):
            return None
        return edge

    @property
    def node_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(
            nid for nid, n in self._submitted_nodes.items()
            if not self._node_rejections(n)
        ))

    @property
    def edge_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._admitted_edges()))

    def neighbours(self, node_id: str) -> Sequence[Tuple[str, str]]:
        """Deterministically ordered (neighbour_node_id, edge_id) pairs.

        Built from the currently admitted edges, so a connection whose evidence
        has stopped resolving is not offered to the router at all.
        """
        if not self._is_node_admitted(node_id):
            return ()
        adjacency: List[Tuple[str, str]] = []
        for eid, edge in self._admitted_edges().items():
            if edge.from_node_id == node_id:
                adjacency.append((edge.to_node_id, eid))
            if edge.bidirectional and edge.to_node_id == node_id:
                adjacency.append((edge.from_node_id, eid))
        return tuple(sorted(adjacency))

    def node_rejection(self, node_id: str) -> Tuple[AdmissionRejection, ...]:
        node = self._submitted_nodes.get(node_id)
        return self._node_rejections(node) if node is not None else ()

    def edge_rejection(self, edge_id: str) -> Tuple[AdmissionRejection, ...]:
        edge = self._submitted_edges.get(edge_id)
        return self._edge_rejections(edge) if edge is not None else ()

    @property
    def all_admitted_edges_have_metric_length(self) -> bool:
        admitted = self._admitted_edges()
        return bool(admitted) and all(e.has_metric_length for e in admitted.values())

    def admission_report(self) -> AdmissionReport:
        return AdmissionReport(
            admitted_node_ids=self.node_ids,
            admitted_edge_ids=self.edge_ids,
            rejected_nodes={
                nid: reasons
                for nid, n in self._submitted_nodes.items()
                if (reasons := self._node_rejections(n))
            },
            rejected_edges={
                eid: reasons
                for eid, e in self._submitted_edges.items()
                if (reasons := self._edge_rejections(e))
            },
        )
