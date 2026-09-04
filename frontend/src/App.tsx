import React, { useState, Suspense } from "react";
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
import { PassengerShipOverview } from "./components/pages/ShipOverviewPage";
import SemanticSearchBar from "./semantic-deck/components/SemanticSearchBar";
import { TimoneloSpatialApiClient } from "./semantic-deck/apiClient";
import { SemanticEntity } from "./semantic-deck/types";
import { LIVE_TEST_TRIP } from "./trip-shell/liveTestContext";
import { X } from "lucide-react";

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
  const [selectedCabinId, setSelectedCabinId] = useState<string>("14122");
  // No port guide exists for either end of this voyage, so there is no port to
  // default to. Undefined means the Ports surface opens as reference browsing
  // rather than opening on some other voyage's port as though it were yours.
  const [selectedPortSlug, setSelectedPortSlug] = useState<string | undefined>(undefined);
  // Likewise no route dataset exists for Shanghai -> Tokyo. Defaulting to one
  // that does exist is how the Western Mediterranean became "your route".
  const [selectedRouteSlug, setSelectedRouteSlug] = useState<string | undefined>(undefined);

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const apiClient = new TimoneloSpatialApiClient("msc-bellissima");

  const handleNavigate = (route: NavRoute | "cabin", param?: string) => {
    if (route === "ships" && param) setSelectedShipSlug(param);
    if (route === "cabin" && param) setSelectedCabinId(param);
    if (route === "ports" && param) setSelectedPortSlug(param);
    if (route === "routes" && param) setSelectedRouteSlug(param);

    setCurrentRoute(route);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleGlobalSearchSelect = (entity: SemanticEntity) => {
    setIsSearchOpen(false);
    setSelectedCabinId(entity.id);
    setSelectedShipSlug(LIVE_TEST_TRIP.vesselSlug);
    setCurrentRoute("cabin");
  };

  const handleSearchSubmit = (query: string) => {
    const q = query.toLowerCase();
    if (q.includes("cabin") || /^\d{4,5}$/.test(q)) {
      const match = q.match(/\d{4,5}/);
      const cabinId = match ? match[0] : "14122";
      handleNavigate("cabin", cabinId);
    } else if (q.includes("port") || q.includes("santorini") || q.includes("genoa")) {
      // Searching a port name opens the Ports surface, which frames itself as
      // reference browsing. Naming a port must not make it a stop on this
      // voyage, so nothing is preselected as "yours".
      handleNavigate("ports");
    } else if (q.includes("route") || q.includes("adriatic") || q.includes("aegean")) {
      // No route dataset exists for this voyage. Search used to hand the
      // Adriatic keyword straight to a Western Mediterranean itinerary and
      // present it as the passenger's; the surface now says it has nothing.
      handleNavigate("routes");
    } else if (q.includes("math") || q.includes("drink") || q.includes("price") || q.includes("cost")) {
      handleNavigate("cruise-math");
    } else if (q.includes("visa") || q.includes("travel") || q.includes("passport")) {
      handleNavigate("travel-info");
    } else {
      handleNavigate("ships", LIVE_TEST_TRIP.vesselSlug);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FBF8F3] text-[#0C1B2A] font-sans selection:bg-[#C58A46]/20">
      {/* 1. Global Navigation Header */}
      <MainNavbar
        currentRoute={currentRoute as NavRoute}
        onNavigate={handleNavigate}
        onOpenSearch={() => setIsSearchOpen(true)}
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
          <PassengerShipOverview vesselId={selectedShipSlug} />
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

      {/* 3. Colophon Footer */}
      <Footer />

      {/* Search Modal Overlay */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 bg-[#0C1B2A]/60 backdrop-blur-sm flex items-start justify-center pt-24 px-6 animate-fadeIn">
          <div className="bg-white rounded-3xl p-6 w-full max-w-xl shadow-2xl border border-[#0C1B2A]/10 space-y-4">
            <div className="flex items-center justify-between">
              <span className="eyebrow-tag">UNIVERSAL INTELLIGENCE SEARCH</span>
              <button
                onClick={() => setIsSearchOpen(false)}
                className="p-1.5 rounded-full hover:bg-slate-100 text-slate-500 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <SemanticSearchBar
              onSearch={(q) => apiClient.searchEntities(q)}
              onSelectEntity={handleGlobalSearchSelect}
            />
            <div className="pt-2 text-[11px] text-[#5B6570] flex items-center justify-between">
              <span>Try searching "14122", "Santorini", "Balcony", "Bellissima", or "Drink Packages"</span>
              <span className="font-mono text-[#C58A46]">ESC to close</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
