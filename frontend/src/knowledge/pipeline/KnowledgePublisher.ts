/**
 * knowledge/pipeline/KnowledgePublisher.ts
 * 
 * Pipeline Stage: Canonical Knowledge Release Gatekeeper.
 * Enforces 4-stage validation (Schema, Graph, Geometry, Integrity) before publication.
 */

export interface ValidationGateResult {
  gate_name: string;
  passed: boolean;
  status: "PASSED" | "FAILED" | "WARNING";
  details: string;
  checked_items_count: number;
}

export interface PublishReleaseReport {
  release_id: string;
  target_vessel_id: string;
  version: string;
  published_by: string;
  published_at: string;
  gates: ValidationGateResult[];
  all_gates_passed: boolean;
  published_entities_count: number;
  published_geometry_files_count: number;
}

export class LegacyPublisherQuarantinedError extends Error {
  constructor() {
    super("Legacy KnowledgePublisher is quarantined and cannot publish passenger assets");
    this.name = "LegacyPublisherQuarantinedError";
  }
}

export class KnowledgePublisher {
  public static validateAndPublish(
    _vesselId: string,
    _version: string = "2026.11.0",
    _officerName: string = "Bridge Officer Tim"
  ): PublishReleaseReport {
    throw new LegacyPublisherQuarantinedError();
  }
}
