import { UPCOMING_EXPANSIONS } from '../fleet';

export function ComingSoonSection() {
  return (
    <section className="section-space border-t border-ink/8 bg-paper/60">
      <div className="page-shell">
        <div className="max-w-2xl mb-12">
          <p className="eyebrow text-muted/70 tracking-widest uppercase">Expanding Horizon</p>
          <h2 className="section-title text-3xl sm:text-4xl md:text-5xl mt-2 font-normal">
            Upcoming Ship Ingestions
          </h2>
          <p className="text-muted text-[15px] leading-relaxed mt-3">
            Timonelo continues to ingest and verify deck plans across major ocean and river operators:
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {UPCOMING_EXPANSIONS.map((line) => (
            <div
              key={line.name}
              className="card p-6 bg-white/70 border border-ink/8 hover:border-ink/20 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] uppercase font-mono tracking-wider text-muted/70">
                    {line.category}
                  </span>
                  <span className="text-[10px] font-mono text-gold font-medium">
                    In Modeling
                  </span>
                </div>
                <h3 className="font-display text-xl text-ink font-normal">{line.name}</h3>
                <p className="text-[12px] text-muted mt-1">{line.region}</p>
                <p className="text-[12px] text-muted/80 mt-2.5 leading-relaxed font-sans border-t border-ink/6 pt-2.5">
                  {line.note}
                </p>
              </div>

              <div className="mt-4 pt-2 text-[11px] text-muted/60 font-mono flex items-center justify-between">
                <span>Spatial Modeling</span>
                <span className="text-ink/60">Coming Soon</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
