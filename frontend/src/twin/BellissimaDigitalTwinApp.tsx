import React, { useState, useEffect } from "react";
import ShipCanvas3D from "./components/ShipCanvas3D";
import DeckSelector from "./components/DeckSelector";
import RightDetailPanel from "./components/RightDetailPanel";
import GlobalSearchBar from "./components/GlobalSearchBar";
import LayerControlBar from "./components/LayerControlBar";
import RouteNavigationModal from "./components/RouteNavigationModal";
import EvidenceSplitView from "./components/EvidenceSplitView";
import EpistemologyInspectorModal from "./components/EpistemologyInspectorModal";
import BottomStatusBar from "./components/BottomStatusBar";
import { CabinData, VenueData, ViewMode, ActiveLayers, RouteResult } from "./types";
import { getCabin, DECKS_MAP, calculateRoute, SearchResultItem } from "./twinEngine";

export default function BellissimaDigitalTwinApp() {
  const [viewMode, setViewMode] = useState<ViewMode>("deck_topdown");
  const [activeDeck, setActiveDeck] = useState<number>(14); // Default to Deck 14 (World Class)
  const [selectedCabin, setSelectedCabin] = useState<CabinData | null>(null);
  const [selectedVenue, setSelectedVenue] = useState<VenueData | null>(null);
  const [hoveredCabin, setHoveredCabin] = useState<CabinData | null>(null);

  const [activeRoute, setActiveRoute] = useState<RouteResult | null>(null);
  const [accessibleOnly, setAccessibleOnly] = useState<boolean>(false);

  const [isEvidenceOpen, setIsEvidenceOpen] = useState<boolean>(false);
  const [isEpistemologyOpen, setIsEpistemologyOpen] = useState<boolean>(false);

  const [layers, setLayers] = useState<ActiveLayers>({
    cabins: true,
    restaurants: true,
    bars: true,
    pools: true,
    shops: true,
    toilets: true,
    elevators: true,
    stairs: true,
    accessible: true,
    routingGraph: true,
    landmarks: true,
    zones: true,
    heatmap: false,
  });

  // Default selection: Cabin 14122 on startup
  useEffect(() => {
    const c14122 = getCabin("14122");
    if (c14122) {
      setSelectedCabin(c14122);
    }
  }, []);

  const handleSelectDeck = (deckNum: number) => {
    setActiveDeck(deckNum);
    setViewMode("deck_topdown");
  };

  const handleSelectCabin = (cabin: CabinData) => {
    setSelectedCabin(cabin);
    setSelectedVenue(null);
    setActiveDeck(cabin.deck);
    setViewMode("deck_topdown");
  };

  const handleSelectVenue = (venue: VenueData) => {
    setSelectedVenue(venue);
    setSelectedCabin(null);
    setActiveDeck(venue.deck);
    setViewMode("deck_topdown");
  };

  const handleSelectSearchResult = (item: SearchResultItem) => {
    if (item.category === "CABIN") {
      handleSelectCabin(item.data as CabinData);
    } else if (item.category === "VENUE") {
      handleSelectVenue(item.data as VenueData);
    } else {
      setActiveDeck(item.deck);
    }
  };

  const handleStartRoute = (from: string, to: string) => {
    const route = calculateRoute(from, to, accessibleOnly);
    setActiveRoute(route);
  };

  const handleToggleAccessible = () => {
    const nextAcc = !accessibleOnly;
    setAccessibleOnly(nextAcc);
    if (activeRoute) {
      const updated = calculateRoute(activeRoute.from, activeRoute.to, nextAcc);
      setActiveRoute(updated);
    }
  };

  const handleToggleLayer = (key: keyof ActiveLayers) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const deckData = DECKS_MAP.get(activeDeck);
  const deckName = deckData?.deck_name ?? "Deck 14";

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-950 text-white font-sans">
      {/* Top Header & Search Bar */}
      <div className="absolute top-6 left-6 right-6 z-30 flex items-center justify-between pointer-events-none">
        {/* Brand Label */}
        <div className="flex items-center gap-3 pointer-events-auto">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20 text-lg">
            T
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-tight flex items-center gap-2">
              MSC Bellissima
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-sky-500/20 text-sky-300 border border-sky-400/30">
                Digital Twin
              </span>
            </h1>
            <p className="text-xs text-slate-400">Timonelo Spatial Knowledge Factory</p>
          </div>
        </div>

        {/* Center Global Search */}
        <GlobalSearchBar onSelectResult={handleSelectSearchResult} />

        {/* Right Layer Filters */}
        <LayerControlBar layers={layers} onToggleLayer={handleToggleLayer} />
      </div>

      {/* Main 3D / 2D Canvas */}
      <ShipCanvas3D
        viewMode={viewMode}
        activeDeck={activeDeck}
        selectedCabin={selectedCabin}
        selectedVenue={selectedVenue}
        hoveredCabin={hoveredCabin}
        activeRoute={activeRoute}
        layers={layers}
        onSelectCabin={handleSelectCabin}
        onHoverCabin={setHoveredCabin}
        onSelectVenue={handleSelectVenue}
        onSelectDeck={handleSelectDeck}
      />

      {/* Left Deck Selector Stack */}
      <DeckSelector
        activeDeck={activeDeck}
        onSelectDeck={handleSelectDeck}
        viewMode={viewMode}
        onToggleViewMode={setViewMode}
      />

      {/* Right Stateroom & Venue Deep Dive Inspector */}
      <RightDetailPanel
        selectedCabin={selectedCabin}
        selectedVenue={selectedVenue}
        onClose={() => {
          setSelectedCabin(null);
          setSelectedVenue(null);
        }}
        onStartRoute={handleStartRoute}
        onOpenEvidence={(c) => setIsEvidenceOpen(true)}
        onSelectCabinNumber={(num) => {
          const c = getCabin(num);
          if (c) handleSelectCabin(c);
        }}
      />

      {/* Turn-by-Turn Route Navigation Drawer */}
      <RouteNavigationModal
        route={activeRoute}
        accessibleOnly={accessibleOnly}
        onToggleAccessible={handleToggleAccessible}
        onClose={() => setActiveRoute(null)}
      />

      {/* Split Screen Official PDF Evidence Viewer */}
      {isEvidenceOpen && selectedCabin && (
        <EvidenceSplitView
          cabin={selectedCabin}
          onClose={() => setIsEvidenceOpen(false)}
          onOpenEpistemology={() => {
            setIsEvidenceOpen(false);
            setIsEpistemologyOpen(true);
          }}
        />
      )}

      {/* Epistemology & Reasoning Chain Inspector Modal */}
      {isEpistemologyOpen && selectedCabin && (
        <EpistemologyInspectorModal
          cabin={selectedCabin}
          onClose={() => setIsEpistemologyOpen(false)}
        />
      )}

      {/* Bottom Telemetry Status Bar */}
      <BottomStatusBar
        activeDeck={activeDeck}
        deckName={deckName}
        selectedCabin={selectedCabin}
        selectedVenue={selectedVenue}
        onOpenEpistemology={() => setIsEpistemologyOpen(true)}
      />
    </div>
  );
}
