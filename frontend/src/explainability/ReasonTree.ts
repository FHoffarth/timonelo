/**
 * explainability/ReasonTree.ts
 * 
 * Generates transparent, deterministic reason trees that break down
 * every score step-by-step from baseline to final value.
 */

import { ExplainableScore, ReasonStep, TriggeredRule, EvidenceProvenance } from "./types";

export class ReasonTreeBuilder {
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
      provenance: {
        evidence_id: "EV-BASELINE",
        source_title: "Timonelo Maritime Baseline Model",
        artifact_id: "TIMONELO-CORE-STANDARDS",
        confidence: 1.0,
        status: "DIRECT",
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

    // Mean confidence
    const confs = triggeredRules.map((r) => r.provenance.confidence);
    const meanConf = confs.length > 0 ? confs.reduce((a, b) => a + b, 0) / confs.length : 0.95;

    return {
      key,
      name,
      baseline_score: baseline,
      final_score: finalScore,
      grade,
      confidence: round(meanConf, 2),
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

function round(val: number, decimals: number): number {
  return Number(Math.round(Number(val + "e" + decimals)) + "e-" + decimals);
}
