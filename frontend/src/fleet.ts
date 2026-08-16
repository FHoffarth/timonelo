// Re-exported from auto-generated knowledge database
export * from './generated/fleet';

export interface UpcomingOperator {
  name: string;
  category: string;
  region: string;
  note: string;
}

export const UPCOMING_OPERATORS: UpcomingOperator[] = [
  {
    name: 'Disney Cruise Line',
    category: 'Family Ocean Cruising',
    region: 'Caribbean & Global',
    note: 'Family stateroom layouts & split bath configurations',
  },
  {
    name: 'Viking River Cruises',
    category: 'European River Cruising',
    region: 'Rhine, Danube & Seine',
    note: 'Longship asymmetric corridors & riverbank sightlines',
  },
  {
    name: 'Royal Caribbean',
    category: 'Ocean Mega-Liners',
    region: 'Caribbean & Mediterranean',
    note: 'Open-air central neighborhoods & multi-deck promenades',
  },
  {
    name: 'Celebrity Cruises',
    category: 'Modern Ocean Cruising',
    region: 'Global Routes',
    note: 'Edge-series cantilevered lounges & infinite verandas',
  },
  {
    name: 'AIDA Cruises',
    category: 'Casual Ocean Cruising',
    region: 'Canaries & Mediterranean',
    note: '360-degree Theatrium & organic buffet concepts',
  },
];

export const UPCOMING_EXPANSIONS = UPCOMING_OPERATORS;

export function getPlatformPrinciplesSummary() {
  return [
    { title: 'Negative Intelligence', desc: 'Prevent regretful cabin choices before booking.' },
    { title: '15-Second Clarity', desc: 'Instant spatial and vertical deck orientation.' },
    { title: 'Verifiable Evidence', desc: 'Backed strictly by official shipyard and port records.' },
  ];
}
