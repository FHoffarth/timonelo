"""
Evidence Dashboard — provenance coverage and conflict analytics.

Governed by ADR-0002 (The Truth Model).

This dashboard reports PROVENANCE COVERAGE. It deliberately does not compute,
rank by, or display a trust or confidence score.

The previous implementation ranked vessels by `confidence_score`, a number
produced inside EvidenceEngine.audit_ship() by incrementing fabricated counters
(`total_facts += 6`, `verified_count += 5`) once per cabin, regardless of
content. It also rendered conflict entries as "SOURCE -> 'value' (98%)" from
authored per-source confidence values. Both are removed rather than replaced:
confidence is a property of graph traversal (ADR-0002 §7) and cannot be
recovered by counting fields.
"""

from __future__ import annotations
from typing import Dict, Any, List
from .evidence import EvidenceEngine, EvidenceConflict


class EvidenceDashboard:
    """Aggregates provenance coverage across the knowledge base."""

    def __init__(self, db: Dict[str, Any]):
        self.db = db
        self.ships = db.get("ships", {})
        self.ports = db.get("ports", {})

    def generate_evidence_report(self) -> Dict[str, Any]:
        total_fields = 0
        total_with_provenance = 0
        total_without_provenance = 0
        total_cabins_present = 0
        total_cabins_audited = 0
        all_conflicts: List[EvidenceConflict] = []
        per_ship: List[Dict[str, Any]] = []

        # sorted() for deterministic output regardless of dict insertion order
        # (ADR-0003 §5.1).
        for slug, ship in sorted(self.ships.items()):
            metrics, conflicts = EvidenceEngine.audit_ship(ship)
            all_conflicts.extend(conflicts)

            total_fields += metrics["total_fields_audited"]
            total_with_provenance += metrics["fields_with_provenance"]
            total_without_provenance += metrics["fields_without_provenance"]
            total_cabins_present += metrics["cabins_present"]
            total_cabins_audited += metrics["cabins_audited"]

            raw_name = ship.get("name")
            name = raw_name.get("value") if isinstance(raw_name, dict) else (raw_name or slug)

            per_ship.append({
                "slug": slug,
                "name": name,
                "fields_audited": metrics["total_fields_audited"],
                "fields_with_provenance": metrics["fields_with_provenance"],
                "provenance_coverage": metrics["provenance_coverage"],
                "cabins_present": metrics["cabins_present"],
                "cabins_audited": metrics["cabins_audited"],
                "conflicts": metrics["conflicts_count"],
            })

        # Ranked by provenance coverage — how much is traceable, not how much
        # is believed. Ties broken by slug so the ordering is total.
        per_ship.sort(key=lambda x: (-x["provenance_coverage"], x["slug"]))

        return {
            "statistics": {
                "total_fields_audited": total_fields,
                "fields_with_provenance": total_with_provenance,
                "fields_without_provenance": total_without_provenance,
                "provenance_coverage": (
                    round(total_with_provenance / total_fields, 4) if total_fields else 0.0
                ),
                # Cabin-level facts are not yet auditable: they carry no
                # per-field provenance. Reported as an explicit gap rather
                # than omitted, so the shortfall stays visible.
                "cabins_present": total_cabins_present,
                "cabins_audited": total_cabins_audited,
                "cabin_audit_gap": total_cabins_present - total_cabins_audited,
                "total_conflicts_detected": len(all_conflicts),
            },
            "ships_by_provenance_coverage": per_ship,
            "conflicts_report": [
                {
                    "conflict_id": c.conflict_id,
                    "entity": c.entity_id,
                    "field": c.field_path,
                    "primary_source": c.primary_source,
                    "primary_value": c.primary_value,
                    "competing_source": c.competing_source,
                    "competing_value": c.competing_value,
                    "status": c.status,
                    "notes": c.notes,
                }
                for c in sorted(all_conflicts, key=lambda c: c.conflict_id)
            ],
        }
