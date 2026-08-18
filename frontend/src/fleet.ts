import { knowledgeRepository } from './knowledge';

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

// Load canonical Bellissima specs from KnowledgeRepository
const bellissimaKnowledge = knowledgeRepository.getShip('msc-bellissima');
const bellissimaCabins = knowledgeRepository.getCabins('msc-bellissima');
const bellissimaPublic = knowledgeRepository.getPublicAreas('msc-bellissima');
const bellissimaEnt = knowledgeRepository.getEntertainment('msc-bellissima');

const galleriaArea = bellissimaPublic.find((p) => p.id === 'PUB-GALLERIA-BELLISSIMA');
const mainTheatre = bellissimaEnt.find((e) => e.id === 'ENT-LONDON-THEATRE');

export const FLEET_REGISTRY: FleetVessel[] = [
  {
    slug: bellissimaKnowledge.vessel_id,
    name: bellissimaKnowledge.vessel_name,
    imo: `IMO ${bellissimaKnowledge.technical_specifications.imo_number}`,
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: bellissimaKnowledge.technical_specifications.class,
    roleTitle: 'Active Reference Model',
    tagline: galleriaArea ? `${galleriaArea.name} with ${galleriaArea.description}` : 'High-tech flagship with LED promenade.',
    subtitle: `MSC Cruises · ${bellissimaKnowledge.technical_specifications.class} · Delivery ${bellissimaKnowledge.technical_specifications.key_milestones.maiden_voyage ? parseInt(bellissimaKnowledge.technical_specifications.key_milestones.maiden_voyage) : 2019}`,
    heroImageUrl: '/media/msc-bellissima-hero.webp',
    lengthM: bellissimaKnowledge.technical_specifications.dimensions.length_meters,
    beamM: bellissimaKnowledge.technical_specifications.dimensions.beam_meters,
    totalDecks: bellissimaKnowledge.technical_specifications.capacities.total_decks,
    cabinCount: bellissimaCabins ? bellissimaCabins.summary.total_staterooms : bellissimaKnowledge.technical_specifications.capacities.total_cabins_max,
    passengerCapacity: bellissimaKnowledge.technical_specifications.capacities.passenger_capacity_max_occupancy,
    buildYear: bellissimaKnowledge.technical_specifications.key_milestones.maiden_voyage ? parseInt(bellissimaKnowledge.technical_specifications.key_milestones.maiden_voyage) : 2019,
    builder: bellissimaKnowledge.technical_specifications.builder,
    region: 'Mediterranean & East Asia',
    defaultCabin: '14122',
    statusLabel: 'Active Reference Model',
    description: `${bellissimaKnowledge.vessel_name} is a ${bellissimaKnowledge.technical_specifications.class} flagship built by ${bellissimaKnowledge.technical_specifications.builder}.`,
    highlights: [
      'Deck 14 Stateroom 14122 direct elevator & gangway mapping',
      galleriaArea ? `${galleriaArea.name} 96m LED dome promenade` : 'Galleria 96m LED dome promenade',
      mainTheatre ? `${mainTheatre.name} main stage with level access routes` : 'London Theatre Deck 6 forward',
      'Muster Station direct evacuation path calculus'
    ]
  },
  {
    slug: 'ms-andorinha',
    name: 'MS Andorinha',
    imo: 'ENI 02338573',
    operator: 'Tauck River Cruises',
    vesselType: 'River Cruise',
    shipClass: 'Douro Boutique Class',
    roleTitle: 'Active Reference Model',
    tagline: 'Custom-built boutique river yacht for the historic Douro Valley and steep locks.',
    subtitle: 'Tauck · Douro Custom Build · Delivery 2020',
    heroImageUrl: '/media/ms-andorinha-hero.webp',
    lengthM: 80.0,
    beamM: 11.4,
    totalDecks: 4,
    cabinCount: 42,
    passengerCapacity: 84,
    buildYear: 2020,
    builder: 'Den Breejen Shipyard',
    region: 'Douro River · Portugal',
    defaultCabin: '218',
    statusLabel: 'Active Reference Model',
    description: 'MS Andorinha was purpose-built for the narrow locks of the Portuguese Douro. Carrying just 84 guests with an exceptionally high space ratio and silent hybrid river propulsion.',
    highlights: [
      'Upper Deck Suite 218 French Balcony with river acoustic isolation',
      'Engineered specifically for Carrapatelo Lock (35m water rise)',
      'Direct quay-level gangway on River Deck 2',
      'Panoramic Sun Deck with pop-up navigation bridge'
    ]
  },
  {
    slug: 'msc-grandiosa',
    name: 'MSC Grandiosa',
    imo: 'IMO 9803613',
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: 'Meraviglia-Plus Class',
    roleTitle: 'Active Reference Model',
    tagline: 'Extended Meraviglia-Plus flagship with enhanced public space and SCR catalysts.',
    subtitle: 'MSC Cruises · Meraviglia-Plus Class · Delivery 2019',
    heroImageUrl: '/media/msc-grandiosa-hero.webp',
    lengthM: 331.4,
    beamM: 43.0,
    totalDecks: 19,
    cabinCount: 2421,
    passengerCapacity: 6334,
    buildYear: 2019,
    builder: "Chantiers de l'Atlantique (Saint-Nazaire)",
    region: 'Western Mediterranean & Northern Europe',
    defaultCabin: '14122',
    statusLabel: 'Active Reference Model',
    description: 'MSC Grandiosa extends the Meraviglia blueprint by 16 meters, offering a larger Galleria promenade, enhanced specialty dining, and selective catalytic reduction (SCR) emissions tech.',
    highlights: [
      'Inherits verified Meraviglia-class stateroom geometry',
      'Extended 112-meter Mediterranean indoor promenade',
      'Direct Terminal Ovest pier access in Genoa (Deck 5)',
      'Vertical noise buffer over residential corridor decks'
    ]
  },
  {
    slug: 'msc-meraviglia',
    name: 'MSC Meraviglia',
    imo: 'IMO 9650418',
    operator: 'MSC Cruises',
    vesselType: 'Ocean Cruise',
    shipClass: 'Meraviglia Class (Prototype)',
    roleTitle: 'Class Reference Model',
    tagline: 'Pioneering lead vessel of the Meraviglia series with 360-degree ocean connectivity.',
    subtitle: 'MSC Cruises · Meraviglia Class (Lead Ship) · Delivery 2017',
    heroImageUrl: '/media/msc-meraviglia-hero.webp',
    lengthM: 315.8,
    beamM: 43.0,
    totalDecks: 19,
    cabinCount: 2217,
    passengerCapacity: 5655,
    buildYear: 2017,
    builder: "Chantiers de l'Atlantique (Saint-Nazaire)",
    region: 'North America & Caribbean',
    defaultCabin: '14122',
    statusLabel: 'Class Reference Model',
    description: 'The archetype vessel establishing the structural, acoustic, and elevator vector foundations for all Meraviglia-class staterooms across the global fleet.',
    highlights: [
      'Foundational shipyard GA blueprints for Meraviglia series',
      'Broadway Theatre and carousel lounge acoustic dampening',
      'Full ADA step-free gangway routing to primary elevators',
      'Double-deck indoor promenade with LED sky screen'
    ]
  }
];

export function getVesselBySlug(slug: string): FleetVessel {
  const found = FLEET_REGISTRY.find((v) => v.slug === slug);
  return found || FLEET_REGISTRY[0];
}
