import React from "react";
import { LayerProps } from "./types";

export const DeckLayer: React.FC<LayerProps> = ({ level, isNight = false }) => {
  const isHighDeck = level.level_index >= 15;
  const isBowTapered = level.level_index >= 12;

  // Generate dynamic hull path based on deck level geometry
  const bowX = isBowTapered ? 960 : 980;
  const sternX = 40;
  const midTopY = isHighDeck ? 55 : 40;
  const midBotY = isHighDeck ? 245 : 260;

  return (
    <g id="deck-layer" className="select-none pointer-events-none">
      {/* 1. Vessel Outer Waterline & Shadow Backdrop */}
      <path
        d={`M ${sternX} 150 
            C ${sternX} ${midTopY + 20}, ${sternX + 120} ${midTopY}, 450 ${midTopY} 
            L 800 ${midTopY} 
            C 890 ${midTopY}, ${bowX - 40} 110, ${bowX} 150 
            C ${bowX - 40} 190, 890 ${midBotY}, 800 ${midBotY} 
            L 450 ${midBotY} 
            C ${sternX + 120} ${midBotY}, ${sternX} ${midBotY - 20}, ${sternX} 150 Z`}
        fill={isNight ? "#090E17" : "#F4EFE6"}
        stroke={isNight ? "#1E293B" : "#D8CEBE"}
        strokeWidth="3"
        strokeLinejoin="round"
      />

      {/* 2. Longitudinal Centerline & Grid Coordinates */}
      <line
        x1={sternX + 20}
        y1="150"
        x2={bowX - 20}
        y2="150"
        stroke={isNight ? "#1E293B" : "#E2D9CC"}
        strokeWidth="1.5"
        strokeDasharray="6 4"
      />

      {/* Frame markers across ship length (every 100 units ~ 30 meters) */}
      {[150, 300, 450, 600, 750, 900].map((x) => (
        <g key={x} opacity={isNight ? 0.3 : 0.45}>
          <line
            x1={x}
            y1={midTopY + 5}
            x2={x}
            y2={midBotY - 5}
            stroke={isNight ? "#334155" : "#C4B5A2"}
            strokeWidth="0.75"
            strokeDasharray="2 4"
          />
          <text
            x={x}
            y={midBotY + 18}
            fill={isNight ? "#64748B" : "#8C7E6C"}
            fontSize="8"
            fontFamily="monospace"
            textAnchor="middle"
          >
            FR-{Math.round(x / 4)}
          </text>
        </g>
      ))}

      {/* 3. Forward & Aft Structural Direction Markers */}
      <g opacity={isNight ? 0.6 : 0.8}>
        {/* Bow (Forward) */}
        <text
          x={bowX - 25}
          y="153"
          fill={isNight ? "#38BDF8" : "#0284C7"}
          fontSize="9"
          fontFamily="sans-serif"
          fontWeight="bold"
          textAnchor="middle"
        >
          BOW ▶
        </text>
        {/* Stern (Aft) */}
        <text
          x={sternX + 35}
          y="153"
          fill={isNight ? "#94A3B8" : "#78716C"}
          fontSize="9"
          fontFamily="sans-serif"
          fontWeight="bold"
          textAnchor="middle"
        >
          ◀ AFT
        </text>
      </g>

      {/* 4. Port & Starboard Hemisphere Labels */}
      <text
        x="500"
        y={midTopY - 12}
        fill={isNight ? "#E06C75" : "#B91C1C"}
        fontSize="9"
        fontFamily="sans-serif"
        fontWeight="600"
        textAnchor="middle"
        opacity="0.7"
      >
        PORT SIDE (🔴 RED LIGHT / LEFT)
      </text>
      <text
        x="500"
        y={midBotY + 34}
        fill={isNight ? "#98C379" : "#15803D"}
        fontSize="9"
        fontFamily="sans-serif"
        fontWeight="600"
        textAnchor="middle"
        opacity="0.7"
      >
        STARBOARD SIDE (🟢 GREEN LIGHT / RIGHT)
      </text>
    </g>
  );
};
