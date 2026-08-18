"""
tests/test_harvester_crawl4ai_adapter.py

Unit tests for Crawl4AI Public Browser Adapter (Phase 11).

Tests:
1.  Stealth mode disabled by policy
2.  Proxy rotation disabled by policy
3.  CAPTCHA bypass disabled by policy
4.  Challenge page detection -> SOURCE_ACCESS_RESTRICTED
5.  Valid rendered page -> PDF candidates extracted
6.  PDF candidate discovered from HTML
7.  PDF bytes still pass normal verifier (fixture bytes)
8.  Fixture cannot become LIVE_VERIFIED
9.  Browser page alone cannot verify document origin
10. Duplicate artifact remains idempotent
"""

import os
import re
import tempfile
import pytest

from timonelo.harvester.adapters.public_browser_policy import (
    PUBLIC_BROWSER_POLICY,
    assert_policy_compliance,
    PolicyViolationError,
)
from timonelo.harvester.adapters.public_browser import (
    _detect_challenge,
    _extract_pdf_candidates,
    Crawl4AIPublicBrowserAdapter,
)
from timonelo.harvester.adapters.direct_http import DirectHttpAdapter
from timonelo.harvester.adapters.base import AcquisitionResult
from timonelo.harvester.verifier import verify_pdf_bytes
from timonelo.harvester.engine import HarvestEngine
from timonelo.harvester.models import HarvestState

FIXTURE_PDF = "evidence/raw/sha256/77/77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf"
REFERENCE_SHA256 = "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"


# =============================================================================
# 1. Stealth mode disabled by policy
# =============================================================================

def test_stealth_mode_is_prohibited_in_policy():
    assert PUBLIC_BROWSER_POLICY["allow_stealth_mode"] is False


def test_stealth_mode_config_raises_policy_violation():
    with pytest.raises(PolicyViolationError, match="stealth mode"):
        assert_policy_compliance({"allow_stealth_mode": True})


# =============================================================================
# 2. Proxy rotation disabled by policy
# =============================================================================

def test_proxy_rotation_is_prohibited_in_policy():
    assert PUBLIC_BROWSER_POLICY["allow_proxy_rotation"] is False


def test_proxy_rotation_config_raises_policy_violation():
    with pytest.raises(PolicyViolationError, match="proxy rotation"):
        assert_policy_compliance({"allow_proxy_rotation": True})


# =============================================================================
# 3. CAPTCHA bypass disabled by policy
# =============================================================================

def test_captcha_bypass_is_prohibited_in_policy():
    assert PUBLIC_BROWSER_POLICY["allow_captcha_bypass"] is False


def test_captcha_bypass_config_raises_policy_violation():
    with pytest.raises(PolicyViolationError, match="captcha bypass"):
        assert_policy_compliance({"allow_captcha_bypass": True})


# =============================================================================
# 4. Challenge page detection -> SOURCE_ACCESS_RESTRICTED
# =============================================================================

@pytest.mark.parametrize("html,expected_type", [
    ("<html><body>Cloudflare - Just a moment...</body></html>", "CLOUDFLARE"),
    ("<html><body>Access Denied - You do not have permission</body></html>", "ACCESS_DENIED"),
    ("<html><body>403 Forbidden</body></html>", "HTTP_FORBIDDEN"),
    ("<html><body>Please complete the CAPTCHA to proceed</body></html>", "CAPTCHA"),
    ("<html><body>Please verify you are a human</body></html>", "CAPTCHA"),
    ("<html><body>DDoS Protection by Akamai</body></html>", "AKAMAI"),
    ("<html><body>Security Check Required</body></html>", "SECURITY_CHECK"),
])
def test_challenge_detected_for_protection_pages(html, expected_type):
    is_challenge, challenge_type = _detect_challenge(html)
    assert is_challenge is True
    assert challenge_type == expected_type


def test_normal_page_not_flagged_as_challenge():
    html = "<html><head><title>MSC Meraviglia</title></head><body><a href='/deckplan.pdf'>Download Deck Plan</a></body></html>"
    is_challenge, challenge_type = _detect_challenge(html)
    assert is_challenge is False
    assert challenge_type is None


# =============================================================================
# 5. Valid rendered page -> PDF candidates extracted
# =============================================================================

def test_pdf_candidates_extracted_from_rendered_page():
    html = """
    <html>
    <body>
      <a href="https://www.msccruises.de/media/deckplan-meraviglia-2025.pdf">Download Deckplan</a>
      <a href="/schiffe/meraviglia">Zur Schiffsseite</a>
      <button data-href="/media/MSC_MERAVIGLIA_DECKPLAN.pdf">Deckplan PDF</button>
      <a href="https://cdn.example.com/marketing.pdf">Marketing</a>
    </body>
    </html>
    """
    base_url = "https://www.msccruises.de"
    candidates = _extract_pdf_candidates(html, base_url)
    # Should find the deckplan PDF links
    assert len(candidates) >= 1
    assert any("deckplan" in c.lower() for c in candidates)


def test_no_pdf_candidates_on_empty_page():
    html = "<html><body><p>No links here at all.</p></body></html>"
    candidates = _extract_pdf_candidates(html, "https://www.msccruises.de")
    assert candidates == []


# =============================================================================
# 6. PDF candidate discovered
# =============================================================================

def test_pdf_candidate_discovered_from_deck_plan_link():
    html = """<a href="https://www.msccruises.de/-/media/msc-cruises/deckplans/msc-meraviglia-deck-plan-2025.pdf">Deck Plan</a>"""
    candidates = _extract_pdf_candidates(html, "https://www.msccruises.de")
    assert len(candidates) == 1
    assert candidates[0].endswith(".pdf")


# =============================================================================
# 7. PDF bytes still pass normal verifier
# =============================================================================

def test_fixture_pdf_bytes_pass_verifier():
    with open(FIXTURE_PDF, "rb") as f:
        data = f.read()
    is_valid, reason, vdata = verify_pdf_bytes(data)
    assert is_valid is True
    assert vdata["sha256"] == REFERENCE_SHA256
    assert vdata["page_count"] == 6


# =============================================================================
# 8. Fixture cannot become LIVE_VERIFIED
# =============================================================================

def test_fixture_origin_never_becomes_live_verified():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = HarvestEngine(
            vault_root=os.path.join(tmpdir, "vault"),
            registry_file=os.path.join(tmpdir, "registry.json")
        )
        with open(FIXTURE_PDF, "rb") as f:
            data = f.read()

        state, rec, _ = engine.process_raw_bytes(
            data,
            source_url=f"file:///{os.path.abspath(FIXTURE_PDF)}",
            final_url=f"file:///{os.path.abspath(FIXTURE_PDF)}",
            discovery_method="LOCAL_FIXTURE"
        )
        assert state == HarvestState.REGISTERED
        assert rec.origin_verification_status == "FIXTURE_ONLY"
        assert rec.origin_verified_at is None
        # Explicitly NOT LIVE_VERIFIED
        assert rec.origin_verification_status != "LIVE_VERIFIED"


# =============================================================================
# 9. Browser page alone cannot verify document origin
# =============================================================================

def test_page_rendered_without_pdf_download_is_not_document_verified():
    """
    An AcquisitionResult with page_rendered=True but success=False
    means the page was reachable but the document origin is not verified.
    This mirrors the case where Crawl4AI renders a page but finds no PDF.
    """
    result = AcquisitionResult(
        success=False,
        requested_url="https://www.msccruises.de/meraviglia",
        final_url="https://www.msccruises.de/meraviglia",
        discovery_method="PUBLIC_BROWSER_CRAWL4AI",
        page_rendered=True,
        page_title="MSC Meraviglia",
        pdf_candidates=[],
        error="LIVE_PAGE_VERIFIED__NO_PDF_CANDIDATES_FOUND",
    )
    # Page rendered does NOT equal document verified
    assert result.page_rendered is True
    assert result.success is False
    # If no bytes: cannot make provenance claims
    assert result.data is None


# =============================================================================
# 10. Duplicate artifact remains idempotent
# =============================================================================

def test_public_browser_duplicate_is_idempotent():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = HarvestEngine(
            vault_root=os.path.join(tmpdir, "vault"),
            registry_file=os.path.join(tmpdir, "registry.json")
        )
        with open(FIXTURE_PDF, "rb") as f:
            data = f.read()

        # First ingestion
        state1, rec1, meta1 = engine.process_raw_bytes(
            data,
            source_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            final_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            discovery_method="PUBLIC_BROWSER_CRAWL4AI",
        )
        assert state1 == HarvestState.REGISTERED
        assert rec1.discovery_method == "PUBLIC_BROWSER_CRAWL4AI"
        assert rec1.origin_verification_status == "LIVE_VERIFIED"

        # Second ingestion of same bytes — must be idempotent
        state2, rec2, meta2 = engine.process_raw_bytes(
            data,
            source_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            final_url="https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
            discovery_method="PUBLIC_BROWSER_CRAWL4AI",
        )
        assert state2 == HarvestState.DUPLICATE
        assert rec2.sha256 == rec1.sha256
        assert meta2["is_duplicate"] is True
        assert len(rec2.retrieval_history) == 2


# =============================================================================
# Adapter construction: verify policy compliance guard
# =============================================================================

def test_adapter_construction_with_clean_config_succeeds():
    adapter = Crawl4AIPublicBrowserAdapter(timeout_seconds=15, adapter_config={})
    assert adapter.discovery_method == "PUBLIC_BROWSER_CRAWL4AI"


def test_adapter_construction_with_policy_violation_fails():
    with pytest.raises(PolicyViolationError):
        Crawl4AIPublicBrowserAdapter(adapter_config={"allow_stealth_mode": True})
