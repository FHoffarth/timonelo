/**
 * explainability/types.ts
 * 
 * Formal type definitions for the Timonelo Explainability Engine.
 * Implements the chain: Evidence -> Graph -> Geometry -> Rule -> Delta -> Score.
 */

export type EvidencePolarity = "POSITIVE" | "NEGATIVE" | "CONFLICTING" | "UNKNOWN";

// P0-H2: provenance fields are nullable — unbacked values fail closed to null
// rather than being synthesized.
export interface EvidenceProvenance {
  evidence_id: string | null;
  source_title: string | null;
  artifact_id: string | null;
  page?: number;
  locator?: string | null;
  graph_edge?: string | null;
  geometry_file?: string | null;
  knowledge_entity_id?: string;
  statement_id?: string | null;
  confidence: number | null;
  status: "DIRECT" | "DERIVED" | "CONFLICT" | "UNKNOWN";
  raw_finding: string;
}

export interface RuleDefinition {
  id: string;
  category: "quiet" | "motion" | "walking" | "privacy" | "accessibility" | "family" | "couple";
  title: string;
  description: string;
  weight: number; // e.g. -25, +12, -18
  polarity: EvidencePolarity;
  required_graph_relations: string[];
  required_knowledge_entities: string[];
  required_geometry: string[];
  required_evidence: {
    artifact_id: string;
    page: number;
    title: string;
  };
}

export interface TriggeredRule {
  rule: RuleDefinition;
  applied_weight: number;
  provenance: EvidenceProvenance;
  explanation: string;
}

export interface ReasonStep {
  step_number: number;
  rule_id: string;
  rule_title: string;
  delta: number;
  running_total: number;
  rationale: string;
  provenance: EvidenceProvenance;
}

export interface ExplainableScore {
  key: string;
  name: string;
  baseline_score: number | null;
  final_score: number | null;
  grade: "EXCELLENT" | "GOOD" | "MODERATE" | "ATTENTION" | "UNAVAILABLE";
  // P0-H2: null when no triggered rule carried a backed confidence value.
  confidence: number | null;
  steps: ReasonStep[];
  rules_triggered: TriggeredRule[];
  positive_evidence: EvidenceProvenance[];
  negative_evidence: EvidenceProvenance[];
  conflicting_evidence: EvidenceProvenance[];
  unknown_evidence: EvidenceProvenance[];
  sources: string[];
}

export interface ExplainableCabinIntelligence {
  cabin_id: string;
  vessel_id: string;
  deck_number: number;
  deck_name: string;
  scores: Record<string, ExplainableScore>;
  all_triggered_rules: TriggeredRule[];
  // P0-H2: null when no rule carried a backed confidence value.
  global_epistemic_confidence: number | null;
  evaluated_at: string;
}
