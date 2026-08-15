"""
Knowledge Factory Stage 06/07: Automated Spatial Integrity & Quality Gate Validator.
Validates 100% of Quality Gates defined in CANON.md and SHIPBOOK.md.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from timonelo.ontology.models import VesselSpatialOntology
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.calculus.sandwich import DeterministicSandwichResolver


@dataclass
class ValidationReport:
    is_valid: bool
    total_decks_audited: int
    total_cabins_audited: int
    total_venues_audited: int
    orphaned_doors_count: int
    missing_evidence_count: int
    issues: List[str] = field(default_factory=list)
    quality_gates_passed: List[str] = field(default_factory=list)


class SpatialIntegrityValidator:
    """Automated validator enforcing mathematical purity across Planes 1–4."""

    @staticmethod
    def audit_vessel(ontology: VesselSpatialOntology) -> ValidationReport:
        issues: List[str] = []
        gates_passed: List[str] = []

        total_cabins = 0
        total_venues = 0
        orphaned_doors = 0
        missing_evidence = 0

        router = DeterministicSpatialRouter(ontology)
        sandwich_resolver = DeterministicSandwichResolver(ontology)

        # 1. Gate 1: Evidence & Provenance Audit
        for deck_num, deck in ontology.decks.items():
            total_venues += len(deck.venues)
            for cabin_num, cabin in deck.cabins.items():
                total_cabins += 1
                if not cabin.evidence_links:
                    issues.append(f"Cabin {cabin_num} on Deck {deck_num} has no linked evidence sources.")
                    missing_evidence += 1

        if missing_evidence == 0:
            gates_passed.append("GATE_1_PROVENANCE_SATISFIED")

        # 2. Gate 2: Corridor & Door Topology Graph Audit
        for deck_num, deck in ontology.decks.items():
            node_ids = set(deck.corridor_nodes.keys())
            for cabin_num, cabin in deck.cabins.items():
                if cabin.door.corridor_snap_node_id not in node_ids:
                    issues.append(f"Cabin {cabin_num} door snaps to non-existent node {cabin.door.corridor_snap_node_id}")
                    orphaned_doors += 1

        if orphaned_doors == 0:
            gates_passed.append("GATE_2_TOPOLOGY_ZERO_ORPHANS")

        # 3. Gate 3: Vertical Sandwich Resolver Audit
        sandwich_failures = 0
        for deck_num, deck in ontology.decks.items():
            for cabin_num in deck.cabins.keys():
                report = sandwich_resolver.resolve_cabin_sandwich(cabin_num)
                if not report:
                    issues.append(f"Cabin {cabin_num} failed vertical sandwich resolution.")
                    sandwich_failures += 1

        if sandwich_failures == 0:
            gates_passed.append("GATE_3_SANDWICH_INTEGRITY")

        # 4. Gate 4: Router Multi-Deck Wayfinding Audit
        routing_failures = 0
        for deck_num, deck in ontology.decks.items():
            for cabin_num, cabin in deck.cabins.items():
                # Test route to nearest elevator on deck
                nearest_lift = f"D{deck_num:02d}_AFT_LIFT"
                if nearest_lift in deck.corridor_nodes:
                    route = router.find_shortest_path(cabin.door.corridor_snap_node_id, nearest_lift)
                    if not route:
                        issues.append(f"Cabin {cabin_num} cannot route to on-deck elevator {nearest_lift}")
                        routing_failures += 1

        if routing_failures == 0:
            gates_passed.append("GATE_4_CIRCULATION_CONNECTED")

        is_valid = len(issues) == 0

        return ValidationReport(
            is_valid=is_valid,
            total_decks_audited=len(ontology.decks),
            total_cabins_audited=total_cabins,
            total_venues_audited=total_venues,
            orphaned_doors_count=orphaned_doors,
            missing_evidence_count=missing_evidence,
            issues=issues,
            quality_gates_passed=gates_passed,
        )
