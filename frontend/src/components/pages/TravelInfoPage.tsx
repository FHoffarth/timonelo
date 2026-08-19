import React from "react";
import { LegacyEpistemicBadge } from "../ui/EpistemicBadge";
import { CANONICAL_TRAVEL_INFO } from "../../data/canonicalPlatformData";
import { ShieldCheck, AlertOctagon, FileCheck, Globe2 } from "lucide-react";

export default function TravelInfoPage() {
  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">CONSULAR & ENVIRONMENTAL INTELLIGENCE</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          Travel Info
        </h1>
        <p className="text-base text-[#5B6570]">
          Visa requirements, weather, health, currency, and immigration — researched for your specific itinerary.
        </p>
        <p className="text-xs font-mono text-[#5B6570]">
          Selected Voyage: MSC Virtuosa • Adriatic & Aegean Run • March 2026
        </p>
      </div>

      {/* 2. Main Content: Border Controls */}
      <div className="max-w-7xl mx-auto w-full px-6 space-y-6">
        <div>
          <span className="eyebrow-tag block mb-1.5">BORDER CONTROLS</span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
            Visa & Immigration
          </h2>
        </div>

        <div className="space-y-4 max-w-5xl">
          {CANONICAL_TRAVEL_INFO.map((item, idx) => (
            <div
              key={idx}
              className="p-6 rounded-3xl bg-white border border-[#0C1B2A]/10 shadow-sm space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
                    {item.country}
                  </h3>
                  <span className="text-xs text-[#5B6570] font-sans">
                    {item.jurisdiction}
                  </span>
                </div>
                <LegacyEpistemicBadge status={item.epistemicStatus} />
              </div>

              <p className="text-sm text-[#5B6570] leading-relaxed">
                {item.visaSummary}
              </p>
            </div>
          ))}

          {/* Critical Requirement Callout Box */}
          <div className="p-6 rounded-3xl bg-[#0C1B2A] text-white shadow-lg space-y-2 border border-white/10">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#C58A46] uppercase">
              <AlertOctagon className="w-4 h-4 text-[#C58A46]" />
              <span>CRITICAL REQUIREMENT: PASSPORT VALIDITY</span>
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Passports must be valid for at least 6 months beyond your scheduled return date. Maritime cruising transit clearances are handled collectively by the ship's Purser; you will typically not stand in individual airport-style customs lines at these ports.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
