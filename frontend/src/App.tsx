import React, { useEffect, useState, Suspense } from "react";
import MainNavbar, { NavRoute } from "./components/ui/MainNavbar";
import SpatialProofViewer from "./spatial-proof/SpatialProofViewer";
import Footer from "./components/ui/Footer";
import HomePage from "./components/pages/HomePage";
import CabinDeepDivePage from "./components/pages/CabinDeepDivePage";
import PortGuidePage from "./components/pages/PortGuidePage";
import RouteIntelligencePage from "./components/pages/RouteIntelligencePage";
import CruiseMathPage from "./components/pages/CruiseMathPage";
import TravelInfoPage from "./components/pages/TravelInfoPage";
import { ReferenceTripShellPreview } from "./components/pages/TripShellPage";
import FleetDiscovery from "./passenger/FleetDiscovery";
import PassengerSearchDialog from "./passenger/PassengerSearchDialog";
import { LIVE_TEST_TRIP } from "./trip-shell/liveTestContext";

// Internal review tool (dev-only lazy import, completely stripped from production build)
const DeckReviewPage = import.meta.env.DEV
  ? React.lazy(() => import("./components/pages/DeckReviewPage"))
  : null;

export default function App() {
  // Evidence viewer, reached deliberately rather than through the product nav:
  // every object in the Deck 14 proof is DRAFT / UNKNOWN / PUBLISH_BLOCKED, so it
  // must not appear as a passenger-facing destination.
  if (typeof window !== "undefined" &&
      new URLSearchParams(window.location.search).get("view") === "spatial-proof") {
    return <SpatialProofViewer />;
  }

  // Human Review workspace for Public Deck Geometry Adjudication (dev/internal review only)
  if (typeof window !== "undefined" &&
      new URLSearchParams(window.location.search).get("view") === "deck-review") {
    if (import.meta.env.DEV && DeckReviewPage) {
      return (
        <Suspense fallback={<div className="p-8 text-center text-xs font-mono text-slate-400">Loading review workspace...</div>}>
          <DeckReviewPage />
        </Suspense>
      );
    }
  }
  const [currentRoute, setCurrentRoute] = useState<NavRoute | "cabin">("home");
  // Defaults are the trip the tester is actually on. They used to be four
  // different voyages -- Bellissima, Santorini, an Adriatic route -- so which
  // voyage the product thought you were on depended on which tab you opened.
  const [selectedShipSlug, setSelectedShipSlug] = useState<string>(LIVE_TEST_TRIP.vesselSlug);
  const [selectedProfileSlug, setSelectedProfileSlug] = useState<string | undefined>();
  const [selectedCabinId, setSelectedCabinId] = useState<string>("14122");
  // No port guide exists for either end of this voyage, so there is no port to
  // default to. Undefined means the Ports surface opens as reference browsing
  // rather than opening on some other voyage's port as though it were yours.
  const [selectedPortSlug, setSelectedPortSlug] = useState<string | undefined>(undefined);
  // Likewise no route dataset exists for Shanghai -> Tokyo. Defaulting to one
  // that does exist is how the Western Mediterranean became "your route".
  const [selectedRouteSlug, setSelectedRouteSlug] = useState<string | undefined>(undefined);

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    window.history.replaceState({ timonelo: true, route: 'home' }, '');
    const restore = (event: PopStateEvent) => {
      const state = event.state;
      if (!state?.timonelo || !['home', 'ships', 'cabin', 'ports', 'routes', 'cruise-math', 'travel-info', 'my-cruise'].includes(state.route)) return;
      setCurrentRoute(state.route);
      setIsSearchOpen(false);
      if (state.route === 'ships') {
        setSelectedProfileSlug(state.param);
        if (state.param) setSelectedShipSlug(state.param);
      }
      if (state.route === 'cabin') setSelectedShipSlug(state.vessel || LIVE_TEST_TRIP.vesselSlug);
      if (state.route === 'cabin') setSelectedCabinId(state.param || '');
      if (state.route === 'ports') setSelectedPortSlug(state.param);
      if (state.route === 'routes') setSelectedRouteSlug(state.param);
    };
    window.addEventListener('popstate', restore);
    return () => window.removeEventListener('popstate', restore);
  }, []);

  const handleNavigate = (route: NavRoute | "cabin", param?: string, vessel?: string) => {
    const cabinVessel = vessel || selectedShipSlug;
    window.history.pushState({ timonelo: true, route, param, vessel: cabinVessel }, '');
    if (route === 'ships') setSelectedProfileSlug(param);
    if (route === "ships" && param) setSelectedShipSlug(param);
    if (route === "cabin" && param) {
      setSelectedCabinId(param);
      setSelectedShipSlug(cabinVessel);
    }
    if (route === "ports" && param) setSelectedPortSlug(param);
    if (route === "routes" && param) setSelectedRouteSlug(param);

    setCurrentRoute(route);
    window.scrollTo({ top: 0, behavior: "instant" });
  };

  const handleSearchSubmit = (query: string) => {
    setSearchQuery(query);
    setIsSearchOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FBF8F3] text-[#0C1B2A] font-sans selection:bg-[#C58A46]/20">
      {/* 1. Global Navigation Header */}
      <MainNavbar
        currentRoute={currentRoute as NavRoute}
        onNavigate={handleNavigate}
        onOpenSearch={() => handleSearchSubmit('')}
      />

      {/* 2. Page Switcher */}
      <main className="flex-1 flex flex-col">
        {currentRoute === "home" && (
          <HomePage
            onNavigate={handleNavigate}
            onSearch={handleSearchSubmit}
          />
        )}

        {currentRoute === "ships" && (
          <FleetDiscovery selectedSlug={selectedProfileSlug} onNavigate={handleNavigate} />
        )}

        {currentRoute === "cabin" && (
          <CabinDeepDivePage
            vesselId={selectedShipSlug}
            cabinId={selectedCabinId}
            onBack={() => handleNavigate("ships", selectedShipSlug)}
          />
        )}

        {currentRoute === "ports" && (
          <PortGuidePage
            portSlug={selectedPortSlug}
            onSelectPort={(slug) => handleNavigate("ports", slug)}
          />
        )}

        {currentRoute === "routes" && (
          <RouteIntelligencePage
            routeSlug={selectedRouteSlug}
            onSelectPort={(slug) => handleNavigate("ports", slug)}
          />
        )}

        {currentRoute === "cruise-math" && (
          <CruiseMathPage />
        )}

        {currentRoute === "travel-info" && (
          <TravelInfoPage />
        )}

        {currentRoute === "my-cruise" && (
          <ReferenceTripShellPreview
            onBack={() => handleNavigate("home")}
          />
        )}
      </main>

      {currentRoute !== 'home' && <nav aria-label="Passenger pages" className="max-w-7xl mx-auto w-full px-4 py-6 flex flex-wrap gap-2">{([{ route: 'home', label: 'Home' }, { route: 'my-cruise', label: 'My Cruise' }, { route: 'ships', label: 'Ships' }, { route: 'routes', label: 'Routes' }, { route: 'ports', label: 'Ports' }, { route: 'travel-info', label: 'Travel Info' }, { route: 'cruise-math', label: 'Cruise Math' }] as const).map(item => <button key={item.route} className="min-h-11 rounded-xl border px-3 text-sm bg-white" onClick={() => handleNavigate(item.route)}>{item.label}</button>)}</nav>}

      {/* 3. Colophon Footer */}
      <Footer />

      {/* Search Modal Overlay */}
      {isSearchOpen && (
        <PassengerSearchDialog initialQuery={searchQuery} vesselSlug={selectedShipSlug} onClose={() => setIsSearchOpen(false)} onSelect={destination => { setIsSearchOpen(false); handleNavigate(destination.route, destination.param, destination.vesselSlug); }} />
      )}
    </div>
  );
}
