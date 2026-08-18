"""
src/timonelo/harvester/engine.py

Official Source Harvester Orchestrator v0.1:
Implements discovery -> fetch -> verification -> fingerprint -> classification -> vessel match -> vault -> registry.
"""

import os
import datetime
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from timonelo.harvester.config import MSC_SOURCE_CONFIG, classify_domain_tier
from timonelo.harvester.models import (
    SourceTrustTier, DocumentType, HarvestState, HarvestedArtifactRecord
)
from timonelo.harvester.vessel_resolver import resolve_vessel
from timonelo.harvester.classifier import classify_document
from timonelo.harvester.verifier import verify_pdf_bytes
from timonelo.harvester.vault import EvidenceVault
from timonelo.harvester.registry import SourceRegistry
from timonelo.harvester.fetcher import ArtifactFetcher
from timonelo.harvester.discovery import DiscoveryEngine


@dataclass
class HarvestRunReport:
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    target_cruise_line: str = "msc"
    target_vessel: Optional[str] = None
    dry_run: bool = False
    candidates_evaluated: int = 0
    downloads_attempted: int = 0
    downloads_successful: int = 0
    valid_pdfs_found: int = 0
    official_sources_verified: int = 0
    third_party_sources: int = 0
    duplicates_detected: int = 0
    version_candidates: int = 0
    unresolved_vessels: int = 0
    failed_downloads: int = 0
    robots_blocked: int = 0
    saved_artifacts: List[str] = field(default_factory=list)
    new_records: List[str] = field(default_factory=list)
    details: List[Dict[str, Any]] = field(default_factory=list)


class HarvestEngine:
    def __init__(
        self,
        vault_root: str = "evidence/raw/sha256",
        registry_file: str = "data/sources_registry.json",
        config: Dict[str, Any] = MSC_SOURCE_CONFIG
    ):
        self.config = config
        self.vault = EvidenceVault(vault_root=vault_root)
        self.registry = SourceRegistry(registry_file=registry_file)
        self.fetcher = ArtifactFetcher(config=config)
        self.discovery = DiscoveryEngine(config=config)

    def process_raw_bytes(
        self,
        data: bytes,
        source_url: str,
        final_url: str,
        dry_run: bool = False,
        hint_vessel_id: Optional[str] = None
    ) -> Tuple[HarvestState, Optional[HarvestedArtifactRecord], Dict[str, Any]]:
        """
        Processes raw bytes through the verification and registration pipeline.
        """
        # 1. Byte-level PDF verification
        is_valid, reason, vdata = verify_pdf_bytes(data)
        if not is_valid:
            state = HarvestState.CORRUPT_FILE if "CORRUPT" in reason else HarvestState.NOT_A_PDF
            return state, None, {"error": reason}

        # 2. Domain & Trust Tier Classification
        parsed_url = urllib.parse.urlparse(source_url)
        domain = parsed_url.netloc or "local"
        tier_str = classify_domain_tier(domain) if domain != "local" else "TIER_A"
        source_tier = SourceTrustTier(tier_str)
        is_official = source_tier in [SourceTrustTier.TIER_A, SourceTrustTier.TIER_B]
        verification_status = "VERIFIED_OFFICIAL_SOURCE" if is_official else "UNVERIFIED_THIRD_PARTY"

        # 3. Document Classification
        doc_type, meta = classify_document(
            first_page_text=vdata.get("first_page_text", ""),
            filename=os.path.basename(parsed_url.path),
            url=source_url,
            pdf_title=vdata.get("pdf_title")
        )

        # 4. Vessel Matching
        matched_vessel_id, vres_status = resolve_vessel(
            text=vdata.get("first_page_text", ""),
            url=source_url,
            filename=os.path.basename(parsed_url.path)
        )
        if not matched_vessel_id and hint_vessel_id:
            matched_vessel_id = hint_vessel_id

        if not matched_vessel_id:
            state = HarvestState.VESSEL_UNRESOLVED if vres_status == "VESSEL_UNRESOLVED" else HarvestState.MANUAL_REVIEW_REQUIRED
            return state, None, {"verification": vdata, "doc_type": doc_type.value, "vessel_status": vres_status}

        sha256 = vdata["sha256"]
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 5. Vault Storage
        vault_rel_path, is_duplicate = self.vault.store_artifact(data, sha256) if not dry_run else (f"evidence/raw/sha256/{sha256[:2]}/{sha256}.pdf", False)

        # 6. Record Generation & Registration
        stable_vessel_tag = matched_vessel_id.replace("msc-", "").upper()
        source_id = f"SRC-MSC-{stable_vessel_tag}-{sha256[:8].upper()}"

        record = HarvestedArtifactRecord(
            source_id=source_id,
            cruise_line_id=self.config["cruise_line_id"],
            vessel_id=matched_vessel_id,
            document_type=doc_type,
            title=meta.get("title") or f"{matched_vessel_id} Deck Plan",
            publisher=self.config["publisher_name"] if is_official else "Third Party / Unverified",
            language=meta.get("language", "unknown"),
            edition=meta.get("edition"),
            source_url=source_url,
            final_url=final_url,
            retrieved_at=now_iso,
            sha256=sha256,
            file_size_bytes=vdata["file_size_bytes"],
            page_count=vdata["page_count"],
            mime_type=vdata["mime_type"],
            source_tier=source_tier,
            verification_status=verification_status,
            vault_path=vault_rel_path
        )

        if dry_run:
            return HarvestState.REGISTERED, record, {"is_duplicate": False, "dry_run": True}

        saved_rec, is_new = self.registry.register_artifact(record, now_iso)
        final_state = HarvestState.REGISTERED if is_new else HarvestState.DUPLICATE
        return final_state, saved_rec, {"is_duplicate": not is_new}

    def harvest_candidate(
        self,
        candidate: Dict[str, Any],
        dry_run: bool = False
    ) -> Tuple[HarvestState, Optional[HarvestedArtifactRecord], Dict[str, Any]]:
        """Harvests a single candidate URL or local fixture."""
        url = candidate["url"]
        target_vessel = candidate.get("target_vessel_id")

        if url.startswith("file://") or candidate.get("local_path"):
            local_path = candidate.get("local_path") or url.replace("file:///", "").replace("file://", "")
            if not os.path.isfile(local_path):
                return HarvestState.HTTP_FAILED, None, {"error": f"Local file not found: {local_path}"}
            with open(local_path, "rb") as f:
                raw_bytes = f.read()
            return self.process_raw_bytes(
                raw_bytes, source_url=url, final_url=url, dry_run=dry_run, hint_vessel_id=target_vessel
            )

        # HTTP Fetch
        success, status, final_url, data, err = self.fetcher.fetch_url(url)
        if not success:
            state = HarvestState.ROBOTS_BLOCKED if err == "ROBOTS_BLOCKED" else HarvestState.HTTP_FAILED
            return state, None, {"status_code": status, "error": err}

        return self.process_raw_bytes(
            data, source_url=url, final_url=final_url, dry_run=dry_run, hint_vessel_id=target_vessel
        )

    def run_harvest(
        self,
        vessel_id: Optional[str] = "msc-meraviglia",
        document_type: str = "deck-plan",
        local_fixture: Optional[str] = None,
        dry_run: bool = False
    ) -> HarvestRunReport:
        """Runs the harvest pipeline."""
        report = HarvestRunReport(
            target_cruise_line="msc",
            target_vessel=vessel_id,
            dry_run=dry_run
        )

        candidates: List[Dict[str, Any]] = []
        if local_fixture:
            fix = self.discovery.discover_local_fixture(local_fixture, vessel_id=vessel_id)
            if fix:
                candidates.append(fix)
        elif vessel_id:
            candidates = self.discovery.discover_candidates_for_vessel(vessel_id, document_type)

        report.candidates_evaluated = len(candidates)

        for cand in candidates:
            report.downloads_attempted += 1
            state, rec, meta = self.harvest_candidate(cand, dry_run=dry_run)

            detail = {
                "url": cand["url"],
                "state": state.value,
                "meta": meta
            }

            if state in [HarvestState.REGISTERED, HarvestState.DUPLICATE]:
                report.downloads_successful += 1
                report.valid_pdfs_found += 1
                if rec and rec.source_tier in [SourceTrustTier.TIER_A, SourceTrustTier.TIER_B]:
                    report.official_sources_verified += 1
                else:
                    report.third_party_sources += 1

                if state == HarvestState.DUPLICATE:
                    report.duplicates_detected += 1
                else:
                    if rec:
                        report.saved_artifacts.append(rec.vault_path)
                        report.new_records.append(rec.source_id)

            elif state == HarvestState.ROBOTS_BLOCKED:
                report.robots_blocked += 1
            elif state == HarvestState.HTTP_FAILED:
                report.failed_downloads += 1
            elif state in [HarvestState.VESSEL_UNRESOLVED, HarvestState.MANUAL_REVIEW_REQUIRED]:
                report.unresolved_vessels += 1

            report.details.append(detail)

        return report
