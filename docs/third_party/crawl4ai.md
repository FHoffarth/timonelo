# Crawl4AI — Third-Party Dependency Notice

## Package Information

| Field | Value |
|---|---|
| **Package** | `crawl4ai` |
| **PyPI** | https://pypi.org/project/crawl4ai/ |
| **GitHub** | https://github.com/unclecode/crawl4ai |
| **Author** | Unclecode (Hossein Tohidi) |
| **License** | Apache License 2.0 |
| **Reviewed Version** | `0.9.2` (as installed for this spike) |
| **Python Compatibility** | Python 3.9+ (tested on 3.14 in Timonelo) |

---

## Usage Scope within Timonelo

Crawl4AI is used **exclusively** as an optional `PUBLIC_BROWSER_CRAWL4AI` acquisition adapter within the Official Source Harvester pipeline. It is:

- **NOT** used for knowledge extraction.
- **NOT** used for evidence generation.
- **NOT** used to replace the verifier, vault, registry, vessel resolver, classifier, or Evidence Gatekeeper.
- **ONLY** used to render public web pages in a normal browser context for the purpose of discovering publicly accessible document download links (PDF candidates).

Usage is strictly gated by `PUBLIC_BROWSER_POLICY` (see `src/timonelo/harvester/adapters/public_browser_policy.py`).

---

## Dependencies Pulled by crawl4ai

`crawl4ai` carries a large dependency graph, including:

| Package | Purpose |
|---|---|
| `playwright` / `patchright` | Browser automation (Chromium, Firefox, WebKit) |
| `playwright-stealth` | **Important: see Security Considerations below** |
| `beautifulsoup4`, `lxml` | HTML parsing |
| `unclecode-litellm` | LLM integration (not used in Timonelo) |
| `openai` | AI SDK (not used in Timonelo) |
| `numpy`, `scipy`, `shapely` | Data processing |
| `nltk`, `tokenizers` | NLP (not used in Timonelo) |
| `fake-useragent` | **Important: see Security Considerations below** |

---

## License

Apache License 2.0.

Full text: https://github.com/unclecode/crawl4ai/blob/main/LICENSE

No attribution requirement beyond standard Apache 2.0 NOTICE compliance (no explicit NOTICE file in crawl4ai as of 0.9.2).

---

## Security Considerations

> [!WARNING]
> `crawl4ai` pulls `playwright-stealth` and `fake-useragent` as transitive dependencies. These packages can be used to disguise automated browser traffic.
>
> **Timonelo explicitly prohibits use of these capabilities via `PUBLIC_BROWSER_POLICY`.**
> - `allow_stealth_mode: False`
> - `allow_fingerprint_spoofing: False`
> - `allow_proxy_rotation: False`
> - `allow_waf_bypass: False`
>
> The `Crawl4AIPublicBrowserAdapter` does **not** activate any stealth, proxy rotation, or fingerprint spoofing features. This is enforced at the adapter level. Any future modification enabling stealth features requires explicit policy change and architecture review.

---

## Attribution Requirement

Apache 2.0 — standard attribution. Inclusion in dependency list and this document satisfies requirements.

---

## Update Policy

Before updating beyond `0.9.x`, re-audit:
1. Whether `playwright-stealth` integration has been deepened in the new version.
2. Whether any automatic stealth or anti-bot bypass became a default behavior.
3. Python version compatibility.
