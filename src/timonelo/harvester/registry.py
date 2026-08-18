"""
src/timonelo/harvester/registry.py

Source Registry managing discovered and verified primary artifacts.
Persists in data/sources_registry.json.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
from timonelo.canonical import canonical_dump
from timonelo.harvester.models import (
    HarvestedArtifactRecord, DocumentType, SourceTrustTier, VersionRecord
)



class SourceRegistry:
    def __init__(self, registry_file: str = "data/sources_registry.json"):
        self.registry_file = registry_file
        self.records: Dict[str, HarvestedArtifactRecord] = {}
        self.versions: List[VersionRecord] = []
        self._load()

    def _load(self) -> None:
        if not os.path.isfile(self.registry_file):
            return
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for item in data.get("sources", []):
                rec = HarvestedArtifactRecord(
                    source_id=item["source_id"],
                    cruise_line_id=item["cruise_line_id"],
                    vessel_id=item.get("vessel_id"),
                    document_type=DocumentType(item["document_type"]),
                    title=item["title"],
                    publisher=item["publisher"],
                    language=item.get("language", "unknown"),
                    edition=item.get("edition"),
                    source_url=item["source_url"],
                    final_url=item["final_url"],
                    retrieved_at=item["retrieved_at"],
                    sha256=item["sha256"],
                    file_size_bytes=item["file_size_bytes"],
                    page_count=item["page_count"],
                    mime_type=item["mime_type"],
                    source_tier=SourceTrustTier(item["source_tier"]),
                    verification_status=item["verification_status"],
                    vault_path=item["vault_path"],
                    retrieval_history=item.get("retrieval_history", [])
                )
                self.records[rec.sha256] = rec

            for v in data.get("versions", []):
                self.versions.append(VersionRecord(**v))

        except Exception as e:
            print(f"[WARN] Failed to load source registry: {e}")

    def save(self) -> None:
        payload = {
            "sources": [r.to_dict() for r in self.records.values()],
            "version": "1.0.0",
            "versions": [v.to_dict() for v in self.versions]
        }
        canonical_dump(payload, self.registry_file)

    def find_by_sha256(self, sha256: str) -> Optional[HarvestedArtifactRecord]:
        return self.records.get(sha256)

    def register_artifact(
        self, record: HarvestedArtifactRecord, timestamp: str
    ) -> Tuple[HarvestedArtifactRecord, bool]:
        """
        Registers an artifact. If SHA-256 already exists, updates retrieval history (duplicate).
        If new SHA-256, registers as new record and checks for version candidate.
        Returns: (record, is_new)
        """
        existing = self.find_by_sha256(record.sha256)
        if existing:
            if timestamp not in existing.retrieval_history:
                existing.retrieval_history.append(timestamp)
            self.save()
            return existing, False

        # New record
        if timestamp not in record.retrieval_history:
            record.retrieval_history.append(timestamp)
        self.records[record.sha256] = record

        # Version candidate tracking
        if record.vessel_id and record.document_type == DocumentType.DECK_PLAN:
            doc_family = f"{record.vessel_id}-deck-plan"
            self.versions.append(VersionRecord(
                document_family=doc_family,
                vessel_id=record.vessel_id,
                artifact_sha256=record.sha256,
                edition=record.edition,
                retrieved_at=timestamp,
                status="CURRENT_CANDIDATE"
            ))

        self.save()
        return record, True
