import { useState, useEffect, type ReactNode } from 'react';
import {
  Compass,
  Anchor,
  Waves,
  Volume2,
  ArrowUp,
  ArrowDown,
  MapPin,
  Plug,
  Accessibility,
  Users,
  Moon,
  Search,
  ArrowRight,
  Ruler,
  Ship as ShipIcon,
  ChevronDown,
  Layers,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import type { ShipData, CabinData } from './types';
import { FLEET_REGISTRY, getVesselBySlug, type FleetVessel } from './fleet';
import { useMedia, Photo } from './media';
import { CabinReport, ExportBar, type LensId } from './report';
import { updateSocialHead, shipSlug } from './share';
import { routeFromLocation, cabinPath } from './routing';
import { BoardingIntelligence } from './boarding';
import { CruiseBriefingView } from './briefing';

export default function App() {
  const [currentSlug, setCurrentSlug] = useState<string>('msc-bellissima');
  const [ship, setShip] = useState<ShipData | null>(null);
  const [selectedCabinNum, setSelectedCabinNum] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [lens, setLens] = useState<LensId>('accessibility');
  const [loading, setLoading] = useState<boolean>(true);
  const [fleetSelectorOpen, setFleetSelectorOpen] = useState<boolean>(false);
  const media = useMedia();

  // Load ship and resolve initial cabin based on route
  const loadShipAndCabin = (slug: string, targetCabin?: string, targetDeck?: number, pushHistory: boolean = false) => {
    setLoading(true);
    const vesselMeta = getVesselBySlug(slug);
    fetch(`/data/${slug}.json`)
      .then((res) => res.json())
      .then((data: ShipData) => {
        setShip(data);
        setCurrentSlug(slug);

        // Determine cabin: targetCabin -> targetDeck first cabin -> vessel default -> first key in cabins
        let resolvedCabin = targetCabin && data.cabins[targetCabin] ? targetCabin : undefined;
        if (!resolvedCabin && targetDeck) {
          const deckCabins = Object.values(data.cabins).filter((c) => c.deck_number === targetDeck);
          if (deckCabins.length > 0) resolvedCabin = deckCabins[0].cabin_number;
        }
        if (!resolvedCabin) {
          resolvedCabin = data.cabins[vesselMeta.defaultCabin] ? vesselMeta.defaultCabin : Object.keys(data.cabins)[0];
        }

        setSelectedCabinNum(resolvedCabin);
        setSearchQuery(resolvedCabin);

        const newPath = cabinPath(slug, resolvedCabin);
        if (pushHistory) {
          window.history.pushState({ ship: slug, cabin: resolvedCabin }, '', newPath);
        } else {
          window.history.replaceState({ ship: slug, cabin: resolvedCabin }, '', newPath);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load ship pack:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    const route = routeFromLocation(window.location);
    loadShipAndCabin(route.shipSlug, route.cabinNumber, route.deckNumber, false);
  }, []);

  const cabin: CabinData | undefined = ship?.cabins[selectedCabinNum];

  // Keep the title, canonical URL and social preview in step with the cabin.
  useEffect(() => {
    if (ship && cabin) updateSocialHead(ship, cabin);
  }, [ship, cabin]);

  // Back/forward navigation resolves the vessel and cabin from the URL
  useEffect(() => {
    const onPop = () => {
      const route = routeFromLocation(window.location);
      if (route.shipSlug !== currentSlug) {
        loadShipAndCabin(route.shipSlug, route.cabinNumber, route.deckNumber, false);
      } else if (ship && route.cabinNumber && ship.cabins[route.cabinNumber]) {
        setSelectedCabinNum(route.cabinNumber);
        setSearchQuery(route.cabinNumber);
      }
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, [currentSlug, ship]);

  // Navigate to a cabin on the current ship
  const goToCabin = (n: string) => {
    if (!ship?.cabins[n]) return;
    setSelectedCabinNum(n);
    setSearchQuery(n);
    window.history.pushState({ ship: currentSlug, cabin: n }, '', cabinPath(currentSlug, n));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Switch to another vessel in the fleet
  const handleSelectVessel = (newSlug: string) => {
    setFleetSelectorOpen(false);
    if (newSlug === currentSlug) return;
    const meta = getVesselBySlug(newSlug);
    loadShipAndCabin(newSlug, meta.defaultCabin, undefined, true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (ship?.cabins[query]) {
      goToCabin(query);
    }
  };

  if (loading || !ship || !cabin) {
    return (
      <div className="min-h-screen bg-paper grid place-items-center text-ink">
        <div className="text-center">
          <p className="eyebrow-mist">Timonelo Spatial Engine</p>
          <h1 className="font-display text-3xl mt-3">Opening your orientation…</h1>
        </div>
      </div>
    );
  }

  const currentVesselMeta = getVesselBySlug(currentSlug);

  return (
    <>
      <div className="screen-app min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink pb-16">
        <Masthead
          ship={ship}
          cabin={cabin}
          currentSlug={currentSlug}
          fleetSelectorOpen={fleetSelectorOpen}
          setFleetSelectorOpen={setFleetSelectorOpen}
          onSelectVessel={handleSelectVessel}
        />
        <Hero
          ship={ship}
          cabin={cabin}
          vesselMeta={currentVesselMeta}
          media={media}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearch={handleSearch}
          onSelect={goToCabin}
        />

        <main className="page-shell mt-12 space-y-16">
          <CruiseBriefingView ship={ship} cabin={cabin} />
          <BoardingIntelligence ship={ship} cabin={cabin} />
          <TakeItWithYou ship={ship} cabin={cabin} />
          <HullPosition ship={ship} cabin={cabin} />
          <ViewAndPhotos cabin={cabin} media={media} />
          <Surroundings cabin={cabin} />
          <GettingAround ship={ship} cabin={cabin} />
          <DeckContext ship={ship} cabin={cabin} media={media} />
          <Lenses cabin={cabin} lens={lens} setLens={setLens} />
          <Evidence cabin={cabin} />
          <FleetGallery currentSlug={currentSlug} onSelectVessel={handleSelectVessel} />
          <Discovery ship={ship} current={selectedCabinNum} onSelect={goToCabin} />
        </main>

        <Footer />
      </div>

      {/* Dedicated Cabin Orientation Report — print / PDF only on screen */}
      <CabinReport ship={ship} cabin={cabin} lens={lens} />
    </>
  );
}

function TakeItWithYou({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  return (
    <section className="card p-6 md:p-7 flex flex-col md:flex-row md:items-center justify-between gap-5">
      <div className="max-w-xl">
        <p className="eyebrow-mist">Take it with you</p>
        <h2 className="font-display text-2xl mt-1.5">Cabin Orientation Report</h2>
        <p className="text-[14px] text-muted mt-1.5 leading-relaxed">
          A clean, printable orientation dossier for Cabin {cabin.cabin_number} on {ship.name} — save it as a PDF, print it for the
          terminal or river pier, or send it to family. Searchable text, no marketing.
        </p>
      </div>
      <ExportBar ship={ship} cabin={cabin} />
    </section>
  );
}

/* ------------------------------------------------------------------ helpers */

function sideLabel(s: CabinData['hull_side']): string {
  return s === 'STARBOARD' ? 'Starboard (right)' : s === 'PORT' ? 'Port (left)' : 'Centreline';
}
function elevationOf(ship: ShipData, deck: number): number | null {
  return ship.decks[String(deck)]?.elevation_m ?? null;
}
/** Longitudinal fraction (0 = aft, 1 = forward) from the zone label. */
function zoneFraction(zone: string): number {
  const z = zone.toLowerCase();
  const fwd = z.includes('forward') || z.includes('bow');
  const aft = z.includes('aft') || z.includes('stern');
  if (z.includes('midship') && aft) return 0.36;
  if (z.includes('midship') && fwd) return 0.64;
  if (aft) return 0.22;
  if (fwd) return 0.78;
  return 0.5;
}

/* ------------------------------------------------------------------ masthead */

function Masthead({
  ship,
  cabin,
  currentSlug,
  fleetSelectorOpen,
  setFleetSelectorOpen,
  onSelectVessel,
}: {
  ship: ShipData;
  cabin: CabinData;
  currentSlug: string;
  fleetSelectorOpen: boolean;
  setFleetSelectorOpen: (v: boolean | ((prev: boolean) => boolean)) => void;
  onSelectVessel: (slug: string) => void;
}) {
  const activeMeta = getVesselBySlug(currentSlug);

  return (
    <header className="sticky top-0 z-30 bg-paper/95 border-b hairline backdrop-blur-xs">
      <div className="page-shell h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <a href="/" className="flex items-center gap-2">
            <span className="w-5 h-5 bg-ink grid place-items-center">
              <span className="w-0.5 h-2.5 bg-paper rotate-45" />
            </span>
            <span className="font-display text-xl tracking-tight text-ink">Timonelo</span>
          </a>

          {/* Interactive Vessel Selector */}
          <div className="relative">
            <button
              onClick={() => setFleetSelectorOpen((prev) => !prev)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xs bg-paper border hairline hover:border-ink/40 text-left transition"
              aria-expanded={fleetSelectorOpen}
            >
              <ShipIcon className="w-3.5 h-3.5 text-gold" />
              <div>
                <span className="block text-xs font-semibold text-ink leading-none">{ship.name}</span>
                <span className="block text-[10px] text-muted leading-tight mt-0.5">
                  {activeMeta.operator} · {activeMeta.vesselType}
                </span>
              </div>
              <ChevronDown className={`w-3.5 h-3.5 text-muted transition-transform ml-1 ${fleetSelectorOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Fleet Selector Dropdown */}
            {fleetSelectorOpen && (
              <div className="absolute left-0 mt-2 w-80 bg-white border hairline shadow-xl rounded-xs p-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-3 py-2 border-b hairline mb-1">
                  <p className="eyebrow-mist text-[10px]">Universal Fleet Registry</p>
                  <p className="text-xs font-medium text-ink mt-0.5">Select a compiled digital twin</p>
                </div>
                <div className="space-y-1">
                  {FLEET_REGISTRY.map((v) => (
                    <button
                      key={v.slug}
                      onClick={() => onSelectVessel(v.slug)}
                      className={`w-full text-left px-3 py-2.5 rounded-xs flex items-start justify-between gap-2 transition ${
                        v.slug === currentSlug ? 'bg-gold/15 border border-gold/30' : 'hover:bg-paper'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-ink">{v.name}</span>
                          <span
                            className={`text-[9px] px-1.5 py-0.2 rounded-xs font-mono uppercase ${
                              v.vesselType === 'River Cruise'
                                ? 'bg-blue-100 text-blue-900 border border-blue-200'
                                : 'bg-slate-100 text-slate-800 border border-slate-200'
                            }`}
                          >
                            {v.vesselType}
                          </span>
                        </div>
                        <div className="text-[11px] text-muted mt-0.5">
                          {v.operator} · {v.totalDecks} Decks · {v.cabinCount} Cabins
                        </div>
                      </div>
                      {v.slug === currentSlug && <CheckCircle2 className="w-4 h-4 text-ink shrink-0 mt-0.5" />}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4 text-right">
          <div className="hidden sm:block">
            <span className="block text-xs font-semibold text-ink">Cabin {cabin.cabin_number}</span>
            <span className="block text-[11px] text-muted">Deck {cabin.deck_number} ({cabin.deck_name})</span>
          </div>
          <span className="h-2 w-2 rounded-full bg-emerald-600" title="Universal Spatial Engine connected" />
        </div>
      </div>
    </header>
  );
}

/* ------------------------------------------------------------------ hero */

function Hero({
  ship,
  cabin,
  vesselMeta,
  media,
  searchQuery,
  setSearchQuery,
  onSearch,
  onSelect,
}: {
  ship: ShipData;
  cabin: CabinData;
  vesselMeta: FleetVessel;
  media: (id: string) => string | null;
  searchQuery: string;
  setSearchQuery: (v: string) => void;
  onSearch: (e: React.FormEvent) => void;
  onSelect: (n: string) => void;
}) {
  const elev = elevationOf(ship, cabin.deck_number);
  const view = cabin.sightlines.has_lifeboat_obstruction ? 'Partially obstructed' : 'Unobstructed view';
  const cabinKeys = Object.keys(ship.cabins);

  return (
    <header className="relative ground-navy chart-lines text-white overflow-hidden">
      {media(`ship:${ship.imo}`) && (
        <img src={media(`ship:${ship.imo}`)!} alt={ship.name} className="absolute inset-0 h-full w-full object-cover opacity-40" />
      )}
      <div className="relative page-shell pt-14 pb-12">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="eyebrow-mist text-gold">{vesselMeta.vesselType} Orientation</span>
              <span className="text-white/40">·</span>
              <span className="text-[11px] font-mono text-white/70 uppercase">{vesselMeta.operator}</span>
            </div>
            <h1 className="font-display text-5xl md:text-7xl leading-[0.95] mt-3">Cabin {cabin.cabin_number}</h1>
            <p className="text-white/75 text-lg mt-4">
              On <span className="text-white">Deck {cabin.deck_number} ({cabin.deck_name})</span>, {sideLabel(cabin.hull_side).toLowerCase()},
              toward the {cabin.zone.toLowerCase()} of {ship.name}.
            </p>
          </div>

          <form onSubmit={onSearch} className="flex items-center gap-2 shrink-0">
            <div className="relative">
              <Search className="w-4 h-4 text-white/40 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter cabin"
                aria-label="Cabin number"
                className="h-12 border border-white/25 bg-white/10 pl-9 pr-4 font-mono text-sm text-white placeholder:text-white/50 outline-none focus:border-gold w-44"
              />
            </div>
            <button type="submit" className="h-12 px-5 bg-white text-ink text-xs font-semibold hover:bg-gold transition-colors">
              Find
            </button>
          </form>
        </div>

        {/* 15-second answer strip */}
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/10 border border-white/10">
          <HeroFact label="Deck" value={`${cabin.deck_number} · ${cabin.deck_name}`} />
          <HeroFact label="Vessel side" value={sideLabel(cabin.hull_side)} />
          <HeroFact label="Nearest vertical core" value={`${cabin.distances.elevator?.meters ?? '—'} m`} />
          <HeroFact label="Sightline view" value={view} />
        </div>

        <div className="mt-6 flex items-center gap-3 flex-wrap text-xs">
          <span className="text-white/55">Verified staterooms:</span>
          {cabinKeys.slice(0, 14).map((n) => (
            <button
              key={n}
              onClick={() => onSelect(n)}
              className={`px-3 py-1.5 font-mono transition ${
                n === cabin.cabin_number ? 'bg-gold text-ink font-semibold' : 'bg-white/10 text-white/85 hover:bg-white/20'
              }`}
            >
              {n}
              {ship.cabins[n].is_accessible ? ' ♿' : ''}
            </button>
          ))}
          {elev != null && <span className="text-white/45 ml-auto hidden md:block">Deck elevation {elev} m above water</span>}
        </div>
      </div>
    </header>
  );
}

function HeroFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-ink px-4 py-4">
      <div className="text-[10px] uppercase tracking-[0.18em] text-white/45">{label}</div>
      <div className="text-[15px] font-medium text-white mt-1 leading-snug">{value}</div>
    </div>
  );
}

/* ------------------------------------------------------------------ sections */

function SectionHead({ eyebrow, title, intro }: { eyebrow: string; title: string; intro?: string }) {
  return (
    <div className="mb-6 max-w-2xl">
      <p className="eyebrow-mist">{eyebrow}</p>
      <h2 className="font-display text-3xl md:text-4xl mt-2 leading-tight">{title}</h2>
      {intro && <p className="text-muted text-[15px] leading-relaxed mt-3">{intro}</p>}
    </div>
  );
}

function HullPosition({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  const frac = zoneFraction(cabin.zone);
  const elevs = Object.values(ship.decks).map((d) => d.elevation_m);
  const maxE = Math.max(...elevs, 1);
  const elev = elevationOf(ship, cabin.deck_number) ?? 0;
  const top = 12 + (1 - elev / maxE) * 60; // higher deck → nearer the top

  return (
    <section>
      <SectionHead eyebrow="Where you are" title="Your position on the hull" />
      <div className="grid lg:grid-cols-[1.5fr_1fr] gap-6 items-stretch">
        <div className="card p-6 md:p-8">
          <div className="flex justify-between text-[11px] text-muted font-mono uppercase tracking-wider mb-3">
            <span>Aft · stern</span>
            <span>Midship</span>
            <span>Forward · bow</span>
          </div>
          <div className="relative h-40 rounded-xs border hairline bg-paper overflow-hidden">
            {/* hull silhouette */}
            <div className="absolute inset-x-6 inset-y-6 border hairline rounded-[40%_40%_46%_46%/60%_60%_40%_40%] bg-white/60" />
            <div className="absolute inset-x-0 bottom-0 h-2 bg-sky-200/50" aria-hidden />
            {/* cabin pin */}
            <div className="absolute z-10 flex flex-col items-center -translate-x-1/2" style={{ left: `${frac * 100}%`, top: `${top}%` }}>
              <div className="h-3.5 w-3.5 rounded-full bg-gold border-2 border-ink" />
              <span className="mt-1 text-[10px] font-mono font-bold bg-ink text-white px-1.5 py-0.5">{cabin.cabin_number}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
            <Fact icon={<ShipIcon className="w-3.5 h-3.5" />} label="Deck" value={`${cabin.deck_number}`} />
            <Fact icon={<Compass className="w-3.5 h-3.5" />} label="Side" value={sideLabel(cabin.hull_side)} />
            <Fact icon={<Anchor className="w-3.5 h-3.5" />} label="Longitudinal" value={cabin.zone} />
            <Fact icon={<Ruler className="w-3.5 h-3.5" />} label="Living space" value={`${cabin.square_meters} m²`} />
          </div>
        </div>

        <div className="card p-6 flex flex-col gap-4">
          <p className="eyebrow-mist">Light & orientation</p>
          <p className="text-[15px] text-ink leading-relaxed">
            A {sideLabel(cabin.hull_side).toLowerCase()} orientation. Sun and water are on the{' '}
            {cabin.hull_side === 'STARBOARD' ? 'starboard' : cabin.hull_side === 'PORT' ? 'port' : 'centre'} beam — the exact
            aspect depends on the vessel’s heading during your cruise.
          </p>
          <div className="mt-auto flex items-center gap-2 text-[12px] text-muted">
            <Moon className="w-3.5 h-3.5 text-gold" aria-hidden />
            Solar aspect is a geometric projection, not a forecast.
          </div>
        </div>
      </div>
    </section>
  );
}

function Fact({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="bg-paper border hairline rounded-xs p-3">
      <div className="flex items-center gap-1.5 text-muted text-[10px] uppercase tracking-[0.12em]">
        <span className="text-gold">{icon}</span>
        {label}
      </div>
      <div className="text-[14px] font-semibold text-ink mt-1.5 leading-tight">{value}</div>
    </div>
  );
}

function ViewAndPhotos({ cabin, media }: { cabin: CabinData; media: (id: string) => string | null }) {
  return (
    <section>
      <SectionHead eyebrow="A first look" title="Your view and your room" intro="Photography is added stateroom by stateroom; until then, the spatial facts stand on their own." />
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <Photo src={media(`view:${cabin.cabin_number}`)} kind="view" label="Balcony view" ratio="16 / 9" priority />
          <div className="card mt-4 p-5 flex items-start gap-3">
            <Waves className="w-4 h-4 text-gold mt-0.5 shrink-0" aria-hidden />
            <div>
              <div className="eyebrow-mist mb-1">Balcony sightline</div>
              <p className="text-[14px] text-ink leading-relaxed">{cabin.sightlines.description}</p>
              <p className="text-[12px] text-muted mt-1">
                {cabin.sightlines.horizon_angle_deg}° horizon ·{' '}
                {cabin.sightlines.has_lifeboat_obstruction ? 'Obstruction present' : 'Unobstructed panorama'}
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <Photo src={media(`cabin:${cabin.cabin_number}`)} kind="cabin" label="Stateroom" ratio="4 / 3" />
          <div className="card p-5">
            <div className="eyebrow-mist mb-2">Balcony type</div>
            <div className="font-display text-xl text-ink capitalize">{cabin.balcony_type.toLowerCase().replace(/_/g, ' ')}</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Surroundings({ cabin }: { cabin: CabinData }) {
  const { overhead, underfoot } = cabin.surroundings;
  return (
    <section>
      <SectionHead eyebrow="What surrounds you" title="Above, below and beside" />
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card p-6">
          <p className="eyebrow-mist mb-4">Vertical context</p>
          <VerticalRow
            dir="above"
            deck={overhead.deck_number}
            name={overhead.deck_name}
            venues={overhead.venues}
            noise={overhead.is_noise_generator}
          />
          <div className="my-3 p-3.5 bg-white border-2 border-gold rounded-xs">
            <div className="text-[11px] font-bold uppercase tracking-wide text-ink">Your cabin · Deck {cabin.deck_number}</div>
            <div className="text-[12px] text-muted">Cabin {cabin.cabin_number} · {cabin.square_meters} m²</div>
          </div>
          <VerticalRow
            dir="below"
            deck={underfoot.deck_number}
            name={underfoot.deck_name}
            venues={underfoot.venues}
            noise={underfoot.is_noise_generator}
          />
        </div>

        <div className="card p-6">
          <p className="eyebrow-mist mb-4">Room specifics</p>
          <Spec label="Bed position" value={cabin.bed_near_balcony == null ? 'Private arrangement' : cabin.bed_near_balcony ? 'Next to the balcony' : 'Next to the entrance'} />
          <Spec label="Connecting door" value={cabin.connecting_cabin_number ? `Yes — to ${cabin.connecting_cabin_number}` : 'None (private wall)'} />
          <Spec label="Doorway width" value={`${cabin.door_width_mm} mm`} mono />
          <Spec label="Category" value={cabin.category_code} mono />
          <Spec label="Accessible" value={cabin.is_accessible ? 'Certified accessible' : 'Standard'} last />
        </div>

        <div className="card p-6">
          <p className="eyebrow-mist mb-4 flex items-center gap-2"><Plug className="w-3.5 h-3.5 text-gold" /> Power outlets</p>
          <div className="grid grid-cols-2 gap-2 text-center">
            <Socket n={cabin.sockets.eu_count} label="EU" />
            <Socket n={cabin.sockets.us_count} label="US" />
            <Socket n={cabin.sockets.usb_a_count} label="USB-A" />
            <Socket n={cabin.sockets.usb_c_count} label="USB-C" />
          </div>
          <p className="text-[12px] text-muted mt-4">
            {cabin.sockets.bedside_usb ? 'Bedside USB charging available.' : 'No bedside USB charging.'}
          </p>
        </div>
      </div>
    </section>
  );
}

function VerticalRow({ dir, deck, name, venues, noise }: { dir: 'above' | 'below'; deck: number | null; name: string | null; venues: string[]; noise?: boolean }) {
  const Icon = dir === 'above' ? ArrowUp : ArrowDown;
  return (
    <div className="p-3.5 bg-paper border hairline rounded-xs">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-bold uppercase tracking-wide text-ink flex items-center gap-1.5">
          <Icon className="w-3.5 h-3.5 text-gold" aria-hidden /> {dir === 'above' ? 'Above you' : 'Below you'}
          {deck != null && ` · Deck ${deck}`}
        </span>
        {noise && (
          <span className="text-[10px] text-amber-900 bg-amber-100 border border-amber-300 px-1.5 py-0.5 inline-flex items-center gap-1">
            <Volume2 className="w-3 h-3" aria-hidden /> Active space
          </span>
        )}
      </div>
      <p className="text-[12px] text-muted mt-1">
        {venues.length > 0 ? venues.join(', ') : `Quiet residential cabins${name ? ` (${name})` : ''}.`}
      </p>
    </div>
  );
}

function Spec({ label, value, mono, last }: { label: string; value: string; mono?: boolean; last?: boolean }) {
  return (
    <div className={`flex justify-between items-center py-2.5 ${last ? '' : 'border-b hairline'}`}>
      <span className="text-[12px] text-muted">{label}</span>
      <span className={`text-[13px] font-medium text-ink ${mono ? 'font-mono' : ''}`}>{value}</span>
    </div>
  );
}

function Socket({ n, label }: { n: number; label: string }) {
  return (
    <div className="bg-paper border hairline rounded-xs py-2.5">
      <div className="font-display text-2xl text-ink leading-none">{n}<span className="text-sm text-muted">×</span></div>
      <div className="text-[10px] uppercase tracking-[0.12em] text-muted mt-1">{label}</div>
    </div>
  );
}

function getDestinationLabel(id: string, ship: ShipData): string {
  const isRiver = ship.total_decks <= 5;
  const customMap: Record<string, string> = {
    buffet: isRiver ? "Arthur's Bistro / Buffet" : 'Marketplace Buffet',
    theater: isRiver ? 'Panorama Lounge & Bar' : 'London Theatre',
    elevator: 'Nearest vertical core / lift',
  };
  return customMap[id] ?? id;
}

function GettingAround({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  const dests = Object.keys(cabin.distances);
  const [dest, setDest] = useState<string>(dests.length > 0 ? dests[0] : '');

  useEffect(() => {
    if (dests.length > 0 && !dests.includes(dest)) {
      setDest(dests[0]);
    }
  }, [cabin]);

  const d = cabin.distances[dest];

  return (
    <section>
      <SectionHead eyebrow="Getting around" title="Walkable distances" intro="Deterministic routes through the circulation graph — measured, not estimated." />
      <div className="card p-6 md:p-8">
        <div className="flex flex-wrap gap-2">
          {dests.map((id) => (
            <button
              key={id}
              onClick={() => setDest(id)}
              className={`px-3.5 py-2 text-[13px] font-medium border transition ${
                dest === id ? 'bg-ink text-white border-ink' : 'bg-paper text-ink border-ink/15 hover:border-ink/40'
              }`}
            >
              {getDestinationLabel(id, ship)}
            </button>
          ))}
        </div>
        {d && (
          <div className="mt-6 grid sm:grid-cols-3 gap-6 items-end">
            <div>
              <div className="eyebrow-mist mb-1">Distance</div>
              <div className="font-display text-5xl text-ink leading-none">{d.meters}<span className="text-2xl text-muted"> m</span></div>
            </div>
            <div>
              <div className="eyebrow-mist mb-1">Effort</div>
              <div className="text-[15px] text-ink font-medium">{d.steps} steps · ~{Math.round(d.seconds)} s</div>
            </div>
            <div>
              <div className="eyebrow-mist mb-1">Access</div>
              <div className={`text-[14px] font-medium ${d.step_free ? 'text-emerald-800' : 'text-amber-800'}`}>
                {d.step_free ? 'Step-free (elevator)' : 'Includes stairs'}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function DeckContext({ ship, cabin, media }: { ship: ShipData; cabin: CabinData; media: (id: string) => string | null }) {
  const decks = Object.values(ship.decks).sort((a, b) => b.deck_number - a.deck_number);
  return (
    <section>
      <SectionHead eyebrow="Your deck" title={`Deck ${cabin.deck_number} — ${cabin.deck_name}`} intro="The deck layout and verified venues are detailed below." />
      <div className="grid lg:grid-cols-[1fr_16rem] gap-6">
        <div>
          <Photo src={media(`plan:${cabin.deck_number}`)} kind="plan" label={`Deck ${cabin.deck_number} plan`} ratio="21 / 9" />
          <div className="card mt-4 p-6">
            <div className="eyebrow-mist mb-3">Venues across decks</div>
            <ul className="space-y-2">
              {decks.filter((d) => d.venues.length > 0).map((d) => (
                <li key={d.deck_number} className="flex items-start gap-3 text-[13px]">
                  <span className="font-mono text-muted w-16 shrink-0">Deck {d.deck_number}</span>
                  <span className="text-ink">{d.venues.map((v) => v.name).join(' · ')}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* deck rail */}
        <aside className="card p-4">
          <div className="eyebrow-mist mb-3">Decks</div>
          <ol className="border-l hairline">
            {decks.map((d) => {
              const active = d.deck_number === cabin.deck_number;
              return (
                <li key={d.deck_number} className={`-ml-px border-l-2 pl-3 py-2 ${active ? 'border-gold' : 'border-transparent'}`}>
                  <div className="flex items-baseline gap-2">
                    <span className={`font-mono text-[12px] w-6 ${active ? 'text-ink font-bold' : 'text-muted'}`}>{d.deck_number}</span>
                    <div>
                      <div className={`text-[13px] leading-tight ${active ? 'text-ink font-semibold' : 'text-muted'}`}>{d.name}</div>
                      <div className="text-[10px] text-muted">{d.elevation_m} m · {d.zone.replace(/_/g, ' ').toLowerCase()}</div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </aside>
      </div>
    </section>
  );
}

const LENSES = [
  { id: 'accessibility', label: 'Mobility', Icon: Accessibility },
  { id: 'family', label: 'Family', Icon: Users },
  { id: 'quiet', label: 'Quiet', Icon: Moon },
] as const;

function Lenses({ cabin, lens, setLens }: { cabin: CabinData; lens: LensId; setLens: (l: LensId) => void }) {
  const summary =
    lens === 'accessibility' ? cabin.lenses.accessibility.summary : lens === 'family' ? cabin.lenses.family.summary : cabin.lenses.quiet.summary;
  const headline =
    lens === 'accessibility'
      ? cabin.lenses.accessibility.is_certified ? 'Certified accessible stateroom' : 'Standard stateroom'
      : lens === 'family'
        ? cabin.lenses.family.has_connecting ? 'Adjoining family pair' : 'Single stateroom'
        : cabin.lenses.quiet.is_quiet_tier ? 'Acoustically buffered' : 'Near an active space';
  return (
    <section>
      <SectionHead eyebrow="Through a lens" title="One cabin, several perspectives" intro="Lenses are optical filters over the same spatial facts — they change the view, never the ship." />
      <div className="card p-6 md:p-8">
        <div className="flex gap-2">
          {LENSES.map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setLens(id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] font-medium border transition ${
                lens === id ? 'bg-ink text-white border-ink' : 'bg-paper text-ink border-ink/15 hover:border-ink/40'
              }`}
            >
              <Icon className="w-4 h-4" aria-hidden /> {label}
            </button>
          ))}
        </div>
        <div className="mt-6">
          <h3 className="font-display text-2xl text-ink">{headline}</h3>
          <p className="text-[15px] text-muted leading-relaxed mt-2 max-w-2xl">{summary}</p>
          {lens === 'quiet' && cabin.lenses.quiet.acoustic_flags.length > 0 && (
            <ul className="mt-4 space-y-1.5">
              {cabin.lenses.quiet.acoustic_flags.map((f) => (
                <li key={f} className="flex items-center gap-2 text-[13px] text-ink">
                  <span className="w-1.5 h-1.5 rounded-full bg-gold" /> {f}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}

function Evidence({ cabin }: { cabin: CabinData }) {
  return (
    <section>
      <SectionHead eyebrow="Where this comes from" title="Evidence & provenance" intro="Every orientation traces to immutable, content-addressed sources. Timonelo never sounds more certain than its evidence." />
      <div className="grid sm:grid-cols-2 gap-4">
        {cabin.evidence.map((e) => (
          <div key={e.source_id} className="card p-5">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gold" aria-hidden />
              <span className="text-[14px] font-medium text-ink">{e.source_id}</span>
            </div>
            <div className="text-[12px] text-muted mt-2">{e.locator.replace(/_/g, ' ')}</div>
            <div className="font-mono text-[11px] text-muted mt-3 break-all">sha256:{e.sha256}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ Fleet Gallery */

function FleetGallery({ currentSlug, onSelectVessel }: { currentSlug: string; onSelectVessel: (slug: string) => void }) {
  return (
    <section className="border-t hairline pt-12">
      <SectionHead
        eyebrow="Universal Maritime Platform"
        title="Compiled Fleet Gallery"
        intro="Timonelo processes ocean mega-liners and luxury riverboats through the exact same spatial calculus."
      />
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {FLEET_REGISTRY.map((v) => {
          const isActive = v.slug === currentSlug;
          return (
            <div
              key={v.slug}
              className={`card p-5 flex flex-col justify-between transition-all ${
                isActive ? 'border-2 border-gold ring-1 ring-gold/20 shadow-md bg-white' : 'hover:border-ink/40'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span
                    className={`text-[9px] px-2 py-0.5 font-mono uppercase font-semibold rounded-xs ${
                      v.vesselType === 'River Cruise'
                        ? 'bg-blue-100 text-blue-900 border border-blue-200'
                        : 'bg-stone-100 text-stone-800 border border-stone-200'
                    }`}
                  >
                    {v.vesselType}
                  </span>
                  <span className="text-[10px] text-emerald-800 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Compiled
                  </span>
                </div>

                <h3 className="font-display text-xl text-ink leading-tight">{v.name}</h3>
                <p className="text-[11px] font-semibold text-gold uppercase tracking-wide mt-0.5">{v.operator}</p>

                <p className="text-[12px] text-muted leading-relaxed mt-2.5 line-clamp-3">{v.description}</p>

                <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t hairline text-[11px]">
                  <div>
                    <span className="text-muted block text-[10px] uppercase">Decks</span>
                    <span className="font-mono font-bold text-ink">{v.totalDecks}</span>
                  </div>
                  <div>
                    <span className="text-muted block text-[10px] uppercase">Cabins</span>
                    <span className="font-mono font-bold text-ink">{v.cabinCount}</span>
                  </div>
                  <div>
                    <span className="text-muted block text-[10px] uppercase">LOA</span>
                    <span className="font-mono font-bold text-ink">{v.lengthM} m</span>
                  </div>
                  <div>
                    <span className="text-muted block text-[10px] uppercase">Class</span>
                    <span className="font-mono font-bold text-ink truncate block" title={v.shipClass}>{v.shipClass}</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3">
                {isActive ? (
                  <div className="w-full py-2 text-center text-xs font-semibold text-ink bg-gold/20 rounded-xs border border-gold/40">
                    Currently Viewing
                  </div>
                ) : (
                  <button
                    onClick={() => onSelectVessel(v.slug)}
                    className="w-full py-2 text-center text-xs font-semibold bg-ink text-white hover:bg-gold hover:text-ink transition-colors rounded-xs flex items-center justify-center gap-1.5"
                  >
                    <span>Open Orientation</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function Discovery({ ship, current, onSelect }: { ship: ShipData; current: string; onSelect: (n: string) => void }) {
  const others = Object.values(ship.cabins).filter((c) => c.cabin_number !== current);
  if (others.length === 0) return null;
  return (
    <section>
      <SectionHead eyebrow="Keep exploring" title="Other staterooms on this vessel" />
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {others.slice(0, 9).map((c) => (
          <button
            key={c.cabin_number}
            onClick={() => onSelect(c.cabin_number)}
            className="group card p-5 text-left hover:border-ink/40 transition-colors flex items-center justify-between"
          >
            <div>
              <div className="font-mono text-lg text-ink">Cabin {c.cabin_number}</div>
              <div className="text-[12px] text-muted mt-0.5">
                Deck {c.deck_number} ({c.deck_name}) · {sideLabel(c.hull_side)}{c.is_accessible ? ' · Accessible' : ''}
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-ink transition-colors" aria-hidden />
          </button>
        ))}
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t hairline mt-20">
      <div className="page-shell py-10 flex flex-col sm:flex-row justify-between items-center gap-3 text-[11px] uppercase tracking-[0.15em] text-muted">
        <span className="inline-flex items-center gap-2"><Anchor className="w-3.5 h-3.5" /> © {new Date().getFullYear()} Timonelo Platform</span>
        <span className="tracking-[0.2em]">Universal Spatial Intelligence · Ocean & River Twins.</span>
      </div>
    </footer>
  );
}
