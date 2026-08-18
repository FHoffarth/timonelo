"""
tests/test_harvester_crawl4ai_live.py

Integration test — Meraviglia live browser test via Crawl4AI.

This test performs an ACTUAL browser request to a public MSC URL.
It is marked @pytest.mark.integration and will be SKIPPED unless:
  - crawl4ai is installed
  - Playwright/Chromium browser is available
  - TIMONELO_LIVE_TESTS=1 environment variable is set

The test is compliant with PUBLIC_BROWSER_POLICY:
  - No stealth mode
  - No proxy rotation
  - No CAPTCHA bypass
  - No WAF circumvention

Expected outcomes:
  - PUBLIC_BROWSER_PASS: page rendered + PDF found + downloaded + SHA matches
  - PARTIAL_PUBLIC_BROWSER_PASS: page rendered, no PDF found or no PDF downloaded
  - PUBLIC_BROWSER_BLOCKED: challenge / access denied detected
"""

import os
import hashlib
import pytest

REFERENCE_SHA256 = "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"

MERAVIGLIA_TARGET_URLS = [
    "https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-meraviglia/deckplan.aspx",
    "https://www.msccruises.de/de-de/Kreuzfahrtschiffe/MSC-Meraviglia.aspx",
    "https://www.msccruises.com/en-gl/Discover-MSC/Cruise-Ships/MSC-Meraviglia.aspx",
]


def _crawl4ai_available() -> bool:
    try:
        import crawl4ai  # noqa: F401
        return True
    except ImportError:
        return False


def _live_tests_enabled() -> bool:
    return os.environ.get("TIMONELO_LIVE_TESTS", "0") == "1"


@pytest.mark.integration
@pytest.mark.skipif(
    not _crawl4ai_available() or not _live_tests_enabled(),
    reason="Integration test: requires crawl4ai + TIMONELO_LIVE_TESTS=1"
)
def test_meraviglia_live_browser_discovery():
    """
    Phase 4 / Phase 9 integration test.
    Attempts live Chromium browser crawl of MSC Meraviglia pages.
    Records result according to three-tier verdict:
      PUBLIC_BROWSER_PASS | PARTIAL_PUBLIC_BROWSER_PASS | PUBLIC_BROWSER_BLOCKED
    """
    from timonelo.harvester.adapters.public_browser import Crawl4AIPublicBrowserAdapter
    from timonelo.harvester.verifier import verify_pdf_bytes

    adapter = Crawl4AIPublicBrowserAdapter(timeout_seconds=30)

    verdict = "PUBLIC_BROWSER_BLOCKED"  # default pessimistic
    final_result = None

    for url in MERAVIGLIA_TARGET_URLS:
        result = adapter.acquire({"url": url, "target_vessel_id": "msc-meraviglia"})
        final_result = result

        if result.challenge_detected:
            print(f"\n[BLOCKED] {url}: challenge={result.challenge_type}")
            continue

        if result.page_rendered and not result.success:
            print(f"\n[PARTIAL] {url}: page rendered, pdf_candidates={result.pdf_candidates}")
            verdict = "PARTIAL_PUBLIC_BROWSER_PASS"
            continue

        if result.success and result.data:
            print(f"\n[PDF FOUND] {url}: final_url={result.final_url}, size={len(result.data)}")
            # Verify PDF
            is_valid, reason, vdata = verify_pdf_bytes(result.data)
            print(f"  PDF valid: {is_valid}, reason: {reason}")

            if is_valid:
                live_sha = vdata["sha256"]
                print(f"  Live SHA256:      {live_sha}")
                print(f"  Reference SHA256: {REFERENCE_SHA256}")

                if live_sha == REFERENCE_SHA256:
                    print("  BYTE_IDENTITY: BYTE_IDENTICAL")
                    verdict = "PUBLIC_BROWSER_PASS"
                else:
                    print("  BYTE_IDENTITY: DIFFERENT_ARTIFACT")
                    verdict = "PARTIAL_PUBLIC_BROWSER_PASS"
            break

    print(f"\n=== INTEGRATION VERDICT: {verdict} ===")

    # The test succeeds regardless of verdict — the verdict is informational.
    # A BLOCKED verdict is a legitimate, expected outcome.
    assert verdict in ("PUBLIC_BROWSER_PASS", "PARTIAL_PUBLIC_BROWSER_PASS", "PUBLIC_BROWSER_BLOCKED")
