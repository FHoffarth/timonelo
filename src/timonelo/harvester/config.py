"""
src/timonelo/harvester/config.py

Configuration for official source discovery and fetching.
Scope v0.1: MSC Cruises.
"""

from typing import Dict, Any, List

MSC_SOURCE_CONFIG: Dict[str, Any] = {
    "cruise_line_id": "msc",
    "publisher_name": "MSC Cruises",
    "allowed_domains": [
        "msccruises.de",
        "www.msccruises.de",
        "msccruises.com",
        "www.msccruises.com",
        "msccruises.co.uk",
        "www.msccruises.co.uk",
        "mscpressarea.com",
        "www.mscpressarea.com",
        "mscbook.com",
        "www.mscbook.com",
        "msccruises.fr",
        "msccruises.it",
        "msccruisesusa.com"
    ],
    "allowed_asset_domains": [
        "msc-media.azureedge.net",
        "assets.msccruises.com",
        "mscimages.msccruises.com",
        "cdn.msccruises.com",
        "mscmedia.msccruises.com"
    ],
    "third_party_hint_domains": [
        "cruisemapper.com",
        "cruisecritic.com",
        "cruisegid.ru",
        "seascanner.com"
    ],
    "known_seed_sitemaps": [
        "https://www.msccruises.de/sitemap.xml",
        "https://www.msccruises.com/sitemap.xml"
    ],
    "known_deckplan_path_patterns": [
        "/de-de/unsere-kreuzfahrtschiffe/{vessel_slug}/deckplan.aspx",
        "/en-gl/discover-msc/cruise-ships/{vessel_slug}/deck-plan.aspx",
        "/assets/deckplans/{vessel_slug}-deckplan.pdf"
    ],
    "respect_robots_txt": True,
    "max_concurrency": 2,
    "request_delay_seconds": 1.0,
    "user_agent": "TimoneloSourceHarvester/0.1 (+https://timonelo.com/bot; research@timonelo.com)"
}


def classify_domain_tier(domain: str) -> str:
    """Classifies a hostname into TIER_A, TIER_B, or TIER_C."""
    clean_domain = domain.lower().strip()
    if clean_domain.startswith("www."):
        clean_domain_no_www = clean_domain[4:]
    else:
        clean_domain_no_www = clean_domain

    if clean_domain in MSC_SOURCE_CONFIG["allowed_domains"] or clean_domain_no_www in MSC_SOURCE_CONFIG["allowed_domains"]:
        return "TIER_A"
    
    for asset_d in MSC_SOURCE_CONFIG["allowed_asset_domains"]:
        if clean_domain == asset_d or clean_domain.endswith("." + asset_d):
            return "TIER_B"
            
    return "TIER_C"
