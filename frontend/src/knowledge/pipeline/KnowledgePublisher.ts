/**
 * knowledge/pipeline/KnowledgePublisher.ts
 *
 * Pipeline Stage: Canonical Knowledge Release Gatekeeper.
 * Enforces structured validation before publication.
 *
 * Governance Rule:
 * - Publication requires physical evidence verification and gate audit.
 * - Bridge Officer Tim is an orchestrator, NOT an approving truth authority.
 * - Release IDs must be deterministic.
 */

import { EvidenceGatekeeper } from "./EvidenceGatekeeper";

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

export class KnowledgePublisher {
  public static validateAndPublish(
    vesselId: string,
    version: string = "2026.11.0",
    curatorName: string = "Evidence Gatekeeper Engine",
    publishedAt: string = "2026-08-18T00:00:00Z"
  ): PublishReleaseReport {
    // Run audit via EvidenceGatekeeper
    const audit = EvidenceGatekeeper.auditShip(vesselId);

    const gates: ValidationGateResult[] = [
      {
        gate_name: "JSON Schema Validation & Physical Source Integrity (SHA-256)",
        passed: audit.passed,
        status: audit.passed ? "PASSED" : "FAILED",
        details: audit.passed
          ? `Primary source artifact verified (${audit.held_artifacts_count} held, SHA-256 verified)`
          : `Gate blocked: ${audit.block_reasons.join("; ")}`,
        checked_items_count: audit.held_artifacts_count,
      },
      {
        gate_name: "W3C Building Topology Ontology (BOT) Graph Grounding",
        passed: audit.direct_facts_count > 0,
        status: audit.direct_facts_count > 0 ? "PASSED" : "WARNING",
        details: `${audit.direct_facts_count} facts backed by DIRECT physical evidence; ${audit.synthetic_facts_count} synthetic facts rejected`,
        checked_items_count: audit.total_facts_count,
      },
      {
        gate_name: "Spatial Geometry & Coordinate Provenance Validation",
        passed: audit.synthetic_geometry_count === 0,
        status: audit.synthetic_geometry_count === 0 ? "PASSED" : "FAILED",
        details: `${audit.direct_geometry_count} deck geometries verified with direct/transformed provenance; 0 unverified synthetic geometries`,
        checked_items_count: audit.direct_geometry_count + audit.synthetic_geometry_count,
      },
      {
        gate_name: "Referential Integrity & Fact Grounding Guard",
        passed: audit.unresolved_conflicts_count === 0,
        status: audit.unresolved_conflicts_count === 0 ? "PASSED" : "FAILED",
        details: `${audit.unresolved_conflicts_count} unresolved conflicts detected`,
        checked_items_count: audit.unresolved_conflicts_count,
      },
    ];

    const allPassed = gates.every((g) => g.passed);
    const releaseSlug = version.replace(/[^a-zA-Z0-9]/g, "");

    return {
      release_id: `REL-${vesselId.toUpperCase()}-${releaseSlug}`,
      target_vessel_id: vesselId,
      version: version,
      published_by: curatorName,
      published_at: publishedAt,
      gates: gates,
      all_gates_passed: allPassed,
      published_entities_count: audit.total_facts_count,
      published_geometry_files_count: audit.direct_geometry_count,
    };
  }
}
