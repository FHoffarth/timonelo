#!/usr/bin/env python3
"""
CLI Tool: Knowledge History & Lifecycle Timeline Dashboard.
Usage:
    python tools/knowledge_history_dashboard.py [--seed-history] [--timeline <entity_id>]
"""

import sys
import os
import json
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.history import (
    KnowledgeHistoryEngine,
    LifecycleEvent,
    LifecycleEventType,
)


def seed_canonical_history(engine: KnowledgeHistoryEngine):
    """Seed verified maritime lifecycle milestones and multi-revision claims."""
    # 1. MSC Bellissima Lifecycles
    engine.record_lifecycle_event(
        LifecycleEvent(
            event_id="life:bellissima:keel-laying",
            entity_id="ship:msc-bellissima",
            event_type=LifecycleEventType.KEEL_LAID,
            date="2016-11-15",
            title="Keel Laying at Saint-Nazaire",
            description="First 500-ton steel block placed in dry dock B at Chantiers de l'Atlantique (Hull H34).",
            location_or_yard="Chantiers de l'Atlantique (Saint-Nazaire, France)",
            source_id="src:chantiers-atlantique-h34",
        )
    )
    engine.record_lifecycle_event(
        LifecycleEvent(
            event_id="life:bellissima:float-out",
            entity_id="ship:msc-bellissima",
            event_type=LifecycleEventType.LAUNCHED,
            date="2018-06-14",
            title="Float Out & Basin Transfer",
            description="Drydock flooded and vessel shifted to Penhoët outfitting basin for interior completion.",
            location_or_yard="Saint-Nazaire, France",
            source_id="src:chantiers-atlantique-h34",
        )
    )
    engine.record_lifecycle_event(
        LifecycleEvent(
            event_id="life:bellissima:delivery",
            entity_id="ship:msc-bellissima",
            event_type=LifecycleEventType.DELIVERED,
            date="2019-02-27",
            title="Official Delivery & Flag Commissioning",
            description="Delivery ceremony with MSC Executive Chairman Pierfrancesco Vago; commissioned under Malta flag.",
            location_or_yard="Saint-Nazaire, France",
            source_id="src:imo-gisis",
        )
    )
    engine.record_lifecycle_event(
        LifecycleEvent(
            event_id="life:bellissima:starlink-retrofit",
            entity_id="ship:msc-bellissima",
            event_type=LifecycleEventType.REFIT,
            date="2023-09-15",
            title="Starlink High-Speed LEO Maritime Retrofit",
            description="Installation of flat-panel Starlink LEO antennas on mast platform for fleet-wide gigabit backhaul.",
            location_or_yard="Naples Drydock, Italy",
            source_id="src:msc-technical-bulletin",
            refit_code="REFIT-2023-LEO",
        )
    )

    # 2. Multi-Revision Fact Evolution for Cabin 14122 Lift Distance
    # Revision 1 (2019 Initial Spec from general arrangement sheet): 24.5m
    engine.record_claim_revision(
        entity_id="cabin:msc-bellissima:14122",
        field_path="distance_to_nearest_lift",
        value=24.5,
        unit="m",
        evidence_type="SHIPYARD_DRAWING",
        source_id="src:chantiers-atlantique-ga-plan-v1",
        confidence=0.90,
        valid_from="2019-02-27",
        reason_for_change="Initial GA plan measurement from cabin threshold to nearest vertical core.",
    )
    # Revision 2 (2022 CAD corridor recalculation): 24.7m
    engine.record_claim_revision(
        entity_id="cabin:msc-bellissima:14122",
        field_path="distance_to_nearest_lift",
        value=24.7,
        unit="m",
        evidence_type="FIELD_MEASUREMENT",
        source_id="src:corridor-routing-cad-v2",
        confidence=0.95,
        valid_from="2022-05-10",
        reason_for_change="Updated to reflect exact corner radius around service fire door frame 138.",
    )
    # Revision 3 (2026 Laser Metrology Field Audit): 24.6m
    engine.record_claim_revision(
        entity_id="cabin:msc-bellissima:14122",
        field_path="distance_to_nearest_lift",
        value=24.6,
        unit="m",
        evidence_type="FIELD_MEASUREMENT",
        source_id="src:laser-distance-audit-2026",
        confidence=0.99,
        valid_from="2026-08-16",
        reason_for_change="Direct onboard laser distance audit confirming center-to-center walking trajectory.",
        observation_context="Measured during October 2026 onboard validation run.",
    )


def main():
    parser = argparse.ArgumentParser(description="Knowledge History & Revision Dashboard")
    parser.add_argument("--seed-history", action="store_true", help="Seed representative lifecycles and revisions")
    parser.add_argument("--timeline", type=str, help="View revision timeline for specific entity/claim ID")
    args = parser.parse_args()

    history_file = os.path.join(REPO_ROOT, "data", "knowledge_history.json")
    engine = KnowledgeHistoryEngine(history_file)

    if args.seed_history or len(engine.claims) == 0:
        seed_canonical_history(engine)

    stats = engine.get_history_statistics()

    print("=========================================================")
    print("      TIMONELO KNOWLEDGE HISTORY & REVISION DASHBOARD    ")
    print("=========================================================")
    print(f"Total Active Claims:           {stats['total_active_claims']}")
    print(f"Total Immutable Revisions:     {stats['total_revisions_stored']}")
    print(f"Active Revisions:              {stats['active_revisions']}")
    print(f"Superseded Historical States:  {stats['superseded_revisions']}")
    print(f"Lifecycle Milestones Tracked:  {stats['lifecycle_events_tracked']}")
    print(f"Downstream Impacts Logged:     {stats['downstream_impacts_detected']}")
    print(f"Oldest Provenance Milestone:   {stats['oldest_verified_fact']}")
    print(f"Newest Active Revision:        {stats['newest_verified_fact']}")
    print("---------------------------------------------------------")
    print("Sample Fact Evolution (Cabin 14122 Lift Distance):")
    sample_claim = engine.claims.get("claim:cabin:msc-bellissima:14122:distance_to_nearest_lift")
    if sample_claim:
        for rev in sample_claim.revisions:
            status_tag = f"[{rev.status.value}]"
            print(f"  * v{rev.revision_number} ({rev.valid_from} -> {rev.valid_until or 'Current'}): {rev.value}{rev.unit or ''} {status_tag}")
            print(f"      Source   : {rev.source_id} ({rev.evidence_type}, {rev.confidence * 100:.0f}%)")
            print(f"      Rationale: {rev.reason_for_change}")
    print("---------------------------------------------------------")
    print("Sample Downstream Impact Report:")
    for imp in engine.downstream_impacts[:2]:
        print(f"  [IMPACT] {imp.entity_id} -> {imp.field_changed} ({imp.old_value} -> {imp.new_value})")
        print(f"      Severity : {imp.impact_severity}")
        print(f"      Domains  : {', '.join(imp.affected_domains)}")
        print(f"      Rationale: {imp.rationale}")
    print("=========================================================")


if __name__ == "__main__":
    main()
