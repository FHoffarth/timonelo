/**
 * Loading and point-picking for the Deck 14 geometry proof.
 *
 * The loader fails closed. A document whose schema or deck does not match is
 * rejected rather than rendered partially: a viewer that silently displays the
 * wrong artifact is worse than one that refuses to open.
 */

import {
  PROOF_DECK_NUMBER,
  PROOF_SCHEMA,
  type ProofDocument,
  type ProofObject,
} from "./proofTypes";

export const PROOF_URL = "/data/deck14.proof.json";

export class ProofLoadError extends Error {}

/** Validates identity before anything is rendered. */
export function parseProof(raw: unknown): ProofDocument {
  const doc = raw as ProofDocument;
  if (!doc || typeof doc !== "object") {
    throw new ProofLoadError("Proof document is not an object.");
  }
  if (doc.schema !== PROOF_SCHEMA) {
    throw new ProofLoadError(
      `Unexpected proof schema ${String(doc.schema)}; this viewer only understands ${PROOF_SCHEMA}.`,
    );
  }
  if (doc.deck?.number !== PROOF_DECK_NUMBER) {
    throw new ProofLoadError(
      `Proof is for deck ${String(doc.deck?.number)}; this viewer is locked to Deck ${PROOF_DECK_NUMBER}.`,
    );
  }
  if (!Array.isArray(doc.objects)) {
    throw new ProofLoadError("Proof document carries no objects array.");
  }
  return doc;
}

export async function loadProof(url: string = PROOF_URL): Promise<ProofDocument> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new ProofLoadError(`Could not load the proof artifact (${response.status}).`);
  }
  return parseProof(await response.json());
}

/**
 * Picks one object at a normalized point, deterministically.
 *
 * Native SVG hit-testing is not usable here. Five pairs of vertically adjacent
 * cabins overlap by 0.0002-0.0108 pt in the source (roughly 3 micrometres on the
 * printed page, from vector rounding around a shared edge), so inside those bands
 * two envelopes genuinely contain the same point and "topmost element wins" would
 * depend on DOM order.
 *
 * Tie-break: smallest area first, then object_id ascending. The same point always
 * resolves to the same object regardless of render order.
 */
export function pickObjectAt(
  objects: ProofObject[],
  x: number,
  y: number,
): ProofObject | null {
  const hits = objects.filter(
    (o) =>
      x >= o.normalized_bbox[0] &&
      x <= o.normalized_bbox[2] &&
      y >= o.normalized_bbox[1] &&
      y <= o.normalized_bbox[3],
  );
  if (hits.length === 0) return null;
  const area = (o: ProofObject) =>
    (o.normalized_bbox[2] - o.normalized_bbox[0]) *
    (o.normalized_bbox[3] - o.normalized_bbox[1]);
  return [...hits].sort(
    (a, b) => area(a) - area(b) || a.object_id.localeCompare(b.object_id),
  )[0];
}

/**
 * Whether any connectivity is evidenced on this deck.
 *
 * Deliberately conservative: connectivity requires an actual navigation graph.
 * Cabin envelopes establish where things are, not that one can walk between them.
 */
export function hasAdmittedConnectivity(doc: ProofDocument): boolean {
  return doc.navigation_graph !== null && doc.navigation_graph !== undefined;
}
