/** Explorer shell: a restrained top bar and breadcrumb. No dashboard chrome. */
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export function Mark() {
  return (
    <Link to="/" className="flex items-center gap-2 shrink-0">
      <span className="w-5 h-5 bg-navy flex items-center justify-center">
        <span className="w-0.5 h-2.5 bg-white rotate-45" />
      </span>
      <span className="font-semibold text-[15px] tracking-tight uppercase text-navy">Timonelo</span>
    </Link>
  );
}

export function TopBar({ right }: { right?: ReactNode }) {
  return (
    <nav className="sticky top-0 z-40 bg-paper/85 backdrop-blur border-b border-line">
      <div className="max-w-6xl mx-auto px-5 md:px-8 h-14 flex items-center justify-between">
        <Mark />
        <div className="flex items-center gap-6">
          <Link to="/explore" className="eyebrow hover:text-navy transition-colors">
            Explore
          </Link>
          {right}
        </div>
      </div>
    </nav>
  );
}

export interface Crumb {
  label: string;
  to?: string;
}

export function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 flex-wrap text-[12px]">
      {items.map((c, i) => {
        const last = i === items.length - 1;
        return (
          <span key={i} className="flex items-center gap-2">
            {c.to && !last ? (
              <Link to={c.to} className="text-mist hover:text-navy transition-colors uppercase tracking-[0.12em] font-semibold">
                {c.label}
              </Link>
            ) : (
              <span className="text-navy uppercase tracking-[0.12em] font-semibold">{c.label}</span>
            )}
            {!last && <ChevronRight className="w-3 h-3 text-fog" aria-hidden />}
          </span>
        );
      })}
    </nav>
  );
}

export function Shell({ children }: { children: ReactNode }) {
  return <div className="explorer min-h-screen bg-paper text-ink">{children}</div>;
}
