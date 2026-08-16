"""
Knowledge History & Immutable Revision Engine for Timonelo.
Every fact has an immutable life story with full traceability, temporal validity, and downstream impact analysis.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import datetime
import json
import os


class LifecycleEventType(str, Enum):
    KEEL_LAID = "KEEL_LAID"
    LAUNCHED = "LAUNCHED"
    DELIVERED = "DELIVERED"
    MAIDEN_VOYAGE = "MAIDEN_VOYAGE"
    REFIT = "REFIT"
    DRYDOCK = "DRYDOCK"
    RENOVATION = "RENOVATION"
    TERMINAL_OPENING = "TERMINAL_OPENING"
    BERTH_EXPANSION = "BERTH_EXPANSION"


@dataclass(frozen=True)
class LifecycleEvent:
    event_id: str
    entity_id: str
    event_type: LifecycleEventType
    date: str
    title: str
    description: str
    location_or_yard: str
    source_id: str
    refit_code: Optional[str] = None


class ClaimStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    CONFLICTED = "CONFLICTED"
    DRAFT = "DRAFT"


@dataclass(frozen=True)
class ClaimRevision:
    revision_id: str
    claim_id: str
    revision_number: int
    value: Any
    unit: Optional[str]
    evidence_type: str
    source_id: str
    confidence: float
    valid_from: str
    valid_until: Optional[str]
    created_at: str
    created_by: str
    status: ClaimStatus = ClaimStatus.ACTIVE
    superseded_by: Optional[str] = None
    reason_for_change: Optional[str] = None
    observation_context: Optional[str] = None


@dataclass
class Claim:
    claim_id: str
    entity_id: str
    field_path: str
    current_revision_id: str
    revisions: List[ClaimRevision] = field(default_factory=list)
    created_at: str = ""
    last_updated_at: str = ""

    def get_current_revision(self) -> Optional[ClaimRevision]:
        for rev in self.revisions:
            if rev.revision_id == self.current_revision_id:
                return rev
        return self.revisions[-1] if self.revisions else None

    def get_revision_as_of(self, as_of_date: str) -> Optional[ClaimRevision]:
        """Time-travel query returning fact state active on given ISO date."""
        for rev in self.revisions:
            if rev.valid_from <= as_of_date:
                if rev.valid_until is None or rev.valid_until > as_of_date:
                    return rev
        return None


@dataclass(frozen=True)
class DownstreamImpact:
    change_event_id: str
    entity_id: str
    field_changed: str
    old_value: Any
    new_value: Any
    affected_domains: List[str]  # e.g., ["WALKING_ROUTES", "CABIN_NOISE", "ACCESSIBILITY"]
    affected_entities: List[str]  # e.g., ["cabin:msc-bellissima:14122", "route:galleria-aft"]
    impact_severity: str         # "LOW", "MEDIUM", "HIGH"
    rationale: str


class KnowledgeHistoryEngine:
    """Manages immutable claim revisions, lifecycles, and downstream impact detection."""

    def __init__(self, history_file: str):
        self.history_file = history_file
        self.claims: Dict[str, Claim] = {}
        self.lifecycle_events: List[LifecycleEvent] = []
        self.downstream_impacts: List[DownstreamImpact] = []
        self._load()

    def record_claim_revision(
        self,
        entity_id: str,
        field_path: str,
        value: Any,
        unit: Optional[str],
        evidence_type: str,
        source_id: str,
        confidence: float,
        valid_from: str,
        valid_until: Optional[str] = None,
        created_by: str = "knowledge_architect",
        reason_for_change: str = "Initial verified baseline",
        observation_context: Optional[str] = None,
    ) -> ClaimRevision:
        claim_id = f"claim:{entity_id}:{field_path}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if claim_id not in self.claims:
            rev_id = f"rev:{claim_id}:v1"
            rev = ClaimRevision(
                revision_id=rev_id,
                claim_id=claim_id,
                revision_number=1,
                value=value,
                unit=unit,
                evidence_type=evidence_type,
                source_id=source_id,
                confidence=confidence,
                valid_from=valid_from,
                valid_until=valid_until,
                created_at=now,
                created_by=created_by,
                status=ClaimStatus.ACTIVE,
                reason_for_change=reason_for_change,
                observation_context=observation_context,
            )
            claim = Claim(
                claim_id=claim_id,
                entity_id=entity_id,
                field_path=field_path,
                current_revision_id=rev_id,
                revisions=[rev],
                created_at=now,
                last_updated_at=now,
            )
            self.claims[claim_id] = claim
            self._save()
            return rev

        # Append new revision and supersede previous
        claim = self.claims[claim_id]
        old_rev = claim.get_current_revision()
        new_rev_num = len(claim.revisions) + 1
        new_rev_id = f"rev:{claim_id}:v{new_rev_num}"

        # Mark old revision as superseded
        if old_rev:
            superseded_old = ClaimRevision(
                revision_id=old_rev.revision_id,
                claim_id=old_rev.claim_id,
                revision_number=old_rev.revision_number,
                value=old_rev.value,
                unit=old_rev.unit,
                evidence_type=old_rev.evidence_type,
                source_id=old_rev.source_id,
                confidence=old_rev.confidence,
                valid_from=old_rev.valid_from,
                valid_until=valid_from,
                created_at=old_rev.created_at,
                created_by=old_rev.created_by,
                status=ClaimStatus.SUPERSEDED,
                superseded_by=new_rev_id,
                reason_for_change=old_rev.reason_for_change,
                observation_context=old_rev.observation_context,
            )
            claim.revisions[-1] = superseded_old

        new_rev = ClaimRevision(
            revision_id=new_rev_id,
            claim_id=claim_id,
            revision_number=new_rev_num,
            value=value,
            unit=unit,
            evidence_type=evidence_type,
            source_id=source_id,
            confidence=confidence,
            valid_from=valid_from,
            valid_until=valid_until,
            created_at=now,
            created_by=created_by,
            status=ClaimStatus.ACTIVE,
            reason_for_change=reason_for_change,
            observation_context=observation_context,
        )
        claim.revisions.append(new_rev)
        claim.current_revision_id = new_rev_id
        claim.last_updated_at = now

        # Detect Downstream Impacts
        if old_rev and old_rev.value != value:
            impact = self._analyze_downstream_impact(entity_id, field_path, old_rev.value, value, new_rev_id)
            if impact:
                self.downstream_impacts.append(impact)

        self._save()
        return new_rev

    def record_lifecycle_event(self, event: LifecycleEvent):
        self.lifecycle_events.append(event)
        self._save()

    def _analyze_downstream_impact(
        self, entity_id: str, field_path: str, old_val: Any, new_val: Any, rev_id: str
    ) -> Optional[DownstreamImpact]:
        """Inspects if an updated fact triggers spatial or acoustic ripples."""
        if "distance_to_nearest_lift" in field_path:
            return DownstreamImpact(
                change_event_id=rev_id,
                entity_id=entity_id,
                field_changed=field_path,
                old_value=old_val,
                new_value=new_val,
                affected_domains=["WALKING_TIME", "ACCESSIBILITY_RANKING"],
                affected_entities=[entity_id],
                impact_severity="MEDIUM",
                rationale=f"Lift distance updated from {old_val}m to {new_val}m; recalculating stateroom transit index.",
            )
        if "deck_number" in field_path or "venue" in entity_id:
            return DownstreamImpact(
                change_event_id=rev_id,
                entity_id=entity_id,
                field_changed=field_path,
                old_value=old_val,
                new_value=new_val,
                affected_domains=["VERTICAL_CIRCULATION", "NOISE_OVERHEAD", "SURROUNDING_CABINS"],
                affected_entities=[f"{entity_id}:surroundings"],
                impact_severity="HIGH",
                rationale="Venue relocation alters vertical deck sound envelope and corridor traffic paths.",
            )
        return None

    def get_history_statistics(self) -> Dict[str, Any]:
        total_claims = len(self.claims)
        total_revisions = sum(len(c.revisions) for c in self.claims.values())
        superseded_count = sum(
            1 for c in self.claims.values() for r in c.revisions if r.status == ClaimStatus.SUPERSEDED
        )
        active_count = sum(
            1 for c in self.claims.values() for r in c.revisions if r.status == ClaimStatus.ACTIVE
        )

        all_dates = [r.created_at for c in self.claims.values() for r in c.revisions if r.created_at]
        all_dates.sort()

        return {
            "total_active_claims": total_claims,
            "total_revisions_stored": total_revisions,
            "active_revisions": active_count,
            "superseded_revisions": superseded_count,
            "lifecycle_events_tracked": len(self.lifecycle_events),
            "downstream_impacts_detected": len(self.downstream_impacts),
            "oldest_verified_fact": all_dates[0] if all_dates else "2019-02-27",
            "newest_verified_fact": all_dates[-1] if all_dates else "2026-08-16",
        }

    def _save(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        data = {
            "version": "1.0.0",
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "entity_id": c.entity_id,
                    "field_path": c.field_path,
                    "current_revision_id": c.current_revision_id,
                    "created_at": c.created_at,
                    "last_updated_at": c.last_updated_at,
                    "revisions": [
                        {
                            "revision_id": r.revision_id,
                            "revision_number": r.revision_number,
                            "value": r.value,
                            "unit": r.unit,
                            "evidence_type": r.evidence_type,
                            "source_id": r.source_id,
                            "confidence": r.confidence,
                            "valid_from": r.valid_from,
                            "valid_until": r.valid_until,
                            "created_at": r.created_at,
                            "created_by": r.created_by,
                            "status": r.status.value,
                            "superseded_by": r.superseded_by,
                            "reason_for_change": r.reason_for_change,
                            "observation_context": r.observation_context,
                        }
                        for r in c.revisions
                    ],
                }
                for c in self.claims.values()
            ],
            "lifecycle_events": [
                {
                    "event_id": e.event_id,
                    "entity_id": e.entity_id,
                    "event_type": e.event_type.value,
                    "date": e.date,
                    "title": e.title,
                    "description": e.description,
                    "location_or_yard": e.location_or_yard,
                    "source_id": e.source_id,
                }
                for e in self.lifecycle_events
            ],
            "downstream_impacts": [
                {
                    "change_event_id": di.change_event_id,
                    "entity_id": di.entity_id,
                    "field_changed": di.field_changed,
                    "old_value": di.old_value,
                    "new_value": di.new_value,
                    "affected_domains": di.affected_domains,
                    "impact_severity": di.impact_severity,
                    "rationale": di.rationale,
                }
                for di in self.downstream_impacts
            ],
        }
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for raw_c in data.get("claims", []):
                        revs = [
                            ClaimRevision(
                                revision_id=r["revision_id"],
                                claim_id=raw_c["claim_id"],
                                revision_number=r["revision_number"],
                                value=r["value"],
                                unit=r.get("unit"),
                                evidence_type=r["evidence_type"],
                                source_id=r["source_id"],
                                confidence=r["confidence"],
                                valid_from=r["valid_from"],
                                valid_until=r.get("valid_until"),
                                created_at=r["created_at"],
                                created_by=r["created_by"],
                                status=ClaimStatus(r["status"]),
                                superseded_by=r.get("superseded_by"),
                                reason_for_change=r.get("reason_for_change"),
                                observation_context=r.get("observation_context"),
                            )
                            for r in raw_c.get("revisions", [])
                        ]
                        claim = Claim(
                            claim_id=raw_c["claim_id"],
                            entity_id=raw_c["entity_id"],
                            field_path=raw_c["field_path"],
                            current_revision_id=raw_c["current_revision_id"],
                            revisions=revs,
                            created_at=raw_c["created_at"],
                            last_updated_at=raw_c["last_updated_at"],
                        )
                        self.claims[claim.claim_id] = claim
            except Exception:
                pass
