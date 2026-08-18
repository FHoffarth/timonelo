import React, { useState } from "react";
import SubTabBar, { TabOption } from "../ui/SubTabBar";
import { CANONICAL_PORTS } from "../../data/canonicalPlatformData";
import { Anchor, Waves, Users, DollarSign, Languages, AlertTriangle } from "lucide-react";

interface PortGuidePageProps {
  portSlug?: string;
  onSelectPort?: (slug: string) => void;
}

export default function PortGuidePage({
  portSlug = "santorini",
  onSelectPort,
}: PortGuidePageProps) {
  const port = CANONICAL_PORTS[portSlug] || CANONICAL_PORTS["santorini"];
  const [activeTab, setActiveTab] = useState<string>("overview");

  const tabs: TabOption[] = [
    { id: "overview", label: "Overview" },
    { id: "getting-around", label: "Getting Around" },
    { id: "excursions", label: "Excursions" },
    { id: "all-aboard", label: "All-Aboard" },
    { id: "travel-info", label: "Travel Info" },
  ];

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">INDEPENDENT PORT GUIDE</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          {port.name}
        </h1>

        {/* Port Metrics Row */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-[#5B6570] flex-wrap font-sans">
          <span className="font-semibold text-[#0C1B2A]">{port.tenderPort ? "Tender Port" : "Docked Berth"}</span>
          <span>•</span>
          <span>{port.bodyOfWater}</span>
          <span>•</span>
          <span>Population {port.population}</span>
          <span>•</span>
          <span>Currency: {port.currency}</span>
          <span>•</span>
          <span>Language: {port.language}</span>
        </div>
      </div>

      {/* 2. Hero Scenic Photography */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-8">
        <div className="relative w-full h-[360px] sm:h-[440px] rounded-3xl overflow-hidden shadow-md">
          <img
            src={port.heroImageUrl}
            alt={port.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0C1B2A]/40 to-transparent" />
        </div>
      </div>

      {/* 3. Sub Navigation Tabs */}
      <div className="max-w-7xl mx-auto w-full px-6">
        <SubTabBar tabs={tabs} activeTab={activeTab} onSelectTab={setActiveTab} />
      </div>

      {/* 4. Tab Content */}
      <div className="max-w-7xl mx-auto w-full px-6 py-10">
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <div className="lg:col-span-2 space-y-6">
              <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
                Port Summary & Arrival Logistics
              </h2>
              <p className="text-base text-[#5B6570] leading-relaxed">
                {port.overviewText}
              </p>

              {/* All Aboard Critical Warning Box */}
              <div className="p-6 rounded-2xl bg-amber-50 border border-amber-200/80 text-amber-950 space-y-2">
                <div className="flex items-center gap-2 font-display text-lg font-bold text-amber-900">
                  <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                  <span>Crucial All-Aboard Notice</span>
                </div>
                <p className="text-xs text-amber-900/90 leading-relaxed font-sans">
                  {port.allAboardWarning}
                </p>
              </div>
            </div>

            {/* Right: Quick Port Facts */}
            <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-4 self-start">
              <h3 className="font-display text-2xl font-bold text-[#0C1B2A]">
                Port Fast Facts
              </h3>
              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-[#0C1B2A]/5">
                  <span className="text-[#5B6570]">Transfer Type:</span>
                  <span className="font-bold text-[#0C1B2A]">{port.tenderPort ? "Tender Boat (~15 min)" : "Walk-off Gangway"}</span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-[#0C1B2A]/5">
                  <span className="text-[#5B6570]">Primary Pier:</span>
                  <span className="font-bold text-[#0C1B2A]">Fira Skala / Old Port</span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-[#0C1B2A]/5">
                  <span className="text-[#5B6570]">Cable Car Cost:</span>
                  <span className="font-bold text-[#C58A46]">€6.00 one-way</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#5B6570]">Language:</span>
                  <span className="font-bold text-[#0C1B2A]">{port.language} (English widespread)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "getting-around" && (
          <div className="p-8 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4 max-w-4xl">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">Getting Around in {port.name}</h2>
            <p className="text-sm text-[#5B6570] leading-relaxed">{port.gettingAround}</p>
          </div>
        )}

        {activeTab === "excursions" && (
          <div className="p-8 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4 max-w-4xl">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">Independent DIY Excursions</h2>
            <p className="text-sm text-[#5B6570]">Step-by-step DIY excursion routes to Oia village, Akrotiri ruins, and Red Beach without overpriced bus tours.</p>
          </div>
        )}

        {activeTab === "all-aboard" && (
          <div className="p-8 bg-amber-50 rounded-2xl border border-amber-200 space-y-4 max-w-4xl">
            <h2 className="font-display text-2xl font-bold text-amber-900">All-Aboard Countdown Strategy</h2>
            <p className="text-sm text-amber-950 leading-relaxed">{port.allAboardWarning}</p>
          </div>
        )}

        {activeTab === "travel-info" && (
          <div className="p-8 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4 max-w-4xl">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">Consular & Immigration Requirements</h2>
            <p className="text-sm text-[#5B6570]">EU / Schengen jurisdiction. Zero advance visa needed for US/UK/EU passport holders under 90 days.</p>
          </div>
        )}
      </div>
    </div>
  );
}
