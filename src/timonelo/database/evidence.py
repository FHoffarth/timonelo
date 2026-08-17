"""
Evidence records for Timonelo.

Governed by ADR-0002 (The Truth Model).

An evidence record states that an OBSERVATION OCCURRED. It is never an attribute
describing a value. Nothing here may carry a confidence number: confidence is
computed by traversing the derivation graph at query time and is never stored.

    ADR-0002 I1 - Confidence is never stored.
    ADR-0002 I2 - Evidence records events, not values.
    ADR-0002 I3 - UNKNOWN is computed, never authored.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple


class EvidenceType(str, Enum):
    OFFICIAL_DOCUMENT = "OFFICIAL_DOCUMENT"
    SHIPYARD_DRAWING = "SHIPYARD_DRAWING"
    CRUISE_LINE = "CRUISE_LINE"
    IMO = "IMO"
    PORT_AUTHORITY = "PORT_AUTHORITY"
    FIELD_MEASUREMENT = "FIELD_MEASUREMENT"
    CREW_VERIFIED = "CREW_VERIFIED"
    PASSENGER_VERIFIED = "PASSENGER_VERIFIED"
    PHOTO_ANALYSIS = "PHOTO_ANALYSIS"
    VIDEO_ANALYSIS = "VIDEO_ANALYSIS"
    COMMUNITY_CONFIRMED = "COMMUNITY_CONFIRMED"
    UNKNOWN = "UNKNOWN"


class ReviewState(str, Enum):
    """Human review state. NOT a confidence level and NOT a truth claim."""
    UNREVIEWED = "UNREVIEWED"
    REVIEWED = "REVIEWED"
    CONFLICTED = "CONFLICTED"


class Method(str, Enum):
    """ADR-0002 6.1 - how the statement was produced."""
    DIRECT = "DIRECT"
    CALCULATED = "CALCULATED"
    INFERRED = "INFERRED"


class Derivation(str, Enum):
    """ADR-0002 6.2 - where the inputs originated. Orthogonal to Method."""
    LOCAL = "LOCAL"
    SISTER_SHIP = "SISTER_SHIP"
    REFERENCE_MODEL = "REFERENCE_MODEL"
    GENERATED = "GENERATED"


# EvidenceField deleted (ADR-0002 §11.2).
#
# It was never referenced anywhere in the codebase: documentation pretending to
# be implementation. Its concepts (method, derivation, validity window, review
# state) now live on ontology.models.EvidenceLink, which is the real trust
# primitive. Keeping a second, dormant trust type invited divergence from the
# one that is actually load-bearing.


@dataclass(frozen=True)
class EvidenceConflict:
    """A discrepancy between two competing evidence records."""
    conflict_id: str
    entity_id: str
    field_path: str
    primary_source: str
    primary_value: Any
    competing_source: str
    competing_value: Any
    status: str = "OPEN_REQUIRES_REVIEW"
    notes: str = ""


class EvidenceEngine:
    """
    Audits provenance coverage.

    This class deliberately does NOT compute a confidence score. Confidence is a
    property of graph traversal (ADR-0002 7) and cannot be derived by counting
    fields. The previous implementation produced one by incrementing fabricated
    counters; that is removed rather than replaced.
    """

    @classmethod
    def audit_ship(cls, ship: Dict[str, Any]) -> Tuple[Dict[str, Any], List[EvidenceConflict]]:
        conflicts: List[EvidenceConflict] = []
        slug = ship.get("slug", "unknown")
        entity_id = f"ship:{slug}"

        total_fields = 0
        with_provenance = 0
        without_provenance = 0

        for _key, value in sorted(ship.get("dimensions", {}).items()):
            total_fields += 1
            # A bare scalar carries no provenance. Absence of evidence is not
            # evidence - it counts as UNKNOWN, never as OFFICIAL.
            if isinstance(value, dict) and value.get("source_id"):
                with_provenance += 1
            else:
                without_provenance += 1

        # Cabins are NOT counted here. Cabin-level facts are only auditable once
        # they carry per-field provenance; counting them by assumption is what
        # the previous implementation did (total_facts += 6, verified_count += 5).
        cabin_count = len(ship.get("cabins", []))

        for raw in ship.get("evidence_conflicts", []):
            conflicts.append(
                EvidenceConflict(
                    conflict_id=raw.get("conflict_id", f"conf:{slug}:{raw.get('field')}"),
                    entity_id=entity_id,
                    field_path=raw.get("field", "unknown"),
                    primary_source=raw.get("primary_source", "UNKNOWN"),
                    primary_value=raw.get("primary_value"),
                    competing_source=raw.get("competing_source", "UNKNOWN"),
                    competing_value=raw.get("competing_value"),
                    status="OPEN_REQUIRES_REVIEW",
                    notes=raw.get("notes", ""),
                )
            )

        metrics = {
            "entity_id": entity_id,
            "total_fields_audited": total_fields,
            "fields_with_provenance": with_provenance,
            "fields_without_provenance": without_provenance,
            # Coverage is provenance coverage only. It is NOT a confidence score
            # and must never be rendered as one (ADR-0002 9).
            "provenance_coverage": (
                round(with_provenance / total_fields, 4) if total_fields else 0.0
            ),
            "cabins_present": cabin_count,
            "cabins_audited": 0,
            "conflicts_count": len(conflicts),
        }
        return metrics, conflicts
