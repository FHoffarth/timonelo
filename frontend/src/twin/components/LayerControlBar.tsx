import React from "react";
import { ActiveLayers } from "../types";
import {
  Bed,
  Utensils,
  Wine,
  Waves,
  Accessibility,
  GitFork,
  Flame,
  Bath,
} from "lucide-react";

interface LayerControlBarProps {
  layers: ActiveLayers;
  onToggleLayer: (key: keyof ActiveLayers) => void;
}

export default function LayerControlBar({ layers, onToggleLayer }: LayerControlBarProps) {
  const layerButtons: Array<{
    key: keyof ActiveLayers;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }> = [
    { key: "cabins", label: "Cabins", icon: Bed },
    { key: "restaurants", label: "Dining", icon: Utensils },
    { key: "bars", label: "Bars", icon: Wine },
    { key: "pools", label: "Lido / Pools", icon: Waves },
    { key: "toilets", label: "Toilets", icon: Bath },
    { key: "accessible", label: "PRM (H)", icon: Accessibility },
    { key: "routingGraph", label: "Graph", icon: GitFork },
  ];

  return (
    <div className="absolute top-6 right-6 z-20 flex items-center gap-1.5 p-1.5 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl pointer-events-auto">
      {layerButtons.map(({ key, label, icon: Icon }) => {
        const isActive = layers[key];
        return (
          <button
            key={key}
            onClick={() => onToggleLayer(key)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
              isActive
                ? "bg-white/10 text-white border border-white/20 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent"
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${isActive ? "text-sky-400" : "text-slate-400"}`} />
            {label}
          </button>
        );
      })}
    </div>
  );
}
