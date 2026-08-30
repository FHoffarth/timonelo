/**
 * explainability/ReasonTree.ts
 * 
 * Generates transparent, deterministic reason trees that break down
 * every score step-by-step from baseline to final value.
 */

import { ExplainableScore, ReasonStep, TriggeredRule, EvidenceProvenance } from "./types";

export class ReasonTreeBuilder {
  public static buildUnavailableScore(key: string, name: string): ExplainableScore {
    return {
      key,
      name,
      baseline_score: null,
      final_score: null,
      grade: "UNAVAILABLE",
      confidence: null,
      steps: [],
      rules_triggered: [],
      positive_evidence: [],
      negative_evidence: [],
      conflicting_evidence: [],
      unknown_evidence: [],
      sources: [],
    };
  }

  public static buildExplainableScore(
    key: string,
    name: string,
    baseline: number,
    triggeredRules: TriggeredRule[]
  ): ExplainableScore {
    let runningTotal = baseline;
    const steps: ReasonStep[] = [];
    const positiveEvidence: EvidenceProvenance[] = [];
    const negativeEvidence: EvidenceProvenance[] = [];
    const conflictingEvidence: EvidenceProvenance[] = [];
    const unknownEvidence: EvidenceProvenance[] = [];
    const sourcesSet = new Set<string>();

    // Initial baseline step
    steps.push({
      step_number: 1,
      rule_id: "BASELINE",
      rule_title: "Neutral Theoretical Baseline",
      delta: baseline,
      running_total: runningTotal,
      rationale: "Theoretical starting baseline prior to empirical spatial adjustments.",
      // P0-H2: the baseline is a scoring step, not evidence. It carries no
      // artifact, statement, confidence, or verified status.
      provenance: {
        evidence_id: null,
        source_title: null,
        artifact_id: null,
        confidence: null,
        status: "UNKNOWN",
        raw_finding: "Initial neutral score value",
      },
    });

    triggeredRules.forEach((tr, idx) => {
      runningTotal += tr.applied_weight;
      // Clamp between 0 and 100
      runningTotal = Math.min(100, Math.max(0, runningTotal));

      steps.push({
        step_number: idx + 2,
        rule_id: tr.rule.id,
        rule_title: tr.rule.title,
        delta: tr.applied_weight,
        running_total: runningTotal,
        rationale: tr.explanation,
        provenance: tr.provenance,
      });

      // Categorize evidence
      if (tr.rule.polarity === "POSITIVE") {
        positiveEvidence.push(tr.provenance);
      } else if (tr.rule.polarity === "NEGATIVE") {
        negativeEvidence.push(tr.provenance);
      } else if (tr.rule.polarity === "CONFLICTING") {
        conflictingEvidence.push(tr.provenance);
      } else {
        unknownEvidence.push(tr.provenance);
      }

      if (tr.provenance.source_title) {
        sourcesSet.add(`${tr.provenance.source_title} (P.${tr.provenance.page ?? 1})`);
      }
    });

    // Final grade calculation
    const finalScore = runningTotal;
    let grade: "EXCELLENT" | "GOOD" | "MODERATE" | "ATTENTION" = "GOOD";
    if (finalScore >= 88) grade = "EXCELLENT";
    else if (finalScore >= 75) grade = "GOOD";
    else if (finalScore >= 60) grade = "MODERATE";
    else grade = "ATTENTION";

    // Mean confidence over backed values only (P0-H2): nulls are excluded,
    // never coerced to 0, and an unbacked set yields null rather than NaN.
    const meanConf = meanBackedConfidence(triggeredRules.map((r) => r.provenance.confidence));

    return {
      key,
      name,
      baseline_score: baseline,
      final_score: finalScore,
      grade,
      confidence: meanConf,
      steps,
      rules_triggered: triggeredRules,
      positive_evidence: positiveEvidence,
      negative_evidence: negativeEvidence,
      conflicting_evidence: conflictingEvidence,
      unknown_evidence: unknownEvidence,
      sources: Array.from(sourcesSet),
    };
  }
}

/**
 * P0-H2: mean of backed confidence values only.
 * Nulls/undefined and non-finite values are excluded rather than coerced to 0.
 * Returns null when nothing is backed. Never returns NaN.
 */
function meanBackedConfidence(values: Array<number | null | undefined>): number | null {
  const backed = [];
  for (const v of values) {
    if (typeof v === "number" && Number.isFinite(v)) backed.push(v);
  }
  if (backed.length === 0) return null;
  const mean = backed.reduce((a, b) => a + b, 0) / backed.length;
  return Number(mean.toFixed(2));
}
