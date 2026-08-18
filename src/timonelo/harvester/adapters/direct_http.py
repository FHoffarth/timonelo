"""
src/timonelo/harvester/adapters/direct_http.py

DirectHttpAdapter — wraps the existing synchronous fetcher as an AcquisitionAdapter.
Acquisition method: DIRECT_HTTP
"""

from timonelo.harvester.adapters.base import AcquisitionAdapter, AcquisitionResult
from timonelo.harvester.fetcher import ArtifactFetcher


class DirectHttpAdapter(AcquisitionAdapter):
    """
    Acquires artifacts via direct unauthenticated HTTP GET.
    This is the original v0.1 strategy: simple, fast, no browser.
    Returns DIRECT_HTTP as discovery method.
    """

    def __init__(self, config: dict):
        self._fetcher = ArtifactFetcher(config=config)

    @property
    def discovery_method(self) -> str:
        return "DIRECT_HTTP"

    def acquire(self, candidate: dict) -> AcquisitionResult:
        url = candidate.get("url", "")
        success, status, final_url, data, err = self._fetcher.fetch_url(url)

        if not success:
            challenge = err in ("ROBOTS_BLOCKED", "FORBIDDEN")
            return AcquisitionResult(
                success=False,
                requested_url=url,
                final_url=final_url or url,
                http_status=status,
                discovery_method=self.discovery_method,
                challenge_detected=challenge,
                challenge_type="WAF_OR_ROBOTS" if challenge else None,
                error=err,
            )

        return AcquisitionResult(
            success=True,
            data=data,
            requested_url=url,
            final_url=final_url,
            http_status=status,
            discovery_method=self.discovery_method,
        )
