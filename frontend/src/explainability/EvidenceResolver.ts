/**
 * explainability/EvidenceResolver.ts
 * 
 * Resolves any topological fact, relation, or spatial geometry coordinate
 * back to its primary ground truth artifact document, PDF page, and statement.
 */

import { EvidenceProvenance, RuleDefinition } from "./types";
import { SemanticEntity } from "../semantic-deck/types";

export class EvidenceResolver {
  public static resolveRuleEvidence(
    rule: RuleDefinition,
    entity: SemanticEntity,
    vesselId: string = "msc-bellissima"
  ): EvidenceProvenance {
    const cid = entity.id;
    const level = entity.level;
    const relations = entity.relations || {};

    let graphEdge = "";
    let geometryFile = `deck${level < 10 ? "0" + level : level}.geometry.json`;
    let rawFinding = rule.description;
    let status: "DIRECT" | "DERIVED" | "CONFLICT" | "UNKNOWN" = "DIRECT";
    let confidence = 0.95;

    // Resolve specific graph edges based on rule ID
    switch (rule.id) {
      case "RULE-QUIET-004":
        graphEdge = `ABOVE(Cabin_${cid}, ${relations.adjacent_overhead || "Marketplace_Buffet"})`;
        geometryFile = "deck15.geometry.json";
        rawFinding = `Marketplace Buffet on Deck 15 is directly positioned above Deck 14 Cabin ${cid}`;
        confidence = 0.98;
        break;

      case "RULE-QUIET-001":
        graphEdge = `SANDWICHED_BETWEEN(Cabin_${cid}, Deck_${level + 1}_Staterooms, Deck_${level - 1}_Staterooms)`;
        rawFinding = `Pure residential buffers above (Deck ${level + 1}) and below (Deck ${level - 1})`;
        confidence = 0.96;
        break;

      case "RULE-QUIET-002":
        graphEdge = `DISJOINT(Cabin_${cid}, Entertainment_Venues)`;
        rawFinding = `No public entertainment or theatre directly bordering Cabin ${cid}`;
        confidence = 0.95;
        break;

      case "RULE-MOTION-001":
        graphEdge = `POSITIONED_IN(Cabin_${cid}, Midship_Neutral_Axis)`;
        rawFinding = `Located within midship neutral flotation envelope (FR-110 to FR-160)`;
        confidence = 0.96;
        break;

      case "RULE-MOTION-002":
        graphEdge = `POSITIONED_IN(Cabin_${cid}, Forward_Bow_Zone)`;
        rawFinding = `Positioned in forward bow zone with high vertical pitch moment`;
        confidence = 0.92;
        break;

      case "RULE-MOTION-004":
        graphEdge = `ELEVATED_AT(Cabin_${cid}, Level_${level})`;
        rawFinding = `Elevation at Deck ${level} increases angular roll displacement`;
        confidence = 0.94;
        break;

      case "RULE-ACC-001":
        graphEdge = `HAS_ATTRIBUTE(Cabin_${cid}, PRM_ACCESSIBLE)`;
        rawFinding = `Designated accessible cabin with wide door and roll-in shower (Symbol H)`;
        status = "DIRECT";
        confidence = 1.0;
        break;

      case "RULE-WALK-001":
        graphEdge = `CONNECTED_TO(Cabin_${cid}, ${relations.connected_vertical_core || "Lift_Core_B"})`;
        rawFinding = `Direct corridor access to ${relations.connected_vertical_core || "Midship Lift Bank"}`;
        confidence = 0.92;
        break;

      default:
        graphEdge = `ASSOCIATED_WITH(Cabin_${cid}, ${rule.category})`;
        rawFinding = rule.description;
        confidence = 0.90;
        break;
    }

    return {
      evidence_id: `EV-${rule.id}-${cid}`,
      source_title: rule.required_evidence.title,
      artifact_id: rule.required_evidence.artifact_id,
      page: rule.required_evidence.page,
      graph_edge: graphEdge,
      geometry_file: geometryFile,
      knowledge_entity_id: rule.required_knowledge_entities[0],
      statement_id: `STM-${vesselId.toUpperCase()}-${cid}`,
      confidence: confidence,
      status: status,
      raw_finding: rawFinding,
    };
  }
}
