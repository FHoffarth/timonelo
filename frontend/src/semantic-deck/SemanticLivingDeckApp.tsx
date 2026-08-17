import React, { useState, useEffect, useMemo } from "react";
import { SemanticDeckEngine } from "./semanticEngine";
import { SemanticDeck, SemanticObject } from "./types";
import DeckNavigationStack from "./components/DeckNavigationStack";
import SemanticDeckGrid from "./components/SemanticDeckGrid";
import SemanticObjectInspector from "./components/SemanticObjectInspector";
import EpistemicLegendBar from "./components/EpistemicLegendBar";
import SemanticSearchBar from "./components/SemanticSearchBar";
import { Compass, Sparkles, ShieldCheck } from "lucide-react";

export default function SemanticLivingDeckApp() {
  const [selectedVesselId, setSelectedVesselId] = useState<string>("msc-bellissima");
  const engine = useMemo(() => new SemanticDeckEngine(selectedVesselId), [selectedVesselId]);

  const currentVessel = engine.getVessel();
  const decks = engine.getDecks();

  // Default active deck: Deck 14 on Bellissima or top deck on other vessels
  const [activeDeckLevel, setActiveDeckLevel] = useState<number>(
    selectedVesselId === "msc-bellissima" ? 14 : decks[0]?.deck_level ?? 1
  );

  const [selectedObject, setSelectedObject] = useState<SemanticObject | null>(null);
  const [hoveredObject, setHoveredObject] = useState<SemanticObject | null>(null);

  // Focus Cabin 14122 by default when loaded on MSC Bellissima
  useEffect(() => {
    if (selectedVesselId === "msc-bellissima") {
      const c14122 = engine.getObject("14122");
      if (c14122) {
        setSelectedObject(c14122);
        setActiveDeckLevel(c14122.deck);
      }
    } else {
      const firstObj = decks[0]?.objects[0];
      if (firstObj) {
        setSelectedObject(firstObj);
        setActiveDeckLevel(decks[0].deck_level);
      }
    }
  }, [selectedVesselId, engine, decks]);

  const activeDeck = engine.getDeck(activeDeckLevel) || decks[0];

  const handleSelectVessel = (vesselId: string) => {
    setSelectedVesselId(vesselId);
  };

  const handleSelectDeck = (deckLevel: number) => {
    setActiveDeckLevel(deckLevel);
  };

  const handleSelectObject = (obj: SemanticObject) => {
    setSelectedObject(obj);
    setActiveDeckLevel(obj.deck);
  };

  const handleSelectObjectId = (id: string) => {
    const obj = engine.getObject(id);
    if (obj) {
      handleSelectObject(obj);
    }
  };

  return (
    <div className="w-screen h-screen overflow-hidden bg-slate-950 text-white font-sans flex flex-col">
      {/* Top Navbar */}
      <header className="h-16 px-6 bg-slate-900/90 backdrop-blur-2xl border-b border-white/10 flex items-center justify-between z-30 select-none">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20 text-base">
            T
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-white tracking-tight">
                Timonelo Living Deck
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Semantic Spatial Model
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {currentVessel.vessel_name} • Reusable Schematic Interface
            </p>
          </div>
        </div>

        {/* Search */}
        <SemanticSearchBar
          onSearch={(q) => engine.search(q)}
          onSelectObject={handleSelectObject}
        />

        {/* Telemetry pill */}
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950/80 border border-white/5 text-xs font-mono text-slate-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{currentVessel.epistemic_summary.total_objects} Objects Loaded</span>
          </div>
        </div>
      </header>

      {/* Epistemic Legend Bar: Orthogonal Separation of Content vs Knowledge */}
      <EpistemicLegendBar />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left: Deck Navigation Stack */}
        <DeckNavigationStack
          currentVessel={currentVessel}
          activeDeckLevel={activeDeckLevel}
          onSelectVessel={handleSelectVessel}
          onSelectDeck={handleSelectDeck}
        />

        {/* Center: Schematic Topological Grid */}
        {activeDeck ? (
          <SemanticDeckGrid
            deck={activeDeck}
            selectedObject={selectedObject}
            hoveredObject={hoveredObject}
            onSelectObject={handleSelectObject}
            onHoverObject={setHoveredObject}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-sm font-mono">
            No deck objects loaded.
          </div>
        )}

        {/* Right: Semantic Object Inspector */}
        <SemanticObjectInspector
          object={selectedObject}
          onClose={() => setSelectedObject(null)}
          onSelectObjectId={handleSelectObjectId}
        />
      </div>
    </div>
  );
}
