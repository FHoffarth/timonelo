import { Link, useParams } from 'react-router-dom';
import { DoorOpen, ArrowUp, ArrowDown, Volume2 } from 'lucide-react';
import { usePack, type Cabin, type Deck, type PackModel } from './pack';
import { areaKindLabel } from './format';
import { Shell, TopBar, Breadcrumb } from './ExplorerChrome';
import { Eyebrow, Loading, KnowledgeLedger, SourceBadge } from './ui';
import { DeckRail } from './DeckRail';
import { SiteFooter } from './ShipPage';

export default function DeckPage() {
  const { shipId = 'msc-meraviglia', deck = '' } = useParams();
  const { model, error } = usePack(shipId);

  if (error || !model) return <Shell><TopBar /><Loading what="the deck" /></Shell>;

  const deckNum = Number(deck);
  const d = model.deck(deckNum);
  if (!d) return <Shell><TopBar /><Loading what="the deck" /></Shell>;

  const cabins = model.cabinsOnDeck(d.entity_id);
  const areas = model.areasOnDeck(d.entity_id);
  const above = model.deckAbove(d.entity_id);
  const below = model.deckBelow(d.entity_id);
  const source = model.primarySource;

  const withNoise = cabins.filter((c) => model.claim(c.entity_id, 'noise_exposure')).length;

  return (
    <Shell>
      <TopBar />
      <main className="max-w-6xl mx-auto px-5 md:px-8">
        <div className="py-6 border-b border-line">
          <Breadcrumb
            items={[
              { label: 'Explore', to: '/explore' },
              { label: model.ship.name, to: `/ship/${shipId}` },
              { label: `Deck ${d.number}` },
            ]}
          />
        </div>

        <div className="grid lg:grid-cols-[15rem_1fr] gap-10 lg:gap-16 py-10">
          <aside>
            <DeckRail model={model} shipId={shipId} current={deckNum} />
          </aside>

          <div className="min-w-0">
            <header className="mb-10">
              <Eyebrow>Deck {d.number}</Eyebrow>
              <h1 className="font-serif text-4xl md:text-6xl text-navy mt-3 leading-none">{d.name}</h1>
              <div className="flex flex-wrap gap-x-8 gap-y-2 mt-6 text-[13px] text-mist">
                <span><span className="text-navy font-semibold">{cabins.length}</span> cabins</span>
                <span><span className="text-navy font-semibold">{areas.length}</span> public areas</span>
                <span>Deck ordinal <span className="text-navy font-semibold">{d.ordinal}</span></span>
              </div>
            </header>

            <Section eyebrow="Public areas" title="What shares this deck">
              {areas.length === 0 ? (
                <Empty>No public areas were located on this deck in the source plan.</Empty>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {areas.map((p) => (
                    <span
                      key={p.entity_id}
                      className="inline-flex items-center gap-2 border border-line bg-white px-3 py-1.5 text-[13px] text-navy-700"
                      title={areaKindLabel(p.kind)}
                    >
                      <DoorOpen className="w-3.5 h-3.5 text-fog" aria-hidden />
                      {p.name}
                      <span className="text-[10px] uppercase tracking-[0.1em] text-fog">
                        {areaKindLabel(p.kind)}
                      </span>
                    </span>
                  ))}
                </div>
              )}
            </Section>

            <Section eyebrow="Vertical connections" title="Decks directly above and below">
              <div className="grid sm:grid-cols-2 gap-3">
                <ConnCard dir="above" deck={above ?? null} model={model} shipId={shipId} />
                <ConnCard dir="below" deck={below ?? null} model={model} shipId={shipId} />
              </div>
            </Section>

            <Section
              eyebrow="Cabins"
              title={`${cabins.length} cabins on this deck`}
              aside={
                <span className="inline-flex items-center gap-1.5 text-[12px] text-mist">
                  <Volume2 className="w-3.5 h-3.5" /> {withNoise} with a noise source
                </span>
              }
            >
              <CabinGrid model={model} cabins={cabins} shipId={shipId} deck={deckNum} />
            </Section>

            <Section eyebrow="Evidence & limitations" title="What we know about this deck">
              <KnowledgeLedger
                know={`Every cabin and public area on Deck ${d.number} is a canonical entity located from the deck plan.`}
                how={
                  <>
                    Vector text and geometry were read directly from the plan. Noise exposure is a
                    deterministic derivation from structural proximity.
                  </>
                }
                dontKnow={
                  <>
                    Cabin category, view, balcony and dimensions are not present in a deck plan and
                    remain <span className="text-navy font-medium">Unknown</span>.
                  </>
                }
                source={
                  <span className="inline-flex items-center gap-2">
                    {source.title} <SourceBadge sourceType={source.source_type} />
                  </span>
                }
              />
            </Section>
          </div>
        </div>
      </main>
      <SiteFooter />
    </Shell>
  );
}

function Section({
  eyebrow,
  title,
  aside,
  children,
}: {
  eyebrow: string;
  title: string;
  aside?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-14">
      <div className="flex items-end justify-between gap-4 mb-5">
        <div>
          <Eyebrow>{eyebrow}</Eyebrow>
          <h2 className="font-serif text-2xl text-navy mt-2">{title}</h2>
        </div>
        {aside}
      </div>
      {children}
    </section>
  );
}

function ConnCard({
  dir,
  deck,
  model,
  shipId,
}: {
  dir: 'above' | 'below';
  deck: Deck | null;
  model: PackModel;
  shipId: string;
}) {
  const Icon = dir === 'above' ? ArrowUp : ArrowDown;
  if (!deck) {
    return (
      <div className="card p-5 flex items-center gap-3 text-mist">
        <Icon className="w-4 h-4 text-fog" aria-hidden />
        <span className="text-[13px]">Nothing {dir} — this is an outer deck.</span>
      </div>
    );
  }
  const count = model.cabinsOnDeck(deck.entity_id).length;
  return (
    <Link
      to={`/ship/${shipId}/deck/${deck.number}`}
      className="group card p-5 flex items-center justify-between hover:border-sea transition-colors"
    >
      <div className="flex items-center gap-3">
        <Icon className="w-4 h-4 text-brass" aria-hidden />
        <div>
          <div className="text-[11px] uppercase tracking-[0.14em] text-fog">Deck {dir}</div>
          <div className="text-[15px] text-navy font-medium">
            Deck {deck.number} · {deck.name}
          </div>
        </div>
      </div>
      <span className="text-[12px] text-mist">{count} cabins</span>
    </Link>
  );
}

function CabinGrid({
  model,
  cabins,
  shipId,
  deck,
}: {
  model: PackModel;
  cabins: Cabin[];
  shipId: string;
  deck: number;
}) {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-8 gap-2">
      {cabins.map((c) => {
        const noisy = !!model.claim(c.entity_id, 'noise_exposure');
        return (
          <Link
            key={c.entity_id}
            to={`/ship/${shipId}/deck/${deck}/cabin/${c.number}`}
            className="group relative border border-line bg-white px-2 py-2.5 text-center hover:border-sea hover:bg-[#f7fafb] transition-colors"
            title={noisy ? 'Has a noise source' : undefined}
          >
            <span className="font-mono text-[13px] text-navy-700 group-hover:text-navy">{c.number}</span>
            {noisy && (
              <span
                className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-brass"
                aria-label="noise source"
              />
            )}
          </Link>
        );
      })}
    </div>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="text-[14px] text-mist italic">{children}</div>;
}
