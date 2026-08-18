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
            Independent, evidence-grounded intelligence for cruise passengers. Ships, cabins, ports, and routes — researched, verified, and scientifically modeled.
          </p>
        </div>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] font-bold text-[#C58A46] uppercase tracking-wider">
            Canonical Knowledge
          </h4>
          <ul className="space-y-1.5 text-[#94A3B8]">
            <li>W3C Building Topology Ontology (BOT)</li>
            <li>W3C Provenance Ontology (PROV-O)</li>
            <li>OGC IndoorGML Spatial Representation</li>
            <li>JSON-LD Semantic Linked Data</li>
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
            <li>Consular & Schengen Regulations</li>
          </ul>
        </div>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] font-bold text-[#C58A46] uppercase tracking-wider">
            Integrity Pinning
          </h4>
          <p className="text-[#94A3B8] text-[11px] leading-relaxed">
            Every stateroom and venue statement is pinned with cryptographic SHA-256 evidence digests from official builder general arrangement plans.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-8 mt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#94A3B8] gap-4">
        <span>© 2026 Timonelo Platform. All rights reserved. Zero affiliate bias.</span>
        <span className="font-mono text-[#C58A46]">Design Freeze v1 • Canonical Platform Release</span>
      </div>
    </footer>
  );
}
