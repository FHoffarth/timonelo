"""
Targeted tests for the evidence-gated spatial graph and router.

These prove the trust rules of the first routable slice, not the breadth of a
route network. Fixtures below that carry supported geometry are TEST fixtures
only; nothing here writes to `knowledge/`, `geometry/` or `evidence/`.

The Deck 14 sections read the canonical proof at
`geometry/proofs/bellissima/deck14/deck14.proof.json` and the canonical
artifact vault. They assert what that proof actually establishes and, more
importantly, what it refuses to.
"""

import copy
import json
import os
import pathlib

import pytest

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
from timonelo.spatial import (
    NO_VERIFICATION,
    AdmissionRejection,
    CostBasis,
    EvidenceGatedRouter,
    EvidenceStance,
    RouteStatus,
    RouteUnknown,
    SpatialEdge,
    SpatialEdgeType,
    SpatialEvidenceVerifier,
    SpatialGraph,
    SpatialNode,
    SpatialNodeType,
)
from timonelo.spatial.deck14_proof import (
    ARTIFACT_ID,
    evidence_verifier,
    DECK_NUMBER,
    VESSEL_ID,
    build_deck14_graph,
    build_deck14_nodes,
    deck14_connectivity_findings,
    default_proof_path,
    load_proof,
    repo_root,
    resolve_artifact,
)

#: The registry these tests verify against: the repository's real artifact
#: root, read-only. Passed as a factory rather than an instance so a test that
#: mutates its own copy of the evidence tree sees the change (see the mutation
#: tests at the end of this file).
ARTIFACTS_ROOT = os.path.join(repo_root(), "evidence", "artifacts")
VERIFIER = SpatialEvidenceVerifier(registry_factory=lambda: ArtifactRegistry(ARTIFACTS_ROOT))

#: ART-0001's real digest, recomputed from the bytes in the SHA vault.
HELD_DIGEST = resolve_artifact()[1]

#: The baseline evidence link for every fixture below.
#:
#: This used to be `EvidenceLink(source_id="ART-0001", ..., sha256=None)` -- a
#: link to a real artifact that was never content-addressed and so could never
#: be resolved. It qualified anyway, because admission counted links instead of
#: resolving them. It now names a registered artifact, carries a digest
#: recomputed from held bytes, and states the axes it is being trusted for. The
#: fixture was strengthened to meet the boundary; the boundary was not weakened
#: to meet the fixture.
LINK = EvidenceLink(
    source_id="ART-0001",
    locator="Page 5, Deck 14 plan",
    sha256=HELD_DIGEST,
    method=Method.DIRECT,
    derivation=Derivation.LOCAL,
    evidence_condition=EvidenceCondition.SUPPORTED,
    human_review_state=HumanReviewState.APPROVED,
)


def make_graph(nodes=(), edges=(), *, verifier=VERIFIER):
    """A graph over the real artifact registry, unless a test says otherwise."""
    return SpatialGraph(nodes=nodes, edges=edges, verifier=verifier)


def stance(
    *,
    geometry_provenance=GeometryProvenance.DIRECT_SOURCE_GEOMETRY,
    evidence_condition=EvidenceCondition.SUPPORTED,
    human_review_state=HumanReviewState.APPROVED,
    publish_status=PublishStatus.PUBLISH_ALLOWED,
    method=Method.DIRECT,
    derivation=Derivation.LOCAL,
    evidence_links=(LINK,),
):
    return EvidenceStance(
        evidence_condition=evidence_condition,
        human_review_state=human_review_state,
        publish_status=publish_status,
        geometry_provenance=geometry_provenance,
        method=method,
        derivation=derivation,
        evidence_links=evidence_links,
    )


def node(node_id, node_type=SpatialNodeType.CORRIDOR_POINT, **kwargs):
    return SpatialNode(
        node_id=node_id,
        node_type=node_type,
        vessel_id=VESSEL_ID,
        deck_number=DECK_NUMBER,
        stance=stance(**kwargs),
    )


def edge(edge_id, a, b, length_meters=None, step_free=None, **kwargs):
    return SpatialEdge(
        edge_id=edge_id,
        edge_type=SpatialEdgeType.WALKABLE,
        from_node_id=a,
        to_node_id=b,
        stance=stance(**kwargs),
        length_meters=length_meters,
        step_free=step_free,
    )


# --- 1. supported nodes/edges produce a deterministic route ----------------


def test_supported_graph_produces_deterministic_metric_route():
    graph = make_graph(
        nodes=[node("A"), node("B"), node("C")],
        edges=[
            edge("E-AB", "A", "B", length_meters=4.0, step_free=True),
            edge("E-BC", "B", "C", length_meters=6.5, step_free=True),
        ],
    )
    router = EvidenceGatedRouter(graph)

    result = router.route("A", "C")

    assert result.status == RouteStatus.ROUTABLE
    assert result.node_ids == ("A", "B", "C")
    assert result.edge_ids == ("E-AB", "E-BC")
    assert result.cost_basis == CostBasis.METRIC_METERS
    assert result.distance_known is True
    assert result.total_distance_meters == 10.5

    # Same inputs in a different insertion order must yield the same answer.
    reversed_graph = make_graph(
        nodes=[node("C"), node("B"), node("A")],
        edges=[
            edge("E-BC", "C", "B", length_meters=6.5, step_free=True),
            edge("E-AB", "B", "A", length_meters=4.0, step_free=True),
        ],
    )
    repeat = EvidenceGatedRouter(reversed_graph).route("A", "C")
    assert repeat.node_ids == result.node_ids
    assert repeat.edge_ids == result.edge_ids
    assert repeat.total_distance_meters == result.total_distance_meters


def test_shortest_metric_path_wins_over_fewer_hops():
    graph = make_graph(
        nodes=[node("A"), node("B"), node("C")],
        edges=[
            edge("E-AB", "A", "B", length_meters=1.0, step_free=True),
            edge("E-BC", "B", "C", length_meters=1.0, step_free=True),
            edge("E-AC", "A", "C", length_meters=50.0, step_free=True),
        ],
    )
    result = EvidenceGatedRouter(graph).route("A", "C")

    assert result.edge_ids == ("E-AB", "E-BC")
    assert result.total_distance_meters == 2.0


# --- 2. disconnected evidence returns NOT_ROUTABLE ------------------------


def test_disconnected_evidence_is_not_routable():
    graph = make_graph(
        nodes=[node("A"), node("B"), node("X"), node("Y")],
        edges=[edge("E-AB", "A", "B", length_meters=3.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "Y")

    assert result.status == RouteStatus.NOT_ROUTABLE
    assert result.node_ids == ()
    assert result.edge_ids == ()
    assert result.total_distance_meters is None
    assert any("NO_ADMITTED_CONNECTIVITY" in r for r in result.blocking_reasons)


def test_unknown_endpoint_is_insufficient_evidence_not_not_routable():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=3.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "LIFT-CORE-A-D14")

    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert any("DESTINATION_NODE_UNKNOWN" in r for r in result.blocking_reasons)


# --- 3. synthetic geometry cannot silently qualify as route truth ----------


def test_synthetic_geometry_node_is_refused_admission():
    graph = make_graph(
        nodes=[
            node("A"),
            node("SYNTH", geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY),
        ]
    )
    assert graph.node_ids == ("A",)
    assert AdmissionRejection.SYNTHETIC_GEOMETRY in graph.node_rejection("SYNTH")


def test_synthetic_edge_cannot_connect_two_evidenced_nodes():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[
            edge(
                "E-SYNTH",
                "A",
                "B",
                geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
            )
        ],
    )
    assert graph.edge_ids == ()
    assert AdmissionRejection.SYNTHETIC_GEOMETRY in graph.edge_rejection("E-SYNTH")
    assert EvidenceGatedRouter(graph).route("A", "B").status == RouteStatus.NOT_ROUTABLE


def test_synthetic_edge_may_not_even_declare_a_length():
    with pytest.raises(ValueError, match="cannot .*support a metric claim"):
        edge(
            "E-SYNTH-M",
            "A",
            "B",
            length_meters=12.0,
            geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
        )


def test_legacy_deck14_geometry_file_is_not_a_route_source():
    """The pre-existing generated deck geometry is synthetic and stays out.

    `knowledge/reports/bellissima_one_deck_geometry_proof.md` records all
    fifteen `geometry/deck*.geometry.json` files as SYNTHETIC_GEOMETRY and
    non-canonical. This guards the actual on-disk artifact, not a stand-in.
    """
    geometry_path = os.path.join(repo_root(), "geometry", "deck14.geometry.json")
    if not os.path.exists(geometry_path):
        pytest.skip("geometry/deck14.geometry.json not present")

    with open(geometry_path, "r", encoding="utf-8") as handle:
        deck = json.load(handle)

    graph = make_graph()
    for obj in deck["objects"]:
        admitted = graph.add_node(
            SpatialNode(
                node_id=obj["id"],
                node_type=SpatialNodeType.CABIN,
                vessel_id=VESSEL_ID,
                deck_number=deck["deck_number"],
                stance=stance(
                    geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
                    evidence_links=(),
                ),
            )
        )
        assert admitted is False

    assert graph.node_ids == ()


def test_canonical_proof_classifies_nothing_as_synthetic():
    proof = load_proof()
    for obj in proof["objects"]:
        assert obj["geometry_provenance"] != GeometryProvenance.SYNTHETIC_GEOMETRY.value


# --- 4. missing geometry does not create distance -------------------------


def test_route_over_lengthless_edges_reports_unknown_distance():
    graph = make_graph(
        nodes=[
            node("A", geometry_provenance=GeometryProvenance.UNKNOWN_PROVENANCE),
            node("B", geometry_provenance=GeometryProvenance.UNKNOWN_PROVENANCE),
        ],
        edges=[
            edge(
                "E-AB",
                "A",
                "B",
                geometry_provenance=GeometryProvenance.UNKNOWN_PROVENANCE,
                step_free=True,
            )
        ],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert result.status == RouteStatus.ROUTABLE
    assert result.cost_basis == CostBasis.EDGE_COUNT
    assert result.distance_known is False
    assert result.total_distance_meters is None
    assert RouteUnknown.METRIC_DISTANCE in result.unknowns


def test_one_lengthless_edge_collapses_the_whole_distance():
    """A partial sum would understate the walk, so none is reported."""
    graph = make_graph(
        nodes=[node("A"), node("B"), node("C")],
        edges=[
            edge("E-AB", "A", "B", length_meters=4.0, step_free=True),
            edge(
                "E-BC",
                "B",
                "C",
                geometry_provenance=GeometryProvenance.UNKNOWN_PROVENANCE,
                step_free=True,
            ),
        ],
    )
    result = EvidenceGatedRouter(graph).route("A", "C")

    assert result.status == RouteStatus.ROUTABLE
    assert result.edge_ids == ("E-AB", "E-BC")
    assert result.total_distance_meters is None
    assert result.distance_known is False


def test_walking_time_is_never_asserted():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=4.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert result.total_distance_meters == 4.0
    assert RouteUnknown.WALKING_TIME in result.unknowns
    assert not hasattr(result, "estimated_walking_seconds")


# --- 5. missing accessibility evidence does not become accessible=true ----


def test_unknown_step_free_stays_unknown():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=4.0, step_free=None)],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert result.status == RouteStatus.ROUTABLE
    assert result.step_free is None
    assert RouteUnknown.STEP_FREE_ACCESSIBILITY in result.unknowns


def test_step_free_only_when_every_edge_says_so():
    graph = make_graph(
        nodes=[node("A"), node("B"), node("C")],
        edges=[
            edge("E-AB", "A", "B", length_meters=1.0, step_free=True),
            edge("E-BC", "B", "C", length_meters=1.0, step_free=None),
        ],
    )
    result = EvidenceGatedRouter(graph).route("A", "C")
    assert result.step_free is None


def test_step_free_request_excludes_unknown_edges_rather_than_assuming_them():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=1.0, step_free=None)],
    )
    router = EvidenceGatedRouter(graph)

    assert router.route("A", "B").status == RouteStatus.ROUTABLE
    assert router.route("A", "B", require_step_free=True).status == RouteStatus.NOT_ROUTABLE


# --- 6. route evidence/provenance is preserved ----------------------------


def test_route_carries_provenance_for_every_component():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=4.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    by_id = {e.component_id: e for e in result.evidence}
    assert set(by_id) == {"A", "B", "E-AB"}
    assert by_id["A"].component_kind == "NODE"
    assert by_id["E-AB"].component_kind == "EDGE"
    for record in result.evidence:
        assert record.geometry_provenance == GeometryProvenance.DIRECT_SOURCE_GEOMETRY
        assert record.evidence_links == (LINK,)


# --- 7. evaluative/generated info cannot override blocked evidence --------


def test_generated_derivation_is_refused():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-GEN", "A", "B", derivation=Derivation.GENERATED)],
    )
    assert AdmissionRejection.GENERATED_DERIVATION in graph.edge_rejection("E-GEN")
    assert graph.edge_ids == ()


def test_inferred_method_is_refused():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-INF", "A", "B", method=Method.INFERRED)],
    )
    assert AdmissionRejection.INFERRED_METHOD in graph.edge_rejection("E-INF")


def test_publish_blocked_edge_stays_blocked_even_with_a_generated_duplicate():
    graph = make_graph(
        nodes=[node("A"), node("B")],
        edges=[
            edge("E-BLOCKED", "A", "B", publish_status=PublishStatus.PUBLISH_BLOCKED),
            edge(
                "E-GENERATED-OVERRIDE",
                "A",
                "B",
                length_meters=None,
                derivation=Derivation.GENERATED,
            ),
        ],
    )
    assert graph.edge_ids == ()
    assert AdmissionRejection.PUBLISH_BLOCKED in graph.edge_rejection("E-BLOCKED")
    assert (
        AdmissionRejection.GENERATED_DERIVATION
        in graph.edge_rejection("E-GENERATED-OVERRIDE")
    )
    assert EvidenceGatedRouter(graph).route("A", "B").status == RouteStatus.NOT_ROUTABLE


def test_unsupported_and_unreviewed_elements_are_refused():
    graph = make_graph(
        nodes=[
            node("A"),
            node("UNSUPPORTED", evidence_condition=EvidenceCondition.UNKNOWN),
            node("DRAFT", human_review_state=HumanReviewState.DRAFT),
            node("NOLINK", evidence_links=()),
        ]
    )
    assert graph.node_ids == ("A",)
    assert AdmissionRejection.EVIDENCE_NOT_SUPPORTED in graph.node_rejection("UNSUPPORTED")
    assert AdmissionRejection.REVIEW_NOT_ACCEPTED in graph.node_rejection("DRAFT")
    assert AdmissionRejection.NO_EVIDENCE_LINK in graph.node_rejection("NOLINK")


def test_edge_to_a_refused_node_is_itself_refused():
    graph = make_graph(
        nodes=[node("A"), node("SYNTH", geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY)],
        edges=[edge("E-AS", "A", "SYNTH", length_meters=2.0, step_free=True)],
    )
    assert AdmissionRejection.ENDPOINT_NOT_ADMITTED in graph.edge_rejection("E-AS")


# --- canonical Deck 14 proof ----------------------------------------------


def test_art_0001_resolves_through_the_canonical_sha_vault_not_the_legacy_blobs():
    path, digest = resolve_artifact()

    assert path is not None, "ART-0001 bytes are not resolvable"
    normalized = path.replace("\\", "/")
    assert "/evidence/raw/sha256/08/" in normalized
    assert "/artifacts/blobs/" not in normalized
    assert digest == "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"

    # The proof's recorded source digest is the same bytes, recomputed.
    assert load_proof()["source"]["artifact_sha256"] == digest


def test_deck14_proof_objects_are_all_publication_blocked():
    proof = load_proof()
    assert len(proof["objects"]) == 244
    for obj in proof["objects"]:
        assert obj["human_review_state"] == "DRAFT"
        assert obj["evidence_condition"] == "UNKNOWN"
        assert obj["publish_status"] == "PUBLISH_BLOCKED"

    graph = build_deck14_graph()
    assert graph.node_ids == ()
    assert graph.edge_ids == ()

    report = graph.admission_report()
    assert len(report.rejected_nodes) == 244
    for reasons in report.rejected_nodes.values():
        assert AdmissionRejection.PUBLISH_BLOCKED in reasons
        assert AdmissionRejection.REVIEW_NOT_ACCEPTED in reasons
        assert AdmissionRejection.EVIDENCE_NOT_SUPPORTED in reasons


def test_deck14_routing_on_the_real_proof_is_insufficient_evidence():
    graph = build_deck14_graph()
    result = EvidenceGatedRouter(graph).route(
        "bellissima-deck14-cabin-14001", "bellissima-deck14-cabin-14010"
    )

    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert result.total_distance_meters is None
    assert result.step_free is None
    assert any("NOT_ADMITTED" in r for r in result.blocking_reasons)


def _hypothetically_adjudicated_nodes():
    """Counterfactual ONLY: the real proof geometry with review state lifted.

    This does not adjudicate anything and is never used by production code. It
    exists to isolate the second, independent reason Deck 14 is unroutable:
    even if a human approved every cabin boundary tomorrow, the proof still
    contains no connection between them.
    """
    proof = copy.deepcopy(load_proof())
    for obj in proof["objects"]:
        obj["human_review_state"] = HumanReviewState.APPROVED.value
        obj["evidence_condition"] = EvidenceCondition.SUPPORTED.value
        obj["publish_status"] = PublishStatus.PUBLISH_ALLOWED.value
    # The digest stays real: only the review axes are counterfactual.
    _, digest = resolve_artifact()
    return proof, build_deck14_nodes(proof, sha256=digest)


def test_genuine_cabin_geometry_does_not_establish_traversability():
    _, nodes = _hypothetically_adjudicated_nodes()
    graph = make_graph(nodes=nodes, edges=())

    # Every cabin plus the lift region becomes a place...
    assert len(graph.node_ids) == 244
    # ...and still nothing connects them.
    assert graph.edge_ids == ()

    result = EvidenceGatedRouter(graph).route(
        "bellissima-deck14-cabin-14001", "bellissima-deck14-cabin-14002"
    )
    assert result.status == RouteStatus.NOT_ROUTABLE
    assert any("NO_ADMITTED_CONNECTIVITY" in r for r in result.blocking_reasons)
    assert result.total_distance_meters is None


def test_inferred_corridor_negative_space_is_never_promoted_to_connectivity():
    proof = load_proof()
    corridor = proof["corridor_observation"]

    assert corridor["classification"] == "INFERRED_NEGATIVE_SPACE"
    assert corridor["accepted_geometry"] is False
    assert corridor["geometry"] is None

    # No corridor node or edge reaches the graph, adjudicated or not.
    _, nodes = _hypothetically_adjudicated_nodes()
    graph = make_graph(nodes=nodes, edges=())
    for node_id in graph.node_ids:
        assert graph.node(node_id).node_type != SpatialNodeType.CORRIDOR_POINT
    assert graph.edge_ids == ()


def test_no_doors_and_no_cabin_to_corridor_edges_are_invented():
    proof = load_proof()
    serialized = json.dumps(proof)

    assert proof["navigation_graph"] is None
    assert proof["nearest_core_calculation"] is None
    assert "door" not in serialized.lower()

    findings = deck14_connectivity_findings(proof)
    assert findings["navigation_graph"] == "ABSENT"
    assert findings["nearest_core_calculation"] == "ABSENT"


def test_ambiguous_lift_region_is_a_place_not_a_transfer():
    _, nodes = _hypothetically_adjudicated_nodes()
    lift = [n for n in nodes if n.node_type == SpatialNodeType.LIFT]

    assert len(lift) == 1
    assert lift[0].stance.geometry_provenance == GeometryProvenance.DERIVED_GEOMETRY

    graph = make_graph(nodes=nodes, edges=())
    result = EvidenceGatedRouter(graph).route(
        "bellissima-deck14-cabin-14001", lift[0].node_id
    )
    assert result.status == RouteStatus.NOT_ROUTABLE

    # The proof disclaims cross-deck identity, so no vertical transfer exists.
    proof = load_proof()
    assert proof["cross_deck_relationships"] == []
    assert proof["above_below_relations"] == []


def test_page_fraction_coordinates_never_become_metres():
    proof = load_proof()
    assert proof["transform"]["target_units"] == "normalized fraction of PDF page MediaBox"
    assert deck14_connectivity_findings(proof)["metric_scale"].startswith("ABSENT")

    _, nodes = _hypothetically_adjudicated_nodes()
    graph = make_graph(nodes=nodes, edges=())
    assert graph.all_admitted_edges_have_metric_length is False

    result = EvidenceGatedRouter(graph).route(
        "bellissima-deck14-cabin-14001", "bellissima-deck14-cabin-14001"
    )
    assert result.status == RouteStatus.ROUTABLE  # a node reaches itself
    assert result.total_distance_meters is None
    assert RouteUnknown.METRIC_DISTANCE in result.unknowns


def test_deck14_nodes_carry_real_source_provenance():
    proof = load_proof()
    _, digest = resolve_artifact()
    nodes = {n.node_id: n for n in build_deck14_nodes(proof, sha256=digest)}

    cabin = nodes["bellissima-deck14-cabin-14001"]
    assert cabin.label == "14001"
    assert cabin.stance.geometry_provenance == GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY

    link = cabin.stance.evidence_links[0]
    assert link.source_id == ARTIFACT_ID
    # The digest is recomputed from held bytes, not copied from the index.
    assert link.sha256 == digest
    assert "page5" in link.locator
    assert "drawing-index" in link.locator


def test_no_cabin_has_both_a_published_fact_and_an_admitted_shape():
    """No Bellissima cabin is currently both stated and located.

    This used to hold trivially: the proof covered 14001-14010 and the
    statements covered 14102-14136, so the two sets could not meet. Now that
    the proof covers the whole Deck 14 cabin block the sets do overlap, and the
    separation rests on the axis that actually carries it — every envelope is
    PUBLISH_BLOCKED, so an overlapping cabin still has no admitted shape.
    """
    proof = load_proof()
    geometry_cabins = {
        o["cabin_number"] for o in proof["objects"] if o["semantic_type"] == "cabin"
    }
    assert len(geometry_cabins) == 243

    statements_path = os.path.join(
        repo_root(), "evidence", "statements", "statements.json"
    )
    with open(statements_path, "r", encoding="utf-8") as handle:
        statements = json.load(handle)
    statement_cabins = {
        s["entity_id"].rsplit(":", 1)[-1]
        for s in statements.values()
        if s["statement_type"] == "cabin.exists"
    }
    assert statement_cabins

    # The sets now genuinely intersect, which is why the publish axis is load-bearing.
    overlap = geometry_cabins & statement_cabins
    assert overlap, "expected the widened proof to reach the stated cabins"
    for obj in proof["objects"]:
        if obj.get("cabin_number") in overlap:
            assert obj["publish_status"] == "PUBLISH_BLOCKED"
            assert obj["evidence_condition"] == "UNKNOWN"
            assert obj["human_review_state"] == "DRAFT"


def test_proof_path_is_the_locked_deck14_proof():
    assert default_proof_path().replace("\\", "/").endswith(
        "geometry/proofs/bellissima/deck14/deck14.proof.json"
    )
    with pytest.raises(ValueError, match="Unexpected proof schema"):
        load_proof(
            os.path.join(repo_root(), "evidence", "artifacts", "index.json")
        )


# --- 8. current evidence resolution ---------------------------------------
#
# The graph used to count evidence links instead of resolving them. A stance
# asserting SUPPORTED / APPROVED / PUBLISH_ALLOWED over a link naming an
# artifact the repository had never held was admitted, and routed, with a
# metric distance. These tests hold that boundary shut from both directions:
# unresolvable evidence must refuse, and real held evidence must still route.


def link(**overrides) -> EvidenceLink:
    """A fully qualifying link to the real held ART-0001, before any override."""
    base = dict(
        source_id="ART-0001",
        locator="Page 5, Deck 14 plan",
        sha256=HELD_DIGEST,
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    base.update(overrides)
    return EvidenceLink(**base)


def two_node_graph(node_stance, *, verifier=VERIFIER, length_meters=10.0):
    """The smallest graph that can produce a metric ROUTABLE result."""
    nodes = [
        SpatialNode("A", SpatialNodeType.CABIN, VESSEL_ID, DECK_NUMBER, node_stance),
        SpatialNode("B", SpatialNodeType.CABIN, VESSEL_ID, DECK_NUMBER, node_stance),
    ]
    edges = [
        SpatialEdge(
            "E-AB", SpatialEdgeType.WALKABLE, "A", "B", node_stance,
            length_meters=length_meters, step_free=True,
        )
    ]
    return SpatialGraph(nodes=nodes, edges=edges, verifier=verifier)


def test_publish_allowed_over_an_unheld_artifact_is_not_routable():
    """The exact reported reproduction, closed.

    Four asserted axes over a direct geometry used to produce ROUTABLE at 10.0
    metres. The artifact was never registered, so there is nothing to route on.
    """
    graph = two_node_graph(
        stance(evidence_links=(link(source_id="ART-NOT-HELD", sha256=None),))
    )

    assert graph.node_ids == ()
    assert graph.edge_ids == ()
    assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in graph.node_rejection("A")

    result = EvidenceGatedRouter(graph).route("A", "B")
    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert result.total_distance_meters is None
    assert result.step_free is None


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"source_id": "ART-DOES-NOT-EXIST"}, AdmissionRejection.ARTIFACT_NOT_REGISTERED),
        ({"source_id": ""}, AdmissionRejection.ARTIFACT_NOT_REGISTERED),
        ({"sha256": None}, AdmissionRejection.NOT_CONTENT_ADDRESSED),
        ({"sha256": "de" * 32}, AdmissionRejection.DIGEST_MISMATCH),
        (
            {"evidence_condition": EvidenceCondition.CONFLICTED},
            AdmissionRejection.STANCE_CONTRADICTS_LINK,
        ),
        (
            {"human_review_state": HumanReviewState.REJECTED},
            AdmissionRejection.STANCE_CONTRADICTS_LINK,
        ),
        (
            {"human_review_state": HumanReviewState.SUPERSEDED},
            AdmissionRejection.STANCE_CONTRADICTS_LINK,
        ),
    ],
)
def test_every_unresolvable_link_variant_is_refused(overrides, expected):
    """Each of these declared the same qualifying axes and used to route."""
    graph = two_node_graph(stance(evidence_links=(link(**overrides),)))

    assert expected in graph.node_rejection("A")
    assert graph.node_ids == ()
    assert EvidenceGatedRouter(graph).route("A", "B").status == (
        RouteStatus.INSUFFICIENT_EVIDENCE
    )


def test_a_link_at_its_default_axes_does_not_support_an_asserted_stance():
    """`EvidenceLink` defaults to UNKNOWN/DRAFT. A stance may not overrule that."""
    bare = EvidenceLink(source_id="ART-0001", locator="Page 5", sha256=HELD_DIGEST)
    assert bare.evidence_condition == EvidenceCondition.UNKNOWN
    assert bare.human_review_state == HumanReviewState.DRAFT

    graph = two_node_graph(stance(evidence_links=(bare,)))
    assert AdmissionRejection.STANCE_CONTRADICTS_LINK in graph.node_rejection("A")
    assert graph.node_ids == ()


def test_a_non_evidence_link_object_is_not_evidence():
    """Counting a container's members never asked what they were."""
    graph = two_node_graph(stance(evidence_links=("just a string",)))

    assert AdmissionRejection.MALFORMED_EVIDENCE_LINK in graph.node_rejection("A")
    assert graph.node_ids == ()
    assert EvidenceGatedRouter(graph).route("A", "B").status == (
        RouteStatus.INSUFFICIENT_EVIDENCE
    )


def test_a_graph_without_a_verification_context_admits_nothing():
    """Being unable to check is not permission to skip the check."""
    graph = two_node_graph(stance(), verifier=None)

    assert graph.node_ids == ()
    assert graph.edge_ids == ()
    assert AdmissionRejection.NO_VERIFICATION_CONTEXT in graph.node_rejection("A")
    assert EvidenceGatedRouter(graph).route("A", "B").status == (
        RouteStatus.INSUFFICIENT_EVIDENCE
    )


def test_one_resolvable_link_cannot_launder_an_unresolvable_one():
    """Universal quantification: adding evidence never subtracts scrutiny."""
    graph = two_node_graph(
        stance(evidence_links=(LINK, link(source_id="ART-NOT-HELD", sha256=None)))
    )

    assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in graph.node_rejection("A")
    assert graph.node_ids == ()


def test_a_node_cannot_reach_even_itself_without_resolvable_evidence():
    """The self-route short circuit is a route, and needs the same admission."""
    unheld = stance(evidence_links=(link(source_id="ART-NOT-HELD", sha256=None),))
    graph = SpatialGraph(
        nodes=[SpatialNode("A", SpatialNodeType.CABIN, VESSEL_ID, DECK_NUMBER, unheld)],
        edges=(),
        verifier=VERIFIER,
    )
    result = EvidenceGatedRouter(graph).route("A", "A")

    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert result.node_ids == ()


def test_held_and_verified_evidence_still_routes():
    """The positive control. A boundary that refuses everything proves nothing."""
    graph = two_node_graph(stance())
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert graph.node_ids == ("A", "B")
    assert graph.edge_ids == ("E-AB",)
    assert result.status == RouteStatus.ROUTABLE
    assert result.total_distance_meters == 10.0
    assert result.step_free is True
    assert result.cost_basis == CostBasis.METRIC_METERS


# --- 9. live evidence mutation invalidates a graph already built ----------


@pytest.fixture
def private_evidence(tmp_path):
    """A registry holding one real artifact, outside production `evidence/`.

    These tests need bytes they are allowed to break. Production evidence is
    read-only to this suite, so they register their own.
    """
    source = tmp_path / "deckplan.txt"
    source.write_text("deck 14 plan, page 5\n", encoding="utf-8")
    root = tmp_path / "evidence" / "artifacts"
    root.mkdir(parents=True)

    registry = ArtifactRegistry(str(root))
    artifact = registry.register(
        str(source),
        document_class="official_ship_map",
        acquired_on="2026-09-03",
        acquisition_method="local_fixture",
        publisher="test",
        subject_vessels=["IMO9766205"],
    )
    return {
        "root": root,
        "artifact": artifact,
        "verifier": SpatialEvidenceVerifier(registry_factory=lambda: ArtifactRegistry(str(root))),
        "held_path": pathlib.Path(registry.resolve_path(artifact.artifact_id)),
    }


def private_graph(private_evidence):
    artifact = private_evidence["artifact"]
    return two_node_graph(
        stance(evidence_links=(link(
            source_id=artifact.artifact_id, sha256=artifact.sha256
        ),)),
        verifier=private_evidence["verifier"],
    )


def test_replacing_artifact_bytes_unroutes_the_same_graph(private_evidence):
    """No reconstruction. The graph that answered ROUTABLE stops, in place."""
    graph = private_graph(private_evidence)
    router = EvidenceGatedRouter(graph)
    assert router.route("A", "B").status == RouteStatus.ROUTABLE

    private_evidence["held_path"].write_text(
        "these are not the bytes that were verified\n", encoding="utf-8"
    )

    assert router.route("A", "B").status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert graph.node_ids == ()
    assert graph.node_rejection("A")


def test_deregistering_the_artifact_unroutes_the_same_graph(private_evidence):
    """The registry is re-read per question, so deregistration is visible."""
    artifact = private_evidence["artifact"]
    graph = private_graph(private_evidence)
    router = EvidenceGatedRouter(graph)
    assert router.route("A", "B").status == RouteStatus.ROUTABLE

    index_path = private_evidence["root"] / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    del index[artifact.artifact_id]
    index_path.write_text(json.dumps(index), encoding="utf-8")

    assert router.route("A", "B").status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in graph.node_rejection("A")


def test_adjudicated_deck14_geometry_still_needs_its_artifact(tmp_path):
    """Lifting the review axes is not enough if the evidence stops resolving.

    The counterfactual above shows adjudicated Deck 14 geometry becoming
    places. It becomes places because ART-0001 genuinely resolves. Point the
    same nodes at an empty registry and every one of them is refused.
    """
    _, nodes = _hypothetically_adjudicated_nodes()
    empty_root = tmp_path / "artifacts"
    empty_root.mkdir(parents=True)
    graph = SpatialGraph(
        nodes=nodes,
        edges=(),
        verifier=SpatialEvidenceVerifier(registry_factory=lambda: ArtifactRegistry(str(empty_root))),
    )

    assert graph.node_ids == ()
    report = graph.admission_report()
    assert len(report.rejected_nodes) == 244
    for reasons in report.rejected_nodes.values():
        assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in reasons


# --- 10. the verification context must be current, or refuse --------------
#
# The first version of `SpatialEvidenceVerifier` accepted either a registry
# factory or a retained `ArtifactRegistry`, and only recommended the factory.
# `ArtifactRegistry` reads `index.json` once in `__init__`, so the retained form
# produced ROUTABLE -> deregister -> ROUTABLE: currentness was a convention the
# caller could opt out of by accident. The factory is now the contract, and a
# context that cannot produce a current registry refuses instead of crashing.


def test_a_retained_registry_cannot_become_a_verification_context():
    """The unsafe shape is refused at construction, not adapted."""
    registry = ArtifactRegistry(ARTIFACTS_ROOT)
    with pytest.raises(TypeError, match="zero-argument callable"):
        SpatialEvidenceVerifier(registry)


@pytest.mark.parametrize("context", [object(), "evidence/artifacts", 42, []])
def test_a_non_callable_context_is_refused_at_construction(context):
    with pytest.raises(TypeError, match="zero-argument callable"):
        SpatialEvidenceVerifier(context)


def test_deregistration_is_visible_through_a_fresh_factory(private_evidence):
    """Same verifier, same graph, same router: the grant does not survive."""
    artifact = private_evidence["artifact"]
    graph = private_graph(private_evidence)
    router = EvidenceGatedRouter(graph)
    assert router.route("A", "B").status == RouteStatus.ROUTABLE

    index_path = private_evidence["root"] / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    del index[artifact.artifact_id]
    index_path.write_text(json.dumps(index), encoding="utf-8")

    result = router.route("A", "B")
    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert AdmissionRejection.ARTIFACT_NOT_REGISTERED in graph.node_rejection("A")
    assert graph.node_ids == ()
    assert graph.edge_ids == ()


def _raises():
    raise RuntimeError("registry could not be opened")


@pytest.mark.parametrize(
    "factory, label",
    [
        (lambda: None, "returns None"),
        (lambda: object(), "returns a non-registry"),
        (lambda: "not a registry", "returns a string"),
        (_raises, "raises"),
    ],
)
def test_a_factory_that_cannot_produce_a_registry_refuses(factory, label):
    """Refusal, never an AttributeError and never an admission."""
    verifier = SpatialEvidenceVerifier(registry_factory=factory)
    assert verifier.has_context is True       # a factory *was* supplied...
    assert verifier.current_registry() is None  # ...but it yields nothing usable

    graph = two_node_graph(stance(), verifier=verifier)
    assert graph.node_ids == ()
    assert graph.edge_ids == ()
    assert AdmissionRejection.VERIFICATION_CONTEXT_UNAVAILABLE in graph.node_rejection("A")
    assert EvidenceGatedRouter(graph).route("A", "B").status == (
        RouteStatus.INSUFFICIENT_EVIDENCE
    )


def test_a_factory_that_starts_failing_unroutes_a_live_graph(private_evidence):
    """Losing the context mid-life is a refusal, not a retained fallback."""
    artifact = private_evidence["artifact"]
    root = private_evidence["root"]
    broken = {"fail": False}

    def factory():
        if broken["fail"]:
            raise RuntimeError("registry became unreadable")
        return ArtifactRegistry(str(root))

    graph = two_node_graph(
        stance(evidence_links=(link(
            source_id=artifact.artifact_id, sha256=artifact.sha256
        ),)),
        verifier=SpatialEvidenceVerifier(registry_factory=factory),
    )
    router = EvidenceGatedRouter(graph)
    assert router.route("A", "B").status == RouteStatus.ROUTABLE

    broken["fail"] = True

    assert router.route("A", "B").status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert AdmissionRejection.VERIFICATION_CONTEXT_UNAVAILABLE in graph.node_rejection("A")


def test_no_factory_is_a_different_refusal_from_a_broken_one():
    """"You gave me nothing" and "yours does not work" are separate operator facts."""
    assert NO_VERIFICATION.has_context is False
    assert NO_VERIFICATION.current_registry() is None

    absent = two_node_graph(stance(), verifier=None)
    broken = two_node_graph(
        stance(), verifier=SpatialEvidenceVerifier(registry_factory=lambda: None)
    )

    assert AdmissionRejection.NO_VERIFICATION_CONTEXT in absent.node_rejection("A")
    assert AdmissionRejection.VERIFICATION_CONTEXT_UNAVAILABLE in broken.node_rejection("A")
    assert absent.node_ids == () and broken.node_ids == ()


def test_the_production_deck14_verifier_is_factory_backed():
    """The one production context must satisfy the contract it documents."""
    verifier = evidence_verifier()
    assert callable(verifier._registry_factory)

    first = verifier.current_registry()
    second = verifier.current_registry()
    assert isinstance(first, ArtifactRegistry)
    # A distinct object per call: the index is re-read, never reused.
    assert first is not second
