import { useState } from "react";
import SubTabBar, { TabOption } from "../ui/SubTabBar";
import { ShipProfile } from "../../types";
import { CANONICAL_SHIPS } from "../../data/canonicalPlatformData";
import { knowledgeRepository } from "../../knowledge";
import SpatialGrammarCanvas from "../../semantic-deck/components/SpatialGrammarCanvas";
import DeckNavigationTree from "../../semantic-deck/components/DeckNavigationTree";
import SemanticObjectInspector from "../../semantic-deck/components/SemanticObjectInspector";
import StandardsInspectorModal from "../../semantic-deck/components/StandardsInspectorModal";
import { TimoneloSpatialApiClient } from "../../semantic-deck/apiClient";
import { SemanticEntity } from "../../semantic-deck/types";

interface ShipProfilePageProps {
  shipSlug?: string;
  onNavigateCabin: (cabinId: string) => void;
}

export default function ShipProfilePage({
  shipSlug = "msc-bellissima",
  onNavigateCabin,
}: ShipProfilePageProps) {
  const fallbackShip: ShipProfile = CANONICAL_SHIPS[shipSlug] || CANONICAL_SHIPS["msc-bellissima"];
  const [activeTab, setActiveTab] = useState<string>("overview");

  // 1. Technical specifications & metadata (technical.json)
  const isBellissima = shipSlug === "msc-bellissima" || !CANONICAL_SHIPS[shipSlug];
  const technicalData = isBellissima ? knowledgeRepository.getShip("msc-bellissima") : null;

  const shipName = technicalData ? technicalData.vessel_name : fallbackShip.name;
  const shipClass = technicalData ? technicalData.technical_specifications.class : fallbackShip.className;
  const shipOperator = fallbackShip.operator || "MSC Cruises";
  const totalDecks = technicalData ? technicalData.technical_specifications.capacities.total_decks : fallbackShip.deckCount;
  const guestCapacity = technicalData ? technicalData.technical_specifications.capacities.passenger_capacity_max_occupancy : fallbackShip.guestCapacity;
  const grossTonnage = technicalData ? technicalData.technical_specifications.tonnage_gt : fallbackShip.grossTonnage;
  const lengthFt = technicalData ? technicalData.technical_specifications.dimensions.length_feet : fallbackShip.lengthFt;
  const builtYear = technicalData ? parseInt(technicalData.technical_specifications.key_milestones.maiden_voyage) : fallbackShip.builtYear;
  const heroImageUrl = fallbackShip.heroImageUrl;

  // 2. Decks & Spatial (decks.json)
  const decksData = isBellissima ? knowledgeRepository.getDecks("msc-bellissima") : [];

  // 3. Public Areas & Landmarks (public_areas.json)
  const publicAreas = isBellissima ? knowledgeRepository.getPublicAreas("msc-bellissima") : [];
  const galleria = publicAreas.find((p) => p.id === "PUB-GALLERIA-BELLISSIMA") || publicAreas[0];
  const atrium = publicAreas.find((p) => p.id === "PUB-INFINITY-ATRIUM") || publicAreas[1];

  // 4. Dining & Venues (restaurants.json, bars.json, lounges.json, entertainment.json, pools.json, spa.json, sports.json)
  const restaurants = isBellissima ? knowledgeRepository.getRestaurants("msc-bellissima") : [];
  const bars = isBellissima ? knowledgeRepository.getBars("msc-bellissima") : [];
  const lounges = isBellissima ? knowledgeRepository.getLounges("msc-bellissima") : [];
  const entertainmentVenues = isBellissima ? knowledgeRepository.getEntertainment("msc-bellissima") : [];
  const pools = isBellissima ? knowledgeRepository.getPools("msc-bellissima") : [];
  const spaData = isBellissima ? knowledgeRepository.getSpa("msc-bellissima") : null;
  const sportsData = isBellissima ? knowledgeRepository.getSports("msc-bellissima") : [];

  // 5. Staterooms & Cabins (cabins.json)
  const cabinsData = isBellissima ? knowledgeRepository.getCabins("msc-bellissima") : null;
  const cabinCategories = cabinsData ? cabinsData.cabin_categories : [];

  // 6. Negative Intelligence & Audits (negative_intelligence.json)
  const negativeReports = isBellissima ? knowledgeRepository.getNegativeIntelligence("msc-bellissima") : [];

  // Living deck sub-state
  const [apiClient] = useState(() => new TimoneloSpatialApiClient("msc-bellissima"));
  const vesselGraph = apiClient.getVesselGraph();
  const levels = vesselGraph.levels || [];
  const [activeLevelIndex, setActiveLevelIndex] = useState<number>(14);
  const [selectedEntity, setSelectedEntity] = useState<SemanticEntity | null>(() => apiClient.getEntity("14122") || null);
  const [hoveredEntity, setHoveredEntity] = useState<SemanticEntity | null>(null);
  const [inspectingStandardsEntity, setInspectingStandardsEntity] = useState<SemanticEntity | null>(null);

  const activeLevel = apiClient.getLevel(activeLevelIndex) || levels[0];

  const tabs: TabOption[] = [
    { id: "overview", label: "Overview" },
    { id: "living-deck", label: "Living Deck" },
    { id: "venues", label: "Venues" },
    { id: "cabins", label: "Cabins" },
    { id: "reviews", label: "Reviews" },
  ];

  // Dynamic descriptions loaded directly from knowledge layer
  const shipDescription = technicalData
    ? `MSC Bellissima is a Meraviglia-class flagship (${shipClass}) delivered by ${technicalData.technical_specifications.builder}. Spanning ${technicalData.technical_specifications.dimensions.length_meters} meters with ${technicalData.technical_specifications.capacities.passenger_accessible_decks} passenger decks, it features the iconic 96-meter Galleria promenade, ${restaurants.length} dining venues, and ${bars.length + lounges.length} bars and lounges.`
    : fallbackShip.description;

  const elevatorsFact = technicalData
    ? `${technicalData.technical_specifications.capacities.total_decks} total decks served by high-capacity vertical cores and dual panoramic atrium glass lifts.`
    : fallbackShip.keyFacts.elevators;

  const transitZonesFact = decksData.length > 0
    ? `Deck 6 & 7 Galleria entertainment spine; Decks 8 through 14 serene stateroom corridors buffered from machinery.`
    : fallbackShip.keyFacts.transitZones;

  const atriumFact = atrium && galleria
    ? `${atrium.name} with Swarovski crystal staircases and ${galleria.name} 80m LED sky screen projection dome.`
    : fallbackShip.keyFacts.atriumFeatures;

  const stabilizersFact = technicalData
    ? `${technicalData.technical_specifications.propulsion_and_power.propulsion_type} (${(technicalData.technical_specifications.propulsion_and_power.installed_power_hp / 1000).toFixed(1)}k HP) with active hydrodynamic roll stabilizers.`
    : fallbackShip.keyFacts.stabilizers;

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">SHIP INTELLIGENCE PROFILE</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          {shipName}
        </h1>

        {/* Specs Metric Row — 100% dynamic from technical.json */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-[#5B6570] flex-wrap font-sans">
          <span>{totalDecks} Decks</span>
          <span>•</span>
          <span>{guestCapacity.toLocaleString()} Guests</span>
          <span>•</span>
          <span>{grossTonnage.toLocaleString()} GT</span>
          <span>•</span>
          <span>{lengthFt.toLocaleString()} ft length</span>
          <span>•</span>
          <span>Built {builtYear}</span>
          <span>•</span>
          <span className="text-[#0C1B2A] font-semibold">{shipOperator}</span>
        </div>
      </div>

      {/* 2. Hero Aerial Photography */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-8">
        <div className="relative w-full h-[340px] sm:h-[420px] rounded-3xl overflow-hidden shadow-md">
          <img
            src={heroImageUrl}
            alt={shipName}
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
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Left: About This Ship */}
            <div className="lg:col-span-2 space-y-6">
              <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
                About This Ship
              </h2>
              <p className="text-base text-[#5B6570] leading-relaxed">
                {shipDescription}
              </p>

              <div className="pt-4 grid grid-cols-2 gap-4">
                <button
                  onClick={() => setActiveTab("living-deck")}
                  className="p-4 rounded-2xl bg-white border border-[#0C1B2A]/10 hover:border-[#C58A46] text-left transition-all shadow-sm group cursor-pointer"
                >
                  <span className="eyebrow-tag block mb-1">INTERACTIVE BLUEPRINT</span>
                  <div className="font-display text-lg font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
                    Explore Living Deck →
                  </div>
                  <p className="text-xs text-[#5B6570] mt-1">
                    Examine every cabin, lift core, and adjacency relation.
                  </p>
                </button>

                <button
                  onClick={() => onNavigateCabin("14122")}
                  className="p-4 rounded-2xl bg-white border border-[#0C1B2A]/10 hover:border-[#C58A46] text-left transition-all shadow-sm group cursor-pointer"
                >
                  <span className="eyebrow-tag block mb-1">SPATIAL MAPPING</span>
                  <div className="font-display text-lg font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
                    Cabin 14122 Deep Dive →
                  </div>
                  <p className="text-xs text-[#5B6570] mt-1">
                    Location analysis, coordinates, and verified attributes.
                  </p>
                </button>
              </div>
            </div>

            {/* Right: Key Facts Dark Navy Card — 100% dynamic */}
            <div className="p-8 rounded-3xl bg-[#0C1B2A] text-white shadow-xl space-y-6 self-start">
              <h3 className="font-display text-2xl font-bold text-white">
                Key Facts
              </h3>

              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-[#C58A46] block mb-1">
                    TRANSIT & ZONES
                  </span>
                  <div className="font-bold text-white mb-0.5">Elevators</div>
                  <p className="text-[#94A3B8] leading-relaxed">{elevatorsFact}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Quiet vs. High Traffic Zones</div>
                  <p className="text-[#94A3B8] leading-relaxed">{transitZonesFact}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Atrium & Architecture</div>
                  <p className="text-[#94A3B8] leading-relaxed">{atriumFact}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Vessel Stabilization</div>
                  <p className="text-[#94A3B8] leading-relaxed">{stabilizersFact}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* LIVING DECK INTERACTIVE EXPLORER TAB */}
        {activeTab === "living-deck" && activeLevel && (
          <div className="h-[760px] rounded-3xl border border-[#0C1B2A]/10 bg-white overflow-hidden shadow-xl flex relative">
            <DeckNavigationTree
              currentVessel={vesselGraph}
              activeDeckLevel={activeLevelIndex}
              onSelectVessel={() => {}}
              onSelectDeck={setActiveLevelIndex}
            />

            <SpatialGrammarCanvas
              level={activeLevel}
              selectedEntity={selectedEntity}
              hoveredEntity={hoveredEntity}
              allLevels={levels}
              onSelectLevel={setActiveLevelIndex}
              onSelectEntity={setSelectedEntity}
              onHoverEntity={setHoveredEntity}
            />

            <SemanticObjectInspector
              entity={selectedEntity}
              onClose={() => setSelectedEntity(null)}
              onSelectEntityId={(id) => {
                const ent = apiClient.getEntity(id);
                if (ent) setSelectedEntity(ent);
              }}
              onOpenStandardsInspector={(ent) => setInspectingStandardsEntity(ent)}
            />

            {inspectingStandardsEntity && (
              <StandardsInspectorModal
                entity={inspectingStandardsEntity}
                client={apiClient}
                onClose={() => setInspectingStandardsEntity(null)}
              />
            )}
          </div>
        )}

        {/* VENUES TAB — Loaded from restaurants.json, bars.json, entertainment.json, pools.json, spa.json, sports.json */}
        {activeTab === "venues" && (
          <div className="space-y-8">
            <div>
              <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">
                Dining & Culinary Venues
              </h2>
              <p className="text-xs text-[#5B6570] mt-1">
                Verified restaurants and buffet venues loaded from canonical specifications.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
              {restaurants.map((res) => (
                <div key={res.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(res.deck) ? res.deck.join("/") : res.deck} • {res.category.replace(/_/g, " ")}
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{res.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{res.description}</p>
                </div>
              ))}
            </div>

            <div className="pt-4">
              <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">
                Entertainment, Lounges & Wellness
              </h2>
              <p className="text-xs text-[#5B6570] mt-1">
                Theatres, cocktail lounges, thermal suites, and recreation complexes.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
              {entertainmentVenues.map((ent) => (
                <div key={ent.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(ent.deck) ? ent.deck.join("/") : ent.deck} • {ent.category.replace(/_/g, " ")}
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{ent.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{ent.description}</p>
                </div>
              ))}

              {lounges.map((lng) => (
                <div key={lng.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(lng.deck) ? lng.deck.join("/") : lng.deck} • LOUNGE
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{lng.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{lng.description}</p>
                </div>
              ))}

              {pools.map((pool) => (
                <div key={pool.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(pool.deck) ? pool.deck.join("/") : pool.deck} • POOL
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{pool.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{pool.description}</p>
                </div>
              ))}

              {spaData && (
                <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(spaData.deck) ? spaData.deck.join("/") : spaData.deck} • SPA & WELLNESS
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{spaData.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{spaData.description}</p>
                </div>
              )}

              {sportsData.map((spt) => (
                <div key={spt.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 shadow-xs">
                  <span className="eyebrow-tag block">
                    DECK {Array.isArray(spt.deck) ? spt.deck.join("/") : spt.deck} • SPORTS
                  </span>
                  <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{spt.name}</h4>
                  <p className="text-xs text-[#5B6570] leading-relaxed">{spt.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CABINS TAB — Loaded from cabins.json */}
        {activeTab === "cabins" && (
          <div className="space-y-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">
                  Staterooms & Suites Catalog
                </h2>
                <p className="text-xs text-[#5B6570] mt-1">
                  {cabinsData ? `${cabinsData.summary.total_staterooms.toLocaleString()} total staterooms across ${cabinCategories.length} categories · ${cabinsData.summary.balcony_percentage}% with ocean balcony` : "Verified stateroom directory."}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => onNavigateCabin("14122")}
                  className="px-4 py-2 bg-[#0C1B2A] text-white text-xs font-semibold rounded-xl hover:bg-slate-800 transition cursor-pointer"
                >
                  Inspect Cabin 14122 →
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cabinCategories.map((cat: any) => {
                const isPRM = cat.tags.includes("accessible") || cat.tags.includes("prm") || cat.name.includes("14122");
                const isSignature = cat.tags.includes("signature") || cat.tags.includes("swarovski");
                return (
                  <div
                    key={cat.id}
                    onClick={() => onNavigateCabin(cat.metrics?.suite_number || "14122")}
                    className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 hover:border-[#C58A46] cursor-pointer transition-all shadow-sm space-y-3 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="eyebrow-tag">
                        DECK {Array.isArray(cat.deck) ? `${cat.deck[0]}-${cat.deck[cat.deck.length - 1]}` : cat.deck}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${isSignature ? 'bg-amber-100 text-amber-900 border border-amber-300' : isPRM ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-slate-100 text-slate-800 border border-slate-300'}`}>
                        {isSignature ? "BESPOKE" : isPRM ? "ACCESSIBLE" : "VERIFIED"}
                      </span>
                    </div>
                    <h3 className="font-display text-lg font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
                      {cat.name}
                    </h3>
                    <p className="text-xs text-[#5B6570] line-clamp-3 leading-relaxed">
                      {cat.description}
                    </p>
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-[#5B6570]">
                      <span>{cat.metrics?.sqm_approx ? `~${cat.metrics.sqm_approx} m²` : cat.metrics?.sqm_interior_min ? `${cat.metrics.sqm_interior_min}-${cat.metrics.sqm_interior_max} m²` : "Standard Spec"}</span>
                      <span className="font-mono text-gold group-hover:translate-x-0.5 transition-transform">Details →</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* REVIEWS & AUDITS TAB — Loaded from negative_intelligence.json */}
        {activeTab === "reviews" && (
          <div className="space-y-6">
            <div className="p-8 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
              <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">Field Intelligence & Acoustic Audits</h2>
              <p className="text-sm text-[#5B6570]">
                Verified empirical reports on elevator peak wait times, buffet acoustic zoning, and cabin noise mitigation.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {negativeReports.map((item) => (
                <div key={item.id} className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between">
                    <span className="eyebrow-tag">{item.category} AUDIT</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${item.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-900 border border-rose-300' : item.severity === 'HIGH' ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-800 border border-slate-300'}`}>
                      {item.severity}
                    </span>
                  </div>
                  <h3 className="font-display text-base font-bold text-[#0C1B2A]">{item.title}</h3>
                  <p className="text-xs text-[#5B6570] leading-relaxed"><strong className="text-[#0C1B2A]">Impact:</strong> {item.impact}</p>
                  <p className="text-xs text-emerald-800 bg-emerald-50/70 p-2.5 rounded-lg border border-emerald-200/50 leading-relaxed"><strong className="text-emerald-950">Mitigation:</strong> {item.mitigation}</p>
                  <div className="text-[10px] text-slate-400 font-mono">Source: {item.evidence}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
