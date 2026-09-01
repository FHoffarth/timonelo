"""
Voyage Knowledge Factory v1 (ADR-0002 / ADR-0001).

Transforms structured voyage intake requests and authoritative sources into
deterministic canonical voyage entities, ports, truth statements, explicit
gaps, and passenger-safe trip knowledge packs.

Core Product Rules:
1. We review source adapters, rules, and exceptions; we do NOT manually review every future voyage.
2. Machine decisions must be machine-labeled (AUTO-ADMISSIBLE vs REVIEW_REQUIRED); never emit fake human approval events.
3. Storage != Truth. Generic infrastructure existence != voyage-specific assignment.
4. Gaps are first-class entities. UNKNOWN is not a failure.
5. Reusable knowledge (Ship, Port/Terminal) is referenced, not duplicated per voyage or per user.
6. Intake is strictly idempotent: running twice creates zero duplicates and preserves existing approved facts.
7. Strict privacy: Passenger PII must never enter canonical reusable voyage data.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from timonelo.evidence import authority
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.publication import NO_AUTHORITY
from timonelo.evidence.models import Statement
from timonelo.evidence.registry import Artifact
from timonelo.evidence.workspace import Workspace
from timonelo.intelligence.ports import PortIntelligenceEvaluator
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)


class AdmissionStatus(str, Enum):
    """Lifecycle policy classification for automated voyage intake."""
    AUTO_ADMISSIBLE = "AUTO_ADMISSIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class AdmissionDecision:
    """Audit record of the automated intake policy evaluation."""
    status: AdmissionStatus
    policy_name: str
    reasons: List[str] = field(default_factory=list)
    evaluated_on: str = field(default_factory=lambda: datetime.date.today().isoformat())


@dataclass(frozen=True)
class ParsedVoyageClaim:
    """Explicit, source-derived claim extracted by an approved parser adapter."""
    question_id: str
    statement_type: str
    value: Any
    artifact_id: str
    locator: str
    parser_id: str
    parser_version: str
    extraction_method: str = "deterministic_pattern_extraction"
    confidence: float = 1.0
    page: Optional[int] = None
    extracted_on: str = field(default_factory=lambda: datetime.date.today().isoformat())


@dataclass(frozen=True)
class VoyageIntakeInput:
    """Minimum reusable input contract representing user/system voyage intent."""
    cruise_line: str
    ship_name: str
    departure_date: str  # YYYY-MM-DD
    departure_location: str  # e.g. "Shanghai, China"
    arrival_date: str  # YYYY-MM-DD
    arrival_location: str  # e.g. "Tokyo, Japan"
    artifact_id: Optional[str] = None  # Reference to registered source artifact
    check_in_time: Optional[str] = None  # e.g. "14:00"
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    voyage_id: Optional[str] = None  # Custom voyage ID override if desired
    claims: Tuple[ParsedVoyageClaim, ...] = ()  # Explicit parsed claims from source

    def validate_syntax(self) -> List[str]:
        """Validate input field syntax and ISO date formats."""
        errors = []
        if not self.cruise_line.strip():
            errors.append("cruise_line is required")
        if not self.ship_name.strip():
            errors.append("ship_name is required")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.departure_date):
            errors.append(f"departure_date '{self.departure_date}' must be YYYY-MM-DD")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.arrival_date):
            errors.append(f"arrival_date '{self.arrival_date}' must be YYYY-MM-DD")
        if not self.departure_location.strip():
            errors.append("departure_location is required")
        if not self.arrival_location.strip():
            errors.append("arrival_location is required")
        return errors


@dataclass(frozen=True)
class VoyageGapRecord:
    """First-class representation of an unresolved factual gap for a voyage."""
    question_id: str
    statement_type: str
    status: str = "UNKNOWN"
    reason: str = ""
    needed_source_class: str = ""
    authoritative_source_family: str = ""
    recheck_strategy: str = ""
    recheck_window: Optional[str] = None
    last_checked_on: str = field(default_factory=lambda: datetime.date.today().isoformat())


@dataclass(frozen=True)
class PassengerTripKnowledgePack:
    """Clean passenger-safe view exposing verified facts, unknowns, and evidence provenance."""
    voyage_entity: str
    vessel_name: str
    departure_date: str
    departure_location: str
    departure_port_unlocode: Optional[str]
    arrival_date: str
    arrival_location: str
    arrival_port_unlocode: Optional[str]
    check_in_time: Optional[str]
    departure_terminal_status: str
    departure_berth_status: str
    arrival_terminal_status: str
    arrival_berth_status: str
    known_generic_infrastructure: List[Dict[str, Any]] = field(default_factory=list)
    trust_metadata: Dict[str, Any] = field(default_factory=dict)
    next_evidence_gaps: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class VoyageKnowledgeResult:
    """Complete output product of Voyage Knowledge Factory intake.
    
    Explicitly separates requested/input context from TruthEngine-verified canonical truth.
    """
    voyage_entity: str
    # Input/Intent Context
    input_vessel: str
    input_departure_date: str
    input_departure_location: str
    input_arrival_date: str
    input_arrival_location: str
    input_check_in_time: Optional[str]
    # TruthEngine-Verified Canonical Facts (None if unverified/unknown)
    vessel: Optional[str] = None
    departure_port: Optional[str] = None
    arrival_port: Optional[str] = None
    departure_date: Optional[str] = None
    departure_location: Optional[str] = None
    arrival_date: Optional[str] = None
    arrival_location: Optional[str] = None
    check_in_time: Optional[str] = None
    departure_terminal: Optional[str] = None
    departure_berth: Optional[str] = None
    arrival_terminal: Optional[str] = None
    arrival_berth: Optional[str] = None
    known_facts: List[Dict[str, Any]] = field(default_factory=list)
    gaps: List[VoyageGapRecord] = field(default_factory=list)
    publishability: PublishStatus = PublishStatus.PUBLISH_BLOCKED
    admission_decision: Optional[AdmissionDecision] = None
    passenger_pack: Optional[PassengerTripKnowledgePack] = None


UNLOCODE_LINKAGE_RULE_DEF = (
    "timonelo.rules.ports.unlocode_linkage:v1:normalize_operator_location_label_and_country_to_unece_unlocode"
)
UNLOCODE_LINKAGE_RULE_HASH = hashlib.sha256(UNLOCODE_LINKAGE_RULE_DEF.encode("utf-8")).hexdigest()

# Standard country name to ISO 3166-1 alpha-2 mapping for UNECE country context
COUNTRY_CODE_MAP = {
    "china": "CN",
    "cn": "CN",
    "japan": "JP",
    "jp": "JP",
    "spain": "ES",
    "es": "ES",
    "italy": "IT",
    "it": "IT",
    "france": "FR",
    "fr": "FR",
    "germany": "DE",
    "de": "DE",
    "united kingdom": "GB",
    "uk": "GB",
    "gb": "GB",
    "united states": "US",
    "usa": "US",
    "us": "US",
}

# Production policy: only genuine, production-approved parsers
DEFAULT_APPROVED_VOYAGE_PARSERS = frozenset({
    "msc_booking_pdf_parser:v1",
    "official_itinerary_parser:v1",
})


def is_admitted_truth(stmt: Statement, *, authority=NO_AUTHORITY) -> bool:
    """Evaluates whether a statement satisfies canonical admitted truth criteria.

    A statement may participate in automated resolution or passenger
    presentation only if it is SUPPORTED, APPROVED, PUBLISH_ALLOWED **and**
    still admissible against the evidence as it stands now. The first three are
    persisted lifecycle state: they record that publication was granted at some
    past moment, under evidence that may since have been superseded. Ship
    identity and port resolution both resolve through this predicate, so a
    statement coasting on a stale grant would put an unverified vessel or
    locode in front of a passenger.

    `authority` therefore defaults to the refusing authority rather than to a
    permissive one. A caller that does not supply the evidence context gets
    False, not a shrug: not being able to check is not the same as passing.
    """
    if not authority.is_currently_authoritative(stmt):
        return False
    return (
        stmt.condition in (EvidenceCondition.SUPPORTED, EvidenceCondition.SUPPORTED.value)
        and stmt.state in (HumanReviewState.APPROVED, HumanReviewState.APPROVED.value)
        and stmt.publishing in (
            PublishStatus.PUBLISH_ALLOWED,
            PublishStatus.PUBLISH_ALLOWED.value,
            PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS,
            PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value,
        )
    )


class VoyageKnowledgeFactory:
    """Deterministic Voyage Knowledge Factory (ADR-0002)."""

    def __init__(
        self,
        workspace: Workspace,
        approved_parsers: Optional[Sequence[str]] = None,
    ):
        self.workspace = workspace
        self.approved_parsers = (
            set(approved_parsers)
            if approved_parsers is not None
            else set(DEFAULT_APPROVED_VOYAGE_PARSERS)
        )

    @property
    def _authority(self):
        """The workspace's publication authority, or the refusing one."""
        editor = getattr(self.workspace, "editor", None)
        return getattr(editor, "authority", None) or NO_AUTHORITY

    @classmethod
    def derive_voyage_entity_id(cls, intake: VoyageIntakeInput) -> str:
        """Deterministically derive canonical voyage entity ID."""
        if intake.voyage_id:
            return intake.voyage_id
        ship_slug = re.sub(r"[^a-z0-9]+", "-", intake.ship_name.strip().lower()).strip("-")
        dep_date_compact = intake.departure_date.replace("-", "")
        dep_loc_slug = intake.departure_location.split(",")[0].strip().lower()
        dep_loc_slug = re.sub(r"[^a-z0-9]+", "-", dep_loc_slug).strip("-")
        arr_loc_slug = intake.arrival_location.split(",")[0].strip().lower()
        arr_loc_slug = re.sub(r"[^a-z0-9]+", "-", arr_loc_slug).strip("-")
        return f"voyage:{ship_slug}:{dep_date_compact}-{dep_loc_slug}-{arr_loc_slug}"

    @classmethod
    def normalize_ship_label(cls, ship_name: str) -> str:
        """Normalizes ship label string to canonical uppercase format."""
        return " ".join(ship_name.strip().upper().split())

    def resolve_ship_identity(self, cruise_line: str, ship_name: str) -> Tuple[Optional[str], Optional[str], bool]:
        """Resolves ship identity against canonical admitted reusable ship knowledge in the workspace.
        
        Storage presence (such as arbitrary cabin or venue records) is NOT identity proof.
        Identity must resolve strictly through admitted truth statements.
        
        Returns:
            (canonical_ship_entity, canonical_vessel_name, is_unique)
        """
        normalized_name = self.normalize_ship_label(ship_name)
        ship_slug = re.sub(r"[^A-Z0-9]+", "-", normalized_name).strip("-")

        matches: List[Tuple[str, str]] = []
        for stmt in self.workspace.editor.all():
            if not is_admitted_truth(stmt, authority=self._authority):
                continue
            if stmt.statement_type in ("ship.official_name", "vessel.official_name", "voyage.vessel"):
                if str(stmt.value).upper() == normalized_name or stmt.entity_id == f"ship:{ship_slug}":
                    matches.append((f"ship:{ship_slug}", normalized_name))
                    break

        if matches:
            return matches[0][0], matches[0][1], True

        return None, None, False

    def resolve_port(self, location_label: str) -> Tuple[Optional[str], Optional[str], bool, Optional[str]]:
        """Resolves a raw port/city location label against canonical UNECE UN/LOCODE knowledge.
        
        Requires BOTH port.official_name and port.un_locode to be canonical admitted truth
        (SUPPORTED + APPROVED + PUBLISH_ALLOWED).
        
        Returns:
            (port_entity_id, unlocode, is_unique, locode_statement_id)
        """
        raw = location_label.strip()
        parts = [p.strip().lower() for p in raw.split(",")]
        city_query = parts[0]
        country_query = parts[1] if len(parts) > 1 else ""
        country_code = COUNTRY_CODE_MAP.get(country_query, "")

        name_stmts_by_entity: Dict[str, Statement] = {}
        locode_stmts_by_entity: Dict[str, Statement] = {}

        for stmt in self.workspace.editor.all():
            if not is_admitted_truth(stmt, authority=self._authority):
                continue
            if stmt.statement_type == "port.official_name":
                name_stmts_by_entity[stmt.entity_id] = stmt
            elif stmt.statement_type == "port.un_locode":
                locode_stmts_by_entity[stmt.entity_id] = stmt

        matches: List[Tuple[str, str, str]] = []

        for entity_id, name_stmt in name_stmts_by_entity.items():
            locode_stmt = locode_stmts_by_entity.get(entity_id)
            if not locode_stmt:
                # Both official_name and un_locode must be admitted truth for this entity
                continue

            port_name = str(name_stmt.value).strip().lower()
            if port_name == city_query or city_query in port_name:
                unlocode = str(locode_stmt.value)
                locode_stmt_id = locode_stmt.statement_id

                if country_code:
                    if unlocode.startswith(country_code):
                        matches.append((entity_id, unlocode, locode_stmt_id))
                else:
                    matches.append((entity_id, unlocode, locode_stmt_id))

        if len(matches) == 1:
            return matches[0][0], matches[0][1], True, matches[0][2]
        elif len(matches) > 1:
            return None, None, False, None

        return None, None, False, None

    def _next_event_id(self) -> str:
        """Collision-safe deterministic event ID generator."""
        nums = []
        pattern = re.compile(r"^EVT-(?:VOYAGE-)?(\d+)$")
        for evt in self.workspace.events.all():
            m = pattern.match(evt.event_id)
            if m:
                nums.append(int(m.group(1)))
        n = 1 + max(nums, default=0)
        return f"EVT-VOYAGE-{n:04d}"

    def evaluate_admission_policy(
        self,
        intake: VoyageIntakeInput,
        ship_resolved: bool,
        dep_port_unique: bool,
        arr_port_unique: bool,
    ) -> AdmissionDecision:
        """Evaluates whether the voyage claims qualify for AUTO-ADMISSIBLE intake."""
        syntax_errors = intake.validate_syntax()
        if syntax_errors:
            return AdmissionDecision(
                status=AdmissionStatus.REJECTED,
                policy_name="voyage_syntax_validation:v1",
                reasons=syntax_errors,
            )

        review_reasons = []

        # 1. Missing artifact check: raw user input is never auto-admitted as truth
        if not intake.artifact_id:
            review_reasons.append("No authoritative source artifact provided; raw input requires review")
            return AdmissionDecision(
                status=AdmissionStatus.REVIEW_REQUIRED,
                policy_name="voyage_intake_automation_policy:v1",
                reasons=review_reasons,
            )

        # 2. Check registered artifact and document class authority
        try:
            artifact = self.workspace.registry.get(intake.artifact_id)
        except Exception:
            review_reasons.append(f"Artifact ID '{intake.artifact_id}' not found in registry")
            return AdmissionDecision(
                status=AdmissionStatus.REVIEW_REQUIRED,
                policy_name="voyage_intake_automation_policy:v1",
                reasons=review_reasons,
            )

        # Validate artifact document class authority for direct voyage claims
        for stype in [
            "voyage.vessel",
            "voyage.departure_date",
            "voyage.departure_location",
            "voyage.arrival_date",
            "voyage.arrival_location",
        ]:
            auth_classes = authority.authoritative_classes(stype)
            if artifact.document_class not in auth_classes:
                review_reasons.append(
                    f"Document class '{artifact.document_class}' has no authority over statement type '{stype}'"
                )

        # 3. Check parsed claims binding
        voyage_entity = self.derive_voyage_entity_id(intake)
        existing_stmts = [s for s in self.workspace.editor.all() if s.entity_id == voyage_entity]

        if not existing_stmts and not intake.claims:
            review_reasons.append("No parsed claims provided for source artifact; cannot auto-admit")
        elif intake.claims:
            claims_by_qid = {c.question_id: c for c in intake.claims}
            required_qids = [
                ("Q-0030", "voyage.vessel", self.normalize_ship_label(intake.ship_name)),
                ("Q-0031", "voyage.departure_date", intake.departure_date),
                ("Q-0032", "voyage.departure_location", intake.departure_location),
                ("Q-0034", "voyage.arrival_date", intake.arrival_date),
                ("Q-0035", "voyage.arrival_location", intake.arrival_location),
            ]
            for q_id, s_type, expected_val in required_qids:
                if not existing_stmts and q_id not in claims_by_qid:
                    review_reasons.append(f"Missing parsed claim for {q_id} ({s_type})")
                    continue
                claim = claims_by_qid.get(q_id)
                if claim:
                    if not claim.locator.strip():
                        review_reasons.append(f"Parsed claim {q_id} is missing a source locator")
                    if claim.parser_id not in self.approved_parsers:
                        review_reasons.append(f"Parser '{claim.parser_id}' is not an approved voyage parser")
                    if claim.artifact_id != intake.artifact_id:
                        review_reasons.append(f"Claim artifact_id '{claim.artifact_id}' mismatch with intake '{intake.artifact_id}'")
                    if str(claim.value).strip() != str(expected_val).strip():
                        review_reasons.append(
                            f"Claim value mismatch for {q_id}: parsed '{claim.value}' != intake '{expected_val}'"
                        )
                    # Check document class authority for this claim's statement type
                    auth_classes = authority.authoritative_classes(claim.statement_type)
                    if artifact.document_class not in auth_classes:
                        review_reasons.append(
                            f"Document class '{artifact.document_class}' has no authority over '{claim.statement_type}'"
                        )

        # 4. Check contradiction against existing truth
        for stmt in existing_stmts:
            for claim in intake.claims:
                if stmt.question_id == claim.question_id and str(stmt.value) != str(claim.value):
                    review_reasons.append(
                        f"Contradiction detected for {stmt.question_id}: existing '{stmt.value}' vs claim '{claim.value}'"
                    )

        # 5. Ship resolution check
        if not ship_resolved:
            review_reasons.append(f"Unknown or unmapped ship name '{intake.ship_name}'")

        # 6. Port ambiguity check
        if not dep_port_unique:
            review_reasons.append(f"Ambiguous or unmapped departure location '{intake.departure_location}'")
        if not arr_port_unique:
            review_reasons.append(f"Ambiguous or unmapped arrival location '{intake.arrival_location}'")

        if review_reasons:
            return AdmissionDecision(
                status=AdmissionStatus.REVIEW_REQUIRED,
                policy_name="voyage_intake_automation_policy:v1",
                reasons=review_reasons,
            )

        return AdmissionDecision(
            status=AdmissionStatus.AUTO_ADMISSIBLE,
            policy_name="voyage_intake_automation_policy:v1",
            reasons=["All required fields uniquely resolved and proven by verified parsed claims"],
        )

    def evaluate_gaps(self, voyage_entity: str, as_of: Optional[str] = None) -> List[VoyageGapRecord]:
        """Detects first-class factual gaps for the voyage."""
        gaps: List[VoyageGapRecord] = []

        gap_configs = [
            (
                "Q-0038",
                "voyage.departure_terminal",
                "No authoritative day-specific departure terminal assignment found for sailing date",
                "port_authority_berth_directory",
                "port_authority",
                "Periodic verification of official embarkation port terminal call schedule",
            ),
            (
                "Q-0039",
                "voyage.arrival_terminal",
                "No authoritative day-specific arrival terminal assignment found for sailing date",
                "port_authority_berth_directory",
                "port_authority",
                "Periodic verification of official debarkation port terminal call schedule",
            ),
            (
                "Q-0040",
                "voyage.departure_berth",
                "No authoritative day-specific departure berth assignment found for sailing date",
                "port_authority_berth_directory",
                "port_authority",
                "Official port authority daily berth assignment log inspection",
            ),
            (
                "Q-0041",
                "voyage.arrival_berth",
                "No authoritative day-specific arrival berth assignment found for sailing date",
                "port_authority_berth_directory",
                "port_authority",
                "Official port authority daily berth assignment log inspection",
            ),
        ]

        for q_id, s_type, reason, src_class, src_family, strategy in gap_configs:
            ans = self.workspace.engine.answer(voyage_entity, q_id, as_of=as_of)
            if not ans.known or ans.value is None:
                gaps.append(
                    VoyageGapRecord(
                        question_id=q_id,
                        statement_type=s_type,
                        status="UNKNOWN",
                        reason=reason,
                        needed_source_class=src_class,
                        authoritative_source_family=src_family,
                        recheck_strategy=strategy,
                        recheck_window="30-60 days prior to call",
                    )
                )

        return gaps

    def build_passenger_pack(
        self,
        voyage_entity: str,
        arr_port_entity: Optional[str],
        gaps: List[VoyageGapRecord],
        as_of: Optional[str] = None,
    ) -> PassengerTripKnowledgePack:
        """Constructs an immutable, passenger-safe trip knowledge pack from TruthEngine."""
        # Query TruthEngine for verified facts
        ans_vessel = self.workspace.engine.answer(voyage_entity, "Q-0030", as_of=as_of)
        ans_dep_date = self.workspace.engine.answer(voyage_entity, "Q-0031", as_of=as_of)
        ans_dep_loc = self.workspace.engine.answer(voyage_entity, "Q-0032", as_of=as_of)
        ans_dep_port = self.workspace.engine.answer(voyage_entity, "Q-0033", as_of=as_of)
        ans_arr_date = self.workspace.engine.answer(voyage_entity, "Q-0034", as_of=as_of)
        ans_arr_loc = self.workspace.engine.answer(voyage_entity, "Q-0035", as_of=as_of)
        ans_arr_port = self.workspace.engine.answer(voyage_entity, "Q-0036", as_of=as_of)
        ans_checkin = self.workspace.engine.answer(voyage_entity, "Q-0037", as_of=as_of)

        vessel_val = str(ans_vessel.value) if ans_vessel.known and ans_vessel.value else "UNVERIFIED"
        dep_date_val = str(ans_dep_date.value) if ans_dep_date.known and ans_dep_date.value else "UNVERIFIED"
        dep_loc_val = str(ans_dep_loc.value) if ans_dep_loc.known and ans_dep_loc.value else "UNVERIFIED"
        dep_port_val = str(ans_dep_port.value).split(":")[-1] if ans_dep_port.known and ans_dep_port.value else None
        arr_date_val = str(ans_arr_date.value) if ans_arr_date.known and ans_arr_date.value else "UNVERIFIED"
        arr_loc_val = str(ans_arr_loc.value) if ans_arr_loc.known and ans_arr_loc.value else "UNVERIFIED"
        arr_port_val = str(ans_arr_port.value).split(":")[-1] if ans_arr_port.known and ans_arr_port.value else None
        checkin_val = str(ans_checkin.value) if ans_checkin.known and ans_checkin.value else None

        # Dynamically discover generic terminal infrastructure for destination port from admitted statements
        generic_infrastructure = []
        if arr_port_entity:
            unlocode = arr_port_entity.split(":")[-1]
            for stmt in self.workspace.editor.all():
                if (
                    stmt.statement_type == "cruise_terminal.official_name"
                    and stmt.entity_id.startswith(f"terminal:{unlocode}:")
                    and is_admitted_truth(stmt, authority=self._authority)
                ):
                    generic_infrastructure.append({
                        "entity_id": stmt.entity_id,
                        "name": str(stmt.value),
                        "notice": "Generic port facility in destination port; specific arrival berth assignment is unconfirmed.",
                    })

        gap_summaries = [f"{g.statement_type}: {g.reason}" for g in gaps]

        return PassengerTripKnowledgePack(
            voyage_entity=voyage_entity,
            vessel_name=vessel_val,
            departure_date=dep_date_val,
            departure_location=dep_loc_val,
            departure_port_unlocode=dep_port_val,
            arrival_date=arr_date_val,
            arrival_location=arr_loc_val,
            arrival_port_unlocode=arr_port_val,
            check_in_time=checkin_val,
            departure_terminal_status="UNCONFIRMED",
            departure_berth_status="UNCONFIRMED",
            arrival_terminal_status="UNCONFIRMED",
            arrival_berth_status="UNCONFIRMED",
            known_generic_infrastructure=generic_infrastructure,
            trust_metadata={
                "governance": "ADR-0002 Truth Engine",
                "truth_model": "Fail-Closed Cryptographic Evidence Graph",
                "pii_isolation": "Zero PII or raw booking payloads in canonical repository",
            },
            next_evidence_gaps=gap_summaries,
        )

    def _ensure_intake_statements(
        self,
        intake: VoyageIntakeInput,
        voyage_entity: str,
        dep_port_entity: Optional[str],
        dep_port_locode_stmt_id: Optional[str],
        arr_port_entity: Optional[str],
        arr_port_locode_stmt_id: Optional[str],
        artifact: Artifact,
    ) -> Dict[str, Statement]:
        """Creates canonical EvidenceEvents and Statements strictly from verified ParsedVoyageClaims."""
        existing_by_question: Dict[str, Statement] = {}
        for stmt in self.workspace.editor.all():
            if stmt.entity_id == voyage_entity:
                existing_by_question[stmt.question_id] = stmt

        claims_by_qid = {c.question_id: c for c in intake.claims}

        for q_id in ["Q-0030", "Q-0031", "Q-0032", "Q-0034", "Q-0035", "Q-0037"]:
            claim = claims_by_qid.get(q_id)
            if not claim or q_id in existing_by_question:
                continue

            event_id = self._next_event_id()
            event = EvidenceEvent(
                event_id=event_id,
                artifact_sha256=artifact.sha256,
                locator=claim.locator,
                entity_id=voyage_entity,
                question_id=q_id,
                observed_value=claim.value,
                observed_by=f"parser:{claim.parser_id}",
                observed_on=claim.extracted_on,
                notes=f"Automated intake claim extracted via {claim.parser_id} ({claim.extraction_method})",
            )
            self.workspace.events.append(event)

            stmt = self.workspace.editor.create(
                entity_id=voyage_entity,
                question_id=q_id,
                statement_type=claim.statement_type,
                value=claim.value,
                artifact_id=artifact.artifact_id,
                locator=claim.locator,
                read_by=f"parser:{claim.parser_id}",
                read_on=claim.extracted_on,
                page=claim.page,
                evidence_event_ids=(event.event_id,),
            )
            stmt = self.workspace.editor.set_evidence_condition(
                statement_id=stmt.statement_id,
                condition=EvidenceCondition.SUPPORTED,
                actor=f"parser:{claim.parser_id}",
                occurred_on=claim.extracted_on,
                note=f"Verified parsed claim via {claim.parser_id}",
            )
            existing_by_question[q_id] = stmt

        # Inferred departure port linkage (Q-0033)
        if "Q-0033" not in existing_by_question and dep_port_entity and dep_port_locode_stmt_id:
            dep_loc_stmt = existing_by_question.get("Q-0032")
            if dep_loc_stmt:
                stmt_dep_port = self.workspace.editor.create(
                    entity_id=voyage_entity,
                    question_id="Q-0033",
                    statement_type="voyage.departure_port",
                    value=dep_port_entity,
                    artifact_id="",
                    locator="",
                    read_by="voyage-intake-automation",
                    read_on=datetime.date.today().isoformat(),
                    method=Method.INFERRED.value,
                    derivation_note=f"Rule {UNLOCODE_LINKAGE_RULE_DEF}: normalize '{intake.departure_location}' to '{dep_port_entity}'",
                    input_statement_ids=(dep_port_locode_stmt_id, dep_loc_stmt.statement_id),
                    rule_hash=UNLOCODE_LINKAGE_RULE_HASH,
                    evidence_event_ids=(),
                )
                stmt_dep_port = self.workspace.editor.set_evidence_condition(
                    statement_id=stmt_dep_port.statement_id,
                    condition=EvidenceCondition.SUPPORTED,
                    actor="voyage-intake-automation",
                    occurred_on=datetime.date.today().isoformat(),
                    note="Inferred UN/LOCODE departure port linkage",
                )
                existing_by_question["Q-0033"] = stmt_dep_port

        # Inferred arrival port linkage (Q-0036)
        if "Q-0036" not in existing_by_question and arr_port_entity and arr_port_locode_stmt_id:
            arr_loc_stmt = existing_by_question.get("Q-0035")
            if arr_loc_stmt:
                stmt_arr_port = self.workspace.editor.create(
                    entity_id=voyage_entity,
                    question_id="Q-0036",
                    statement_type="voyage.arrival_port",
                    value=arr_port_entity,
                    artifact_id="",
                    locator="",
                    read_by="voyage-intake-automation",
                    read_on=datetime.date.today().isoformat(),
                    method=Method.INFERRED.value,
                    derivation_note=f"Rule {UNLOCODE_LINKAGE_RULE_DEF}: normalize '{intake.arrival_location}' to '{arr_port_entity}'",
                    input_statement_ids=(arr_port_locode_stmt_id, arr_loc_stmt.statement_id),
                    rule_hash=UNLOCODE_LINKAGE_RULE_HASH,
                    evidence_event_ids=(),
                )
                stmt_arr_port = self.workspace.editor.set_evidence_condition(
                    statement_id=stmt_arr_port.statement_id,
                    condition=EvidenceCondition.SUPPORTED,
                    actor="voyage-intake-automation",
                    occurred_on=datetime.date.today().isoformat(),
                    note="Inferred UN/LOCODE arrival port linkage",
                )
                existing_by_question["Q-0036"] = stmt_arr_port

        return existing_by_question

    def create_or_get_voyage(
        self,
        intake: VoyageIntakeInput,
        as_of: Optional[str] = None,
    ) -> VoyageKnowledgeResult:
        """Idempotently process voyage intake and compile complete VoyageKnowledgeResult."""
        voyage_entity = self.derive_voyage_entity_id(intake)
        ship_entity, vessel_name, ship_resolved = self.resolve_ship_identity(intake.cruise_line, intake.ship_name)
        vessel_display = vessel_name if vessel_name else self.normalize_ship_label(intake.ship_name)

        dep_port_entity, dep_unlocode, dep_port_unique, dep_port_locode_stmt_id = self.resolve_port(intake.departure_location)
        arr_port_entity, arr_unlocode, arr_port_unique, arr_port_locode_stmt_id = self.resolve_port(intake.arrival_location)

        admission_decision = self.evaluate_admission_policy(
            intake, ship_resolved, dep_port_unique, arr_port_unique
        )

        # Author statements strictly if admission decision is AUTO_ADMISSIBLE and claims are provided
        if intake.artifact_id and admission_decision.status == AdmissionStatus.AUTO_ADMISSIBLE and intake.claims:
            artifact = self.workspace.registry.get(intake.artifact_id)
            self._ensure_intake_statements(
                intake=intake,
                voyage_entity=voyage_entity,
                dep_port_entity=dep_port_entity,
                dep_port_locode_stmt_id=dep_port_locode_stmt_id,
                arr_port_entity=arr_port_entity,
                arr_port_locode_stmt_id=arr_port_locode_stmt_id,
                artifact=artifact,
            )

        # Retrieve statements for this voyage entity
        existing_by_question: Dict[str, Statement] = {}
        for stmt in self.workspace.editor.all():
            if stmt.entity_id == voyage_entity:
                existing_by_question[stmt.question_id] = stmt

        # Collect verified facts strictly from TruthEngine
        known_facts: List[Dict[str, Any]] = []
        for q_id in ["Q-0030", "Q-0031", "Q-0032", "Q-0033", "Q-0034", "Q-0035", "Q-0036", "Q-0037"]:
            ans = self.workspace.engine.answer(voyage_entity, q_id, as_of=as_of)
            if ans.known and ans.value is not None:
                known_facts.append({
                    "question_id": q_id,
                    "value": ans.value,
                    "statement_id": ans.provenance.statement_id if ans.provenance else None,
                })

        # Answer truth-verified fields
        ans_vessel = self.workspace.engine.answer(voyage_entity, "Q-0030", as_of=as_of)
        ans_dep_date = self.workspace.engine.answer(voyage_entity, "Q-0031", as_of=as_of)
        ans_dep_loc = self.workspace.engine.answer(voyage_entity, "Q-0032", as_of=as_of)
        ans_dep_port = self.workspace.engine.answer(voyage_entity, "Q-0033", as_of=as_of)
        ans_arr_date = self.workspace.engine.answer(voyage_entity, "Q-0034", as_of=as_of)
        ans_arr_loc = self.workspace.engine.answer(voyage_entity, "Q-0035", as_of=as_of)
        ans_arr_port = self.workspace.engine.answer(voyage_entity, "Q-0036", as_of=as_of)
        ans_checkin = self.workspace.engine.answer(voyage_entity, "Q-0037", as_of=as_of)

        # Evaluate first-class gaps
        gaps = self.evaluate_gaps(voyage_entity, as_of=as_of)

        # Build passenger pack strictly from TruthEngine
        passenger_pack = self.build_passenger_pack(
            voyage_entity=voyage_entity,
            arr_port_entity=arr_port_entity,
            gaps=gaps,
            as_of=as_of,
        )

        # An aggregate is only as publishable as its constituents are now.
        # Reading each statement's stored `publish_status` let a voyage present
        # itself as publishable on the strength of grants made when its
        # statements were authored -- the same defect as a single statement
        # coasting, multiplied by six.
        publishability = (
            PublishStatus.PUBLISH_ALLOWED
            if all(
                is_admitted_truth(s, authority=self._authority)
                for s in existing_by_question.values()
            ) and len(existing_by_question) >= 6
            else PublishStatus.PUBLISH_BLOCKED
        )

        return VoyageKnowledgeResult(
            voyage_entity=voyage_entity,
            input_vessel=vessel_display,
            input_departure_date=intake.departure_date,
            input_departure_location=intake.departure_location,
            input_arrival_date=intake.arrival_date,
            input_arrival_location=intake.arrival_location,
            input_check_in_time=intake.check_in_time,
            vessel=str(ans_vessel.value) if ans_vessel.known and ans_vessel.value else None,
            departure_port=str(ans_dep_port.value) if ans_dep_port.known and ans_dep_port.value else None,
            arrival_port=str(ans_arr_port.value) if ans_arr_port.known and ans_arr_port.value else None,
            departure_date=str(ans_dep_date.value) if ans_dep_date.known and ans_dep_date.value else None,
            departure_location=str(ans_dep_loc.value) if ans_dep_loc.known and ans_dep_loc.value else None,
            arrival_date=str(ans_arr_date.value) if ans_arr_date.known and ans_arr_date.value else None,
            arrival_location=str(ans_arr_loc.value) if ans_arr_loc.known and ans_arr_loc.value else None,
            check_in_time=str(ans_checkin.value) if ans_checkin.known and ans_checkin.value else None,
            departure_terminal=None,
            departure_berth=None,
            arrival_terminal=None,
            arrival_berth=None,
            known_facts=known_facts,
            gaps=gaps,
            publishability=publishability,
            admission_decision=admission_decision,
            passenger_pack=passenger_pack,
        )
