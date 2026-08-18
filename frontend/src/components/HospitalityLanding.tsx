import React, { useState } from 'react';
import { ArrowRight, Compass, Waves, MapPin, Volume2, DoorOpen, Footprints, ShieldCheck } from 'lucide-react';
import { FLEET_REGISTRY } from '../fleet';
import { useI18n } from '../i18n';
import { knowledgeRepository } from '../knowledge';

interface HospitalityLandingProps {
  onSelectVessel: (slug: string) => void;
  onExploreCabin: (slug: string, cabinNumber: string) => void;
}

/**
 * Landing page with a single conversion goal: a first-time visitor who just
 * booked a cruise must understand — in five seconds, without scrolling — that
 * this tells them about their exact cabin, and be able to act. Utility first;
 * trust and philosophy come only after the product is understood.
 */

const bellissimaShip = knowledgeRepository.getShip('msc-bellissima');
const bellissimaDeck14 = knowledgeRepository.getDeck('msc-bellissima', 14);

/** Real, source-backed facts for the demonstration cabin (MSC Bellissima 14122). */
const EXAMPLE = {
  slug: bellissimaShip.vessel_id,
  ship: bellissimaShip.vessel_name,
  cabin: '14122',
  deck: `14 · ${bellissimaDeck14 ? bellissimaDeck14.name.replace('Deck 14 (', '').replace(')', '') : 'World Class'}`,
  side: { en: 'Starboard (right)', de: 'Steuerbord (rechts)' },
  liftSteps: 17,
  buffetSteps: 35,
  theatreSteps: 302,
  gangway: 'Deck 5',
  turn: { en: 'Turn right off the lift', de: 'Am Aufzug rechts abbiegen' },
  noise: { en: 'Buffet on the deck above', de: 'Buffet auf dem Deck darüber' },
};

export const HospitalityLanding: React.FC<HospitalityLandingProps> = ({ onSelectVessel, onExploreCabin }) => {
  const { isGerman } = useI18n();
  const [shipSlug, setShipSlug] = useState<string>(bellissimaShip.vessel_id);
  const [cabin, setCabin] = useState<string>('');

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const c = cabin.trim();
    if (c) onExploreCabin(shipSlug, c);
    else onSelectVessel(shipSlug);
  };

  const openExample = () => onExploreCabin(EXAMPLE.slug, EXAMPLE.cabin);

  return (
    <div>
      {/* ── SECTION 1 · HERO — What is it? Who is it for? Act now. ───────── */}
      <section className="relative overflow-hidden border-b border-slate-200/80">
        <div className="absolute inset-0 pointer-events-none select-none z-0 overflow-hidden">
          <img
            src="/hero-cruise-mist.webp"
            alt=""
            fetchPriority="high"
            decoding="async"
            className="absolute right-0 top-0 h-full w-full sm:w-[70%] object-cover object-[65%_center] opacity-80 mix-blend-multiply"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#f4f2ed] via-[#f4f2ed]/90 to-[#f4f2ed]/20" />
        </div>

        <div className="relative z-10 page-shell pt-14 pb-16 md:pt-20 md:pb-20 grid lg:grid-cols-[1.1fr_0.9fr] gap-12 items-center">
          {/* Left: message + primary action */}
          <div>
            <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl font-normal tracking-tight text-[#0c1b2a] leading-[1.05] max-w-xl">
              {isGerman ? 'Kenne deine Kabine, bevor du an Bord gehst.' : 'Know your cabin before you board.'}
            </h1>
            <p className="mt-5 text-lg text-slate-600 font-light max-w-md leading-relaxed">
              {isGerman
                ? 'Finde deine Kabine. Verstehe dein Schiff. Geh sicher an Bord.'
                : 'Find your cabin. Understand your ship. Board with confidence.'}
            </p>

            {/* Primary action — no scrolling required */}
            <form onSubmit={submit} className="mt-8 bg-white border border-ink/10 rounded-xs shadow-sm p-4 max-w-md">
              <div className="flex flex-col sm:flex-row gap-3">
                <label className="flex-1">
                  <span className="block text-[11px] uppercase tracking-wider text-muted font-semibold mb-1">
                    {isGerman ? 'Kabinennummer' : 'Cabin number'}
                  </span>
                  <input
                    value={cabin}
                    onChange={(e) => setCabin(e.target.value)}
                    inputMode="numeric"
                    placeholder="14122"
                    aria-label={isGerman ? 'Kabinennummer' : 'Cabin number'}
                    className="w-full h-11 border border-ink/15 rounded-xs px-3 font-mono text-sm text-ink outline-none focus:border-gold"
                  />
                </label>
                <label className="sm:w-44">
                  <span className="block text-[11px] uppercase tracking-wider text-muted font-semibold mb-1">
                    {isGerman ? 'Schiff' : 'Ship'}
                  </span>
                  <select
                    value={shipSlug}
                    onChange={(e) => setShipSlug(e.target.value)}
                    aria-label={isGerman ? 'Schiff wählen' : 'Choose ship'}
                    className="w-full h-11 border border-ink/15 rounded-xs px-2 text-sm text-ink bg-white outline-none focus:border-gold"
                  >
                    {FLEET_REGISTRY.map((v) => (
                      <option key={v.slug} value={v.slug}>{v.name}</option>
                    ))}
                  </select>
                </label>
              </div>
              <button
                type="submit"
                className="mt-3 w-full h-11 bg-[#0c1b2a] text-white text-sm font-medium rounded-xs hover:bg-slate-800 transition-colors inline-flex items-center justify-center gap-2 cursor-pointer"
              >
                {isGerman ? 'Meine Kreuzfahrt erkunden' : 'Explore my cruise'}
                <ArrowRight className="w-4 h-4 text-amber-300" />
              </button>
            </form>
          </div>

          {/* Right: a real cabin, demonstrated (not explained) */}
          <button
            onClick={openExample}
            className="text-left bg-white border border-ink/10 rounded-xs shadow-md p-6 hover:border-ink/30 transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-between border-b border-ink/8 pb-3">
              <div>
                <div className="text-[11px] uppercase tracking-wider text-gold font-semibold">
                  {isGerman ? 'Beispiel' : 'Example'}
                </div>
                <div className="font-serif text-2xl text-ink leading-tight">{isGerman ? 'Kabine' : 'Cabin'} {EXAMPLE.cabin}</div>
                <div className="text-xs text-muted">{EXAMPLE.ship}</div>
              </div>
              <ArrowRight className="w-4 h-4 text-muted" aria-hidden />
            </div>
            <ul className="mt-4 space-y-2 text-[13px] text-ink/85">
              <li>• {isGerman ? 'Deck 14 · Steuerbord (rechts)' : 'Deck 14 · Starboard (right)'}</li>
              <li>• {isGerman ? `${EXAMPLE.liftSteps} Schritte zum Aufzug · ${EXAMPLE.buffetSteps} zum Buffet` : `${EXAMPLE.liftSteps} steps to the lift · ${EXAMPLE.buffetSteps} to the buffet`}</li>
              <li>• {isGerman ? EXAMPLE.turn.de : EXAMPLE.turn.en}</li>
              <li>• {isGerman ? EXAMPLE.noise.de : EXAMPLE.noise.en}</li>
              <li>• {isGerman ? `Landgang über ${EXAMPLE.gangway}` : `Gangway on ${EXAMPLE.gangway}`}</li>
            </ul>
            <span className="mt-4 inline-flex items-center gap-1.5 text-[13px] text-ink font-medium">
              {isGerman ? 'Vollständige Übersicht öffnen' : 'Open full briefing'} <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </button>
        </div>
      </section>

      {/* ── SECTION 2 · What do I get? (real questions) ──────────────────── */}
      <section className="page-shell py-16 md:py-20">
        <h2 className="font-serif text-3xl md:text-4xl text-ink font-normal">
          {isGerman ? 'Was Timonelo dir sagt' : 'What Timonelo tells you'}
        </h2>
        <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { icon: Volume2, en: 'Is my cabin quiet?', de: 'Ist meine Kabine ruhig?' },
            { icon: DoorOpen, en: 'Which lift should I use?', de: 'Welchen Aufzug nehme ich?' },
            { icon: Compass, en: 'Which direction do I turn?', de: 'In welche Richtung biege ich ab?' },
            { icon: Footprints, en: 'How far to the buffet?', de: 'Wie weit zum Buffet?' },
            { icon: MapPin, en: 'Which deck do I board from?', de: 'Über welches Deck gehe ich an Bord?' },
            { icon: Waves, en: 'Which side is my balcony?', de: 'Auf welcher Seite liegt mein Balkon?' },
          ].map((q) => (
            <button
              key={q.en}
              onClick={openExample}
              className="text-left flex items-center gap-3 bg-white border border-ink/8 rounded-xs p-4 hover:border-ink/30 transition-colors cursor-pointer"
            >
              <q.icon className="w-5 h-5 text-gold shrink-0" strokeWidth={1.6} aria-hidden />
              <span className="text-[15px] text-ink">{isGerman ? q.de : q.en}</span>
            </button>
          ))}
        </div>
      </section>

      {/* ── SECTION 3 · Show me (one real cabin) ─────────────────────────── */}
      <section className="bg-white border-y border-ink/8">
        <div className="page-shell py-16 md:py-20">
          <h2 className="font-serif text-3xl md:text-4xl text-ink font-normal">
            {isGerman ? 'Das bekommst du' : 'This is what you receive'}
          </h2>
          <p className="mt-2 text-muted text-[15px] max-w-2xl">
            {isGerman
              ? 'Eine echte Kabinen-Übersicht — Beispiel: Kabine 14122 auf der MSC Bellissima.'
              : 'A real cabin briefing — example: Cabin 14122 on MSC Bellissima.'}
          </p>
          <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-ink/8 border border-ink/8 rounded-xs overflow-hidden">
            {[
              { k: isGerman ? 'Deck' : 'Deck', v: EXAMPLE.deck },
              { k: isGerman ? 'Balkonseite' : 'Balcony side', v: isGerman ? EXAMPLE.side.de : EXAMPLE.side.en },
              { k: isGerman ? 'Nächster Aufzug' : 'Nearest lift', v: `${EXAMPLE.liftSteps} ${isGerman ? 'Schritte' : 'steps'}` },
              { k: isGerman ? 'Zum Buffet' : 'To the buffet', v: `${EXAMPLE.buffetSteps} ${isGerman ? 'Schritte' : 'steps'}` },
              { k: isGerman ? 'Zum Theater' : 'To the theatre', v: `${EXAMPLE.theatreSteps} ${isGerman ? 'Schritte' : 'steps'}` },
              { k: isGerman ? 'Über dir' : 'Above you', v: isGerman ? EXAMPLE.noise.de : EXAMPLE.noise.en },
            ].map((row) => (
              <div key={row.k} className="bg-white p-5">
                <div className="text-[11px] uppercase tracking-wider text-muted font-semibold">{row.k}</div>
                <div className="text-[15px] font-medium text-ink mt-1">{row.v}</div>
              </div>
            ))}
          </div>
          <button
            onClick={openExample}
            className="mt-8 inline-flex items-center gap-2 px-6 py-3 bg-[#0c1b2a] text-white text-sm font-medium rounded-xs hover:bg-slate-800 transition-colors cursor-pointer"
          >
            {isGerman ? 'Vollständige Übersicht öffnen' : 'Open full briefing'} <ArrowRight className="w-4 h-4 text-amber-300" />
          </button>
        </div>
      </section>

      {/* ── SECTION 4 · How it works ─────────────────────────────────────── */}
      <section className="page-shell py-16 md:py-20">
        <h2 className="font-serif text-3xl md:text-4xl text-ink font-normal">
          {isGerman ? 'So funktioniert es' : 'How it works'}
        </h2>
        <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { en: 'Choose your ship', de: 'Schiff wählen' },
            { en: 'Enter your cabin', de: 'Kabine eingeben' },
            { en: 'Receive your briefing', de: 'Übersicht erhalten' },
            { en: 'Board with confidence', de: 'Sicher an Bord' },
          ].map((s, i) => (
            <div key={s.en} className="bg-white border border-ink/8 rounded-xs p-5">
              <div className="font-mono text-sm text-gold">{i + 1}</div>
              <div className="text-[15px] text-ink mt-2">{isGerman ? s.de : s.en}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── SECTION 5 · Why trust it (Tim = trust, not the product) ──────── */}
      <section className="bg-[#0c1b2a] text-white">
        <div className="page-shell py-14 md:py-16 flex flex-col md:flex-row md:items-center gap-6">
          <ShieldCheck className="w-8 h-8 text-gold shrink-0" strokeWidth={1.5} aria-hidden />
          <div>
            <h2 className="font-serif text-2xl md:text-3xl font-normal">
              {isGerman ? 'Warum du dich darauf verlassen kannst' : 'Why you can trust it'}
            </h2>
            <p className="mt-2 text-white/75 text-[15px] leading-relaxed max-w-2xl font-light">
              {isGerman
                ? 'Bridge Officer Tim zeigt nur, was die Schiffspläne belegen — modelliert aus den geprüften Meraviglia-Klasse-Referenzplänen. Was unbekannt ist, bleibt klar als Unbekannt markiert.'
                : 'Bridge Officer Tim shows only what the ship’s plans support — modelled from the verified Meraviglia-class reference plans. Anything unknown stays clearly marked Unknown.'}
            </p>
          </div>
        </div>
      </section>

      {/* ── SECTION 6 · Philosophy (supporting, near the footer) ─────────── */}
      <section className="page-shell py-12 text-center">
        <p className="text-muted text-[14px] max-w-xl mx-auto leading-relaxed">
          {isGerman
            ? 'Timonelo ist unabhängig und evidenzbasiert — keine Werbung, kein Affiliate-Tracking. Ruhige Gewissheit statt Lärm.'
            : 'Timonelo is independent and evidence-first — no advertising, no affiliate tracking. Quiet certainty over noise.'}
        </p>
      </section>
    </div>
  );
};
