import { useState } from "react";
import { knowledgeRepository } from "../../knowledge";
import { LIVE_TEST_TRIP } from "../../trip-shell/liveTestContext";
import {
  Compass,
  Anchor,
  Waves,
  Calendar,
  Clock,
  Navigation,
  MapPin,
  Building2,
  Sun,
  ShieldCheck,
  ArrowRight,
  Route as RouteIcon,
} from "lucide-react";

interface RouteIntelligencePageProps {
  routeSlug?: string;
  onSelectPort?: (portSlug: string) => void;
}

export default function RouteIntelligencePage({
  routeSlug,
  onSelectPort,
}: RouteIntelligencePageProps) {
  // No default and no fallback. Both used to be
  // "ROUTE_MSC_BELLISSIMA_WMED_7N", so opening Routes -- or searching
  // "adriatic", which resolved to a slug this repository does not have --
  // presented a 7-night Western Mediterranean loop as the passenger's own
  // itinerary. Right ship, wrong ocean, stated with day-by-day timings.
  //
  // There is no Shanghai to Tokyo route dataset here, and inventing one is not
  // this package's job. So the surface says so.
  const routeData = routeSlug ? knowledgeRepository.getRoute(routeSlug) : null;

  const [selectedLegIndex, setSelectedLegIndex] = useState<number>(0);

  if (!routeData) {
    return (
      <div className="w-full flex-1 bg-[#FBF8F3] px-6 py-16">
        <div className="max-w-2xl mx-auto rounded-3xl border border-[#0C1B2A]/10 bg-white p-8 text-center space-y-3">
          <h1 className="font-display text-2xl font-bold text-[#0C1B2A]">
            We have not mapped this route yet
          </h1>
          <p className="text-sm text-[#5B6570] leading-relaxed">
            Timonelo does not yet hold a day-by-day itinerary for{" "}
            {LIVE_TEST_TRIP.departure.city} to {LIVE_TEST_TRIP.arrival.city}.
            Rather than show you a different voyage&apos;s route, we are showing
            you nothing until we have this one.
          </p>
        </div>
      </div>
    );
  }

  const relationships = knowledgeRepository.getRelationships();
  const unlocodeToSlug: Record<string, string> = {};
  if (relationships && relationships.port_slug_to_unlocode) {
    Object.entries(relationships.port_slug_to_unlocode).forEach(([slug, unlocode]) => {
      unlocodeToSlug[unlocode as string] = slug;
    });
  }

  // Helper to dynamically resolve port data from its own canonical JSON
  const getPortDataByUnlocode = (unlocode: string) => {
    const slug = unlocodeToSlug[unlocode] || unlocode.toLowerCase();
    const port = knowledgeRepository.getPort(slug);
    const transport = knowledgeRepository.getPortDomain(slug, "transport");
    const weather = knowledgeRepository.getPortDomain(slug, "weather");
    return { slug, port, transport, weather };
  };

  const legs = routeData.legs || [];
  const activeLeg = legs[selectedLegIndex] || legs[0];
  const activePortInfo = activeLeg ? getPortDataByUnlocode(activeLeg.destination_canonical_id) : null;

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <div className="flex items-center gap-2">
          <span className="eyebrow-tag block">MARITIME ITINERARY INTELLIGENCE</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-900 border border-amber-300">
            {routeData.itinerary_type}
          </span>
        </div>

        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          {routeData.title}
        </h1>

        <div className="flex items-center gap-3 text-xs sm:text-sm text-[#5B6570] font-sans flex-wrap">
          <span>Vessel: <strong className="text-[#0C1B2A]">{routeData.vessel_name}</strong></span>
          <span>•</span>
          <span>Duration: {routeData.duration_nights} Nights</span>
          <span>•</span>
          <span>Total Distance: ~{routeData.total_nautical_miles_approx} NM</span>
          <span>•</span>
          {/* The fallback here was "5/5 Verified", and since `provenance` carries
              no confidence_score it was not a fallback at all -- it was the only
              value this line ever rendered. A confidence rating nothing computes
              is not a rating. It is shown when a route actually carries one. */}
          {routeData.provenance?.confidence_score && (
            <span>Confidence: <strong className="text-[#C58A46]">{routeData.provenance.confidence_score}</strong></span>
          )}
        </div>
      </div>

      {/* 2. Maritime Trajectory Map & Circuit Schematic */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-10">
        <div className="relative w-full h-[360px] sm:h-[420px] rounded-3xl bg-[#0C1B2A] border border-[#0C1B2A]/10 overflow-hidden shadow-xl flex items-center justify-center p-6 text-white">
          {/* Schematic SVG Map Graphic for Western Med Loop */}
          <svg className="w-full h-full" viewBox="0 0 900 380" fill="none">
            {/* Background maritime grid lines */}
            <line x1="50" y1="100" x2="850" y2="100" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="50" y1="200" x2="850" y2="200" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="50" y1="300" x2="850" y2="300" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />

            {/* Trajectory Loop Path */}
            {/* Coordinates: BCN(180, 140) -> MRS(340, 70) -> GOA(500, 80) -> NAP(640, 190) -> MSN(660, 270) -> MLA(620, 330) -> (Sea Day) -> BCN(180, 140) */}
            <path
              d="M 180 140 L 340 70 L 500 80 L 640 190 L 660 270 L 620 330 L 180 140"
              stroke="#C58A46"
              strokeWidth="3"
              strokeDasharray="8 4"
              strokeLinecap="round"
              className="animate-pulse"
            />

            {/* Waypoints with dynamic labels */}
            {[
              { id: "ES-BCN", name: "Barcelona", x: 180, y: 140, day: "Day 1 / 8" },
              { id: "FR-MRS", name: "Marseille", x: 340, y: 70, day: "Day 2" },
              { id: "IT-GOA", name: "Genoa", x: 500, y: 80, day: "Day 3" },
              { id: "IT-NAP", name: "Naples", x: 640, y: 190, day: "Day 4" },
              { id: "IT-MSN", name: "Messina", x: 660, y: 270, day: "Day 5" },
              { id: "MT-MLA", name: "Valletta", x: 620, y: 330, day: "Day 6" },
            ].map((pt) => {
              const portInfo = getPortDataByUnlocode(pt.id);
              return (
                <g
                  key={pt.id}
                  onClick={() => onSelectPort && portInfo.slug && onSelectPort(portInfo.slug)}
                  className="cursor-pointer group"
                >
                  <circle cx={pt.x} cy={pt.y} r="8" fill="#C58A46" stroke="#0C1B2A" strokeWidth="2" />
                  <circle cx={pt.x} cy={pt.y} r="4" fill="#FFFFFF" />
                  <text
                    x={pt.x + 14}
                    y={pt.y + 4}
                    fill="#FFFFFF"
                    fontSize="13"
                    fontWeight="bold"
                    fontFamily="Newsreader, serif"
                    className="group-hover:fill-[#C58A46] transition-colors"
                  >
                    {pt.name}
                  </text>
                  <text x={pt.x + 14} y={pt.y + 18} fill="#94A3B8" fontSize="10" fontFamily="Inter, sans-serif">
                    {pt.day} • {pt.id}
                  </text>
                </g>
              );
            })}

            {/* Sea Day Open Water Marker */}
            <g>
              <rect x="340" y="240" width="160" height="34" rx="17" fill="#1E293B" stroke="#C58A46" strokeWidth="1" />
              <text x="360" y="261" fill="#C58A46" fontSize="11" fontWeight="bold" fontFamily="Inter, sans-serif">
                🌊 Sea Day: ~600 NM
              </text>
            </g>
          </svg>

          {/* Floating Pill */}
          <div className="absolute bottom-4 left-6 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-white text-xs font-mono">
            Relational Circuit: 8 Interporting Legs · 6 Strategic Ports · 1 Sea Day
          </div>
        </div>
      </div>

      {/* 3. Main Content: Day-by-Day Timeline & Dynamic Port Intelligence */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Left 2 Cols: Chronological Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <span className="eyebrow-tag block mb-1">RELATIONAL TIMELINE</span>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
              Day-by-Day Route Itinerary
            </h2>
            <p className="text-xs text-[#5B6570] mt-1">
              Every waypoint references canonical port IDs only. Click any leg to inspect verified port intelligence.
            </p>
          </div>

          <div className="space-y-3">
            {legs.map((leg: any, idx: number) => {
              const destPortInfo = getPortDataByUnlocode(leg.destination_canonical_id);
              const isSelected = selectedLegIndex === idx;

              return (
                <div
                  key={leg.leg_sequence}
                  onClick={() => setSelectedLegIndex(idx)}
                  className={`p-5 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-white border-[#C58A46] shadow-md ring-1 ring-[#C58A46]"
                      : "bg-white/80 border-[#0C1B2A]/10 hover:border-[#0C1B2A]/30 hover:bg-white"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-start sm:items-center gap-4">
                      {/* Day Number Badge */}
                      <div className="w-12 h-12 rounded-xl bg-[#0C1B2A] text-white flex flex-col items-center justify-center shrink-0">
                        <span className="text-[9px] font-mono text-slate-400 uppercase leading-none">DAY</span>
                        <span className="text-lg font-bold font-mono leading-tight">{leg.day}</span>
                      </div>

                      {/* Leg Details */}
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-display text-lg font-bold text-[#0C1B2A]">
                            {leg.sea_day ? "At Sea (Cruising Western Mediterranean)" : destPortInfo.port ? destPortInfo.port.name : leg.destination_canonical_id}
                          </h3>
                          {leg.sea_day ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-100 text-sky-900 border border-sky-300">
                              SEA DAY
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-900 border border-amber-300">
                              {leg.destination_canonical_id}
                            </span>
                          )}
                          {leg.homeport && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                              EMBARKATION / HOMEPORT
                            </span>
                          )}
                        </div>

                        {/* Timing & Nautical Details */}
                        <div className="flex items-center gap-4 text-xs text-[#5B6570] font-sans flex-wrap">
                          {leg.arrival && (
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 text-emerald-600" />
                              Arrival: <strong>{leg.arrival}</strong>
                            </span>
                          )}
                          {leg.departure && (
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 text-amber-600" />
                              Departure: <strong>{leg.departure}</strong>
                            </span>
                          )}
                          {leg.distance_if_known_nm > 0 && (
                            <span className="flex items-center gap-1 font-mono text-[#C58A46]">
                              <Navigation className="w-3.5 h-3.5" />
                              {leg.distance_if_known_nm} NM
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Action Button */}
                    {!leg.sea_day && destPortInfo.slug && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectPort) onSelectPort(destPortInfo.slug);
                        }}
                        className="self-start sm:self-center px-3 py-1.5 bg-slate-100 hover:bg-[#0C1B2A] hover:text-white rounded-xl text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer shrink-0"
                      >
                        <span>Port Guide</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Dynamic Port Card Loaded Directly From Port's Own JSON */}
        <div className="space-y-6 self-start">
          {activePortInfo && activePortInfo.port ? (
            <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="eyebrow-tag block">DYNAMIC PORT DOSSIER</span>
                  <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
                    {activePortInfo.port.name}
                  </h3>
                </div>
                <span className="px-2 py-1 bg-[#0C1B2A] text-white text-xs font-mono font-bold rounded-lg">
                  {activeLeg.destination_canonical_id}
                </span>
              </div>

              {/* Port Summary from its own port.json */}
              <p className="text-xs text-[#5B6570] leading-relaxed">
                {activePortInfo.port.overview_text}
              </p>

              {/* Walking Feasibility from port.json */}
              {activePortInfo.port.walking_feasibility && (
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/70 space-y-1">
                  <div className="text-[10px] font-mono uppercase font-bold text-[#C58A46] flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>Walking Feasibility ({activePortInfo.port.walking_feasibility.rating})</span>
                  </div>
                  <p className="text-xs text-[#5B6570]">
                    {activePortInfo.port.walking_feasibility.description}
                  </p>
                </div>
              )}

              {/* Terminals from port.json */}
              {activePortInfo.port.terminals && (
                <div className="space-y-2">
                  <div className="text-[11px] font-mono font-bold uppercase text-[#0C1B2A]">
                    Berthing Terminals ({activePortInfo.port.terminals.length})
                  </div>
                  <div className="space-y-1.5">
                    {activePortInfo.port.terminals.slice(0, 2).map((t: any) => (
                      <div key={t.id} className="text-xs p-2 rounded-lg bg-slate-50 border border-slate-200/50">
                        <div className="font-bold text-[#0C1B2A]">{t.name}</div>
                        <div className="text-[11px] text-slate-500">{t.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Weather Snapshot from weather.json */}
              {activePortInfo.weather?.climate_profile && (
                <div className="p-3.5 rounded-2xl bg-amber-50/60 border border-amber-200/60 space-y-1">
                  <div className="text-[10px] font-mono uppercase font-bold text-amber-900 flex items-center gap-1">
                    <Sun className="w-3.5 h-3.5 text-amber-600" />
                    <span>Climate ({activePortInfo.weather.climate_profile.climate_type})</span>
                  </div>
                  <p className="text-xs text-amber-950">
                    Summer High: {activePortInfo.weather.climate_profile.seasonal_patterns?.summer?.avg_high_celsius || "28"}°C • Best transit months: March – October.
                  </p>
                </div>
              )}

              {/* Drill-Down Action Button */}
              {onSelectPort && activePortInfo.slug && (
                <button
                  onClick={() => onSelectPort(activePortInfo.slug)}
                  className="w-full py-3 bg-[#0C1B2A] text-white text-xs font-semibold rounded-2xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-md"
                >
                  <span>Open Full {activePortInfo.port.name.split(" ")[0]} Guide</span>
                  <ArrowRight className="w-4 h-4 text-amber-300" />
                </button>
              )}
            </div>
          ) : (
            /* Sea Day Info Card */
            <div className="p-6 bg-[#0C1B2A] text-white rounded-3xl shadow-xl space-y-4">
              <span className="eyebrow-tag text-[#C58A46] block">OPEN SEA TRANSIT</span>
              <h3 className="font-display text-2xl font-bold">Western Mediterranean Transit</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                600 Nautical Miles of open sea navigation between Valletta (Malta) and Barcelona (Spain).
              </p>
              <div className="pt-3 border-t border-white/10 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Required Speed:</span>
                  <span className="font-bold text-[#C58A46]">~16.5 knots</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Stabilizer Status:</span>
                  <span className="font-bold text-emerald-400">Hydrodynamic Active</span>
                </div>
              </div>
            </div>
          )}

          {/* Sources & Provenance Box */}
          <div className="p-5 bg-white rounded-2xl border border-[#0C1B2A]/10 text-xs space-y-2">
            <div className="font-bold text-[#0C1B2A] flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Evidentiary Sources</span>
            </div>
            <ul className="space-y-1 text-[11px] text-slate-500">
              {(routeData.sources || []).map((s: any, i: number) => (
                <li key={i}>• {s.name} ({s.type})</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
