import React from "react";
import { LayerProps } from "./types";
import { SemanticEntity } from "../types";

export const VenueLayer: React.FC<LayerProps> = ({
  level,
  selectedEntity,
  hoveredEntity,
  onSelectEntity,
  onHoverEntity,
  isNight = false,
}) => {
  const venues = level.spaces.filter((s) => !s.classification.startsWith("STATEROOM") && !s.classification.startsWith("CIRCULATION"));

  // Helper for dynamic venue styling
  const getVenueStyle = (venue: SemanticEntity) => {
    switch (venue.classification) {
      case "PUBLIC_DINING":
        return { fill: isNight ? "#7C2D12" : "#FED7AA", stroke: "#EA580C", labelColor: isNight ? "#FFEDD5" : "#9A3412" };
      case "PUBLIC_LOUNGE":
        return { fill: isNight ? "#4C1D95" : "#DDD6FE", stroke: "#8B5CF6", labelColor: isNight ? "#EDE9FE" : "#5B21B6" };
      case "PUBLIC_ENTERTAINMENT":
        return { fill: isNight ? "#831843" : "#FBCFE8", stroke: "#EC4899", labelColor: isNight ? "#FDF2F8" : "#9D174D" };
      case "PUBLIC_WELLNESS":
        return { fill: isNight ? "#064E3B" : "#A7F3D0", stroke: "#10B981", labelColor: isNight ? "#ECFDF5" : "#065F46" };
      default:
        return { fill: isNight ? "#1E293B" : "#E2E8F0", stroke: "#64748B", labelColor: isNight ? "#F8FAFC" : "#334155" };
    }
  };

  return (
    <g id="venue-layer" className="cursor-pointer">
      {venues.map((venue, idx) => {
        const isSelected = selectedEntity?.id === venue.id;
        const isHovered = hoveredEntity?.id === venue.id;
        const style = getVenueStyle(venue);

        // Layout positioning based on zone (Forward, Midship, Aft)
        let xPos = 180;
        let width = 140;
        if (venue.zone === "AFT" || venue.zone.includes("AFT")) {
          xPos = 80 + idx * 110;
          width = 120;
        } else if (venue.zone === "FORWARD" || venue.zone.includes("FORWARD")) {
          xPos = 720 + (idx % 3) * 80;
          width = 110;
        } else {
          xPos = 280 + (idx % 4) * 110;
          width = 100;
        }

        const yPos = venue.side === "PORT" ? 75 : venue.side === "STARBOARD" ? 165 : 100;
        const height = venue.side === "CENTER" ? 100 : 60;

        return (
          <g
            key={venue.id}
            onClick={() => onSelectEntity(venue)}
            onMouseEnter={() => onHoverEntity(venue)}
            onMouseLeave={() => onHoverEntity(null)}
            className="group transition-transform"
          >
            {/* 1. Venue Area Boundary */}
            <rect
              x={xPos}
              y={yPos}
              width={width}
              height={height}
              fill={style.fill}
              fillOpacity={isSelected ? 1.0 : isHovered ? 0.9 : 0.8}
              stroke={isSelected ? "#C58A46" : isHovered ? "#FFFFFF" : style.stroke}
              strokeWidth={isSelected ? 3 : 1.5}
              rx="8"
            />

            {/* 2. Venue Type Pill Badge */}
            <rect
              x={xPos + 6}
              y={yPos + 6}
              width={Math.min(75, width - 12)}
              height={14}
              fill={isNight ? "#0C1B2A" : "#FFFFFF"}
              rx="4"
              opacity="0.85"
            />
            <text
              x={xPos + 10}
              y={yPos + 16}
              fill={style.labelColor}
              fontSize="7"
              fontFamily="monospace"
              fontWeight="bold"
            >
              {venue.classification.replace("PUBLIC_", "")}
            </text>

            {/* 3. Venue Title Text */}
            <text
              x={xPos + width / 2}
              y={yPos + height / 2 + 6}
              fill={style.labelColor}
              fontSize="10"
              fontWeight="bold"
              fontFamily="Newsreader, serif"
              textAnchor="middle"
              className="group-hover:scale-105 transition-transform"
            >
              {venue.label || venue.id}
            </text>
          </g>
        );
      })}
    </g>
  );
};
