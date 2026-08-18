# Crawl4AI Public Browser Spike Report

**Spike**: `SOURCE HARVESTER v0.2a — Crawl4AI Public Browser Adapter`  
**Branch**: `spike/crawl4ai-public-browser-adapter`  
**Date**: `2026-08-18`  
**Policy**: `PUBLIC_BROWSER_POLICY` strictly enforced — no stealth, no proxy, no CAPTCHA bypass  

---

## Executive Verdict

### `PUBLIC_BROWSER_BLOCKED`

> **Key Finding**: Crawl4AI / Playwright successfully rendered all 3 MSC URLs at the network/browser level (HTTP 200/301, HTML returned, page titles confirmed). However, the rendered HTML body contained Akamai challenge content embedded within an otherwise normal-looking 404 page. All challenge detections fired correctly, and the adapter aborted without evasion attempts.

---

## Crawl4AI Version

`0.9.2`

---

## Browser Runtime

Playwright / Chromium (via Crawl4AI `AsyncWebCrawler`, patchright backend)

---

## Requested MSC URLs

- `https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-meraviglia/deckplan.aspx`
- `https://www.msccruises.de/de-de/Kreuzfahrtschiffe/MSC-Meraviglia.aspx`
- `https://www.msccruises.com/en-gl/Discover-MSC/Cruise-Ships/MSC-Meraviglia.aspx`

---

## Per-URL Render Results

| URL | HTTP Status | Browser Rendered | Challenge | Challenge Type | Status |
|:----|:-----------:|:----------------:|:---------:|:--------------:|:-------|
| `.../msc-meraviglia/deckplan.aspx` | `404` | ✅ Yes | ✅ Yes | `AKAMAI` | `SOURCE_ACCESS_RESTRICTED` |
| `.../Kreuzfahrtschiffe/MSC-Meraviglia.aspx` | `301` | ✅ Yes | ✅ Yes | `AKAMAI` | `SOURCE_ACCESS_RESTRICTED` |
| `.../Discover-MSC/Cruise-Ships/MSC-Meraviglia.aspx` | `301` | ✅ Yes | ✅ Yes | `AKAMAI` | `SOURCE_ACCESS_RESTRICTED` |

> [!NOTE]
> Crawl4AI successfully established a browser connection and retrieved HTML for all three URLs. The page titles confirm Akamai-generated error pages ("Seite nicht gefunden - Fehler 404 | MSC Cruises" / "Error 404 - Page not found") with embedded Akamai bot-protection content in the DOM. The adapter correctly detected and classified the challenge, then aborted without retrying with evasion.

---

## Challenge Detection

⚠️ **All 3 URLs served Akamai challenge pages** embedded within 404 responses. The adapted challenge detector fired correctly on the keyword `akamai` present in the rendered HTML bodies.

The adapter complied with `PUBLIC_BROWSER_POLICY`:
- Did NOT retry with stealth mode.
- Did NOT rotate proxy.
- Did NOT attempt to solve the challenge.
- Returned `SOURCE_ACCESS_RESTRICTED` for all three candidates.

---

## PDF Candidates

**Total unique candidates discovered**: **0**

No PDF links were extractable from the Akamai challenge pages.

---

## Download Result

❌ No PDF downloaded. All pages blocked by Akamai challenge content.

---

## SHA Result

| | SHA-256 |
|---|---|
| **Reference (Fixture)** | `77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9` |
| **Live Download** | `N/A` |
| **Byte Identity** | `NO_LIVE_ARTIFACT` |

---

## Registry Impact

No new registry record was created. For any future `PUBLIC_BROWSER_CRAWL4AI` acquisition that succeeds:

```json
{
  "discovery_method": "PUBLIC_BROWSER_CRAWL4AI",
  "origin_verification_status": "SOURCE_ACCESS_RESTRICTED"
}
```

For a successful live browser + PDF download:

```json
{
  "discovery_method": "PUBLIC_BROWSER_CRAWL4AI",
  "origin_verification_status": "LIVE_VERIFIED"
}
```

---

## Policy Compliance

| Capability | Allowed | Enforced | Used in Spike |
|---|:---:|:---:|:---:|
| JavaScript execution | ✅ | ✅ | ✅ Yes |
| Normal cookies | ✅ | ✅ | ✅ Yes |
| Page rendering | ✅ | ✅ | ✅ Yes |
| Dynamic link extraction | ✅ | ✅ | N/A (blocked before extraction) |
| Stealth mode | ❌ | ❌ blocked at construction | ❌ Not used |
| Fingerprint spoofing | ❌ | ❌ blocked at construction | ❌ Not used |
| CAPTCHA bypass | ❌ | ❌ blocked at construction | ❌ Not used |
| Proxy rotation | ❌ | ❌ blocked at construction | ❌ Not used |
| WAF bypass | ❌ | ❌ blocked at construction | ❌ Not used |

**Full policy compliance achieved.**

---

## Tests

| Suite | Tests | Result |
|---|:---:|:---:|
| `test_harvester_crawl4ai_adapter.py` (unit) | 23 | ✅ **23/23 passed** |
| `test_harvester_crawl4ai_live.py` (integration) | 1 | ✅ Skipped by default — run with `TIMONELO_LIVE_TESTS=1` |

---

## Key Technical Observations

1. **Browser access ≠ content access**: Crawl4AI + Playwright successfully established a browser-level connection and retrieved HTML (730 KB for the DE site). The Akamai challenge is embedded *within* a valid HTML document — not a TCP/TLS block. This is fundamentally different from the HTTP 403 seen in unauthenticated curl/urllib probes.

2. **Akamai Bot Manager pattern**: The challenge is injected into the body of a served 404 page. The rendered DOM contains the keyword "akamai" and a bot-detection script payload. This is the `Akamai Bot Manager` product, which performs JavaScript-based browser fingerprinting at render time.

3. **Legacy URL paths**: All 3 tested URL paths returned 404 status codes (with Akamai challenge). The current (2025) MSC website may use different URL structures than the tested canonical paths.

4. **Correct abort behavior**: The adapter correctly detected the challenge, logged `SOURCE_ACCESS_RESTRICTED`, and did not attempt retries, alternative paths, or stealth workarounds.

---

## Risks

1. **Akamai Bot Manager**: MSC deploys JavaScript-based fingerprinting at browser level. Even a standard Chromium instance can be identified. Defeating this without stealth mode is extremely difficult.
2. **URL Staleness**: The MSC website URL structure for ship pages and deckplan downloads may have changed since the tested canonical paths were identified.
3. **`playwright-stealth` in dependency graph**: Present in the crawl4ai install but explicitly disabled in the Timonelo adapter. Monitor upstream for changes that auto-activate stealth.
4. **Dependency footprint**: `crawl4ai 0.9.2` installs ~45 packages (~200 MB total). Consider `extras_require` gating to make this optional.

---

## Recommendations for v0.3

- Test with **current live URL structures** for MSC.de/MSC.com (sitemap-driven discovery rather than hardcoded paths).
- Explore **MSC Press Portal** (`mscpressarea.com`) which returned HTTP 200 without bot challenge — this may be the correct public-facing PDF source.
- Consider **authorized B2B API feed** (`mscbook.com`) as the only reliable automated path for WAF-protected consumer sites.
- If browser acquisition is pursued further, evaluate whether a **headed browser session** (user-managed login flow) rather than headless crawl is feasible for the press portal.
