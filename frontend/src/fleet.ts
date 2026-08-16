// Re-exported from auto-generated knowledge database
import { FLEET_REGISTRY as RAW_FLEET_REGISTRY } from './generated/fleet';

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
  roleTitle: cleanStr(v.roleTitle, 'Active Reference Model'),
  tagline: cleanStr(v.tagline, 'Evidence-Backed Maritime Intelligence'),
  subtitle: cleanStr(v.subtitle, ''),
  description: cleanStr(v.description, ''),
}));

export function getVesselBySlug(slug: string): FleetVessel {
  const found = FLEET_REGISTRY.find((v) => v.slug === slug);
  return found || FLEET_REGISTRY[0];
}
