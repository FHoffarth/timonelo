import React, { useState, useRef, useEffect, useCallback } from "react";
import { DeckRendererProps, ViewportState, RenderOverlayMode } from "./types";
import { DeckLayer } from "./DeckLayer";
import { CabinLayer } from "./CabinLayer";
import { VenueLayer } from "./VenueLayer";
import { LiftLayer } from "./LiftLayer";
import { SelectionLayer } from "./SelectionLayer";
import { LegendLayer } from "./LegendLayer";
import { useTheme } from "../themeContext";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  ChevronUp,
  ChevronDown,
  Layers,
  Sparkles,
} from "lucide-react";

export const DeckRenderer: React.FC<DeckRendererProps> = ({
  level,
  allLevels = [],
  vesselGraph,
  selectedEntity,
  hoveredEntity,
  overlayMode: initialOverlayMode = "none",
  layersConfig = {},
  onSelectEntity,
  onHoverEntity,
  onSelectLevel,
  onNavigateAdjacent,
  className = "",
}) => {
  const { theme } = useTheme();
  const isNight = theme === "night";

  const [overlayMode, setOverlayMode] = useState<RenderOverlayMode>(initialOverlayMode);

  // Viewport camera transform state
  const [viewport, setViewport] = useState<ViewportState>({ x: 0, y: 0, zoom: 1.0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement>(null);

  // Reset viewport when deck changes
  useEffect(() => {
    setViewport({ x: 0, y: 0, zoom: 1.0 });
  }, [level.level_index]);

  // Handle Zoom In / Out
  const handleZoom = useCallback((delta: number) => {
    setViewport((prev) => ({
      ...prev,
      zoom: Math.min(3.5, Math.max(0.6, prev.zoom + delta)),
    }));
  }, []);

  const handleResetZoom = useCallback(() => {
    setViewport({ x: 0, y: 0, zoom: 1.0 });
  }, []);

  // Handle Mouse Wheel Zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const zoomDelta = e.deltaY < 0 ? 0.15 : -0.15;
    handleZoom(zoomDelta);
  }, [handleZoom]);

  // Handle Pan Start
  const handleMouseDown = (e: React.MouseEvent) => {
    // Only pan on background drag
    if ((e.target as HTMLElement).tagName === "svg" || (e.target as HTMLElement).id === "deck-layer") {
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewport.x, y: e.clientY - viewport.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setViewport((prev) => ({
        ...prev,
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      }));
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  // Keyboard navigation for vertical traversal and adjacent cabins
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "PageUp" || (e.altKey && e.key === "ArrowUp")) {
        // Climb deck up
        const nextLevel = level.level_index < 19 ? level.level_index + (level.level_index === 16 ? 2 : 1) : 19;
        onSelectLevel(nextLevel);
      } else if (e.key === "PageDown" || (e.altKey && e.key === "ArrowDown")) {
        // Descend deck down
        const prevLevel = level.level_index > 4 ? level.level_index - (level.level_index === 18 ? 2 : 1) : 4;
        onSelectLevel(prevLevel);
      } else if (selectedEntity && onNavigateAdjacent) {
        if (e.key === "ArrowLeft") onNavigateAdjacent("aft");
        if (e.key === "ArrowRight") onNavigateAdjacent("fore");
        if (e.key === "ArrowUp") onNavigateAdjacent("across");
        if (e.key === "ArrowDown") onNavigateAdjacent("across");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [level.level_index, selectedEntity, onSelectLevel, onNavigateAdjacent]);

  const layerProps = {
    level,
    allLevels,
    selectedEntity,
    hoveredEntity,
    overlayMode,
    onSelectEntity,
    onHoverEntity,
    isNight,
  };

  return (
    <div
      ref={containerRef}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      className={`relative w-full h-full overflow-hidden flex items-center justify-center select-none ${
        isNight ? "bg-slate-950" : "bg-[#F7F4EE]"
      } ${className}`}
    >
      {/* 1. Interactive SVG Canvas Viewport */}
      <svg
        viewBox="0 0 1020 300"
        className="w-full h-full cursor-grab active:cursor-grabbing transition-transform duration-75"
        style={{
          transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.zoom})`,
          transformOrigin: "center center",
        }}
      >
        {/* Layer 1: Deck Hull & Grid */}
        <DeckLayer {...layerProps} />

        {/* Layer 2: Cabins & Staterooms */}
        <CabinLayer {...layerProps} />

        {/* Layer 3: Public Venues & Landmarks */}
        <VenueLayer {...layerProps} />

        {/* Layer 4: Vertical Transit Lift Cores */}
        <LiftLayer {...layerProps} onSelectLevel={onSelectLevel} />

        {/* Layer 5: Dynamic Selection & Adjacency Vectors */}
        <SelectionLayer {...layerProps} />
      </svg>

      {/* 2. Floating Viewport Controls (Zoom, Reset, Vertical Climbers) */}
      <div className="absolute top-4 right-6 z-20 flex items-center gap-1.5 p-1.5 rounded-2xl bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-white/10 shadow-lg backdrop-blur-md text-xs">
        <button
          onClick={() => handleZoom(0.25)}
          title="Zoom In"
          className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => handleZoom(-0.25)}
          title="Zoom Out"
          className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleResetZoom}
          title="Fit Deck to Viewport"
          className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        <div className="h-4 w-px bg-slate-200 dark:bg-white/10 mx-0.5" />

        {/* Deck Climbing Shortcuts */}
        <button
          onClick={() => onSelectLevel(level.level_index < 19 ? level.level_index + (level.level_index === 16 ? 2 : 1) : 19)}
          title="Climb Deck Up"
          className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
        >
          <ChevronUp className="w-4 h-4" />
        </button>
        <button
          onClick={() => onSelectLevel(level.level_index > 4 ? level.level_index - (level.level_index === 18 ? 2 : 1) : 4)}
          title="Descend Deck Down"
          className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* 3. Floating Interactive Legend Layer */}
      <LegendLayer
        overlayMode={overlayMode}
        onSelectOverlayMode={setOverlayMode}
        isNight={isNight}
      />
    </div>
  );
};

export default DeckRenderer;
