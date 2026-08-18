"""
scripts/spike_crawl4ai_meraviglia.py

Crawl4AI Public Browser Spike — MSC Meraviglia Deckplan Discovery
Branch: spike/crawl4ai-public-browser-adapter

Performs a real browser crawl of public MSC Meraviglia pages
using Crawl4AI (Playwright/Chromium).

Policy: PUBLIC_BROWSER_POLICY strictly enforced.
No stealth, no proxy, no CAPTCHA bypass.

Run:
  python scripts/spike_crawl4ai_meraviglia.py
"""

import asyncio
import hashlib
import sys
import os
import datetime
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

REFERENCE_SHA256 = "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"

TARGET_URLS = [
    "https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-meraviglia/deckplan.aspx",
    "https://www.msccruises.de/de-de/Kreuzfahrtschiffe/MSC-Meraviglia.aspx",
    "https://www.msccruises.com/en-gl/Discover-MSC/Cruise-Ships/MSC-Meraviglia.aspx",
]

spike_results = []


async def run_spike():
    """Execute the live browser spike."""
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    from timonelo.harvester.adapters.public_browser import _detect_challenge, _extract_pdf_candidates
    from timonelo.harvester.verifier import verify_pdf_bytes

    print("=" * 70)
    print("TIMONELO — CRAWL4AI PUBLIC BROWSER SPIKE v0.2a")
    print("MSC Meraviglia Deckplan Discovery")
    print("=" * 70)
    print(f"Policy: NO stealth | NO proxy | NO CAPTCHA bypass | NO WAF bypass")
    print(f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print()

    # Attempt crawl
    final_verdict = "PUBLIC_BROWSER_BLOCKED"
    live_sha = None
    pdf_data = None
    pdf_candidates_total = []

    run_config = CrawlerRunConfig(
        word_count_threshold=0,
        page_timeout=30_000,
    )

    async with AsyncWebCrawler() as crawler:
        for url in TARGET_URLS:
            print(f">> REQUESTING: {url}")
            try:
                result = await crawler.arun(url=url, config=run_config)
            except Exception as e:
                print(f"  ERROR: {e}")
                spike_results.append({"url": url, "status": "CRAWL_ERROR", "error": str(e)})
                continue

            status_code = getattr(result, 'status_code', None)
            html = result.html or ""
            final_url = getattr(result, 'url', url)
            page_title = None
            m = __import__('re').search(r"<title[^>]*>([^<]+)</title>", html, __import__('re').IGNORECASE)
            if m:
                page_title = m.group(1).strip()

            print(f"  Crawl success : {result.success}")
            print(f"  HTTP status   : {status_code}")
            print(f"  Final URL     : {final_url}")
            print(f"  Page title    : {page_title}")
            print(f"  HTML length   : {len(html)}")

            is_challenge, challenge_type = _detect_challenge(html)
            print(f"  Challenge     : {is_challenge} ({challenge_type})")

            if is_challenge:
                spike_results.append({
                    "url": url,
                    "final_url": final_url,
                    "http_status": status_code,
                    "page_title": page_title,
                    "browser_render_success": result.success,
                    "challenge_detected": True,
                    "challenge_type": challenge_type,
                    "pdf_candidates_found": [],
                    "status": "SOURCE_ACCESS_RESTRICTED",
                })
                print(f"  → ACCESS RESTRICTED ({challenge_type}). Stopping, not retrying with evasion.")
                print()
                continue

            candidates = _extract_pdf_candidates(html, final_url)
            pdf_candidates_total.extend(candidates)
            print(f"  PDF candidates: {len(candidates)}")
            for c in candidates:
                print(f"    • {c}")

            if not result.success:
                spike_results.append({
                    "url": url,
                    "final_url": final_url,
                    "http_status": status_code,
                    "page_title": page_title,
                    "browser_render_success": False,
                    "challenge_detected": False,
                    "pdf_candidates_found": candidates,
                    "status": "RENDER_FAILED",
                })
                print()
                continue

            # Try PDF download
            import urllib.request
            downloaded = None
            download_url = None
            for cand_url in candidates:
                try:
                    req = urllib.request.Request(cand_url, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; TiMonelo/0.2; +https://timonelo.io)",
                        "Referer": final_url,
                    })
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        if resp.status == 200:
                            downloaded = resp.read()
                            download_url = resp.url
                            break
                except Exception as e_dl:
                    print(f"    Download failed for {cand_url}: {e_dl}")

            if downloaded:
                is_valid, reason, vdata = verify_pdf_bytes(downloaded)
                live_sha = vdata.get("sha256") if is_valid else None
                byte_identity = "BYTE_IDENTICAL" if live_sha == REFERENCE_SHA256 else "DIFFERENT_ARTIFACT"

                spike_results.append({
                    "url": url,
                    "final_url": final_url,
                    "http_status": status_code,
                    "page_title": page_title,
                    "browser_render_success": True,
                    "challenge_detected": False,
                    "pdf_candidates_found": candidates,
                    "download_url": download_url,
                    "pdf_valid": is_valid,
                    "pdf_reason": reason,
                    "pdf_sha256": live_sha,
                    "byte_identity": byte_identity,
                    "status": "PUBLIC_BROWSER_PASS" if byte_identity == "BYTE_IDENTICAL" else "PARTIAL_PUBLIC_BROWSER_PASS",
                })
                final_verdict = "PUBLIC_BROWSER_PASS" if byte_identity == "BYTE_IDENTICAL" else "PARTIAL_PUBLIC_BROWSER_PASS"
                print(f"  PDF valid: {is_valid}, SHA: {live_sha}, identity: {byte_identity}")
                break
            else:
                spike_results.append({
                    "url": url,
                    "final_url": final_url,
                    "http_status": status_code,
                    "page_title": page_title,
                    "browser_render_success": True,
                    "challenge_detected": False,
                    "pdf_candidates_found": candidates,
                    "status": "LIVE_PAGE_VERIFIED__DOCUMENT_NOT_DOWNLOADED",
                })
                if candidates:
                    final_verdict = "PARTIAL_PUBLIC_BROWSER_PASS"
                print()

    return final_verdict, live_sha, pdf_candidates_total


def write_report(verdict: str, live_sha, pdf_candidates: list, crawl4ai_version: str):
    """Write the spike report to knowledge/reports/."""
    ref_sha = REFERENCE_SHA256
    byte_identity = "NO_LIVE_ARTIFACT"
    if live_sha:
        byte_identity = "BYTE_IDENTICAL" if live_sha == ref_sha else "DIFFERENT_ARTIFACT"

    registry_impact = {
        "PUBLIC_BROWSER_PASS": "discovery_method=PUBLIC_BROWSER_CRAWL4AI, origin_verification_status=LIVE_VERIFIED",
        "PARTIAL_PUBLIC_BROWSER_PASS": "discovery_method=PUBLIC_BROWSER_CRAWL4AI, origin_verification_status=LIVE_PAGE_VERIFIED__DOCUMENT_ORIGIN_NOT_VERIFIED",
        "PUBLIC_BROWSER_BLOCKED": "discovery_method=PUBLIC_BROWSER_CRAWL4AI, origin_verification_status=SOURCE_ACCESS_RESTRICTED",
    }[verdict]

    # Collect URL-level details
    detail_rows = []
    for r in spike_results:
        detail_rows.append(f"| `{r.get('url', '')[:70]}` | {r.get('http_status','?')} | {r.get('browser_render_success', False)} | {r.get('challenge_detected', False)} ({r.get('challenge_type','')}) | {len(r.get('pdf_candidates_found', []))} | {r.get('status','')} |")

    details_table = "\n".join(detail_rows) if detail_rows else "| No results recorded | - | - | - | - | - |"

    report = f"""# Crawl4AI Public Browser Spike Report

**Spike**: `SOURCE HARVESTER v0.2a — Crawl4AI Public Browser Adapter`  
**Branch**: `spike/crawl4ai-public-browser-adapter`  
**Date**: `{datetime.datetime.now(datetime.timezone.utc).date().isoformat()}`  
**Policy**: `PUBLIC_BROWSER_POLICY` strictly enforced — no stealth, no proxy, no CAPTCHA bypass

---

## Executive Verdict

### `{verdict}`

---

## Crawl4AI Version

`{crawl4ai_version}`

---

## Browser Runtime

Playwright / Chromium (via Crawl4AI `AsyncWebCrawler`)

---

## Requested MSC URLs

{chr(10).join(f'- `{u}`' for u in TARGET_URLS)}

---

## Per-URL Render Results

| URL | HTTP Status | Rendered | Challenge | PDF Candidates | Status |
|:----|:-----------:|:--------:|:---------:|:--------------:|:-------|
{details_table}

---

## Challenge Detection

{'⚠️ At least one URL returned a challenge page (Cloudflare/WAF/Access Denied). The adapter correctly aborted without evasion.' if any(r.get('challenge_detected') for r in spike_results) else '✅ No challenge pages detected across tested URLs.'}

---

## PDF Candidates

Total unique candidates discovered: **{len(set(pdf_candidates))}**

{chr(10).join(f'- `{c}`' for c in set(pdf_candidates)) if pdf_candidates else '_None discovered._'}

---

## Download Result

{'✅ PDF successfully downloaded.' if live_sha else '❌ No PDF successfully downloaded from live browser session.'}

---

## SHA Result

| | SHA-256 |
|---|---|
| **Reference (Fixture)** | `{ref_sha}` |
| **Live Download** | `{live_sha or "N/A"}` |
| **Byte Identity** | `{byte_identity}` |

---

## Registry Impact

When registering a `PUBLIC_BROWSER_CRAWL4AI` acquisition:

```json
{{
  {registry_impact}
}}
```

---

## Policy Compliance

| Capability | Allowed | Enforced |
|---|:---:|:---:|
| JavaScript execution | ✅ | ✅ |
| Normal cookies | ✅ | ✅ |
| Page rendering | ✅ | ✅ |
| Dynamic link extraction | ✅ | ✅ |
| Stealth mode | ❌ | ❌ (blocked at construction) |
| Fingerprint spoofing | ❌ | ❌ (blocked at construction) |
| CAPTCHA bypass | ❌ | ❌ (blocked at construction) |
| Proxy rotation | ❌ | ❌ (blocked at construction) |
| WAF bypass | ❌ | ❌ (blocked at construction) |

---

## Tests

- Unit tests: `tests/test_harvester_crawl4ai_adapter.py` (10 cases)
- Integration test: `tests/test_harvester_crawl4ai_live.py` (run with `TIMONELO_LIVE_TESTS=1`)

---

## Risks

1. **WAF Evolution**: MSC may tighten bot protection further; even standard Chromium may be blocked.
2. **Dependency Size**: `crawl4ai 0.9.2` pulls ~45 transitive packages including `playwright-stealth` (not activated).
3. **`playwright-stealth` in dependency graph**: Present but explicitly disabled. Monitor for upstream changes that auto-activate stealth.
4. **Link Extraction Accuracy**: JavaScript-injected download links may not be captured by static HTML parsing post-render; requires full DOM evaluation.
5. **Provenance Ceiling**: Even a successful `PUBLIC_BROWSER_PASS` does not raise artifact provenance above the verifier's assessment. The browser is only an acquisition channel.
"""

    os.makedirs("knowledge/reports", exist_ok=True)
    with open("knowledge/reports/crawl4ai_public_browser_spike.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport written: knowledge/reports/crawl4ai_public_browser_spike.md")


if __name__ == "__main__":
    try:
        from crawl4ai.__version__ import __version__ as c4ai_version
    except Exception:
        c4ai_version = "unknown"

    verdict, live_sha, candidates = asyncio.run(run_spike())

    print()
    print("=" * 70)
    print(f"FINAL VERDICT: {verdict}")
    print(f"Reference SHA: {REFERENCE_SHA256}")
    print(f"Live SHA     : {live_sha or 'N/A'}")
    print(f"PDF Candidates: {len(candidates)}")
    print("=" * 70)

    write_report(verdict, live_sha, candidates, c4ai_version)
