"""
Knowledge Review Queue and Ingestion Staging Workflow.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import datetime
import json
import os


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MERGED = "MERGED"


@dataclass
class ReviewQueueItem:
    item_id: str
    entity_id: str
    entity_type: str
    importer_source_id: str
    submitted_at: str
    candidate_payload: Dict[str, Any]
    diff_summary: Dict[str, Any]
    validation_status: str  # "PASSED" or "FAILED"
    validation_errors: List[str]
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[str] = None


class KnowledgeReviewQueue:
    """Manages staging and human review workflow before production promotion."""

    def __init__(self, staging_file: str):
        self.staging_file = staging_file
        self.items: Dict[str, ReviewQueueItem] = {}
        self._load()

    def submit_candidate(
        self,
        entity_id: str,
        entity_type: str,
        importer_source_id: str,
        candidate_payload: Dict[str, Any],
        diff_summary: Dict[str, Any],
        validation_errors: List[str],
    ) -> ReviewQueueItem:
        item_id = f"rev:{entity_type.lower()}:{candidate_payload.get('slug', 'entry')}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        status = ReviewStatus.PENDING
        val_status = "PASSED" if not validation_errors else "FAILED"
        if validation_errors:
            status = ReviewStatus.REJECTED

        item = ReviewQueueItem(
            item_id=item_id,
            entity_id=entity_id,
            entity_type=entity_type,
            importer_source_id=importer_source_id,
            submitted_at=now,
            candidate_payload=candidate_payload,
            diff_summary=diff_summary,
            validation_status=val_status,
            validation_errors=validation_errors,
            status=status,
        )
        self.items[item_id] = item
        self._save()
        return item

    def approve_item(self, item_id: str, notes: str = "Approved for production") -> bool:
        if item_id in self.items:
            item = self.items[item_id]
            if item.validation_status == "PASSED":
                item.status = ReviewStatus.APPROVED
                item.reviewer_notes = notes
                item.reviewed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                self._save()
                return True
        return False

    def get_statistics(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in ReviewStatus}
        for it in self.items.values():
            counts[it.status.value] = counts.get(it.status.value, 0) + 1
        return {
            "total_staged_items": len(self.items),
            **counts,
        }

    def _save(self):
        os.makedirs(os.path.dirname(self.staging_file), exist_ok=True)
        data = {
            "version": "1.0.0",
            "items": [
                {
                    "item_id": it.item_id,
                    "entity_id": it.entity_id,
                    "entity_type": it.entity_type,
                    "importer_source_id": it.importer_source_id,
                    "submitted_at": it.submitted_at,
                    "validation_status": it.validation_status,
                    "validation_errors": it.validation_errors,
                    "status": it.status.value,
                    "reviewer_notes": it.reviewer_notes,
                    "reviewed_at": it.reviewed_at,
                    "candidate_payload": it.candidate_payload,
                    "diff_summary": it.diff_summary,
                }
                for it in self.items.values()
            ],
        }
        with open(self.staging_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)

    def _load(self):
        if os.path.exists(self.staging_file):
            try:
                with open(self.staging_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for raw in data.get("items", []):
                        item = ReviewQueueItem(
                            item_id=raw["item_id"],
                            entity_id=raw["entity_id"],
                            entity_type=raw["entity_type"],
                            importer_source_id=raw["importer_source_id"],
                            submitted_at=raw["submitted_at"],
                            candidate_payload=raw.get("candidate_payload", {}),
                            diff_summary=raw.get("diff_summary", {}),
                            validation_status=raw.get("validation_status", "PASSED"),
                            validation_errors=raw.get("validation_errors", []),
                            status=ReviewStatus(raw.get("status", "PENDING")),
                            reviewer_notes=raw.get("reviewer_notes"),
                            reviewed_at=raw.get("reviewed_at"),
                        )
                        self.items[item.item_id] = item
            except Exception:
                pass
