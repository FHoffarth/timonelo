/**
 * knowledge/pipeline/KnowledgeFactory.ts
 * 
 * End-to-end orchestrator for automated maritime knowledge production.
 * Manages the transition from raw artifact evidence to canonical graph & geometry.
 */

import { ArtifactQueueManager } from "./ArtifactQueue";
import { ConflictResolver } from "./ConflictResolver";
import type { PublishReleaseReport } from "./KnowledgePublisher";

export interface ShipProductionStatus {
  vessel_id: string;
  name: string;
  ship_class: string;
  total_cabins: number;
  total_venues: number;
  passenger_decks: number;
  status: "PRODUCTION_READY" | "IN_QUEUE" | "PARSING" | "AUDIT_REQUIRED";
  knowledge_coverage_pct: number;
  schema_coverage_pct: number;
  graph_coverage_pct: number;
  geometry_coverage_pct: number;
  primary_artifact: string;
}

export interface FactoryMetrics {
  artifacts_waiting: number;
  active_conflicts: number;
  ships_ready_count: number;
  total_ships_count: number;
  ports_ready_count: number;
  routes_ready_count: number;
  global_knowledge_coverage: number;
  global_schema_coverage: number;
  global_graph_coverage: number;
  global_geometry_coverage: number;
  ships: ShipProductionStatus[];
}

export class KnowledgeFactory {
  public static getFactoryMetrics(): FactoryMetrics {
    const queue = ArtifactQueueManager.getQueue();
    const conflicts = ConflictResolver.getConflicts();

    const waitingArtifacts = queue.filter((q) => q.stage !== "PUBLISHED").length;
    const unresolvedConflicts = conflicts.filter((c) => !c.officer_approved).length;

    const ships: ShipProductionStatus[] = [
      {
        vessel_id: "msc-bellissima",
        name: "MSC Bellissima",
        ship_class: "Meraviglia-Class",
        total_cabins: 2217,
        total_venues: 38,
        passenger_decks: 15,
        status: "PRODUCTION_READY",
        knowledge_coverage_pct: 100,
        schema_coverage_pct: 100,
        graph_coverage_pct: 100,
        geometry_coverage_pct: 100,
        primary_artifact: "MSC Bellissima Deck Plan (11.2025 DEU)",
      },
      {
        vessel_id: "ms-andorinha",
        name: "MS Andorinha",
        ship_class: "Douro River Custom",
        total_cabins: 42,
        total_venues: 6,
        passenger_decks: 4,
        status: "PRODUCTION_READY",
        knowledge_coverage_pct: 100,
        schema_coverage_pct: 100,
        graph_coverage_pct: 100,
        geometry_coverage_pct: 100,
        primary_artifact: "MS Andorinha Douro GA Blueprint",
      },
      {
        vessel_id: "msc-grandiosa",
        name: "MSC Grandiosa",
        ship_class: "Meraviglia-Plus-Class",
        total_cabins: 2421,
        total_venues: 44,
        passenger_decks: 16,
        status: "IN_QUEUE",
        knowledge_coverage_pct: 85,
        schema_coverage_pct: 100,
        graph_coverage_pct: 80,
        geometry_coverage_pct: 75,
        primary_artifact: "MSC Grandiosa Deck Plan (03.2026 DEU)",
      },
      {
        vessel_id: "msc-meraviglia",
        name: "MSC Meraviglia",
        ship_class: "Meraviglia-Class",
        total_cabins: 2244,
        total_venues: 36,
        passenger_decks: 15,
        status: "IN_QUEUE",
        knowledge_coverage_pct: 80,
        schema_coverage_pct: 100,
        graph_coverage_pct: 75,
        geometry_coverage_pct: 70,
        primary_artifact: "MSC Meraviglia General Arrangement",
      },
    ];

    const readyShips = ships.filter((s) => s.status === "PRODUCTION_READY").length;

    return {
      artifacts_waiting: waitingArtifacts,
      active_conflicts: unresolvedConflicts,
      ships_ready_count: readyShips,
      total_ships_count: ships.length,
      ports_ready_count: 12,
      routes_ready_count: 4,
      global_knowledge_coverage: 95.8,
      global_schema_coverage: 100.0,
      global_graph_coverage: 94.2,
      global_geometry_coverage: 92.5,
      ships,
    };
  }

  public static executeIngestionPipeline(
    queueId: string,
    _officerName: string = "Bridge Officer Tim"
  ): { success: boolean; release?: PublishReleaseReport; message: string } {
    const queue = ArtifactQueueManager.getQueue();
    const item = queue.find((q) => q.queue_id === queueId);

    if (!item) {
      return { success: false, message: `Artifact ${queueId} not found in pipeline queue.` };
    }

    return {
      success: false,
      message: `Legacy ingestion for ${item.evidence.target_vessel_id} is quarantined; no publication was attempted.`,
    };
  }
}
