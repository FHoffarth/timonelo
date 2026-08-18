"""
src/timonelo/harvester/adapters/public_browser_policy.py

Explicit runtime policy for PUBLIC_BROWSER_CRAWL4AI acquisition adapter.

This policy is immutable at runtime and must be respected by all
browser-based acquisition code in Timonelo.

PRINCIPLE: Browser rendering may improve acquisition.
           It must never weaken provenance.
"""

PUBLIC_BROWSER_POLICY: dict = {
    # ---------------------------------------------------------------
    # PERMITTED capabilities
    # ---------------------------------------------------------------
    # Execute JavaScript (required to render dynamic MSC pages)
    "allow_javascript": True,

    # Send normal browser cookies (session cookies from normal navigation)
    "allow_normal_cookies": True,

    # Render the full page DOM including JS-injected content
    "allow_page_rendering": True,

    # Extract links that are only present after JS execution
    "allow_dynamic_link_extraction": True,

    # Follow a clearly visible "Download" link via a browser click
    "allow_download_clicks": True,

    # ---------------------------------------------------------------
    # PROHIBITED capabilities — MUST NEVER BE ENABLED
    # ---------------------------------------------------------------
    # Playwright-stealth or equivalent bot fingerprint masking
    "allow_stealth_mode": False,

    # Changing browser fingerprints (User-Agent spoofing, canvas spoofing, etc.)
    "allow_fingerprint_spoofing": False,

    # Any automatic or semi-automatic CAPTCHA solving
    "allow_captcha_bypass": False,

    # Rotating residential or datacenter proxies
    "allow_proxy_rotation": False,

    # Any technique explicitly designed to circumvent WAF / rate-limiting
    "allow_waf_bypass": False,
}


def assert_policy_compliance(adapter_config: dict) -> None:
    """
    Raise an error if an adapter configuration violates PUBLIC_BROWSER_POLICY.
    Called at adapter construction time.
    """
    forbidden = [k for k, v in PUBLIC_BROWSER_POLICY.items() if not v]
    for key in forbidden:
        if adapter_config.get(key, False):
            raise PolicyViolationError(
                f"PUBLIC_BROWSER_POLICY violation: '{key}' is explicitly prohibited. "
                f"Timonelo does not permit {key.replace('allow_', '').replace('_', ' ')}."
            )


class PolicyViolationError(Exception):
    """Raised when an adapter configuration violates PUBLIC_BROWSER_POLICY."""
    pass
