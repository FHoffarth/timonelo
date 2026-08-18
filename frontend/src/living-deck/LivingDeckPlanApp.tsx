import React, { useState, useEffect } from "react";
import LivingDeckCanvas from "./components/LivingDeckCanvas";
import LivingDeckSelector from "./components/LivingDeckSelector";
import LivingRightInspector from "./components/LivingRightInspector";
import LivingSearchBar from "./components/LivingSearchBar";
import LivingEvidenceModal from "./components/LivingEvidenceModal";
import LivingBottomBar from "./components/LivingBottomBar";
import { knowledgeRepository } from "../knowledge";
import { LivingCabin, LivingViewMode } from "./types";
import {
  getLivingCabin,
  getLivingDeck,
  computeLivingRoute,
  ProvenRoute,
  LivingSearchResult,
} from "./livingEngine";

export default function LivingDeckPlanApp() {
  const [viewMode, setViewMode] = useState<LivingViewMode>("single_deck");
  const [activeDeck, setActiveDeck] = useState<number>(14); // Default to Deck 14 (World Class)
  const [selectedCabin, setSelectedCabin] = useState<LivingCabin | null>(null);
  const [hoveredCabin, setHoveredCabin] = useState<LivingCabin | null>(null);

  const [activeRoute, setActiveRoute] = useState<ProvenRoute | null>(null);
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState<boolean>(false);

  // Default focus: Cabin 14122
  useEffect(() => {
    const c14122 = getLivingCabin("14122");
    if (c14122) {
      setSelectedCabin(c14122);
    }
  }, []);

  const handleSelectDeck = (deckNum: number) => {
    setActiveDeck(deckNum);
  };

  const handleSelectCabin = (cabin: LivingCabin) => {
    setSelectedCabin(cabin);
    setActiveDeck(cabin.deck);
    setViewMode("single_deck");
  };

  const handleSearchResult = (result: LivingSearchResult) => {
    if (result.cabin) {
      handleSelectCabin(result.cabin);
    } else {
      setActiveDeck(result.deck);
      setViewMode("single_deck");
    }
  };

  const handleStartRoute = (cabinNum: string, target: string) => {
    const route = computeLivingRoute(cabinNum, target);
    setActiveRoute(route);
  };

  const currentDeckObj = getLivingDeck(activeDeck);
  const deckName = currentDeckObj?.deck_name ?? `Deck ${activeDeck}`;

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-950 text-white font-sans">
      {/* Top Header & Search Bar */}
      <div className="absolute top-6 left-6 right-6 z-30 flex items-center justify-between pointer-events-none select-none">
        {/* Brand */}
        <div className="flex items-center gap-3 pointer-events-auto">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20 text-lg">
            T
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-tight flex items-center gap-2">
              Living Deck Plans
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Official PDF Alive
              </span>
            </h1>
            <p className="text-xs text-slate-400">{knowledgeRepository.getShip("msc-bellissima").vessel_name} • Verified Topology</p>
          </div>
        </div>

        {/* Global Instant Search */}
        <LivingSearchBar onSelectResult={handleSearchResult} />

        {/* Empty placeholder for balance */}
        <div className="w-32 hidden md:block" />
      </div>

      {/* Main Living Deck Canvas (Single Deck or Exploded Stack) */}
      <LivingDeckCanvas
        viewMode={viewMode}
        activeDeck={activeDeck}
        selectedCabin={selectedCabin}
        hoveredCabin={hoveredCabin}
        activeRoute={activeRoute}
        onSelectCabin={handleSelectCabin}
        onHoverCabin={setHoveredCabin}
        onSelectDeck={handleSelectDeck}
      />

      {/* Left Deck Selector & Exploded Mode Toggle */}
      <LivingDeckSelector
        activeDeck={activeDeck}
        viewMode={viewMode}
        onSelectDeck={handleSelectDeck}
        onToggleViewMode={setViewMode}
      />

      {/* Right Detail Inspector */}
      <LivingRightInspector
        cabin={selectedCabin}
        onClose={() => setSelectedCabin(null)}
        onStartRoute={handleStartRoute}
        onOpenEvidence={() => setIsEvidenceModalOpen(true)}
        onSelectCabinNumber={(num) => {
          const c = getLivingCabin(num);
          if (c) handleSelectCabin(c);
        }}
      />

      {/* Ground Truth & Epistemology Modal */}
      {isEvidenceModalOpen && selectedCabin && (
        <LivingEvidenceModal
          cabin={selectedCabin}
          onClose={() => setIsEvidenceModalOpen(false)}
        />
      )}

      {/* Bottom Telemetry Bar */}
      <LivingBottomBar
        activeDeck={activeDeck}
        deckName={deckName}
        selectedCabin={selectedCabin}
        onOpenEvidence={() => setIsEvidenceModalOpen(true)}
      />
    </div>
  );
}
