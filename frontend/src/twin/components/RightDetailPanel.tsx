import React from "react";
import { CabinData, VenueData } from "../types";
import {
  X,
  Navigation2,
  FileCheck2,
  Accessibility,
  Footprints,
  Compass,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  MapPin,
  Clock,
} from "lucide-react";

interface RightDetailPanelProps {
  selectedCabin: CabinData | null;
  selectedVenue: VenueData | null;
  onClose: () => void;
  onStartRoute: (from: string, to: string) => void;
  onOpenEvidence: (cabin: CabinData) => void;
  onSelectCabinNumber: (cNum: string) => void;
}

export default function RightDetailPanel({
  selectedCabin,
  selectedVenue,
  onClose,
  onStartRoute,
  onOpenEvidence,
  onSelectCabinNumber,
}: RightDetailPanelProps) {
  if (!selectedCabin && !selectedVenue) return null;

  return (
    <div className="absolute right-6 top-24 bottom-16 w-96 z-30 pointer-events-auto flex flex-col bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-8 duration-300">
      {/* Header Banner */}
      <div className="relative p-5 pb-4 bg-gradient-to-b from-sky-500/10 to-transparent border-b border-white/5 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase bg-sky-500/20 text-sky-300 border border-sky-400/30">
              {selectedCabin ? "Stateroom Profile" : "Public Venue"}
            </span>
            {selectedCabin?.accessible && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 flex items-center gap-1">
                <Accessibility className="w-3 h-3" />
                PRM Accessible (H)
              </span>
            )}
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {selectedCabin ? `Cabin ${selectedCabin.cabin_number}` : selectedVenue?.name}
          </h2>
          <p className="text-xs text-slate-400 font-medium">
            {selectedCabin
              ? `Deck ${selectedCabin.deck} • ${selectedCabin.deck_name} • ${selectedCabin.category}`
              : `Deck ${selectedVenue?.deck} • ${selectedVenue?.category.replace(/_/g, " ")}`}
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Scrollable Content Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 no-scrollbar text-sm text-slate-300">
        {/* Quick Action Navigation Buttons */}
        <div className="grid grid-cols-2 gap-2.5">
          <button
            onClick={() =>
              selectedCabin
                ? onStartRoute(selectedCabin.cabin_number, "Marketplace Buffet")
                : onStartRoute("14122", selectedVenue?.name ?? "")
            }
            className="px-4 py-2.5 rounded-2xl font-semibold text-xs bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 transition-all active:scale-95"
          >
            <Navigation2 className="w-4 h-4 fill-slate-950" />
            Route to Buffet
          </button>
          {selectedCabin && (
            <button
              onClick={() => onOpenEvidence(selectedCabin)}
              className="px-4 py-2.5 rounded-2xl font-semibold text-xs bg-slate-800 hover:bg-slate-700 text-white border border-white/10 flex items-center justify-center gap-2 transition-all active:scale-95"
            >
              <FileCheck2 className="w-4 h-4 text-sky-400" />
              Official Evidence
            </button>
          )}
        </div>

        {/* Stateroom Physical Specs */}
        {selectedCabin && (
          <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Stateroom Specifications
            </h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-slate-500 block text-[11px]">Hull Side</span>
                <span className="font-semibold text-slate-200">{selectedCabin.hull_side}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Balcony</span>
                <span className="font-semibold text-slate-200">
                  {selectedCabin.balcony ? "Yes (Private Veranda)" : "Interior (No Balcony)"}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Connecting Door</span>
                <span className="font-semibold text-slate-200">
                  {selectedCabin.connecting_cabin ? "Yes" : "No"}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Berth Beds</span>
                <span className="font-mono text-slate-400">UNKNOWN (Unreviewed)</span>
              </div>
            </div>
          </div>
        )}

        {/* Spatial Neighborhood / Adjacencies */}
        {selectedCabin && (
          <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2.5">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Spatial Adjacencies</span>
              <span className="text-[10px] text-sky-400 font-mono">Topology Proof</span>
            </h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div
                onClick={() => selectedCabin.neighbor_left && onSelectCabinNumber(selectedCabin.neighbor_left)}
                className="p-2 rounded-xl bg-slate-900/60 border border-white/5 hover:border-sky-400/40 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowLeft className="w-3 h-3" /> Neighbor Left (Fwd)
                </div>
                <div className="font-mono font-semibold text-slate-200 mt-0.5">
                  {selectedCabin.neighbor_left ?? "Bulkhead"}
                </div>
              </div>

              <div
                onClick={() => selectedCabin.neighbor_right && onSelectCabinNumber(selectedCabin.neighbor_right)}
                className="p-2 rounded-xl bg-slate-900/60 border border-white/5 hover:border-sky-400/40 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowRight className="w-3 h-3" /> Neighbor Right (Aft)
                </div>
                <div className="font-mono font-semibold text-slate-200 mt-0.5">
                  {selectedCabin.neighbor_right ?? "Bulkhead"}
                </div>
              </div>

              <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowUp className="w-3 h-3 text-emerald-400" /> Ceiling Above (Deck {selectedCabin.deck + 1})
                </div>
                <div className="font-semibold text-slate-200 mt-0.5">
                  {selectedCabin.cabin_above ?? "Residential Stateroom"}
                </div>
              </div>

              <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowDown className="w-3 h-3 text-blue-400" /> Floor Below (Deck {selectedCabin.deck - 1})
                </div>
                <div className="font-semibold text-slate-200 mt-0.5">
                  {selectedCabin.cabin_below ?? "Residential Stateroom"}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Proximity & Distance Matrix */}
        {selectedCabin && (
          <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Nearest Amenities & Landmarks
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40">
                <div className="flex items-center gap-2">
                  <Compass className="w-4 h-4 text-cyan-400" />
                  <span>{selectedCabin.nearest_elevator.name}</span>
                </div>
                <span className="font-mono text-cyan-300 font-semibold">
                  {selectedCabin.nearest_elevator.walking_distance_m}m (~17s)
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40">
                <div className="flex items-center gap-2">
                  <Footprints className="w-4 h-4 text-emerald-400" />
                  <span>Marketplace Buffet</span>
                </div>
                <span className="font-mono text-emerald-300 font-semibold">
                  111.1m (~1.9min)
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-rose-400" />
                  <span className="truncate max-w-[180px]">{selectedCabin.nearest_muster_station}</span>
                </div>
                <span className="font-mono text-rose-300 font-semibold">Deck 6</span>
              </div>
            </div>
          </div>
        )}

        {/* Evidence Provenance Badge */}
        {selectedCabin && (
          <div className="p-3 bg-sky-950/40 border border-sky-500/20 rounded-2xl text-xs space-y-1">
            <div className="text-[11px] font-semibold text-sky-400 flex items-center gap-1.5">
              <FileCheck2 className="w-3.5 h-3.5" />
              Source: {selectedCabin.evidence_artifact}
            </div>
            <div className="text-[11px] text-slate-400 font-mono">
              Page {selectedCabin.page} • Locator: {selectedCabin.locator}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
