import React from "react";
import { LayerProps } from "./types";
import { isPassengerFactAdmitted } from "../passengerAdmission";

export const SelectionLayer: React.FC<LayerProps> = ({
  selectedEntity,
  hoveredEntity,
  isNight = false,
}) => {
  if (!selectedEntity && !hoveredEntity) return null;

  const target = selectedEntity || hoveredEntity;
  if (!target) return null;

  const relations = target.relations || {};

  return (
    <g id="selection-layer" className="pointer-events-none">
      {/* 1. Target Entity Spatial Focus Aura */}
      {selectedEntity && (
        <g>
          {/* Pulsing ring indicator */}
          <circle
            cx="500"
            cy="150"
            r="120"
            fill="none"
            stroke="#C58A46"
            strokeWidth="1"
            strokeDasharray="4 6"
            opacity="0.25"
          />
        </g>
      )}

      {/* 2. Adjacency Relations Breadcrumbs HUD */}
      {selectedEntity && (
        <g id="adjacency-vectors">
          {/* Fore Neighbor */}
          {isPassengerFactAdmitted(target, "adjacent_fore") && relations.adjacent_fore && (
            <g transform="translate(680, 20)">
              <rect width="90" height="20" rx="6" fill={isNight ? "#0C1B2A" : "#FFFFFF"} stroke="#C58A46" strokeWidth="1" />
              <text x="45" y="14" fill={isNight ? "#F8FAFC" : "#0C1B2A"} fontSize="8" fontFamily="monospace" textAnchor="middle">
                ▲ Fore: {relations.adjacent_fore}
              </text>
            </g>
          )}

          {/* Aft Neighbor */}
          {isPassengerFactAdmitted(target, "adjacent_aft") && relations.adjacent_aft && (
            <g transform="translate(230, 20)">
              <rect width="90" height="20" rx="6" fill={isNight ? "#0C1B2A" : "#FFFFFF"} stroke="#C58A46" strokeWidth="1" />
              <text x="45" y="14" fill={isNight ? "#F8FAFC" : "#0C1B2A"} fontSize="8" fontFamily="monospace" textAnchor="middle">
                ▼ Aft: {relations.adjacent_aft}
              </text>
            </g>
          )}

          {/* Across Corridor */}
          {isPassengerFactAdmitted(target, "adjacent_across") && relations.adjacent_across && (
            <g transform="translate(455, 20)">
              <rect width="100" height="20" rx="6" fill={isNight ? "#0C1B2A" : "#FFFFFF"} stroke="#38BDF8" strokeWidth="1" />
              <text x="50" y="14" fill={isNight ? "#F8FAFC" : "#0C1B2A"} fontSize="8" fontFamily="monospace" textAnchor="middle">
                ↔ Across: {relations.adjacent_across}
              </text>
            </g>
          )}

          {/* Overhead Buffer Zone */}
          {isPassengerFactAdmitted(target, "adjacent_overhead") && relations.adjacent_overhead && (
            <g transform="translate(410, 268)">
              <rect width="180" height="20" rx="6" fill={isNight ? "#1E293B" : "#F1F5F9"} stroke="#94A3B8" strokeWidth="1" />
              <text x="90" y="14" fill={isNight ? "#94A3B8" : "#475569"} fontSize="8" fontFamily="monospace" textAnchor="middle">
                ↑ Overhead: {relations.adjacent_overhead}
              </text>
            </g>
          )}
        </g>
      )}
    </g>
  );
};
