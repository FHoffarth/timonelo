/**
 * Presentation helpers. These format canonical values into human labels.
 * They never change a value's meaning and never invent a value where the pack
 * carries none — a null renders as an explicit "Unknown", never as blank.
 */

export function titleCase(s: string): string {
  return s.replace(/[_-]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const SOURCE_TYPE_LABELS: Record<string, string> = {
  official_technical_sheet: 'Official technical sheet',
  official_deck_plan: 'Official deck plan',
  third_party_deck_plan: 'Third-party deck plan',
  ship_page: 'Official ship page',
};

export function sourceTypeLabel(t: string): string {
  return SOURCE_TYPE_LABELS[t] ?? titleCase(t);
}

const MATURITY: Record<string, { label: string; rung: number }> = {
  structured: { label: 'Structured', rung: 1 },
  verified: { label: 'Verified', rung: 2 },
  field_validated: { label: 'Field Validated', rung: 3 },
  knowledge_complete: { label: 'Knowledge Complete', rung: 4 },
  reference: { label: 'Reference', rung: 4 },
};

export function maturityLabel(m: string): string {
  return MATURITY[m]?.label ?? titleCase(m);
}
export function maturityRung(m: string): number {
  return MATURITY[m]?.rung ?? 0;
}
export const MATURITY_LADDER = ['structured', 'verified', 'field_validated', 'knowledge_complete'];

const AREA_KIND_LABELS: Record<string, string> = {
  dining: 'Dining',
  entertainment: 'Entertainment',
  guest_service: 'Guest service',
  lounge: 'Bar & lounge',
  promenade: 'Promenade & deck',
  recreation: 'Recreation',
  retail: 'Retail',
  wellness: 'Wellness',
};
export function areaKindLabel(k: string): string {
  return AREA_KIND_LABELS[k] ?? titleCase(k);
}

const NOISE_SOURCE_LABELS: Record<string, string> = {
  lift_adjacent: 'Adjacent to a lift shaft',
  stair_adjacent: 'Adjacent to a stairwell',
  restaurant_adjacent: 'Adjacent to a restaurant',
  nightlife_below: 'Nightlife venue on the deck below',
  nightlife_above: 'Nightlife venue on the deck above',
  public_above: 'Public venue on the deck above',
  public_below: 'Public venue on the deck below',
};
export function noiseSourceLabel(s: string): string {
  return NOISE_SOURCE_LABELS[s] ?? titleCase(s);
}

export function exposureTone(level: string | null): 'low' | 'medium' | 'high' | 'unknown' {
  if (level === 'low' || level === 'medium' || level === 'high') return level;
  return 'unknown';
}

export function valueOrUnknown(v: string | null | undefined): string {
  return v == null || v === '' ? 'Unknown' : titleCase(v);
}
export function metres(v: number | null | undefined): string {
  return v == null ? 'Unknown' : `${v} m`;
}
