import { describe, expect, it } from "vitest";

import { ExplainabilityEngine } from "./ExplainabilityEngine";
import type { SemanticEntity } from "../semantic-deck/types";

const base: SemanticEntity = {
  vessel_id: "msc-bellissima",
  provenance_vessel_id: "msc-bellissima",
  data_origin: "LEGACY_SCHEMATIC",
  evidence_condition: "UNKNOWN",
  human_review_state: "DRAFT",
  publish_status: "PUBLISH_BLOCKED",
  geometry_provenance: "UNKNOWN_PROVENANCE",
  method: null,
  derivation: null,
  admitted_fact_keys: [],
  id: "14122",
  iri: "urn:cabin:14122",
  label: "Cabin 14122",
  classification: "STATEROOM_INTERIOR",
  classification_label: "Interior",
  level: 14,
  level_name: "Deck 14",
  side: "STARBOARD",
  zone: "MIDSHIP_FORWARD",
  sequence_order: 1,
  accessible: true,
  connecting: false,
  has_balcony: false,
  epistemic_state: "DIRECT",
  review_state: "PUBLISHED_VERIFIED",
  confidence: null,
  statement_count: 1,
  statements: ["legacy-statement"],
  artifact_count: 1,
  evidence_links: [],
  relations: { connected_vertical_core: "Midship Lift Bank" },
  unknown_fields: [],
};

describe("ExplainabilityEngine admission", () => {
  it("keeps legacy and UNKNOWN entities unavailable through scoring", () => {
    const result = ExplainabilityEngine.explainCabin(base, "msc-bellissima");

    expect(result.global_epistemic_confidence).toBeNull();
    expect(result.all_triggered_rules).toEqual([]);
    for (const score of Object.values(result.scores)) {
      expect(score.final_score).toBeNull();
      expect(score.grade).toBe("UNAVAILABLE");
      expect(score.steps).toEqual([]);
    }
  });

  it("continues to evaluate a specifically admitted walking rule", () => {
    const admitted: SemanticEntity = {
      ...base,
      data_origin: "CANONICAL_TRUTH_ENGINE",
      evidence_condition: "SUPPORTED",
      human_review_state: "APPROVED",
      publish_status: "PUBLISH_ALLOWED",
      geometry_provenance: "DIRECT_SOURCE_GEOMETRY",
      method: "DIRECT",
      derivation: "LOCAL",
      admitted_fact_keys: [
        "identity",
        "deck",
        "connected_vertical_core",
        "corridor_connectivity",
        "walking_intelligence",
      ],
      confidence: 0.9,
      evidence_links: [{
        artifact_id: "ART-REAL",
        source_title: "Held source",
        digest: "abc",
        locator: "page 5",
        page: 5,
      }],
    };

    const result = ExplainabilityEngine.explainCabin(admitted, "msc-bellissima");
    expect(result.scores.walking.final_score).toBe(88);
    expect(result.scores.walking.rules_triggered).toHaveLength(1);
    expect(result.scores.quiet.final_score).toBeNull();
  });

  it("does not use a raw relation unless that exact relation is admitted", () => {
    const admittedScoreOnly: SemanticEntity = {
      ...base,
      data_origin: "CANONICAL_TRUTH_ENGINE",
      evidence_condition: "SUPPORTED",
      human_review_state: "APPROVED",
      publish_status: "PUBLISH_ALLOWED",
      geometry_provenance: "DIRECT_SOURCE_GEOMETRY",
      method: "DIRECT",
      derivation: "LOCAL",
      admitted_fact_keys: ["quiet_intelligence"],
      relations: { adjacent_overhead: "Marketplace Buffet" },
    };

    const result = ExplainabilityEngine.explainCabin(admittedScoreOnly, "msc-bellissima");
    expect(result.scores.quiet.rules_triggered).toEqual([]);
    expect(JSON.stringify(result)).not.toMatch(/Marketplace Buffet directly overhead/);
  });
});
