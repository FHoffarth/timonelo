import React, { useState } from 'react';
import {
  Plane,
  Building,
  Award,
  FileCheck,
  Car,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Compass,
  MapPin,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import {
  TRAVEL_PREPARATION_DATA,
  type TravelPreparationDashboardData,
} from '../generated/travel_preparation';

export const TravelPreparationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'flight' | 'hotel' | 'status' | 'visa' | 'transfer'>('flight');
  const data: TravelPreparationDashboardData = TRAVEL_PREPARATION_DATA;

  return (
    <section id="travel-preparation" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-900 border border-blue-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-blue-700" />
            Complete Travel Preparation · Chapter III Sprint 07
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Von der Haustür bis zur Kabine.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Flugverbindungen, Vorabend-Hotel, Status-Vorteile, Visa-Einreise und Terminal-Transfer – alles vorab geprüft, damit Sie vollkommen entspannt an Bord gehen.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          <button
            onClick={() => setActiveTab('flight')}
            className={`px-3 py-2 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'flight'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Plane className="w-3.5 h-3.5 text-blue-600" />
            <span>Flug & Airport</span>
          </button>
          <button
            onClick={() => setActiveTab('hotel')}
            className={`px-3 py-2 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'hotel'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Building className="w-3.5 h-3.5 text-amber-600" />
            <span>Hotel</span>
          </button>
          <button
            onClick={() => setActiveTab('status')}
            className={`px-3 py-2 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'status'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Award className="w-3.5 h-3.5 text-purple-600" />
            <span>Status & Perks</span>
          </button>
          <button
            onClick={() => setActiveTab('visa')}
            className={`px-3 py-2 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'visa'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Visa & Einreise</span>
          </button>
          <button
            onClick={() => setActiveTab('transfer')}
            className={`px-3 py-2 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'transfer'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Car className="w-3.5 h-3.5 text-indigo-600" />
            <span>Terminal-Transfer</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden p-6 md:p-10 space-y-8">
        {/* Tab 1: Flight */}
        {activeTab === 'flight' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-mono font-semibold uppercase text-blue-600">
                  Flugverbindung & Lounge
                </span>
                <h3 className="text-2xl font-serif text-slate-900 mt-0.5">
                  {data.flight.carrierName} {data.flight.flightNumber} · {data.flight.route}
                </h3>
              </div>
              <span className="text-xs font-mono px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full">
                Ankunft: {data.flight.arrivalTime} (Vortag)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                <div className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
                  Lounge-Zugang & Airport Hub
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {data.flight.loungeSummary}
                </p>
                <div className="text-[11px] text-slate-500 font-mono pt-1">
                  Zielflughafen: {data.flight.airportHub.name} ({data.flight.airportHub.iataCode}) · Einreise: {data.flight.airportHub.immigrationTime}
                </div>
              </div>

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                <div className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
                  Öffentlicher Nahverkehr & Taxis
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  <span className="font-semibold">Transit:</span> {data.flight.airportHub.publicTransit}
                </p>
                <p className="text-xs text-slate-700 leading-relaxed">
                  <span className="font-semibold">Taxi:</span> {data.flight.airportHub.taxiAdvice}
                </p>
              </div>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-2xl text-xs text-blue-950">
              <span className="font-semibold">Bridge Officer Tim:</span> {data.flight.botRecommendation}
            </div>

            <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-950">
              <span className="font-semibold">Negative Intelligence:</span> {data.flight.negativeIntelligence}
            </div>
          </div>
        )}

        {/* Tab 2: Hotel */}
        {activeTab === 'hotel' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-mono font-semibold uppercase text-amber-600">
                  Vorabend-Hotel & Terminal-Anbindung
                </span>
                <h3 className="text-2xl font-serif text-slate-900 mt-0.5">
                  {data.hotel.propertyName}, {data.hotel.city}
                </h3>
              </div>
              <span className="text-xs font-mono px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full">
                {data.hotel.chainLoyalty}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                <div className="text-xs font-semibold text-slate-900 mb-1">Distanz & Fahrzeit</div>
                <div className="text-sm font-semibold text-slate-900">{data.hotel.distanceToTerminal} ({data.hotel.transferDuration})</div>
                <div className="text-xs text-slate-500 mt-1">Empfohlene Abfahrt: {data.hotel.departureRecommendation}</div>
              </div>

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                <div className="text-xs font-semibold text-slate-900 mb-1">Frühstück & Check-out</div>
                <div className="text-xs text-slate-700">Frühstück ab {data.hotel.breakfastTime}</div>
                <div className="text-xs text-emerald-700 font-semibold mt-1">Late Check-out: {data.hotel.lateCheckout}</div>
              </div>

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                <div className="text-xs font-semibold text-slate-900 mb-1">Umgebung (200m)</div>
                <ul className="text-[11px] text-slate-600 space-y-0.5">
                  {data.hotel.conveniences.slice(0, 3).map((c, i) => (
                    <li key={i}>• {c}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl text-xs text-amber-950">
              <span className="font-semibold">Bridge Officer Tim:</span> {data.hotel.botVerdict}
            </div>

            <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-950">
              <span className="font-semibold">Negative Intelligence:</span> {data.hotel.negativeIntelligence}
            </div>
          </div>
        )}

        {/* Tab 3: Status */}
        {activeTab === 'status' && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <span className="text-xs font-mono font-semibold uppercase text-purple-600">
                Aktivierte Treuestatus & VIP-Vorteile
              </span>
              <h3 className="text-2xl font-serif text-slate-900 mt-0.5">
                Kreuzfahrt-, Hotel- & Flug-Privilegien
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.loyalty.map((l, idx) => (
                <div key={idx} className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-900">{l.programName}</span>
                    <span className="px-2.5 py-0.5 bg-purple-100 text-purple-800 text-xs font-bold rounded-full">
                      {l.tierName}
                    </span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    {l.keyPerks.map((p, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="pt-2 border-t border-slate-200 text-[11px] text-slate-500 font-mono">
                    {l.lateCheckout} · {l.pointsEstimate}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Visa */}
        {activeTab === 'visa' && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <span className="text-xs font-mono font-semibold uppercase text-emerald-600">
                Einreise-Voraussetzungen
              </span>
              <h3 className="text-2xl font-serif text-slate-900 mt-0.5">
                Visa, Reisepass-Gültigkeit & Formulare
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.visaRequirements.map((v, idx) => (
                <div key={idx} className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-base font-semibold text-slate-900">{v.country}</span>
                    <span className="px-2.5 py-0.5 bg-emerald-100 text-emerald-800 text-xs font-semibold rounded-full">
                      {v.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">{v.details}</p>
                  <div className="text-[11px] text-slate-500 font-mono pt-1">
                    Passrestgültigkeit: {v.passportValidity}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 5: Transfer */}
        {activeTab === 'transfer' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-mono font-semibold uppercase text-indigo-600">
                  Einschiffungsmorgen-Logistik
                </span>
                <h3 className="text-2xl font-serif text-slate-900 mt-0.5">
                  Transfer: {data.transfer.pickupLocation} → {data.transfer.destination}
                </h3>
              </div>
              <span className="text-xs font-mono px-3 py-1 bg-indigo-50 text-indigo-900 border border-indigo-200 rounded-full">
                Abfahrt: {data.transfer.departureTime} (Ankunft: {data.transfer.terminalArrival})
              </span>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-800 space-y-1">
              <div><span className="font-semibold">Empfohlenes Verkehrsmittel:</span> {data.transfer.bestOption}</div>
              <div><span className="font-semibold">Gepäckannahme:</span> Gate 2 Vorzone vor Terminal T1/T2 (MSC Kofferanhänger Kabine 14122)</div>
            </div>

            <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-950">
              <span className="font-semibold">Negative Intelligence:</span> {data.transfer.negativeIntelligence}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
