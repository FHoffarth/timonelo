/**
 * Cabin feature read model.
 *
 * Features are statements about a cabin, not properties of its envelope, so
 * they arrive in their own artifact rather than inside the geometry proof.
 * `deck14.features.json` is a projection of the authored statement graph.
 *
 * The file records positive observations only. A cabin missing from `cabins`
 * has no symbol printed for it on the deck plan, which is UNKNOWN — never a
 * claim that the feature is absent. Callers must not turn an empty list into
 * "no features"; see `UNKNOWN_FEATURES_COPY`.
 */

export const FEATURES_SCHEMA = "timonelo.deck14-cabin-features.v0";
export const FEATURES_URL = "/data/deck14.features.json";

export interface CabinFeature {
  family_id: string;
  label_en: string;
  legend_de: string;
  statement_id: string;
  statement_type: string;
  question_id: string;
  artifact_id: string;
  page: number;
  locator: string;
  method: string;
  derivation_note: string;
  evidence_condition: string;
  human_review_state: string;
  publish_status: string;
}

export interface FeatureFamily {
  family_id: string;
  label_en: string;
  legend_de: string;
  statement_type: string;
  question_id: string;
  derived_from_cardinality: boolean;
}

export interface FeatureDocument {
  schema: string;
  vessel: string;
  deck: number;
  source: {
    artifact_id: string;
    artifact_sha256: string;
    pdf_page_number: number;
    legend_page_number: number;
    document_class: string;
  };
  unknown_guidance: string;
  families: FeatureFamily[];
  cabins: Record<string, CabinFeature[]>;
}

export class FeatureLoadError extends Error {}

/**
 * The only sentence shown when a cabin carries no grounded symbol.
 *
 * Deliberately not "no features" and not "no sofa bed". The deck plan is
 * silent about this stateroom, and silence is not a denial.
 */
export const UNKNOWN_FEATURES_COPY =
  "Other cabin features are not established from the current evidence.";

export function parseFeatures(raw: unknown): FeatureDocument {
  const doc = raw as FeatureDocument;
  if (!doc || typeof doc !== "object") {
    throw new FeatureLoadError("Feature document is not an object.");
  }
  if (doc.schema !== FEATURES_SCHEMA) {
    throw new FeatureLoadError(
      `Unexpected feature schema ${String(doc.schema)}; this viewer only understands ${FEATURES_SCHEMA}.`,
    );
  }
  if (doc.deck !== 14) {
    throw new FeatureLoadError(`Feature document is for deck ${String(doc.deck)}.`);
  }
  if (!doc.cabins || typeof doc.cabins !== "object") {
    throw new FeatureLoadError("Feature document carries no cabins map.");
  }
  return doc;
}

export async function loadFeatures(url: string = FEATURES_URL): Promise<FeatureDocument> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new FeatureLoadError(`Could not load cabin features (${response.status}).`);
  }
  return parseFeatures(await response.json());
}

/**
 * Positively evidenced features for one cabin.
 *
 * Returns an empty array both when the cabin has no symbols and when the
 * cabin is not a cabin at all. Callers render `UNKNOWN_FEATURES_COPY` for the
 * empty case rather than inventing a negative.
 */
export function featuresForCabin(
  doc: FeatureDocument | null,
  cabinNumber: string | undefined,
): CabinFeature[] {
  if (!doc || !cabinNumber) return [];
  return doc.cabins[cabinNumber] ?? [];
}
