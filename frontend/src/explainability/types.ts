/**
 * explainability/types.ts
 * 
 * Formal type definitions for the Timonelo Explainability Engine.
 * Implements the chain: Evidence -> Graph -> Geometry -> Rule -> Delta -> Score.
 */

export type EvidencePolarity = "POSITIVE" | "NEGATIVE" | "CONFLICTING" | "UNKNOWN";

export interface EvidenceProvenance {
  evidence_id: string;
  source_title: string;
  artifact_id: string;
  page?: number;
  locator?: string;
  graph_edge?: string;
  geometry_file?: string;
  knowledge_entity_id?: string;
  statement_id?: string;
  confidence: number;
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
  baseline_score: number;
  final_score: number;
  grade: "EXCELLENT" | "GOOD" | "MODERATE" | "ATTENTION";
  confidence: number;
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
  global_epistemic_confidence: number;
  evaluated_at: string;
}
