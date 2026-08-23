import { useState, useRef, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { SpatialEntityViewModel, DeckSpatialViewModel } from './types';

interface DeckCanvasProps {
  deck: DeckSpatialViewModel;
  entities: SpatialEntityViewModel[];
  selectedEntityId: string | null;
  onSelectEntity: (entity: SpatialEntityViewModel | null) => void;
  className?: string;
}

export default function DeckCanvas({
  deck,
  entities,
  selectedEntityId,
  onSelectEntity,
  className = '',
}: DeckCanvasProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement | null>(null);

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev * 1.3, 5));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev / 1.3, 0.6));
  };

  const handleFitToDeck = useCallback(() => {
    setZoom(1);
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

  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      setIsDragging(true);
      setDragStart({ x: touch.clientX - pan.x, y: touch.clientY - pan.y });
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || e.touches.length !== 1) return;
    const touch = e.touches[0];
    setPan({
      x: touch.clientX - dragStart.x,
      y: touch.clientY - dragStart.y,
    });
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  // Convert polygon coordinates to SVG points string
  const getPointsString = (polygon: Array<[number, number]>) => {
    return polygon.map(([x, y]) => `${x},${y}`).join(' ');
  };

  const { minX, minY, width, height } = deck.viewBox;

  return (
    <div className={`relative bg-slate-900 rounded-3xl overflow-hidden border border-[#0C1B2A]/20 shadow-inner flex flex-col items-center justify-center min-h-[380px] sm:min-h-[460px] select-none touch-none ${className}`}>
      {/* Floating Canvas Controls */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-1.5 bg-white/90 backdrop-blur-md p-1.5 rounded-2xl shadow-md border border-slate-200/50">
        <button
          onClick={handleZoomIn}
          aria-label="Zoom in"
          title="Zoom in"
          className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl hover:bg-slate-100 text-slate-700 transition-colors cursor-pointer"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          aria-label="Zoom out"
          title="Zoom out"
          className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl hover:bg-slate-100 text-slate-700 transition-colors cursor-pointer"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleFitToDeck}
          aria-label="Fit to deck"
          title="Fit to deck"
          className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl hover:bg-slate-100 text-slate-700 transition-colors cursor-pointer"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Canvas Viewport Badge */}
      <div className="absolute top-4 left-4 z-10 bg-slate-800/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/50 text-[11px] font-mono text-slate-300 pointer-events-none">
        <span>{deck.deckName}</span>
        <span className="text-slate-500 mx-1.5">•</span>
        <span className="text-[#C58A46]">{entities.length} mapped spaces</span>
      </div>

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        viewBox={`${minX} ${minY} ${width} ${height}`}
        className="w-full h-full max-h-[480px] sm:max-h-[560px] cursor-grab active:cursor-grabbing transition-transform duration-75"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: 'center center',
        }}
      >
        <g id="deck-geometry-layer">
          {/* Deck Silhouette Hull Background */}
          <rect
            x={minX}
            y={minY}
            width={width}
            height={height}
            fill="#0F1E2E"
            rx={0.01}
            stroke="#1E3246"
            strokeWidth={0.001}
          />

          {/* Admitted Mapped Objects */}
          {entities.map((entity) => {
            const isSelected = entity.id === selectedEntityId;
            const isCabin = entity.entityType === 'cabin';
            const isVerticalCore = entity.entityType === 'vertical_core';

            let fillColor = isCabin ? '#22384D' : '#C58A46';
            let strokeColor = isCabin ? '#385570' : '#E8B67C';
            let strokeWidth = 0.0003;

            if (isSelected) {
              fillColor = '#C58A46';
              strokeColor = '#FFFFFF';
              strokeWidth = 0.0015;
            } else if (isVerticalCore) {
              fillColor = '#8A6D3B';
              strokeColor = '#C58A46';
            }

            return (
              <g
                key={entity.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEntity(isSelected ? null : entity);
                }}
                className="cursor-pointer transition-colors group"
                role="button"
                tabIndex={0}
                aria-label={entity.name}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectEntity(isSelected ? null : entity);
                  }
                }}
              >
                {entity.polygon.length > 0 ? (
                  <polygon
                    points={getPointsString(entity.polygon)}
                    fill={fillColor}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    className="hover:opacity-90 transition-opacity"
                  />
                ) : (
                  <rect
                    x={entity.bbox[0]}
                    y={entity.bbox[1]}
                    width={entity.bbox[2] - entity.bbox[0]}
                    height={entity.bbox[3] - entity.bbox[1]}
                    fill={fillColor}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    className="hover:opacity-90 transition-opacity"
                  />
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {/* Canvas Usage Hint for Mobile */}
      <div className="absolute bottom-3 left-0 right-0 text-center pointer-events-none px-4">
        <span className="text-[10px] text-slate-400/80 font-mono bg-slate-900/60 px-3 py-1 rounded-full border border-slate-700/40">
          Drag to pan • Pinch / buttons to zoom • Tap cabin to inspect
        </span>
      </div>
    </div>
  );
}
