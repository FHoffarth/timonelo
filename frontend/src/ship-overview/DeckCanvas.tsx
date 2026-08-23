import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { DeckSpatialViewModel, SpatialEntityViewModel } from './types';

interface DeckCanvasProps {
  deck: DeckSpatialViewModel;
  entities: SpatialEntityViewModel[];
  selectedEntityId: string | null;
  onSelectEntity: (entity: SpatialEntityViewModel) => void;
  className?: string;
}

export default function DeckCanvas({
  deck,
  entities,
  selectedEntityId,
  onSelectEntity,
  className = '',
}: DeckCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Reset zoom and pan when deck changes
  useEffect(() => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  }, [deck.deckNumber]);

  const handleZoomIn = useCallback(() => {
    setZoom((prev) => Math.min(prev * 1.35, 5.0));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((prev) => Math.max(prev / 1.35, 0.7));
  }, []);

  const handleFitToDeck = useCallback(() => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Wheel zoom (presentation viewport transform only)
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.88;
    setZoom((prev) => Math.min(Math.max(prev * zoomFactor, 0.7), 5.0));
  };

  const { viewBox } = deck;
  const showLabels = zoom >= 1.75;

  return (
    <div
      ref={containerRef}
      className={`relative w-full bg-[#111C28] rounded-3xl overflow-hidden shadow-inner border border-[#0C1B2A]/20 select-none ${className}`}
      style={{ height: '520px', minHeight: '380px' }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Background Grid Pattern */}
      <div
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(#C58A46 1px, transparent 1px)',
          backgroundSize: '24px 24px',
        }}
      />

      {/* SVG Canvas */}
      <svg
        className={`w-full h-full cursor-${isDragging ? 'grabbing' : 'grab'}`}
        viewBox={`${viewBox.minX} ${viewBox.minY} ${viewBox.width} ${viewBox.height}`}
        preserveAspectRatio="xMidYMid meet"
        role="region"
        aria-label={`Interactive map of ${deck.deckName}`}
      >
        <g
          transform={`translate(${pan.x / 500}, ${pan.y / 500}) scale(${zoom})`}
          style={{
            transformOrigin: `${viewBox.minX + viewBox.width / 2}px ${viewBox.minY + viewBox.height / 2}px`,
            transition: isDragging ? 'none' : 'transform 0.15s ease-out',
          }}
        >
          {/* Deck Silhouette Hull Outline */}
          {deck.deckBounds && (
            <rect
              x={deck.deckBounds[0] - (deck.deckBounds[2] - deck.deckBounds[0]) * 0.02}
              y={deck.deckBounds[1] - (deck.deckBounds[3] - deck.deckBounds[1]) * 0.04}
              width={(deck.deckBounds[2] - deck.deckBounds[0]) * 1.04}
              height={(deck.deckBounds[3] - deck.deckBounds[1]) * 1.08}
              rx={0.015}
              fill="#182736"
              stroke="#2A3B4D"
              strokeWidth={0.0015}
            />
          )}

          {/* Render Spatial Entities */}
          {entities.map((entity) => {
            const isSelected = entity.id === selectedEntityId;
            const isVerticalCore = entity.entityType === 'vertical_core';
            const isVenue = entity.entityType === 'venue';

            const pointsString =
              entity.polygon.length > 0
                ? entity.polygon.map((p) => `${p[0]},${p[1]}`).join(' ')
                : `${entity.bbox[0]},${entity.bbox[1]} ${entity.bbox[2]},${entity.bbox[1]} ${entity.bbox[2]},${entity.bbox[3]} ${entity.bbox[0]},${entity.bbox[3]}`;

            // Colors based on admitted semantics
            let fillColor = '#FFFFFF';
            let strokeColor = '#CBD5E1';
            let strokeWidth = zoom < 1.5 ? 0.0006 : 0.001;

            if (isVerticalCore) {
              fillColor = '#334155';
              strokeColor = '#64748B';
              strokeWidth = 0.0015;
            } else if (isVenue) {
              fillColor = '#FDE68A';
              strokeColor = '#D97706';
              strokeWidth = 0.0012;
            }

            if (isSelected) {
              fillColor = '#FDE68A';
              strokeColor = '#C58A46';
              strokeWidth = 0.003;
            }

            return (
              <g
                key={entity.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEntity(entity);
                }}
                className="cursor-pointer transition-all duration-150"
                tabIndex={0}
                role="button"
                aria-label={`${entity.name}, ${entity.categoryLabel}`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectEntity(entity);
                  }
                }}
              >
                <polygon
                  points={pointsString}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  className="hover:opacity-90 transition-opacity"
                />

                {/* Selected glow ring */}
                {isSelected && (
                  <polygon
                    points={pointsString}
                    fill="none"
                    stroke="#C58A46"
                    strokeWidth={0.005}
                    strokeDasharray="0.004 0.002"
                    opacity={0.8}
                  />
                )}

                {/* Text Label on High Zoom or Selection */}
                {(showLabels || isSelected) && !isVerticalCore && (
                  <text
                    x={entity.center[0]}
                    y={entity.center[1]}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={zoom < 2.5 ? '0.0035px' : '0.0045px'}
                    fill={isSelected ? '#78350F' : '#0F172A'}
                    fontWeight={isSelected ? 'bold' : '600'}
                    fontFamily="monospace"
                    pointerEvents="none"
                  >
                    {entity.name.replace(/^Cabin\s*/i, '')}
                  </text>
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {/* Floating Canvas Controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-10">
        <button
          onClick={handleZoomIn}
          aria-label="Zoom in"
          className="min-h-[44px] min-w-[44px] p-2.5 rounded-2xl bg-white/90 hover:bg-white text-[#0C1B2A] shadow-lg backdrop-blur-md border border-white/40 flex items-center justify-center transition-all hover:scale-105 active:scale-95 cursor-pointer"
        >
          <ZoomIn className="w-5 h-5" />
        </button>

        <button
          onClick={handleZoomOut}
          aria-label="Zoom out"
          className="min-h-[44px] min-w-[44px] p-2.5 rounded-2xl bg-white/90 hover:bg-white text-[#0C1B2A] shadow-lg backdrop-blur-md border border-white/40 flex items-center justify-center transition-all hover:scale-105 active:scale-95 cursor-pointer"
        >
          <ZoomOut className="w-5 h-5" />
        </button>

        <button
          onClick={handleFitToDeck}
          aria-label="Fit to deck"
          className="min-h-[44px] min-w-[44px] p-2.5 rounded-2xl bg-white/90 hover:bg-white text-[#0C1B2A] shadow-lg backdrop-blur-md border border-white/40 flex items-center justify-center transition-all hover:scale-105 active:scale-95 cursor-pointer"
        >
          <Maximize2 className="w-5 h-5" />
        </button>
      </div>

      {/* Legend & Density Note */}
      <div className="absolute bottom-4 left-4 hidden sm:flex items-center gap-3 bg-[#0C1B2A]/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[11px] text-slate-300 font-mono">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-white border border-slate-400" />
          <span>Stateroom</span>
        </span>
        {entities.some((e) => e.entityType === 'venue') && (
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-300 border border-amber-500" />
            <span>Public Venue</span>
          </span>
        )}
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-slate-600 border border-slate-500" />
          <span>Infrastructure</span>
        </span>
        <span className="text-slate-400">| Zoom: {Math.round(zoom * 100)}%</span>
      </div>
    </div>
  );
}
