import React from "react";
import { LayerProps } from "./types";
import { SemanticEntity } from "../types";

export const CabinLayer: React.FC<LayerProps> = ({
  level,
  selectedEntity,
  hoveredEntity,
  overlayMode,
  onSelectEntity,
  onHoverEntity,
  isNight = false,
}) => {
  const cabins = level.spaces.filter((s) => s.classification.startsWith("STATEROOM"));

  // Helper for dynamic coloring based on category or overlay mode
  const getCabinColor = (cabin: SemanticEntity) => {
    if (overlayMode === "epistemic") {
      switch (cabin.epistemic_state) {
        case "DIRECT": return isNight ? "#10B981" : "#059669";
        case "DERIVED": return isNight ? "#3B82F6" : "#2563EB";
        case "CONFLICT": return isNight ? "#EF4444" : "#DC2626";
        default: return isNight ? "#64748B" : "#94A3B8";
      }
    }

    if (overlayMode === "acoustic") {
      // Under buffet (Deck 15) or engine zone
      if (level.level_index === 14) return isNight ? "#F59E0B" : "#D97706";
      return isNight ? "#10B981" : "#16A34A";
    }

    // Default by classification
    switch (cabin.classification) {
      case "STATEROOM_SUITE":
        return isNight ? "#D97706" : "#C58A46"; // Gold
      case "STATEROOM_BALCONY":
        return isNight ? "#2563EB" : "#3B82F6"; // Ocean Blue
      case "STATEROOM_OCEAN_VIEW":
        return isNight ? "#0D9488" : "#14B8A6"; // Teal
      case "STATEROOM_INTERIOR":
      default:
        return isNight ? "#475569" : "#64748B"; // Slate
    }
  };

  return (
    <g id="cabin-layer" className="cursor-pointer">
      {cabins.map((cabin, idx) => {
        const isSelected = selectedEntity?.id === cabin.id;
        const isHovered = hoveredEntity?.id === cabin.id;

        // Position derived from sequence order and side
        const totalInSide = cabins.filter((c) => c.side === cabin.side).length || 1;
        const sideIndex = cabins.filter((c) => c.side === cabin.side).findIndex((c) => c.id === cabin.id);
        
        // Normalized longitudinal coordinate (from 160 to 860)
        const xPos = 160 + (sideIndex / Math.max(totalInSide, 1)) * 680;
        const width = Math.min(28, 680 / totalInSide - 2);

        // Lateral Y coordinate based on Port / Starboard / Center
        let yPos = 135;
        let height = 30;
        if (cabin.side === "PORT") {
          yPos = 68;
          height = cabin.has_balcony ? 38 : 32;
        } else if (cabin.side === "STARBOARD") {
          yPos = 194;
          height = cabin.has_balcony ? 38 : 32;
        } else {
          yPos = 132;
          height = 36;
        }

        const fillColor = getCabinColor(cabin);

        return (
          <g
            key={cabin.id}
            onClick={() => onSelectEntity(cabin)}
            onMouseEnter={() => onHoverEntity(cabin)}
            onMouseLeave={() => onHoverEntity(null)}
            className="transition-transform duration-150 group"
          >
            {/* 1. Balcony Railing Boundary (if applicable) */}
            {cabin.has_balcony && (
              <rect
                x={xPos}
                y={cabin.side === "PORT" ? yPos - 6 : yPos + height}
                width={width}
                height={6}
                fill={isNight ? "#0284C7" : "#38BDF8"}
                opacity="0.8"
                rx="1"
              />
            )}

            {/* 2. Cabin Main Polygon Frame */}
            <rect
              x={xPos}
              y={yPos}
              width={width}
              height={height}
              fill={fillColor}
              fillOpacity={isSelected ? 1.0 : isHovered ? 0.9 : 0.75}
              stroke={isSelected ? "#C58A46" : isHovered ? "#FFFFFF" : isNight ? "#0F172A" : "#FFFFFF"}
              strokeWidth={isSelected ? 2.5 : isHovered ? 1.5 : 1}
              rx="2"
            />

            {/* 3. Accessible (PRM) Indicator Symbol 'H' */}
            {cabin.accessible && (
              <circle
                cx={xPos + width / 2}
                cy={yPos + height / 2}
                r="5"
                fill="#10B981"
                stroke="#FFFFFF"
                strokeWidth="1"
              />
            )}

            {/* 4. Cabin Number Label */}
            {width > 14 && (
              <text
                x={xPos + width / 2}
                y={yPos + (cabin.accessible ? height / 2 + 10 : height / 2 + 3)}
                fill="#FFFFFF"
                fontSize={width < 20 ? "7" : "8.5"}
                fontWeight="bold"
                fontFamily="monospace"
                textAnchor="middle"
                pointerEvents="none"
              >
                {cabin.id.length > 5 ? cabin.id.slice(-4) : cabin.id}
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
};
