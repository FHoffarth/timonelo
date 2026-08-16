"""
End-to-End Knowledge Factory Pipeline.
"""

from __future__ import annotations
from typing import Dict, Any, List
import os
import json

from .base_importer import BaseImporter, RawPayload
from .normalizer import DataNormalizer
from .validator import IngestionValidator
from .diff_engine import KnowledgeDiffEngine
from .review_queue import KnowledgeReviewQueue, ReviewStatus


class KnowledgeFactoryPipeline:
    """Executes the full ingestion, normalization, diff, and staging cycle."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.staging_file = os.path.join(root_dir, "data", "review_queue.json")
        self.review_queue = KnowledgeReviewQueue(self.staging_file)

    def ingest_ship_candidate(
        self,
        importer: BaseImporter,
        raw_data: Dict[str, Any],
        source_url: str,
        confidence: float = 1.0,
        existing_production_ship: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        # 1. Ingest Raw Payload
        payload = importer.ingest_payload(raw_data, source_url, confidence)

        # 2. Extract and Normalize
        normalized_ship = DataNormalizer.normalize_ship(raw_data, importer.source_id, confidence)

        # 3. Validate against quality gates
        validation_errors = IngestionValidator.validate_ship(normalized_ship)

        # 4. Compute Knowledge Diff
        diff_report = KnowledgeDiffEngine.compare_ship(existing_production_ship, normalized_ship)

        # 5. Stage in Review Queue
        queue_item = self.review_queue.submit_candidate(
            entity_id=diff_report.entity_id,
            entity_type="Ship",
            importer_source_id=importer.source_id,
            candidate_payload=normalized_ship,
            diff_summary={
                "diff_type": diff_report.diff_type,
                "fields_changed": len(diff_report.field_diffs),
                "review_required": diff_report.review_required,
            },
            validation_errors=validation_errors,
        )

        return {
            "queue_item_id": queue_item.item_id,
            "status": queue_item.status.value,
            "validation_status": queue_item.validation_status,
            "validation_errors": validation_errors,
            "diff_type": diff_report.diff_type,
            "requires_review": diff_report.review_required,
            "normalized_entity": normalized_ship,
        }
