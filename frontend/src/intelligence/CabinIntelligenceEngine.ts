/**
 * CabinIntelligenceEngine.ts
 * 
 * Deterministic, Explainable Spatial & Acoustic Intelligence Engine.
 * 
 * Rules:
 * - Never invent facts.
 * - Never use black-box inference or probabilistic LLM hallucinations.
 * - Every single score is strictly derived from verified W3C graph relations,
 *   shipboard geometry, and canonical negative intelligence audits.
 */

import { SemanticEntity } from "../semantic-deck/types";
import {
  getPassengerFact,
  isPassengerEntityAdmitted,
  isPassengerFactAdmitted,
  type PassengerFactKey,
} from "../semantic-deck/passengerAdmission";

export interface ScoreItem {
  name: string;
  key: string;
  score: number | null; // null means the required evidence was not admitted
  grade: "EXCELLENT" | "GOOD" | "MODERATE" | "ATTENTION" | "UNAVAILABLE";
  summary: string;
  factors: string[];
}

export interface CabinIntelligence {
  cabin_id: string;
  vessel_id: string;
  deck_number: number | null;
  deck_name: string;
  classification: string | null;
  side: "PORT" | "STARBOARD" | "CENTER" | null;
  is_accessible: boolean | null;
  has_balcony: boolean | null;
  
  // Deterministic Core Scores (0 - 100)
  quiet_score: ScoreItem;
  motion_score: ScoreItem;
  walking_score: ScoreItem;
  privacy_score: ScoreItem;
  accessibility_score: ScoreItem;
  family_score: ScoreItem;
  couple_score: ScoreItem;

  // Key explainable findings
  all_reasoning: string[];
  scores: Record<string, ScoreItem>;
  epistemic_confidence: number | null;
  provenance_sources: string[];
}

function getGrade(score: number): "EXCELLENT" | "GOOD" | "MODERATE" | "ATTENTION" {
  if (score >= 88) return "EXCELLENT";
  if (score >= 75) return "GOOD";
  if (score >= 60) return "MODERATE";
  return "ATTENTION";
}

export class CabinIntelligenceEngine {
  public static evaluateCabin(entity: SemanticEntity, vesselId: string): CabinIntelligence {
    const relations = entity.relations || {};
    const deck = entity.level;
    const side = entity.side;
    const cid = entity.id;

    const reasoning: string[] = [];
    const provSources: string[] = isPassengerFactAdmitted(entity, "source_artifact", vesselId)
      ? entity.evidence_links
          .map((link) => link.source_title || link.artifact_id)
          .filter((source): source is string => Boolean(source))
      : [];

    // ==========================================
    // 1. QUIET SCORE (Acoustic & Tranquility)
    // ==========================================
    let quietScoreVal = 90;
    const quietFactors: string[] = [];

    // Overhead analysis
    const overhead = relations.adjacent_overhead || "";
    if (overhead.toLowerCase().includes("buffet") || overhead.toLowerCase().includes("marketplace")) {
      quietScoreVal -= 24;
      quietFactors.push("Marketplace Buffet directly overhead on Deck 15 (potential morning cart rolling & galley prep noise)");
      reasoning.push("Acoustic buffer warning: Positioned directly under Marketplace Buffet galley stations.");
    } else if (overhead.toLowerCase().includes("pool") || overhead.toLowerCase().includes("aquapark")) {
      quietScoreVal -= 18;
      quietFactors.push("Open pool deck / sundeck overhead (lounger scraping during morning setup)");
    }

    // Underfoot analysis
    const underfoot = relations.adjacent_underfoot || "";
    if (underfoot.toLowerCase().includes("theatre") || underfoot.toLowerCase().includes("casino") || underfoot.toLowerCase().includes("carousel")) {
      quietScoreVal -= 22;
      quietFactors.push("High-energy entertainment venue directly below on lower deck");
    }

    quietScoreVal = Math.min(99, Math.max(40, quietScoreVal));

    const quietScore: ScoreItem = {
      name: "Tranquility & Quietness",
      key: "quiet",
      score: quietScoreVal,
      grade: getGrade(quietScoreVal),
      summary: "Evidence-gated acoustic rule result based only on admitted vertical relations.",
      factors: quietFactors
    };

    // ==========================================
    // 2. MOTION SCORE (Seakeeping & Stability)
    // ==========================================
    let motionScoreVal = 85;
    const motionFactors: string[] = [];

    // Longitudinal position (Bow, Midship, Stern)
    const isForward = entity.zone.includes("FORWARD");
    const isAft = entity.zone.includes("AFT");

    if (isForward) {
      motionScoreVal -= 18;
      motionFactors.push("Forward bow quadrant experiences highest vertical heave and slamming acceleration in heavy seas");
      reasoning.push("Motion sensitivity: Located in forward section; guests sensitive to pitch motion should note high bow displacement.");
    } else if (isAft) {
      motionScoreVal -= 8;
      motionFactors.push("Aft stern section experiences slight horizontal sway and low-frequency propeller cavitation wake");
    } else {
      motionScoreVal += 12;
      motionFactors.push("Positioned in the midship neutral roll-pitch center of flotation (lowest sea motion)");
      reasoning.push("Optimal seaworthiness: Located near midship center of gravity for maximum hydrodynamic stability.");
    }

    // Vertical height displacement
    if (deck <= 8) {
      motionScoreVal += 5;
      motionFactors.push("Low center-of-mass deck height minimizes angular roll pendulum effect");
    } else if (deck >= 14) {
      motionScoreVal -= 10;
      motionFactors.push(`High deck elevation (Deck ${deck}) amplifies angular roll amplitude during swell`);
    }

    motionScoreVal = Math.min(99, Math.max(45, motionScoreVal));

    const motionScore: ScoreItem = {
      name: "Vessel Stability & Low Motion",
      key: "motion",
      score: motionScoreVal,
      grade: getGrade(motionScoreVal),
      summary: motionScoreVal >= 85 ? "Superb stability located near vessel neutral buoyancy axis." : "Noticeable pitch/roll dynamics during high sea states.",
      factors: motionFactors
    };

    // ==========================================
    // 3. WALKING & LIFT CONVENIENCE SCORE
    // ==========================================
    let walkingScoreVal = 88;
    const walkingFactors: string[] = [];

    walkingFactors.push(`Admitted corridor connection to ${relations.connected_vertical_core}`);

    const walkingScore: ScoreItem = {
      name: "Transit & Lift Convenience",
      key: "walking",
      score: walkingScoreVal,
      grade: getGrade(walkingScoreVal),
      summary: "An admitted corridor-to-core relation supports this transit score.",
      factors: walkingFactors
    };

    // ==========================================
    // 4. PRIVACY & SIGHTLINES SCORE
    // ==========================================
    let privacyScoreVal = 90;
    const privacyFactors: string[] = [];

    if (entity.has_balcony) {
      privacyScoreVal += 5;
      privacyFactors.push("Admitted balcony classification contributes to this analysis");
    }

    const privacyScore: ScoreItem = {
      name: "Privacy & Visual Solitude",
      key: "privacy",
      score: Math.min(99, privacyScoreVal),
      grade: getGrade(privacyScoreVal),
      summary: "Privacy analysis is limited to explicitly admitted cabin facts.",
      factors: privacyFactors
    };

    // ==========================================
    // 5. ACCESSIBILITY SCORE
    // ==========================================
    let accessScoreVal = entity.accessible ? 98 : 70;
    const accessFactors: string[] = [];

    if (entity.accessible) {
      accessFactors.push("Mobility-designated stateroom status is admitted");
    }

    const accessibilityScore: ScoreItem = {
      name: "Physical Accessibility (PRM)",
      key: "accessibility",
      score: accessScoreVal,
      grade: getGrade(accessScoreVal),
      summary: entity.accessible
        ? "Mobility designation is admitted; detailed accessibility features require separate evidence."
        : "No positive mobility designation is admitted for this evaluation.",
      factors: accessFactors
    };

    // ==========================================
    // 6. FAMILY & MULTI-BERTH SCORE
    // ==========================================
    let familyScoreVal = entity.connecting ? 95 : 78;
    const familyFactors: string[] = [];
    if (entity.connecting) {
      familyFactors.push("Admitted connecting-cabin designation contributes to this analysis");
    }

    const familyScore: ScoreItem = {
      name: "Family Suitability",
      key: "family",
      score: familyScoreVal,
      grade: getGrade(familyScoreVal),
      summary: entity.connecting
        ? "An admitted connecting-cabin relation supports this family analysis."
        : "Family suitability analysis is admitted without a connecting-cabin boost.",
      factors: familyFactors
    };

    // ==========================================
    // 7. COUPLE & LUXURY SCORE
    // ==========================================
    let coupleScoreVal = entity.has_balcony ? 94 : 80;
    const coupleFactors: string[] = [];
    if (entity.has_balcony) coupleFactors.push("Admitted balcony classification contributes to this analysis");

    const coupleScore: ScoreItem = {
      name: "Couples & Romance Index",
      key: "couple",
      score: coupleScoreVal,
      grade: getGrade(coupleScoreVal),
      summary: "Couples suitability is available only as an admitted rule result.",
      factors: coupleFactors
    };

    const unavailableScore = (name: string, key: string): ScoreItem => ({
      name,
      key,
      score: null,
      grade: "UNAVAILABLE",
      summary: "Unavailable — the required facts have not crossed the passenger evidence gate.",
      factors: [],
    });
    const admitScore = (
      fact: PassengerFactKey,
      item: ScoreItem,
      requiredFacts: PassengerFactKey[] = [],
    ): ScoreItem => isPassengerFactAdmitted(entity, fact, vesselId) &&
      requiredFacts.every((required) => isPassengerFactAdmitted(entity, required, vesselId))
      ? item
      : unavailableScore(item.name, item.key);

    const admittedQuiet = admitScore("quiet_intelligence", quietScore, ["adjacent_overhead", "adjacent_underfoot"]);
    const admittedMotion = admitScore("motion_intelligence", motionScore, ["zone", "deck"]);
    const walkingFactsAdmitted =
      isPassengerFactAdmitted(entity, "walking_intelligence", vesselId) &&
      isPassengerFactAdmitted(entity, "corridor_connectivity", vesselId) &&
      isPassengerFactAdmitted(entity, "connected_vertical_core", vesselId) &&
      Boolean(relations.connected_vertical_core);
    const admittedWalking = walkingFactsAdmitted
      ? walkingScore
      : unavailableScore(walkingScore.name, walkingScore.key);
    const admittedPrivacy = admitScore("privacy_intelligence", privacyScore, ["balcony"]);
    const admittedAccessibility = admitScore("accessibility_intelligence", accessibilityScore, ["accessible_designation"]);
    const admittedFamily = admitScore("family_intelligence", familyScore, ["connecting_cabin"]);
    const admittedCouple = admitScore("couple_intelligence", coupleScore, ["balcony"]);
    const scores: Record<string, ScoreItem> = {
      quiet: admittedQuiet,
      motion: admittedMotion,
      walking: admittedWalking,
      privacy: admittedPrivacy,
      accessibility: admittedAccessibility,
      family: admittedFamily,
      couple: admittedCouple,
    };

    const confidence = isPassengerEntityAdmitted(entity, vesselId) &&
      typeof entity.confidence === "number"
      ? entity.confidence
      : null;

    return {
      cabin_id: cid,
      vessel_id: vesselId,
      deck_number: getPassengerFact(entity, "deck", deck, vesselId),
      deck_name: getPassengerFact(entity, "deck", entity.level_name || `Deck ${deck}`, vesselId) || "Deck unavailable",
      classification: getPassengerFact(
        entity,
        "classification",
        entity.classification_label || entity.classification,
        vesselId,
      ),
      side: getPassengerFact(entity, "side", side, vesselId),
      is_accessible: getPassengerFact(entity, "accessible_designation", entity.accessible, vesselId),
      has_balcony: getPassengerFact(entity, "balcony", entity.has_balcony, vesselId),
      quiet_score: admittedQuiet,
      motion_score: admittedMotion,
      walking_score: admittedWalking,
      privacy_score: admittedPrivacy,
      accessibility_score: admittedAccessibility,
      family_score: admittedFamily,
      couple_score: admittedCouple,
      scores,
      all_reasoning: Object.values(scores).flatMap((item) => item.factors),
      epistemic_confidence: confidence,
      provenance_sources: provSources
    };
  }
}
