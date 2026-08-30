// P0-D fail-closed cabin resolution.
//
// A cabin ID is only "known" if it is backed by real data: either a canonical
// frontend record, or a real entity in the active spatial knowledge graph.
// Unknown IDs MUST NOT be substituted with another cabin (e.g. 14122) and MUST
// NOT have synthetic DIRECT / PUBLISHED_VERIFIED / confidence / adjacency facts
// fabricated for them.

/**
 * Returns true only when the requested cabin ID has real backing data.
 *
 * @param cabinId        The requested cabin ID (as routed / searched).
 * @param canonical      The canonical frontend cabin map (CANONICAL_CABINS).
 * @param lookupEntity   Spatial-graph entity lookup (apiClient.getEntity).
 */
export function isKnownCabin(
  cabinId: string | undefined | null,
  canonical: Record<string, unknown>,
  lookupEntity: (id: string) => unknown,
): boolean {
  if (!cabinId) return false;
  if (canonical[cabinId] != null) return true;
  if (lookupEntity(cabinId) != null) return true;
  return false;
}

// Minimal shape of a spatial-graph entity that this resolver reads.
export interface GraphEntityLike {
  level: number;
  level_name: string;
  classification_label: string;
  side: string;
  zone: string;
  accessible: boolean;
  evidence_links?: Array<{ artifact_id?: string | null }>;
}

// Resolved cabin metadata for the deep-dive render. Canonical fields the graph
// does not carry are null and MUST render as "Unavailable" — never borrowed
// from another cabin.
export interface ResolvedCabinMeta {
  id: string;
  shipSlug: string;
  deckNumber: number;
  deckName: string;
  category: string;
  tier: string | null;
  side: string;
  zone: string;
  sqmInterior: number | null;
  sqmBalcony: number | null;
  bedConfig: string | null;
  connectingCabinId: string | undefined;
  isPRM: boolean;
  heroImageUrl: string | null;
  evidenceArtifactId: string | null;
}

/**
 * P0-D follow-up: resolve the metadata used to render a known cabin.
 *
 * - Canonical record present -> return it verbatim (behavior unchanged).
 * - Graph-only cabin (no canonical record) -> derive ONLY from its own graph
 *   entity; fields the graph does not provide stay null (render "Unavailable").
 *   Never substitutes another cabin's (e.g. 14122) metadata.
 * - Neither -> null (caller handles the unknown / fail-closed path).
 */
export function resolveCabinMeta<T>(
  cabinId: string,
  canonicalCabin: T | undefined,
  knownEntity: GraphEntityLike | undefined | null,
): T | ResolvedCabinMeta | null {
  if (canonicalCabin != null) return canonicalCabin;
  if (knownEntity != null) {
    return {
      id: cabinId,
      shipSlug: "msc-bellissima",
      deckNumber: knownEntity.level,
      deckName: knownEntity.level_name,
      category: knownEntity.classification_label,
      tier: null,
      side: knownEntity.side,
      zone: knownEntity.zone,
      sqmInterior: null,
      sqmBalcony: null,
      bedConfig: null,
      connectingCabinId: undefined,
      isPRM: knownEntity.accessible,
      heroImageUrl: null,
      evidenceArtifactId: knownEntity.evidence_links?.[0]?.artifact_id ?? null,
    };
  }
  return null;
}
