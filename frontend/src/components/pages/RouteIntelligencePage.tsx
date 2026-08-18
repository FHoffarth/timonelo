import React from "react";
import EpistemicBadge from "../ui/EpistemicBadge";
import { CANONICAL_ROUTES } from "../../data/canonicalPlatformData";
import { Compass, CloudSun, Calendar, Navigation, MapPin } from "lucide-react";

interface RouteIntelligencePageProps {
  routeSlug?: string;
  onSelectPort?: (portSlug: string) => void;
}

export default function RouteIntelligencePage({
  routeSlug = "7-night-adriatic-aegean",
  onSelectPort,
}: RouteIntelligencePageProps) {
  const route = CANONICAL_ROUTES[routeSlug] || CANONICAL_ROUTES["7-night-adriatic-aegean"];

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">ITINERARY INTELLIGENCE MAPPING</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          {route.title}
        </h1>

        <div className="flex items-center gap-3 text-xs sm:text-sm text-[#5B6570] font-sans">
          <span>Vessel: <strong className="text-[#0C1B2A]">{route.vesselName}</strong></span>
          <span>•</span>
          <span>Seasonal Profile: {route.seasonalProfile}</span>
        </div>
      </div>

      {/* 2. Maritime Trajectory Map Container */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-12">
        <div className="relative w-full h-[360px] sm:h-[440px] rounded-3xl bg-[#E6F0FA]/80 border border-[#0C1B2A]/10 overflow-hidden shadow-md flex items-center justify-center p-8">
          {/* Schematic SVG Map Graphic */}
          <svg className="w-full h-full" viewBox="0 0 800 350" fill="none">
            {/* Trajectory dotted navigation path */}
            <path
              d="M 160 80 L 260 160 L 320 280 L 480 230 L 410 130 L 260 80 Z"
              stroke="#C58A46"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              className="animate-pulse"
            />
            {/* Waypoints */}
            <g className="cursor-pointer">
              <circle cx="160" cy="80" r="6" fill="#0C1B2A" />
              <text x="175" y="85" fill="#0C1B2A" fontSize="12" fontWeight="bold" fontFamily="Newsreader, serif">
                Venice (Start/End)
              </text>
            </g>
            <g className="cursor-pointer">
              <circle cx="260" cy="160" r="5" fill="#0C1B2A" />
              <text x="275" y="165" fill="#0C1B2A" fontSize="11" fontWeight="600" fontFamily="Newsreader, serif">
                Bari
              </text>
            </g>
            <g className="cursor-pointer">
              <circle cx="320" cy="280" r="5" fill="#0C1B2A" />
              <text x="310" y="305" fill="#0C1B2A" fontSize="11" fontWeight="600" fontFamily="Newsreader, serif">
                Corfu
              </text>
            </g>
            <g className="cursor-pointer">
              <circle cx="480" cy="230" r="5" fill="#0C1B2A" />
              <text x="495" y="235" fill="#0C1B2A" fontSize="11" fontWeight="600" fontFamily="Newsreader, serif">
                Mykonos
              </text>
            </g>
            <g className="cursor-pointer">
              <circle cx="410" cy="130" r="5" fill="#0C1B2A" />
              <text x="390" y="115" fill="#0C1B2A" fontSize="11" fontWeight="600" fontFamily="Newsreader, serif">
                Dubrovnik
              </text>
            </g>
          </svg>

          {/* Floating Pill Status */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-5 py-2 rounded-full bg-[#0C1B2A] text-white text-xs font-mono font-bold shadow-lg">
            Maritime Verified Trajectory Map
          </div>
        </div>
      </div>

      {/* 3. Main Content: Route Logistics Breakdown & Weather */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Left 2 Cols: Day by Day Logistics */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <span className="eyebrow-tag block mb-1.5">DAY-BY-DAY LOGISTICS</span>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
              Route Breakdown
            </h2>
          </div>

          <div className="space-y-3">
            {route.ports.map((p: any, idx: number) => (
              <div
                key={idx}
                className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-sm flex items-center justify-between transition-all hover:shadow-md"
              >
                <div className="flex items-center gap-4">
                  <span className="font-mono text-xs font-bold text-[#C58A46] min-w-[50px]">
                    Day {p.day}
                  </span>
                  <div>
                    <h4 className="font-display text-base font-bold text-[#0C1B2A]">
                      {p.portName}
                    </h4>
                    <p className="text-xs text-[#5B6570] font-sans">
                      {p.status}
                    </p>
                  </div>
                </div>

                <EpistemicBadge status={p.epistemic} />
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: Weather Overview Card */}
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-4 self-start">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-2xl font-bold text-[#0C1B2A]">
              Weather Overview
            </h3>
            <CloudSun className="w-5 h-5 text-[#C58A46]" />
          </div>

          <p className="text-xs text-[#5B6570] leading-relaxed">
            {route.weatherOverview}
          </p>

          <div className="pt-3 border-t border-[#0C1B2A]/5 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#0C1B2A]">Adriatic Sea (Venice, Bari)</span>
              <EpistemicBadge status="LIKELY" />
            </div>
            <p className="text-[11px] text-[#5B6570]">10°C - 16°C • Occasional mist</p>
          </div>
        </div>
      </div>
    </div>
  );
}
