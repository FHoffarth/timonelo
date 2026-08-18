"""
src/timonelo/harvester/adapters/public_browser.py

Crawl4AIPublicBrowserAdapter — PUBLIC_BROWSER_CRAWL4AI acquisition adapter.

Uses Crawl4AI (backed by Playwright/Chromium) to render public web pages,
extract PDF candidate links, and download referenced documents.

POLICY: PUBLIC_BROWSER_POLICY is enforced at construction time.
        No stealth, no proxy rotation, no CAPTCHA bypass, no WAF circumvention.

IMPORTANT PROVENANCE RULE:
  - A rendered page alone proves LIVE_PAGE_VERIFIED, not DOCUMENT_ORIGIN_VERIFIED.
  - Only a successful PDF download with valid magic bytes + official origin chain
    yields LIVE_VERIFIED for the artifact.
  - Crawl4AI markdown/text output is NEVER used as evidence. Only the raw PDF bytes.

CHALLENGE DETECTION:
  If the rendered page content matches known challenge patterns
  (Cloudflare, CAPTCHA, Akamai, Access Denied), the adapter returns
  challenge_detected=True and does not attempt further processing.
"""

from __future__ import annotations

import asyncio
import re
import urllib.parse
from typing import List, Optional
import urllib.request

from timonelo.harvester.adapters.base import AcquisitionAdapter, AcquisitionResult
from timonelo.harvester.adapters.public_browser_policy import (
    PUBLIC_BROWSER_POLICY,
    assert_policy_compliance,
)


# ---------------------------------------------------------------------------
# Challenge page detection patterns
# ---------------------------------------------------------------------------
CHALLENGE_PATTERNS: list[tuple[str, str]] = [
    (r"cloudflare", "CLOUDFLARE"),
    (r"just a moment", "CLOUDFLARE"),
    (r"cf-browser-verification", "CLOUDFLARE"),
    (r"under attack mode", "CLOUDFLARE"),
    (r"access denied", "ACCESS_DENIED"),
    (r"403 forbidden", "HTTP_FORBIDDEN"),
    (r"akamai", "AKAMAI"),
    (r"bot detection", "BOT_DETECTION"),
    (r"captcha", "CAPTCHA"),
    (r"please verify you are a human", "CAPTCHA"),
    (r"enable cookies", "COOKIE_CHALLENGE"),
    (r"security check", "SECURITY_CHECK"),
    (r"ddos protection", "DDOS_PROTECTION"),
]

# PDF link detection patterns
PDF_LINK_PATTERNS = [
    r'\.pdf(\?[^"\']*)?',
    r'deckplan',
    r'deck.?plan',
    r'deckpl[äa]ne',
]


def _detect_challenge(html: str) -> tuple[bool, Optional[str]]:
    """Returns (is_challenge, challenge_type) from rendered HTML."""
    lower = html.lower()
    for pattern, kind in CHALLENGE_PATTERNS:
        if re.search(pattern, lower):
            return True, kind
    return False, None


def _extract_pdf_candidates(html: str, base_url: str) -> list[str]:
    """
    Extract PDF/deck-plan candidate URLs from rendered HTML.
    Only returns absolute URLs or absolute-path-resolved URLs.
    """
    candidates: list[str] = []

    # href and src attributes
    for attr_match in re.finditer(r'(?:href|src|data-href|action)=["\']([^"\']+)["\']', html, re.IGNORECASE):
        url_part = attr_match.group(1)
        # Check if it looks like a PDF or deckplan
        for pattern in PDF_LINK_PATTERNS:
            if re.search(pattern, url_part, re.IGNORECASE):
                abs_url = urllib.parse.urljoin(base_url, url_part)
                if abs_url not in candidates:
                    candidates.append(abs_url)
                break

    # data-url and similar attributes
    for attr_match in re.finditer(r'data-(?:url|link|href|download)=["\']([^"\']+)["\']', html, re.IGNORECASE):
        url_part = attr_match.group(1)
        for pattern in PDF_LINK_PATTERNS:
            if re.search(pattern, url_part, re.IGNORECASE):
                abs_url = urllib.parse.urljoin(base_url, url_part)
                if abs_url not in candidates:
                    candidates.append(abs_url)
                break

    return candidates


class Crawl4AIPublicBrowserAdapter(AcquisitionAdapter):
    """
    Acquisition adapter using Crawl4AI for public browser rendering.

    Workflow:
      1. Render page with normal browser (Chromium via Crawl4AI / Playwright)
      2. Detect challenge pages → abort if found
      3. Extract PDF candidate links
      4. For each candidate: attempt direct HTTP download (not through browser download)
      5. Return first successfully acquired PDF bytes

    POLICY: PUBLIC_BROWSER_POLICY is enforced. No stealth, no proxy, no CAPTCHA bypass.
    """

    # Adapter config keys that might violate policy
    _PROHIBITED_KEYS = [
        "allow_stealth_mode",
        "allow_fingerprint_spoofing",
        "allow_captcha_bypass",
        "allow_proxy_rotation",
        "allow_waf_bypass",
    ]

    def __init__(self, timeout_seconds: int = 30, adapter_config: Optional[dict] = None):
        # Enforce policy on any caller-supplied config
        cfg = adapter_config or {}
        assert_policy_compliance(cfg)
        self._timeout = timeout_seconds

    @property
    def discovery_method(self) -> str:
        return "PUBLIC_BROWSER_CRAWL4AI"

    def acquire(self, candidate: dict) -> AcquisitionResult:
        """Synchronous entry point — runs the async crawl in a fresh event loop."""
        url = candidate.get("url", "")
        try:
            return asyncio.run(self._async_acquire(url))
        except Exception as exc:
            return AcquisitionResult(
                success=False,
                requested_url=url,
                final_url=url,
                discovery_method=self.discovery_method,
                error=f"BROWSER_ERROR: {exc}",
            )

    async def _async_acquire(self, url: str) -> AcquisitionResult:
        """
        Core async acquisition logic.
        Attempts to import crawl4ai; if not available, returns a clean error.
        """
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        except ImportError:
            return AcquisitionResult(
                success=False,
                requested_url=url,
                final_url=url,
                discovery_method=self.discovery_method,
                error="CRAWL4AI_NOT_INSTALLED: pip install crawl4ai",
            )

        # Build minimal config — NO stealth, NO proxy
        run_config = CrawlerRunConfig(
            # No magic_pdf, no screenshot needed for link extraction
            word_count_threshold=0,
            # Standard timeout
            page_timeout=self._timeout * 1000,
        )

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            return AcquisitionResult(
                success=False,
                requested_url=url,
                final_url=getattr(result, "url", url),
                discovery_method=self.discovery_method,
                page_rendered=False,
                error=f"CRAWL4AI_FAILED: {getattr(result, 'error_message', 'unknown')}",
            )

        # We have rendered HTML
        html = result.html or ""
        page_title = self._extract_title(html)
        final_url = getattr(result, "url", url)

        # Challenge detection
        is_challenge, challenge_type = _detect_challenge(html)
        if is_challenge:
            return AcquisitionResult(
                success=False,
                requested_url=url,
                final_url=final_url,
                discovery_method=self.discovery_method,
                page_rendered=True,
                page_title=page_title,
                challenge_detected=True,
                challenge_type=challenge_type,
                error=f"SOURCE_ACCESS_RESTRICTED: {challenge_type}",
            )

        # Extract PDF candidates from rendered DOM
        pdf_candidates = _extract_pdf_candidates(html, final_url)

        # Attempt download of first candidate using plain HTTP (not browser download)
        downloaded_data: Optional[bytes] = None
        download_final_url: str = ""
        download_http_status: Optional[int] = None

        for candidate_url in pdf_candidates:
            try:
                req = urllib.request.Request(candidate_url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; TiMonelo Source Harvester/0.2; +https://timonelo.io/harvester)",
                    "Referer": final_url,
                })
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    download_http_status = resp.status
                    if download_http_status == 200:
                        downloaded_data = resp.read()
                        download_final_url = resp.url
                        break
            except Exception:
                continue

        if downloaded_data:
            return AcquisitionResult(
                success=True,
                data=downloaded_data,
                requested_url=url,
                final_url=download_final_url,
                http_status=download_http_status,
                discovery_method=self.discovery_method,
                page_rendered=True,
                page_title=page_title,
                challenge_detected=False,
                pdf_candidates=pdf_candidates,
            )

        # Page rendered, no PDF downloaded
        return AcquisitionResult(
            success=False,
            requested_url=url,
            final_url=final_url,
            discovery_method=self.discovery_method,
            page_rendered=True,
            page_title=page_title,
            challenge_detected=False,
            pdf_candidates=pdf_candidates,
            error="LIVE_PAGE_VERIFIED__DOCUMENT_ORIGIN_NOT_VERIFIED" if pdf_candidates else "LIVE_PAGE_VERIFIED__NO_PDF_CANDIDATES_FOUND",
        )

    @staticmethod
    def _extract_title(html: str) -> Optional[str]:
        """Extract <title> from HTML."""
        m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        return m.group(1).strip() if m else None
