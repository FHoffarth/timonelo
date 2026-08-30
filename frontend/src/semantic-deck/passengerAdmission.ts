/**
 * Single frontend admission boundary for passenger-facing spatial facts.
 *
 * These fields mirror the canonical Gatekeeper/SpatialGraph axes. Legacy
 * semantic state (`DIRECT`, `PUBLISHED_VERIFIED`, stored confidence) is not an
 * admission signal and is deliberately absent from this predicate.
 */

import type {
  Derivation,
  EvidenceCondition,
  GeometryProvenance,
  HumanReviewState,
  Method,
  PublishStatus,
} from "../generated/canon";

export type PassengerDataOrigin =
  | "CANONICAL_TRUTH_ENGINE"
  | "LEGACY_SCHEMATIC";

export type PassengerFactKey =
  | "identity"
  | "deck"
  | "classification"
  | "side"
  | "zone"
  | "accessible_designation"
  | "connecting_cabin"
  | "balcony"
  | "interior_area"
  | "balcony_area"
  | "bed_configuration"
  | "source_artifact"
  | "source_envelope"
  | "adjacent_fore"
  | "adjacent_aft"
  | "adjacent_across"
  | "adjacent_overhead"
  | "adjacent_underfoot"
  | "corridor_connectivity"
  | "connected_vertical_core"
  | "metric_distance"
  | "walking_time"
  | "quiet_intelligence"
  | "motion_intelligence"
  | "walking_intelligence"
  | "privacy_intelligence"
  | "accessibility_intelligence"
  | "family_intelligence"
  | "couple_intelligence";

export interface PassengerAdmission {
  data_origin: PassengerDataOrigin;
  evidence_condition: EvidenceCondition;
  human_review_state: HumanReviewState;
  publish_status: PublishStatus;
  geometry_provenance: GeometryProvenance;
  method: Method | null;
  derivation: Derivation | null;
  admitted_fact_keys: PassengerFactKey[];
}

const GEOMETRY_FACTS = new Set<PassengerFactKey>([
  "source_envelope",
  "interior_area",
  "balcony_area",
  "side",
  "zone",
  "adjacent_fore",
  "adjacent_aft",
  "adjacent_across",
  "adjacent_overhead",
  "adjacent_underfoot",
  "corridor_connectivity",
  "connected_vertical_core",
  "metric_distance",
  "walking_time",
]);

const GEOMETRY_QUALIFIED = new Set<GeometryProvenance>([
  "DIRECT_SOURCE_GEOMETRY",
  "TRANSFORMED_SOURCE_GEOMETRY",
  "DERIVED_GEOMETRY",
]);

export function isPassengerEntityAdmitted(
  admission: Partial<PassengerAdmission>,
): boolean {
  const hasAdmissibleMethod =
    admission.method === "DIRECT" ||
    admission.method === "CALCULATED" ||
    admission.method === "INFERRED";
  const hasAdmissibleDerivation =
    admission.derivation === "LOCAL" ||
    admission.derivation === "SISTER_SHIP" ||
    admission.derivation === "REFERENCE_MODEL";
  return (
    admission.data_origin === "CANONICAL_TRUTH_ENGINE" &&
    admission.evidence_condition === "SUPPORTED" &&
    admission.human_review_state === "APPROVED" &&
    (admission.publish_status === "PUBLISH_ALLOWED" ||
      admission.publish_status === "PUBLISH_ALLOWED_WITH_WARNINGS") &&
    hasAdmissibleMethod &&
    hasAdmissibleDerivation
  );
}

export function isPassengerFactAdmitted(
  admission: Partial<PassengerAdmission>,
  fact: PassengerFactKey,
): boolean {
  if (!isPassengerEntityAdmitted(admission)) return false;
  if (!(admission.admitted_fact_keys || []).includes(fact)) return false;
  if (GEOMETRY_FACTS.has(fact)) {
    return (
      admission.method !== "INFERRED" &&
      GEOMETRY_QUALIFIED.has(admission.geometry_provenance as GeometryProvenance)
    );
  }
  return true;
}

/** Return a value only when its exact fact key crossed the canonical gate. */
export function getPassengerFact<T>(
  admission: Partial<PassengerAdmission>,
  fact: PassengerFactKey,
  value: T,
): T | null {
  return isPassengerFactAdmitted(admission, fact) ? value : null;
}

export const LEGACY_SCHEMATIC_ADMISSION: PassengerAdmission = {
  data_origin: "LEGACY_SCHEMATIC",
  evidence_condition: "UNKNOWN",
  human_review_state: "DRAFT",
  publish_status: "PUBLISH_BLOCKED",
  geometry_provenance: "UNKNOWN_PROVENANCE",
  method: null,
  derivation: null,
  admitted_fact_keys: [],
};
