import { useState, useMemo } from 'react';
import {
  Ship,
  Search,
  Compass,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  X,
  AlertCircle,
  MapPin,
} from 'lucide-react';
import {
  SpatialPassengerViewModel,
  SpatialEntityViewModel,
  UnmappedEntityViewModel,
} from './types';
import DeckCanvas from './DeckCanvas';

interface ShipOverviewProps {
  viewModel: SpatialPassengerViewModel;
  onSelectDeck?: (deckNumber: number) => void;
  className?: string;
}

export default function ShipOverview({
  viewModel,
  onSelectDeck,
  className = '',
}: ShipOverviewProps) {
  const [selectedDeckNumber, setSelectedDeckNumber] = useState<number>(
    viewModel.selectedDeck.deckNumber
  );
  const [selectedEntity, setSelectedEntity] = useState<
    SpatialEntityViewModel | UnmappedEntityViewModel | null
  >(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isTrustDetailsOpen, setIsTrustDetailsOpen] = useState(false);
  const [isUnmappedSectionOpen, setIsUnmappedSectionOpen] = useState(false);

  const handleDeckClick = (deckNumber: number, hasGeometry: boolean) => {
    if (!hasGeometry) return;
    setSelectedDeckNumber(deckNumber);
    setSelectedEntity(null);
    if (onSelectDeck) {
      onSelectDeck(deckNumber);
    }
  };

  // Filter search results across admitted mapped entities and admitted unmapped venues
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return { mappedHits: [], unmappedHits: [] };
    const query = searchQuery.toLowerCase().trim();

    const mappedHits = viewModel.spatialEntities
      .filter((e) => e.name.toLowerCase().includes(query))
      .slice(0, 8);

    const unmappedHits = viewModel.unmappedEntities
      .filter((u) => u.name.toLowerCase().includes(query))
      .slice(0, 8);

    return { mappedHits, unmappedHits };
  }, [searchQuery, viewModel.spatialEntities, viewModel.unmappedEntities]);

  const hasSearchHits =
    searchResults.mappedHits.length > 0 || searchResults.unmappedHits.length > 0;

  const currentDeckEntities = useMemo(() => {
    return viewModel.spatialEntities.filter((e) => e.deckNumber === selectedDeckNumber);
  }, [viewModel.spatialEntities, selectedDeckNumber]);

  return (
    <div className={`w-full max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-6 sm:space-y-8 ${className}`}>
      {/* 1. Ship Header & Status */}
      <section className="bg-white rounded-3xl p-6 sm:p-8 border border-[#0C1B2A]/10 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-[#C58A46]/10 text-[#C58A46]">
              <Ship className="w-4 h-4" />
            </span>
            <span className="text-xs font-mono font-semibold tracking-wider text-[#C58A46] uppercase">
              {viewModel.shipName}
            </span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200/60">
            <Compass className="w-3.5 h-3.5 text-[#C58A46]" />
            <span>Spatial Overview</span>
          </div>
        </div>

        <div className="space-y-1">
          <h1 className="text-2xl sm:text-4xl font-display font-bold text-[#0C1B2A] tracking-tight">
            Ship Deck Overview
          </h1>
          <p className="text-sm text-[#5B6570] font-medium">
            Explore verified deck layouts and stateroom locations.
          </p>
        </div>

        {/* Deck Availability Status Bar */}
        <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-emerald-800 bg-emerald-50 px-3 py-1 rounded-xl border border-emerald-200/50">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-semibold">Deck 14 available</span>
          </div>
          <div className="text-slate-500 text-xs">
            <span>More deck views are not available yet.</span>
          </div>
        </div>
      </section>

      {/* 2. Deck Selector Bar */}
      <section className="space-y-2">
        <div className="flex items-center justify-between px-1">
          <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase">
            SELECT DECK
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            {viewModel.trustSummary.mappedDecksCount} of {viewModel.trustSummary.totalDecksCount} deck mapped
          </span>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
          {viewModel.availableDecks.map((deck) => {
            const isSelected = deck.deckNumber === selectedDeckNumber;
            const isAvailable = deck.hasSpatialGeometry;

            return (
              <button
                key={deck.deckNumber}
                onClick={() => handleDeckClick(deck.deckNumber, isAvailable)}
                disabled={!isAvailable}
                className={`min-h-[44px] min-w-[44px] px-4 py-2 rounded-2xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-2 border ${
                  isSelected
                    ? 'bg-[#0C1B2A] text-white border-[#0C1B2A] shadow-md'
                    : isAvailable
                    ? 'bg-white text-[#0C1B2A] border-slate-200 hover:bg-slate-50 cursor-pointer'
                    : 'bg-slate-100 text-slate-400 border-slate-200/40 cursor-not-allowed opacity-75'
                }`}
                title={isAvailable ? `View ${deck.deckName}` : 'Spatial view not available yet'}
              >
                <span>{deck.deckName}</span>
                {!isAvailable && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200 text-slate-500">
                    Not mapped
                  </span>
                )}
                {isAvailable && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* 3. Search Bar: "Find on ship" */}
      <section className="space-y-2 relative">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Find on ship (e.g. 14122, vertical core...)"
            aria-label="Find on ship"
            className="w-full bg-white pl-11 pr-10 py-3.5 rounded-2xl border border-[#0C1B2A]/10 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#C58A46]/30 shadow-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-slate-600 rounded-full cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {hasSearchHits && searchQuery && (
          <div className="absolute top-full left-0 right-0 z-20 mt-1.5 bg-white rounded-2xl border border-slate-200 shadow-xl max-h-72 overflow-y-auto p-2 space-y-1">
            {searchResults.mappedHits.map((hit) => (
              <button
                key={hit.id}
                onClick={() => {
                  setSelectedEntity(hit);
                  if (hit.deckNumber !== selectedDeckNumber) {
                    setSelectedDeckNumber(hit.deckNumber);
                  }
                  setSearchQuery('');
                }}
                className="w-full text-left p-3 rounded-xl hover:bg-slate-50 flex items-center justify-between text-xs transition-colors cursor-pointer"
              >
                <div>
                  <span className="font-semibold text-[#0C1B2A] block">{hit.name}</span>
                  <span className="text-[11px] text-slate-500">
                    Deck {hit.deckNumber} • {hit.categoryLabel}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/50">
                  Mapped on Deck {hit.deckNumber}
                </span>
              </button>
            ))}

            {searchResults.unmappedHits.map((hit) => (
              <button
                key={hit.id}
                onClick={() => {
                  setSelectedEntity(hit);
                  setSearchQuery('');
                }}
                className="w-full text-left p-3 rounded-xl hover:bg-slate-50 flex items-center justify-between text-xs transition-colors cursor-pointer"
              >
                <div>
                  <span className="font-semibold text-[#0C1B2A] block">{hit.name}</span>
                  <span className="text-[11px] text-slate-500">
                    Deck {hit.deckNumber} • {hit.categoryLabel}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200/50">
                  Location not mapped yet
                </span>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* 4. Selected POI / Cabin Card */}
      {selectedEntity && (
        <section className="bg-white rounded-2xl p-5 sm:p-6 border border-[#C58A46]/30 shadow-md animate-fadeIn relative">
          <button
            onClick={() => setSelectedEntity(null)}
            aria-label="Close details"
            className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono font-bold text-[#C58A46] uppercase tracking-wider flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  DECK {selectedEntity.deckNumber}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                  {selectedEntity.categoryLabel}
                </span>
              </div>
              <h3 className="text-xl font-display font-bold text-[#0C1B2A]">
                {selectedEntity.name}
              </h3>
            </div>

            <div className="text-left sm:text-right space-y-1">
              <div className="flex items-center sm:justify-end gap-1.5">
                {selectedEntity.status === 'mapped' ? (
                  <span className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200/50">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Mapped on official deck plan
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs text-amber-700 font-semibold bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200/50">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Location not mapped yet
                  </span>
                )}
              </div>
              {'provenanceLabel' in selectedEntity && (
                <p className="text-[11px] text-slate-400 font-mono">
                  {selectedEntity.provenanceLabel}
                </p>
              )}
            </div>
          </div>
        </section>
      )}

      {/* 5. Interactive SVG Deck Canvas */}
      <section className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase">
            DECK VIEW
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            {currentDeckEntities.length} verified spaces
          </span>
        </div>

        <DeckCanvas
          deck={viewModel.selectedDeck}
          entities={currentDeckEntities}
          selectedEntityId={selectedEntity?.id || null}
          onSelectEntity={(entity) => setSelectedEntity(entity)}
        />
      </section>

      {/* 6. Unmapped Known Venues List (Only rendered if publication-admitted unmapped venues exist) */}
      {viewModel.unmappedEntities.length > 0 && (
        <section className="bg-white rounded-3xl p-6 sm:p-8 border border-[#0C1B2A]/10 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h2 className="text-sm font-bold text-[#0C1B2A]">
                Known Places on Other Decks
              </h2>
              <p className="text-xs text-[#5B6570]">
                These places are verified in ship records, but their precise coordinates are not mapped yet.
              </p>
            </div>

            <button
              onClick={() => setIsUnmappedSectionOpen(!isUnmappedSectionOpen)}
              className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-[#0C1B2A] transition-colors cursor-pointer shrink-0"
            >
              <span>{isUnmappedSectionOpen ? 'Hide' : 'View list'}</span>
              {isUnmappedSectionOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          {isUnmappedSectionOpen && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-100">
              {viewModel.unmappedEntities.map((venue) => (
                <div
                  key={venue.id}
                  onClick={() => setSelectedEntity(venue)}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-200 cursor-pointer space-y-1 transition-colors"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-[#0C1B2A]">
                    <span>{venue.name}</span>
                    <span className="text-[10px] font-mono text-[#C58A46]">Deck {venue.deckNumber}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>{venue.categoryLabel}</span>
                    <span className="text-[10px] text-amber-700">Location not mapped yet</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* 7. Trust & Spatial Governance */}
      <section className="bg-slate-50 rounded-3xl p-6 sm:p-8 border border-[#0C1B2A]/10 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-xl bg-emerald-100 text-emerald-800 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <div>
              <h2 className="text-sm font-bold text-[#0C1B2A]">
                {viewModel.trustSummary.statusBadge}
              </h2>
              <p className="text-xs text-[#5B6570]">
                {viewModel.trustSummary.sourceNotice}
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsTrustDetailsOpen(!isTrustDetailsOpen)}
            className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-full bg-white hover:bg-slate-100 text-xs font-semibold text-[#0C1B2A] border border-[#0C1B2A]/10 shadow-sm transition-colors cursor-pointer self-start sm:self-auto"
          >
            <span>Why do we know this?</span>
            {isTrustDetailsOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {isTrustDetailsOpen && (
          <div className="pt-4 mt-2 border-t border-slate-200/60 text-xs space-y-3 text-[#5B6570] animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-white rounded-xl p-3.5 border border-slate-200/40">
                <span className="font-semibold text-[#0C1B2A] block mb-1">Spatial Truth Policy</span>
                <p className="leading-relaxed">
                  Only reviewed, publication-approved spatial data derived from official source material is shown here. We never manufacture speculative shapes or infer walking paths.
                </p>
              </div>

              <div className="bg-white rounded-xl p-3.5 border border-slate-200/40">
                <span className="font-semibold text-[#0C1B2A] block mb-1">Coverage & Scope</span>
                <p className="leading-relaxed">
                  {viewModel.trustSummary.coverageNotice}. Additional decks are incorporated only when source drawings undergo evidence verification.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 text-[11px] text-slate-400 font-mono">
              <span>{viewModel.trustSummary.governanceNotice}</span>
              <span>{viewModel.trustSummary.admittedCabinsCount} verified staterooms on Deck 14</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
