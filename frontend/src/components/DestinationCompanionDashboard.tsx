import React, { useState } from 'react';
import {
  Compass,
  MapPin,
  Clock,
  Footprints,
  Car,
  AlertTriangle,
  Utensils,
  LifeBuoy,
  PhoneCall,
  CheckCircle2,
  Anchor,
  Sparkles,
  Zap,
  Droplets,
  CreditCard,
  Layers,
} from 'lucide-react';
import {
  PORT_CITY_PROFILES,
  type PortCityProfileData,
} from '../generated/port_city_intelligence';

export const DestinationCompanionDashboard: React.FC = () => {
  const [selectedCitySlug, setSelectedCitySlug] = useState<string>('yokohama');
  const [activeSection, setActiveSection] = useState<'overview' | 'gangway' | 'shoretime' | 'negative' | 'culinary'>('shoretime');

  const city: PortCityProfileData =
    PORT_CITY_PROFILES.find((c) => c.citySlug === selectedCitySlug) || PORT_CITY_PROFILES[0];

  return (
    <section id="destination-companion" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-amber-700" />
            Port & City Companion · Chapter III Sprint 08
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Acht Stunden an Land. Perfekt genutzt.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Kein Sightseeing-Ballast, sondern operative Sicherheit: Vom Gangway-Ausgang bis zur staufreien Rückkehr an Bord – mit verlässlichen Puffern und Scam-Prävention.
          </p>
        </div>

        {/* City Selector */}
        <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          {PORT_CITY_PROFILES.map((c) => (
            <button
              key={c.citySlug}
              onClick={() => setSelectedCitySlug(c.citySlug)}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
                selectedCitySlug === c.citySlug
                  ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {c.officialName.split('(')[0].trim()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Destination Container */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
        {/* Destination Top Bar */}
        <div className="bg-slate-900 text-white px-6 md:px-8 py-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs text-amber-400 uppercase tracking-wider font-mono flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5" />
              <span>{city.country} · {city.timezone}</span>
            </div>
            <h3 className="text-2xl md:text-3xl font-serif text-white font-normal mt-0.5">
              {city.officialName}
            </h3>
            <div className="text-xs text-slate-400 font-mono mt-0.5">
              Terminal: {city.terminalName}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 bg-white/10 text-white text-xs font-mono rounded-lg border border-white/10">
              {city.currency.split('·')[0].trim()}
            </span>
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-mono rounded-lg border border-emerald-500/30">
              {city.tapWater.includes('SAFE') ? '✓ Trinkwasser OK' : '⚠ Flaschenwasser'}
            </span>
          </div>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex flex-wrap gap-2 px-6 md:px-8 py-3 bg-slate-50 border-b border-slate-200 text-xs">
          <button
            onClick={() => setActiveSection('shoretime')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeSection === 'shoretime'
                ? 'bg-slate-900 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-200/60'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Zeitfenster & Puffer</span>
          </button>
          <button
            onClick={() => setActiveSection('gangway')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeSection === 'gangway'
                ? 'bg-slate-900 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-200/60'
            }`}
          >
            <Footprints className="w-3.5 h-3.5" />
            <span>Gangway → Stadt</span>
          </button>
          <button
            onClick={() => setActiveSection('negative')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeSection === 'negative'
                ? 'bg-slate-900 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-200/60'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            <span>Negative Intelligence</span>
          </button>
          <button
            onClick={() => setActiveSection('culinary')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeSection === 'culinary'
                ? 'bg-slate-900 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-200/60'
            }`}
          >
            <Utensils className="w-3.5 h-3.5 text-emerald-500" />
            <span>Kulinarik-Tipps</span>
          </button>
          <button
            onClick={() => setActiveSection('overview')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeSection === 'overview'
                ? 'bg-slate-900 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-200/60'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Logistik & Notruf</span>
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="p-6 md:p-10 space-y-8">
          {/* TAB 1: Shore Time Window & Return Clock */}
          {activeSection === 'shoretime' && (
            <div className="space-y-6">
              <div className="p-6 bg-slate-900 text-white rounded-3xl grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-white/5 border border-white/10 rounded-2xl text-center">
                  <div className="text-[10px] uppercase font-mono text-slate-400">Anlegen</div>
                  <div className="text-xl font-bold text-white mt-0.5">{city.shoreTime.scheduledArrival}</div>
                </div>
                <div className="p-3 bg-white/5 border border-white/10 rounded-2xl text-center">
                  <div className="text-[10px] uppercase font-mono text-rose-300">All Aboard</div>
                  <div className="text-xl font-bold text-rose-400 mt-0.5">{city.shoreTime.scheduledAllAboard}</div>
                </div>
                <div className="p-3 bg-emerald-500/20 border border-emerald-500/30 rounded-2xl text-center">
                  <div className="text-[10px] uppercase font-mono text-emerald-300">Empfohlene Rückkehr</div>
                  <div className="text-xl font-bold text-emerald-400 mt-0.5">{city.shoreTime.recommendedLatestReturn}</div>
                </div>
                <div className="p-3 bg-white/5 border border-white/10 rounded-2xl text-center">
                  <div className="text-[10px] uppercase font-mono text-slate-400">Sicherheits-Puffer</div>
                  <div className="text-xl font-bold text-white mt-0.5">{city.shoreTime.safeBufferMinutes} min</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-700">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-1">
                  <div className="font-semibold text-slate-900">Stoßzeiten & Verkehrsengpässe:</div>
                  <div>{city.shoreTime.rushHourWarningWindow}</div>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-1">
                  <div className="font-semibold text-slate-900">Sicherer Aktionsradius zu Fuß:</div>
                  <div>Bis zu {city.shoreTime.safeWalkingRadiusKm} km um das Kreuzfahrtterminal</div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Gangway Steps */}
          {activeSection === 'gangway' && (
            <div className="space-y-6">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Schritt-für-Schritt Wegführung vom Schiff ins Zentrum:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {city.gangwaySteps.map((step) => (
                  <div key={step.stepNum} className="p-5 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-mono font-bold flex items-center justify-center">
                          {step.stepNum}
                        </span>
                        <span className="text-xs font-mono text-slate-500">~{step.typicalMinutes} min</span>
                      </div>
                      <div className="text-sm font-semibold text-slate-900 mb-1">{step.title}</div>
                      <p className="text-xs text-slate-700 leading-relaxed">{step.instruction}</p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-slate-200 text-[11px] text-slate-500 italic">
                      💡 {step.orientationHint}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Negative Intelligence */}
          {activeSection === 'negative' && (
            <div className="space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-rose-900 mb-2">
                Häufige Touristenfallen & Fehler in {city.officialName.split('(')[0]}:
              </div>
              <ul className="space-y-2.5 text-xs text-rose-950">
                {city.negativeIntelligenceTraps.map((trap, idx) => (
                  <li key={idx} className="p-4 bg-rose-50/80 border border-rose-200 rounded-2xl leading-relaxed flex items-start gap-3">
                    <span className="font-mono font-bold text-rose-700 shrink-0 text-sm">!</span>
                    <span>{trap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* TAB 4: Local Culinary Tips */}
          {activeSection === 'culinary' && (
            <div className="space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-emerald-900 mb-2">
                Authentische regionale Spezialitäten:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {city.localCulinaryTips.map((tip, idx) => (
                  <div key={idx} className="p-5 bg-emerald-50/60 border border-emerald-200 rounded-2xl text-xs text-emerald-950 space-y-1">
                    <div className="font-semibold text-emerald-900 text-sm flex items-center gap-1.5">
                      <Utensils className="w-4 h-4 text-emerald-600" />
                      Empfehlung #{idx + 1}
                    </div>
                    <p className="leading-relaxed text-slate-800">{tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Overview, Logistics & Emergency */}
          {activeSection === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
              <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
                <div className="font-semibold text-slate-900 uppercase text-[11px] tracking-wider">
                  Öffentlicher Nahverkehr & Taxis
                </div>
                <div><span className="font-semibold">ÖPNV:</span> {city.publicTransportSummary}</div>
                <div><span className="font-semibold">Fahrdienste:</span> {city.rideHailingApps.join(', ')}</div>
                <div><span className="font-semibold">Fußgänger-Freundlichkeit:</span> {city.walking_friendliness}</div>
                <div><span className="font-semibold">Barrierefreiheit:</span> {city.accessibilityNotes}</div>
              </div>

              <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
                <div className="font-semibold text-slate-900 uppercase text-[11px] tracking-wider">
                  Notruf, Mobilfunk & Zahlung
                </div>
                <div><span className="font-semibold">Notruf:</span> Polizei {city.emergencyPolice} · Notarzt {city.emergencyMedical}</div>
                <div><span className="font-semibold">SIM / eSIM:</span> {city.simEsimAdvice}</div>
                <div><span className="font-semibold">Kartenkultur:</span> {city.cardVsCashCulture}</div>
                <div><span className="font-semibold">Steckertyp:</span> {city.plugType}</div>
              </div>
            </div>
          )}

          {/* Proactive Bridge Officer Notices */}
          {city.botProactiveNotices.length > 0 && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl space-y-1.5 text-xs text-amber-950">
              {city.botProactiveNotices.map((n, i) => (
                <div key={i} className="flex items-start gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <span>{n}</span>
                </div>
              ))}
            </div>
          )}

          {/* Signature Sign-Off */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>Evidenz: {city.evidenceSources.join(', ')}</span>
            <span className="font-serif italic text-amber-800 font-medium">
              „{city.botClosingPhrase}“
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
