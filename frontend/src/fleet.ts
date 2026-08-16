// Re-exported from auto-generated knowledge database
import { FLEET_REGISTRY as RAW_FLEET_REGISTRY, type FleetVessel as RawFleetVessel } from './generated/fleet';

function cleanStr(val: any, fallback = ''): string {
  if (typeof val === 'string') return val;
  if (typeof val === 'object' && val !== null) {
    if (typeof val.value === 'string') return val.value;
    if (typeof val.name === 'string') return val.name;
    return String(val.value || val.name || fallback);
  }
  return String(val || fallback);
}

export interface FleetVessel {
  slug: string;
  name: string;
  imo: string;
  operator: string;
  vesselType: 'Ocean Cruise' | 'River Cruise';
  shipClass: string;
  roleTitle: string;
  tagline: string;
  subtitle: string;
  heroImageUrl: string;
  lengthM: number;
  beamM: number;
  totalDecks: number;
  cabinCount: number;
  passengerCapacity: number;
  buildYear: number;
  builder: string;
  region: string;
  defaultCabin: string;
  statusLabel: string;
  description: string;
  highlights: string[];
}

export const FLEET_REGISTRY: FleetVessel[] = RAW_FLEET_REGISTRY.map((v: any) => ({
  ...v,
  shipClass: cleanStr(v.shipClass, 'Cruise Vessel Class'),
  builder: cleanStr(v.builder, 'European Shipyard'),
  roleTitle: cleanStr(v.roleTitle, 'Verified Twin'),
  tagline: cleanStr(v.tagline, 'Evidence-Backed Maritime Intelligence'),
  subtitle: cleanStr(v.subtitle, ''),
  description: cleanStr(v.description, ''),
}));

export function getVesselBySlug(slug: string): FleetVessel {
  const found = FLEET_REGISTRY.find((v) => v.slug === slug);
  return found || FLEET_REGISTRY[0];
}

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
