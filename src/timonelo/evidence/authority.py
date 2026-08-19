"""
Statement Authority Matrix.

Governed by ADR-0002 §6, §7, §13. This is not a new provenance model: it is
content plus a runtime check for the mechanism already present in
EvidenceEventLog.append() and Question.supportable_by.

THREE PROPERTIES ARE DELIBERATELY KEPT SEPARATE.

  1. EPISTEMIC AUTHORITY — can this document class establish this fact at all?
  2. ACQUISITION STATUS  — can we obtain a copy?
  3. USE PERMISSION      — may we store and publish from it?

Collapsing them is the trap. A shipyard general arrangement is the highest
epistemic authority for cabin geometry AND the most restricted document in the
set. If those live in one field, either restriction silently reads as
unreliability, or a document we may not use reads as authoritative. Both are
wrong, and the second is the more dangerous.

A FOURTH property, validity scope, is the one the taxonomy omits and the one
that will bite first. A Daily Programme genuinely supports buffet opening
hours — for one sailing day. Without a declared scope, an observation from a
March 2024 programme would support that claim forever. That is the same defect
as a decorative hash, displaced into time.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Optional, Tuple


class ValidityScope(str, Enum):
    """How long an observation from this class remains a statement."""
    STRUCTURAL = "STRUCTURAL"      # until the hull is modified; survives refits mostly
    REFIT_SCOPED = "REFIT_SCOPED"  # valid until the next refit
    SEASON_SCOPED = "SEASON_SCOPED"  # valid for a deployment season
    SAILING_SCOPED = "SAILING_SCOPED"  # valid for one voyage
    DAY_SCOPED = "DAY_SCOPED"      # valid for one day
    POINT_IN_TIME = "POINT_IN_TIME"  # an event that occurred; never expires, never generalises


class Acquisition(str, Enum):
    """Whether we can obtain a copy. Independent of authority."""
    PUBLIC = "PUBLIC"              # downloadable
    REQUESTABLE = "REQUESTABLE"    # obtainable by asking, with effort
    RESTRICTED = "RESTRICTED"      # requires a commercial or legal relationship
    ONBOARD_ONLY = "ONBOARD_ONLY"  # exists only physically aboard; requires a survey


class UsePermission(str, Enum):
    """What we may do with it. Facts extracted are generally not protectable;
    the artifact itself generally is."""
    CITE_AND_STORE = "CITE_AND_STORE"      # may retain the bytes
    CITE_ONLY = "CITE_ONLY"                # may reference, may not redistribute
    INTERNAL_ONLY = "INTERNAL_ONLY"        # may inform statements, never surfaced
    LEGAL_REVIEW_REQUIRED = "LEGAL_REVIEW_REQUIRED"


@dataclass(frozen=True)
class DocumentClass:
    class_id: str
    label: str
    reliability: float           # DIRECT confidence ceiling (ADR-0002 §7)
    validity_scope: ValidityScope
    acquisition: Acquisition
    use_permission: UsePermission
    notes: str = ""


# ---------------------------------------------------------------------------
# Document classes.
#
# Reliability is capped at 0.97 throughout: 1.0 is reserved for tautologies
# (ADR-0002 §7.2). Values are our declared trust in the class, not a measured
# error rate, and should be revised when a conflict proves one wrong.
# ---------------------------------------------------------------------------

DOCUMENT_CLASSES: Dict[str, DocumentClass] = {
    "shipyard_general_arrangement": DocumentClass(
        "shipyard_general_arrangement", "Shipyard General Arrangement drawing",
        reliability=0.97, validity_scope=ValidityScope.STRUCTURAL,
        acquisition=Acquisition.RESTRICTED,
        use_permission=UsePermission.LEGAL_REVIEW_REQUIRED,
        notes="Dimensioned. The only class that can establish areas and structure.",
    ),
    "builder_specification": DocumentClass(
        "builder_specification", "Builder specification",
        reliability=0.95, validity_scope=ValidityScope.STRUCTURAL,
        acquisition=Acquisition.RESTRICTED,
        use_permission=UsePermission.LEGAL_REVIEW_REQUIRED,
    ),
    "classification_society_record": DocumentClass(
        "classification_society_record", "Classification society record",
        reliability=0.95, validity_scope=ValidityScope.REFIT_SCOPED,
        acquisition=Acquisition.REQUESTABLE,
        use_permission=UsePermission.CITE_ONLY,
    ),
    "accessibility_guide": DocumentClass(
        "accessibility_guide", "Operator accessibility guide",
        reliability=0.90, validity_scope=ValidityScope.REFIT_SCOPED,
        acquisition=Acquisition.PUBLIC,
        use_permission=UsePermission.CITE_AND_STORE,
        notes="Operator-published; dimensioned for accessible cabins only.",
    ),
    "onboard_survey": DocumentClass(
        "onboard_survey", "First-party onboard survey",
        reliability=0.90, validity_scope=ValidityScope.REFIT_SCOPED,
        acquisition=Acquisition.ONBOARD_ONLY,
        use_permission=UsePermission.CITE_AND_STORE,
        notes="Our own measurement. Requires being aboard; not remotely obtainable.",
    ),
    "solas_placard": DocumentClass(
        "solas_placard", "SOLAS door placard / muster card",
        reliability=0.95, validity_scope=ValidityScope.SAILING_SCOPED,
        acquisition=Acquisition.ONBOARD_ONLY,
        use_permission=UsePermission.INTERNAL_ONLY,
        notes=(
            "Authoritative for muster assignment, but assignment is per-sailing "
            "and per-booking. Photographed aboard; cannot be acquired remotely. "
            "INTERNAL_ONLY: see AUTHORITY note on safety statements below."
        ),
    ),
    "cruise_line_deck_plan": DocumentClass(
        "cruise_line_deck_plan", "Operator deck plan",
        reliability=0.80, validity_scope=ValidityScope.REFIT_SCOPED,
        acquisition=Acquisition.PUBLIC,
        use_permission=UsePermission.CITE_ONLY,
        notes="Schematic, undated, not dimensioned. Topology yes, geometry no.",
    ),
    "daily_programme": DocumentClass(
        "daily_programme", "Daily programme",
        reliability=0.90, validity_scope=ValidityScope.DAY_SCOPED,
        acquisition=Acquisition.ONBOARD_ONLY,
        use_permission=UsePermission.CITE_AND_STORE,
        notes="High reliability, one-day validity. Never generalises to a schedule.",
    ),
    "port_state_inspection": DocumentClass(
        "port_state_inspection", "Port state control inspection report",
        reliability=0.95, validity_scope=ValidityScope.POINT_IN_TIME,
        acquisition=Acquisition.PUBLIC,
        use_permission=UsePermission.INTERNAL_ONLY,
        notes=(
            "Factually reliable about a past inspection. INTERNAL_ONLY: a "
            "closed deficiency from 2019 rendered on a cabin page is accurate "
            "and misleading at once. Surfacing requires product and legal "
            "decisions not yet taken."
        ),
    ),
    "cruise_line_marketing": DocumentClass(
        "cruise_line_marketing", "Operator marketing material",
        reliability=0.55, validity_scope=ValidityScope.SEASON_SCOPED,
        acquisition=Acquisition.PUBLIC,
        use_permission=UsePermission.CITE_ONLY,
    ),
}


# ---------------------------------------------------------------------------
# The matrix: statement type -> document classes with authority over it.
#
# Absence is not permission. A statement type not listed here has NO
# authoritative class and cannot be evidenced at all.
# ---------------------------------------------------------------------------

AUTHORITY: Dict[str, Tuple[str, ...]] = {
    # -- topology: what is where. Deck plans suffice.
    "cabin.deck":                 ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.hull_side":            ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.category":             ("cruise_line_deck_plan", "cruise_line_marketing", "shipyard_general_arrangement"),
    "cabin.corridor_position":    ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.connecting_cabin":     ("cruise_line_deck_plan", "shipyard_general_arrangement"),
    "cabin.nearest_lift":         ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),
    "deck.venue_present":         ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),
    "deck.venue_position":        ("cruise_line_deck_plan", "shipyard_general_arrangement"),

    # -- vessel overview: capacity and stateroom counts from operator deck plans / specifications
    "vessel.total_cabins":        ("cruise_line_deck_plan", "builder_specification", "classification_society_record"),
    "vessel.passenger_capacity_max": ("cruise_line_deck_plan", "builder_specification", "classification_society_record"),

    # -- cabin features: bed arrangement explicitly stated on deck plans / surveys
    "cabin.bed_configuration":    ("cruise_line_deck_plan", "shipyard_general_arrangement", "onboard_survey"),

    # -- geometry: dimensioned quantities. Deck plans are NOT authoritative.
    "cabin.area_sqm":             ("shipyard_general_arrangement", "builder_specification"),
    "cabin.wall_composition":     ("shipyard_general_arrangement", "builder_specification"),
    "cabin.service_void":         ("shipyard_general_arrangement", "builder_specification"),
    "cabin.hvac_riser":           ("shipyard_general_arrangement", "builder_specification"),
    "cabin.structural_adjacency": ("shipyard_general_arrangement", "builder_specification"),

    # -- accessibility: dimensioned, but an operator guide is authoritative.
    "cabin.door_clear_width_mm":  ("accessibility_guide", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.bathroom_layout":      ("accessibility_guide", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.turning_radius_mm":    ("accessibility_guide", "shipyard_general_arrangement", "onboard_survey"),
    "cabin.accessibility_equipment": ("accessibility_guide", "onboard_survey"),

    # -- safety: authoritative class exists, but see SAFETY_STATEMENTS below.
    "cabin.muster_station":       ("solas_placard",),
    "cabin.escape_direction":     ("solas_placard", "shipyard_general_arrangement"),

    # -- operations: day-scoped, never generalised.
    "venue.opening_hours":        ("daily_programme",),
    "venue.activity":             ("daily_programme",),
    "venue.theatre_schedule":     ("daily_programme",),

    # -- vessel history: internal only.
    "vessel.inspection_finding":  ("port_state_inspection",),
}


# Statement types that must never be rendered to a passenger even when
# evidenced, because being right is not sufficient for them to be safe.
SAFETY_STATEMENTS: FrozenSet[str] = frozenset({
    "cabin.muster_station",
    "cabin.escape_direction",
})


class AuthorityError(ValueError):
    """Raised when a document class has no authority over a statement type."""


def reliability_of(class_id: str) -> float:
    if class_id not in DOCUMENT_CLASSES:
        raise AuthorityError(
            f"Unregistered document class {class_id!r}. Declare it in "
            "DOCUMENT_CLASSES before using it as evidence."
        )
    return DOCUMENT_CLASSES[class_id].reliability


def authoritative_classes(statement_type: str) -> Tuple[str, ...]:
    if statement_type not in AUTHORITY:
        raise AuthorityError(
            f"No authority declared for statement type {statement_type!r}. "
            "Absence is not permission: a statement type with no authoritative "
            "class cannot be evidenced."
        )
    return AUTHORITY[statement_type]


def check(statement_type: str, class_id: str) -> None:
    """Raise unless this class may create this statement type."""
    allowed = authoritative_classes(statement_type)
    if class_id not in allowed:
        cls = DOCUMENT_CLASSES.get(class_id)
        label = cls.label if cls else class_id
        raise AuthorityError(
            f"{label} has no authority over {statement_type!r}. "
            f"Authoritative classes: {', '.join(allowed)}."
        )


def is_publishable(statement_type: str, class_id: str) -> Tuple[bool, Optional[str]]:
    """Whether a statement may reach a passenger. Separate from authority."""
    if statement_type in SAFETY_STATEMENTS:
        return False, (
            "Safety statements are not rendered even when evidenced. A muster "
            "assignment is per-sailing and per-booking; a stale one displaces "
            "the passenger's check of their own cabin card."
        )
    cls = DOCUMENT_CLASSES[class_id]
    if cls.use_permission is UsePermission.INTERNAL_ONLY:
        return False, f"{cls.label} is INTERNAL_ONLY: {cls.notes}"
    if cls.use_permission is UsePermission.LEGAL_REVIEW_REQUIRED:
        return False, f"{cls.label} requires legal review before publication."
    return True, None


def scope_of(class_id: str) -> ValidityScope:
    return DOCUMENT_CLASSES[class_id].validity_scope


# ---------------------------------------------------------------------------
# Workspace-declared classes.
#
# The matrix above is the curated default. A curator may declare additional
# document classes and statement authorities in the workspace without editing
# source — but only by declaring reliability, validity scope, acquisition and
# use permission explicitly. There is no way to add a class without stating
# what it is trusted for.
# ---------------------------------------------------------------------------

# Snapshot of the classes declared in this module. Only these are protected
# from workspace redefinition; workspace-loaded classes may be re-loaded freely,
# which makes opening the same workspace twice in one process a no-op rather
# than an error.
CURATED_CLASS_IDS: FrozenSet[str] = frozenset(DOCUMENT_CLASSES)


def load_workspace_classes(path: str) -> int:
    """Merge classes and authorities declared in a workspace file.

    Returns the number of classes loaded. Never silently overrides a curated
    class: a workspace file may add, not redefine.
    """
    import json
    import os

    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    loaded = 0
    for cid, d in sorted(raw.get("document_classes", {}).items()):
        if cid in CURATED_CLASS_IDS:
            raise AuthorityError(
                f"Workspace file redefines curated document class {cid!r}. "
                "Workspace declarations may add classes, not override them."
            )
        DOCUMENT_CLASSES[cid] = DocumentClass(
            class_id=cid,
            label=d["label"],
            reliability=float(d["reliability"]),
            validity_scope=ValidityScope(d["validity_scope"]),
            acquisition=Acquisition(d["acquisition"]),
            use_permission=UsePermission(d["use_permission"]),
            notes=d.get("notes", ""),
        )
        if not 0.0 < DOCUMENT_CLASSES[cid].reliability < 1.0:
            raise AuthorityError(
                f"{cid!r}: reliability must be above 0 and below 1. "
                "1.0 is reserved for tautologies (ADR-0002 §7.2)."
            )
        loaded += 1

    for stype, classes in sorted(raw.get("authority", {}).items()):
        unknown = [c for c in classes if c not in DOCUMENT_CLASSES]
        if unknown:
            raise AuthorityError(
                f"Statement type {stype!r} grants authority to undeclared "
                f"class(es) {unknown}."
            )
        AUTHORITY[stype] = tuple(classes)
    return loaded
