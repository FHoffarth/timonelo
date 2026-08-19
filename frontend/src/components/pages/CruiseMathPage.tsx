import React, { useState } from "react";
import { LegacyEpistemicBadge } from "../ui/EpistemicBadge";
import { CANONICAL_CRUISE_MATH } from "../../data/canonicalPlatformData";
import { Calculator, Wine, Coffee, DollarSign, Check, Info } from "lucide-react";

export default function CruiseMathPage() {
  const { defaultConfig, drinkPackages, tripSummaryDefaults } = CANONICAL_CRUISE_MATH;

  const [selectedShip, setSelectedShip] = useState(defaultConfig.shipName);
  const [destination, setDestination] = useState(defaultConfig.destination);
  const [durationNights, setDurationNights] = useState(defaultConfig.durationNights);
  const [travelers, setTravelers] = useState(defaultConfig.travelers);
  const [selectedDrinkPkg, setSelectedDrinkPkg] = useState<string>("easy");

  const drinkCost = selectedDrinkPkg === "easy" ? 49 * durationNights * travelers : selectedDrinkPkg === "premium-extra" ? 69 * durationNights * travelers : 0;
  const gratuityCost = 14 * durationNights * travelers;
  const totalMin = tripSummaryDefaults.baseFare + drinkCost + tripSummaryDefaults.specialtyDining + gratuityCost + tripSummaryDefaults.portExcursions.min;
  const totalMax = tripSummaryDefaults.baseFare + drinkCost + tripSummaryDefaults.specialtyDining + 350 + gratuityCost + tripSummaryDefaults.portExcursions.max;

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">INDEPENDENT COST CALCULATOR</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          Cruise Math
        </h1>
        <p className="text-base text-[#5B6570]">
          Independent calculations based on published pricing. No affiliate links. No upselling.
        </p>
      </div>

      {/* 2. Horizontal Trip Configuration Card */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-10">
        <div className="p-6 rounded-3xl bg-white border border-[#0C1B2A]/10 shadow-sm grid grid-cols-2 sm:grid-cols-4 gap-6 text-xs">
          <div className="space-y-1">
            <span className="text-[#5B6570]">Selected Ship</span>
            <div className="font-bold text-[#0C1B2A] text-sm">{selectedShip}</div>
          </div>
          <div className="space-y-1">
            <span className="text-[#5B6570]">Destination</span>
            <div className="font-bold text-[#0C1B2A] text-sm">{destination}</div>
          </div>
          <div className="space-y-1">
            <span className="text-[#5B6570]">Duration</span>
            <div className="font-bold text-[#0C1B2A] text-sm">{durationNights} Nights</div>
          </div>
          <div className="space-y-1">
            <span className="text-[#5B6570]">Travelers</span>
            <div className="font-bold text-[#0C1B2A] text-sm">{travelers} Guests</div>
          </div>
        </div>
      </div>

      {/* 3. Main Calculator Grid */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Left 2 Cols: Onboard Beverage Analysis */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <span className="eyebrow-tag block mb-1.5">ONBOARD BEVERAGE ANALYSIS</span>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
              Drink Packages
            </h2>
          </div>

          <div className="space-y-4">
            {drinkPackages.map((pkg) => {
              const isSelected = selectedDrinkPkg === pkg.id;
              const packageTotal = pkg.pricePerDayPerPerson * durationNights * travelers;

              return (
                <div
                  key={pkg.id}
                  onClick={() => setSelectedDrinkPkg(pkg.id)}
                  className={`p-6 rounded-3xl border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-white border-[#C58A46] ring-2 ring-[#C58A46]/20 shadow-md"
                      : "bg-white/80 border-[#0C1B2A]/10 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
                        {pkg.name}
                      </h3>
                      <LegacyEpistemicBadge status={pkg.epistemic} />
                      <div className="text-sm font-semibold text-[#C58A46] mt-0.5 font-mono">
                        €{pkg.pricePerDayPerPerson} / day / person • {durationNights} nights × {travelers} = €{packageTotal}
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-[#5B6570] leading-relaxed mt-3">
                    {pkg.description} <strong>Break-even requirement: {pkg.breakEven}.</strong>
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Trip Summary Dark Navy Card */}
        <div className="p-8 rounded-3xl bg-[#0C1B2A] text-white shadow-xl space-y-6 self-start">
          <h3 className="font-display text-2xl font-bold text-white">
            Trip Summary
          </h3>

          <div className="space-y-4 text-xs font-mono">
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Base Cruise Fare<br/><span className="text-[10px] text-slate-400">For 2 guests (User input)</span></span>
              <span className="font-bold text-white text-sm">€{tripSummaryDefaults.baseFare.toLocaleString('de-DE', {minimumFractionDigits: 2})}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Drink Packages<br/><span className="text-[10px] text-slate-400">Both guests, package selection</span></span>
              <span className="font-bold text-white text-sm">€{drinkCost.toLocaleString('de-DE', {minimumFractionDigits: 2})}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Specialty Dining<br/><span className="text-[10px] text-slate-400">Estimated 2-dinner package</span></span>
              <span className="font-bold text-white text-sm">~€{tripSummaryDefaults.specialtyDining.toLocaleString('de-DE', {minimumFractionDigits: 2})}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Onboard Internet<br/><span className="text-[10px] text-slate-400">Select options or use ports</span></span>
              <span className="font-bold text-white text-sm">€0,00 – €350,00</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Daily Gratuities<br/><span className="text-[10px] text-slate-400">7 Nights × 2 Guests</span></span>
              <span className="font-bold text-white text-sm">€{gratuityCost.toLocaleString('de-DE', {minimumFractionDigits: 2})}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[#94A3B8]">Port Excursions<br/><span className="text-[10px] text-slate-400">Independent DIY estimates</span></span>
              <span className="font-bold text-white text-sm">€200,00 – €600,00</span>
            </div>

            <div className="pt-2 flex items-center justify-between font-bold text-base text-[#C58A46]">
              <span>Estimated Total</span>
              <span>€{totalMin.toLocaleString('de-DE', {minimumFractionDigits: 2})} – €{totalMax.toLocaleString('de-DE', {minimumFractionDigits: 2})}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
