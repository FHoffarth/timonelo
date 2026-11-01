import catalog from './fleetCatalog.json';

export const FLEET = catalog;
export type FleetShip = typeof FLEET[number];
export type ProfileSection = 'identity' | 'decks' | 'venues' | 'cabins';
export interface PublishedFact {
  statement_id: string; entity_id: string; question_id: string; statement_type: string;
  section: ProfileSection; value: unknown; artifact_id: string; page: number | null; locator: string;
  publish_status: string;
}
export interface FleetProfileData {
  candidate_count: number; level: number; facts: PublishedFact[];
  sources: { artifact_id: string; sha256: string; filename: string }[];
}
export interface FleetProjection {
  schema: 'timonelo.fleet.v1'; as_of: string; ships: Record<string, FleetProfileData>;
}
export const getFleetShip = (slug: string | undefined) => FLEET.find(s => s.slug === slug);
const record = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const text = (v: unknown): v is string => typeof v === 'string' && v.length > 0;

// Transport validation only. Publication policy lives in Python, never here.
export function parseFleetProjection(value: unknown): FleetProjection | null {
  if (!record(value) || value.schema !== 'timonelo.fleet.v1' || typeof value.as_of !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value.as_of) || !record(value.ships)) return null;
  for (const ship of FLEET) {
    const p = value.ships[ship.slug];
    if (!record(p) || !Number.isInteger(p.candidate_count) || Number(p.candidate_count) < 0 ||
        !Number.isInteger(p.level) || Number(p.level) < 0 || Number(p.level) > 3 || !Array.isArray(p.facts) || !Array.isArray(p.sources)) return null;
    for (const f of p.facts) {
      if (!record(f) || !text(f.statement_id) || !text(f.entity_id) || !text(f.question_id) ||
          !text(f.statement_type) || !['identity', 'decks', 'venues', 'cabins'].includes(String(f.section)) ||
          !text(f.artifact_id) || !text(f.locator) || !text(f.publish_status) || !(f.page === null || Number.isInteger(f.page)) || !('value' in f)) return null;
      if (!f.entity_id.toLowerCase().split(':').includes(ship.slug)) return null;
      if (!p.sources.some(s => record(s) && s.artifact_id === f.artifact_id)) return null;
    }
    if (!p.sources.every(s => record(s) && text(s.artifact_id) && text(s.filename) && typeof s.sha256 === 'string' && /^[a-f0-9]{64}$/.test(s.sha256))) return null;
  }
  return value as unknown as FleetProjection;
}
