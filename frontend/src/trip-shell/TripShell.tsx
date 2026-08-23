import { useState } from 'react';
import {
  Ship,
  MapPin,
  Calendar,
  Clock,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  FileText,
  Anchor,
  Compass,
} from 'lucide-react';
import { PassengerTripViewModel } from './types';

interface TripShellProps {
  viewModel: PassengerTripViewModel;
  className?: string;
}

export default function TripShell({ viewModel, className = '' }: TripShellProps) {
  const [isTrustDetailsOpen, setIsTrustDetailsOpen] = useState(false);

  return (
    <div className={`w-full max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-8 sm:space-y-12 ${className}`}>
      {/* 1. Top Section: Trip Header */}
      <section className="bg-white rounded-3xl p-6 sm:p-8 border border-[#0C1B2A]/10 shadow-sm relative overflow-hidden">
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-full bg-[#C58A46]/10 text-[#C58A46]">
                <Ship className="w-4 h-4" />
              </span>
              <span className="text-xs font-mono font-semibold tracking-wider text-[#C58A46] uppercase">
                {viewModel.shipName}
              </span>
            </div>

            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-200/50">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>{viewModel.trustSummary.statusBadge}</span>
            </div>
          </div>

          <div>
            <h1 className="text-2xl sm:text-4xl font-display font-bold text-[#0C1B2A] tracking-tight">
              {viewModel.routeLabel}
            </h1>
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-sm text-[#5B6570] mt-2 font-medium">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-[#C58A46]" />
                <span>{viewModel.dateRangeLabel}</span>
              </div>
              {viewModel.durationLabel && (
                <>
                  <span className="text-slate-300">•</span>
                  <span>{viewModel.durationLabel}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 2. Status Area: Departure & Arrival Cards */}
      <section className="space-y-3">
        <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase px-1">
          TRIP MILESTONES
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Departure Card */}
          <article className="bg-white rounded-2xl p-5 sm:p-6 border border-[#0C1B2A]/10 shadow-sm flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-[#C58A46] uppercase tracking-wider">
                  EMBARKATION
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-[#5B6570] font-medium">
                  {viewModel.departure.dateFormatted}
                </span>
              </div>
              <h3 className="text-xl font-display font-bold text-[#0C1B2A]">
                {viewModel.departure.city}
              </h3>
              {viewModel.departure.country && (
                <p className="text-xs text-[#5B6570]">{viewModel.departure.country}</p>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
              {viewModel.departure.timeFormatted && (
                <div className="flex items-center justify-between">
                  <span className="text-[#5B6570] flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-[#C58A46]" />
                    {viewModel.departure.timeLabel || 'Check-in'}
                  </span>
                  <span className="font-semibold text-[#0C1B2A]">
                    {viewModel.departure.timeFormatted.replace(/^Check-in:?\s*/i, '')}
                  </span>
                </div>
              )}

              <div className="flex items-center justify-between">
                <span className="text-[#5B6570] flex items-center gap-1.5">
                  <Anchor className="w-3.5 h-3.5 text-slate-400" />
                  Terminal
                </span>
                <span className="text-[#5B6570] italic font-normal">
                  {viewModel.departure.terminalStatusText}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#5B6570] flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  Berth
                </span>
                <span className="text-[#5B6570] italic font-normal">
                  {viewModel.departure.berthStatusText}
                </span>
              </div>
            </div>
          </article>

          {/* Arrival Card */}
          <article className="bg-white rounded-2xl p-5 sm:p-6 border border-[#0C1B2A]/10 shadow-sm flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-[#C58A46] uppercase tracking-wider">
                  DISEMBARKATION
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-[#5B6570] font-medium">
                  {viewModel.arrival.dateFormatted}
                </span>
              </div>
              <h3 className="text-xl font-display font-bold text-[#0C1B2A]">
                {viewModel.arrival.city}
              </h3>
              {viewModel.arrival.country && (
                <p className="text-xs text-[#5B6570]">{viewModel.arrival.country}</p>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[#5B6570] flex items-center gap-1.5">
                  <Anchor className="w-3.5 h-3.5 text-slate-400" />
                  Terminal
                </span>
                <span className="text-[#5B6570] italic font-normal">
                  {viewModel.arrival.terminalStatusText}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#5B6570] flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  Berth
                </span>
                <span className="text-[#5B6570] italic font-normal">
                  {viewModel.arrival.berthStatusText}
                </span>
              </div>
            </div>
          </article>
        </div>
      </section>

      {/* 3. Trip Timeline */}
      <section className="space-y-3">
        <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase px-1">
          ITINERARY TIMELINE
        </h2>
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#0C1B2A]/10 shadow-sm space-y-6">
          {viewModel.timeline.map((day, idx) => (
            <div key={idx} className="relative pl-6 sm:pl-8 border-l-2 border-[#C58A46]/20 last:border-l-0 pb-6 last:pb-0">
              {/* Timeline Marker */}
              <div className="absolute -left-[9px] top-0.5 w-4 h-4 rounded-full bg-white border-2 border-[#C58A46] flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-[#C58A46]" />
              </div>

              <div className="space-y-2">
                <div className="flex flex-wrap items-baseline gap-2">
                  <span className="text-xs font-mono font-bold text-[#C58A46]">
                    {day.dateFormatted} {day.dayOfWeek ? `(${day.dayOfWeek})` : ''}
                  </span>
                  <span className="text-sm font-display font-bold text-[#0C1B2A]">
                    {day.locationTitle}
                  </span>
                </div>

                <div className="space-y-2">
                  {day.events.map((evt, eIdx) => (
                    <div key={eIdx} className="bg-slate-50 rounded-xl p-3 text-xs space-y-1">
                      <div className="flex items-center justify-between font-semibold text-[#0C1B2A]">
                        <span>{evt.label}</span>
                        {evt.time && <span className="font-mono text-[#C58A46]">{evt.time}</span>}
                      </div>
                      {evt.note && <p className="text-[#5B6570] leading-relaxed">{evt.note}</p>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. What Is Confirmed & What Is Pending */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Confirmed Overview */}
        <div className="bg-white rounded-2xl p-5 sm:p-6 border border-[#0C1B2A]/10 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <h2 className="text-sm font-bold text-[#0C1B2A]">What is confirmed</h2>
            </div>
            <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/40">
              {viewModel.trustSummary.verifiedCount} confirmed facts
            </span>
          </div>
          <div className="space-y-2.5">
            {viewModel.confirmedFacts.map((fact, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs py-1 border-b border-slate-100 last:border-0">
                <span className="text-[#5B6570]">{fact.label}</span>
                <span className="font-semibold text-[#0C1B2A] text-right">{fact.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pending Details */}
        <div className="bg-white rounded-2xl p-5 sm:p-6 border border-[#0C1B2A]/10 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#C58A46]" />
              <h2 className="text-sm font-bold text-[#0C1B2A]">Details not available yet</h2>
            </div>
            <span className="text-[11px] font-mono text-[#C58A46] bg-amber-50 px-2 py-0.5 rounded border border-amber-200/40">
              {viewModel.trustSummary.pendingCount} details pending
            </span>
          </div>
          <div className="space-y-3">
            {viewModel.pendingFacts.map((pending, idx) => (
              <div key={idx} className="bg-amber-50/50 rounded-xl p-3 text-xs space-y-1 border border-amber-200/40">
                <div className="flex items-center justify-between font-semibold text-[#0C1B2A]">
                  <span>{pending.label}</span>
                  <span className="text-[10px] font-mono text-[#C58A46] uppercase px-2 py-0.5 rounded bg-amber-100/60">
                    {pending.statusText}
                  </span>
                </div>
                <p className="text-[#5B6570] leading-relaxed">{pending.whyPending}</p>
                <p className="text-[11px] text-[#C58A46] font-medium pt-1">{pending.whatNext}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Separate Section: Generic Port Information */}
      {viewModel.genericPortFacilities.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase">
              PORT INFORMATION (DESTINATION)
            </h2>
            <span className="text-[11px] text-[#5B6570] font-medium">General facility reference</span>
          </div>

          <div className="bg-white rounded-2xl p-5 sm:p-6 border border-[#0C1B2A]/10 shadow-sm space-y-4">
            <div className="flex items-start gap-3">
              <span className="p-2 rounded-xl bg-slate-100 text-slate-700 shrink-0">
                <Compass className="w-5 h-5" />
              </span>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-[#0C1B2A]">
                  {viewModel.arrival.city} Port Facilities
                </h3>
                <p className="text-xs text-[#5B6570] leading-relaxed">
                  The following facilities are registered in the destination port. Your specific arrival berth has not been confirmed yet.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 pt-2">
              {viewModel.genericPortFacilities.map((facility, idx) => (
                <div key={idx} className="bg-slate-50 rounded-xl p-4 text-xs space-y-1 border border-slate-100">
                  <div className="flex items-center justify-between font-semibold text-[#0C1B2A]">
                    <span className="text-sm">{facility.name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200/60 text-[#5B6570]">
                      {facility.facilityType}
                    </span>
                  </div>
                  <p className="text-[#C58A46] font-medium text-[11px]">
                    {facility.notice}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 6. Before You Go Checklist */}
      <section className="space-y-3">
        <h2 className="text-xs font-mono font-bold tracking-widest text-[#5B6570] uppercase px-1">
          BEFORE YOU GO
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {viewModel.beforeYouGo.map((item, idx) => (
            <article key={idx} className="bg-white rounded-2xl p-5 border border-[#0C1B2A]/10 shadow-sm space-y-2">
              <div className="w-8 h-8 rounded-full bg-[#C58A46]/10 text-[#C58A46] flex items-center justify-center mb-3">
                {item.iconName === 'terminal' && <Anchor className="w-4 h-4" />}
                {item.iconName === 'documents' && <FileText className="w-4 h-4" />}
                {item.iconName === 'port' && <Compass className="w-4 h-4" />}
              </div>
              <h3 className="text-sm font-bold text-[#0C1B2A] leading-snug">
                {item.title}
              </h3>
              <p className="text-xs text-[#5B6570] leading-relaxed">
                {item.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* 7. Trust UX / Why We Know This */}
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
                <span className="font-semibold text-[#0C1B2A] block mb-1">Evidence & Verification</span>
                <p className="leading-relaxed">
                  Facts are verified against authoritative cruise line booking confirmations and international UNECE port registries.
                </p>
              </div>

              <div className="bg-white rounded-xl p-3.5 border border-slate-200/40">
                <span className="font-semibold text-[#0C1B2A] block mb-1">Privacy & Data Isolation</span>
                <p className="leading-relaxed">
                  {viewModel.trustSummary.piiNotice}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 text-[11px] text-slate-400 font-mono">
              <span>{viewModel.trustSummary.governanceNotice}</span>
              {viewModel.trustSummary.lastCheckedDate && (
                <span>Last checked: {viewModel.trustSummary.lastCheckedDate}</span>
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
