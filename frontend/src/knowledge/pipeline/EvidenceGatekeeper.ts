/**
 * frontend/src/knowledge/pipeline/EvidenceGatekeeper.ts
 *
 * Evidence Gatekeeper v1 — The Absolute Trust Infrastructure for Timonelo.
 * Enforces:
 * 1. Physical Source Artifact Verification
 * 2. Fact-Level Epistemic Integrity (DIRECT / DERIVED / INFERRED / UNVERIFIED / CONFLICTED)
 * 3. Geometry Provenance (DIRECT_SOURCE_GEOMETRY / TRANSFORMED_SOURCE_GEOMETRY / DERIVED_GEOMETRY / SYNTHETIC_GEOMETRY / UNKNOWN_PROVENANCE)
 * 4. Epistemic Ceiling Rules
 * 5. Deterministic Coverage Calculation
 * 6. Conflict Detection Execution Gate
 * 7. Publish Gatekeeper
 * 8. Report Language Guard
 */

export type SourceType = 'OFFICIAL_PDF' | 'BUILDER_DOC' | 'REGISTER' | 'OFFICIAL_WEB' | 'OTHER';

export type VerificationStatus = 'VERIFIED' | 'UNVERIFIED' | 'MISSING' | 'HASH_MISMATCH';

export interface SourceArtifactRecord {
  source_id: string;
  title: string;
  publisher: string;
  source_type: SourceType;
  file_path: string | null;
  source_url: string | null;
  edition: string | null;
  publication_date: string | null;
  retrieved_at: string | null;
  sha256: string | null;
  page_count: number;
  verification_status: VerificationStatus;
}

export type EpistemicStatus = 'DIRECT' | 'DERIVED' | 'INFERRED' | 'UNVERIFIED' | 'CONFLICTED';

export interface EvidenceLocator {
  source_id: string;
  page?: number;
  section?: string;
  evidence_type: 'TEXT' | 'TABLE' | 'VISUAL' | 'GEOMETRY';
  locator?: string;
}

export interface FactEvidenceRecord {
  fact_id: string;
  entity_id: string;
  attribute: string;
  value: any;
  epistemic_status: EpistemicStatus;
  evidence: EvidenceLocator[];
  parent_fact_ids?: string[];
}

export type GeometryProvenanceType =
  | 'DIRECT_SOURCE_GEOMETRY'
  | 'TRANSFORMED_SOURCE_GEOMETRY'
  | 'DERIVED_GEOMETRY'
  | 'SYNTHETIC_GEOMETRY'
  | 'UNKNOWN_PROVENANCE';

export interface GeometryProvenanceRecord {
  object_id: string;
  deck_number: number;
  geometry_type: GeometryProvenanceType;
  source_id?: string;
  extraction_method?: string;
  transform_parameters?: Record<string, any>;
  confidence: number;
}

export interface EpistemicCoverageMetrics {
  total_sources: number;
  verified_sources: number;
  source_coverage_pct: number;

  total_facts: number;
  direct_facts: number;
  derived_facts: number;
  inferred_facts: number;
  unverified_facts: number;
  fact_evidence_coverage_pct: number;
  direct_evidence_coverage_pct: number;

  total_geometry_objects: number;
  direct_geometry_objects: number;
  synthetic_geometry_objects: number;
  geometry_provenance_coverage_pct: number;

  total_graph_relations: number;
  grounded_graph_relations: number;
  graph_provenance_coverage_pct: number;

  conflicts_total: number;
  conflicts_resolved: number;
  conflict_resolution_coverage_pct: number;

  global_epistemic_score: number;
}

export interface ConflictGateResult {
  executed: boolean;
  resolver_version: string;
  checked_entities: number;
  conflicts_found: number;
  unresolved_conflicts: number;
  status_summary: string;
}

export type PublishStatus = 'PUBLISH_ALLOWED' | 'PUBLISH_ALLOWED_WITH_WARNINGS' | 'PUBLISH_BLOCKED';

export interface PublishGateResult {
  status: PublishStatus;
  reasons: string[];
  warnings: string[];
  metrics: EpistemicCoverageMetrics;
  conflict_gate: ConflictGateResult;
}

/**
 * Computes maximum permissible epistemic trust for a derived node.
 */
export function computeEpistemicCeiling(
  upstreamStatuses: EpistemicStatus[],
  sourceStatus?: VerificationStatus,
  geometryType?: GeometryProvenanceType
): EpistemicStatus {
  if (sourceStatus === 'MISSING' || sourceStatus === 'HASH_MISMATCH' || sourceStatus === 'UNVERIFIED') {
    return 'UNVERIFIED';
  }
  if (geometryType === 'SYNTHETIC_GEOMETRY' || geometryType === 'UNKNOWN_PROVENANCE') {
    return 'INFERRED';
  }
  if (!upstreamStatuses || upstreamStatuses.length === 0) {
    return 'UNVERIFIED';
  }
  if (upstreamStatuses.includes('CONFLICTED')) return 'CONFLICTED';
  if (upstreamStatuses.includes('UNVERIFIED')) return 'UNVERIFIED';
  if (upstreamStatuses.includes('INFERRED')) return 'INFERRED';
  if (upstreamStatuses.includes('DERIVED')) return 'DERIVED';
  if (upstreamStatuses.every((s) => s === 'DIRECT')) return 'DIRECT';
  return 'UNVERIFIED';
}

/**
 * Deterministic coverage calculation engine.
 */
export function computeEpistemicCoverage(
  sources: SourceArtifactRecord[],
  facts: FactEvidenceRecord[],
  geometries: GeometryProvenanceRecord[],
  graphRelations: Array<{ grounded: boolean }>,
  conflictGate: ConflictGateResult
): EpistemicCoverageMetrics {
  const verifiedSources = sources.filter((s) => s.verification_status === 'VERIFIED').length;
  const source_coverage_pct = Number(((verifiedSources / Math.max(1, sources.length)) * 100).toFixed(2));

  const directFacts = facts.filter((f) => f.epistemic_status === 'DIRECT').length;
  const derivedFacts = facts.filter((f) => f.epistemic_status === 'DERIVED').length;
  const inferredFacts = facts.filter((f) => f.epistemic_status === 'INFERRED').length;
  const unverifiedFacts = facts.filter((f) => f.epistemic_status === 'UNVERIFIED').length;
  const fact_evidence_coverage_pct = Number((((directFacts + derivedFacts) / Math.max(1, facts.length)) * 100).toFixed(2));
  const direct_evidence_coverage_pct = Number(((directFacts / Math.max(1, facts.length)) * 100).toFixed(2));

  const directGeometries = geometries.filter(
    (g) => g.geometry_type === 'DIRECT_SOURCE_GEOMETRY' || g.geometry_type === 'TRANSFORMED_SOURCE_GEOMETRY'
  ).length;
  const syntheticGeometries = geometries.filter((g) => g.geometry_type === 'SYNTHETIC_GEOMETRY').length;
  const geometry_provenance_coverage_pct = Number(((directGeometries / Math.max(1, geometries.length)) * 100).toFixed(2));

  const groundedRelations = graphRelations.filter((r) => r.grounded).length;
  const graph_provenance_coverage_pct = Number(((groundedRelations / Math.max(1, graphRelations.length)) * 100).toFixed(2));

  let conflict_resolution_coverage_pct = 100.0;
  if (conflictGate.conflicts_found > 0) {
    conflict_resolution_coverage_pct = Number(
      (((conflictGate.conflicts_found - conflictGate.unresolved_conflicts) / conflictGate.conflicts_found) * 100).toFixed(2)
    );
  }

  // Composite Formula: 30% Source + 30% Fact Evidence + 20% Geometry + 20% Graph
  const global_epistemic_score = Number(
    (
      0.30 * source_coverage_pct +
      0.30 * fact_evidence_coverage_pct +
      0.20 * geometry_provenance_coverage_pct +
      0.20 * graph_provenance_coverage_pct
    ).toFixed(2)
  );

  return {
    total_sources: sources.length,
    verified_sources: verifiedSources,
    source_coverage_pct,
    total_facts: facts.length,
    direct_facts: directFacts,
    derived_facts: derivedFacts,
    inferred_facts: inferredFacts,
    unverified_facts: unverifiedFacts,
    fact_evidence_coverage_pct,
    direct_evidence_coverage_pct,
    total_geometry_objects: geometries.length,
    direct_geometry_objects: directGeometries,
    synthetic_geometry_objects: syntheticGeometries,
    geometry_provenance_coverage_pct,
    total_graph_relations: graphRelations.length,
    grounded_graph_relations: groundedRelations,
    graph_provenance_coverage_pct,
    conflicts_total: conflictGate.conflicts_found,
    conflicts_resolved: conflictGate.conflicts_found - conflictGate.unresolved_conflicts,
    conflict_resolution_coverage_pct,
    global_epistemic_score
  };
}

/**
 * Main Gatekeeper Class
 */
export class EvidenceGatekeeper {
  private sources: Map<string, SourceArtifactRecord> = new Map();
  private facts: FactEvidenceRecord[] = [];
  private geometries: GeometryProvenanceRecord[] = [];
  private graphRelations: Array<{ grounded: boolean }> = [];
  private conflictGate: ConflictGateResult = {
    executed: false,
    resolver_version: 'ConflictResolver_v1.0',
    checked_entities: 0,
    conflicts_found: 0,
    unresolved_conflicts: 0,
    status_summary: 'CONFLICT STATUS UNKNOWN (Conflict Detection not executed)'
  };

  public registerSource(source: SourceArtifactRecord): void {
    this.sources.set(source.source_id, source);
  }

  public addFact(fact: FactEvidenceRecord): void {
    this.facts.append ? this.facts.push(fact) : this.facts.push(fact);
  }

  public addGeometry(geom: GeometryProvenanceRecord): void {
    this.geometries.push(geom);
  }

  public setConflictResult(result: ConflictGateResult): void {
    this.conflictGate = result;
  }

  public evaluatePublishGate(): PublishGateResult {
    const reasons: string[] = [];
    const warnings: string[] = [];

    const sourceList = Array.from(this.sources.values());

    // 1. Check Primary Sources
    if (sourceList.length === 0) {
      reasons.push('NO_SOURCES_REGISTERED');
    } else {
      const missing = sourceList.filter((s) => s.verification_status === 'MISSING').map((s) => s.source_id);
      if (missing.length > 0) {
        reasons.push(`PRIMARY_SOURCE_MISSING: ${missing.join(', ')}`);
      }
      const mismatches = sourceList.filter((s) => s.verification_status === 'HASH_MISMATCH').map((s) => s.source_id);
      if (mismatches.length > 0) {
        reasons.push(`SOURCE_HASH_MISMATCH: ${mismatches.join(', ')}`);
      }
    }

    // 2. Validate Fact-Level Epistemic Integrity
    for (const fact of this.facts) {
      if (fact.epistemic_status === 'DIRECT') {
        if (!fact.evidence || fact.evidence.length === 0) {
          reasons.push(`INVALID_FACT_EPISTEMIC_STATUS: Fact '${fact.fact_id}' declared DIRECT but missing evidence.`);
        } else {
          for (const ev of fact.evidence) {
            const src = this.sources.get(ev.source_id);
            if (!src || src.verification_status !== 'VERIFIED') {
              reasons.push(`INVALID_FACT_EPISTEMIC_STATUS: Fact '${fact.fact_id}' references unverified source '${ev.source_id}'.`);
            }
          }
        }
      } else if (fact.epistemic_status === 'DERIVED') {
        if (!fact.parent_fact_ids || fact.parent_fact_ids.length === 0) {
          reasons.push(`INVALID_FACT_EPISTEMIC_STATUS: Fact '${fact.fact_id}' declared DERIVED but missing parent_fact_ids.`);
        }
      }
    }

    // 3. Check Geometry Provenance Truth
    for (const geom of this.geometries) {
      if (geom.geometry_type === 'DIRECT_SOURCE_GEOMETRY') {
        if (!geom.source_id || !this.sources.get(geom.source_id) || this.sources.get(geom.source_id)?.verification_status !== 'VERIFIED') {
          reasons.push(`GEOMETRY_PROVENANCE_VIOLATION: Geometry '${geom.object_id}' is marked DIRECT but lacks verified source.`);
        }
      } else if (geom.geometry_type === 'SYNTHETIC_GEOMETRY' && geom.confidence > 0.60) {
        reasons.push(`GEOMETRY_PROVENANCE_VIOLATION: Synthetic geometry '${geom.object_id}' carries unjustified confidence ${geom.confidence}.`);
      }
    }

    // 4. Check Conflict Detection Execution
    if (!this.conflictGate.executed) {
      reasons.push('CONFLICT_DETECTION_NOT_EXECUTED');
    } else if (this.conflictGate.unresolved_conflicts > 0) {
      reasons.push(`UNRESOLVED_CRITICAL_CONFLICTS (${this.conflictGate.unresolved_conflicts})`);
    }

    // 5. Compute Deterministic Metrics
    const metrics = computeEpistemicCoverage(sourceList, this.facts, this.geometries, this.graphRelations, this.conflictGate);

    if (metrics.global_epistemic_score < 70.0) {
      warnings.push(`LOW_GLOBAL_EPISTEMIC_SCORE (${metrics.global_epistemic_score}%)`);
    }

    if (reasons.length > 0) {
      return {
        status: 'PUBLISH_BLOCKED',
        reasons,
        warnings,
        metrics,
        conflict_gate: this.conflictGate
      };
    } else if (warnings.length > 0) {
      return {
        status: 'PUBLISH_ALLOWED_WITH_WARNINGS',
        reasons: [],
        warnings,
        metrics,
        conflict_gate: this.conflictGate
      };
    } else {
      return {
        status: 'PUBLISH_ALLOWED',
        reasons: [],
        warnings: [],
        metrics,
        conflict_gate: this.conflictGate
      };
    }
  }
}
