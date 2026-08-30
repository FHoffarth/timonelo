/**
 * explainability/EvidenceResolver.ts
 *
 * Resolves a rule's provenance from the entity's canonical evidence only.
 *
 * P0-H2 FAIL-CLOSED: this resolver must never synthesize evidence, provenance,
 * or trust. Every returned field is either a real value carried by the
 * SemanticEntity (evidence_links / statements / epistemic_state / confidence)
 * or null. No invented evidence or statement identifiers, no hardcoded DIRECT
 * status, no hardcoded confidence, no unverified geometry filename, and no
 * entity-specific physical claims.
 */

import type { EvidenceProvenance, RuleDefinition } from "./types";
import type { SemanticEntity } from "../semantic-deck/types";
import type { PassengerFactKey } from "../semantic-deck/passengerAdmission";

export interface ResolvedPassengerAdmission {
  entityAdmitted: boolean;
  admittedFactKeys: ReadonlySet<PassengerFactKey>;
}

// Keys in required_graph_relations that are entity attributes rather than
// entries in entity.relations.
const ENTITY_ATTRIBUTE_KEYS = new Set([
  "level",
  "zone",
  "side",
  "accessible",
  "has_balcony",
  "connecting",
]);

const REQUIRED_KEY_FACTS: Record<string, PassengerFactKey> = {
  level: "deck",
  zone: "zone",
  side: "side",
  accessible: "accessible_designation",
  has_balcony: "balcony",
  connecting: "connecting_cabin",
  adjacent_fore: "adjacent_fore",
  adjacent_aft: "adjacent_aft",
  adjacent_across: "adjacent_across",
  adjacent_overhead: "adjacent_overhead",
  adjacent_underfoot: "adjacent_underfoot",
  connected_vertical_core: "connected_vertical_core",
};

/**
 * Resolve one required key to a real value on the entity, or null.
 * Never invents a fallback.
 */
function resolveRequiredKey(
  entity: SemanticEntity,
  key: string,
  admittedFactKeys: ReadonlySet<PassengerFactKey>,
): string | null {
  const fact = REQUIRED_KEY_FACTS[key];
  if (!fact || !admittedFactKeys.has(fact)) return null;
  if (ENTITY_ATTRIBUTE_KEYS.has(key)) {
    const val = (entity as unknown as Record<string, unknown>)[key];
    if (val === undefined || val === null || val === "") return null;
    return String(val);
  }
  const rel = (entity.relations || {})[key];
  if (rel === undefined || rel === null || rel === "") return null;
  return String(rel);
}

export class EvidenceResolver {
  public static resolveRuleEvidence(
    rule: RuleDefinition,
    entity: SemanticEntity,
    _vesselId: string = "msc-bellissima",
    admission?: ResolvedPassengerAdmission,
  ): EvidenceProvenance {
    const cid = entity.id;

    if (!admission?.entityAdmitted) {
      return {
        evidence_id: null,
        source_title: null,
        artifact_id: null,
        graph_edge: null,
        geometry_file: null,
        knowledge_entity_id: rule.required_knowledge_entities?.[0],
        statement_id: null,
        confidence: null,
        status: "UNKNOWN",
        raw_finding: rule.description,
      };
    }

    // Canonical evidence for this entity. Absent -> everything fails closed.
    const sourceAdmitted = admission.admittedFactKeys.has("source_artifact");
    const link = sourceAdmitted ? (entity.evidence_links || [])[0] : undefined;

    // graph_edge is emitted only when every relation/attribute the rule
    // requires resolves to a real value on the entity. The edge text restates
    // those resolved bindings; it never asserts an unbacked topology claim.
    const requiredKeys = rule.required_graph_relations || [];
    let graphEdge: string | null = null;
    if (requiredKeys.length > 0) {
      const bindings: string[] = [];
      let allResolved = true;
      for (const key of requiredKeys) {
        const value = resolveRequiredKey(entity, key, admission.admittedFactKeys);
        if (value === null) {
          allResolved = false;
          break;
        }
        bindings.push(`${key}(Cabin_${cid}) = ${value}`);
      }
      if (allResolved) graphEdge = bindings.join("; ");
    }

    return {
      // No canonical evidence identifier exists in the source data.
      evidence_id: null,
      source_title: link?.source_title ?? null,
      artifact_id: link?.artifact_id ?? null,
      page: link?.page,
      locator: link?.locator ?? null,
      graph_edge: graphEdge,
      // Geometry files are not verified from the frontend.
      geometry_file: null,
      knowledge_entity_id: rule.required_knowledge_entities?.[0],
      statement_id: sourceAdmitted ? entity.statements?.[0] ?? null : null,
      confidence: typeof entity.confidence === "number" ? entity.confidence : null,
      status: entity.epistemic_state === "DIRECT" || entity.epistemic_state === "DERIVED"
        ? entity.epistemic_state
        : "UNKNOWN",
      // Neutral rule description only — never an entity-specific invented claim.
      raw_finding: rule.description,
    };
  }
}
