"""
Knowledge Diff Engine.
Detects additions, removals, modifications, and confidence deltas between knowledge states.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class FieldDiff:
    field_path: str
    old_value: Any
    new_value: Any
    old_source_id: Optional[str]
    new_source_id: Optional[str]
    confidence_delta: float
    requires_human_review: bool


@dataclass(frozen=True)
class EntityDiffReport:
    entity_id: str
    entity_type: str  # "Ship", "Port", "Class", "Venue"
    diff_type: str    # "ADDED", "REMOVED", "MODIFIED", "UNCHANGED"
    field_diffs: List[FieldDiff] = field(default_factory=list)
    review_required: bool = False


class KnowledgeDiffEngine:
    """Compares previous production state against newly ingested candidates."""

    @classmethod
    def compare_ship(cls, old_ship: Optional[Dict[str, Any]], new_ship: Dict[str, Any]) -> EntityDiffReport:
        slug = new_ship.get("slug", "unknown")
        entity_id = f"ship:{slug}"

        if not old_ship:
            return EntityDiffReport(
                entity_id=entity_id,
                entity_type="Ship",
                diff_type="ADDED",
                review_required=True,
            )

        field_diffs: List[FieldDiff] = []
        requires_review = False

        # Compare dimensions
        old_dims = old_ship.get("dimensions", {})
        new_dims = new_ship.get("dimensions", {})
        for dim_key in ["length_m", "beam_m", "gross_tonnage", "draft_m"]:
            old_val = cls._get_val(old_dims.get(dim_key))
            new_val = cls._get_val(new_dims.get(dim_key))
            if old_val != new_val and new_val is not None:
                # If dimension changed by more than 1%, flag for human review
                pct_change = abs(new_val - old_val) / (old_val or 1) if old_val else 1.0
                flag = pct_change > 0.01
                if flag:
                    requires_review = True

                field_diffs.append(
                    FieldDiff(
                        field_path=f"dimensions.{dim_key}",
                        old_value=old_val,
                        new_value=new_val,
                        old_source_id=cls._get_src(old_dims.get(dim_key)),
                        new_source_id=cls._get_src(new_dims.get(dim_key)),
                        confidence_delta=0.0,
                        requires_human_review=flag,
                    )
                )

        # Compare capacities
        old_caps = old_ship.get("capacities", {})
        new_caps = new_ship.get("capacities", {})
        for cap_key in ["passenger_max", "crew", "total_staterooms"]:
            old_val = cls._get_val(old_caps.get(cap_key))
            new_val = cls._get_val(new_caps.get(cap_key))
            if old_val != new_val and new_val is not None:
                field_diffs.append(
                    FieldDiff(
                        field_path=f"capacities.{cap_key}",
                        old_value=old_val,
                        new_value=new_val,
                        old_source_id=cls._get_src(old_caps.get(cap_key)),
                        new_source_id=cls._get_src(new_caps.get(cap_key)),
                        confidence_delta=0.0,
                        requires_human_review=True,
                    )
                )
                requires_review = True

        diff_type = "MODIFIED" if field_diffs else "UNCHANGED"
        return EntityDiffReport(
            entity_id=entity_id,
            entity_type="Ship",
            diff_type=diff_type,
            field_diffs=field_diffs,
            review_required=requires_review,
        )

    @staticmethod
    def _get_val(entry: Any) -> Any:
        if isinstance(entry, dict):
            return entry.get("value")
        return entry

    @staticmethod
    def _get_src(entry: Any) -> Optional[str]:
        if isinstance(entry, dict):
            return entry.get("source_id")
        return None
