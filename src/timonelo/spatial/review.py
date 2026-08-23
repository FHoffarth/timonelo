"""
Spatial Review Adjudication Engine (ADR-0002 §5, ADR-0003 §7).
Governs human adjudication of extracted public deck geometries.

Core rules:
- Agent proposes, human reviewer decides.
- Acceptance proves that extracted geometry corresponds to the labeled region on source drawings.
- It does NOT prove entrance, passenger access, seating boundary semantics, connectivity, or accessibility.
- Publication admission strictly requires canonical Gatekeeper truth conditions (valid source provenance, admitted identity).
- Finalization fails closed without an explicit, non-empty reviewer identity (no phantom reviewer).
- Surgical mutation only: records pre/post lifecycle deltas and generates audit logs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from timonelo.evidence.gatekeeper import (
    GeometryProvenanceRecord,
    is_canonical_statement_admitted,
)
from timonelo.ontology.models import (
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    PublishStatus,
)


class ReviewDecisionState(str, Enum):
    UNREVIEWED = "UNREVIEWED"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    NEEDS_CORRECTION = "NEEDS_CORRECTION"


class VenueAssociationState(str, Enum):
    MATCHED = "MATCHED"
    AMBIGUOUS = "AMBIGUOUS"
    NO_MATCH = "NO_MATCH"


# Documented canonical alias mapping for official deck plan labels to statements
KNOWN_VENUE_ALIASES: Dict[str, str] = {
    "posidonia restaurant": "POSIDONIA RESTAURANT",
    "infinity atrium": "INFINITY ATRIUM",
    "infinity bar": "INFINITY BAR",
    "london theatre": "LONDON THEATRE",
    "lighthouse restaurant": "LIGHTHOUSE RESTAURANT",
    "galleria bellissima": "GALLERIA BELLISSIMA",
    "bellissima bar & lounge": "BELLISSIMA BAR & LOUNGE",
    "bellissima lounge": "BELLISSIMA BAR & LOUNGE",
    "edge cocktail bar": "EDGE COCKTAIL BAR",
    "hola! tapas bar": "HOLA! TAPAS BAR",
    "tapas bar": "HOLA! TAPAS BAR",
    "imperial casino": "IMPERIAL CASINO",
    "champagne bar": "CHAMPAGNE BAR",
    "kaito sushi bar": "KAITO SUSHI BAR",
    "tv studio & bar": "TV STUDIO & BAR",
    "tv studio": "TV STUDIO & BAR",
    "carousel lounge": "CAROUSEL LOUNGE",
    "msc aurea spa": "MSC AUREA SPA",
    "butcher's cut": "BUTCHER'S CUT",
    "kaito teppanyaki": "KAITO TEPPANYAKI",
}

BANNED_PHANTOM_REVIEWERS = frozenset({
    "",
    "unspecified_reviewer",
    "human_curator",
    "null",
    "none",
    "undefined",
    "system",
    "agent",
    "machine",
})


@dataclass(frozen=True)
class VenueAssociationResult:
    state: VenueAssociationState
    statement_id: Optional[str] = None
    statement_name: Optional[str] = None
    statement_deck: Optional[int] = None
    statement_data: Optional[Dict[str, Any]] = None
    is_canonical_admitted: bool = False
    reason: str = ""


@dataclass(frozen=True)
class SpatialReviewDecision:
    object_id: str
    decision: ReviewDecisionState
    reviewer: str
    timestamp: str
    deck_number: int
    note: str = ""


@dataclass(frozen=True)
class LifecycleDelta:
    object_id: str
    from_review_state: str
    to_review_state: str
    from_publish_status: str
    to_publish_status: str
    from_condition: str
    to_condition: str
    adjudication_outcome: str


def compute_proof_snapshot_hash(proof_data: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 hash of proof objects prior to adjudication."""
    canonical_json = json.dumps(proof_data.get("objects", []), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def match_venue_statement(
    candidate_label: str,
    deck_number: int,
    statements: Dict[str, Dict[str, Any]],
) -> VenueAssociationResult:
    """Deterministically associates a candidate extracted label with a canonical statement.
    Evaluates statement publishability directly through canonical is_canonical_statement_admitted().
    """
    clean_label = candidate_label.strip().lower()
    canonical_target = KNOWN_VENUE_ALIASES.get(clean_label)
    
    matches: List[Tuple[str, Dict[str, Any]]] = []
    
    for sid, s in statements.items():
        if s.get("statement_type") != "deck.venue_present":
            continue
        
        # Check deck match
        s_decks = s.get("value") or [s.get("deck_number")]
        if isinstance(s_decks, int):
            s_decks = [s_decks]
        if deck_number not in s_decks and s.get("deck_number") != deck_number:
            continue
        
        # Check target entity / name match
        target = s.get("target_entity", "").upper()
        locator = s.get("locator", "").upper()
        
        is_name_match = False
        if canonical_target and (canonical_target in target or f'"{canonical_target}"' in locator):
            is_name_match = True
        elif clean_label.upper() in target or f'"{clean_label.upper()}"' in locator:
            is_name_match = True
            
        if is_name_match:
            matches.append((sid, s))
            
    if len(matches) == 1:
        sid, stmt = matches[0]
        name = stmt.get("target_entity") or clean_label.title()
        is_admitted, gate_reason = is_canonical_statement_admitted(stmt)
        return VenueAssociationResult(
            state=VenueAssociationState.MATCHED,
            statement_id=sid,
            statement_name=name,
            statement_deck=deck_number,
            statement_data=stmt,
            is_canonical_admitted=is_admitted,
            reason=f"Matched statement {sid} on Deck {deck_number}: {gate_reason}",
        )
    elif len(matches) > 1:
        return VenueAssociationResult(
            state=VenueAssociationState.AMBIGUOUS,
            reason=f"Multiple competing candidate statements ({len(matches)}) found on Deck {deck_number}",
        )
    else:
        return VenueAssociationResult(
            state=VenueAssociationState.NO_MATCH,
            reason=f"No matching venue statement registered for '{candidate_label}' on Deck {deck_number}",
        )


def adjudicate_spatial_objects(
    proof_data: Dict[str, Any],
    decisions: Dict[str, SpatialReviewDecision],
    statements: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, Any], List[LifecycleDelta], List[Dict[str, Any]]]:
    """Applies surgical adjudication mutations to proof objects based on human decisions
    gated by canonical Gatekeeper rules and requiring explicit reviewer identity.
    """
    updated_objects: List[Dict[str, Any]] = []
    deltas: List[LifecycleDelta] = []
    audit_entries: List[Dict[str, Any]] = []
    
    deck_num = proof_data.get("deck", {}).get("number", 0)
    
    for obj in proof_data.get("objects", []):
        oid = obj["object_id"]
        decision_record = decisions.get(oid)
        
        from_rev = obj.get("human_review_state", HumanReviewState.DRAFT.value)
        from_pub = obj.get("publish_status", PublishStatus.PUBLISH_BLOCKED.value)
        from_cond = obj.get("evidence_condition", EvidenceCondition.UNKNOWN.value)
        
        if not decision_record or decision_record.decision == ReviewDecisionState.UNREVIEWED:
            updated_objects.append(obj)
            continue
            
        # Reviewer Identity Validation — fail closed on phantom or empty reviewers
        raw_reviewer = decision_record.reviewer.strip()
        if raw_reviewer.lower() in BANNED_PHANTOM_REVIEWERS:
            raise ValueError("Reviewer name is required before finalizing decisions.")
            
        to_rev = from_rev
        to_pub = from_pub
        to_cond = from_cond
        outcome = "NO_CHANGE"
        
        if decision_record.decision == ReviewDecisionState.ACCEPT:
            # 1. Evaluate Geometry Provenance via canonical Gatekeeper record
            prov_str = obj.get("geometry_provenance", "")
            try:
                geom_prov = GeometryProvenance(prov_str)
            except ValueError:
                geom_prov = GeometryProvenance.SYNTHETIC_GEOMETRY
                
            geom_record = GeometryProvenanceRecord(
                object_id=oid,
                deck_number=deck_num,
                geometry_provenance=geom_prov,
                source_id=obj.get("source_references", [None])[0],
            )
            
            valid_prov = geom_prov in (
                GeometryProvenance.DIRECT_SOURCE_GEOMETRY,
                GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY,
                GeometryProvenance.DERIVED_GEOMETRY,
            )
            
            # Geometry visual accuracy accepted by human reviewer
            to_rev = HumanReviewState.APPROVED.value
            
            # 2. Evaluate Venue Association and Canonical Statement Gate
            assoc = match_venue_statement(obj.get("label", ""), deck_num, statements)
            
            if valid_prov and assoc.state == VenueAssociationState.MATCHED:
                if assoc.is_canonical_admitted:
                    to_cond = EvidenceCondition.SUPPORTED.value
                    to_pub = PublishStatus.PUBLISH_ALLOWED.value
                    outcome = "PROMOTED_TO_PASSENGER_PUBLISH"
                else:
                    # Statement exists but canonical gate rejected publication -> keep publish blocked!
                    to_cond = EvidenceCondition.SUPPORTED.value
                    to_pub = PublishStatus.PUBLISH_BLOCKED.value
                    outcome = "GEOMETRY_APPROVED_IDENTITY_STATEMENT_BLOCKED"
            elif obj.get("semantic_type") in ("cabin", "vertical_core_region") and valid_prov:
                to_cond = EvidenceCondition.SUPPORTED.value
                to_pub = PublishStatus.PUBLISH_BLOCKED.value
                outcome = "GEOMETRY_APPROVED_INFRASTRUCTURE_BLOCKED"
            else:
                to_cond = EvidenceCondition.SUPPORTED.value
                to_pub = PublishStatus.PUBLISH_BLOCKED.value
                outcome = "GEOMETRY_APPROVED_IDENTITY_UNADMITTED"
                
        elif decision_record.decision == ReviewDecisionState.REJECT:
            to_rev = HumanReviewState.REJECTED.value
            to_pub = PublishStatus.PUBLISH_BLOCKED.value
            to_cond = EvidenceCondition.UNSUPPORTED.value
            outcome = "REJECTED_BY_REVIEWER"
            
        elif decision_record.decision == ReviewDecisionState.NEEDS_CORRECTION:
            to_rev = HumanReviewState.UNDER_REVIEW.value
            to_pub = PublishStatus.PUBLISH_BLOCKED.value
            to_cond = EvidenceCondition.UNKNOWN.value
            outcome = "NEEDS_CORRECTION_FLAGGED"
            
        updated_obj = dict(obj)
        updated_obj["human_review_state"] = to_rev
        updated_obj["publish_status"] = to_pub
        updated_obj["evidence_condition"] = to_cond
        updated_obj["last_reviewed_at"] = decision_record.timestamp
        updated_obj["reviewer"] = raw_reviewer
        updated_obj["reviewer_note"] = decision_record.note
        
        updated_objects.append(updated_obj)
        
        delta = LifecycleDelta(
            object_id=oid,
            from_review_state=from_rev,
            to_review_state=to_rev,
            from_publish_status=from_pub,
            to_publish_status=to_pub,
            from_condition=from_cond,
            to_condition=to_cond,
            adjudication_outcome=outcome,
        )
        deltas.append(delta)
        
        audit_entries.append({
            "object_id": oid,
            "decision": decision_record.decision.value,
            "reviewer": raw_reviewer,
            "timestamp": decision_record.timestamp,
            "note": decision_record.note,
            "deck_number": deck_num,
            "pre_review_state": {
                "human_review_state": from_rev,
                "publish_status": from_pub,
                "evidence_condition": from_cond,
            },
            "post_review_state": {
                "human_review_state": to_rev,
                "publish_status": to_pub,
                "evidence_condition": to_cond,
            },
            "outcome": outcome,
        })
        
    new_proof_data = dict(proof_data)
    new_proof_data["objects"] = updated_objects
    return new_proof_data, deltas, audit_entries
