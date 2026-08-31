import { describe, expect, it } from "vitest";

import { CabinIntelligenceEngine } from "./CabinIntelligenceEngine";
import type { SemanticEntity } from "../semantic-deck/types";

function legacyCabin(overrides: Partial<SemanticEntity> = {}): SemanticEntity {
  return {
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
    relations: {},
    unknown_fields: [],
    ...overrides,
  };
}

describe("CabinIntelligenceEngine passenger boundary", () => {
  it("does not turn legacy DIRECT into scores or confidence", () => {
    const intel = CabinIntelligenceEngine.evaluateCabin(legacyCabin(), "msc-bellissima");

    expect(intel.epistemic_confidence).toBeNull();
    expect(intel.side).toBeNull();
    expect(intel.is_accessible).toBeNull();
    expect(intel.has_balcony).toBeNull();
    for (const score of Object.values(intel.scores)) {
      expect(score.score).toBeNull();
      expect(score.grade).toBe("UNAVAILABLE");
      expect(score.factors).toEqual([]);
    }
  });

  it("does not invent lift, corridor, or walking claims when relations are missing", () => {
    const intel = CabinIntelligenceEngine.evaluateCabin(legacyCabin({ relations: {} }), "msc-bellissima");
    const serialized = JSON.stringify(intel);

    expect(intel.walking_score.score).toBeNull();
    expect(serialized).not.toMatch(/lift bank|direct corridor|walking radius/i);
  });

  it("does not expose a numeric confidence when the source value is missing", () => {
    const intel = CabinIntelligenceEngine.evaluateCabin(legacyCabin({ confidence: null }), "msc-bellissima");
    expect(intel.epistemic_confidence).toBeNull();
  });
});
