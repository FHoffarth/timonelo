/**
 * knowledge/pipeline/ConflictResolver.ts
 *
 * Prevents silent overwrites of canonical knowledge.
 * Classifies contradictions as MATCH, CONFLICT, UNKNOWN, or SUPERSEDED.
 *
 * Epistemic Governance Rules (ADR-0002):
 * - Conflicts CANNOT auto-resolve solely by confidence comparison.
 * - Bridge Officer Tim is an orchestrator, NOT an approving truth authority.
 * - Resolution requires verified physical evidence or explicit curator approval.
 */

import { FieldDiff } from "./KnowledgeDiff";

export type ResolutionStatus = "MATCH" | "CONFLICT" | "UNKNOWN" | "SUPERSEDED";

export interface ConflictDecision {
  conflict_id: string;
  entity_id: string;
  field_name: string;
  status: ResolutionStatus;
  canonical_value: any;
  incoming_value: any;
  canonical_artifact: string;
  incoming_artifact: string;
  evidence_page: number;
  publisher: string;
  edition: string;
  statement_id: string;
  resolution_rationale: string;
  curator_reviewed: boolean;
  reviewed_by?: string;
  resolved_at?: string;
}

export class ConflictResolver {
  private static pendingConflicts: ConflictDecision[] = [
    {
      conflict_id: "CONF-001",
      entity_id: "technical.json:max_passengers",
      field_name: "max_passenger_capacity",
      status: "SUPERSEDED",
      canonical_value: 5686,
      incoming_value: 5654,
      canonical_artifact: "Pre-Refit Legacy Specs",
      incoming_artifact: "MSC Bellissima Official Deck Plans 11/2025 DEU",
      evidence_page: 2,
      publisher: "MSC Cruises S.A.",
      edition: "11.2025",
      statement_id: "STM-BEL-TECH-001",
      resolution_rationale: "Official 11/2025 Deck Plan specifies exactly 5.654 passengers across 2.217 staterooms, superseding legacy shipyard theoretical max.",
      curator_reviewed: true,
      reviewed_by: "Knowledge Curator (Evidence Audit)",
      resolved_at: "2026-08-17T20:45:00Z",
    },
    {
      conflict_id: "CONF-002",
      entity_id: "bars.json:BAR-EDGE",
      field_name: "deck_location",
      status: "SUPERSEDED",
      canonical_value: "Deck 7",
      incoming_value: "Deck 6",
      canonical_artifact: "Legacy Venues Index",
      incoming_artifact: "MSC Bellissima Official Deck Plans 11/2025 DEU",
      evidence_page: 3,
      publisher: "MSC Cruises S.A.",
      edition: "11.2025",
      statement_id: "STM-BEL-BAR-002",
      resolution_rationale: "Deck 6 Musica floor plan explicitly labels Edge Cocktail Bar at Midship Atrium level.",
      curator_reviewed: true,
      reviewed_by: "Knowledge Curator (Evidence Audit)",
      resolved_at: "2026-08-17T20:50:00Z",
    },
    {
      conflict_id: "CONF-003",
      entity_id: "restaurants.json:RES-HOLA",
      field_name: "title",
      status: "SUPERSEDED",
      canonical_value: "HOLA! Tacos & Cantina",
      incoming_value: "HOLA! Tapas Bar",
      canonical_artifact: "Fleet Default Naming",
      incoming_artifact: "MSC Bellissima Official Deck Plans 11/2025 DEU",
      evidence_page: 3,
      publisher: "MSC Cruises S.A.",
      edition: "11.2025",
      statement_id: "STM-BEL-RES-003",
      resolution_rationale: "Official Deck 6 floor plan shows HOLA! Tapas Bar by Ramón Freixa on Bellissima.",
      curator_reviewed: true,
      reviewed_by: "Knowledge Curator (Evidence Audit)",
      resolved_at: "2026-08-17T20:55:00Z",
    },
  ];

  public static getConflicts(): ConflictDecision[] {
    return [...this.pendingConflicts];
  }

  public static classifyDiff(
    diff: FieldDiff,
    publisher: string = "MSC Cruises S.A.",
    edition: string = "11.2025",
    asOf: string = "2026-08-18T00:00:00Z"
  ): ConflictDecision {
    let status: ResolutionStatus = "CONFLICT";
    let rationale = "";

    if (JSON.stringify(diff.old_value) === JSON.stringify(diff.new_value)) {
      status = "MATCH";
      rationale = "Exact agreement with canonical ground truth.";
    } else if (diff.old_value === undefined || diff.old_value === null) {
      status = "SUPERSEDED";
      rationale = "New factual knowledge established from official primary evidence.";
    } else {
      // Direct conflict: must NOT be auto-superseded merely by confidence numbers
      status = "CONFLICT";
      rationale = `Contradiction detected between active canonical dataset (${diff.old_provenance || "Canonical Ground Truth"}) and incoming artifact (${diff.new_provenance}). Requires verified evidence audit.`;
    }

    const decision: ConflictDecision = {
      conflict_id: `CONF-${String(this.pendingConflicts.length + 1).padStart(3, "0")}`,
      entity_id: `${diff.entity_id}:${diff.field_name}`,
      field_name: diff.field_name,
      status: status,
      canonical_value: diff.old_value,
      incoming_value: diff.new_value,
      canonical_artifact: diff.old_provenance || "Canonical Knowledge Layer",
      incoming_artifact: diff.new_provenance,
      evidence_page: diff.evidence_page,
      publisher: publisher,
      edition: edition,
      statement_id: `STM-${diff.entity_id.toUpperCase()}`,
      resolution_rationale: rationale,
      curator_reviewed: status === "MATCH",
      reviewed_by: undefined,
      resolved_at: status === "MATCH" ? asOf : undefined,
    };

    this.pendingConflicts.unshift(decision);
    return decision;
  }

  public static resolveConflictWithEvidence(
    conflictId: string,
    curatorName: string,
    rationale: string,
    resolvedAt: string = "2026-08-18T00:00:00Z"
  ): boolean {
    const item = this.pendingConflicts.find((c) => c.conflict_id === conflictId);
    if (item) {
      item.curator_reviewed = true;
      item.reviewed_by = curatorName;
      item.status = "SUPERSEDED";
      item.resolution_rationale = rationale;
      item.resolved_at = resolvedAt;
      return true;
    }
    return false;
  }
}
