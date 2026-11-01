import React from "react";
import SearchPill from "../ui/SearchPill";
import { NavRoute } from "../ui/MainNavbar";
import { Ship, Compass, Calculator } from "lucide-react";
import { LIVE_TEST_TRIP } from "../../trip-shell/liveTestContext";

interface HomePageProps {
  onNavigate: (route: NavRoute, param?: string) => void;
  onSearch: (query: string) => void;
}

export default function HomePage({ onNavigate, onSearch }: HomePageProps) {
  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3]">
      {/* Hero Section */}
      <section className="py-24 px-6 text-center select-none">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold text-[#0C1B2A] tracking-tight leading-[1.05]">
            Know Your Cruise
          </h1>

          <p className="text-base sm:text-lg text-[#5B6570] max-w-2xl mx-auto leading-relaxed">
            Explore Bellissima, check cabin information and browse port references. We show you what is available and where information is still missing.
          </p>

          <div className="pt-4 flex justify-center">
            <SearchPill placeholder="Bellissima, Genoa, cabin 14122..." onSearch={onSearch} />
          </div>
          <button onClick={() => onNavigate('my-cruise')} className="min-h-11 rounded-full bg-[#0C1B2A] text-white px-5">Open past reference voyage</button>
          <button onClick={() => onNavigate('ships')} className="min-h-11 rounded-full border border-[#0C1B2A]/20 px-5 ml-2">Browse MSC ships</button>
        </div>
      </section>

      {/* 3 Pillars / Feature Grid */}
      <section className="py-16 px-6 border-t border-[#0C1B2A]/10 bg-white/60">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Pillar 1: Ship Intelligence */}
          <button type="button"
            onClick={() => onNavigate("ships", LIVE_TEST_TRIP.vesselSlug)}
            className="text-left space-y-3 cursor-pointer group p-6 rounded-2xl hover:bg-white transition-all hover:shadow-md border border-transparent hover:border-[#0C1B2A]/10"
          >
            <h3 className="font-display text-2xl font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
              Ship Intelligence
            </h3>
            <p className="text-sm text-[#5B6570] leading-relaxed">
              Explore the Bellissima guide, restaurant references and cabin information availability. Source limitations stay visible.
            </p>
          </button>

          {/* Pillar 2: Port Guides */}
          <button type="button"
            onClick={() => onNavigate("ports")}
            className="text-left space-y-3 cursor-pointer group p-6 rounded-2xl hover:bg-white transition-all hover:shadow-md border border-transparent hover:border-[#0C1B2A]/10"
          >
            <h3 className="font-display text-2xl font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
              Port Guides
            </h3>
            <p className="text-sm text-[#5B6570] leading-relaxed">
              Where you dock, how to get around, and what to prioritise ashore — for the
              ports we have researched so far. Browse them freely; none of them is
              assumed to be a stop on your voyage.
            </p>
          </button>

          {/* Pillar 3: Cruise Math */}
          <button type="button"
            onClick={() => onNavigate("cruise-math")}
            className="text-left space-y-3 cursor-pointer group p-6 rounded-2xl hover:bg-white transition-all hover:shadow-md border border-transparent hover:border-[#0C1B2A]/10"
          >
            <h3 className="font-display text-2xl font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
              Cruise Math
            </h3>
            <p className="text-sm text-[#5B6570] leading-relaxed">
              What your cruise actually costs. Drink packages, dining, Wi-Fi, gratuities — calculated honestly.
            </p>
          </button>
        </div>
      </section>
    </div>
  );
}
