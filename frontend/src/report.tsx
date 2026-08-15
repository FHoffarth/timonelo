/**
 * Cabin Orientation Report — a dedicated, print/PDF-first document (Plane 5).
 * Not the web interface: an official orientation dossier a passenger can print,
 * save as a searchable A4 PDF, or share. Architectural, calm, evidence-first.
 */
import { useState } from 'react';
import { Printer, FileDown, Share2, Link as LinkIcon, Check } from 'lucide-react';
import type { ShipData, CabinData } from './types';
import { categoryLabel, canonicalPath, shareBriefing, copyLink } from './share';

export const REPORT_VERSION = '1.0';
export type LensId = 'accessibility' | 'family' | 'quiet';

function sideLabel(s: CabinData['hull_side']): string {
  return s === 'STARBOARD' ? 'Starboard' : s === 'PORT' ? 'Port' : 'Centreline';
}
function longitudinal(zone: string): string {
  const z = zone.toLowerCase();
  if (z.includes('aft')) return 'Aft';
  if (z.includes('forward') || z.includes('bow')) return 'Forward';
  return 'Midship';
}
function zoneFraction(zone: string): number {
  const z = zone.toLowerCase();
  const fwd = z.includes('forward') || z.includes('bow');
  const aft = z.includes('aft');
  if (z.includes('midship') && aft) return 0.36;
  if (z.includes('midship') && fwd) return 0.64;
  if (aft) return 0.22;
  if (fwd) return 0.78;
  return 0.5;
}
function fmtDate(d: Date): string {
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
}

/* ------------------------------------------------------------- export bar */

export function ExportBar({ ship, cabin }: { ship: ShipData; cabin: CabinData }) {
  const [msg, setMsg] = useState<string | null>(null);
  const flash = (m: string) => {
    setMsg(m);
    window.setTimeout(() => setMsg(null), 2200);
  };

  return (
    <div className="no-print flex flex-wrap items-center gap-2" role="group" aria-label="Export cabin briefing">
      <button onClick={() => window.print()} className="inline-flex items-center gap-2 bg-ink text-white px-4 py-2.5 text-[13px] font-semibold hover:bg-ink/90 transition-colors">
        <FileDown className="w-4 h-4" aria-hidden /> Save PDF
      </button>
      <button onClick={() => window.print()} className="inline-flex items-center gap-2 border border-ink/20 bg-white px-4 py-2.5 text-[13px] font-medium text-ink hover:border-ink/50 transition-colors">
        <Printer className="w-4 h-4" aria-hidden /> Print
      </button>
      <button
        onClick={async () => {
          const r = await shareBriefing(ship, cabin);
          flash(r === 'shared' ? 'Shared' : r === 'copied' ? 'Link copied' : 'Sharing unavailable');
        }}
        className="inline-flex items-center gap-2 border border-ink/20 bg-white px-4 py-2.5 text-[13px] font-medium text-ink hover:border-ink/50 transition-colors"
      >
        <Share2 className="w-4 h-4" aria-hidden /> Share
      </button>
      <button
        onClick={async () => flash((await copyLink(cabin.cabin_number)) ? 'Link copied' : 'Copy failed')}
        className="inline-flex items-center gap-2 border border-ink/20 bg-white px-4 py-2.5 text-[13px] font-medium text-ink hover:border-ink/50 transition-colors"
      >
        <LinkIcon className="w-4 h-4" aria-hidden /> Copy link
      </button>
      <span aria-live="polite" className="text-[12px] text-muted min-w-[6rem]">
        {msg && (
          <span className="inline-flex items-center gap-1.5 text-emerald-800">
            <Check className="w-3.5 h-3.5" aria-hidden /> {msg}
          </span>
        )}
      </span>
    </div>
  );
}

/* ------------------------------------------------------------- the document */

export function CabinReport({ ship, cabin, lens }: { ship: ShipData; cabin: CabinData; lens: LensId }) {
  const now = new Date();
  const elevation = ship.decks[String(cabin.deck_number)]?.elevation_m ?? null;
  const evidenceVersion = cabin.evidence[0]?.source_id ?? 'Unknown';

  return (
    <article className="report-doc" aria-label="Cabin Orientation Report">
      {/* Masthead */}
      <header className="report-section">
        <div className="flex items-center justify-between">
          <span className="r-eyebrow">Timonelo · Cabin Orientation Report</span>
          <span className="r-eyebrow">Report v{REPORT_VERSION}</span>
        </div>
        <div className="r-rule mt-2 mb-4" />
        <h1 className="r-serif" style={{ fontSize: '26pt', lineHeight: 1.05, margin: 0 }}>
          {ship.name} · Cabin {cabin.cabin_number}
        </h1>
        <div className="grid grid-cols-4 gap-4 mt-4">
          <Field label="Ship" value={ship.name} />
          <Field label="Cabin" value={cabin.cabin_number} />
          <Field label="Category" value={categoryLabel(cabin)} />
          <Field label="Deck" value={`${cabin.deck_number} · ${cabin.deck_name}`} />
        </div>
        <div className="flex justify-between mt-3 text-[9pt]" style={{ color: '#555' }}>
          <span>Generated {fmtDate(now)}</span>
          <span>IMO {ship.imo.replace('IMO', '')}</span>
        </div>
      </header>

      {/* Section 1 — Cabin Summary */}
      <Section n="01" title="Cabin Summary">
        <table>
          <tbody>
            <Row k="Deck" v={`Deck ${cabin.deck_number} (${cabin.deck_name})`} />
            <Row k="Longitudinal position" v={`${longitudinal(cabin.zone)} · ${cabin.zone}`} />
            <Row k="Ship side" v={`${sideLabel(cabin.hull_side)} (${cabin.hull_side === 'STARBOARD' ? 'right' : cabin.hull_side === 'PORT' ? 'left' : 'centre'})`} />
            <Row k="Living area" v={`${cabin.square_meters} m²`} />
            <Row k="Balcony" v={cabin.balcony_type.replace(/_/g, ' ').toLowerCase()} />
          </tbody>
        </table>
      </Section>

      {/* Section 2 — Spatial Orientation */}
      <Section n="02" title="Spatial Orientation">
        <div className="grid grid-cols-[1.3fr_1fr] gap-6 items-start">
          <HullDiagram frac={zoneFraction(cabin.zone)} cabinNumber={cabin.cabin_number} />
          <table>
            <tbody>
              <Row k="Deck position" v={elevation != null ? `Deck ${cabin.deck_number} · ${elevation} m above sea` : `Deck ${cabin.deck_number}`} />
              <Row k="Relative location" v={`${longitudinal(cabin.zone)}, ${sideLabel(cabin.hull_side).toLowerCase()} side`} />
              <Row k="Orientation" v={`${sideLabel(cabin.hull_side)}-facing balcony; solar aspect varies with heading`} />
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-[10pt]" style={{ color: '#333' }}>
          <strong>Orientation notes.</strong> {cabin.sightlines.description}{' '}
          {cabin.sightlines.has_lifeboat_obstruction ? 'A lifeboat intersects the downward sightline.' : 'No lifeboat obstruction on the sightline.'}
        </p>
      </Section>

      {/* Section 3 — What Sits Around You */}
      <Section n="03" title="What Sits Around You">
        <table>
          <tbody>
            <Row k="Above" v={surround(cabin.surroundings.overhead)} />
            <Row k="Below" v={surround(cabin.surroundings.underfoot)} />
            <Row k="Adjacent (connecting)" v={cabin.connecting_cabin_number ? `Cabin ${cabin.connecting_cabin_number}` : 'None'} />
            <Row k="Nearest elevator" v={cabin.distances.elevator ? `${cabin.distances.elevator.meters} m (${cabin.distances.elevator.steps} steps)` : undefined} />
            <Row k="Nearest staircase" v={undefined} />
          </tbody>
        </table>
      </Section>

      {/* Section 4 — Walking Distances */}
      <Section n="04" title="Walking Distances">
        <table>
          <thead>
            <tr><th>Destination</th><th>Distance</th><th>Walking time</th><th>Steps</th></tr>
          </thead>
          <tbody>
            <DistRow label="Marketplace Buffet" d={cabin.distances.buffet} />
            <DistRow label="Pool" d={cabin.distances.pool} />
            <DistRow label="Theatre" d={cabin.distances.theater} />
            <DistRow label="Dining Room" d={cabin.distances.dining} />
            <DistRow label="Nearest Elevator" d={cabin.distances.elevator} />
          </tbody>
        </table>
        <p className="mt-2 text-[9pt]" style={{ color: '#666' }}>Distances are deterministic routes through the ship’s circulation graph. Unknown destinations are not yet mapped for this cabin.</p>
      </Section>

      {/* Section 5 — Traveler Lens (selected only) */}
      <Section n="05" title={`Traveler Lens · ${lens === 'accessibility' ? 'Accessibility' : lens === 'family' ? 'Family' : 'Quiet Cabin'}`}>
        <LensBlock cabin={cabin} lens={lens} />
      </Section>

      {/* Section 6 — Evidence */}
      <Section n="06" title="Evidence">
        <table>
          <thead>
            <tr><th>Source</th><th>Reference</th><th>Integrity (SHA-256)</th></tr>
          </thead>
          <tbody>
            {cabin.evidence.map((e) => (
              <tr key={e.source_id}>
                <td>{e.source_id}</td>
                <td>{e.locator.replace(/_/g, ' ')}</td>
                <td className="font-mono" style={{ fontSize: '7.5pt', wordBreak: 'break-all' }}>{e.sha256}</td>
              </tr>
            ))}
            <tr>
              <td>Verified photography</td>
              <td className="r-unknown" colSpan={2}>None on file — unknown</td>
            </tr>
          </tbody>
        </table>
      </Section>

      {/* Section 7 — Footer */}
      <footer className="report-section" style={{ marginTop: '16pt' }}>
        <div className="r-rule mb-3" />
        <div className="flex justify-between items-start text-[9pt]" style={{ color: '#555' }}>
          <div>
            <div className="r-serif" style={{ fontSize: '11pt', color: '#111' }}>Timonelo — Cabin Orientation Report</div>
            <div className="mt-1">Generated by the Timonelo Spatial Engine · Never more certain than the evidence.</div>
          </div>
          <div className="text-right">
            <div>Report v{REPORT_VERSION}</div>
            <div>Evidence: {evidenceVersion}</div>
            <div>Exported {now.toISOString().replace('T', ' ').slice(0, 16)} UTC</div>
            <div>timonelo.com{canonicalPath(ship, cabin.cabin_number)}</div>
          </div>
        </div>
      </footer>
    </article>
  );
}

/* --------------------------------------------------------------- fragments */

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="r-eyebrow" style={{ fontSize: '7.5pt' }}>{label}</div>
      <div style={{ fontSize: '11pt', fontWeight: 600, marginTop: '2pt' }}>{value}</div>
    </div>
  );
}

function Section({ n, title, children }: { n: string; title: string; children: React.ReactNode }) {
  return (
    <section className="report-section" style={{ marginTop: '18pt' }}>
      <div className="flex items-baseline gap-3">
        <span className="font-mono" style={{ fontSize: '8pt', color: '#888' }}>{n}</span>
        <h2 className="r-serif" style={{ fontSize: '14pt', margin: 0 }}>{title}</h2>
      </div>
      <div className="r-hair mt-1.5 mb-3" />
      {children}
    </section>
  );
}

function Row({ k, v }: { k: string; v: string | undefined }) {
  return (
    <tr>
      <th style={{ width: '42%' }}>{k}</th>
      <td className={v == null ? 'r-unknown' : ''}>{v ?? 'Unknown — not yet mapped'}</td>
    </tr>
  );
}

function DistRow({ label, d }: { label: string; d?: { meters: number; seconds: number; steps: number; step_free: boolean } }) {
  if (!d) {
    return (
      <tr>
        <td>{label}</td>
        <td className="r-unknown" colSpan={3}>Unknown — not yet mapped</td>
      </tr>
    );
  }
  return (
    <tr>
      <td>{label}{d.step_free ? '' : ' *'}</td>
      <td>{d.meters} m</td>
      <td>~{Math.round(d.seconds)} s</td>
      <td>{d.steps}</td>
    </tr>
  );
}

function surround(l: { deck_number: number | null; deck_name: string | null; venues: string[] }): string {
  if (l.venues.length > 0) return `Deck ${l.deck_number} (${l.deck_name}) — ${l.venues.join(', ')}`;
  return l.deck_number != null ? `Deck ${l.deck_number} (${l.deck_name}) — residential cabins` : 'Unknown';
}

function LensBlock({ cabin, lens }: { cabin: CabinData; lens: LensId }) {
  if (lens === 'accessibility') {
    const a = cabin.lenses.accessibility;
    return (
      <div>
        <p style={{ fontWeight: 600, fontSize: '11pt' }}>{a.is_certified ? 'Certified accessible stateroom' : 'Standard stateroom'}</p>
        <p style={{ fontSize: '10pt', color: '#333', marginTop: '3pt' }}>{a.summary}</p>
        <p style={{ fontSize: '10pt', marginTop: '3pt' }}>Step-free route to nearest elevator core: {a.lift_distance_m} m.</p>
      </div>
    );
  }
  if (lens === 'family') {
    const f = cabin.lenses.family;
    return (
      <div>
        <p style={{ fontWeight: 600, fontSize: '11pt' }}>{f.has_connecting ? 'Adjoining family pair' : 'Single stateroom'}</p>
        <p style={{ fontSize: '10pt', color: '#333', marginTop: '3pt' }}>{f.summary}</p>
        <p style={{ fontSize: '10pt', marginTop: '3pt' }}>Distance to youth club: {f.kids_club_distance_m} m{f.connecting_cabin ? ` · connects to Cabin ${f.connecting_cabin}` : ''}.</p>
      </div>
    );
  }
  const q = cabin.lenses.quiet;
  return (
    <div>
      <p style={{ fontWeight: 600, fontSize: '11pt' }}>{q.is_quiet_tier ? 'Acoustically buffered' : 'Near an active space'}</p>
      <p style={{ fontSize: '10pt', color: '#333', marginTop: '3pt' }}>{q.summary}</p>
      {q.acoustic_flags.length > 0 && (
        <ul style={{ fontSize: '10pt', marginTop: '4pt', paddingLeft: '14pt' }}>
          {q.acoustic_flags.map((f) => <li key={f}>{f}</li>)}
        </ul>
      )}
    </div>
  );
}

/** Grayscale line-art ship elevation with the cabin marked. Print-safe. */
function HullDiagram({ frac, cabinNumber }: { frac: number; cabinNumber: string }) {
  const x = 30 + frac * 300; // within 0..360 usable width
  return (
    <svg viewBox="0 0 380 150" width="100%" role="img" aria-label={`Ship elevation with cabin ${cabinNumber} marked`}>
      <text x="20" y="12" fontSize="7" fill="#888" letterSpacing="1">AFT</text>
      <text x="335" y="12" fontSize="7" fill="#888" letterSpacing="1">FWD</text>
      {/* hull outline (bow to the right) */}
      <path d="M20 40 L330 40 Q372 40 372 78 Q372 116 330 116 L20 116 Q10 78 20 40 Z" fill="none" stroke="#111" strokeWidth="1.5" />
      {/* deck lines */}
      {[58, 78, 98].map((y) => (
        <line key={y} x1="24" y1={y} x2="360" y2={y} stroke="#ccc" strokeWidth="1" />
      ))}
      {/* waterline */}
      <line x1="0" y1="128" x2="380" y2="128" stroke="#111" strokeWidth="1" strokeDasharray="3 3" />
      {/* cabin marker */}
      <circle cx={x} cy="52" r="4.5" fill="#111" />
      <line x1={x} y1="56" x2={x} y2="66" stroke="#111" strokeWidth="1" />
      <text x={x} y="76" fontSize="8" fill="#111" textAnchor="middle" fontFamily="monospace">{cabinNumber}</text>
    </svg>
  );
}
