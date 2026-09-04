import React from "react";
import { AlertOctagon } from "lucide-react";
import { LIVE_TEST_TRIP } from "../../trip-shell/liveTestContext";

/**
 * Travel requirements for the live-test voyage.
 *
 * This page used to render three hardcoded Schengen entries -- Italy, Greece,
 * Croatia -- each badged KNOWN, under a heading promising the content was
 * "researched for your specific itinerary", above a line naming MSC Virtuosa's
 * Adriatic run. The live-test voyage sails Shanghai to Tokyo. A passenger on
 * that trip was being told, in confident product language, that they needed
 * "zero advance visa procedures", which is not true of China for most
 * nationalities and is not how Japan works either.
 *
 * That was the one place in the build where being wrong could cost someone
 * their sailing, so it is gone rather than adjusted. Nothing replaces it: this
 * repository holds no China or Japan entry requirements, and writing some from
 * model knowledge would reproduce the same defect with a different region's
 * facts. The dedicated Shanghai to Tokyo readiness package will bring real
 * sources.
 *
 * What remains is the true statement -- we do not have this yet -- and a push
 * toward the authorities who do.
 */
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
          Visa requirements, health, currency and immigration for the voyage you are on.
        </p>
        <p className="text-xs font-mono text-[#5B6570]">
          Your voyage: {LIVE_TEST_TRIP.shortLabel}
        </p>
      </div>

      {/* 2. Explicit unavailable state */}
      <div className="max-w-7xl mx-auto w-full px-6 space-y-6">
        <div className="max-w-3xl p-8 rounded-3xl bg-white border border-[#0C1B2A]/10 shadow-sm space-y-4">
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
            We do not have travel requirements for this voyage yet
          </h2>
          <p className="text-sm text-[#5B6570] leading-relaxed">
            Timonelo has not yet researched entry requirements for {LIVE_TEST_TRIP.departure.city}{" "}
            or {LIVE_TEST_TRIP.arrival.city}. We would rather tell you that than
            show you guidance written for a different part of the world.
          </p>
          <p className="text-sm text-[#5B6570] leading-relaxed">
            Before you travel, check the official requirements for your own
            nationality with the embassies or consulates of the countries you
            are visiting, and with your cruise line. Those are the only sources
            that are current and that apply to you specifically.
          </p>

          <div className="p-5 rounded-2xl bg-[#0C1B2A] text-white space-y-2 border border-white/10">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#C58A46] uppercase">
              <AlertOctagon className="w-4 h-4 text-[#C58A46]" />
              <span>Please verify before travel</span>
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Entry rules, visa policies and passport validity requirements change,
              and they differ by nationality. Do not rely on Timonelo for this
              voyage yet — confirm with the official authorities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
