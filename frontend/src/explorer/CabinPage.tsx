import { Link, useParams } from 'react-router-dom';
import { Compass, Anchor, Navigation, Volume2, MapPin } from 'lucide-react';
import {
  usePack,
  type Cabin,
  type Deck,
  type MotionProfile,
  type NoiseValue,
  type PackModel,
} from './pack';
import { metres, noiseSourceLabel, valueOrUnknown } from './format';
import { Shell, TopBar, Breadcrumb } from './ExplorerChrome';
import {
  Eyebrow,
  Pill,
  ExposureMeter,
  KnowledgeLedger,
  UnknownList,
  SourceBadge,
  Loading,
  ExploreLink,
} from './ui';
import { SiteFooter } from './ShipPage';

// Predicates a deck plan cannot cover — Unknown kept first-class.
const CABIN_UNKNOWNS = [
  { predicate: 'category', detail: 'Cabin category is not present in the deck-plan geometry.' },
  { predicate: 'view', detail: 'Exterior orientation and obstruction are not derivable from this source.' },
  { predicate: 'balcony', detail: 'Balcony presence and depth are not present in the source.' },
  { predicate: 'dimensions', detail: 'Cabin dimensions are not present in the source.' },
];

export default function CabinPage() {
  const { shipId = 'msc-meraviglia', cabin = '' } = useParams();
  const { model, error } = usePack(shipId);

  if (error || !model) return <Shell><TopBar /><Loading what="the cabin" /></Shell>;

  const c = model.cabin(cabin);
  const d = c ? model.pack.decks.find((x) => x.entity_id === c.deck_id) : undefined;
  if (!c || !d) return <Shell><TopBar /><Loading what="the cabin" /></Shell>;

  const source = model.source(c.source_ids[0]) ?? model.primarySource;
  const motionClaim = model.claim(c.entity_id, 'motion_profile');
  const motion = (motionClaim?.value ?? null) as MotionProfile | null;
  const noiseClaim = model.claim(c.entity_id, 'noise_exposure');
  const noise = (noiseClaim?.value ?? null) as NoiseValue | null;
  const above = model.deckAbove(d.entity_id);
  const below = model.deckBelow(d.entity_id);

  return (
    <Shell>
      <TopBar />
      <main className="max-w-5xl mx-auto px-5 md:px-8">
        <div className="py-6 border-b border-line">
          <Breadcrumb
            items={[
              { label: 'Explore', to: '/explore' },
              { label: model.ship.name, to: `/ship/${shipId}` },
              { label: `Deck ${d.number}`, to: `/ship/${shipId}/deck/${d.number}` },
              { label: `Cabin ${c.number}` },
            ]}
          />
        </div>

        {/* 1 — Identity */}
        <header className="py-12 md:py-16 border-b border-line">
          <Eyebrow>Cabin Briefing</Eyebrow>
          <div className="flex flex-wrap items-end gap-x-6 gap-y-3 mt-4">
            <h1 className="font-serif text-6xl md:text-8xl text-navy leading-none">{c.number}</h1>
            <div className="mb-2 flex flex-wrap gap-2">
              <Pill tone="neutral">Deck {d.number} · {d.name}</Pill>
              <Pill tone="quiet">{model.ship.name}</Pill>
            </div>
          </div>
          <p className="text-[15px] text-mist mt-6 max-w-xl leading-relaxed">
            Everything Timonelo can stand behind for this cabin — and, just as clearly, what it
            cannot yet tell you.
          </p>
        </header>

        <div className="grid lg:grid-cols-[1fr_18rem] gap-12 lg:gap-16 py-12">
          <div className="min-w-0 space-y-16">
            {/* 2 — Position */}
            <Block n="02" title="Position" icon={<Compass className="w-4 h-4" />}>
              <div className="grid sm:grid-cols-3 gap-6">
                <Fact label="Along the ship" value={valueOrUnknown(motion?.longitudinal_position)} />
                <Fact label="Vertical zone" value={valueOrUnknown(motion?.vertical_zone)} />
                <Fact label="From midship" value={metres(motion?.distance_from_midship_m)} />
              </div>
              <div className="mt-8 card p-5">
                <div className="eyebrow mb-3">Motion exposure — geometry, not a forecast</div>
                <ExposureMeter level={motion?.overall ?? null} label="Overall motion exposure" />
                <ExposureMeter level={motion?.pitch ?? null} label="Pitch (fore–aft)" />
                <ExposureMeter level={motion?.roll ?? null} label="Roll (side–side)" />
                <p className="text-[12px] text-mist mt-3 leading-relaxed">
                  {motionClaim?.limitation ??
                    'Position relative to the ship’s centre, not the sea conditions you will feel.'}
                </p>
              </div>
            </Block>

            {/* 3 — Relationships */}
            <Block n="03" title="Relationships" icon={<Navigation className="w-4 h-4" />}>
              <div className="eyebrow mb-3">Other cabins on this deck</div>
              <div className="grid grid-cols-3 gap-3">
                {neighbours(model, c).map((n) => (
                  <NeighbourCard key={n} cabin={n} deck={d.number} shipId={shipId} />
                ))}
              </div>

              <div className="eyebrow mb-3 mt-8">Decks directly above &amp; below</div>
              <div className="grid sm:grid-cols-2 gap-3">
                <DeckRelCard label="Directly above" deck={above ?? null} shipId={shipId} />
                <DeckRelCard label="Directly below" deck={below ?? null} shipId={shipId} />
              </div>

              <p className="text-[12px] text-mist mt-5 leading-relaxed max-w-xl">
                Vertical adjacency is stated at deck level — the source draws each deck in its own
                frame, so a specific cabin “directly above” cannot be established without
                overclaiming. Cabin numbers on this deck are shown for onward exploration, not as a
                spatial adjacency claim.
              </p>
            </Block>

            {/* 4 — What Timonelo knows */}
            <Block n="04" title="What Timonelo knows" icon={<Volume2 className="w-4 h-4" />}>
              <div className="card p-6">
                <div className="flex items-center justify-between">
                  <div className="eyebrow">Noise exposure</div>
                  {noise?.confidence != null && (
                    <span className="text-[12px] text-mist">
                      confidence {Math.round(noise.confidence * 100)}%
                    </span>
                  )}
                </div>
                {noise && noise.sources.length > 0 ? (
                  <ul className="mt-4 space-y-2">
                    {noise.sources.map((s) => (
                      <li key={s} className="flex items-center gap-2 text-[14px] text-navy-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-brass" />
                        {noiseSourceLabel(s)}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-4 text-[14px] text-navy-700">
                    No structural noise source was detected adjacent to this cabin in the plan. That
                    is an absence of evidence for nearby sources — not a promise of quiet.
                  </p>
                )}
                {noiseClaim?.limitation && (
                  <p className="text-[12px] text-mist mt-3">{noiseClaim.limitation}</p>
                )}
              </div>
            </Block>

            {/* 5 — Sources */}
            <Block n="05" title="Sources" icon={<MapPin className="w-4 h-4" />}>
              <div className="card p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-[15px] font-medium text-navy">{source.title}</div>
                    <div className="text-[13px] text-mist mt-1">{source.publisher}</div>
                  </div>
                  <SourceBadge sourceType={source.source_type} />
                </div>
                <div className="h-px bg-line my-5" />
                <div className="text-[12px] text-mist">Located at: {c.source_locator}</div>
              </div>
            </Block>

            {/* 6 & 7 — Limitations + Unknown, first-class */}
            <Block n="06" title="Limitations & the unknown" icon={<Anchor className="w-4 h-4" />}>
              <p className="text-[14px] text-mist leading-relaxed mb-6 max-w-xl">
                Uncertainty is never hidden. These are the things this source cannot tell us about
                cabin {c.number}. They stay Unknown until a source that covers them is added.
              </p>
              <div className="card p-6">
                <UnknownList items={CABIN_UNKNOWNS} />
              </div>
            </Block>

            <KnowledgeLedger
              know={`Cabin ${c.number} sits on Deck ${d.number} (${d.name}), ${
                motion?.longitudinal_position ?? 'position unknown'
              } and ${metres(motion?.distance_from_midship_m)} from midship.`}
              how="Coordinates read directly from the deck plan; motion and noise are deterministic derivations recorded as canonical claims."
              dontKnow="Category, view, balcony and dimensions — not present in a deck plan."
              source={
                <span className="inline-flex items-center gap-2">
                  {source.title} <SourceBadge sourceType={source.source_type} />
                </span>
              }
            />
          </div>

          {/* Discovery — gentle exploration, no recommendations */}
          <aside className="lg:sticky lg:top-20 self-start space-y-3">
            <div className="eyebrow mb-1">Keep exploring</div>
            <Discovery model={model} cabin={c} deck={d} shipId={shipId} />
          </aside>
        </div>
      </main>
      <SiteFooter />
    </Shell>
  );
}

function neighbours(model: PackModel, c: Cabin): string[] {
  const list = model.cabinsOnDeck(c.deck_id);
  const i = list.findIndex((x) => x.entity_id === c.entity_id);
  return [list[i - 1], list[i + 1], list[i + 2]].filter(Boolean).map((x) => x!.number);
}

function Block({
  n,
  title,
  icon,
  children,
}: {
  n: string;
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <span className="font-mono text-[12px] text-fog">{n}</span>
        <span className="text-brass">{icon}</span>
        <h2 className="font-serif text-2xl text-navy">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  const unknown = value === 'Unknown';
  return (
    <div>
      <div className="eyebrow mb-2">{label}</div>
      <div className={`text-xl ${unknown ? 'text-fog italic font-serif' : 'text-navy font-medium'}`}>
        {value}
      </div>
    </div>
  );
}

function NeighbourCard({ cabin, deck, shipId }: { cabin: string; deck: number; shipId: string }) {
  return (
    <Link
      to={`/ship/${shipId}/deck/${deck}/cabin/${cabin}`}
      className="group card p-4 hover:border-sea transition-colors block text-center"
    >
      <div className="font-mono text-lg text-navy group-hover:text-sea">{cabin}</div>
    </Link>
  );
}

function DeckRelCard({ label, deck, shipId }: { label: string; deck: Deck | null; shipId: string }) {
  if (!deck) {
    return (
      <div className="card p-4">
        <div className="eyebrow mb-2">{label}</div>
        <div className="text-fog italic font-serif text-lg">None — outer deck</div>
      </div>
    );
  }
  return (
    <Link
      to={`/ship/${shipId}/deck/${deck.number}`}
      className="group card p-4 hover:border-sea transition-colors block"
    >
      <div className="eyebrow mb-2">{label}</div>
      <div className="text-lg text-navy group-hover:text-sea font-medium">
        Deck {deck.number} · {deck.name}
      </div>
    </Link>
  );
}

function Discovery({
  model,
  cabin,
  deck,
  shipId,
}: {
  model: PackModel;
  cabin: Cabin;
  deck: Deck;
  shipId: string;
}) {
  const nbrs = neighbours(model, cabin);
  const decks = model.decksTopToBottom();
  const idx = decks.findIndex((x) => x.number === deck.number);
  const otherDeck = decks[(idx + 1) % decks.length];
  const onDeck = model.cabinsOnDeck(deck.entity_id).length;

  return (
    <div className="space-y-3">
      {nbrs.map((n) => (
        <ExploreLink
          key={n}
          to={`/ship/${shipId}/deck/${deck.number}/cabin/${n}`}
          label={`Cabin ${n}`}
          sub="Nearby on this deck"
        />
      ))}
      <ExploreLink
        to={`/ship/${shipId}/deck/${deck.number}`}
        label={`All ${onDeck} cabins`}
        sub={`Deck ${deck.number} · ${deck.name}`}
      />
      <ExploreLink
        to={`/ship/${shipId}/deck/${otherDeck.number}`}
        label={`Deck ${otherDeck.number} · ${otherDeck.name}`}
        sub="Another deck"
      />
    </div>
  );
}
