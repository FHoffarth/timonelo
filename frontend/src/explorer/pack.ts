/**
 * Canonical Knowledge Pack types + loader.
 *
 * The Explorer consumes a sealed canonical pack (the schema defined by
 * src/timonelo/knowledge_pack). It renders entities, relationships and claims —
 * it never derives new facts, never strengthens a claim, and never hides an
 * Unknown. Any canonical pack renders here; MSC Meraviglia is the migrated one.
 */
import { useEffect, useMemo, useState } from 'react';

export type EvidenceKind = 'source_assertion' | 'deterministic_derivation';

export interface Source {
  source_id: string;
  title: string;
  publisher: string;
  url: string;
  accessed_at: string;
  source_type: string;
  published_at: string | null;
  limitations: string[];
}

export interface Ship {
  entity_id: string;
  name: string;
  operator_name: string;
  source_ids: string[];
  source_locator: string;
  cabin_count: number | null;
  guest_capacity: number | null;
}

export interface Deck {
  entity_id: string;
  ship_id: string;
  number: number;
  name: string;
  ordinal: number;
  source_ids: string[];
  source_locator: string;
}

export interface Cabin {
  entity_id: string;
  ship_id: string;
  deck_id: string;
  number: string;
  category_id: string | null;
  feature_codes: string[];
  source_ids: string[];
  source_locator: string;
  limitations: string[];
}

export interface PublicArea {
  entity_id: string;
  ship_id: string;
  name: string;
  kind: string;
  deck_ids: string[];
  source_ids: string[];
  source_locator: string;
  limitations: string[];
}

export interface Relationship {
  relationship_id: string;
  source_entity_id: string;
  target_entity_id: string;
  kind: string;
  evidence_kind: EvidenceKind;
  source_ids: string[];
  source_locator: string;
  derivation_rule: string | null;
  limitation: string | null;
}

export interface Claim {
  claim_id: string;
  subject_entity_id: string;
  predicate: string;
  statement: string;
  value: unknown;
  unit: string | null;
  evidence_kind: EvidenceKind;
  source_ids: string[];
  source_locator: string;
  derivation_rule: string | null;
  limitation: string | null;
}

export interface KnowledgePack {
  schema_version: string;
  pack_id: string;
  version: string;
  effective_date: string;
  status: string;
  limitations: string[];
  sources: Source[];
  ship: Ship;
  decks: Deck[];
  cabin_categories: unknown[];
  cabins: Cabin[];
  public_areas: PublicArea[];
  relationships: Relationship[];
  claims: Claim[];
}

/** Motion profile carried as a canonical claim value. */
export interface MotionProfile {
  overall: string | null;
  pitch: string | null;
  roll: string | null;
  longitudinal_position: string | null;
  vertical_zone: string | null;
  distance_from_midship_m: number | null;
}
export interface NoiseValue {
  sources: string[];
  confidence: number | null;
}

/** Indexed, read-only view over a pack. Built once per pack. */
export class PackModel {
  readonly pack: KnowledgePack;
  private cabinsByDeck = new Map<string, Cabin[]>();
  private areasByDeck = new Map<string, PublicArea[]>();
  private claimsBySubject = new Map<string, Claim[]>();
  private relsBySource = new Map<string, Relationship[]>();
  private deckByNumber = new Map<number, Deck>();
  private cabinByNumber = new Map<string, Cabin>();
  private sourceById = new Map<string, Source>();

  constructor(pack: KnowledgePack) {
    this.pack = pack;
    for (const s of pack.sources) this.sourceById.set(s.source_id, s);
    for (const d of pack.decks) this.deckByNumber.set(d.number, d);
    for (const c of pack.cabins) {
      this.cabinByNumber.set(c.number, c);
      push(this.cabinsByDeck, c.deck_id, c);
    }
    for (const a of pack.public_areas) for (const d of a.deck_ids) push(this.areasByDeck, d, a);
    for (const cl of pack.claims) push(this.claimsBySubject, cl.subject_entity_id, cl);
    for (const r of pack.relationships) push(this.relsBySource, r.source_entity_id, r);
  }

  get ship() {
    return this.pack.ship;
  }
  get primarySource() {
    return this.pack.sources[0];
  }
  source(id: string) {
    return this.sourceById.get(id);
  }

  decksTopToBottom(): Deck[] {
    return [...this.pack.decks].sort((a, b) => b.number - a.number);
  }
  deck(number: number): Deck | undefined {
    return this.deckByNumber.get(number);
  }
  cabin(number: string): Cabin | undefined {
    return this.cabinByNumber.get(number);
  }
  cabinsOnDeck(deckId: string): Cabin[] {
    return (this.cabinsByDeck.get(deckId) ?? []).slice().sort((a, b) =>
      a.number.localeCompare(b.number, undefined, { numeric: true }),
    );
  }
  areasOnDeck(deckId: string): PublicArea[] {
    return (this.areasByDeck.get(deckId) ?? []).slice().sort((a, b) => a.name.localeCompare(b.name));
  }
  claimsFor(entityId: string): Claim[] {
    return this.claimsBySubject.get(entityId) ?? [];
  }
  claim(entityId: string, predicate: string): Claim | undefined {
    return this.claimsFor(entityId).find((c) => c.predicate === predicate);
  }

  /** Deck directly above D: the deck D is "below" (relationship kind=below). */
  deckAbove(deckId: string): Deck | undefined {
    const rel = (this.relsBySource.get(deckId) ?? []).find((r) => r.kind === 'below');
    return rel ? this.pack.decks.find((d) => d.entity_id === rel.target_entity_id) : undefined;
  }
  /** Deck directly below D: the deck D is "above" (relationship kind=above). */
  deckBelow(deckId: string): Deck | undefined {
    const rel = (this.relsBySource.get(deckId) ?? []).find((r) => r.kind === 'above');
    return rel ? this.pack.decks.find((d) => d.entity_id === rel.target_entity_id) : undefined;
  }
  deckRelationship(deckId: string, wantAbove: boolean): Relationship | undefined {
    return (this.relsBySource.get(deckId) ?? []).find((r) => r.kind === (wantAbove ? 'below' : 'above'));
  }
}

function push<K, V>(map: Map<K, V[]>, key: K, value: V) {
  const list = map.get(key);
  if (list) list.push(value);
  else map.set(key, [value]);
}

const CACHE = new Map<string, KnowledgePack>();

export function usePack(shipId: string) {
  const [pack, setPack] = useState<KnowledgePack | null>(CACHE.get(shipId) ?? null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (CACHE.has(shipId)) {
      setPack(CACHE.get(shipId)!);
      return;
    }
    let alive = true;
    fetch(`${import.meta.env.BASE_URL}packs/${shipId}.pack.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`Pack ${shipId} not found`);
        return r.json();
      })
      .then((data: KnowledgePack) => {
        CACHE.set(shipId, data);
        if (alive) setPack(data);
      })
      .catch((e) => alive && setError(String(e.message ?? e)));
    return () => {
      alive = false;
    };
  }, [shipId]);

  const model = useMemo(() => (pack ? new PackModel(pack) : null), [pack]);
  return { model, error };
}
