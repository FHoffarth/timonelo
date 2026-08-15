/**
 * Shared Explorer UI. Editorial, maritime, premium. No dashboard chrome.
 * Components here never assert certainty the pack does not carry.
 */
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, CircleHelp } from 'lucide-react';
import { exposureTone, maturityLabel, maturityRung, MATURITY_LADDER, sourceTypeLabel } from './format';

export function Eyebrow({ children }: { children: ReactNode }) {
  return <div className="eyebrow">{children}</div>;
}

export function SectionHeader({
  eyebrow,
  title,
  intro,
}: {
  eyebrow?: string;
  title: string;
  intro?: string;
}) {
  return (
    <header className="mb-8 max-w-2xl">
      {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
      <h2 className="font-serif text-3xl md:text-4xl text-navy mt-3 leading-[1.1]">{title}</h2>
      {intro && <p className="text-mist text-[15px] leading-relaxed mt-4">{intro}</p>}
    </header>
  );
}

export function Divider() {
  return <div className="h-px bg-line my-12" />;
}

export function Pill({
  children,
  tone = 'neutral',
}: {
  children: ReactNode;
  tone?: 'neutral' | 'brass' | 'sea' | 'quiet';
}) {
  const tones: Record<string, string> = {
    neutral: 'border-line text-navy bg-white',
    brass: 'border-brass-soft text-amber bg-[#faf6ee]',
    sea: 'border-line-cool text-sea bg-[#f2f7fa]',
    quiet: 'border-line text-mist bg-paper-2',
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

/** A single evidence statistic — large numeral, quiet label. */
export function Stat({ value, label }: { value: ReactNode; label: string }) {
  return (
    <div>
      <div className="font-serif text-4xl md:text-5xl text-navy leading-none">{value}</div>
      <div className="eyebrow mt-3">{label}</div>
    </div>
  );
}

/** Maturity as a four-rung ladder — describes knowledge completeness, not quality. */
export function MaturityLadder({ maturity }: { maturity: string }) {
  const rung = maturityRung(maturity);
  return (
    <div>
      <div className="flex items-center gap-2">
        {MATURITY_LADDER.map((m, i) => {
          const reached = i + 1 <= rung;
          return (
            <div key={m} className="flex-1">
              <div
                className={`h-1 rounded-full ${reached ? 'bg-brass' : 'bg-line'}`}
                aria-hidden
              />
            </div>
          );
        })}
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="font-serif text-xl text-navy">{maturityLabel(maturity)}</span>
        <span className="text-[11px] text-fog uppercase tracking-[0.14em]">
          Rung {rung} of 4
        </span>
      </div>
    </div>
  );
}

export function SourceBadge({ sourceType }: { sourceType: string }) {
  return <Pill tone="sea">{sourceTypeLabel(sourceType)}</Pill>;
}

/** Exposure indicator. Neutral three-step weight, explicitly not a rating. */
export function ExposureMeter({ level, label }: { level: string | null; label: string }) {
  const tone = exposureTone(level);
  const filled = tone === 'high' ? 3 : tone === 'medium' ? 2 : tone === 'low' ? 1 : 0;
  const color =
    tone === 'unknown' ? 'bg-line' : tone === 'high' ? 'bg-amber' : tone === 'medium' ? 'bg-brass-soft' : 'bg-mint';
  return (
    <div className="flex items-center justify-between py-3 border-b border-line last:border-0">
      <span className="text-[13px] text-navy-700">{label}</span>
      <div className="flex items-center gap-3">
        <span className="text-[12px] text-mist w-16 text-right">
          {tone === 'unknown' ? 'Unknown' : tone[0].toUpperCase() + tone.slice(1)}
        </span>
        <div className="flex gap-1" aria-hidden>
          {[0, 1, 2].map((i) => (
            <div key={i} className={`w-5 h-1.5 rounded-full ${i < filled ? color : 'bg-line'}`} />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * The knowledge ledger — the transparency contract rendered on every page:
 * what we know, how, what we do not, where it came from.
 */
export function KnowledgeLedger({
  know,
  how,
  dontKnow,
  source,
}: {
  know: ReactNode;
  how: ReactNode;
  dontKnow: ReactNode;
  source: ReactNode;
}) {
  const rows: [string, ReactNode][] = [
    ['What we know', know],
    ['How we know it', how],
    ['What we do not know', dontKnow],
    ['Where it came from', source],
  ];
  return (
    <div className="card p-0 divide-y divide-line">
      {rows.map(([k, v]) => (
        <div key={k} className="grid grid-cols-1 sm:grid-cols-[9rem_1fr] gap-1 sm:gap-6 p-5 sm:p-6">
          <div className="eyebrow pt-0.5">{k}</div>
          <div className="text-[14px] text-navy-700 leading-relaxed">{v}</div>
        </div>
      ))}
    </div>
  );
}

/** Unknown treated as a first-class citizen, never hidden. */
export function UnknownList({
  items,
}: {
  items: { predicate: string; detail: string }[];
}) {
  return (
    <ul className="space-y-4">
      {items.map((u) => (
        <li key={u.predicate} className="flex gap-3">
          <CircleHelp className="w-4 h-4 text-fog shrink-0 mt-0.5" aria-hidden />
          <div>
            <div className="text-[13px] font-semibold text-navy capitalize">{u.predicate}</div>
            <div className="text-[13px] text-mist leading-relaxed">{u.detail}</div>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function ExploreLink({ to, label, sub }: { to: string; label: string; sub?: string }) {
  return (
    <Link
      to={to}
      className="group flex items-center justify-between gap-4 p-5 card hover:border-sea transition-colors"
    >
      <div>
        <div className="text-[15px] font-medium text-navy">{label}</div>
        {sub && <div className="text-[13px] text-mist mt-0.5">{sub}</div>}
      </div>
      <ArrowUpRight className="w-4 h-4 text-fog group-hover:text-sea transition-colors" aria-hidden />
    </Link>
  );
}

export function Loading({ what }: { what: string }) {
  return (
    <div className="min-h-[60vh] grid place-items-center">
      <div className="text-center">
        <div className="eyebrow">Timonelo</div>
        <div className="font-serif text-2xl text-navy mt-3">Opening {what}…</div>
      </div>
    </div>
  );
}
