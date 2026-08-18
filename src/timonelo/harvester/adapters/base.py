"""
src/timonelo/harvester/adapters/base.py

Abstract base class for all acquisition adapters.

An AcquisitionAdapter is responsible for one thing only:
  Given a candidate URL, acquire the raw bytes of the artifact (if possible).

It does NOT:
  - Verify PDF validity
  - Compute SHA-256
  - Store in vault
  - Update registry
  - Extract knowledge

All downstream pipeline steps remain unchanged regardless of which adapter is used.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AcquisitionResult:
    """
    The outcome of an acquisition attempt.

    success=True means raw bytes are available.
    success=False means the adapter could not retrieve the resource
    (404, 403, WAF challenge, network error, etc.).
    """
    # Whether raw bytes were successfully acquired
    success: bool

    # The raw bytes of the artifact (only set when success=True)
    data: Optional[bytes] = None

    # The source URL that was requested
    requested_url: str = ""

    # The final URL after any redirects
    final_url: str = ""

    # HTTP status code received (None for browser-only flows)
    http_status: Optional[int] = None

    # Which acquisition method was used
    discovery_method: str = "DIRECT_HTTP"

    # If a challenge page was detected (Cloudflare, CAPTCHA, Akamai, etc.)
    challenge_detected: bool = False
    challenge_type: Optional[str] = None  # e.g. "CLOUDFLARE", "CAPTCHA", "AKAMAI"

    # If page was rendered (browser adapters only)
    page_rendered: bool = False
    page_title: Optional[str] = None

    # PDF candidate links discovered from the page (browser adapters only)
    pdf_candidates: list = field(default_factory=list)

    # Any error message
    error: Optional[str] = None


class AcquisitionAdapter(ABC):
    """
    Abstract base for all acquisition adapters.
    Subclasses implement `acquire()` for a specific acquisition strategy.
    """

    @abstractmethod
    def acquire(self, candidate: dict) -> AcquisitionResult:
        """
        Attempt to acquire the artifact described by `candidate`.

        Args:
            candidate: dict with at minimum:
                - url: str  (the target URL)
                - target_vessel_id: Optional[str]

        Returns:
            AcquisitionResult
        """
        ...

    @property
    @abstractmethod
    def discovery_method(self) -> str:
        """Returns the string identifier for this adapter's discovery method."""
        ...
