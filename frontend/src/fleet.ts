/**
 * Official Timonelo Fleet Registry.
 * Multi-class maritime registry spanning ocean mega-liners, river cruise vessels, and expedition twins.
 */

export interface FleetVessel {
  slug: string;
  name: string;
  imo: string;
  operator: string;
  vesselType: 'Ocean Cruise' | 'River Cruise' | 'Expedition';
  shipClass: string;
  lengthM: number;
  beamM: number;
  totalDecks: number;
  cabinCount: number;
  passengerCapacity: number;
  region: string;
  defaultCabin: string;
  compilationStatus: 'VERIFIED_BASELINE' | 'VERIFIED_PATCH';
  badgeText: string;
  description: string;
}

export const FLEET_REGISTRY: FleetVessel[] = [
  {
    slug: 'msc-bellissima',
    name: 'MSC Bellissima',
    imo: 'IMO9766205',
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: 'Meraviglia Class',
    lengthM: 315.83,
    beamM: 43.0,
    totalDecks: 19,
    cabinCount: 2217,
    passengerCapacity: 5655,
    region: 'Mediterranean & Global',
    defaultCabin: '14122',
    compilationStatus: 'VERIFIED_BASELINE',
    badgeText: 'Reference Baseline v1.0',
    description: 'Flagship Meraviglia-class ocean liner with 19 decks, 3 vertical elevator cores, and full multi-deck circulation graph.',
  },
  {
    slug: 'ms-andorinha',
    name: 'MS Andorinha',
    imo: 'ENI02338573',
    operator: 'Tauck / Scylla AG',
    vesselType: 'River Cruise',
    shipClass: 'Douro River Class',
    lengthM: 80.0,
    beamM: 11.4,
    totalDecks: 4,
    cabinCount: 42,
    passengerCapacity: 84,
    region: 'Douro River (Portugal & Spain)',
    defaultCabin: '301',
    compilationStatus: 'VERIFIED_BASELINE',
    badgeText: 'Primary River Twin',
    description: 'Custom-built Douro River luxury vessel with 42 staterooms, The Compass Rose restaurant, Panorama Lounge, and Arthur\'s Bistro.',
  },
  {
    slug: 'msc-grandiosa',
    name: 'MSC Grandiosa',
    imo: 'IMO9803613',
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: 'Meraviglia-Plus Class',
    lengthM: 331.43,
    beamM: 43.0,
    totalDecks: 19,
    cabinCount: 2421,
    passengerCapacity: 6334,
    region: 'Western Mediterranean & Europe',
    defaultCabin: '14122',
    compilationStatus: 'VERIFIED_PATCH',
    badgeText: 'Meraviglia-Plus Twin',
    description: 'Stretched Meraviglia-Plus hull featuring 16m additional midship promenade length and expanded stateroom capacity.',
  },
  {
    slug: 'msc-meraviglia',
    name: 'MSC Meraviglia',
    imo: 'IMO9647710',
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: 'Meraviglia Class',
    lengthM: 315.83,
    beamM: 43.0,
    totalDecks: 19,
    cabinCount: 2217,
    passengerCapacity: 5655,
    region: 'Caribbean & North America',
    defaultCabin: '14122',
    compilationStatus: 'VERIFIED_PATCH',
    badgeText: 'Sister Ship Twin',
    description: 'Pioneering Meraviglia-class sister vessel with identical structural ontology and verified SPEC-008 delta patches.',
  },
];

export function getVesselBySlug(slug: string): FleetVessel {
  return FLEET_REGISTRY.find((v) => v.slug === slug) ?? FLEET_REGISTRY[0];
}
