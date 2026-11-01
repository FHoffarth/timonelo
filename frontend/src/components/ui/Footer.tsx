import React from "react";

export default function Footer() {
  return (
    <footer className="bg-[#0C1B2A] text-white py-16 px-6 select-none border-t border-white/10 mt-auto">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 text-xs">
        <div className="space-y-3">
          <div className="flex items-baseline gap-2">
            <span className="font-display text-xl font-bold text-white tracking-tight">
              Timonelo
            </span>
            <span className="text-[9px] font-mono font-bold tracking-[0.18em] text-[#C58A46] uppercase">
              CRUISE INTELLIGENCE
            </span>
          </div>
          <p className="text-[#94A3B8] leading-relaxed text-[11px]">
            Cruise information with visible source limitations. Reference material is distinguished from admitted passenger facts.
          </p>
        </div>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] font-bold text-[#C58A46] uppercase tracking-wider">
            Information status
          </h4>
          <ul className="space-y-1.5 text-[#94A3B8]">
            <li>Reference material is not a confirmed booking.</li>
            <li>Unavailable details stay unavailable.</li>
            <li>Deck and cabin facts require their own evidence checks.</li>
          </ul>
        </div>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] font-bold text-[#C58A46] uppercase tracking-wider">
            Pillars
          </h4>
          <ul className="space-y-1.5 text-[#94A3B8]">
            <li>Ship Intelligence & Living Decks</li>
            <li>Independent Port & Tender Guides</li>
            <li>True Cost Math & Beverage Calculator</li>
            <li>Travel information availability</li>
          </ul>
        </div>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] font-bold text-[#C58A46] uppercase tracking-wider">
            Source limitations
          </h4>
          <p className="text-[#94A3B8] text-[11px] leading-relaxed">
            Some ship and port material is retained as unverified reference data. This beta does not establish current operations, access, travel requirements or cabin geometry from those references.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-8 mt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#94A3B8] gap-4">
        <span>© 2026 Timonelo Platform. All rights reserved. Zero affiliate bias.</span>
        <span className="font-mono text-[#C58A46]">Passenger Beta • Reference coverage varies</span>
      </div>
    </footer>
  );
}
