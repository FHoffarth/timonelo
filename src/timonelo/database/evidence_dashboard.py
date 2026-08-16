"""
Evidence Dashboard and Discrepancy Conflict Analytics Engine.
"""

from __future__ import annotations
from typing import Dict, Any, List
from .evidence import EvidenceEngine, EvidenceConflict


class EvidenceDashboard:
    """Computes evidence provenance, confidence rankings, and conflict reports."""

    def __init__(self, db: Dict[str, Any]):
        self.db = db
        self.ships = db.get("ships", {})
        self.ports = db.get("ports", {})

    def generate_evidence_report(self) -> Dict[str, Any]:
        total_facts = 0
        total_official = 0
        total_verified = 0
        total_community = 0
        total_unknown = 0
        all_conflicts: List[EvidenceConflict] = []
        ship_trust_scores: List[Dict[str, Any]] = []

        for slug, ship in self.ships.items():
            metrics, conflicts = EvidenceEngine.audit_ship(ship)
            all_conflicts.extend(conflicts)
            total_facts += metrics["total_facts_audited"]
            total_official += metrics["official_facts"]
            total_verified += metrics["verified_facts"]
            total_community += metrics["community_facts"]
            total_unknown += metrics["unknown_facts"]

            name = ship.get("name", {}).get("value") if isinstance(ship.get("name"), dict) else slug
            ship_trust_scores.append({
                "slug": slug,
                "name": name,
                "score": metrics["confidence_score"],
                "facts": metrics["total_facts_audited"],
                "conflicts": metrics["conflicts_count"],
            })

        ship_trust_scores.sort(key=lambda x: (x["score"], x["facts"]), reverse=True)

        return {
            "statistics": {
                "total_facts_audited": total_facts,
                "official_facts_pct": round((total_official / (total_facts or 1)) * 100, 2),
                "field_and_crew_verified_pct": round((total_verified / (total_facts or 1)) * 100, 2),
                "community_pct": round((total_community / (total_facts or 1)) * 100, 2),
                "unknown_pct": round((total_unknown / (total_facts or 1)) * 100, 2),
                "total_conflicts_detected": len(all_conflicts),
            },
            "most_trusted_ships": ship_trust_scores[:5],
            "conflicts_report": [
                {
                    "conflict_id": c.conflict_id,
                    "entity": c.entity_id,
                    "field": c.field_path,
                    "primary": f"{c.primary_source} -> '{c.primary_value}' ({c.confidence_primary * 100:.0f}%)",
                    "competing": f"{c.competing_source} -> '{c.competing_value}' ({c.confidence_competing * 100:.0f}%)",
                    "status": c.status,
                    "notes": c.notes,
                }
                for c in all_conflicts
            ],
        }
