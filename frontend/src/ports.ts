import { PORTS_REGISTRY as RAW_PORTS } from './generated/ports';

export interface CuratedPort {
  slug: string;
  name: string;
  shortName: string;
  unLocode: string;
  country: string;
  region: string;
  headlineEn: string;
  headlineDe: string;
  storyEn: string;
  storyDe: string;
  terminalPier: string;
  gangwayDeck: number | null;
  distanceToCenterKm: number | null;
  walkingTimeMin: number | null;
  stepFreeAccess: boolean;
  transitNoteEn: string;
  transitNoteDe: string;
  airportTransitEn: string;
  airportTransitDe: string;
  currency: string;
  cardAcceptancePct: number;
  emergencyPhone: string;
  policePhone: string;
  callingShips: { slug: string; name: string }[];
  timEssentialsDe: string[];
  timEssentialsEn: string[];
}

const CURATED_PORT_STORIES: Record<string, {
  shortName: string;
  headlineDe: string;
  headlineEn: string;
  storyDe: string;
  storyEn: string;
  terminalPier: string;
  gangwayDeck: number;
  distanceKm: number;
  walkingMin: number;
  transitDe: string;
  transitEn: string;
  airportDe: string;
  airportEn: string;
  police: string;
  emergency: string;
  essentialsDe: string[];
  essentialsEn: string[];
}> = {
  genoa: {
    shortName: 'Genua',
    headlineDe: 'Historischer Kreuzfahrthafen am ligurischen Mittelmeer.',
    headlineEn: 'Historic Mediterranean turnaround gateway at Ponte dei Mille.',
    storyDe: 'Der historische Kreuzfahrthafen Ponte dei Mille liegt direkt am Porto Antico. Von Gangway Deck 5 erreichen Sie das Herz von Genua in ca. 15 Gehminuten ohne Umwege.',
    storyEn: 'The historic Ponte dei Mille terminal is situated right at Porto Antico. From Gangway Deck 5, the city centre of Genoa is accessible in a 15-minute walk.',
    terminalPier: 'Ponte dei Mille · Terminal Ovest',
    gangwayDeck: 5,
    distanceKm: 1.2,
    walkingMin: 15,
    transitDe: 'Stufenloser Fußweg über die Piazza Caricamento oder Metro-Station Principe (5 Min.).',
    transitEn: 'Step-free walk via Piazza Caricamento or Principe Metro station (5 min walk).',
    airportDe: 'Volabus Express-Shuttle zum Flughafen Genua (GOA) alle 30 Min. ab Bahnhof Principe.',
    airportEn: 'Volabus Express shuttle to Genoa Airport (GOA) every 30 min from Principe station.',
    police: '112 / +39 010 53601 (Guardia Costiera)',
    emergency: '112 (EU-Notruf)',
    essentialsDe: [
      'Gangway regulär auf Deck 5 (Ponte dei Mille)',
      '15 Minuten stufenloser Fußweg zum Porto Antico & Aquarium',
      'Kein Taxi für die Innenstadt nötig · Metro Principe in 400 m'
    ],
    essentialsEn: [
      'Gangway regularly on Deck 5 (Ponte dei Mille)',
      '15-minute step-free walk to Porto Antico & Aquarium',
      'No taxi required for city centre · Metro Principe 400 m'
    ]
  },
  porto: {
    shortName: 'Porto',
    headlineDe: 'Traditionsreicher Flusshafen im UNESCO-Welterbe des Douro-Tals.',
    headlineEn: 'Boutique river embarkation point in the Douro UNESCO valley.',
    storyDe: 'Der Liegeplatz an der Cais da Ribeira dient exklusiv Flusskreuzfahrten auf dem Douro. Die MS Andorinha liegt direkt am historischen Flussufer, nur wenige Schritte von den berühmten Portweinkellern von Vila Nova de Gaia entfernt.',
    storyEn: 'The Cais da Ribeira berth serves boutique river cruises on the Douro. MS Andorinha docks right along the historic riverbank, just steps from the renowned port wine cellars of Gaia.',
    terminalPier: 'Cais da Ribeira · Flussanleger Douro',
    gangwayDeck: 2,
    distanceKm: 0.3,
    walkingMin: 5,
    transitDe: 'Direkt im historischen Zentrum. Alle Sehenswürdigkeiten der Ribeira sind bequem zu Fuß erreichbar.',
    transitEn: 'Directly in the historic core. All Ribeira attractions are within immediate walking distance.',
    airportDe: 'Metro-Linie E (Violett) verbindet den Flughafen Francisco Sá Carneiro (OPO) mit Trindade in 25 Min.',
    airportEn: 'Metro Line E (Purple) connects Airport (OPO) to Trindade in 25 minutes.',
    police: '112 / +351 22 200 6344 (Polícia Marítima)',
    emergency: '112 (EU-Notruf)',
    essentialsDe: [
      'Gangway auf Flussdeck 2 (ebenerdig zur Kaimauer)',
      '5 Minuten Fußweg zur Ribeira & Brücke Dom Luís I',
      'Flusskreuzfahrt ohne Seegang · Kein Shuttle-Bus erforderlich'
    ],
    essentialsEn: [
      'Gangway on River Deck 2 (flush with the quay)',
      '5-minute walk to Ribeira & Dom Luís I Bridge',
      'River cruise with zero swell · No shuttle bus required'
    ]
  },
  yokohama: {
    shortName: 'Yokohama',
    headlineDe: 'Architektonisch preisgekröntes Passagierterminal der Bucht von Tokio.',
    headlineEn: 'Award-winning passenger terminal overlooking Tokyo Bay.',
    storyDe: 'Das futuristische Osanbashi Pier bietet einen komplett stufenlosen Zugang über sein hölzernes Wellendeck. Die Red Brick Warehouses und der Yamashita-Park liegen in bequemer Gehweite.',
    storyEn: 'The futuristic Osanbashi Pier offers completely step-free access across its undulating wooden deck. The Red Brick Warehouses and Yamashita Park are within easy walking distance.',
    terminalPier: 'Osanbashi International Passenger Terminal · Berth A/B',
    gangwayDeck: 5,
    distanceKm: 1.4,
    walkingMin: 18,
    transitDe: 'Minatomirai Line (Nihon-odori Station) in 7 Min. zu Fuß · Direkte Expresszüge nach Tokio-Shibuya in 35 Min.',
    transitEn: 'Minatomirai Line (Nihon-odori Station) 7 min walk · Direct express trains to Tokyo Shibuya in 35 min.',
    airportDe: 'Keikyu Limousine Bus direkt von Osanbashi zum Flughafen Tokio-Haneda (HND) in 30 Min.',
    airportEn: 'Keikyu Limousine Bus direct from Osanbashi to Tokyo Haneda Airport (HND) in 30 min.',
    police: '110 / +81 45 211 0770 (Yokohama Coast Guard)',
    emergency: '119 (Notarzt & Feuerwehr) · 110 (Polizei)',
    essentialsDe: [
      'Gangway auf Deck 5 mit stufenlosem Holzdeck zum Terminal',
      '18 Minuten Fußweg zum Minato Mirai & Red Brick Warehouse',
      'Minatomirai Line (Nihon-odori) in 7 Min. · Züge nach Tokio alle 10 Min.'
    ],
    essentialsEn: [
      'Gangway on Deck 5 with step-free wooden boardwalk',
      '18-minute walk to Minato Mirai & Red Brick Warehouses',
      'Minatomirai Line (Nihon-odori) 7 min · Trains to Tokyo every 10 min'
    ]
  },
  shanghai: {
    shortName: 'Shanghai',
    headlineDe: 'Asiens modernstes Kreuzfahrt-Drehkreuz am Zusammenfluss von Jangtsekiang und Huangpu.',
    headlineEn: "Asia's premier cruise gateway at the Yangtze & Huangpu confluence.",
    storyDe: 'Das Wusongkou International Cruise Terminal im Distrikt Baoshan fertigt Megaliner wie MSC Bellissima an Liegeplatz 3 ab. Geräumige Hallen und moderne Zollkontrollen sorgen für zügige Einschiffung.',
    storyEn: 'Wusongkou International Cruise Terminal in Baoshan district berths mega-liners including MSC Bellissima. Spacious terminals and digital customs enable efficient embarkation.',
    terminalPier: 'Wusongkou International Cruise Terminal · Terminal 2 · Liegeplatz 3',
    gangwayDeck: 5,
    distanceKm: 24.0,
    walkingMin: 0, // Not walkable
    transitDe: 'Metro-Linie 3 (Baoyang Road Station) mit offiziellem Hafenshuttle erreichbar · Taxis mit Taxameter ab Terminal 2.',
    transitEn: 'Metro Line 3 (Baoyang Road Station) via official port shuttle · Metered taxis from Terminal 2.',
    airportDe: 'Fahrzeit zum Flughafen Shanghai-Pudong (PVG) ca. 60 Min. per Taxi oder Maglev ab Longyang Road.',
    airportEn: 'Approx. 60 min by taxi to Shanghai Pudong Airport (PVG) or Maglev from Longyang Road.',
    police: '110 / +86 21 5667 2222 (Shanghai Maritime Safety)',
    emergency: '120 (Notarzt) · 110 (Polizei)',
    essentialsDe: [
      'Gangway auf Deck 5 direkt in den geschlossenen Fluggastfinger',
      'Kofferabgabe an Tor 3 vor Terminal 2 · Reisepass & Barcode griffbereit halten',
      'Offizielle Taxi-Warteschlange nutzen · Alipay / WeChat Pay vorab einrichten'
    ],
    essentialsEn: [
      'Gangway on Deck 5 directly into climate-controlled skybridge',
      'Luggage drop at Gate 3 outside Terminal 2 · Keep passport & barcode ready',
      'Use official taxi queue · Ensure Alipay / WeChat Pay is pre-installed'
    ]
  },
  barcelona: {
    shortName: 'Barcelona',
    headlineDe: 'Mittelmeer-Metropole mit direktem Zugang zur Promenade La Rambla.',
    headlineEn: 'Vibrant Mediterranean turnaround hub with seamless city access.',
    storyDe: 'Der Moll Adossat liegt wenige Kilometer südlich des Stadtzentrums. Der blaue PortBus (Cruise Bus) verbindet alle Terminals direkt mit dem Christopher-Kolumbus-Denkmal am Beginn der Ramblas.',
    storyEn: 'Moll Adossat is situated just south of the city center. The blue PortBus links all cruise terminals directly to the Columbus Monument at the foot of La Rambla.',
    terminalPier: 'Moll Adossat · Terminal A-E',
    gangwayDeck: 5,
    distanceKm: 3.5,
    walkingMin: 40,
    transitDe: 'Blauer PortBus (T3 Cruise Bus) pendelt alle 10 Min. zur Plaça de les Drassanes (3 € Einzelfahrt / 4,50 € Hin- und Rückfahrt).',
    transitEn: 'Blue PortBus (T3 Cruise Bus) runs every 10 min to Plaça de les Drassanes (€3 single / €4.50 return).',
    airportDe: 'Aerobús A1/A2 ab Plaça Catalunya oder Taxi zum Flughafen El Prat (BCN) in 25 Min. (ca. 35 € Fixpreis).',
    airportEn: 'Aerobús A1/A2 from Plaça Catalunya or taxi to El Prat Airport (BCN) in 25 min (approx. €35 fixed fare).',
    police: '112 / +34 93 298 6000 (Guardia Civil Puerto)',
    emergency: '112 (EU-Notruf)',
    essentialsDe: [
      'Gangway auf Deck 5 mit Passagierbrücke zum Terminal',
      'Blauer T3 PortBus fährt alle 10 Min. direkt zum Beginn der Ramblas (3 €)',
      'Rückkehrpuffer: Mindestens 45 Min. vor All Aboard am Bus einfinden'
    ],
    essentialsEn: [
      'Gangway on Deck 5 with enclosed jetway to terminal',
      'Blue T3 PortBus runs every 10 min directly to La Rambla (€3)',
      'Return buffer: Arrive at bus stop at least 45 min before All Aboard'
    ]
  },
  naples: {
    shortName: 'Neapel',
    headlineDe: 'Historisches Stazione Marittima im Schatten des Vesuvs.',
    headlineEn: 'Historic Stazione Marittima directly adjoining the city centre.',
    storyDe: 'Das Stazione Marittima liegt am Molo Angioino, unmittelbar vor dem imposanten Castel Nuovo. Nach dem Verlassen der Gangway stehen Sie bereits im Herzen von Neapel.',
    storyEn: 'The Stazione Marittima is located at Molo Angioino, directly adjacent to Castel Nuovo. Exiting the terminal places you immediately in central Naples.',
    terminalPier: 'Molo Angioino · Stazione Marittima',
    gangwayDeck: 5,
    distanceKm: 0.8,
    walkingMin: 10,
    transitDe: 'Direkt zu Fuß erreichbar · Metro-Station Municipio (Linie 1) in 3 Gehminuten.',
    transitEn: 'Directly walkable on foot · Municipio Metro station (Line 1) within 3 minutes.',
    airportDe: 'Alibus Shuttle direkt vom Molo Beverello zum Flughafen Neapel-Capodichino (NAP) alle 20 Min.',
    airportEn: 'Alibus shuttle from Molo Beverello directly to Naples Airport (NAP) every 20 min.',
    police: '112 / +39 081 244 5111 (Capitaneria di Porto)',
    emergency: '112 (EU-Notruf)',
    essentialsDe: [
      'Gangway auf Deck 5 · Direkter Fußweg aus dem Terminal in die Stadt',
      '10 Minuten Gehzeit zur Piazza del Plebiscito und Galleria Umberto I',
      'Fähren nach Capri & Ischia legen direkt am Nachbarkai Molo Beverello ab'
    ],
    essentialsEn: [
      'Gangway on Deck 5 · Direct walk out of the terminal into the city',
      '10-minute walk to Piazza del Plebiscito and Galleria Umberto I',
      'Ferries to Capri & Ischia depart from adjoining Molo Beverello quay'
    ]
  },
};

// Transform into sanitized, decision-layered CuratedPort objects
export const PORTS_REGISTRY: CuratedPort[] = [
  'genoa',
  'porto',
  'yokohama',
  'shanghai',
  'barcelona',
  'naples'
].map((slug) => {
  const custom = CURATED_PORT_STORIES[slug];
  const customCallingShips: Record<string, { slug: string; name: string }[]> = {
    porto: [{ slug: 'ms-andorinha', name: 'MS Andorinha' }],
    genoa: [
      { slug: 'msc-bellissima', name: 'MSC Bellissima' },
      { slug: 'msc-grandiosa', name: 'MSC Grandiosa' },
    ],
    yokohama: [{ slug: 'msc-bellissima', name: 'MSC Bellissima' }],
    shanghai: [{ slug: 'msc-bellissima', name: 'MSC Bellissima' }],
    barcelona: [
      { slug: 'msc-bellissima', name: 'MSC Bellissima' },
      { slug: 'msc-grandiosa', name: 'MSC Grandiosa' },
    ],
    naples: [
      { slug: 'msc-bellissima', name: 'MSC Bellissima' },
      { slug: 'msc-meraviglia', name: 'MSC Meraviglia' },
    ],
  };
  const callingShips = customCallingShips[slug] || [
    { slug: 'msc-bellissima', name: 'MSC Bellissima' }
  ];
  const raw = RAW_PORTS.find((p) => p.slug === slug);

  return {
    slug,
    name: raw ? raw.name : custom.shortName,
    shortName: custom.shortName,
    unLocode: raw ? raw.unLocode : slug.toUpperCase(),
    country: raw ? raw.country : 'Europe / Global',
    region: raw ? raw.region : 'Mediterranean & River',
    headlineDe: custom.headlineDe,
    headlineEn: custom.headlineEn,
    storyDe: custom.storyDe,
    storyEn: custom.storyEn,
    terminalPier: custom.terminalPier,
    gangwayDeck: custom.gangwayDeck,
    distanceToCenterKm: custom.distanceKm,
    walkingTimeMin: custom.walkingMin,
    stepFreeAccess: true,
    transitNoteDe: custom.transitDe,
    transitNoteEn: custom.transitEn,
    airportTransitDe: custom.airportDe,
    airportTransitEn: custom.airportEn,
    currency: raw ? raw.currency : 'EUR (€)',
    cardAcceptancePct: raw ? raw.cardAcceptancePct : 98,
    emergencyPhone: custom.emergency,
    policePhone: custom.police,
    callingShips,
    timEssentialsDe: custom.essentialsDe,
    timEssentialsEn: custom.essentialsEn,
  };
});

export function getPortBySlug(slug: string): CuratedPort {
  const found = PORTS_REGISTRY.find((p) => p.slug === slug);
  return found || PORTS_REGISTRY[0];
}
