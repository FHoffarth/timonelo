import knowledgePackDocument from '../../../data/ships/msc-bellissima/knowledge-pack.json';

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
  cabin_count: number | null;
  guest_capacity: number | null;
  source_ids: string[];
  source_locator: string;
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

export interface CabinCategory {
  entity_id: string;
  code: string;
  name: string;
  accommodation_type: 'interior' | 'ocean_view' | 'balcony' | 'suite';
  deck_numbers: number[];
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
  evidence_kind: 'source_assertion' | 'deterministic_derivation';
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
  evidence_kind: 'source_assertion' | 'deterministic_derivation';
  source_ids: string[];
  source_locator: string;
  derivation_rule: string | null;
  limitation: string | null;
}

interface KnowledgePack {
  schema_version: string;
  pack_id: string;
  version: string;
  effective_date: string;
  status: string;
  limitations: string[];
  sources: Source[];
  ship: Ship;
  decks: Deck[];
  cabin_categories: CabinCategory[];
  cabins: Cabin[];
  public_areas: PublicArea[];
  relationships: Relationship[];
  claims: Claim[];
}

export const knowledgePack = knowledgePackDocument as KnowledgePack;

const decksById = new Map(knowledgePack.decks.map((deck) => [deck.entity_id, deck]));
const cabinsByNumber = new Map(knowledgePack.cabins.map((cabin) => [cabin.number, cabin]));
const categoriesById = new Map(knowledgePack.cabin_categories.map((category) => [category.entity_id, category]));
const sourcesById = new Map(knowledgePack.sources.map((source) => [source.source_id, source]));

export function deckPath(deck: Deck): string {
  return `/explore/decks/${deck.number}`;
}

export function cabinPath(cabin: Cabin): string {
  return `/explore/cabins/${cabin.number}`;
}

export function getDeck(number: number): Deck | undefined {
  return knowledgePack.decks.find((deck) => deck.number === number);
}

export function getDeckById(id: string): Deck | undefined {
  return decksById.get(id);
}

export function getCabin(number: string): Cabin | undefined {
  return cabinsByNumber.get(number);
}

export function getCabinsOnDeck(deckId: string): Cabin[] {
  return knowledgePack.cabins.filter((cabin) => cabin.deck_id === deckId);
}

export function getPublicAreasOnDeck(deckId: string): PublicArea[] {
  return knowledgePack.public_areas.filter((area) => area.deck_ids.includes(deckId));
}

export function getCategory(id: string | null): CabinCategory | undefined {
  return id ? categoriesById.get(id) : undefined;
}

export function getSources(ids: string[]): Source[] {
  return ids.flatMap((id) => {
    const source = sourcesById.get(id);
    return source ? [source] : [];
  });
}

export function getClaimsFor(entityId: string): Claim[] {
  return knowledgePack.claims.filter((claim) => claim.subject_entity_id === entityId);
}

export function getRelationshipsFor(entityId: string): Relationship[] {
  return knowledgePack.relationships.filter(
    (relationship) => relationship.source_entity_id === entityId || relationship.target_entity_id === entityId,
  );
}

export function getEntityName(entityId: string): string {
  if (entityId === knowledgePack.ship.entity_id) return knowledgePack.ship.name;
  const deck = decksById.get(entityId);
  if (deck) return `Deck ${deck.number} — ${deck.name}`;
  const cabin = knowledgePack.cabins.find((item) => item.entity_id === entityId);
  if (cabin) return `Cabin ${cabin.number}`;
  const area = knowledgePack.public_areas.find((item) => item.entity_id === entityId);
  if (area) return area.name;
  return entityId;
}

export function getEntityPath(entityId: string): string | undefined {
  const deck = decksById.get(entityId);
  if (deck) return deckPath(deck);
  const cabin = knowledgePack.cabins.find((item) => item.entity_id === entityId);
  if (cabin) return cabinPath(cabin);
  if (entityId === knowledgePack.ship.entity_id) return '/explore/ships/msc-bellissima';
  return undefined;
}

export function formatEvidenceKind(kind: Relationship['evidence_kind']): string {
  return kind === 'source_assertion' ? 'Source assertion' : 'Deterministic derivation';
}

export function formatFeatureCode(code: string): string {
  const known: Record<string, string> = {
    'bunk-bed-only': 'Bunk bed only',
    'crystal-cabin': 'Crystal cabin',
  };
  return known[code] ?? code.replaceAll('-', ' ');
}

export function formatKind(kind: string): string {
  return kind.replaceAll('_', ' ').replace(/^./, (character) => character.toUpperCase());
}
