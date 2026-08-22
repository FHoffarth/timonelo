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
from timonelo.spatial import (
    AdmissionRejection,
    CostBasis,
    EvidenceGatedRouter,
    EvidenceStance,
    RouteStatus,
    RouteUnknown,
    SpatialEdge,
    SpatialEdgeType,
    SpatialGraph,
    SpatialNode,
    SpatialNodeType,
)
from timonelo.spatial.deck14_proof import (
    ARTIFACT_ID,
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

LINK = EvidenceLink(source_id="ART-0001", locator="Page 5, Deck 14 plan", sha256=None)


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
    graph = SpatialGraph(
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
    reversed_graph = SpatialGraph(
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
    graph = SpatialGraph(
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
    graph = SpatialGraph(
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
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=3.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "LIFT-CORE-A-D14")

    assert result.status == RouteStatus.INSUFFICIENT_EVIDENCE
    assert any("DESTINATION_NODE_UNKNOWN" in r for r in result.blocking_reasons)


# --- 3. synthetic geometry cannot silently qualify as route truth ----------


def test_synthetic_geometry_node_is_refused_admission():
    graph = SpatialGraph(
        nodes=[
            node("A"),
            node("SYNTH", geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY),
        ]
    )
    assert graph.node_ids == ("A",)
    assert AdmissionRejection.SYNTHETIC_GEOMETRY in graph.node_rejection("SYNTH")


def test_synthetic_edge_cannot_connect_two_evidenced_nodes():
    graph = SpatialGraph(
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

    graph = SpatialGraph()
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
    graph = SpatialGraph(
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
    graph = SpatialGraph(
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
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=4.0, step_free=True)],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert result.total_distance_meters == 4.0
    assert RouteUnknown.WALKING_TIME in result.unknowns
    assert not hasattr(result, "estimated_walking_seconds")


# --- 5. missing accessibility evidence does not become accessible=true ----


def test_unknown_step_free_stays_unknown():
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=4.0, step_free=None)],
    )
    result = EvidenceGatedRouter(graph).route("A", "B")

    assert result.status == RouteStatus.ROUTABLE
    assert result.step_free is None
    assert RouteUnknown.STEP_FREE_ACCESSIBILITY in result.unknowns


def test_step_free_only_when_every_edge_says_so():
    graph = SpatialGraph(
        nodes=[node("A"), node("B"), node("C")],
        edges=[
            edge("E-AB", "A", "B", length_meters=1.0, step_free=True),
            edge("E-BC", "B", "C", length_meters=1.0, step_free=None),
        ],
    )
    result = EvidenceGatedRouter(graph).route("A", "C")
    assert result.step_free is None


def test_step_free_request_excludes_unknown_edges_rather_than_assuming_them():
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-AB", "A", "B", length_meters=1.0, step_free=None)],
    )
    router = EvidenceGatedRouter(graph)

    assert router.route("A", "B").status == RouteStatus.ROUTABLE
    assert router.route("A", "B", require_step_free=True).status == RouteStatus.NOT_ROUTABLE


# --- 6. route evidence/provenance is preserved ----------------------------


def test_route_carries_provenance_for_every_component():
    graph = SpatialGraph(
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
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-GEN", "A", "B", derivation=Derivation.GENERATED)],
    )
    assert AdmissionRejection.GENERATED_DERIVATION in graph.edge_rejection("E-GEN")
    assert graph.edge_ids == ()


def test_inferred_method_is_refused():
    graph = SpatialGraph(
        nodes=[node("A"), node("B")],
        edges=[edge("E-INF", "A", "B", method=Method.INFERRED)],
    )
    assert AdmissionRejection.INFERRED_METHOD in graph.edge_rejection("E-INF")


def test_publish_blocked_edge_stays_blocked_even_with_a_generated_duplicate():
    graph = SpatialGraph(
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
    graph = SpatialGraph(
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
    graph = SpatialGraph(
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
    assert len(proof["objects"]) == 11
    for obj in proof["objects"]:
        assert obj["human_review_state"] == "DRAFT"
        assert obj["evidence_condition"] == "UNKNOWN"
        assert obj["publish_status"] == "PUBLISH_BLOCKED"

    graph = build_deck14_graph()
    assert graph.node_ids == ()
    assert graph.edge_ids == ()

    report = graph.admission_report()
    assert len(report.rejected_nodes) == 11
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
    even if a human approved all ten cabin boundaries tomorrow, the proof
    still contains no connection between them.
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
    graph = SpatialGraph(nodes=nodes, edges=())

    # All ten cabins plus the lift region become places...
    assert len(graph.node_ids) == 11
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
    graph = SpatialGraph(nodes=nodes, edges=())
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

    graph = SpatialGraph(nodes=nodes, edges=())
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
    graph = SpatialGraph(nodes=nodes, edges=())
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


def test_proof_cabin_set_is_disjoint_from_the_published_statement_set():
    """No Bellissima cabin currently has both a published fact and a shape."""
    proof = load_proof()
    geometry_cabins = {
        o["cabin_number"] for o in proof["objects"] if o["semantic_type"] == "cabin"
    }
    assert geometry_cabins == {f"140{n:02d}" for n in range(1, 11)}

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
    assert geometry_cabins.isdisjoint(statement_cabins)


def test_proof_path_is_the_locked_deck14_proof():
    assert default_proof_path().replace("\\", "/").endswith(
        "geometry/proofs/bellissima/deck14/deck14.proof.json"
    )
    with pytest.raises(ValueError, match="Unexpected proof schema"):
        load_proof(
            os.path.join(repo_root(), "evidence", "artifacts", "index.json")
        )
