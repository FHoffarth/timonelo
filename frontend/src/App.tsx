import React, { useState } from "react";
import MainNavbar, { NavRoute } from "./components/ui/MainNavbar";
import SpatialProofViewer from "./spatial-proof/SpatialProofViewer";
import Footer from "./components/ui/Footer";
import HomePage from "./components/pages/HomePage";
import ShipProfilePage from "./components/pages/ShipProfilePage";
import CabinDeepDivePage from "./components/pages/CabinDeepDivePage";
import PortGuidePage from "./components/pages/PortGuidePage";
import RouteIntelligencePage from "./components/pages/RouteIntelligencePage";
import CruiseMathPage from "./components/pages/CruiseMathPage";
import TravelInfoPage from "./components/pages/TravelInfoPage";
import KnowledgeDashboardPage from "./components/pages/KnowledgeDashboardPage";
import { ReferenceTripShellPreview } from "./components/pages/TripShellPage";
import { ReferenceShipOverviewPreview } from "./components/pages/ShipOverviewPage";
import SemanticSearchBar from "./semantic-deck/components/SemanticSearchBar";
import { TimoneloSpatialApiClient } from "./semantic-deck/apiClient";
import { SemanticEntity } from "./semantic-deck/types";
import { X } from "lucide-react";

export default function App() {
  // Evidence viewer, reached deliberately rather than through the product nav:
  // every object in the Deck 14 proof is DRAFT / UNKNOWN / PUBLISH_BLOCKED, so it
  // must not appear as a passenger-facing destination.
  if (typeof window !== "undefined" &&
      new URLSearchParams(window.location.search).get("view") === "spatial-proof") {
    return <SpatialProofViewer />;
  }
  const [currentRoute, setCurrentRoute] = useState<NavRoute | "cabin">("home");
  const [selectedShipSlug, setSelectedShipSlug] = useState<string>("msc-bellissima");
  const [selectedCabinId, setSelectedCabinId] = useState<string>("14122");
  const [selectedPortSlug, setSelectedPortSlug] = useState<string>("santorini");
  const [selectedRouteSlug, setSelectedRouteSlug] = useState<string>("7-night-adriatic-aegean");

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
    setSelectedShipSlug("msc-bellissima");
    setCurrentRoute("cabin");
  };

  const handleSearchSubmit = (query: string) => {
    const q = query.toLowerCase();
    if (q.includes("cabin") || /^\d{4,5}$/.test(q)) {
      const match = q.match(/\d{4,5}/);
      const cabinId = match ? match[0] : "14122";
      handleNavigate("cabin", cabinId);
    } else if (q.includes("port") || q.includes("santorini") || q.includes("genoa")) {
      handleNavigate("ports", q.includes("genoa") ? "genoa" : "santorini");
    } else if (q.includes("route") || q.includes("adriatic") || q.includes("aegean")) {
      handleNavigate("routes", "7-night-adriatic-aegean");
    } else if (q.includes("math") || q.includes("drink") || q.includes("price") || q.includes("cost")) {
      handleNavigate("cruise-math");
    } else if (q.includes("visa") || q.includes("travel") || q.includes("passport")) {
      handleNavigate("travel-info");
    } else if (q.includes("factory") || q.includes("pipeline") || q.includes("conflict")) {
      handleNavigate("knowledge-factory");
    } else {
      handleNavigate("ships", "msc-bellissima");
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
          <ReferenceShipOverviewPreview />
        )}

        {currentRoute === "cabin" && (
          <CabinDeepDivePage
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

        {currentRoute === "knowledge-factory" && (
          <KnowledgeDashboardPage />
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
