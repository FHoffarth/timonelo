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
import {
  isPassengerEntityAdmitted,
  isPassengerFactAdmitted,
} from "../semantic-deck/passengerAdmission";

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
    const isForward = entity.zone.includes("FORWARD");

    const allTriggeredRules: TriggeredRule[] = [];

    // Helper to evaluate and trigger a rule
    const trigger = (ruleId: string, customExplanation?: string, weightOverride?: number): TriggeredRule => {
      const rule = RULE_REGISTRY[ruleId];
      if (!rule) {
        throw new Error(`Orphan or unknown rule ID: ${ruleId}`);
      }

      const weight = weightOverride !== undefined ? weightOverride : rule.weight;
      const admittedFactKeys = new Set(
        entity.admitted_fact_keys.filter((fact) => isPassengerFactAdmitted(entity, fact)),
      );
      const provenance = EvidenceResolver.resolveRuleEvidence(rule, entity, vesselId, {
        entityAdmitted: isPassengerEntityAdmitted(entity),
        admittedFactKeys,
      });

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
    const quietAdmitted = isPassengerFactAdmitted(entity, "quiet_intelligence");
    const overheadAdmitted = isPassengerFactAdmitted(entity, "adjacent_overhead");
    const underfootAdmitted = isPassengerFactAdmitted(entity, "adjacent_underfoot");
    if (quietAdmitted && overheadAdmitted && (overhead.toLowerCase().includes("buffet") || overhead.toLowerCase().includes("marketplace"))) {
      quietRules.push(trigger("RULE-QUIET-004", "Marketplace Buffet directly overhead on Deck 15"));
    } else if (quietAdmitted && overheadAdmitted && (overhead.toLowerCase().includes("pool") || overhead.toLowerCase().includes("aquapark"))) {
      quietRules.push(trigger("RULE-QUIET-005", "Open pool deck overhead"));
    }

    if (quietAdmitted && underfootAdmitted &&
        !underfoot.toLowerCase().includes("theatre") && !underfoot.toLowerCase().includes("casino")) {
      quietRules.push(trigger("RULE-QUIET-002", "No high-energy entertainment venue directly below"));
    }

    const quietExplainable: ExplainableScore = quietAdmitted ? ReasonTreeBuilder.buildExplainableScore(
      "quiet",
      "Tranquility & Quietness",
      90, // Baseline
      quietRules
    ) : ReasonTreeBuilder.buildUnavailableScore("quiet", "Tranquility & Quietness");

    // =========================================================================
    // 2. MOTION EXPLAINABILITY
    // =========================================================================
    const motionRules: TriggeredRule[] = [];
    const motionAdmitted = isPassengerFactAdmitted(entity, "motion_intelligence");
    const zoneAdmitted = isPassengerFactAdmitted(entity, "zone");
    const deckAdmitted = isPassengerFactAdmitted(entity, "deck");
    if (motionAdmitted && zoneAdmitted && isForward) {
      motionRules.push(trigger("RULE-MOTION-002", "Positioned in forward bow zone; experiences high vertical pitch heave in swell"));
    } else if (motionAdmitted && zoneAdmitted) {
      motionRules.push(trigger("RULE-MOTION-001", "Located near midship neutral flotation axis (lowest sea motion)"));
    }

    if (motionAdmitted && deckAdmitted && level <= 8) {
      motionRules.push(trigger("RULE-MOTION-003", "Low deck elevation minimizes roll pendulum moment"));
    } else if (motionAdmitted && deckAdmitted && level >= 14) {
      motionRules.push(trigger("RULE-MOTION-004", "Upper deck elevation increases angular roll amplitude"));
    }

    const motionExplainable: ExplainableScore = motionAdmitted ? ReasonTreeBuilder.buildExplainableScore(
      "motion",
      "Vessel Stability & Motion",
      85, // Baseline
      motionRules
    ) : ReasonTreeBuilder.buildUnavailableScore("motion", "Vessel Stability & Motion");

    // =========================================================================
    // 3. WALKING EXPLAINABILITY
    // =========================================================================
    const walkingAdmitted =
      isPassengerFactAdmitted(entity, "walking_intelligence") &&
      isPassengerFactAdmitted(entity, "corridor_connectivity") &&
      isPassengerFactAdmitted(entity, "connected_vertical_core") &&
      Boolean(relations.connected_vertical_core);
    const walkingRules: TriggeredRule[] = walkingAdmitted ? [
      trigger("RULE-WALK-001", `Direct corridor link to ${relations.connected_vertical_core}`),
    ] : [];

    const walkingExplainable: ExplainableScore = walkingAdmitted ? ReasonTreeBuilder.buildExplainableScore(
      "walking",
      "Transit & Lift Convenience",
      80, // Baseline
      walkingRules
    ) : ReasonTreeBuilder.buildUnavailableScore("walking", "Transit & Lift Convenience");

    // =========================================================================
    // 4. PRIVACY EXPLAINABILITY
    // =========================================================================
    const privacyRules: TriggeredRule[] = [];
    const privacyAdmitted = isPassengerFactAdmitted(entity, "privacy_intelligence");
    if (privacyAdmitted && isPassengerFactAdmitted(entity, "balcony") && entity.has_balcony) {
      privacyRules.push(trigger("RULE-PRIV-001", "Private step-out ocean veranda with unobstructed sea views"));
    }

    const privacyExplainable: ExplainableScore = privacyAdmitted ? ReasonTreeBuilder.buildExplainableScore(
      "privacy",
      "Privacy & Solitude",
      85, // Baseline
      privacyRules
    ) : ReasonTreeBuilder.buildUnavailableScore("privacy", "Privacy & Solitude");

    // =========================================================================
    // 5. ACCESSIBILITY EXPLAINABILITY
    // =========================================================================
    const accessRules: TriggeredRule[] = [];
    const accessibilityAdmitted = isPassengerFactAdmitted(entity, "accessibility_intelligence");
    if (accessibilityAdmitted && isPassengerFactAdmitted(entity, "accessible_designation") && entity.accessible) {
      accessRules.push(trigger("RULE-ACC-001", "Canonical accessibility designation is admitted for passenger use"));
    }

    const accessExplainable: ExplainableScore = accessibilityAdmitted ? ReasonTreeBuilder.buildExplainableScore(
      "accessibility",
      "Physical Accessibility (PRM)",
      70, // Baseline
      accessRules
    ) : ReasonTreeBuilder.buildUnavailableScore("accessibility", "Physical Accessibility (PRM)");

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
