import { useState } from "react";
import SubTabBar, { TabOption } from "../ui/SubTabBar";
import { knowledgeRepository } from "../../knowledge";
import {
  MapPin,
  Building2,
  Navigation,
  Bus,
  Train,
  Plane,
  Car,
  HeartPulse,
  PhoneCall,
  Sun,
  Zap,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";

interface PortGuidePageProps {
  portSlug?: string;
  onSelectPort?: (slug: string) => void;
}

export default function PortGuidePage({
  portSlug = "genoa",
  onSelectPort,
}: PortGuidePageProps) {
  // Normalize slug and load directly from the canonical Knowledge Layer
  const canonicalPortSlug = knowledgeRepository.getPort(portSlug) ? portSlug : "genoa";
  const portData = knowledgeRepository.getPort(canonicalPortSlug);
  const transportData = knowledgeRepository.getPortDomain(canonicalPortSlug, "transport");
  const emergencyData = knowledgeRepository.getPortDomain(canonicalPortSlug, "emergency");
  const medicalData = knowledgeRepository.getPortDomain(canonicalPortSlug, "medical");
  const weatherData = knowledgeRepository.getPortDomain(canonicalPortSlug, "weather");
  const sustainabilityData = knowledgeRepository.getPortDomain(canonicalPortSlug, "sustainability");

  const [activeTab, setActiveTab] = useState<string>("overview");

  const allAvailablePorts = ["barcelona", "marseille", "genoa", "naples", "messina", "valletta"];

  const tabs: TabOption[] = [
    { id: "overview", label: "Overview & Terminals" },
    { id: "transport", label: "Transit, Walking & Airport" },
    { id: "medical-emergency", label: "Emergency & Medical" },
    { id: "weather", label: "Climate & Weather" },
    { id: "sustainability", label: "Shore Power & Ecology" },
  ];

  if (!portData) {
    return (
      <div className="p-12 text-center text-slate-500">
        Port intelligence data not found.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="eyebrow-tag block">CANONICAL PORT INTELLIGENCE</span>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
              {portData.name}
            </h1>
          </div>

          {/* Quick Port Switcher */}
          {onSelectPort && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold mr-1">Switch Port:</span>
              {allAvailablePorts.map((slug) => {
                const p = knowledgeRepository.getPort(slug);
                return (
                  <button
                    key={slug}
                    onClick={() => onSelectPort(slug)}
                    className={`px-2.5 py-1 text-xs font-medium rounded-lg border transition-all cursor-pointer ${
                      slug === canonicalPortSlug
                        ? "bg-[#0C1B2A] text-white border-[#0C1B2A]"
                        : "bg-white text-slate-600 border-slate-200 hover:border-[#C58A46]"
                    }`}
                  >
                    {p ? p.name.split(" ")[0].replace("Port", "").replace("of", "").trim() || slug : slug}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Port Metrics Row */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-[#5B6570] flex-wrap font-sans pt-1">
          <span className="font-semibold text-[#0C1B2A]">{portData.tender_port ? "Tender Port" : "Docked Berth"}</span>
          <span>•</span>
          <span>{portData.country}</span>
          <span>•</span>
          <span>{portData.body_of_water}</span>
          <span>•</span>
          <span>Population {portData.population}</span>
          <span>•</span>
          <span>Currency: {portData.currency}</span>
          <span>•</span>
          <span>Language: {portData.language}</span>
        </div>
      </div>

      {/* 2. Hero Scenic Photography */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-8">
        <div className="relative w-full h-[320px] sm:h-[400px] rounded-3xl overflow-hidden shadow-md bg-slate-900">
          <img
            src={`https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=1600&q=80`}
            alt={portData.name}
            className="w-full h-full object-cover opacity-90"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0C1B2A]/70 via-transparent to-transparent" />
          <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between text-white">
            <div>
              <span className="px-2.5 py-1 rounded bg-[#C58A46] text-white text-[11px] font-mono font-bold uppercase tracking-wider">
                UN/LOCODE: {canonicalPortSlug.toUpperCase()}
              </span>
              <h3 className="font-display text-2xl font-bold mt-2">{portData.country} Turnaround & Transit Hub</h3>
            </div>
            <div className="hidden sm:block text-right text-xs text-slate-300">
              <div>Verified Authority: {portData.provenance?.verification_authority || "Port Authority Register"}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Sub Navigation Tabs */}
      <div className="max-w-7xl mx-auto w-full px-6">
        <SubTabBar tabs={tabs} activeTab={activeTab} onSelectTab={setActiveTab} />
      </div>

      {/* 4. Tab Content */}
      <div className="max-w-7xl mx-auto w-full px-6 py-10">
        {/* TAB 1: OVERVIEW & TERMINALS */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <div className="lg:col-span-2 space-y-8">
              {/* Port Summary */}
              <div className="space-y-4">
                <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
                  Port Overview & Logistics
                </h2>
                <p className="text-base text-[#5B6570] leading-relaxed">
                  {portData.overview_text}
                </p>
                <p className="text-sm text-[#5B6570] leading-relaxed">
                  {portData.arrival_procedures}
                </p>
              </div>

              {/* Terminals Grid */}
              <div className="space-y-4 pt-2">
                <h3 className="font-display text-xl font-bold text-[#0C1B2A] flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-[#C58A46]" />
                  <span>Passenger Terminals & Berthing Quays</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(portData.terminals || []).map((term: any) => (
                    <div key={term.id} className="p-5 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                      <div className="flex items-center justify-between">
                        <span className="eyebrow-tag">{term.id}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                          {term.status || "Operational"}
                        </span>
                      </div>
                      <h4 className="font-display text-base font-bold text-[#0C1B2A]">{term.name}</h4>
                      <p className="text-xs text-[#5B6570] leading-relaxed">{term.description}</p>
                      <div className="text-[11px] text-slate-400 pt-1">Location: {term.location}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* All Aboard Critical Notice */}
              {portData.all_aboard_warning && (
                <div className="p-6 rounded-2xl bg-amber-50 border border-amber-200/80 text-amber-950 space-y-2">
                  <div className="flex items-center gap-2 font-display text-lg font-bold text-amber-900">
                    <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                    <span>Crucial All-Aboard Strategy</span>
                  </div>
                  <p className="text-xs text-amber-900/90 leading-relaxed font-sans">
                    {portData.all_aboard_warning}
                  </p>
                </div>
              )}
            </div>

            {/* Right: Quick Port Facts */}
            <div className="p-8 bg-[#0C1B2A] text-white rounded-3xl shadow-xl space-y-6 self-start">
              <h3 className="font-display text-2xl font-bold text-white">
                Port Summary
              </h3>

              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-[#C58A46] block mb-1">
                    BERTHING & ACCESS
                  </span>
                  <div className="font-bold text-white mb-0.5">Transfer Mode</div>
                  <p className="text-[#94A3B8]">{portData.tender_port ? "Tender Transfers (~15 min)" : "Direct Gangway Walk-Off"}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Walking to City Center</div>
                  <p className="text-[#94A3B8]">
                    {portData.walking_feasibility?.rating} ({portData.walking_feasibility?.distance_to_center_km} km)
                  </p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Departure Protocols</div>
                  <p className="text-[#94A3B8]">{portData.departure_procedures}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Shore Power Status</div>
                  <p className="text-[#94A3B8]">{sustainabilityData?.shore_power_ops?.status || "OPS Enabled"}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TRANSIT, WALKING & AIRPORT */}
        {activeTab === "transport" && transportData && (
          <div className="space-y-8 max-w-5xl">
            {/* Walking Feasibility */}
            {portData.walking_feasibility && (
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3">
                <div className="flex items-center gap-2 font-display text-xl font-bold text-[#0C1B2A]">
                  <Navigation className="w-5 h-5 text-[#C58A46]" />
                  <span>Walking Access & Pedestrian Corridors</span>
                </div>
                <div className="text-xs font-mono text-[#C58A46] uppercase font-bold">
                  Rating: {portData.walking_feasibility.rating} • {portData.walking_feasibility.distance_to_center_km} km to historic core
                </div>
                <p className="text-xs text-[#5B6570] leading-relaxed">
                  {portData.walking_feasibility.description}
                </p>
              </div>
            )}

            {/* Public Transport & Rail */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {transportData.public_transport?.rail_stations && (
                <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3">
                  <div className="flex items-center gap-2 font-display text-lg font-bold text-[#0C1B2A]">
                    <Train className="w-5 h-5 text-emerald-700" />
                    <span>Railway Stations</span>
                  </div>
                  {transportData.public_transport.rail_stations.map((rail: any) => (
                    <div key={rail.id} className="text-xs space-y-1">
                      <div className="font-bold text-[#0C1B2A]">{rail.name}</div>
                      <p className="text-[#5B6570]">{rail.description}</p>
                      <div className="text-[11px] text-slate-400 font-mono">Distance: {rail.distance_meters ? `${rail.distance_meters}m` : rail.distance_minutes}</div>
                    </div>
                  ))}
                </div>
              )}

              {transportData.public_transport?.metro_stations && (
                <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3">
                  <div className="flex items-center gap-2 font-display text-lg font-bold text-[#0C1B2A]">
                    <Bus className="w-5 h-5 text-sky-700" />
                    <span>Metro & Subway Stations</span>
                  </div>
                  {transportData.public_transport.metro_stations.map((metro: any) => (
                    <div key={metro.id} className="text-xs space-y-1">
                      <div className="font-bold text-[#0C1B2A]">{metro.name}</div>
                      <p className="text-[#5B6570]">{metro.description}</p>
                      <div className="text-[11px] text-slate-400 font-mono">Walk: ~{metro.distance_minutes} minutes</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Taxi & Rideshare */}
            {transportData.taxi_services && (
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4">
                <div className="flex items-center gap-2 font-display text-lg font-bold text-[#0C1B2A]">
                  <Car className="w-5 h-5 text-amber-700" />
                  <span>Licensed Taxi Services & Official Fares</span>
                </div>
                <div className="text-xs text-[#5B6570]">
                  Official Dispatch: <strong className="text-[#0C1B2A]">{transportData.taxi_services.booking_phone}</strong>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">City Center Fare</span>
                    <span className="font-bold text-[#0C1B2A] text-sm">€{transportData.taxi_services.pricing_guidelines?.fare_to_piazza_de_ferrari_eur || transportData.taxi_services.pricing_guidelines?.fare_to_center_eur || "15.00"}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Airport Fare</span>
                    <span className="font-bold text-[#0C1B2A] text-sm">€{transportData.taxi_services.pricing_guidelines?.fare_to_airport_eur || "25.00 - 35.00"}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Duration</span>
                    <span className="font-bold text-[#0C1B2A] text-sm">~{transportData.taxi_services.pricing_guidelines?.duration_to_center_minutes || "10"} min</span>
                  </div>
                </div>
              </div>
            )}

            {/* Airport Connection */}
            {transportData.airport_connections && (
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4">
                <div className="flex items-center gap-2 font-display text-lg font-bold text-[#0C1B2A]">
                  <Plane className="w-5 h-5 text-indigo-700" />
                  <span>Airport Transfers: {transportData.airport_connections.airport_name}</span>
                </div>
                <div className="text-xs text-[#5B6570]">
                  Distance from cruise terminal: <strong>{transportData.airport_connections.distance_km} km</strong>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(transportData.airport_connections.transit_options || []).map((opt: any, idx: number) => (
                    <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200/60 text-xs space-y-1">
                      <div className="font-bold text-[#0C1B2A] text-sm">{opt.mode}</div>
                      {opt.route && <p className="text-[#5B6570]">{opt.route}</p>}
                      <div className="flex items-center justify-between text-slate-500 pt-1 font-mono text-[11px]">
                        <span>Duration: {opt.duration_minutes} min</span>
                        <span className="text-[#C58A46] font-bold">Cost: {opt.cost_eur ? `€${opt.cost_eur}` : "Standard Fare"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: EMERGENCY & MEDICAL */}
        {activeTab === "medical-emergency" && (
          <div className="space-y-8 max-w-5xl">
            {/* Emergency Phone Dispatch */}
            {emergencyData?.emergency_numbers && (
              <div className="space-y-4">
                <h3 className="font-display text-xl font-bold text-[#0C1B2A] flex items-center gap-2">
                  <PhoneCall className="w-5 h-5 text-rose-600" />
                  <span>Emergency Dispatch & Safety Numbers</span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {emergencyData.emergency_numbers.map((em: any) => (
                    <div key={em.id} className="p-5 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                      <span className="eyebrow-tag">{em.name}</span>
                      <div className="font-display text-2xl font-bold text-rose-700 font-mono">{em.number}</div>
                      <p className="text-xs text-[#5B6570] leading-relaxed">{em.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Medical Facilities & Hospitals */}
            {medicalData?.medical_facilities && (
              <div className="space-y-4 pt-4">
                <h3 className="font-display text-xl font-bold text-[#0C1B2A] flex items-center gap-2">
                  <HeartPulse className="w-5 h-5 text-emerald-600" />
                  <span>Hospitals, Trauma Centers & Emergency Care</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {medicalData.medical_facilities.map((hosp: any) => (
                    <div key={hosp.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3 shadow-xs">
                      <div className="flex items-center justify-between">
                        <span className="eyebrow-tag">{hosp.type || "Hospital"}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                          24/7 ER
                        </span>
                      </div>
                      <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{hosp.name}</h4>
                      <p className="text-xs text-rose-900 font-semibold bg-rose-50 p-2 rounded-lg border border-rose-200">
                        {hosp.emergency_department}
                      </p>
                      <div className="text-xs text-[#5B6570] space-y-1">
                        <div><strong>Address:</strong> {hosp.address}</div>
                        <div><strong>Phone:</strong> <span className="font-mono text-[#0C1B2A] font-semibold">{hosp.phone}</span></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: CLIMATE & WEATHER */}
        {activeTab === "weather" && weatherData && (
          <div className="space-y-6 max-w-5xl">
            <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
              <div className="flex items-center gap-2 font-display text-xl font-bold text-[#0C1B2A]">
                <Sun className="w-5 h-5 text-[#C58A46]" />
                <span>Mediterranean Climate Profile</span>
              </div>
              <p className="text-xs text-[#5B6570]">
                Climate Classification: <strong className="text-[#0C1B2A]">{weatherData.climate_profile?.climate_type || "Mediterranean"}</strong>
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {weatherData.climate_profile?.seasonal_patterns && Object.entries(weatherData.climate_profile.seasonal_patterns).map(([season, info]: [string, any]) => (
                <div key={season} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3 shadow-xs">
                  <span className="eyebrow-tag block uppercase">{season.replace("_", " & ")}</span>
                  <div className="font-display text-lg font-bold text-[#0C1B2A]">{info.months}</div>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{info.description}</p>
                  {info.avg_high_celsius && (
                    <div className="pt-2 border-t border-slate-100 text-xs font-mono text-[#C58A46] font-bold">
                      Avg High: {info.avg_high_celsius}°C ({info.avg_high_fahrenheit}°F)
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: SUSTAINABILITY & SHORE POWER */}
        {activeTab === "sustainability" && sustainabilityData && (
          <div className="space-y-6 max-w-5xl">
            <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3">
              <div className="flex items-center gap-2 font-display text-xl font-bold text-[#0C1B2A]">
                <Zap className="w-5 h-5 text-emerald-600" />
                <span>Onshore Power Supply (OPS) & Shore-to-Ship Electrification</span>
              </div>
              <div className="text-xs font-mono text-emerald-800 font-semibold">
                Status: {sustainabilityData.shore_power_ops?.status}
              </div>
            </div>

            {sustainabilityData.shore_power_ops?.current_operational && (
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
                <span className="eyebrow-tag">CURRENT OPERATIONAL BERTH</span>
                <h4 className="font-display text-lg font-bold text-[#0C1B2A]">
                  {sustainabilityData.shore_power_ops.current_operational.terminal}
                </h4>
                <p className="text-xs text-[#5B6570] leading-relaxed">
                  {sustainabilityData.shore_power_ops.current_operational.capacity}
                </p>
              </div>
            )}

            {sustainabilityData.shore_power_ops?.cruise_infrastructure_pipeline && (
              <div className="p-6 bg-[#0C1B2A] text-white rounded-3xl space-y-4 shadow-xl">
                <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-[#C58A46] block">
                  CRUISE INFRASTRUCTURE PIPELINE
                </span>
                <h4 className="font-display text-xl font-bold">
                  High-Voltage Electrification: {sustainabilityData.shore_power_ops.cruise_infrastructure_pipeline.terminals?.join(", ")}
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {sustainabilityData.shore_power_ops.cruise_infrastructure_pipeline.technical_details}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs border-t border-white/10">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">Investment</span>
                    <span className="font-bold text-white">€{(sustainabilityData.shore_power_ops.cruise_infrastructure_pipeline.project_investment_eur / 1000000).toFixed(1)}M</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">Contractor</span>
                    <span className="font-bold text-white">{sustainabilityData.shore_power_ops.cruise_infrastructure_pipeline.contractor}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">Commissioning</span>
                    <span className="font-bold text-[#C58A46]">{sustainabilityData.shore_power_ops.cruise_infrastructure_pipeline.scheduled_commissioning}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
