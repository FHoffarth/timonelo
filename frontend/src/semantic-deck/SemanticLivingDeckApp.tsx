import { useState, useEffect, useMemo } from "react";
import { TimoneloSpatialApiClient } from "./apiClient";
import { SemanticEntity } from "./types";
import { ThemeProvider, useTheme } from "./themeContext";
import DeckNavigationTree from "./components/DeckNavigationTree";
import SpatialGrammarCanvas from "./components/SpatialGrammarCanvas";
import SemanticObjectInspector from "./components/SemanticObjectInspector";
import EpistemicLegendBar from "./components/EpistemicLegendBar";
import SemanticSearchBar from "./components/SemanticSearchBar";
import StandardsInspectorModal from "./components/StandardsInspectorModal";
import {
  History,
  Workflow,
  Sun,
  Moon,
  Footprints,
} from "lucide-react";

function LivingDeckInner() {
  const { theme, toggleTheme } = useTheme();
  const isNight = theme === "night";

  const [selectedVesselId, setSelectedVesselId] = useState<string>("msc-bellissima");
  const apiClient = useMemo(() => new TimoneloSpatialApiClient(selectedVesselId), [selectedVesselId]);

  const vesselGraph = apiClient.getVesselGraph();
  const levels = vesselGraph.levels || [];

  // Default active level: Level 14 (Girasole / World Class) or top level
  const [activeLevelIndex, setActiveLevelIndex] = useState<number>(
    selectedVesselId === "msc-bellissima" ? 14 : levels[0]?.level_index ?? 1
  );

  const [selectedEntity, setSelectedEntity] = useState<SemanticEntity | null>(null);
  const [hoveredEntity, setHoveredEntity] = useState<SemanticEntity | null>(null);

  // Standards Inspector Modal state
  const [inspectingStandardsEntity, setInspectingStandardsEntity] = useState<SemanticEntity | null>(null);

  // Active top-level platform mode
  const [activePlatformView, setActivePlatformView] = useState<
    "LIVING_DECK" | "TOPOLOGY_INSPECTOR" | "PROVENANCE_VIEWER"
  >("LIVING_DECK");

  // Focus Cabin 14122 by default on Deck 14
  useEffect(() => {
    if (selectedVesselId === "msc-bellissima") {
      const defaultSpace = apiClient.getEntity("14122") || apiClient.getEntity("10012") || levels[0]?.spaces[0];
      if (defaultSpace) {
        setSelectedEntity(defaultSpace);
        setActiveLevelIndex(defaultSpace.level);
      }
    } else {
      const firstEntity = levels[0]?.spaces[0];
      if (firstEntity) {
        setSelectedEntity(firstEntity);
        setActiveLevelIndex(levels[0].level_index);
      }
    }
  }, [selectedVesselId, apiClient, levels]);

  const activeLevel = apiClient.getLevel(activeLevelIndex) || levels[0];

  const handleSelectVessel = (vesselId: string) => {
    setSelectedVesselId(vesselId);
  };

  const handleSelectLevel = (levelIndex: number) => {
    setActiveLevelIndex(levelIndex);
  };

  const handleSelectEntity = (entity: SemanticEntity | null) => {
    setSelectedEntity(entity);
    if (entity) setActiveLevelIndex(entity.level);
  };

  const handleSelectEntityId = (id: string) => {
    const ent = apiClient.getEntity(id);
    if (ent) {
      handleSelectEntity(ent);
    }
  };

  return (
    <div className={`w-screen h-screen overflow-hidden font-sans flex flex-col ${isNight ? "bg-slate-950 text-white" : "bg-slate-100 text-slate-900"}`}>
      {/* Top Navbar */}
      <header className={`h-16 px-6 border-b flex items-center justify-between z-30 select-none backdrop-blur-2xl transition-colors duration-200 ${isNight ? "bg-slate-900/90 border-white/10" : "bg-white/95 border-slate-200"}`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20 text-base">
            T
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-tight">
                Timonelo Living Deck
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                LEGACY SCHEMATIC DATASET
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {vesselGraph.vessel_name} • Spatial Grammar & Mental Model Navigation
            </p>
          </div>
        </div>

        {/* Global Search across all spatial entities */}
        <SemanticSearchBar
          onSearch={(q) => apiClient.searchEntities(q)}
          onSelectEntity={handleSelectEntity}
        />

        {/* Top Platform View Switcher & Day/Night Mode */}
        <div className="flex items-center gap-3">
          <div className={`p-1 rounded-2xl border flex items-center gap-1 text-xs ${isNight ? "bg-slate-950/80 border-white/5" : "bg-slate-100 border-slate-200"}`}>
            <button
              onClick={() => setActivePlatformView("LIVING_DECK")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "LIVING_DECK"
                  ? "bg-sky-500/20 text-sky-400 border border-sky-400/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Footprints className="w-3.5 h-3.5" />
              Living Deck
            </button>
            <button
              onClick={() => setActivePlatformView("TOPOLOGY_INSPECTOR")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "TOPOLOGY_INSPECTOR"
                  ? "bg-sky-500/20 text-sky-400 border border-sky-400/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Workflow className="w-3.5 h-3.5" />
              Topology Inspector
            </button>
            <button
              onClick={() => setActivePlatformView("PROVENANCE_VIEWER")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "PROVENANCE_VIEWER"
                  ? "bg-sky-500/20 text-sky-400 border border-sky-400/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <History className="w-3.5 h-3.5" />
              PROV-O Viewer
            </button>
          </div>

          {/* Day Shift / Night Shift Toggle */}
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-xl border transition-colors flex items-center gap-1.5 text-xs font-semibold ${
              isNight
                ? "bg-slate-900 border-white/10 text-amber-300 hover:bg-slate-800"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-100 shadow-sm"
            }`}
            title={`Switch to ${isNight ? "Day Shift" : "Night Shift"}`}
          >
            {isNight ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
          </button>
        </div>
      </header>

      {/* Epistemic Subheader: Content Categories vs Knowledge Certainty */}
      <EpistemicLegendBar />

      {/* Main Workspace Layout: Left Tree + Spatial Grammar Canvas + Right Inspector */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left: Navigation Tree */}
        <DeckNavigationTree
          currentVessel={vesselGraph}
          activeDeckLevel={activeLevelIndex}
          onSelectVessel={handleSelectVessel}
          onSelectDeck={handleSelectLevel}
        />

        {/* Center: Living Deck Spatial Grammar Canvas */}
        {activePlatformView === "LIVING_DECK" && activeLevel && (
          <SpatialGrammarCanvas
            level={activeLevel}
            selectedEntity={selectedEntity}
            hoveredEntity={hoveredEntity}
            allLevels={levels}
            onSelectLevel={handleSelectLevel}
            onSelectEntity={handleSelectEntity}
            onHoverEntity={setHoveredEntity}
          />
        )}

        {/* Topology Inspector View */}
        {activePlatformView === "TOPOLOGY_INSPECTOR" && (
          <div className="flex-1 p-8 overflow-y-auto no-scrollbar flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-sky-500/10 border border-sky-400/20 flex items-center justify-center text-sky-400">
              <Workflow className="w-8 h-8" />
            </div>
            <h2 className="text-lg font-bold text-white">Topology unavailable for passenger use</h2>
            <p className="text-xs text-slate-400 max-w-md text-center leading-relaxed">
              This view is backed by a legacy schematic dataset. No adjacency,
              corridor, or vertical connectivity has crossed the canonical gate.
            </p>
            <div className="p-4 bg-slate-900/60 rounded-2xl border border-white/10 text-xs font-mono text-slate-300 space-y-1">
              <div>Admission state: PUBLISH_BLOCKED</div>
              <div>Admitted topology edges: 0</div>
              <div>Computed confidence: unavailable</div>
            </div>
          </div>
        )}

        {/* PROV-O Provenance Viewer */}
        {activePlatformView === "PROVENANCE_VIEWER" && (
          <div className="flex-1 p-8 overflow-y-auto no-scrollbar flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <History className="w-8 h-8" />
            </div>
            <h2 className="text-lg font-bold text-white">Canonical lineage unavailable</h2>
            <p className="text-xs text-slate-400 max-w-md text-center leading-relaxed">
              Legacy source links do not prove how each attached value came into
              existence. They are not presented as Ground Truth provenance.
            </p>
            <div className="p-4 bg-slate-900/60 rounded-2xl border border-white/10 text-xs font-mono text-emerald-300 space-y-1">
              <div>Data origin: LEGACY_SCHEMATIC</div>
              <div>Admitted provenance records: 0</div>
              <div>Passenger state: UNKNOWN</div>
            </div>
          </div>
        )}

        {/* Right: Semantic Object Inspector */}
        <SemanticObjectInspector
          entity={selectedEntity}
          onClose={() => setSelectedEntity(null)}
          onSelectEntityId={handleSelectEntityId}
          onOpenStandardsInspector={(ent) => setInspectingStandardsEntity(ent)}
        />
      </div>

      {/* International Standards Inspector Modal (W3C BOT, PROV-O, IndoorGML, JSON-LD) */}
      {inspectingStandardsEntity && (
        <StandardsInspectorModal
          entity={inspectingStandardsEntity}
          client={apiClient}
          onClose={() => setInspectingStandardsEntity(null)}
        />
      )}
    </div>
  );
}

export default function SemanticLivingDeckApp() {
  return (
    <ThemeProvider>
      <LivingDeckInner />
    </ThemeProvider>
  );
}
