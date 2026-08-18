import React from "react";
import { CloudSun } from "lucide-react";
import EpistemicBadge from "./EpistemicBadge";

interface WeatherOverviewProps {
  summary: string;
  regionName: string;
  temperatureRange: string;
  epistemicStatus?: string;
  className?: string;
}

export default function WeatherCard({
  summary,
  regionName,
  temperatureRange,
  epistemicStatus = "LIKELY",
  className = "",
}: WeatherOverviewProps) {
  return (
    <div className={`p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-4 select-none ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-display text-2xl font-bold text-[#0C1B2A]">
          Weather Overview
        </h3>
        <CloudSun className="w-5 h-5 text-[#C58A46]" />
      </div>

      <p className="text-xs text-[#5B6570] leading-relaxed">
        {summary}
      </p>

      <div className="pt-3 border-t border-[#0C1B2A]/5 space-y-1 text-xs">
        <div className="flex items-center justify-between">
          <span className="font-bold text-[#0C1B2A]">{regionName}</span>
          <EpistemicBadge status={epistemicStatus} />
        </div>
        <p className="text-[11px] text-[#5B6570]">{temperatureRange}</p>
      </div>
    </div>
  );
}
