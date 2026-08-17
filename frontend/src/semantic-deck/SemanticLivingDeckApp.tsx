import React, { useState, useEffect, useMemo } from "react";
import { TimoneloSpatialApiClient } from "./apiClient";
import { SemanticLevel, SemanticEntity } from "./types";
import DeckNavigationStack from "./components/DeckNavigationStack";
import SemanticDeckGrid from "./components/SemanticDeckGrid";
import SemanticObjectInspector from "./components/SemanticObjectInspector";
import EpistemicLegendBar from "./components/EpistemicLegendBar";
import SemanticSearchBar from "./components/SemanticSearchBar";
import StandardsInspectorModal from "./components/StandardsInspectorModal";
import {
  Compass,
  Sparkles,
  ShieldCheck,
  Code2,
  Layers,
  History,
  AlertTriangle,
  Workflow,
} from "lucide-react";

export default function SemanticLivingDeckApp() {
  const [selectedVesselId, setSelectedVesselId] = useState<string>("msc-bellissima");
  const apiClient = useMemo(() => new TimoneloSpatialApiClient(selectedVesselId), [selectedVesselId]);

  const vesselGraph = apiClient.getVesselGraph();
  const levels = vesselGraph.levels || [];

  // Default active level: Level 14 on Bellissima or top level
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

  // Focus Space 14122 by default when loaded on MSC Bellissima
  useEffect(() => {
    if (selectedVesselId === "msc-bellissima") {
      const c14122 = apiClient.getEntity("14122");
      if (c14122) {
        setSelectedEntity(c14122);
        setActiveLevelIndex(c14122.level);
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

  const handleSelectEntity = (entity: SemanticEntity) => {
    setSelectedEntity(entity);
    setActiveLevelIndex(entity.level);
  };

  const handleSelectEntityId = (id: string) => {
    const ent = apiClient.getEntity(id);
    if (ent) {
      handleSelectEntity(ent);
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
                W3C BOT & PROV-O Ready
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {vesselGraph.vessel_name} • Canonical Knowledge Graph Platform
            </p>
          </div>
        </div>

        {/* Global Search across all spatial entities */}
        <SemanticSearchBar
          onSearch={(q) => apiClient.searchEntities(q)}
          onSelectEntity={handleSelectEntity}
        />

        {/* Top Platform View Switcher */}
        <div className="flex items-center gap-2">
          <div className="p-1 bg-slate-950/80 rounded-2xl border border-white/5 flex items-center gap-1 text-xs">
            <button
              onClick={() => setActivePlatformView("LIVING_DECK")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "LIVING_DECK"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              Living Deck
            </button>
            <button
              onClick={() => setActivePlatformView("TOPOLOGY_INSPECTOR")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "TOPOLOGY_INSPECTOR"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <Workflow className="w-3.5 h-3.5" />
              Topology Inspector
            </button>
            <button
              onClick={() => setActivePlatformView("PROVENANCE_VIEWER")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activePlatformView === "PROVENANCE_VIEWER"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <History className="w-3.5 h-3.5" />
              PROV-O Viewer
            </button>
          </div>
        </div>
      </header>

      {/* Epistemic Legend Bar */}
      <EpistemicLegendBar />

      {/* Main Scientific Spatial Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left: Deck & Level Navigation Stack */}
        <DeckNavigationStack
          currentVessel={vesselGraph}
          activeDeckLevel={activeLevelIndex}
          onSelectVessel={handleSelectVessel}
          onSelectDeck={handleSelectLevel}
        />

        {/* Center: Main View */}
        {activePlatformView === "LIVING_DECK" && activeLevel && (
          <SemanticDeckGrid
            level={activeLevel}
            selectedEntity={selectedEntity}
            hoveredEntity={hoveredEntity}
            onSelectEntity={handleSelectEntity}
            onHoverEntity={setHoveredEntity}
          />
        )}

        {activePlatformView === "TOPOLOGY_INSPECTOR" && (
          <div className="flex-1 p-8 bg-slate-950 overflow-y-auto no-scrollbar flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-sky-500/10 border border-sky-400/20 flex items-center justify-center text-sky-400">
              <Workflow className="w-8 h-8" />
            </div>
            <h2 className="text-lg font-bold text-white">Canonical Topology Inspector (W3C BOT)</h2>
            <p className="text-xs text-slate-400 max-w-md text-center leading-relaxed">
              Exposing topological graph edges, vertical elevator transit shafts, and adjacent boundary spaces generated from the Truth Engine without geometric assumptions.
            </p>
            <div className="p-4 bg-slate-900/60 rounded-2xl border border-white/10 text-xs font-mono text-slate-300 space-y-1">
              <div>bot:Storey Count: {vesselGraph.levels.length} Levels</div>
              <div>bot:Space Count: {vesselGraph.epistemic_summary.total_entities} Verified Entities</div>
              <div>Mean Confidence: {(vesselGraph.epistemic_summary.mean_confidence * 100).toFixed(0)}%</div>
            </div>
          </div>
        )}

        {activePlatformView === "PROVENANCE_VIEWER" && (
          <div className="flex-1 p-8 bg-slate-950 overflow-y-auto no-scrollbar flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <History className="w-8 h-8" />
            </div>
            <h2 className="text-lg font-bold text-white">W3C PROV-O Lineage Viewer</h2>
            <p className="text-xs text-slate-400 max-w-md text-center leading-relaxed">
              Every spatial statement is formally linked to its originating artifact with SHA-256 integrity pinning, extraction activity, and reviewer attribution.
            </p>
            <div className="p-4 bg-slate-900/60 rounded-2xl border border-white/10 text-xs font-mono text-emerald-300 space-y-1">
              <div>Direct Provenance Count: {vesselGraph.epistemic_summary.direct_evidence_count}</div>
              <div>Derived Formula Count: {vesselGraph.epistemic_summary.derived_count}</div>
              <div>Uncertainty Count: {vesselGraph.epistemic_summary.unknown_count}</div>
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

      {/* International Standards Inspector Modal */}
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
