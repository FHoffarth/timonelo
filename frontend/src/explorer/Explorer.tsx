import { type ReactNode, useEffect } from 'react';

import {
  cabinPath,
  deckPath,
  formatEvidenceKind,
  formatFeatureCode,
  formatKind,
  getCabin,
  getCabinsOnDeck,
  getCategory,
  getClaimsFor,
  getDeck,
  getDeckById,
  getEntityName,
  getEntityPath,
  getPublicAreasOnDeck,
  getRelationshipsFor,
  getSources,
  knowledgePack,
  type Cabin,
  type Claim,
  type Deck,
  type PublicArea,
  type Relationship,
} from './knowledge';

const shipPath = '/explore/ships/msc-bellissima';
const heroCruise = '/hero-cruise-golden-hour.webp';

export default function Explorer() {
  const pathname = window.location.pathname.replace(/\/$/, '') || '/';
  const deckMatch = pathname.match(/^\/explore\/decks\/(\d+)$/);
  const cabinMatch = pathname.match(/^\/explore\/cabins\/(\d+)$/);

  if (deckMatch) {
    const deck = getDeck(Number(deckMatch[1]));
    return deck ? <DeckPage deck={deck} /> : <NotFoundPage />;
  }
  if (cabinMatch) {
    const cabin = getCabin(cabinMatch[1]);
    return cabin ? <CabinPage cabin={cabin} /> : <NotFoundPage />;
  }
  if (pathname === '/explore' || pathname === shipPath) return <ShipPage />;
  return <NotFoundPage />;
}

function ExplorerShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink">
      <a className="skip-link" href="#explorer-content">Skip to explorer content</a>
      <header className="explorer-header">
        <div className="page-shell flex h-18 items-center justify-between gap-5 sm:h-20">
          <div className="flex min-w-0 items-baseline gap-4">
            <a className="font-display text-2xl tracking-[-0.02em] text-white" href="/">Timonelo</a>
            <span className="hidden border-l border-white/25 pl-4 text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-white/55 sm:block">
              Cruise Explorer
            </span>
          </div>
          <nav aria-label="Explorer navigation" className="flex items-center gap-5 text-xs font-semibold text-white/78 sm:gap-8">
            <a className="nav-link" href={shipPath}>MSC Bellissima</a>
            <a className="explorer-exit" href="/">About Timonelo</a>
          </nav>
        </div>
      </header>
      <main id="explorer-content">{children}</main>
      <footer className="border-t border-ink/15 bg-white py-8">
        <div className="page-shell flex flex-col gap-3 text-xs leading-5 text-muted sm:flex-row sm:justify-between">
          <p>Knowledge Pack {knowledgePack.version} · Snapshot {formatDate(knowledgePack.effective_date)}</p>
          <p>Verified knowledge only. No scores, recommendations, or inferred suitability.</p>
        </div>
      </footer>
    </div>
  );
}

function ShipPage() {
  usePageMetadata('MSC Bellissima — Cruise Explorer', 'Explore verified decks, cabins, public areas, and complete source provenance for MSC Bellissima.');
  const shipClaims = getClaimsFor(knowledgePack.ship.entity_id);

  return (
    <ExplorerShell>
      <section className="explorer-ship-hero bg-ink text-white">
        <img alt="" aria-hidden="true" className="absolute inset-0 h-full w-full object-cover" src={heroCruise} />
        <div className="explorer-ship-overlay absolute inset-0" aria-hidden="true" />
        <div className="page-shell relative z-10 flex min-h-[34rem] items-end pb-12 pt-24 sm:min-h-[42rem] sm:pb-16">
          <div className="max-w-4xl">
            <p className="eyebrow text-white/65">Verified ship knowledge · MSC Cruises</p>
            <h1 className="mt-5 max-w-[11ch] font-display text-[clamp(3.8rem,10vw,7.8rem)] leading-[0.9] tracking-[-0.045em]">
              MSC Bellissima
            </h1>
            <p className="mt-7 max-w-2xl text-base leading-7 text-white/78 sm:text-lg sm:leading-8">
              An evidence-bounded view of the ship’s structural configuration, decks, selected cabins, and public areas.
            </p>
          </div>
        </div>
        <p className="absolute bottom-4 right-4 z-10 text-[0.6rem] uppercase tracking-[0.14em] text-white/55 sm:bottom-6 sm:right-8">
          Maritime context image · Not documentary evidence
        </p>
      </section>

      <div className="page-shell py-12 sm:py-16">
        <Breadcrumbs items={[['Cruise Explorer', '/explore'], ['MSC Bellissima']]} />
        <section aria-labelledby="ship-facts-heading" className="mt-10">
          <SectionIntro
            eyebrow="Ship record"
            id="ship-facts-heading"
            title="What the source establishes."
            text="These statements are preserved from the canonical pack with their original evidence boundaries."
          />
          <div className="mt-10 grid border-t border-ink/20 sm:grid-cols-2">
            {shipClaims.map((claim) => <ClaimCard claim={claim} key={claim.claim_id} />)}
          </div>
          <ProvenanceStrip sourceIds={knowledgePack.ship.source_ids} locator={knowledgePack.ship.source_locator} />
        </section>

        <section aria-labelledby="decks-heading" className="explorer-section">
          <SectionIntro
            eyebrow="15 represented decks"
            id="decks-heading"
            title="Explore the ship by deck."
            text="Counts describe records in this Knowledge Pack—not the complete physical inventory of the ship."
          />
          <div className="mt-10 border-t border-ink/20">
            {knowledgePack.decks.map((deck) => <DeckRow deck={deck} key={deck.entity_id} />)}
          </div>
        </section>

        <section aria-labelledby="coverage-heading" className="explorer-section grid gap-10 border-t border-ink/20 pt-10 lg:grid-cols-[0.75fr_1.25fr]">
          <div>
            <p className="eyebrow text-muted">Coverage boundary</p>
            <h2 className="mt-4 font-display text-4xl tracking-[-0.03em] sm:text-5xl" id="coverage-heading">Small by design.</h2>
          </div>
          <div>
            <p className="max-w-2xl text-lg leading-8 text-ink/75">
              This first pack contains {knowledgePack.cabins.length} individually verified cabin records. It does not claim complete cabin coverage and never fills absent category assignments by inference.
            </p>
            <Limitations limitations={knowledgePack.limitations} />
          </div>
        </section>

        <SourceRegistry />
      </div>
    </ExplorerShell>
  );
}

function DeckPage({ deck }: { deck: Deck }) {
  usePageMetadata(`Deck ${deck.number} — ${deck.name} — Timonelo`, `Verified cabins and public areas represented on MSC Bellissima Deck ${deck.number}.`);
  const cabins = getCabinsOnDeck(deck.entity_id);
  const areas = getPublicAreasOnDeck(deck.entity_id);
  const relationships = getRelationshipsFor(deck.entity_id).filter((item) => item.kind === 'below');
  const deckIndex = knowledgePack.decks.findIndex((item) => item.entity_id === deck.entity_id);
  const previous = knowledgePack.decks[deckIndex - 1];
  const next = knowledgePack.decks[deckIndex + 1];

  return (
    <ExplorerShell>
      <div className="page-shell py-10 sm:py-14">
        <Breadcrumbs items={[['Cruise Explorer', '/explore'], ['MSC Bellissima', shipPath], [`Deck ${deck.number}`]]} />
        <header className="explorer-page-heading">
          <div>
            <p className="eyebrow text-muted">MSC Bellissima · Structural level {deck.ordinal} of {knowledgePack.decks.length}</p>
            <h1 className="mt-5 font-display text-[clamp(4rem,11vw,8rem)] leading-[0.86] tracking-[-0.05em]">Deck {deck.number}</h1>
            <p className="mt-5 font-display text-3xl text-ink/62 sm:text-4xl">{deck.name}</p>
          </div>
          <RecordStatus />
        </header>
        <ProvenanceStrip sourceIds={deck.source_ids} locator={deck.source_locator} />

        <section aria-labelledby="deck-context-heading" className="explorer-section">
          <SectionIntro eyebrow="Structural context" id="deck-context-heading" title="Where this deck sits." text="Ordering is structural only. It does not imply passenger impact or suitability." />
          <div className="mt-10 grid gap-px bg-ink/15 border border-ink/15 sm:grid-cols-2">
            <DeckNeighbour label="Represented level below" deck={previous} />
            <DeckNeighbour label="Represented level above" deck={next} />
          </div>
          {relationships.length > 0 && (
            <div className="mt-6 space-y-3">
              {relationships.map((relationship) => <RelationshipDisclosure key={relationship.relationship_id} relationship={relationship} />)}
            </div>
          )}
        </section>

        <section aria-labelledby="deck-cabins-heading" className="explorer-section">
          <SectionIntro eyebrow={`${cabins.length} represented cabin${cabins.length === 1 ? '' : 's'}`} id="deck-cabins-heading" title="Verified cabin records." text="Only cabins individually established in this pack appear here." />
          {cabins.length ? (
            <div className="mt-10 border-t border-ink/20">{cabins.map((cabin) => <CabinRow cabin={cabin} key={cabin.entity_id} />)}</div>
          ) : <EmptyKnowledge text="No individual cabin has been established for this deck in the current pack." />}
        </section>

        <section aria-labelledby="deck-areas-heading" className="explorer-section">
          <SectionIntro eyebrow={`${areas.length} represented public area${areas.length === 1 ? '' : 's'}`} id="deck-areas-heading" title="Public areas in evidence." text="Presence is recorded without claims about noise, convenience, or passenger experience." />
          {areas.length ? (
            <div className="mt-10 grid gap-px border border-ink/15 bg-ink/15 md:grid-cols-2">{areas.map((area) => <PublicAreaCard area={area} key={area.entity_id} />)}</div>
          ) : <EmptyKnowledge text="No public area has been established for this deck in the current pack." />}
        </section>

        <Pager previous={previous} next={next} />
      </div>
    </ExplorerShell>
  );
}

function CabinPage({ cabin }: { cabin: Cabin }) {
  usePageMetadata(`Cabin ${cabin.number} — MSC Bellissima — Timonelo`, `Verified structural knowledge and complete provenance for MSC Bellissima cabin ${cabin.number}.`);
  const deck = getDeckById(cabin.deck_id);
  const category = getCategory(cabin.category_id);
  const relationships = getRelationshipsFor(cabin.entity_id);

  return (
    <ExplorerShell>
      <div className="page-shell py-10 sm:py-14">
        <Breadcrumbs items={[['Cruise Explorer', '/explore'], ['MSC Bellissima', shipPath], [deck ? `Deck ${deck.number}` : 'Deck', deck ? deckPath(deck) : shipPath], [`Cabin ${cabin.number}`]]} />
        <header className="explorer-page-heading">
          <div>
            <p className="eyebrow text-muted">MSC Bellissima · Individual cabin record</p>
            <h1 className="mt-5 font-display text-[clamp(4rem,11vw,8rem)] leading-[0.86] tracking-[-0.05em]">Cabin {cabin.number}</h1>
            {deck && <p className="mt-5 font-display text-3xl text-ink/62 sm:text-4xl">Deck {deck.number} — {deck.name}</p>}
          </div>
          <RecordStatus />
        </header>
        <ProvenanceStrip sourceIds={cabin.source_ids} locator={cabin.source_locator} />

        <section aria-labelledby="cabin-record-heading" className="explorer-section">
          <SectionIntro eyebrow="Cabin record" id="cabin-record-heading" title="Established attributes." text="Unknown values stay visibly unknown; no nearby cabin or commercial category is used to fill a gap." />
          <dl className="mt-10 border-t border-ink/20">
            <FactRow label="Ship" value={knowledgePack.ship.name} />
            <FactRow label="Deck" value={deck ? `Deck ${deck.number} — ${deck.name}` : 'Unknown'} href={deck ? deckPath(deck) : undefined} />
            <FactRow label="Cabin category" value={category ? `${category.code} — ${category.name}` : 'Unknown in this Knowledge Pack'} unknown={!category} />
            <FactRow label="Accommodation type" value={category ? formatKind(category.accommodation_type) : 'Unknown in this Knowledge Pack'} unknown={!category} />
            <FactRow label="Recorded features" value={cabin.feature_codes.length ? cabin.feature_codes.map(formatFeatureCode).join(', ') : 'No individual feature established'} unknown={!cabin.feature_codes.length} />
          </dl>
          {category && (
            <div className="mt-7 border-l-2 border-gold bg-white p-6">
              <p className="eyebrow text-muted">Category boundary</p>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-ink/72">Category information is operator-defined and does not establish that every cabin in the category has an identical size, layout, or furniture configuration.</p>
              <ProvenanceInline sourceIds={category.source_ids} locator={category.source_locator} />
            </div>
          )}
          <Limitations limitations={cabin.limitations} />
        </section>

        <section aria-labelledby="cabin-relationships-heading" className="explorer-section">
          <SectionIntro eyebrow={`${relationships.length} represented relationship${relationships.length === 1 ? '' : 's'}`} id="cabin-relationships-heading" title="Structural relationships." text="Relationships describe plan structure only and do not imply comfort, access, or suitability." />
          {relationships.length ? (
            <div className="mt-10 space-y-3">{relationships.map((relationship) => <RelationshipDisclosure key={relationship.relationship_id} relationship={relationship} />)}</div>
          ) : <EmptyKnowledge text="No cabin-to-cabin structural relationship has been established for this cabin in the current pack." />}
        </section>

        <section aria-labelledby="cabin-provenance-heading" className="explorer-section">
          <SectionIntro eyebrow="Complete provenance" id="cabin-provenance-heading" title="Inspect the evidence boundary." text="The record points back to the exact source location used by the canonical pack." />
          <div className="mt-10"><ProvenanceDetail sourceIds={cabin.source_ids} locator={cabin.source_locator} /></div>
        </section>
      </div>
    </ExplorerShell>
  );
}

function DeckRow({ deck }: { deck: Deck }) {
  const cabins = getCabinsOnDeck(deck.entity_id);
  const areas = getPublicAreasOnDeck(deck.entity_id);
  return (
    <a className="deck-row group" href={deckPath(deck)}>
      <span className="font-display text-4xl tabular-nums sm:text-5xl">{String(deck.number).padStart(2, '0')}</span>
      <span>
        <span className="block font-display text-2xl sm:text-3xl">{deck.name}</span>
        <span className="mt-1 block text-xs leading-5 text-muted">{cabins.length} represented cabins · {areas.length} represented public areas</span>
      </span>
      <span className="hidden text-xs leading-5 text-muted lg:block">{deck.source_locator}</span>
      <span aria-hidden="true" className="text-xl transition-transform group-hover:translate-x-1">→</span>
    </a>
  );
}

function CabinRow({ cabin }: { cabin: Cabin }) {
  const category = getCategory(cabin.category_id);
  return (
    <a className="cabin-row group" href={cabinPath(cabin)}>
      <span className="font-display text-3xl">Cabin {cabin.number}</span>
      <span className={category ? 'text-sm text-muted' : 'text-sm text-ink/58'}>{category ? `${category.code} — ${category.name}` : 'Category unknown'}</span>
      <span className="hidden text-xs leading-5 text-muted md:block">{cabin.source_locator}</span>
      <span aria-hidden="true" className="transition-transform group-hover:translate-x-1">→</span>
    </a>
  );
}

function PublicAreaCard({ area }: { area: PublicArea }) {
  return (
    <article className="bg-white p-6 sm:p-8">
      <p className="eyebrow text-muted">{formatKind(area.kind)}</p>
      <h3 className="mt-4 font-display text-3xl tracking-[-0.02em]">{area.name}</h3>
      <ProvenanceInline sourceIds={area.source_ids} locator={area.source_locator} />
      <Limitations limitations={area.limitations} compact />
    </article>
  );
}

function ClaimCard({ claim }: { claim: Claim }) {
  return (
    <article className="border-b border-ink/20 py-7 sm:min-h-52 sm:px-8 sm:py-9 sm:odd:border-r sm:first:pl-0">
      <p className="eyebrow text-muted">{formatEvidenceKind(claim.evidence_kind)}</p>
      <p className="mt-4 max-w-xl font-display text-2xl leading-snug sm:text-3xl">{claim.statement}</p>
      <ProvenanceInline sourceIds={claim.source_ids} locator={claim.source_locator} />
      {claim.limitation && <p className="mt-4 text-xs leading-5 text-muted">Limit: {claim.limitation}</p>}
    </article>
  );
}

function RelationshipDisclosure({ relationship }: { relationship: Relationship }) {
  const currentPath = getEntityPath(relationship.source_entity_id);
  const targetPath = getEntityPath(relationship.target_entity_id);
  return (
    <details className="relationship-disclosure">
      <summary>
        <span>
          <span className="eyebrow text-muted">{formatEvidenceKind(relationship.evidence_kind)}</span>
          <span className="mt-2 block font-display text-xl sm:text-2xl">
            {renderEntityLink(relationship.source_entity_id, currentPath)} <span className="text-ink/45">{formatKind(relationship.kind).toLowerCase()}</span> {renderEntityLink(relationship.target_entity_id, targetPath)}
          </span>
        </span>
        <span aria-hidden="true" className="text-xl">+</span>
      </summary>
      <div className="border-t border-ink/12 px-5 py-5 sm:px-7">
        <ProvenanceInline sourceIds={relationship.source_ids} locator={relationship.source_locator} />
        {relationship.derivation_rule && <p className="mt-3 text-xs leading-5 text-muted">Derivation rule: <code>{relationship.derivation_rule}</code></p>}
        {relationship.limitation && <p className="mt-3 text-xs leading-5 text-muted">Limit: {relationship.limitation}</p>}
      </div>
    </details>
  );
}

function ProvenanceStrip({ sourceIds, locator }: { sourceIds: string[]; locator: string }) {
  return (
    <div className="provenance-strip">
      <span className="eyebrow text-muted">Provenance</span>
      <span className="text-sm leading-6 text-ink/72">{getSources(sourceIds).map((source, index) => (
        <span key={source.source_id}>{index > 0 && ' · '}<a className="source-link" href={source.url} rel="noreferrer" target="_blank">{source.title}</a></span>
      ))}</span>
      <span className="text-xs leading-5 text-muted">{locator}</span>
    </div>
  );
}

function ProvenanceInline({ sourceIds, locator }: { sourceIds: string[]; locator: string }) {
  return (
    <div className="mt-5 text-xs leading-5 text-muted">
      <p>{getSources(sourceIds).map((source, index) => (
        <span key={source.source_id}>{index > 0 && ' · '}<a className="source-link" href={source.url} rel="noreferrer" target="_blank">{source.title}</a></span>
      ))}</p>
      <p className="mt-1">Locator: {locator}</p>
    </div>
  );
}

function ProvenanceDetail({ sourceIds, locator }: { sourceIds: string[]; locator?: string }) {
  return (
    <div className="grid gap-px border border-ink/15 bg-ink/15 md:grid-cols-2">
      {getSources(sourceIds).map((source) => (
        <article className="bg-white p-6 sm:p-8" key={source.source_id}>
          <p className="eyebrow text-muted">{formatKind(source.source_type)}</p>
          <h3 className="mt-4 font-display text-2xl">{source.title}</h3>
          <p className="mt-2 text-sm text-muted">{source.publisher} · Accessed {formatDate(source.accessed_at)}</p>
          {locator && <p className="mt-4 text-sm leading-6 text-ink/72">Locator: {locator}</p>}
          <a className="text-link mt-5" href={source.url} rel="noreferrer" target="_blank">Open source <span aria-hidden="true">↗</span></a>
          <Limitations limitations={source.limitations} compact />
        </article>
      ))}
    </div>
  );
}

function SourceRegistry() {
  return (
    <section aria-labelledby="sources-heading" className="explorer-section">
      <SectionIntro eyebrow={`${knowledgePack.sources.length} official sources`} id="sources-heading" title="Source registry." text="Every material record in this explorer resolves to one or more of these publisher sources." />
      <div className="mt-10"><ProvenanceDetail sourceIds={knowledgePack.sources.map((source) => source.source_id)} /></div>
    </section>
  );
}

function DeckNeighbour({ label, deck }: { label: string; deck: Deck | undefined }) {
  return deck ? (
    <a className="group bg-white p-6 sm:p-8" href={deckPath(deck)}>
      <span className="eyebrow text-muted">{label}</span>
      <span className="mt-4 flex items-baseline justify-between gap-4">
        <span className="font-display text-3xl">Deck {deck.number} — {deck.name}</span>
        <span aria-hidden="true" className="transition-transform group-hover:translate-x-1">→</span>
      </span>
    </a>
  ) : <div className="bg-white p-6 sm:p-8"><p className="eyebrow text-muted">{label}</p><p className="mt-4 text-sm text-muted">No represented structural level.</p></div>;
}

function Pager({ previous, next }: { previous: Deck | undefined; next: Deck | undefined }) {
  return (
    <nav aria-label="Deck pagination" className="explorer-section grid gap-px border border-ink/15 bg-ink/15 sm:grid-cols-2">
      <PagerLink deck={previous} label="Previous represented deck" direction="←" />
      <PagerLink deck={next} label="Next represented deck" direction="→" alignRight />
    </nav>
  );
}

function PagerLink({ deck, label, direction, alignRight = false }: { deck: Deck | undefined; label: string; direction: string; alignRight?: boolean }) {
  if (!deck) return <span className="bg-white p-6 text-sm text-muted sm:p-8">No {label.toLowerCase()}</span>;
  return <a className={`bg-white p-6 sm:p-8 ${alignRight ? 'sm:text-right' : ''}`} href={deckPath(deck)}><span className="eyebrow text-muted">{label}</span><span className="mt-3 block font-display text-2xl">{direction} Deck {deck.number}</span></a>;
}

function FactRow({ label, value, href, unknown = false }: { label: string; value: string; href?: string; unknown?: boolean }) {
  return (
    <div className="grid gap-2 border-b border-ink/20 py-6 sm:grid-cols-[13rem_1fr] sm:items-baseline">
      <dt className="eyebrow text-muted">{label}</dt>
      <dd className={`font-display text-2xl ${unknown ? 'text-ink/48' : ''}`}>{href ? <a className="source-link" href={href}>{value}</a> : value}</dd>
    </div>
  );
}

function Limitations({ limitations, compact = false }: { limitations: string[]; compact?: boolean }) {
  if (!limitations.length) return null;
  return (
    <div className={compact ? 'mt-5' : 'mt-8'}>
      <p className="eyebrow text-muted">Limits</p>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-muted">
        {limitations.map((limitation) => <li className="flex gap-3" key={limitation}><span aria-hidden="true">—</span><span>{limitation}</span></li>)}
      </ul>
    </div>
  );
}

function EmptyKnowledge({ text }: { text: string }) {
  return <div className="mt-10 border-l-2 border-gold bg-white p-6 text-sm leading-6 text-muted sm:p-8"><p className="eyebrow mb-3 text-muted">Explicit unknown</p>{text}</div>;
}

function RecordStatus() {
  return <div className="record-status"><span className="status-dot" aria-hidden="true" /><span><strong className="block text-sm text-ink">Source-backed record</strong><span className="mt-1 block text-xs text-muted">Canonical pack {knowledgePack.version}</span></span></div>;
}

function SectionIntro({ eyebrow, id, title, text }: { eyebrow: string; id: string; title: string; text: string }) {
  return <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr] lg:items-end lg:gap-20"><div><p className="eyebrow text-muted">{eyebrow}</p><h2 className="mt-4 max-w-[14ch] font-display text-[clamp(2.7rem,6vw,5rem)] leading-[0.96] tracking-[-0.04em]" id={id}>{title}</h2></div><p className="max-w-xl text-base leading-7 text-muted sm:text-lg sm:leading-8">{text}</p></div>;
}

function Breadcrumbs({ items }: { items: Array<[string, string?]> }) {
  return <nav aria-label="Breadcrumb"><ol className="flex flex-wrap items-center gap-2 text-xs text-muted">{items.map(([label, href], index) => <li className="flex items-center gap-2" key={`${label}-${index}`}>{index > 0 && <span aria-hidden="true">/</span>}{href ? <a className="source-link" href={href}>{label}</a> : <span aria-current="page">{label}</span>}</li>)}</ol></nav>;
}

function NotFoundPage() {
  usePageMetadata('Knowledge record not found — Timonelo', 'The requested record is not represented in the current Knowledge Pack.');
  return <ExplorerShell><div className="page-shell flex min-h-[70vh] items-center py-20"><div><p className="eyebrow text-muted">Explicit unknown</p><h1 className="mt-5 max-w-[12ch] font-display text-5xl leading-none tracking-[-0.04em] sm:text-7xl">This record is not represented.</h1><p className="mt-6 max-w-xl text-base leading-7 text-muted">The current Knowledge Pack does not contain the requested ship, deck, or cabin record. No substitute result has been inferred.</p><a className="button button-dark mt-8" href={shipPath}>Return to MSC Bellissima</a></div></div></ExplorerShell>;
}

function renderEntityLink(entityId: string, path: string | undefined): ReactNode {
  const name = getEntityName(entityId);
  return path ? <a className="source-link" href={path}>{name}</a> : name;
}

function usePageMetadata(title: string, description: string) {
  useEffect(() => {
    document.title = title;
    document.querySelector<HTMLMetaElement>('meta[name="description"]')?.setAttribute('content', description);
    document.querySelector<HTMLMetaElement>('meta[property="og:title"]')?.setAttribute('content', title);
    document.querySelector<HTMLMetaElement>('meta[property="og:description"]')?.setAttribute('content', description);
    document.querySelector<HTMLMetaElement>('#og-url')?.setAttribute('content', window.location.href);
    document.querySelector<HTMLMetaElement>('meta[name="twitter:title"]')?.setAttribute('content', title);
    document.querySelector<HTMLMetaElement>('meta[name="twitter:description"]')?.setAttribute('content', description);
    document.querySelector<HTMLLinkElement>('#canonical-url')?.setAttribute('href', window.location.href);
  }, [description, title]);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`));
}
