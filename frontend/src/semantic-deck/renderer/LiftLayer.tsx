import React from "react";
import { LayerProps } from "./types";

interface LiftCoreDefinition {
  id: string;
  name: string;
  x: number;
  y: number;
  shaftHeight: number;
  isPanoramic?: boolean;
}

export const LiftLayer: React.FC<LayerProps & { onSelectLevel?: (lvl: number) => void }> = ({
  level,
  allLevels = [],
  selectedEntity,
  onSelectLevel,
  isNight = false,
}) => {
  // Verified vertical cores geometry
  const liftCores: LiftCoreDefinition[] = [
    { id: "LIFT_CORE_A_FWD", name: "Lift Core A (Forward)", x: 740, y: 130, shaftHeight: 40 },
    { id: "LIFT_CORE_B_MID", name: "Lift Core B (Midship)", x: 490, y: 130, shaftHeight: 40 },
    { id: "LIFT_CORE_C_AFT", name: "Lift Core C (Aft)", x: 230, y: 130, shaftHeight: 40 },
    { id: "LIFT_CORE_PANORAMIC", name: "Panoramic Atrium Lifts", x: 440, y: 52, shaftHeight: 28, isPanoramic: true },
  ];

  const connectedLiftId = selectedEntity?.relations?.connected_vertical_core;

  return (
    <g id="lift-layer">
      {liftCores.map((lift) => {
        const isTargeted = connectedLiftId === lift.id || connectedLiftId?.includes(lift.id.slice(10));

        return (
          <g key={lift.id} className="transition-all duration-200">
            {/* 1. Lift Shaft Ambient Ring / Highlight Indicator */}
            {isTargeted && (
              <circle
                cx={lift.x + 15}
                cy={lift.y + 15}
                r="30"
                fill="#C58A46"
                fillOpacity="0.2"
                stroke="#C58A46"
                strokeWidth="1.5"
                strokeDasharray="4 2"
                className="animate-spin"
              />
            )}

            {/* 2. Lift Core Main Box */}
            <rect
              x={lift.x}
              y={lift.y}
              width={30}
              height={lift.shaftHeight}
              fill={lift.isPanoramic ? (isNight ? "#0284C7" : "#38BDF8") : (isNight ? "#1E293B" : "#E2E8F0")}
              stroke={isTargeted ? "#C58A46" : isNight ? "#38BDF8" : "#0284C7"}
              strokeWidth={isTargeted ? 2.5 : 1.5}
              rx="6"
              className="cursor-pointer hover:opacity-90"
            />

            {/* 3. Elevator Graphic Icon (Up/Down arrows) */}
            <path
              d={`M ${lift.x + 10} ${lift.y + 12} L ${lift.x + 15} ${lift.y + 6} L ${lift.x + 20} ${lift.y + 12} Z`}
              fill={isNight ? "#FFFFFF" : "#0C1B2A"}
            />
            <path
              d={`M ${lift.x + 10} ${lift.y + lift.shaftHeight - 12} L ${lift.x + 15} ${lift.y + lift.shaftHeight - 6} L ${lift.x + 20} ${lift.y + lift.shaftHeight - 12} Z`}
              fill={isNight ? "#FFFFFF" : "#0C1B2A"}
            />

            {/* 4. Core Label */}
            <text
              x={lift.x + 15}
              y={lift.y + lift.shaftHeight + 12}
              fill={isTargeted ? "#C58A46" : isNight ? "#94A3B8" : "#475569"}
              fontSize="7.5"
              fontFamily="monospace"
              fontWeight="bold"
              textAnchor="middle"
            >
              {lift.isPanoramic ? "PANORAMIC LIFT" : "LIFT"}
            </text>

            {/* 5. Interactive Vertical Traversal Hotspots (Climb Up / Descend Down) */}
            {isTargeted && onSelectLevel && (
              <g className="cursor-pointer">
                {level.level_index < 19 && (
                  <g
                    onClick={() => onSelectLevel(level.level_index + (level.level_index === 16 ? 2 : 1))}
                    className="group"
                  >
                    <rect
                      x={lift.x + 36}
                      y={lift.y - 4}
                      width={52}
                      height={18}
                      fill="#0C1B2A"
                      rx="4"
                      stroke="#C58A46"
                      strokeWidth="1"
                    />
                    <text x={lift.x + 62} y={lift.y + 8} fill="#FFFFFF" fontSize="7.5" fontFamily="monospace" textAnchor="middle">
                      ▲ Climb D{level.level_index + (level.level_index === 16 ? 2 : 1)}
                    </text>
                  </g>
                )}

                {level.level_index > 4 && (
                  <g
                    onClick={() => onSelectLevel(level.level_index - (level.level_index === 18 ? 2 : 1))}
                    className="group"
                  >
                    <rect
                      x={lift.x + 36}
                      y={lift.y + 20}
                      width={52}
                      height={18}
                      fill="#0C1B2A"
                      rx="4"
                      stroke="#C58A46"
                      strokeWidth="1"
                    />
                    <text x={lift.x + 62} y={lift.y + 32} fill="#FFFFFF" fontSize="7.5" fontFamily="monospace" textAnchor="middle">
                      ▼ Descend D{level.level_index - (level.level_index === 18 ? 2 : 1)}
                    </text>
                  </g>
                )}
              </g>
            )}
          </g>
        );
      })}
    </g>
  );
};
