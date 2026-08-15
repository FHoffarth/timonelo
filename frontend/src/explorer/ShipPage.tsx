import { Link, useParams } from 'react-router-dom';
import { ArrowRight, Layers, Anchor, DoorOpen } from 'lucide-react';
import { usePack } from './pack';
import { maturityLabel } from './format';
import { Shell, TopBar, Breadcrumb } from './ExplorerChrome';
import { Eyebrow, Stat, MaturityLadder, SourceBadge, Divider, Loading, ExploreLink } from './ui';

export default function ShipPage() {
  const { shipId = 'msc-meraviglia' } = useParams();
  const { model, error } = usePack(shipId);

  if (error) return <NotFound message={error} />;
  if (!model) return <Shell><TopBar /><Loading what="the ship" /></Shell>;

  const { ship } = model;
  const pack = model.pack;
  const source = model.primarySource;
  const decks = model.decksTopToBottom();

  const deckCount = pack.decks.length;
  const cabinCount = ship.cabin_count ?? pack.cabins.length;
  const areaCount = pack.public_areas.length;
  const elevators = model.claim(ship.entity_id, 'elevator_count')?.value as number | undefined;

  return (
    <Shell>
      <TopBar />

      <header className="chart-bg text-white">
        <ChartLines />
        <div className="relative max-w-6xl mx-auto px-5 md:px-8 pt-16 pb-20 md:pt-24 md:pb-28">
          <Eyebrow>
            <span className="text-brass-soft">{ship.operator_name}</span>
          </Eyebrow>
          <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl leading-[0.98] mt-5 max-w-4xl">
            {ship.name}
          </h1>
          <p className="text-[15px] md:text-lg text-white/70 max-w-xl mt-6 leading-relaxed font-light">
            {deckCount} decks, {cabinCount.toLocaleString()} cabins and {areaCount} public areas —
            mapped from ship geometry, with every claim traceable to its source.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              to={`/ship/${shipId}/deck/${decks[0].number}`}
              className="inline-flex items-center gap-2 bg-white text-navy px-6 py-3.5 text-[13px] font-semibold tracking-wide hover:bg-brass-soft transition-colors"
            >
              Explore decks <ArrowRight className="w-4 h-4" />
            </Link>
            <span className="text-[12px] text-white/55 uppercase tracking-[0.15em]">
              Pack v{pack.version} · {maturityLabel(pack.status)}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-5 md:px-8">
        <div className="py-6 border-b border-line">
          <Breadcrumb items={[{ label: 'Explore', to: '/explore' }, { label: ship.name }]} />
        </div>

        <section className="py-14">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-y-12 gap-x-6">
            <Stat value={deckCount} label="Decks mapped" />
            <Stat value={cabinCount.toLocaleString()} label="Cabins located" />
            <Stat value={areaCount} label="Public areas" />
            <Stat value={elevators ?? '—'} label="Elevators" />
            <Stat value={model.pack.relationships.length} label="Structural relationships" />
            <Stat value={model.pack.claims.length.toLocaleString()} label="Evidence claims" />
            <Stat value={model.pack.sources.length} label="Sources" />
            <Stat value={<span className="text-mint">100%</span>} label="Claims with provenance" />
          </div>
        </section>

        <Divider />

        <section className="grid lg:grid-cols-[1fr_1fr] gap-12 lg:gap-20 pb-16">
          <div>
            <Eyebrow>Knowledge Pack</Eyebrow>
            <h2 className="font-serif text-3xl text-navy mt-3 mb-6 leading-tight">
              What Timonelo can stand behind
            </h2>
            <MaturityLadder maturity={pack.status} />
            <p className="text-[14px] text-mist leading-relaxed mt-5">{pack.limitations[0]}</p>
            <dl className="mt-8 grid grid-cols-2 gap-y-5 text-[13px]">
              <dt className="text-fog uppercase tracking-[0.12em] text-[11px]">Pack id</dt>
              <dd className="text-navy font-mono text-[12px] break-all">{pack.pack_id}</dd>
              <dt className="text-fog uppercase tracking-[0.12em] text-[11px]">Version</dt>
              <dd className="text-navy font-medium">v{pack.version}</dd>
              <dt className="text-fog uppercase tracking-[0.12em] text-[11px]">Effective</dt>
              <dd className="text-navy">{pack.effective_date}</dd>
              <dt className="text-fog uppercase tracking-[0.12em] text-[11px]">Schema</dt>
              <dd className="text-navy">canonical v{pack.schema_version}</dd>
            </dl>
          </div>

          <div>
            <Eyebrow>Source summary</Eyebrow>
            <h2 className="font-serif text-3xl text-navy mt-3 mb-6 leading-tight">
              Where the knowledge comes from
            </h2>
            <div className="card p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-[15px] font-medium text-navy">{source.title}</div>
                  <div className="text-[13px] text-mist mt-1">{source.publisher}</div>
                </div>
                <SourceBadge sourceType={source.source_type} />
              </div>
              <div className="h-px bg-line my-5" />
              <ul className="space-y-2">
                {source.limitations.map((l, i) => (
                  <li key={i} className="text-[12px] text-mist leading-relaxed flex gap-2">
                    <span className="text-fog">—</span>
                    <span>{l}</span>
                  </li>
                ))}
              </ul>
            </div>
            <p className="text-[13px] text-mist leading-relaxed mt-5">
              Trust is more important than completeness. Timonelo shows the evidence and its limits
              rather than implying a certainty it has not earned.
            </p>
          </div>
        </section>

        <Divider />

        <section className="pb-24">
          <div className="flex items-end justify-between mb-8 flex-wrap gap-4">
            <div>
              <Eyebrow>Begin exploring</Eyebrow>
              <h2 className="font-serif text-3xl md:text-4xl text-navy mt-3 leading-tight">
                {deckCount} decks, top to keel
              </h2>
            </div>
            <div className="flex gap-4 text-[12px] text-mist">
              <span className="inline-flex items-center gap-1.5"><Layers className="w-3.5 h-3.5" /> Deck</span>
              <span className="inline-flex items-center gap-1.5"><Anchor className="w-3.5 h-3.5" /> Cabins</span>
              <span className="inline-flex items-center gap-1.5"><DoorOpen className="w-3.5 h-3.5" /> Areas</span>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {decks.map((d) => (
              <ExploreLink
                key={d.entity_id}
                to={`/ship/${shipId}/deck/${d.number}`}
                label={`Deck ${d.number} · ${d.name}`}
                sub={`${model.cabinsOnDeck(d.entity_id).length} cabins · ${model.areasOnDeck(d.entity_id).length} public areas`}
              />
            ))}
          </div>
        </section>
      </main>
      <SiteFooter />
    </Shell>
  );
}

function ChartLines() {
  return (
    <svg
      className="absolute inset-0 w-full h-full opacity-[0.13]"
      aria-hidden
      preserveAspectRatio="none"
      viewBox="0 0 1200 600"
    >
      {Array.from({ length: 9 }).map((_, i) => (
        <path
          key={i}
          d={`M0 ${60 + i * 62} C 300 ${20 + i * 62}, 900 ${120 + i * 62}, 1200 ${40 + i * 62}`}
          fill="none"
          stroke="#cbb489"
          strokeWidth="1"
        />
      ))}
    </svg>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-line">
      <div className="max-w-6xl mx-auto px-5 md:px-8 py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] uppercase tracking-[0.15em] text-fog">
        <span>© {new Date().getFullYear()} Timonelo</span>
        <span className="tracking-[0.2em] text-mist">Never more certain than the evidence.</span>
      </div>
    </footer>
  );
}

function NotFound({ message }: { message: string }) {
  return (
    <Shell>
      <TopBar />
      <div className="max-w-2xl mx-auto px-6 py-32 text-center">
        <div className="eyebrow">Not found</div>
        <h1 className="font-serif text-4xl text-navy mt-4">This ship isn’t in the library yet</h1>
        <p className="text-mist mt-4">{message}</p>
        <Link to="/explore" className="inline-block mt-8 text-sea font-medium">
          ← Back to the Explorer
        </Link>
      </div>
    </Shell>
  );
}
