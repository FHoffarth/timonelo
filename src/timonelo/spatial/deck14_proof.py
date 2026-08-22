"""
The MSC Bellissima Deck 14 proof slice, loaded from the canonical geometry proof.

Source of truth for this module is
`geometry/proofs/bellissima/deck14/deck14.proof.json`
(schema `timonelo.one-deck-geometry-proof.v1`), produced by
`scripts/extract_bellissima_one_deck_geometry_proof.py` from ART-0001 page 5
and written up in `knowledge/reports/bellissima_one_deck_geometry_proof.md`.

ART-0001 bytes are held. They resolve through
`timonelo.evidence.registry.ArtifactRegistry.resolve_path` to the canonical
content-addressed vault at `evidence/raw/sha256/08/<digest>.pdf`, and the
digest is recomputed from those bytes rather than copied from the index. The
legacy `evidence/artifacts/blobs/` directory is empty and is consulted by the
resolver only when the canonical vault holds nothing; this module never reads
it directly.

What the canonical proof establishes:
    * ten cabin labels (14001-14010) each uniquely contained by one
      source-drawn vector boundary -> TRANSFORMED_SOURCE_GEOMETRY, backed by
      DIRECT_SOURCE_GEOMETRY drawing records
    * one labelled lift region -> DERIVED_GEOMETRY (union bbox of two direct
      source vector groups)

What it explicitly refuses to establish, and what this module therefore will
not manufacture:
    * corridor geometry — the apparent corridor is INFERRED_NEGATIVE_SPACE
      with `accepted_geometry: false`; negative space is not a walkable edge
    * any door, or any cabin-to-corridor connection
    * lift connectivity, cross-deck identity or nearest-core status — the
      proof records that its lift region "establishes neither the exact
      functional boundary nor cross-deck identity, nearest-core status,
      connectivity, or travel distance"
    * any metric length. Normalized coordinates are fractions of the PDF page
      MediaBox, not metres. No scale bar has been read, so no distance exists.
    * `navigation_graph` is `null` in the proof. There is no graph to import.

Two independent reasons therefore keep this deck non-routable, and the tests
assert both:

  1. Publication. Every proof object is `DRAFT` / `UNKNOWN` /
     `PUBLISH_BLOCKED` pending human adjudication, so none is admitted.
  2. Connectivity. Even under a hypothetical adjudication, the proof contains
     no edge of any kind. Genuine cabin geometry establishes a spatial
     envelope; it does not establish that one can walk from one envelope to
     another.

`geometry/deck14.geometry.json` is NOT read here. Its cabin polygons are laid
out by `scripts/extract_spatial_geometry.py` on an evenly spaced synthetic
strip and its lifts and corridors are hardcoded constants. The proof report
records all fifteen such files as SYNTHETIC_GEOMETRY and non-canonical; the
admission gate in `spatial.graph` would refuse them even if they were loaded.

Separately: `evidence/statements/statements.json` holds 113 PUBLISHED
statements about Deck 14 staterooms 14102-14136. That cabin set is disjoint
from the geometry proof set 14001-14010, and those statements carry no
geometry at all. No cabin on this ship currently has both a published fact and
a source-linked shape, which is why nothing here is both admitted and located.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

from timonelo.evidence.registry import ArtifactRegistry, sha256_of_file
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    EvidenceLink,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)
from timonelo.spatial.graph import (
    EvidenceStance,
    SpatialGraph,
    SpatialNode,
    SpatialNodeType,
)

VESSEL_ID = "MSC-BELLISSIMA"
DECK_NUMBER = 14
ARTIFACT_ID = "ART-0001"
PROOF_SCHEMA = "timonelo.one-deck-geometry-proof.v1"

PROOF_RELATIVE_PATH = os.path.join(
    "geometry", "proofs", "bellissima", "deck14", "deck14.proof.json"
)

#: Proof `semantic_type` mapped onto canonical node types. A
#: `vertical_core_region` is a labelled region, not a working lift: the proof
#: states it establishes no connectivity, so it enters the graph (if ever
#: adjudicated) as a place, never as a transfer.
_SEMANTIC_TYPE_MAP: Dict[str, SpatialNodeType] = {
    "cabin": SpatialNodeType.CABIN,
    "vertical_core_region": SpatialNodeType.LIFT,
}

_GEOMETRY_PROVENANCE_MAP = {p.value: p for p in GeometryProvenance}
_EVIDENCE_CONDITION_MAP = {c.value: c for c in EvidenceCondition}
_REVIEW_STATE_MAP = {s.value: s for s in HumanReviewState}
_PUBLISH_STATUS_MAP = {s.value: s for s in PublishStatus}


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def default_proof_path() -> str:
    return os.path.join(repo_root(), PROOF_RELATIVE_PATH)


def load_proof(path: Optional[str] = None) -> dict:
    """Loads the canonical Deck 14 proof, refusing an unexpected schema."""
    with open(path or default_proof_path(), "r", encoding="utf-8") as handle:
        proof = json.load(handle)
    if proof.get("schema") != PROOF_SCHEMA:
        raise ValueError(
            f"Unexpected proof schema {proof.get('schema')!r}; "
            f"this loader only understands {PROOF_SCHEMA!r}."
        )
    if proof.get("deck", {}).get("number") != DECK_NUMBER:
        raise ValueError("Proof is not the locked Deck 14 proof.")
    return proof


def resolve_artifact(
    artifact_id: str = ARTIFACT_ID, evidence_root: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Resolves ART-0001 through the canonical resolver.

    Returns `(path, sha256)` where the digest is recomputed from the resolved
    bytes. Returns `(None, None)` when the resolver holds nothing or fails
    closed on ambiguity — a digest is never taken from the index in that case,
    because an index entry is a claim about bytes, not the bytes.
    """
    root = evidence_root or os.path.join(repo_root(), "evidence", "artifacts")
    registry = ArtifactRegistry(root)
    if not registry.has(artifact_id):
        return None, None
    path = registry.resolve_path(artifact_id)
    if path is None:
        return None, None
    return path, sha256_of_file(path)


def _stance_from_proof_object(
    obj: dict, sha256: Optional[str], proof: dict
) -> EvidenceStance:
    """Reads the four axes off the proof object. Nothing is upgraded."""
    source = proof.get("source", {})
    locator = (
        f"page{source.get('pdf_page_number')}:"
        f"{obj.get('object_id')}:"
        f"{','.join(obj.get('source_references', ())) or 'no-source-reference'}"
    )
    geometry_provenance = _GEOMETRY_PROVENANCE_MAP.get(
        obj.get("geometry_provenance", ""), GeometryProvenance.UNKNOWN_PROVENANCE
    )
    # A DERIVED_GEOMETRY object was computed from direct source records, so its
    # method is CALCULATED; a transformed source polygon was read, not computed.
    method = (
        Method.CALCULATED
        if geometry_provenance == GeometryProvenance.DERIVED_GEOMETRY
        else Method.DIRECT
    )
    evidence_condition = _EVIDENCE_CONDITION_MAP.get(
        obj.get("evidence_condition", ""), EvidenceCondition.UNKNOWN
    )
    human_review_state = _REVIEW_STATE_MAP.get(
        obj.get("human_review_state", ""), HumanReviewState.DRAFT
    )

    # The link restates the same axes rather than leaving them at their
    # defaults, so a link read in isolation cannot look more settled than the
    # object it came from. `sha256` is a digest recomputed from held bytes or
    # None — never a placeholder; ontology.EvidenceLink rejects those anyway.
    links = (
        EvidenceLink(
            source_id=ARTIFACT_ID,
            locator=locator,
            sha256=sha256,
            method=method,
            derivation=Derivation.LOCAL,
            evidence_condition=evidence_condition,
            human_review_state=human_review_state,
            observed_on=source.get("extraction_timestamp"),
        ),
    )

    return EvidenceStance(
        evidence_condition=evidence_condition,
        human_review_state=human_review_state,
        publish_status=_PUBLISH_STATUS_MAP.get(
            obj.get("publish_status", ""), PublishStatus.PUBLISH_BLOCKED
        ),
        geometry_provenance=geometry_provenance,
        method=method,
        derivation=Derivation.LOCAL,
        evidence_links=links,
    )


def build_deck14_nodes(
    proof: Optional[dict] = None,
    sha256: Optional[str] = None,
) -> List[SpatialNode]:
    """Builds one candidate node per proof object, carrying its declared axes.

    "Candidate" is the operative word: whether a node is admitted is decided
    by `SpatialGraph`, not here. This function never rewrites a review state.
    """
    proof = proof if proof is not None else load_proof()
    if sha256 is None:
        _, sha256 = resolve_artifact()

    nodes: List[SpatialNode] = []
    for obj in proof.get("objects", []):
        node_type = _SEMANTIC_TYPE_MAP.get(obj.get("semantic_type", ""))
        if node_type is None:
            # An unrecognised semantic type is not quietly coerced to a place.
            continue
        label = obj.get("cabin_number") or obj.get("semantic_type")
        nodes.append(
            SpatialNode(
                node_id=obj["object_id"],
                node_type=node_type,
                vessel_id=VESSEL_ID,
                deck_number=DECK_NUMBER,
                label=label,
                stance=_stance_from_proof_object(obj, sha256, proof),
            )
        )
    return nodes


def build_deck14_graph(proof_path: Optional[str] = None) -> SpatialGraph:
    """Builds the Deck 14 spatial graph from the canonical proof.

    No edges are produced. The proof's `navigation_graph` is null, its
    corridor observation is rejected negative space, and its lift region
    disclaims connectivity. There is nothing to connect.
    """
    proof = load_proof(proof_path)
    return SpatialGraph(nodes=build_deck14_nodes(proof), edges=())


def deck14_connectivity_findings(proof: Optional[dict] = None) -> Dict[str, str]:
    """Why Deck 14 has no edges, quoted from the proof rather than asserted."""
    proof = proof if proof is not None else load_proof()
    corridor = proof.get("corridor_observation") or {}
    return {
        "navigation_graph": (
            "ABSENT" if proof.get("navigation_graph") is None else "PRESENT"
        ),
        "corridor": (
            f"{corridor.get('classification')} "
            f"(accepted_geometry={corridor.get('accepted_geometry')})"
        ),
        "nearest_core_calculation": (
            "ABSENT" if proof.get("nearest_core_calculation") is None else "PRESENT"
        ),
        "cross_deck_relationships": str(len(proof.get("cross_deck_relationships") or [])),
        "port_starboard_associations": str(
            len(proof.get("port_starboard_associations") or [])
        ),
        "metric_scale": (
            f"ABSENT (target_units="
            f"{proof.get('transform', {}).get('target_units')!r})"
        ),
    }
