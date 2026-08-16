import React, { useState, useEffect } from 'react';
import {
  Anchor,
  Compass,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  MapPin,
  ChevronRight,
  BookOpen,
  Waves,
  Radio,
} from 'lucide-react';
import { useI18n } from '../i18n';

interface HospitalityLandingProps {
  onSelectVessel: (slug: string) => void;
  onOpenPreparation?: () => void;
}

export const HospitalityLanding: React.FC<HospitalityLandingProps> = ({
  onSelectVessel,
  onOpenPreparation,
}) => {
  const { t, locale, formatTime } = useI18n();
  const isGerman = locale === 'de';
  const [selectedVoyageTab, setSelectedVoyageTab] = useState<'bellissima' | 'andorinha'>('bellissima');
  const [activeScenarioKey, setActiveScenarioKey] = useState<'embarkation' | 'seaday' | 'portday' | 'evening'>('embarkation');
  
  // Real-time time of day greeting
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [utcString, setUtcString] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now);
      setUtcString(now.toUTCString().slice(17, 22) + ' UTC');
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const hour = currentTime.getHours();
  const greeting = hour >= 5 && hour < 12 
    ? t.hero.greetingMorning 
    : hour >= 12 && hour < 18 
      ? t.hero.greetingAfternoon 
      : t.hero.greetingEvening;

  const currentScenario = t.todayOnWatch.scenarios[activeScenarioKey];

  return (
    <div className="bg-[#f4f2ed] text-[#0c1b2a] min-h-screen selection:bg-amber-200 selection:text-slate-900">
      {/* ─────────────────────────────────────────────────────────────
          SECTION 1 · WELCOME ABOARD (ATMOSPHERIC MARITIME HERO)
          Spatial Staging: Deep light, physical ocean presence & mist.
      ───────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden min-h-[88vh] flex flex-col justify-center border-b border-slate-200/80">
        {/* Atmosphere & Ocean Spatial Stage */}
        <div className="absolute inset-0 pointer-events-none select-none z-0 overflow-hidden">
          {/* Luminous Sun & Horizon Glow */}
          <div className="absolute top-0 right-0 w-[800px] h-[500px] bg-gradient-to-bl from-amber-200/35 via-amber-100/20 to-transparent blur-3xl opacity-70" />
          
          {/* Physical Vessel emerging through morning ocean mist */}
          <div className="absolute right-0 top-0 bottom-0 w-full sm:w-[85%] lg:w-[70%] xl:w-[62%] h-full flex items-center justify-end">
            <div className="relative w-full h-full">
              <img
                src="/hero-cruise-mist.webp"
                alt="Luxury Cruise Vessel sailing through morning sea mist"
                fetchPriority="high"
                decoding="async"
                className="w-full h-full object-cover object-[65%_center] lg:object-right opacity-85 mix-blend-multiply filter contrast-[1.04] brightness-[1.02]"
              />
              
              {/* Volumetric Sea Mist & Gradient Falloffs (Seamless integration into #f4f2ed) */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#f4f2ed] via-[#f4f2ed]/90 to-[#f4f2ed]/30 sm:via-[#f4f2ed]/80 sm:to-transparent w-full lg:w-[65%]" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#f4f2ed] via-transparent to-transparent h-full" />
              <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-[#f4f2ed] to-transparent" />
              
              {/* Soft Ambient Horizon Haze */}
              <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[#f4f2ed] via-[#f4f2ed]/60 to-transparent backdrop-blur-[1px]" />
            </div>
          </div>
        </div>

        {/* Foreground Content */}
        <div className="relative z-10 pt-16 pb-20 md:pt-24 md:pb-28 px-6 max-w-5xl mx-auto w-full flex flex-col items-start justify-center">
          {/* Dynamic Status Indicator */}
          <div className="flex flex-wrap items-center gap-3 mb-8">
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-white/95 border border-slate-200/90 shadow-xs text-xs font-medium text-slate-800 backdrop-blur-md">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
              </span>
              <span className="font-semibold text-slate-900">{t.hero.officerStatus}</span>
              <span className="text-slate-300">|</span>
              <span className="text-slate-600">{t.hero.deckLocation}</span>
            </div>

            <div className="hidden sm:inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/80 border border-slate-200/70 text-xs text-slate-600 font-sans backdrop-blur-md shadow-2xs">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{formatTime(currentTime)} · {utcString || '17:42 UTC'}</span>
            </div>
          </div>

          {/* Main Title */}
          <h1 className="font-serif text-5xl sm:text-6xl md:text-7xl lg:text-[5.2rem] font-normal tracking-tight text-[#0c1b2a] leading-[1.05] max-w-2xl">
            {t.hero.welcome}
          </h1>

          {/* Tim's Living Dialogue */}
          <div className="mt-8 space-y-3 max-w-2xl text-slate-700 text-lg md:text-xl font-sans leading-relaxed font-light">
            <p className="font-serif italic text-2xl md:text-3xl text-slate-900 leading-snug">
              » {greeting} {t.hero.readyNotice} «
            </p>
            <p className="text-base md:text-lg text-slate-600 font-light pt-1">
              {t.hero.leadNotice}
            </p>
          </div>

          {/* Primary CTA */}
          <div className="mt-12 flex flex-col sm:flex-row sm:items-center gap-5">
            <button
              onClick={() => {
                if (onOpenPreparation) {
                  onOpenPreparation();
                } else {
                  const el = document.getElementById('live-watch');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }
              }}
              className="group inline-flex items-center gap-3 px-8 py-4 rounded-full bg-[#0c1b2a] text-white hover:bg-slate-800 transition-all text-base font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 cursor-pointer"
            >
              <span>{t.hero.primaryCta}</span>
              <ArrowRight className="w-4 h-4 text-amber-300 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 2 · TIM'S LIVE OBSERVATIONS (TODAY ON WATCH)
      ───────────────────────────────────────────────────────────── */}
      <section id="live-watch" className="py-20 md:py-28 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.todayOnWatch.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.todayOnWatch.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.todayOnWatch.subtitle}
          </p>
        </div>

        {/* Scenario Selector Pills */}
        <div className="flex flex-wrap gap-2">
          {(['embarkation', 'seaday', 'portday', 'evening'] as const).map((key) => {
            const scenario = t.todayOnWatch.scenarios[key];
            const isActive = activeScenarioKey === key;
            return (
              <button
                key={key}
                onClick={() => setActiveScenarioKey(key)}
                className={`px-4 py-2.5 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-md'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-amber-400' : 'bg-slate-300'}`} />
                <span>{scenario.timeLabel.split('·')[1]?.trim() || scenario.timeLabel}</span>
              </button>
            );
          })}
        </div>

        {/* Active Scenario Card - Pure Maritime Hospitality */}
        <div className="bg-[#0c1b2a] text-white border border-slate-800 rounded-3xl p-6 md:p-10 shadow-2xl space-y-8 transition-all">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="text-xs uppercase text-amber-400 font-semibold tracking-wider flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                <span>{currentScenario.timeLabel}</span>
              </div>
              <h3 className="text-2xl md:text-3xl font-serif text-white mt-1">
                {currentScenario.title}
              </h3>
            </div>
            <div className="text-xs text-slate-400 bg-white/5 px-3.5 py-1.5 rounded-full self-start sm:self-auto flex items-center gap-1.5">
              <MapPin className="w-3 h-3 text-slate-300" />
              <span>{currentScenario.location}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            {/* Observation */}
            <div className="p-5 bg-white/5 border border-white/10 rounded-2xl space-y-2">
              <div className="text-xs uppercase text-blue-300 font-semibold flex items-center gap-2">
                <Compass className="w-4 h-4 text-blue-400" />
                <span>{t.todayOnWatch.bridgeObservation}</span>
              </div>
              <p className="text-slate-200 leading-relaxed font-light">
                {currentScenario.observation}
              </p>
            </div>

            {/* Recommendation */}
            <div className="p-5 bg-emerald-950/20 border border-emerald-500/30 rounded-2xl space-y-2">
              <div className="text-xs uppercase text-emerald-400 font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{t.todayOnWatch.recommendation}</span>
              </div>
              <p className="text-slate-200 leading-relaxed font-light">
                {currentScenario.recommendation}
              </p>
            </div>

            {/* Thing to Avoid */}
            <div className="p-5 bg-rose-950/20 border border-rose-900/30 rounded-2xl space-y-2">
              <div className="text-xs uppercase text-rose-400 font-semibold flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>{t.todayOnWatch.whatToAvoid}</span>
              </div>
              <p className="text-slate-300 leading-relaxed font-light">
                {currentScenario.avoid}
              </p>
            </div>

            {/* Next Step */}
            <div className="p-5 bg-amber-500/10 border border-amber-500/20 rounded-2xl space-y-2">
              <div className="text-xs uppercase text-amber-400 font-semibold flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                <span>{t.todayOnWatch.nextStep}</span>
              </div>
              <p className="text-slate-200 leading-relaxed font-light">
                {currentScenario.nextStep}
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span className="italic">» {t.todayOnWatch.officerSignOff} «</span>
            <span className="text-amber-400 font-serif font-medium">{t.todayOnWatch.officerName}</span>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 3 · YOUR VOYAGE & FLEET GALLERY
      ───────────────────────────────────────────────────────────── */}
      <section id="fleet-gallery" className="py-20 md:py-28 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.yourVoyage.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.yourVoyage.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.yourVoyage.subtitle}
          </p>
        </div>

        {/* Voyage Switcher Card */}
        <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-10 shadow-xs space-y-8">
          <div className="flex flex-wrap gap-2 border-b border-slate-100 pb-4">
            <button
              onClick={() => setSelectedVoyageTab('bellissima')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                selectedVoyageTab === 'bellissima'
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              {t.yourVoyage.tabOcean}
            </button>
            <button
              onClick={() => setSelectedVoyageTab('andorinha')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                selectedVoyageTab === 'andorinha'
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              {t.yourVoyage.tabRiver}
            </button>
          </div>

          {selectedVoyageTab === 'bellissima' ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
              <div className="space-y-1 md:col-span-2">
                <div className="inline-flex items-center gap-2 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded-md mb-2 font-medium">
                  <Compass className="w-3.5 h-3.5" />
                  <span>{t.yourVoyage.bellissimaSubtitle}</span>
                </div>
                <h3 className="text-2xl font-serif text-slate-900">
                  {t.yourVoyage.bellissimaTitle}
                </h3>
                <p className="text-sm text-slate-600 font-light leading-relaxed pt-1">
                  {t.yourVoyage.bellissimaDesc}
                </p>
                <div className="pt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 font-medium">
                  <span>{t.yourVoyage.bellissimaMuster}</span>
                  <span>·</span>
                  <span>{t.yourVoyage.bellissimaStatus}</span>
                  <span>·</span>
                  <span>{isGerman ? 'Deck 14 · Mittschiffs' : 'Deck 14 · Midship'}</span>
                </div>
              </div>

              <div className="flex justify-start md:justify-end">
                <button
                  onClick={() => onSelectVessel('msc-bellissima')}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm hover:shadow-md"
                >
                  <span>{t.common.stepAboard}</span>
                  <ChevronRight className="w-4 h-4 text-amber-300" />
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
              <div className="space-y-1 md:col-span-2">
                <div className="inline-flex items-center gap-2 text-xs text-blue-800 bg-blue-50 px-2.5 py-1 rounded-md mb-2 font-medium">
                  <Waves className="w-3.5 h-3.5" />
                  <span>{t.yourVoyage.andorinhaSubtitle}</span>
                </div>
                <h3 className="text-2xl font-serif text-slate-900">
                  {t.yourVoyage.andorinhaTitle}
                </h3>
                <p className="text-sm text-slate-600 font-light leading-relaxed pt-1">
                  {t.yourVoyage.andorinhaDesc}
                </p>
                <div className="pt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 font-medium">
                  <span>{t.yourVoyage.andorinhaLocks}</span>
                  <span>·</span>
                  <span>{t.yourVoyage.andorinhaStyle}</span>
                </div>
              </div>

              <div className="flex justify-start md:justify-end">
                <button
                  onClick={() => onSelectVessel('ms-andorinha')}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm hover:shadow-md"
                >
                  <span>{t.common.stepOnRiverDeck}</span>
                  <ChevronRight className="w-4 h-4 text-amber-300" />
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 4 · QUIET CERTAINTY (PHILOSOPHY)
      ───────────────────────────────────────────────────────────── */}
      <section id="platform-principles" className="py-20 md:py-28 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.philosophy.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.philosophy.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.philosophy.subtitle}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-8 bg-white border border-slate-200/80 rounded-3xl space-y-3 shadow-xs">
            <h3 className="text-lg font-serif font-medium text-slate-900">{t.philosophy.reduceUncertaintyTitle}</h3>
            <p className="text-sm text-slate-600 font-light leading-relaxed">
              {t.philosophy.reduceUncertaintyDesc}
            </p>
          </div>

          <div className="p-8 bg-white border border-slate-200/80 rounded-3xl space-y-3 shadow-xs">
            <h3 className="text-lg font-serif font-medium text-slate-900">{t.philosophy.neverInventTitle}</h3>
            <p className="text-sm text-slate-600 font-light leading-relaxed">
              {t.philosophy.neverInventDesc}
            </p>
          </div>

          <div className="p-8 bg-white border border-slate-200/80 rounded-3xl space-y-3 shadow-xs">
            <h3 className="text-lg font-serif font-medium text-slate-900">{t.philosophy.buildCalmTitle}</h3>
            <p className="text-sm text-slate-600 font-light leading-relaxed">
              {t.philosophy.buildCalmDesc}
            </p>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 5 · BRIDGE OFFICER TIM (CONDUCT & BOUNDARIES)
      ───────────────────────────────────────────────────────────── */}
      <section className="py-20 md:py-28 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.officerConduct.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.officerConduct.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.officerConduct.subtitle}
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-8 md:p-12 shadow-xs grid grid-cols-1 md:grid-cols-2 gap-10">
          <div className="space-y-4">
            <div className="text-xs uppercase text-emerald-800 font-semibold tracking-wider">
              {t.officerConduct.whatIDoTitle}
            </div>
            <ul className="space-y-3.5 text-sm text-slate-700 font-light">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{t.officerConduct.whatIDo1}</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{t.officerConduct.whatIDo2}</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{t.officerConduct.whatIDo3}</span>
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <div className="text-xs uppercase text-slate-500 font-semibold tracking-wider">
              {t.officerConduct.whatINeverDoTitle}
            </div>
            <ul className="space-y-3.5 text-sm text-slate-500 font-light">
              <li className="flex items-start gap-3">
                <span className="text-slate-400 font-bold">✕</span>
                <span>{t.officerConduct.whatINeverDo1}</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-slate-400 font-bold">✕</span>
                <span>{t.officerConduct.whatINeverDo2}</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-slate-400 font-bold">✕</span>
                <span>{t.officerConduct.whatINeverDo3}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 6 · CONNECTED SHIP SYSTEMS
      ───────────────────────────────────────────────────────────── */}
      <section className="py-20 md:py-28 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.connectedSystems.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.connectedSystems.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.connectedSystems.subtitle}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-left">
          <div className="p-6 bg-white border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
            <div className="text-xs text-amber-700 font-semibold uppercase">{t.connectedSystems.system1Badge}</div>
            <h4 className="text-sm font-semibold text-slate-900">{t.connectedSystems.system1Title}</h4>
            <p className="text-xs text-slate-500 font-light leading-relaxed">{t.connectedSystems.system1Desc}</p>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
            <div className="text-xs text-amber-700 font-semibold uppercase">{t.connectedSystems.system2Badge}</div>
            <h4 className="text-sm font-semibold text-slate-900">{t.connectedSystems.system2Title}</h4>
            <p className="text-xs text-slate-500 font-light leading-relaxed">{t.connectedSystems.system2Desc}</p>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
            <div className="text-xs text-amber-700 font-semibold uppercase">{t.connectedSystems.system3Badge}</div>
            <h4 className="text-sm font-semibold text-slate-900">{t.connectedSystems.system3Title}</h4>
            <p className="text-xs text-slate-500 font-light leading-relaxed">{t.connectedSystems.system3Desc}</p>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
            <div className="text-xs text-amber-700 font-semibold uppercase">{t.connectedSystems.system4Badge}</div>
            <h4 className="text-sm font-semibold text-slate-900">{t.connectedSystems.system4Title}</h4>
            <p className="text-xs text-slate-500 font-light leading-relaxed">{t.connectedSystems.system4Desc}</p>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          SECTION 7 · MEMORIES OF THE SEA (LOGBOOK)
      ───────────────────────────────────────────────────────────── */}
      <section className="py-20 md:py-32 px-6 max-w-5xl mx-auto space-y-10">
        <div className="space-y-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
            {t.logbook.badge}
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-[#0c1b2a] font-normal tracking-tight">
            {t.logbook.title}
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl font-light">
            {t.logbook.subtitle}
          </p>
        </div>

        {/* The Leather-bound Memory Box */}
        <div className="p-8 md:p-12 bg-[#0c1b2a] text-white border border-amber-900/40 rounded-3xl shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-amber-400" />
              <span className="text-xs uppercase tracking-wider text-amber-300 font-semibold">
                {t.logbook.journalEntryBadge}
              </span>
            </div>
            <span className="text-xs text-slate-400 font-medium">{t.logbook.journalLocation}</span>
          </div>

          <p className="text-lg md:text-xl font-serif italic text-slate-200 leading-relaxed">
            {t.logbook.journalQuote}
          </p>

          <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="text-xs text-slate-400 italic">
              {t.logbook.journalSignOff}
            </div>
            <div className="text-xs md:text-sm text-amber-400 font-serif flex items-center gap-2">
              <Anchor className="w-4 h-4" />
              <span>{t.logbook.officerSignature}</span>
            </div>
          </div>
        </div>

        {/* Final Sign-off Quote */}
        <div className="text-center pt-8 pb-4">
          <p className="font-serif text-2xl md:text-3xl text-slate-800 italic">
            {t.logbook.finalQuote}
          </p>
        </div>
      </section>
    </div>
  );
};
