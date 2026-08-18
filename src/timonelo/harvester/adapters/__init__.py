"""
src/timonelo/harvester/adapters/__init__.py
"""
from timonelo.harvester.adapters.base import AcquisitionAdapter, AcquisitionResult
from timonelo.harvester.adapters.direct_http import DirectHttpAdapter
from timonelo.harvester.adapters.public_browser import Crawl4AIPublicBrowserAdapter
from timonelo.harvester.adapters.public_browser_policy import PUBLIC_BROWSER_POLICY

__all__ = [
    "AcquisitionAdapter",
    "AcquisitionResult",
    "DirectHttpAdapter",
    "Crawl4AIPublicBrowserAdapter",
    "PUBLIC_BROWSER_POLICY",
]
