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
  ArrowLeft,
} from 'lucide-react';
import type { ShipData, CabinData } from './types';
import { FLEET_REGISTRY, getVesselBySlug, type FleetVessel } from './fleet';
import { useI18n } from './i18n';
import { useMedia, Photo } from './media';
import { CabinReport, ExportBar, type LensId } from './report';
import { updateSocialHead } from './share';
import { routeFromLocation, cabinPath, portPath, vesselPath } from './routing';
import { BoardingIntelligence } from './boarding';
import { CruiseBriefingView } from './briefing';
import { Navigation } from './components/Navigation';
import { HospitalityLanding } from './components/HospitalityLanding';
import { Footer } from './components/Footer';
import { PortExplorer } from './components/PortExplorer';
import { CrewSection } from './components/CrewSection';
import { MissionSection } from './components/MissionSection';
import { UniversalSearchModal } from './components/UniversalSearchModal';
import { ShipLandingPage } from './components/ShipLandingPage';
import { InteractiveVesselSilhouette } from './components/InteractiveVesselSilhouette';

export default function App() {
  const { t, locale } = useI18n();
  const [viewMode, setViewMode] = useState<'landing' | 'vessel' | 'cabin' | 'port' | 'crew' | 'mission'>('landing');
  const [currentSlug, setCurrentSlug] = useState<string>('msc-bellissima');
  const [selectedPortSlug, setSelectedPortSlug] = useState<string>('genoa');
  const [ship, setShip] = useState<ShipData | null>(null);
  const [selectedCabinNum, setSelectedCabinNum] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [lens, setLens] = useState<LensId>('accessibility');
  const [loading, setLoading] = useState<boolean>(false);
  const [searchModalOpen, setSearchModalOpen] = useState<boolean>(false);
  const media = useMedia();

  const [notFoundVessel, setNotFoundVessel] = useState<string | null>(null);
  const [unmappedCabinNumber, setUnmappedCabinNumber] = useState<string | null>(null);

  // Load ship data and resolve cabin
  const loadShipData = (
    slug: string,
    targetCabin?: string,
    targetDeck?: number,
    mode: 'landing' | 'vessel' | 'cabin' = 'cabin',
    pushHistory: boolean = false
  ) => {
    setLoading(true);
    setNotFoundVessel(null);
    const vesselMeta = getVesselBySlug(slug);

    fetch(`/data/${slug}.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: ShipData) => {
        setShip(data);
        setCurrentSlug(slug);
        setViewMode(mode);

        let resolvedCabin = targetCabin && data.cabins[targetCabin] ? targetCabin : undefined;
        if (targetCabin && !data.cabins[targetCabin]) {
          setUnmappedCabinNumber(targetCabin);
        } else {
          setUnmappedCabinNumber(null);
        }

        if (!resolvedCabin && targetDeck) {
          const deckCabins = Object.values(data.cabins).filter((c) => c.deck_number === targetDeck);
          if (deckCabins.length > 0) resolvedCabin = deckCabins[0].cabin_number;
        }
        if (!resolvedCabin) {
          resolvedCabin = data.cabins[vesselMeta.defaultCabin] ? vesselMeta.defaultCabin : Object.keys(data.cabins)[0];
        }

        setSelectedCabinNum(resolvedCabin);
        setSearchQuery(resolvedCabin);

        const newPath = mode === 'landing' ? '/' : mode === 'vessel' ? vesselPath(slug) : cabinPath(slug, resolvedCabin);
        if (pushHistory) {
          window.history.pushState({ viewMode: mode, ship: slug, cabin: resolvedCabin }, '', newPath);
        } else {
          window.history.replaceState({ viewMode: mode, ship: slug, cabin: resolvedCabin }, '', newPath);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load ship pack:', err);
        setNotFoundVessel(slug);
        setLoading(false);
      });
  };

  // Keyboard shortcut for search (⌘K or /)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchModalOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Initial routing resolution
  useEffect(() => {
    const route = routeFromLocation(window.location);
    if (route.viewMode === 'landing') {
      setViewMode('landing');
      fetch(`/data/msc-bellissima.json`)
        .then((res) => res.json())
        .then((data: ShipData) => {
          setShip(data);
          setSelectedCabinNum('14122');
          setSearchQuery('14122');
        })
        .catch(() => {});
      if (route.sectionTarget === 'fleet') {
        setTimeout(() => {
          const el = document.getElementById('fleet-gallery');
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }, 150);
      }
    } else if (route.viewMode === 'port') {
      setViewMode('port');
      if (route.portSlug) setSelectedPortSlug(route.portSlug);
    } else if (route.viewMode === 'crew') {
      setViewMode('crew');
    } else if (route.viewMode === 'mission') {
      setViewMode('mission');
    } else {
      const slug = route.shipSlug || 'msc-bellissima';
      loadShipData(slug, route.cabinNumber, route.deckNumber, route.viewMode, false);
    }
  }, []);

  const cabin: CabinData | undefined = ship?.cabins[selectedCabinNum];

  // Keep title & social preview updated
  useEffect(() => {
    if (viewMode === 'cabin' && ship && cabin) {
      updateSocialHead(ship, cabin);
    } else if (viewMode === 'port') {
      document.title = 'Timonelo — Strategic Cruise Ports';
    } else if (viewMode === 'crew') {
      document.title = 'Timonelo — Verified Crew Contributor Programme';
    } else if (viewMode === 'mission') {
      document.title = 'Timonelo — Why Timonelo Exists';
    } else if (viewMode === 'vessel') {
      const meta = getVesselBySlug(currentSlug);
      document.title = `Timonelo — ${meta.name} (${meta.shipClass})`;
    } else {
      document.title = 'Timonelo — Universal Vessel Intelligence';
    }
  }, [viewMode, ship, cabin, currentSlug]);

  // Back/forward browser navigation
  useEffect(() => {
    const onPop = () => {
      const route = routeFromLocation(window.location);
      if (route.viewMode === 'landing') {
        setViewMode('landing');
      } else if (route.viewMode === 'port') {
        setViewMode('port');
        if (route.portSlug) setSelectedPortSlug(route.portSlug);
      } else if (route.viewMode === 'crew') {
        setViewMode('crew');
      } else if (route.viewMode === 'mission') {
        setViewMode('mission');
      } else {
        const slug = route.shipSlug || 'msc-bellissima';
        if (slug !== currentSlug || !ship) {
          loadShipData(slug, route.cabinNumber, route.deckNumber, route.viewMode, false);
        } else if (route.cabinNumber && ship.cabins[route.cabinNumber]) {
          setViewMode('cabin');
          setSelectedCabinNum(route.cabinNumber);
          setSearchQuery(route.cabinNumber);
        }
      }
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, [currentSlug, ship]);

  // Navigation handlers
  const handleNavigateHome = () => {
    setViewMode('landing');
    window.history.pushState({ viewMode: 'landing' }, '', '/');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateFleet = () => {
    if (viewMode !== 'landing') {
      setViewMode('landing');
      window.history.pushState({ viewMode: 'landing' }, '', '/fleet');
    }
    setTimeout(() => {
      const el = document.getElementById('fleet-gallery');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const handleNavigatePorts = (portSlug?: string) => {
    setViewMode('port');
    if (portSlug) setSelectedPortSlug(portSlug);
    window.history.pushState({ viewMode: 'port' }, '', portSlug ? portPath(portSlug) : '/ports');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateCrew = () => {
    setViewMode('crew');
    window.history.pushState({ viewMode: 'crew' }, '', '/crew');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateMission = () => {
    setViewMode('mission');
    window.history.pushState({ viewMode: 'mission' }, '', '/mission');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigatePrinciples = () => {
    if (viewMode !== 'landing') {
      setViewMode('landing');
      window.history.pushState({ viewMode: 'landing' }, '', '/about');
    }
    setTimeout(() => {
      const el = document.getElementById('platform-principles');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const handleSelectVessel = (slug: string) => {
    const meta = getVesselBySlug(slug);
    loadShipData(slug, meta.defaultCabin, undefined, 'vessel', true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleExploreCabins = (slug: string, cabinNum?: string) => {
    loadShipData(slug, cabinNum, undefined, 'cabin', true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const goToCabin = (n: string) => {
    if (!ship?.cabins[n]) return;
    setSelectedCabinNum(n);
    setSearchQuery(n);
    window.history.pushState({ viewMode: 'cabin', ship: currentSlug, cabin: n }, '', cabinPath(currentSlug, n));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (ship?.cabins[query]) {
      goToCabin(query);
    }
  };

  if (loading && viewMode !== 'landing') {
    return (
      <div className="min-h-screen bg-paper grid place-items-center text-ink">
        <div className="text-center">
          <p className="eyebrow text-gold">Timonelo</p>
          <h1 className="font-display text-3xl mt-3 font-normal">Opening ship orientation…</h1>
        </div>
      </div>
    );
  }

  const currentVesselMeta = getVesselBySlug(currentSlug);

  return (
    <div className="min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink flex flex-col justify-between">
      <div>
        <Navigation
          currentView={viewMode}
          currentSlug={currentSlug}
          ship={ship}
          cabin={cabin || null}
          onNavigateHome={handleNavigateHome}
          onNavigateFleet={handleNavigateFleet}
          onNavigatePorts={() => handleNavigatePorts()}
          onNavigateCrew={handleNavigateCrew}
          onNavigateMission={handleNavigateMission}
          onSelectVessel={handleSelectVessel}
          onOpenSearch={() => setSearchModalOpen(true)}
        />

        {notFoundVessel ? (
          <div className="min-h-[70vh] flex items-center justify-center p-6 text-center">
            <div className="max-w-md bg-white border border-slate-200 rounded-3xl p-8 sm:p-10 shadow-xs space-y-6">
              <div className="w-14 h-14 bg-[#0c1b2a] text-amber-400 rounded-full grid place-items-center mx-auto shadow-md">
                <Compass className="w-7 h-7" />
              </div>
              <div className="space-y-2">
                <span className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
                  {locale === 'de' ? 'Offiziers-Meldung' : 'Bridge Notice'}
                </span>
                <h2 className="font-serif text-2xl md:text-3xl text-slate-900 font-normal">
                  {t.notFound.title}
                </h2>
                <p className="font-serif italic text-slate-700 pt-2 text-base leading-relaxed">
                  » {t.notFound.officerNote} «
                </p>
              </div>
              <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={handleNavigateHome}
                  className="px-6 py-3 rounded-full bg-[#0c1b2a] text-white hover:bg-slate-800 text-xs font-medium transition cursor-pointer shadow-xs"
                >
                  {t.notFound.returnToBridge}
                </button>
                <button
                  onClick={() => setSearchModalOpen(true)}
                  className="px-6 py-3 rounded-full border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium transition cursor-pointer"
                >
                  {t.notFound.searchRegistry}
                </button>
              </div>
            </div>
          </div>
        ) : viewMode === 'landing' ? (
          <HospitalityLanding
            onSelectVessel={handleSelectVessel}
            onOpenPreparation={() => handleSelectVessel('msc-bellissima')}
          />
        ) : viewMode === 'port' ? (
          <PortExplorer
            initialPortSlug={selectedPortSlug}
            onSelectShip={handleSelectVessel}
          />
        ) : viewMode === 'crew' ? (
          <CrewSection />
        ) : viewMode === 'mission' ? (
          <MissionSection onExploreFleet={handleNavigateFleet} />
        ) : viewMode === 'vessel' ? (
          <ShipLandingPage
            vessel={currentVesselMeta}
            onExploreCabins={(c) => handleExploreCabins(currentSlug, c)}
            onSelectShip={handleSelectVessel}
            onBackToFleet={handleNavigateHome}
          />
        ) : ship && cabin ? (
          <div className="screen-app pb-20">
            <Hero
              ship={ship}
              cabin={cabin}
              vesselMeta={currentVesselMeta}
              media={media}
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              onSearch={handleSearch}
              onSelect={goToCabin}
              onBackToFleet={handleNavigateHome}
              unmappedCabinNumber={unmappedCabinNumber}
            />

            <main className="page-shell mt-14 space-y-20">
              <CruiseBriefingView ship={ship} cabin={cabin} />
              <BoardingIntelligence ship={ship} cabin={cabin} />
              <TakeItWithYou ship={ship} cabin={cabin} />
              <HullPosition ship={ship} cabin={cabin} onSelect={goToCabin} />
              <ViewAndPhotos cabin={cabin} media={media} isRiver={ship.total_decks <= 5} />
              <Surroundings cabin={cabin} />
              <GettingAround ship={ship} cabin={cabin} />
              <DeckContext ship={ship} cabin={cabin} media={media} />
              <Lenses cabin={cabin} lens={lens} setLens={setLens} />
              <Evidence cabin={cabin} />
              <Discovery ship={ship} current={selectedCabinNum} onSelect={goToCabin} />
            </main>

            {/* Dedicated Cabin Orientation Report — print / PDF only */}
            <CabinReport ship={ship} cabin={cabin} lens={lens} />
          </div>
        ) : null}
      </div>

      <Footer
        onNavigateHome={handleNavigateHome}
        onNavigateFleet={handleNavigateFleet}
        onNavigatePorts={() => handleNavigatePorts()}
        onNavigateCrew={handleNavigateCrew}
        onNavigateMission={handleNavigateMission}
        onNavigatePrinciples={handleNavigatePrinciples}
      />

      {/* Universal Search Modal */}
      <UniversalSearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
        onSelectShip={handleSelectVessel}
        onSelectCabin={(shipSlug, cabinNum) => handleExploreCabins(shipSlug, cabinNum)}
        onSelectPort={(portSlug) => handleNavigatePorts(portSlug)}
      />
    </div>
  );
}

function TakeItWithYou({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  return (
    <section className="card p-7 md:p-8 bg-white border border-ink/8 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xs">
      <div className="max-w-xl">
        <p className="eyebrow text-gold">Summary Dossier</p>
        <h2 className="font-display text-2xl md:text-3xl mt-1.5 font-normal">Cabin Orientation Report</h2>
        <p className="text-[14px] text-muted mt-2 leading-relaxed">
          A clean orientation summary for Cabin {cabin.cabin_number} on {ship.name} — save it as a PDF, print it for boarding, or share with family. Factual details with zero advertising.
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
  onBackToFleet,
  unmappedCabinNumber,
}: {
  ship: ShipData;
  cabin: CabinData;
  vesselMeta: FleetVessel;
  media: (id: string) => string | null;
  searchQuery: string;
  setSearchQuery: (v: string) => void;
  onSearch: (e: React.FormEvent) => void;
  onSelect: (n: string) => void;
  onBackToFleet: () => void;
  unmappedCabinNumber?: string | null;
}) {
  const { locale } = useI18n();
  const elev = elevationOf(ship, cabin.deck_number);
  const view = cabin.sightlines.has_lifeboat_obstruction ? 'Partially obstructed' : 'Unobstructed view';
  const cabinKeys = Object.keys(ship.cabins);

  return (
    <header className="relative ground-navy chart-lines text-white overflow-hidden">
      {media(`ship:${ship.imo}`) && (
        <img src={media(`ship:${ship.imo}`)!} alt={ship.name} className="absolute inset-0 h-full w-full object-cover opacity-35" />
      )}
      <div className="relative page-shell pt-10 pb-12">
        {/* Unmapped Cabin Warning Banner */}
        {unmappedCabinNumber && (
          <div className="mb-6 p-4 rounded-xs bg-amber-500/20 border border-amber-400/40 text-amber-100 flex items-start gap-3 backdrop-blur-sm">
            <span className="text-amber-300 font-bold text-base mt-0.5">ℹ</span>
            <div className="text-xs space-y-1">
              <p className="font-semibold text-white">
                {isGerman
                  ? `Hinweis: Kabine ${unmappedCabinNumber} ist noch nicht einzeln erfasst.`
                  : `Notice: Cabin ${unmappedCabinNumber} is not yet individually blueprint-mapped.`}
              </p>
              <p className="text-white/80">
                {isGerman
                  ? `Angezeigt wird Referenzkabine ${cabin.cabin_number} (${cabin.category_name}) auf Deck ${cabin.deck_number} (Abgeleitet vom Referenzmodell).`
                  : `Displaying reference Cabin ${cabin.cabin_number} (${cabin.category_name}) on Deck ${cabin.deck_number} (Inherited from reference model).`}
              </p>
            </div>
          </div>
        )}

        {/* Back breadcrumb */}
        <div className="mb-6">
          <button
            onClick={onBackToFleet}
            className="inline-flex items-center gap-1.5 text-xs text-white/65 hover:text-white transition font-mono uppercase tracking-wider cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>The Fleet</span>
            <span className="text-white/30">/</span>
            <span className="text-gold font-medium">{ship.name}</span>
          </button>
        </div>

        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[11px] font-mono text-gold tracking-wide uppercase">{vesselMeta.vesselType}</span>
              <span className="text-white/30">·</span>
              <span className="text-[11px] font-mono text-white/65 uppercase">{vesselMeta.operator}</span>
              <span className="text-white/30">·</span>
              <span className="text-[11px] font-mono text-white/65">{ship.imo}</span>
            </div>
            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl leading-[0.98] font-normal text-white">
              Cabin {cabin.cabin_number}
            </h1>
            <p className="text-white/80 text-base sm:text-lg mt-4 font-display italic">
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
                className="h-11 border border-white/20 bg-white/8 pl-9 pr-4 font-mono text-xs text-white placeholder:text-white/40 outline-none focus:border-gold w-40 rounded-xs"
              />
            </div>
            <button type="submit" className="h-11 px-4 bg-white text-ink text-xs font-medium hover:bg-gold transition-colors cursor-pointer rounded-xs">
              Find
            </button>
          </form>
        </div>

        {/* 15-second answer strip */}
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/10 border border-white/10">
          <HeroFact label="Deck" value={`${cabin.deck_number} · ${cabin.deck_name}`} />
          <HeroFact label="Vessel side" value={sideLabel(cabin.hull_side)} />
          <HeroFact label="Nearest elevator" value={`${cabin.distances.elevator?.meters ?? '—'} m`} />
          <HeroFact label="Sightline view" value={view} />
        </div>

        <div className="mt-6 flex items-center gap-2 flex-wrap text-xs">
          <span className="text-white/50 text-[11px]">Verified cabins:</span>
          {cabinKeys.slice(0, 12).map((n) => (
            <button
              key={n}
              onClick={() => onSelect(n)}
              className={`px-2.5 py-1 font-mono text-[11px] rounded-xs transition cursor-pointer ${
                n === cabin.cabin_number ? 'bg-gold text-ink font-medium' : 'bg-white/8 text-white/80 hover:bg-white/16'
              }`}
            >
              {n}
              {ship.cabins[n].is_accessible ? ' ♿' : ''}
            </button>
          ))}
          {elev != null && <span className="text-white/40 ml-auto hidden md:block text-[11px]">Deck elevation {elev} m above water</span>}
        </div>
      </div>
    </header>
  );
}

function HeroFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-ink/75 p-4">
      <div className="text-[10px] uppercase font-mono tracking-widest text-white/45">{label}</div>
      <div className="font-display text-lg text-white mt-0.5 leading-snug font-normal">{value}</div>
    </div>
  );
}

/* ------------------------------------------------------------------ sections */

function SectionHead({ eyebrow, title, intro }: { eyebrow: string; title: string; intro?: string }) {
  return (
    <div className="mb-6 max-w-2xl">
      <p className="eyebrow text-muted/70">{eyebrow}</p>
      <h2 className="section-title text-3xl sm:text-4xl md:text-5xl mt-1.5 font-normal">{title}</h2>
      {intro && <p className="text-muted text-[15px] leading-relaxed mt-2">{intro}</p>}
    </div>
  );
}

function HullPosition({ ship, cabin, onSelect }: { ship: ShipData; cabin: CabinData; onSelect?: (n: string) => void }) {
  return (
    <section>
      <SectionHead eyebrow="Vessel Geometry" title="Position on the Hull" />
      <div className="space-y-6">
        <InteractiveVesselSilhouette ship={ship} cabin={cabin} onSelectCabin={onSelect} />
      </div>
    </section>
  );
}

function Fact({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="bg-paper/50 border border-ink/6 rounded-xs p-3">
      <div className="flex items-center gap-1.5 text-muted text-[10px] uppercase tracking-wider font-mono">
        <span className="text-gold">{icon}</span>
        {label}
      </div>
      <div className="font-display text-base text-ink mt-1 font-medium">{value}</div>
    </div>
  );
}

function ViewAndPhotos({ cabin, media, isRiver }: { cabin: CabinData; media: (id: string, isRiver?: boolean) => string | null; isRiver?: boolean }) {
  return (
    <section>
      <SectionHead eyebrow="Visual Sightlines" title="View & Stateroom Photos" intro="Onboard photography is cataloged cabin by cabin; spatial dimensions stand permanently on their own." />
      <div className="grid md:grid-cols-3 gap-5">
        <div className="md:col-span-2">
          <Photo src={media(`view:${cabin.cabin_number}`, isRiver)} kind="view" label="Balcony view" ratio="16 / 9" priority />
          <div className="card mt-4 p-5 bg-white border border-ink/8 flex items-start gap-3">
            <Waves className="w-4 h-4 text-gold mt-0.5 shrink-0" aria-hidden />
            <div>
              <div className="eyebrow text-gold mb-0.5">Balcony Sightline</div>
              <p className="text-[14px] text-ink leading-relaxed">{cabin.sightlines.description}</p>
              <p className="text-[12px] text-muted mt-1 font-mono">
                {cabin.sightlines.horizon_angle_deg}° horizon view ·{' '}
                {cabin.sightlines.has_lifeboat_obstruction ? 'Lifeboat obstruction present' : 'Unobstructed view'}
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <Photo src={media(`cabin:${cabin.cabin_number}`, isRiver)} kind="cabin" label="Stateroom" ratio="4 / 3" />
          <div className="card p-5 bg-white border border-ink/8">
            <div className="eyebrow text-muted/70 mb-1">Balcony Type</div>
            <div className="font-display text-xl text-ink font-normal capitalize">{cabin.balcony_type.toLowerCase().replace(/_/g, ' ')}</div>
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
      <SectionHead eyebrow="Vertical Neighborhood" title="Above, Below & Beside" intro="Knowing what sits directly above your ceiling and below your floor prevents noise surprises." />
      <div className="grid md:grid-cols-3 gap-5">
        <div className="card p-6 bg-white border border-ink/8">
          <p className="eyebrow text-muted/70 mb-4">Vertical Context</p>
          <VerticalRow
            dir="above"
            deck={overhead.deck_number}
            name={overhead.deck_name}
            venues={overhead.venues}
            noise={overhead.is_noise_generator}
          />
          <div className="my-3 p-3.5 bg-paper/60 border border-gold/40 rounded-xs">
            <div className="text-[11px] font-medium uppercase tracking-wider text-ink font-mono">Your Cabin · Deck {cabin.deck_number}</div>
            <div className="text-[12px] text-muted mt-0.5">Cabin {cabin.cabin_number} · {cabin.square_meters} m²</div>
          </div>
          <VerticalRow
            dir="below"
            deck={underfoot.deck_number}
            name={underfoot.deck_name}
            venues={underfoot.venues}
            noise={underfoot.is_noise_generator}
          />
        </div>

        <div className="card p-6 bg-white border border-ink/8">
          <p className="eyebrow text-muted/70 mb-4">Room Details</p>
          <Spec label="Bed Placement" value={cabin.bed_near_balcony == null ? 'Private layout' : cabin.bed_near_balcony ? 'Next to balcony' : 'Next to doorway'} />
          <Spec label="Connecting Door" value={cabin.connecting_cabin_number ? `Yes — to ${cabin.connecting_cabin_number}` : 'None (private wall)'} />
          <Spec label="Doorway Width" value={`${cabin.door_width_mm} mm`} mono />
          <Spec label="Category" value={cabin.category_code} mono />
          <Spec label="Accessibility" value={cabin.is_accessible ? 'Certified accessible' : 'Standard'} last />
        </div>

        <div className="card p-6 bg-white border border-ink/8">
          <p className="eyebrow text-muted/70 mb-4 flex items-center gap-1.5"><Plug className="w-3.5 h-3.5 text-gold" /> Power Sockets</p>
          <div className="grid grid-cols-2 gap-2 text-center">
            <Socket n={cabin.sockets.eu_count} label="EU Sockets" />
            <Socket n={cabin.sockets.us_count} label="US Sockets" />
            <Socket n={cabin.sockets.usb_a_count} label="USB-A" />
            <Socket n={cabin.sockets.usb_c_count} label="USB-C" />
          </div>
          <p className="text-[12px] text-muted mt-4 leading-relaxed">
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
    <div className="p-3.5 bg-paper/40 border border-ink/6 rounded-xs">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-medium uppercase tracking-wider text-ink flex items-center gap-1.5 font-mono">
          <Icon className="w-3.5 h-3.5 text-gold" aria-hidden /> {dir === 'above' ? 'Above' : 'Below'}
          {deck != null && ` · Deck ${deck}`}
        </span>
        {noise && (
          <span className="text-[10px] text-amber-900 bg-amber-50 border border-amber-200 px-1.5 py-0.2 rounded-xs inline-flex items-center gap-1 font-mono">
            <Volume2 className="w-3 h-3" aria-hidden /> Active Area
          </span>
        )}
      </div>
      <p className="text-[12px] text-muted mt-1 leading-snug">
        {venues.length > 0 ? venues.join(', ') : `Residential cabins${name ? ` (${name})` : ''}.`}
      </p>
    </div>
  );
}

function Spec({ label, value, mono, last }: { label: string; value: string; mono?: boolean; last?: boolean }) {
  return (
    <div className={`flex justify-between items-center py-2.5 ${last ? '' : 'border-b border-ink/6'}`}>
      <span className="text-[12px] text-muted">{label}</span>
      <span className={`text-[13px] text-ink ${mono ? 'font-mono' : 'font-medium'}`}>{value}</span>
    </div>
  );
}

function Socket({ n, label }: { n: number; label: string }) {
  return (
    <div className="bg-paper/40 border border-ink/6 rounded-xs py-2.5">
      <div className="font-display text-2xl text-ink leading-none">{n}<span className="text-xs text-muted">×</span></div>
      <div className="text-[10px] uppercase tracking-wider text-muted font-mono mt-1">{label}</div>
    </div>
  );
}

function getDestinationLabel(id: string, ship: ShipData): string {
  const isRiver = ship.total_decks <= 5;
  const customMap: Record<string, string> = {
    buffet: isRiver ? "Arthur's Bistro / Buffet" : 'Marketplace Buffet',
    theater: isRiver ? 'Panorama Lounge & Bar' : 'London Theatre',
    elevator: 'Nearest elevator / lift',
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
      <SectionHead eyebrow="Wayfinding" title="Measured Walking Distances" intro="Exact walking distances and step counts from your door to key venues." />
      <div className="card p-6 md:p-8 bg-white border border-ink/8">
        <div className="flex flex-wrap gap-2">
          {dests.map((id) => (
            <button
              key={id}
              onClick={() => setDest(id)}
              className={`px-3.5 py-1.5 text-xs font-medium border rounded-xs transition cursor-pointer ${
                dest === id ? 'bg-ink text-white border-ink' : 'bg-paper text-ink border-ink/10 hover:border-ink/25'
              }`}
            >
              {getDestinationLabel(id, ship)}
            </button>
          ))}
        </div>
        {d && (
          <div className="mt-8 grid sm:grid-cols-3 gap-6 items-end">
            <div>
              <div className="eyebrow text-muted/70 mb-1">Distance</div>
              <div className="font-display text-4xl sm:text-5xl text-ink leading-none font-normal">{d.meters}<span className="text-xl text-muted font-sans"> m</span></div>
            </div>
            <div>
              <div className="eyebrow text-muted/70 mb-1">Estimated Walk</div>
              <div className="text-[14px] text-ink font-medium">{d.steps} steps · ~{Math.round(d.seconds)} s</div>
            </div>
            <div>
              <div className="eyebrow text-muted/70 mb-1">Route Type</div>
              <div className={`text-[13px] font-medium ${d.step_free ? 'text-emerald-800' : 'text-amber-800'}`}>
                {d.step_free ? 'Step-free (Elevator route)' : 'Includes stairs'}
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
      <SectionHead eyebrow="Deck Structure" title={`Deck ${cabin.deck_number} — ${cabin.deck_name}`} intro="The layout and public venues across this ship level." />
      <div className="grid lg:grid-cols-[1fr_16rem] gap-6">
        <div>
          <Photo src={media(`plan:${cabin.deck_number}`)} kind="plan" label={`Deck ${cabin.deck_number} plan`} ratio="21 / 9" />
          <div className="card mt-4 p-6 bg-white border border-ink/8">
            <div className="eyebrow text-muted/70 mb-3">Public Venues Across Decks</div>
            <ul className="space-y-2">
              {decks.filter((d) => d.venues.length > 0).map((d) => (
                <li key={d.deck_number} className="flex items-start gap-3 text-[13px]">
                  <span className="font-mono text-muted/80 w-16 shrink-0">Deck {d.deck_number}</span>
                  <span className="text-ink">{d.venues.map((v) => v.name).join(' · ')}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* deck rail */}
        <aside className="card p-4 bg-white border border-ink/8">
          <div className="eyebrow text-muted/70 mb-3">Decks</div>
          <ol className="border-l border-ink/10">
            {decks.map((d) => {
              const active = d.deck_number === cabin.deck_number;
              return (
                <li key={d.deck_number} className={`-ml-px border-l-2 pl-3 py-2 ${active ? 'border-gold' : 'border-transparent'}`}>
                  <div className="flex items-baseline gap-2">
                    <span className={`font-mono text-[12px] w-5 ${active ? 'text-ink font-bold' : 'text-muted/70'}`}>{d.deck_number}</span>
                    <div>
                      <div className={`text-[13px] leading-tight ${active ? 'text-ink font-medium' : 'text-muted'}`}>{d.name}</div>
                      <div className="text-[10px] text-muted/60 font-mono mt-0.5">{d.elevation_m}m · {d.zone.replace(/_/g, ' ').toLowerCase()}</div>
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
  { id: 'accessibility', label: 'Mobility & Step-Free', Icon: Accessibility },
  { id: 'family', label: 'Family & Adjoining', Icon: Users },
  { id: 'quiet', label: 'Acoustics & Quiet', Icon: Moon },
] as const;

function Lenses({ cabin, lens, setLens }: { cabin: CabinData; lens: LensId; setLens: (l: LensId) => void }) {
  const summary =
    lens === 'accessibility' ? cabin.lenses.accessibility.summary : lens === 'family' ? cabin.lenses.family.summary : cabin.lenses.quiet.summary;
  const headline =
    lens === 'accessibility'
      ? cabin.lenses.accessibility.is_certified ? 'Certified accessible stateroom' : 'Standard step-free stateroom'
      : lens === 'family'
        ? cabin.lenses.family.has_connecting ? 'Adjoining family stateroom pair' : 'Single stateroom configuration'
        : cabin.lenses.quiet.is_quiet_tier ? 'Acoustically buffered location' : 'Near active public space';

  return (
    <section>
      <SectionHead eyebrow="Travel Filters" title="One Cabin, Three Perspectives" intro="Tailored evaluations for your specific travel needs without changing the underlying deck facts." />
      <div className="card p-6 md:p-8 bg-white border border-ink/8">
        <div className="flex gap-2 flex-wrap">
          {LENSES.map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setLens(id)}
              className={`flex items-center gap-2 px-4 py-2 text-xs font-medium border rounded-xs transition cursor-pointer ${
                lens === id ? 'bg-ink text-white border-ink' : 'bg-paper text-ink border-ink/10 hover:border-ink/25'
              }`}
            >
              <Icon className="w-3.5 h-3.5" aria-hidden /> {label}
            </button>
          ))}
        </div>
        <div className="mt-6">
          <h3 className="font-display text-2xl sm:text-3xl text-ink font-normal">{headline}</h3>
          <p className="text-[14px] text-muted leading-relaxed mt-2.5 max-w-2xl">{summary}</p>
          {lens === 'quiet' && cabin.lenses.quiet.acoustic_flags.length > 0 && (
            <ul className="mt-4 space-y-1">
              {cabin.lenses.quiet.acoustic_flags.map((f) => (
                <li key={f} className="flex items-center gap-2 text-[13px] text-ink font-sans">
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
      <SectionHead eyebrow="Provenance" title="Evidence & Official Sources" intro="Every orientation traces to official general arrangement deck plans and physical survey audits." />
      <div className="grid sm:grid-cols-2 gap-4">
        {cabin.evidence.map((e) => (
          <div key={e.source_id} className="card p-5 bg-white border border-ink/8">
            <div className="flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-gold" aria-hidden />
              <span className="text-[13px] font-medium text-ink">{e.source_id}</span>
            </div>
            <div className="text-[12px] text-muted mt-2">{e.locator.replace(/_/g, ' ')}</div>
            <div className="font-mono text-[10px] text-muted/70 mt-3 break-all bg-paper/60 p-2 rounded-xs">Source hash: {e.sha256}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Discovery({ ship, current, onSelect }: { ship: ShipData; current: string; onSelect: (n: string) => void }) {
  const others = Object.values(ship.cabins).filter((c) => c.cabin_number !== current);
  if (others.length === 0) return null;
  return (
    <section>
      <SectionHead eyebrow="Explore Staterooms" title="Other Mapped Cabins in this Class" />
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {others.slice(0, 9).map((c) => (
          <button
            key={c.cabin_number}
            onClick={() => onSelect(c.cabin_number)}
            className="group card p-5 bg-white border border-ink/8 text-left hover:border-ink/30 transition-colors flex items-center justify-between cursor-pointer"
          >
            <div>
              <div className="font-display text-lg text-ink">Cabin {c.cabin_number}</div>
              <div className="text-[11px] text-muted mt-0.5">
                Deck {c.deck_number} ({c.deck_name}) · {sideLabel(c.hull_side)}{c.is_accessible ? ' · Accessible' : ''}
              </div>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-muted group-hover:text-ink transition-colors" aria-hidden />
          </button>
        ))}
      </div>
    </section>
  );
}
