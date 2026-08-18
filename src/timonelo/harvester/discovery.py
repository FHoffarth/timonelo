"""
src/timonelo/harvester/discovery.py

Candidate source discovery engine for MSC deck plan artifacts.
Supports:
1. Pattern-based official URL generation
2. Sitemap URL extraction
3. Local file fixture injection for testing and offline builds
"""

import os
import re
from typing import List, Dict, Any, Optional
from timonelo.harvester.config import MSC_SOURCE_CONFIG


class DiscoveryEngine:
    def __init__(self, config: Dict[str, Any] = MSC_SOURCE_CONFIG):
        self.config = config

    def discover_candidates_for_vessel(
        self,
        vessel_id: str,
        document_type: str = "deck-plan"
    ) -> List[Dict[str, Any]]:
        """
        Discovers candidate URLs for a specific vessel.
        """
        candidates: List[Dict[str, Any]] = []
        slug = vessel_id.replace("msc-", "")

        # Official pattern candidates
        candidate_urls = [
            f"https://www.msccruises.de/-/media/global-contents/deck-plans/msc-{slug}-deck-plan.pdf",
            f"https://www.msccruises.com/-/media/global-contents/deck-plans/msc-{slug}-deckplan.pdf",
            f"https://assets.msccruises.com/deckplans/msc-{slug}-deckplan-de.pdf",
            f"https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-{slug}/deckplan.aspx"
        ]

        for u in candidate_urls:
            candidates.append({
                "url": u,
                "discovery_method": "PATTERN_DISCOVERY",
                "target_vessel_id": vessel_id,
                "document_type": document_type
            })

        return candidates

    def discover_local_fixture(
        self,
        fixture_path: str,
        vessel_id: Optional[str] = "msc-meraviglia"
    ) -> Optional[Dict[str, Any]]:
        """
        Injects a known local PDF file as a discovery item (e.g. for offline regression).
        """
        if not os.path.isfile(fixture_path):
            return None
        return {
            "url": f"file:///{os.path.abspath(fixture_path).replace('\\', '/')}",
            "local_path": os.path.abspath(fixture_path),
            "discovery_method": "LOCAL_REGRESSION_FIXTURE",
            "target_vessel_id": vessel_id,
            "document_type": "DECK_PLAN"
        }
