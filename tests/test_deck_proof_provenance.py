"""
Proof provenance records must describe the proofs they sit next to.

A staged Deck 14 adjudication carries `proof_sha256` so that whatever applies it
later can refuse a record made against a proof that has since been regenerated.
That guarantee is only worth the digest being correct, and the digest lives in a
JSON file beside the proof rather than being computed in the browser, which
cannot hash its own imported modules.

So the two can drift, and this is what notices. Regenerate a proof without
regenerating its provenance and the review workspace would keep stamping staged
records with the digest of a proof that no longer exists.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = REPO_ROOT / "geometry" / "proofs" / "bellissima"
DECKS = ("05", "06", "07", "14")


def _paths(deck: str) -> tuple[Path, Path]:
    return (
        PROOF_DIR / f"deck{deck}" / f"deck{deck}.proof.json",
        PROOF_DIR / f"deck{deck}" / f"deck{deck}.proof.provenance.json",
    )


@pytest.mark.parametrize("deck", DECKS)
def test_every_reviewable_proof_has_a_provenance_record(deck: str) -> None:
    proof, prov = _paths(deck)
    assert proof.is_file(), f"{proof} is missing"
    assert prov.is_file(), f"{prov} is missing"


@pytest.mark.parametrize("deck", DECKS)
def test_provenance_digest_matches_the_proof_bytes(deck: str) -> None:
    proof, prov = _paths(deck)
    recorded = json.loads(prov.read_text(encoding="utf-8"))["output_sha256"]
    assert recorded == hashlib.sha256(proof.read_bytes()).hexdigest(), (
        f"deck{deck} proof provenance is stale: regenerate "
        f"{prov.name} whenever {proof.name} changes"
    )


@pytest.mark.parametrize("deck", DECKS)
def test_provenance_describes_the_proof_it_names(deck: str) -> None:
    proof, prov = _paths(deck)
    doc = json.loads(proof.read_text(encoding="utf-8"))
    rec = json.loads(prov.read_text(encoding="utf-8"))

    assert rec["proof"]["deck_number"] == doc["deck"]["number"]
    assert rec["proof"]["object_count"] == len(doc["objects"])

    source = doc.get("source", {})
    assert rec["source"]["artifact_id"] == source.get("artifact_id")
    assert rec["source"]["artifact_sha256"] == (
        source.get("artifact_sha256") or source.get("sha256")
    )
    assert rec["source"]["pdf_page_number"] == (
        source.get("pdf_page_number") or source.get("page_number")
    )


def test_proof_and_raster_digests_are_independent_bindings() -> None:
    """Three separate things are identified, and none stands in for another."""
    _, prov = _paths("14")
    proof_sha = json.loads(prov.read_text(encoding="utf-8"))["output_sha256"]
    raster = json.loads(
        (REPO_ROOT / "frontend" / "public" / "data" / "deck14.page5.provenance.json")
        .read_text(encoding="utf-8")
    )
    assert proof_sha != raster["output_sha256"]
    assert proof_sha != raster["source"]["sha256"]
    assert raster["output_sha256"] != raster["source"]["sha256"]


def test_the_served_deck14_proof_is_the_governed_one() -> None:
    """The review workspace reads geometry/, the Ships page reads public/data/.

    They must be the same bytes, or the two surfaces are adjudicating and
    displaying different Deck 14s while citing one digest.
    """
    governed = (PROOF_DIR / "deck14" / "deck14.proof.json").read_bytes()
    served = (REPO_ROOT / "frontend" / "public" / "data" / "deck14.proof.json").read_bytes()
    assert hashlib.sha256(governed).hexdigest() == hashlib.sha256(served).hexdigest()
