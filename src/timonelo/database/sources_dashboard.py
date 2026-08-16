"""
Source Network Quality, Provenance Freshness, and Dependency Chain Dashboard Engine.
"""

from __future__ import annotations
from typing import Dict, Any, List
from collections import Counter


class SourcesDashboard:
    """Computes source quality ratings, access method shares, and dependency chains."""

    def __init__(self, db: Dict[str, Any]):
        self.db = db
        self.sources = db.get("sources", {})
        self.ships = db.get("ships", {})
        self.ports = db.get("ports", {})

    def generate_sources_report(self) -> Dict[str, Any]:
        total_sources = len(self.sources)
        category_counts = Counter()
        access_counts = Counter()
        freshness_buckets = {
            "Today (0 days)": 0,
            "Last Week (1-7 days)": 0,
            "Last Month (8-30 days)": 0,
            "Older (>30 days)": 0,
        }

        for sid, src in self.sources.items():
            cat = src.get("category", "OTHER")
            category_counts[cat] += 1

            method = src.get("access_method", "MANUAL")
            access_counts[method] += 1

            days = src.get("freshness_days", 0)
            if days == 0:
                freshness_buckets["Today (0 days)"] += 1
            elif days <= 7:
                freshness_buckets["Last Week (1-7 days)"] += 1
            elif days <= 30:
                freshness_buckets["Last Month (8-30 days)"] += 1
            else:
                freshness_buckets["Older (>30 days)"] += 1

        # Calculate average trust score
        trust_scores = [src.get("trust_score", 0.95) for src in self.sources.values()]
        avg_trust = round((sum(trust_scores) / (len(trust_scores) or 1)) * 100, 1)

        # Canonical Dependency Chain for MSC Bellissima
        bellissima_deps = [
            {"tier": "Statutory Identity", "source": "src:imo-gisis", "name": "IMO Global Integrated Shipping Information System", "trust": "100%"},
            {"tier": "Radiocommunications", "source": "src:itu-mars", "name": "ITU Maritime Mobile Access and Retrieval System", "trust": "100%"},
            {"tier": "Naval Architecture", "source": "src:chantiers-atlantique-ga", "name": "Chantiers de l'Atlantique General Arrangement Sheet", "trust": "98%"},
            {"tier": "Classification Society", "source": "src:bureau-veritas-marine", "name": "Bureau Veritas Marine Register", "trust": "99%"},
            {"tier": "Commercial Operations", "source": "src:msc-cruises-official", "name": "MSC Cruises Official Stateroom & Venue Registry", "trust": "95%"},
            {"tier": "Homeport Logistics", "source": "src:port-authority-genoa", "name": "Ports of Genoa Authority (Ponte dei Mille)", "trust": "98%"},
        ]

        return {
            "total_sources_indexed": total_sources,
            "average_network_trust_pct": avg_trust,
            "category_distribution": dict(category_counts),
            "access_method_distribution": dict(access_counts),
            "freshness_distribution": freshness_buckets,
            "canonical_dependency_chain": bellissima_deps,
        }
