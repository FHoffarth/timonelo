/**
 * explainability/ExplainabilityEngine.ts
 * 
 * High-level coordinator linking deterministic rules, evidence provenance,
 * and reason trees into fully explainable cabin intelligence.
 */

import { ExplainableCabinIntelligence, ExplainableScore, TriggeredRule } from "./types";
import { RULE_REGISTRY } from "./RuleRegistry";
import { EvidenceResolver } from "./EvidenceResolver";
import { ReasonTreeBuilder } from "./ReasonTree";
import { SemanticEntity } from "../semantic-deck/types";

/**
 * P0-H2: mean of backed confidence values only.
 * Nulls are excluded, never coerced to 0. Returns null when nothing is backed,
 * so callers can render "unavailable" instead of a fabricated number. Never
 * returns NaN.
 */
export function meanBackedConfidence(values: Array<number | null | undefined>): number | null {
  const backed = [];
  for (const v of values) {
    if (typeof v === "number" && Number.isFinite(v)) backed.push(v);
  }
  if (backed.length === 0) return null;
  const mean = backed.reduce((a, b) => a + b, 0) / backed.length;
  return Number(mean.toFixed(2));
}

export class ExplainabilityEngine {
  public static explainCabin(entity: SemanticEntity, vesselId: string = "msc-bellissima"): ExplainableCabinIntelligence {
    const cid = entity.id;
    const level = entity.level;
    const relations = entity.relations || {};
    const overhead = relations.adjacent_overhead || "";
    const underfoot = relations.adjacent_underfoot || "";
    const isForward = entity.zone.includes("FORWARD") || cid.endsWith("01") || cid.endsWith("02") || cid.endsWith("03");

    const allTriggeredRules: TriggeredRule[] = [];

    // Helper to evaluate and trigger a rule
    const trigger = (ruleId: string, customExplanation?: string, weightOverride?: number): TriggeredRule => {
      const rule = RULE_REGISTRY[ruleId];
      if (!rule) {
        throw new Error(`Orphan or unknown rule ID: ${ruleId}`);
      }

      const weight = weightOverride !== undefined ? weightOverride : rule.weight;
      const provenance = EvidenceResolver.resolveRuleEvidence(rule, entity, vesselId);

      const triggered: TriggeredRule = {
        rule,
        applied_weight: weight,
        provenance,
        explanation: customExplanation || rule.description,
      };

      allTriggeredRules.push(triggered);
      return triggered;
    };

    // =========================================================================
    // 1. QUIET EXPLAINABILITY
    // =========================================================================
    const quietRules: TriggeredRule[] = [];
    if (overhead.toLowerCase().includes("buffet") || overhead.toLowerCase().includes("marketplace")) {
      quietRules.push(trigger("RULE-QUIET-004", "Marketplace Buffet directly overhead on Deck 15"));
    } else if (overhead.toLowerCase().includes("pool") || overhead.toLowerCase().includes("aquapark")) {
      quietRules.push(trigger("RULE-QUIET-005", "Open pool deck overhead"));
    } else if (level >= 9 && level <= 13) {
      quietRules.push(trigger("RULE-QUIET-001", "Sandwiched between purely residential stateroom decks above & below"));
    }

    if (!underfoot.toLowerCase().includes("theatre") && !underfoot.toLowerCase().includes("casino")) {
      quietRules.push(trigger("RULE-QUIET-002", "No high-energy entertainment venue directly below"));
    }

    const quietExplainable: ExplainableScore = ReasonTreeBuilder.buildExplainableScore(
      "quiet",
      "Tranquility & Quietness",
      90, // Baseline
      quietRules
    );

    // =========================================================================
    // 2. MOTION EXPLAINABILITY
    // =========================================================================
    const motionRules: TriggeredRule[] = [];
    if (isForward) {
      motionRules.push(trigger("RULE-MOTION-002", "Positioned in forward bow zone; experiences high vertical pitch heave in swell"));
    } else {
      motionRules.push(trigger("RULE-MOTION-001", "Located near midship neutral flotation axis (lowest sea motion)"));
    }

    if (level <= 8) {
      motionRules.push(trigger("RULE-MOTION-003", "Low deck elevation minimizes roll pendulum moment"));
    } else if (level >= 14) {
      motionRules.push(trigger("RULE-MOTION-004", "Upper deck elevation increases angular roll amplitude"));
    }

    const motionExplainable: ExplainableScore = ReasonTreeBuilder.buildExplainableScore(
      "motion",
      "Vessel Stability & Motion",
      85, // Baseline
      motionRules
    );

    // =========================================================================
    // 3. WALKING EXPLAINABILITY
    // =========================================================================
    const walkingRules: TriggeredRule[] = [
      trigger("RULE-WALK-001", `Direct corridor link to ${relations.connected_vertical_core || "Midship Lift Bank"}`),
    ];

    const walkingExplainable: ExplainableScore = ReasonTreeBuilder.buildExplainableScore(
      "walking",
      "Transit & Lift Convenience",
      80, // Baseline
      walkingRules
    );

    // =========================================================================
    // 4. PRIVACY EXPLAINABILITY
    // =========================================================================
    const privacyRules: TriggeredRule[] = [];
    if (entity.has_balcony) {
      privacyRules.push(trigger("RULE-PRIV-001", "Private step-out ocean veranda with unobstructed sea views"));
    }

    const privacyExplainable: ExplainableScore = ReasonTreeBuilder.buildExplainableScore(
      "privacy",
      "Privacy & Solitude",
      85, // Baseline
      privacyRules
    );

    // =========================================================================
    // 5. ACCESSIBILITY EXPLAINABILITY
    // =========================================================================
    const accessRules: TriggeredRule[] = [];
    if (entity.accessible) {
      accessRules.push(trigger("RULE-ACC-001", "Certified PRM stateroom with 85cm wide door and step-free roll-in shower"));
    }

    const accessExplainable: ExplainableScore = ReasonTreeBuilder.buildExplainableScore(
      "accessibility",
      "Physical Accessibility (PRM)",
      70, // Baseline
      accessRules
    );

    const scores: Record<string, ExplainableScore> = {
      quiet: quietExplainable,
      motion: motionExplainable,
      walking: walkingExplainable,
      privacy: privacyExplainable,
      accessibility: accessExplainable,
    };

    // Calculate global confidence over backed values only (P0-H2).
    const globalConfidence = meanBackedConfidence(
      allTriggeredRules.map((r) => r.provenance.confidence)
    );

    return {
      cabin_id: cid,
      vessel_id: vesselId,
      deck_number: level,
      deck_name: entity.level_name || `Deck ${level}`,
      scores,
      all_triggered_rules: allTriggeredRules,
      global_epistemic_confidence: globalConfidence,
      evaluated_at: "2026-08-18",
    };
  }
}
