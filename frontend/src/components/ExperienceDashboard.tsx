import React, { useState } from 'react';
import {
  Compass,
  Sparkles,
  Shirt,
  Calendar,
  AlertTriangle,
  Volume2,
  VolumeX,
  Music,
  Wine,
  Moon,
  Clock,
  CheckCircle2,
  Anchor,
  Layers,
  Flame,
} from 'lucide-react';
import {
  EXPERIENCE_PROFILES,
  type ExperienceProfileData,
  type VoyageEventData,
} from '../generated/experience_intelligence';

export const ExperienceDashboard: React.FC = () => {
  const [selectedVoyageId, setSelectedVoyageId] = useState<string>('bellissima-asia-standard');
  const profile: ExperienceProfileData =
    EXPERIENCE_PROFILES.find((p) => p.voyageId === selectedVoyageId) || EXPERIENCE_PROFILES[0];

  return (
    <section id="experience-intelligence" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-900 border border-purple-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5 text-purple-700" />
            Experience Intelligence · Chapter IV Sprint 01
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Jede Reise hat ihre eigene Kultur.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Gala-Abend, White Night oder Gourmet-Event: Bridge Officer Tim versteht die Atmosphäre der Reise, erklärt Dresscodes und empfiehlt ruhige Rückzugsorte.
          </p>
        </div>

        {/* Voyage Profile Switcher */}
        <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          <button
            onClick={() => setSelectedVoyageId('bellissima-asia-standard')}
            className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
              selectedVoyageId === 'bellissima-asia-standard'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            White Night & Gala
          </button>
          <button
            onClick={() => setSelectedVoyageId('music-festival-charter')}
            className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
              selectedVoyageId === 'music-festival-charter'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Sinfonie & Jazz Festival
          </button>
          <button
            onClick={() => setSelectedVoyageId('gourmet-food-wine')}
            className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
              selectedVoyageId === 'gourmet-food-wine'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Gourmet & Wein-Tour
          </button>
        </div>
      </div>

      {/* Main Luxury Experience Container */}
      <div className="bg-slate-950 text-white border border-slate-800 rounded-3xl p-6 md:p-10 shadow-2xl space-y-10 relative overflow-hidden">
        {/* Ambient Lights */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* 1. VOYAGE CULTURE HEADER & DRESS GUIDANCE */}
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="text-xs font-mono uppercase text-purple-400 tracking-wider flex items-center gap-2">
                <Flame className="w-3.5 h-3.5" />
                <span>{profile.experienceType.split('(')[0].trim()} · {profile.ship_name}</span>
              </div>
              <h3 className="text-2xl md:text-3xl font-serif text-white mt-1">
                {profile.voyageThemeTitle}
              </h3>
              <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
                {profile.description}
              </p>
            </div>
            {profile.charterOrganizer && (
              <span className="px-3 py-1.5 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-mono self-start md:self-auto">
                Host: {profile.charterOrganizer}
              </span>
            )}
          </div>

          {/* Dress Guidance Box */}
          <div className="p-5 bg-purple-500/10 border border-purple-500/20 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-300 shrink-0 mt-0.5">
                <Shirt className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-semibold text-purple-300 uppercase font-mono tracking-wider">
                  Kleiderordnung & Abendmotto der Brücke
                </div>
                <p className="text-xs md:text-sm text-slate-200 mt-1 leading-relaxed">
                  {profile.dressGuidanceSummary}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 2. TODAY'S EVENT PROGRAMME TIMELINE */}
        <div className="space-y-4">
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2 border-b border-slate-800 pb-3">
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span>Tages- & Abendprogramm · Zeitlicher Ablauf</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {profile.eventsSchedule.map((ev) => (
              <div
                key={ev.eventId}
                className="p-5 bg-white/5 border border-white/10 rounded-2xl flex flex-col justify-between space-y-3 hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-[10px] font-mono rounded">
                      {ev.startTime}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      {ev.deckLocation}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white">
                    {ev.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {ev.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-1.5 text-[11px] font-mono">
                  <div className="text-slate-400">
                    Motto: <span className="text-amber-400">{ev.dressCode.split('(')[0].trim()}</span>
                  </div>
                  {ev.quieterAlternativeVenue && (
                    <div className="text-emerald-400 flex items-start gap-1">
                      <VolumeX className="w-3 h-3 shrink-0 mt-0.5" />
                      <span>Ruhige Alternative: {ev.quieterAlternativeVenue}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. NEGATIVE INTELLIGENCE & QUIET RETREATS (SPLIT GRID) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Busy Areas to Avoid */}
          <div className="space-y-3 p-5 bg-rose-950/20 border border-rose-900/30 rounded-2xl">
            <div className="text-xs font-mono uppercase text-rose-400 font-semibold flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Negative Intelligence · High-Traffic Zonen</span>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {profile.busyAreasToAvoid.map((busy, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="font-mono text-rose-400 font-bold">!</span>
                  <span>{busy}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Quiet Retreat Venues */}
          <div className="space-y-3 p-5 bg-emerald-950/20 border border-emerald-900/30 rounded-2xl">
            <div className="text-xs font-mono uppercase text-emerald-400 font-semibold flex items-center gap-2">
              <VolumeX className="w-3.5 h-3.5" />
              <span>Ruhige Rückzugsorte an Bord</span>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {profile.quietRetreatVenues.map((quiet, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{quiet}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* 4. PROACTIVE BOT OBSERVATIONS */}
        {profile.botProactiveObservations.length > 0 && (
          <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl space-y-2 text-xs text-amber-200">
            {profile.botProactiveObservations.map((obs, i) => (
              <div key={i} className="flex items-start gap-2">
                <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span>{obs}</span>
              </div>
            ))}
          </div>
        )}

        {/* 5. EVENING SIGN-OFF */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic max-w-2xl">
            » {profile.botEveningSignOff} «
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
