"""
tests/test_source_harvester.py

Unit tests for Official Source Harvester v0.1:
- Domain Trust Tiers (A, B, C)
- Byte-level PDF Verification & Magic Bytes
- Deterministic Fingerprinting (SHA-256)
- Document Classification (DECK_PLAN vs UNKNOWN)
- Deterministic Vessel Resolution
- Immutable Vault & Duplicate Detection
- Strict Origin Provenance (FIXTURE_ONLY vs LIVE_VERIFIED)
- Source Registry & Version Candidate Tracking
"""

import os
import io
import tempfile
import pytest

from timonelo.harvester.config import classify_domain_tier
from timonelo.harvester.models import (
    SourceTrustTier, DocumentType, HarvestState, HarvestedArtifactRecord,
    OriginVerificationStatus
)
from timonelo.harvester.vessel_resolver import resolve_vessel
from timonelo.harvester.classifier import classify_document
from timonelo.harvester.verifier import verify_pdf_bytes, compute_bytes_sha256
from timonelo.harvester.vault import EvidenceVault
from timonelo.harvester.registry import SourceRegistry
from timonelo.harvester.engine import HarvestEngine


FIXTURE_PDF = "tests/fixtures/MSC_MERAVIGLIA_DECKPLAN_GER.pdf"


# =========================================================================
# 1. DOMAIN TRUST TIER TESTS
# =========================================================================

def test_domain_trust_tiers():
    assert classify_domain_tier("msccruises.de") == "TIER_A"
    assert classify_domain_tier("www.msccruises.com") == "TIER_A"
    assert classify_domain_tier("mscpressarea.com") == "TIER_A"
    assert classify_domain_tier("msc-media.azureedge.net") == "TIER_B"
    assert classify_domain_tier("assets.msccruises.com") == "TIER_B"
    assert classify_domain_tier("cruisecritic.com") == "TIER_C"
    assert classify_domain_tier("random-travel-blog.org") == "TIER_C"


# =========================================================================
# 2. PDF VERIFICATION & MAGIC BYTES TESTS
# =========================================================================

def test_verify_pdf_valid_fixture():
    assert os.path.isfile(FIXTURE_PDF)
    with open(FIXTURE_PDF, "rb") as f:
        data = f.read()

    is_valid, reason, vdata = verify_pdf_bytes(data)
    assert is_valid is True
    assert reason == "VALID_PDF"
    assert vdata["page_count"] == 6
    assert vdata["sha256"] == "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"
    assert vdata["mime_type"] == "application/pdf"


def test_verify_pdf_html_masquerade_rejected():
    fake_html = b"<!DOCTYPE html><html><head><title>404 Not Found</title></head></html>"
    is_valid, reason, _ = verify_pdf_bytes(fake_html)
    assert is_valid is False
    assert reason == "HTML_MASQUERADING_AS_PDF"


def test_verify_pdf_corrupt_rejected():
    corrupt_data = b"%PDF-1.4 CORRUPT DATA TRUNCATED"
    is_valid, reason, _ = verify_pdf_bytes(corrupt_data)
    assert is_valid is False
    assert "CORRUPT_PDF_PARSE_ERROR" in reason


def test_verify_pdf_empty_rejected():
    is_valid, reason, _ = verify_pdf_bytes(b"")
    assert is_valid is False
    assert reason == "EMPTY_PAYLOAD"


# =========================================================================
# 3. SHA-256 DETERMINISTIC FINGERPRINT TESTS
# =========================================================================

def test_deterministic_sha256():
    payload_a = b"%PDF-1.7 Test Deckplan Payload"
    payload_b = b"%PDF-1.7 Test Deckplan Payload"
    payload_c = b"%PDF-1.7 Different Deckplan Payload"

    hash_a = compute_bytes_sha256(payload_a)
    hash_b = compute_bytes_sha256(payload_b)
    hash_c = compute_bytes_sha256(payload_c)

    assert hash_a == hash_b
    assert hash_a != hash_c


# =========================================================================
# 4. CLASSIFICATION TESTS
# =========================================================================

def test_classify_deck_plan():
    doc_type, meta = classify_document(
        first_page_text="MSC MERAVIGLIA DECKPLÄNE 11.2025 DEU",
        filename="MSC_MERAVIGLIA_DECKPLAN_GER.pdf"
    )
    assert doc_type == DocumentType.DECK_PLAN
    assert meta["language"] == "de"
    assert meta["edition"] == "11.2025"


def test_classify_unrelated_document():
    doc_type, meta = classify_document(
        first_page_text="Terms and Conditions for Passenger Bookings",
        filename="booking_terms.pdf"
    )
    assert doc_type == DocumentType.UNKNOWN


# =========================================================================
# 5. VESSEL RESOLVER TESTS
# =========================================================================

def test_vessel_resolver_exact_and_alias():
    vid, status = resolve_vessel("MSC Meraviglia Deckpläne")
    assert vid == "msc-meraviglia"
    assert status == "RESOLVED"

    vid2, status2 = resolve_vessel("Deck plan for MSC Bellissima 2026")
    assert vid2 == "msc-bellissima"
    assert status2 == "RESOLVED"


def test_vessel_resolver_ambiguous():
    vid, status = resolve_vessel("Comparison between MSC Meraviglia and MSC Bellissima")
    assert vid is None
    assert status == "MANUAL_REVIEW_REQUIRED"


def test_vessel_resolver_unresolved():
    vid, status = resolve_vessel("General Ship Information")
    assert vid is None
    assert status == "VESSEL_UNRESOLVED"


# =========================================================================
# 6. VAULT, REGISTRY & DUPLICATE TESTS
# =========================================================================

def test_vault_and_registry_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = os.path.join(tmpdir, "vault")
        registry_file = os.path.join(tmpdir, "registry.json")

        engine = HarvestEngine(vault_root=vault_root, registry_file=registry_file)

        with open(FIXTURE_PDF, "rb") as f:
            data = f.read()

        # Run 1: New Registration
        state1, rec1, meta1 = engine.process_raw_bytes(
            data,
            source_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            final_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            discovery_method="KNOWN_PATTERN",
            dry_run=False
        )
        assert state1 == HarvestState.REGISTERED
        assert rec1 is not None
        assert meta1["is_duplicate"] is False
        assert rec1.origin_verification_status == "LIVE_VERIFIED"
        assert os.path.isfile(os.path.join(tmpdir, rec1.vault_path))

        # Run 2: Duplicate Ingest (same bytes)
        state2, rec2, meta2 = engine.process_raw_bytes(
            data,
            source_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            final_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            discovery_method="KNOWN_PATTERN",
            dry_run=False
        )
        assert state2 == HarvestState.DUPLICATE
        assert meta2["is_duplicate"] is True
        assert rec2.sha256 == rec1.sha256
        assert len(rec2.retrieval_history) == 2


# =========================================================================
# 7. STRICT ORIGIN PROVENANCE SEPARATION TESTS
# =========================================================================

def test_fixture_origin_status_cannot_be_live_verified():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = os.path.join(tmpdir, "vault")
        registry_file = os.path.join(tmpdir, "registry.json")
        engine = HarvestEngine(vault_root=vault_root, registry_file=registry_file)

        with open(FIXTURE_PDF, "rb") as f:
            data = f.read()

        state, rec, _ = engine.process_raw_bytes(
            data,
            source_url=f"file:///{os.path.abspath(FIXTURE_PDF)}",
            final_url=f"file:///{os.path.abspath(FIXTURE_PDF)}",
            discovery_method="LOCAL_FIXTURE"
        )
        assert state == HarvestState.REGISTERED
        assert rec.discovery_method == "LOCAL_FIXTURE"
        assert rec.origin_verification_status == "FIXTURE_ONLY"
        assert rec.origin_verified_at is None


def test_tier_c_origin_status_is_candidate_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = os.path.join(tmpdir, "vault")
        registry_file = os.path.join(tmpdir, "registry.json")
        engine = HarvestEngine(vault_root=vault_root, registry_file=registry_file)

        with open(FIXTURE_PDF, "rb") as f:
            data = f.read()

        state, rec, _ = engine.process_raw_bytes(
            data,
            source_url="https://www.cruisemapper.com/deckplans/msc-meraviglia.pdf",
            final_url="https://www.cruisemapper.com/deckplans/msc-meraviglia.pdf",
            discovery_method="SEARCH_HINT"
        )
        assert state == HarvestState.REGISTERED
        assert rec.source_tier == SourceTrustTier.TIER_C
        assert rec.verification_status == "UNVERIFIED_THIRD_PARTY"
        assert rec.origin_verification_status == "CANDIDATE_ONLY"
        assert rec.origin_verified_at is None
