import React, { useState } from 'react';
import {
  BookOpen,
  Anchor,
  Sparkles,
  Award,
  Heart,
  Compass,
  Ship,
  MapPin,
  Calendar,
  CheckCircle2,
  Clock,
  ChevronRight,
  Bookmark,
  Footprints,
} from 'lucide-react';
import {
  SHIPMATE_PROFILE_DATA,
  type TravellerShipmateProfileData,
  type CompletedVoyageLogData,
} from '../generated/shipmate_memory';

export const ShipLogbookDashboard: React.FC = () => {
  const data: TravellerShipmateProfileData = SHIPMATE_PROFILE_DATA;
  const [selectedVoyageId, setSelectedVoyageId] = useState<string>('voy:bellissima-asia-2026');

  const activeVoyage: CompletedVoyageLogData =
    data.voyageHistory.find((v) => v.voyageId === selectedVoyageId) || data.voyageHistory[0];

  return (
    <section id="shipmate-logbook" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <BookOpen className="w-3.5 h-3.5 text-amber-700" />
            Shipmate Memory · Chapter V Sprint 01
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Bridge Officer Tim erinnert sich an jede Reise.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Keine privaten Details, sondern pure Reiselogistik: Ihre bevorzugten Sonnenuntergangsplätze, ruhige Frühstückszeiten und das chronologische Brücken-Journal.
          </p>
        </div>

        {/* Total Stats Summary Pill */}
        <div className="flex items-center gap-4 p-3 bg-slate-900 text-white rounded-2xl border border-slate-800 self-start md:self-auto font-mono text-xs shadow-md">
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Reisen</span>
            <span className="text-amber-400 font-bold text-sm">{data.totalVoyagesCount}</span>
          </div>
          <div className="w-px h-6 bg-slate-800" />
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Seetage</span>
            <span className="text-amber-400 font-bold text-sm">{data.totalSeaDays}</span>
          </div>
          <div className="w-px h-6 bg-slate-800" />
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Länder</span>
            <span className="text-amber-400 font-bold text-sm">{data.visitedCountries.length}</span>
          </div>
        </div>
      </div>

      {/* Main Leather-Bound Logbook Console Container */}
      <div className="bg-slate-950 text-white border border-amber-900/40 rounded-3xl p-6 md:p-10 shadow-2xl space-y-10 relative overflow-hidden">
        {/* Warm Ambient Glows */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />

        {/* 1. WELCOME BACK GREETING */}
        <div className="p-6 bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 border border-amber-900/30 rounded-2xl space-y-2">
          <div className="text-xs font-mono uppercase text-amber-400 font-semibold flex items-center gap-2">
            <Anchor className="w-3.5 h-3.5" />
            <span>Offizielles Logbuch der Brücke · Reisender: {data.travellerName}</span>
          </div>
          <p className="text-sm md:text-base text-slate-200 font-serif italic leading-relaxed">
            » {data.botWelcomeBackGreeting} «
          </p>
        </div>

        {/* 2. CHRONOLOGICAL LOGBOOK & VOYAGE SELECTOR */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Bookmark className="w-3.5 h-3.5 text-amber-400" />
              <span>Logbuch-Einträge & Chronologie</span>
            </div>

            {/* Voyage Switcher */}
            <div className="flex flex-wrap gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800">
              {data.voyageHistory.map((voy) => (
                <button
                  key={voy.voyageId}
                  onClick={() => setSelectedVoyageId(voy.voyageId)}
                  className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                    selectedVoyageId === voy.voyageId
                      ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  <Ship className="w-3 h-3" />
                  <span>{voy.shipName} ({voy.departureDate.split(' ')[0]})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Active Voyage Logbook Page */}
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-4">
              <div>
                <span className="text-xs font-mono text-amber-400">{activeVoyage.cruiseLine}</span>
                <h3 className="text-xl md:text-2xl font-serif text-white mt-0.5">
                  {activeVoyage.shipName} · {activeVoyage.departureDate}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-mono">
                  Route: {activeVoyage.itinerarySummary}
                </p>
              </div>
              <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-mono self-start sm:self-auto flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Erfolgreich abgeschlossen
              </span>
            </div>

            {/* Daily One-Sentence Journal Entries */}
            <div className="space-y-3">
              <div className="text-xs font-mono uppercase text-slate-400 font-semibold">
                Brücken-Journal (Ein präziser Faktenschein pro Reisetag):
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {activeVoyage.journalEntries.map((entry) => (
                  <div
                    key={entry.entryId}
                    className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl flex flex-col justify-between space-y-2"
                  >
                    <div>
                      <div className="flex items-center justify-between text-[11px] font-mono text-amber-400 mb-1">
                        <span>{entry.dateStr}</span>
                        <span className="text-slate-400">{entry.portOrSeaLocation}</span>
                      </div>
                      <div className="text-[10px] font-mono text-slate-400 uppercase">
                        {entry.voyageDayLabel}
                      </div>
                      <p className="text-xs text-slate-200 mt-2 font-serif leading-relaxed italic">
                        » {entry.factualMilestoneSentence} «
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Highlights */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-white/10 text-xs font-mono">
              <div className="p-3 bg-white/5 rounded-xl space-y-1">
                <span className="text-slate-400 uppercase text-[10px] block">Lieblingsort an Bord:</span>
                <span className="text-white font-semibold">{activeVoyage.favouriteVenue}</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl space-y-1">
                <span className="text-slate-400 uppercase text-[10px] block">Bleibender Moment:</span>
                <span className="text-slate-200">{activeVoyage.favouriteMemory}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. FAVOURITE PLACES & CONFIRMED TRAVEL HABITS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Favourite Locations */}
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
            <div className="text-xs font-mono uppercase text-amber-400 font-semibold flex items-center gap-2">
              <Heart className="w-3.5 h-3.5" />
              <span>Verifizierte Lieblingsorte an Bord</span>
            </div>
            <div className="space-y-3">
              {data.favouritePlaces.map((fav) => (
                <div key={fav.locationId} className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">{fav.name}</span>
                    <span className="text-[11px] font-mono text-amber-400">{fav.deckLocation}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{fav.whyFavoured}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Confirmed Travel Habits */}
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
            <div className="text-xs font-mono uppercase text-blue-400 font-semibold flex items-center gap-2">
              <Footprints className="w-3.5 h-3.5" />
              <span>Beobachtete Reisegewohnheiten</span>
            </div>
            <div className="space-y-3">
              {data.confirmedHabits.map((hab) => (
                <div key={hab.habitId} className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase text-blue-300">
                      {hab.category.split('(')[0].trim()}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{hab.evidenceVoyage}</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed">{hab.observation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 4. PROACTIVE RECURRING MEMORY INSIGHTS */}
        <div className="p-5 bg-amber-500/10 border border-amber-500/20 rounded-2xl space-y-2">
          <div className="text-xs font-mono uppercase text-amber-400 font-semibold flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Erinnerungs-Transfer für die nächste Reise</span>
          </div>
          <div className="space-y-1.5 text-xs text-slate-200">
            {data.proactiveMemoryInsights.map((ins, i) => (
              <div key={i} className="flex items-start gap-2">
                <ChevronRight className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span>{ins}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 5. PERMANENT BRIDGE LOG CLOSING NOTE */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic max-w-2xl">
            » {data.botClosingLogNote} «
          </div>
          <div className="text-xs md:text-sm text-amber-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0">
            <Anchor className="w-4 h-4 text-amber-400" />
            <span>Ich bleibe auf der Brücke.</span>
          </div>
        </div>
      </div>
    </section>
  );
};
