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
  shipSlug = "msc-virtuosa",
  onNavigateCabin,
}: ShipProfilePageProps) {
  const ship: ShipProfile = CANONICAL_SHIPS[shipSlug] || CANONICAL_SHIPS["msc-virtuosa"];
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Dynamic knowledge layer data for venues and amenities
  const bellissimaRestaurants = knowledgeRepository.getRestaurants("msc-bellissima");
  const bellissimaEntertainment = knowledgeRepository.getEntertainment("msc-bellissima");
  const bellissimaLounges = knowledgeRepository.getLounges("msc-bellissima");

  const buffet = bellissimaRestaurants.find((r) => r.id === "RES-MARKETPLACE-BUFFET") || bellissimaRestaurants[0];
  const theatre = bellissimaEntertainment.find((e) => e.id === "ENT-LONDON-THEATRE") || bellissimaEntertainment[0];
  const carousel = bellissimaLounges.find((l) => l.id === "LNG-CAROUSEL-LOUNGE") || bellissimaLounges[0];

  // Living deck sub-state
  const [apiClient] = useState(() => new TimoneloSpatialApiClient(shipSlug === "msc-bellissima" ? "msc-bellissima" : "msc-bellissima"));
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

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none">
      {/* 1. Header Section */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <span className="eyebrow-tag block">SHIP INTELLIGENCE PROFILE</span>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          {ship.name}
        </h1>

        {/* Specs Metric Row */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-[#5B6570] flex-wrap font-sans">
          <span>{ship.deckCount} Decks</span>
          <span>•</span>
          <span>{ship.guestCapacity.toLocaleString()} Guests</span>
          <span>•</span>
          <span>{ship.grossTonnage.toLocaleString()} GT</span>
          <span>•</span>
          <span>{ship.lengthFt.toLocaleString()} ft length</span>
          <span>•</span>
          <span>Built {ship.builtYear}</span>
          <span>•</span>
          <span className="text-[#0C1B2A] font-semibold">{ship.operator}</span>
        </div>
      </div>

      {/* 2. Hero Aerial Photography */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-8">
        <div className="relative w-full h-[340px] sm:h-[420px] rounded-3xl overflow-hidden shadow-md">
          <img
            src={ship.heroImageUrl}
            alt={ship.name}
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
            {/* Left: About This Ship */}
            <div className="lg:col-span-2 space-y-6">
              <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A]">
                About This Ship
              </h2>
              <p className="text-base text-[#5B6570] leading-relaxed">
                {ship.description}
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
                  onClick={() => onNavigateCabin("12142")}
                  className="p-4 rounded-2xl bg-white border border-[#0C1B2A]/10 hover:border-[#C58A46] text-left transition-all shadow-sm group cursor-pointer"
                >
                  <span className="eyebrow-tag block mb-1">SPATIAL MAPPING</span>
                  <div className="font-display text-lg font-bold text-[#0C1B2A] group-hover:text-[#C58A46] transition-colors">
                    Cabin 12142 Deep Dive →
                  </div>
                  <p className="text-xs text-[#5B6570] mt-1">
                    Location analysis, coordinates, and verified attributes.
                  </p>
                </button>
              </div>
            </div>

            {/* Right: Key Facts Dark Navy Card */}
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
                  <p className="text-[#94A3B8] leading-relaxed">{ship.keyFacts.elevators}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Quiet vs. High Traffic Zones</div>
                  <p className="text-[#94A3B8] leading-relaxed">{ship.keyFacts.transitZones}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Atrium & Architecture</div>
                  <p className="text-[#94A3B8] leading-relaxed">{ship.keyFacts.atriumFeatures}</p>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="font-bold text-white mb-0.5">Vessel Stabilization</div>
                  <p className="text-[#94A3B8] leading-relaxed">{ship.keyFacts.stabilizers}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Living Deck Interactive Explorer Tab */}
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

        {/* Venues Tab */}
        {activeTab === "venues" && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">
              Dining & Entertainment Venues
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
                <span className="eyebrow-tag block">DECK {buffet.deck} • BUFFET</span>
                <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{buffet.name}</h4>
                <p className="text-xs text-[#5B6570]">{buffet.description}</p>
              </div>
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
                <span className="eyebrow-tag block">DECK {Array.isArray(theatre.deck) ? theatre.deck.join("/") : theatre.deck} • THEATRE</span>
                <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{theatre.name}</h4>
                <p className="text-xs text-[#5B6570]">{theatre.description}</p>
              </div>
              <div className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2">
                <span className="eyebrow-tag block">DECK {carousel.deck} • ENTERTAINMENT</span>
                <h4 className="font-display text-lg font-bold text-[#0C1B2A]">{carousel.name}</h4>
                <p className="text-xs text-[#5B6570]">{carousel.description}</p>
              </div>
            </div>
          </div>
        )}

        {/* Cabins Tab */}
        {activeTab === "cabins" && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">
              Staterooms & Suites
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                onClick={() => onNavigateCabin("12142")}
                className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 hover:border-[#C58A46] cursor-pointer transition-all shadow-sm space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="eyebrow-tag">DECK 12 • MIDSHIP</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-900 border border-amber-300">
                    KNOWN
                  </span>
                </div>
                <h3 className="font-display text-xl font-bold text-[#0C1B2A]">Cabin 12142 (Deluxe Balcony)</h3>
                <p className="text-xs text-[#5B6570]">17m² + 4m² private veranda • Port Side • Structurally quiet zone</p>
              </div>

              <div
                onClick={() => onNavigateCabin("14122")}
                className="p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 hover:border-[#C58A46] cursor-pointer transition-all shadow-sm space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="eyebrow-tag">DECK 14 • STARBOARD</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                    VERIFIED
                  </span>
                </div>
                <h3 className="font-display text-xl font-bold text-[#0C1B2A]">Cabin 14122 (Deluxe Interior)</h3>
                <p className="text-xs text-[#5B6570]">PRM Accessible (H) • 16m² • Directly below Marketplace quiet zone</p>
              </div>
            </div>
          </div>
        )}

        {/* Reviews Tab */}
        {activeTab === "reviews" && (
          <div className="p-8 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-4">
            <h2 className="font-display text-2xl font-bold text-[#0C1B2A]">Passenger Reviews & Verifications</h2>
            <p className="text-sm text-[#5B6570]">Aggregated from 50,000+ verified cruise traveler reports across acoustic ratings, bed comfort, and transit times.</p>
          </div>
        )}
      </div>
    </div>
  );
}
