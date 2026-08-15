/**
 * Boarding Intelligence UI (Plane 5). Calm, minimal orientation for the first
 * minutes onboard — turn direction, the first walk, a "you are here" diagram,
 * return journeys, and orientation moments. Human language, full precision.
 */
import { useState } from 'react';
import { ArrowRight, ArrowLeft, CornerDownLeft, CornerDownRight, Footprints, DoorOpen, Compass } from 'lucide-react';
import type { ShipData, CabinData } from './types';
import {
  parityInsight,
  firstWalk,
  returnJourneys,
  orientationMoments,
  turnFromSide,
  humanSide,
  elevatorLabel,
} from './boarding-core';

export function BoardingIntelligence({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  const parity = parityInsight(ship, cabin);
  const walk = firstWalk(cabin);
  const turn = turnFromSide(cabin.hull_side);

  return (
    <section aria-label="Boarding intelligence">
      <div className="mb-6 max-w-2xl">
        <p className="eyebrow-mist">First minutes onboard</p>
        <h2 className="font-display text-3xl md:text-4xl mt-2 leading-tight">Finding your cabin</h2>
        <p className="text-muted text-[15px] leading-relaxed mt-3">
          Leave the lift and go the right way the first time — the ship’s language, translated into left and right.
        </p>
      </div>

      {/* Even/odd turn headline */}
      {turn !== 'ahead' && (
        <div className="card p-6 md:p-7 mb-4 flex flex-col sm:flex-row sm:items-center gap-5">
          <div className="shrink-0 grid place-items-center w-16 h-16 rounded-full bg-ink text-white">
            {turn === 'right' ? <CornerDownRight className="w-7 h-7" aria-hidden /> : <CornerDownLeft className="w-7 h-7" aria-hidden />}
          </div>
          <div>
            <div className="font-display text-2xl text-ink">
              When you leave the {elevatorLabel(cabin.zone)}, turn <span className="uppercase">{turn}</span>.
            </div>
            <p className="text-[14px] text-muted mt-1">
              Cabin {cabin.cabin_number} is on {humanSide(cabin.hull_side)}
              {parity?.conventionExplains ? (
                <> — {parity.even ? 'even' : 'odd'}-numbered cabins sit on this side.</>
              ) : (
                <>.</>
              )}
            </p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        {/* First walk */}
        <div className="card p-6">
          <p className="eyebrow-mist mb-4 flex items-center gap-2"><Footprints className="w-3.5 h-3.5 text-gold" /> First walk to your cabin</p>
          <ol className="space-y-3">
            {walk.map((s, i) => (
              <li key={i} className="flex gap-3">
                <span className="shrink-0 w-6 h-6 rounded-full border border-ink/20 grid place-items-center text-[12px] font-mono text-muted">{i + 1}</span>
                <span className="text-[14px] text-ink leading-relaxed pt-0.5">{s.text}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* You are here diagram */}
        <div className="card p-6">
          <p className="eyebrow-mist mb-4 flex items-center gap-2"><Compass className="w-3.5 h-3.5 text-gold" /> You are here</p>
          <YouAreHere cabin={cabin} />
        </div>
      </div>

      {/* Orientation moments + return journeys */}
      <div className="grid lg:grid-cols-2 gap-4 mt-4">
        <OrientationMoments cabin={cabin} />
        <ReturnJourneys cabin={cabin} />
      </div>
    </section>
  );
}

function YouAreHere({ cabin }: { cabin: CabinData }) {
  const turn = turnFromSide(cabin.hull_side);
  const right = turn === 'right';
  return (
    <div>
      <div className="flex justify-between text-[10px] uppercase tracking-[0.16em] text-muted mb-2">
        <span className="flex items-center gap-1"><ArrowLeft className="w-3 h-3" /> Port · left</span>
        <span className="flex items-center gap-1">Starboard · right <ArrowRight className="w-3 h-3" /></span>
      </div>
      <div className="relative border hairline rounded-xs bg-paper h-40 overflow-hidden">
        {/* corridor line */}
        <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-px bg-ink/20" />
        {/* elevator (centre) */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="px-2.5 py-1.5 bg-ink text-white text-[11px] font-mono">Elevator</div>
        </div>
        {/* turn arrow + cabin on the correct side */}
        <div className={`absolute top-1/2 -translate-y-1/2 flex items-center gap-2 ${right ? 'right-5 flex-row-reverse' : 'left-5'}`}>
          <div className="h-3.5 w-3.5 rounded-full bg-gold border-2 border-ink" />
          <span className="text-[11px] font-mono font-bold bg-ink text-white px-1.5 py-0.5">{cabin.cabin_number}</span>
        </div>
        {/* turn instruction */}
        <div className={`absolute bottom-3 ${right ? 'right-5' : 'left-5'} text-[11px] font-semibold text-ink flex items-center gap-1`}>
          {right ? <>Turn right <ArrowRight className="w-3.5 h-3.5" /></> : <><ArrowLeft className="w-3.5 h-3.5" /> Turn left</>}
        </div>
      </div>
      <p className="text-[12px] text-muted mt-3">A simple picture, not a scale drawing — enough to know which way to go.</p>
    </div>
  );
}

function OrientationMoments({ cabin }: { cabin: CabinData }) {
  const moments = orientationMoments(cabin);
  const [active, setActive] = useState(moments[0]?.id);
  const current = moments.find((m) => m.id === active) ?? moments[0];
  return (
    <div className="card p-6">
      <p className="eyebrow-mist mb-4 flex items-center gap-2"><DoorOpen className="w-3.5 h-3.5 text-gold" /> Orientation moments</p>
      <div className="flex flex-wrap gap-2">
        {moments.map((m) => (
          <button
            key={m.id}
            onClick={() => setActive(m.id)}
            className={`px-3 py-1.5 text-[12px] font-medium border transition ${
              active === m.id ? 'bg-ink text-white border-ink' : 'bg-paper text-ink border-ink/15 hover:border-ink/40'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
      {current && <p className="text-[14px] text-ink leading-relaxed mt-4">{current.guidance}</p>}
    </div>
  );
}

function ReturnJourneys({ cabin }: { cabin: CabinData }) {
  const journeys = returnJourneys(cabin);
  return (
    <div className="card p-6">
      <p className="eyebrow-mist mb-4 flex items-center gap-2"><ArrowLeft className="w-3.5 h-3.5 text-gold" /> Finding your way back</p>
      <ul className="space-y-3.5">
        {journeys.map((j) => (
          <li key={j.id}>
            <div className="text-[12px] uppercase tracking-[0.1em] text-muted">Returning from {j.from}</div>
            <div className="text-[14px] text-ink leading-relaxed mt-0.5">{j.text}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
