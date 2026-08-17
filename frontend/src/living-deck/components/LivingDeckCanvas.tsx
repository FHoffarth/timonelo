import React, { useRef, useState, useEffect } from "react";
import { LivingDeck, LivingCabin, LivingViewMode } from "../types";
import { LIVING_DECKS, LIVING_DECKS_MAP, ProvenRoute } from "../livingEngine";
import { ZoomIn, ZoomOut, RotateCcw, Sparkles, Accessibility, Navigation2, CheckCircle2 } from "lucide-react";

interface LivingDeckCanvasProps {
  viewMode: LivingViewMode;
  activeDeck: number;
  selectedCabin: LivingCabin | null;
  hoveredCabin: LivingCabin | null;
  activeRoute: ProvenRoute | null;
  onSelectCabin: (cabin: LivingCabin) => void;
  onHoverCabin: (cabin: LivingCabin | null) => void;
  onSelectDeck: (deckNum: number) => void;
}

export default function LivingDeckCanvas({
  viewMode,
  activeDeck,
  selectedCabin,
  hoveredCabin,
  activeRoute,
  onSelectCabin,
  onHoverCabin,
  onSelectDeck,
}: LivingDeckCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const currentDeckObj = LIVING_DECKS_MAP.get(activeDeck) || LIVING_DECKS[0];

  // Auto-focus on selected cabin
  useEffect(() => {
    if (selectedCabin && selectedCabin.deck === activeDeck) {
      const [rx, ry, rw, rh] = selectedCabin.rel_bbox;
      const targetY = -(ry - 300) * zoom;
      setPan({ x: 0, y: Math.max(-400, Math.min(400, targetY)) });
    }
  }, [selectedCabin, activeDeck]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    setZoom((prev) => Math.min(3.5, Math.max(0.6, prev * zoomFactor)));
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      className={`relative w-full h-full bg-slate-950 overflow-hidden select-none cursor-grab ${
        isDragging ? "cursor-grabbing" : ""
      }`}
    >
      {/* Floating Canvas Controls */}
      <div className="absolute right-6 bottom-20 z-20 flex flex-col gap-1.5 p-1.5 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl pointer-events-auto">
        <button
          onClick={() => setZoom((prev) => Math.min(3.5, prev * 1.25))}
          className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((prev) => Math.max(0.6, prev * 0.8))}
          className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => {
            setZoom(1.0);
            setPan({ x: 0, y: 0 });
          }}
          className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* MODE A: SINGLE DECK LIVING VIEW (Google Maps Deep Dive)           */}
      {/* ------------------------------------------------------------------ */}
      {viewMode === "single_deck" && (
        <div
          className="absolute inset-0 flex items-center justify-center transition-transform duration-75 ease-out pointer-events-none"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          }}
        >
          <div className="relative w-[340px] md:w-[420px] max-h-[88vh] aspect-[1/3.2] bg-slate-900/40 rounded-3xl border border-white/10 shadow-2xl p-2 pointer-events-auto flex items-center justify-center">
            {/* Official MSC Deck Plan High-Res Vector Slice */}
            <img
              src={`/decks/deck_${activeDeck}.png`}
              alt={`MSC Bellissima Official Deck Plan - Deck ${activeDeck}`}
              className="w-full h-full object-contain filter drop-shadow-2xl rounded-2xl"
              draggable={false}
            />

            {/* Interactive SVG Living Layer Overlay */}
            <svg
              className="absolute inset-2 w-[calc(100%-16px)] h-[calc(100%-16px)] pointer-events-auto"
              viewBox={`0 0 ${currentDeckObj.width_pt} ${currentDeckObj.height_pt}`}
              preserveAspectRatio="xMidYMid meet"
            >
              {/* Interactive Staterooms Overlay */}
              {currentDeckObj.cabins.map((c) => {
                const [rx, ry, rw, rh] = c.rel_bbox;
                const isSelected = selectedCabin?.cabin_number === c.cabin_number;
                const isHovered = hoveredCabin?.cabin_number === c.cabin_number;

                // Subtle category color border
                let strokeColor = "rgba(56, 189, 248, 0.4)"; // Sky
                if (c.category.includes("Balcony")) strokeColor = "rgba(16, 185, 129, 0.5)"; // Emerald
                if (c.category.includes("Suite") || c.category.includes("Yacht")) strokeColor = "rgba(245, 158, 11, 0.6)"; // Gold

                if (isSelected) strokeColor = "#f43f5e"; // Pulsing Rose
                else if (isHovered) strokeColor = "#ffffff";

                return (
                  <g
                    key={c.cabin_number}
                    id={`cabin-${c.cabin_number}`}
                    className="cursor-pointer group"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectCabin(c);
                    }}
                    onMouseEnter={() => onHoverCabin(c)}
                    onMouseLeave={() => onHoverCabin(null)}
                  >
                    {/* Clickable Hover / Focus Area */}
                    <rect
                      x={rx - 1}
                      y={ry - 1}
                      width={rw + 2}
                      height={rh + 2}
                      fill={isSelected ? "rgba(244, 63, 94, 0.25)" : (isHovered ? "rgba(56, 189, 248, 0.2)" : "transparent")}
                      stroke={strokeColor}
                      strokeWidth={isSelected ? 2.0 : (isHovered ? 1.5 : 0.8)}
                      rx={1}
                      className={`transition-all duration-150 ${isSelected ? "animate-pulse" : ""}`}
                    />

                    {/* PRM Accessible Marker */}
                    {c.accessible && (
                      <circle
                        cx={rx + rw / 2}
                        cy={ry - 2}
                        r={2.5}
                        fill="#38bdf8"
                        stroke="#ffffff"
                        strokeWidth={0.5}
                      />
                    )}
                  </g>
                );
              })}

              {/* Animated Proven Routing Line */}
              {activeRoute && activeRoute.fromDeck === activeDeck && (
                <g className="animate-in fade-in duration-300">
                  <path
                    d={`M ${currentDeckObj.width_pt / 2} ${currentDeckObj.height_pt * 0.48} L ${currentDeckObj.width_pt / 2} ${currentDeckObj.height_pt * 0.35}`}
                    fill="none"
                    stroke="#f43f5e"
                    strokeWidth={3}
                    strokeDasharray="4 2"
                    strokeLinecap="round"
                    className="animate-pulse"
                  />
                  <circle
                    cx={currentDeckObj.width_pt / 2}
                    cy={currentDeckObj.height_pt * 0.48}
                    r={4}
                    fill="#10b981"
                    stroke="#ffffff"
                    strokeWidth={1}
                  />
                  <circle
                    cx={currentDeckObj.width_pt / 2}
                    cy={currentDeckObj.height_pt * 0.35}
                    r={4}
                    fill="#f43f5e"
                    stroke="#ffffff"
                    strokeWidth={1}
                  />
                </g>
              )}
            </svg>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* MODE B: EXPLODED MULTI-DECK ARCHITECTURAL STACK                  */}
      {/* ------------------------------------------------------------------ */}
      {viewMode === "exploded_stack" && (
        <div
          className="absolute inset-0 flex items-center justify-center transition-transform duration-100 ease-out pointer-events-none"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          }}
        >
          <div className="relative flex items-center gap-6 px-12 pointer-events-auto overflow-x-auto no-scrollbar">
            {LIVING_DECKS.map((deck) => {
              const isCurrent = deck.deck_number === activeDeck;

              return (
                <div
                  key={deck.deck_number}
                  onClick={() => onSelectDeck(deck.deck_number)}
                  className={`relative flex flex-col items-center cursor-pointer transition-all duration-300 transform ${
                    isCurrent
                      ? "scale-105 opacity-100 -translate-y-4"
                      : "opacity-40 hover:opacity-80 scale-95"
                  }`}
                >
                  <div className="mb-2 px-3 py-1 bg-slate-900/90 border border-white/10 rounded-xl text-center shadow-lg">
                    <span className="text-xs font-mono font-bold text-sky-400">
                      Deck {deck.deck_number}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate max-w-[120px]">
                      {deck.deck_name}
                    </span>
                  </div>

                  <div className="relative w-44 aspect-[1/3.2] bg-slate-900/60 rounded-2xl border border-white/10 p-1.5 shadow-2xl">
                    <img
                      src={`/decks/deck_${deck.deck_number}.png`}
                      alt={`Deck ${deck.deck_number}`}
                      className="w-full h-full object-contain rounded-xl"
                      draggable={false}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
