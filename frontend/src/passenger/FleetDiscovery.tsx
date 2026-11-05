import { useState } from 'react';
import type { NavRoute } from '../components/ui/MainNavbar';
import BellissimaGuide from './BellissimaGuide';
import { FLEET, getFleetShip, type FleetShip, type FleetProfileData, type PublishedFact } from './fleet';
import { usePublicationSnapshot } from './usePublicationSnapshot';
import { ShipPhoto } from './ShipPhoto';

type Navigate = (route: NavRoute | 'cabin', param?: string) => void;
const sections = ['identity', 'decks', 'venues', 'cabins'] as const;
const bellissimaSections = { identity: 'Ship identity', decks: 'Deck orientation', venues: 'Dining, entertainment & services', cabins: 'Cabins & accommodation' };

function deckLocation(fact: PublishedFact): string | null {
  if (fact.statement_type !== 'deck.venue_present' || !Array.isArray(fact.value) ||
      fact.value.length === 0 || !fact.value.every(value => Number.isInteger(value))) return null;
  return `Deck${fact.value.length === 1 ? '' : 's'} ${fact.value.join(' & ')}`;
}

export function FleetProfile({ ship, profile, onNavigate }: { ship: FleetShip; profile: FleetProfileData | undefined; onNavigate: Navigate }) {
  const bellissima = ship.slug === 'msc-bellissima';
  return <section className="space-y-6" aria-label={`${ship.label} profile`}>
    <header className="space-y-5">
      <button className="min-h-11 border rounded-xl px-4 hover:bg-white" onClick={() => onNavigate('ships')}>← All ships</button>
      <div className="flex flex-wrap gap-4 items-end justify-between"><div className="space-y-3"><p className="text-xs uppercase tracking-[0.2em] text-[#8B653D]">The MSC collection · ship portrait</p><h1 className="font-display text-4xl sm:text-6xl font-bold break-words">{ship.label}</h1></div><span className="rounded-full bg-white border px-4 py-2 text-sm">{profile ? `${profile.facts.length} published answers` : 'Publication data unavailable'}</span></div>
      <ShipPhoto key={ship.slug} slug={ship.slug} label={ship.label} priority />
      <div className="grid md:grid-cols-[1.4fr_1fr] gap-6 rounded-2xl bg-[#0C1B2A] text-white p-5 sm:p-8">
        <div className="space-y-3"><h2 className="font-display text-3xl">A closer look. A clear view of what we know.</h2><p className="text-sm leading-relaxed text-white/80">Explore this ship through licensed photography and source-traceable knowledge. Ship details appear below only when the canonical publication process admits them. Missing information stays visible.</p></div>
        <div className="space-y-3"><p className="text-xs uppercase tracking-widest text-[#E7C7A2]">Knowledge coverage</p><p className="font-display text-2xl">{profile ? `Coverage level ${profile.level}/3` : 'Publication data unavailable'}</p><p className="text-sm text-white/80">A photograph identifies its subject for browsing. It does not confirm cabin details, current operations or a route.</p></div>
      </div>
    </header>
    {bellissima && <nav aria-label="Bellissima profile sections" className="grid grid-cols-2 sm:grid-cols-4 gap-2">
      {sections.map(section => <a key={section} href={`#${ship.slug}-${section}`} className="min-w-0 min-h-11 rounded-xl border bg-white px-3 py-3 text-sm leading-relaxed hover:border-[#C58A46] focus-visible:outline-offset-4">{bellissimaSections[section]}</a>)}
    </nav>}
    {['msc-bellissima', 'msc-euribia'].includes(ship.slug) && <section className="rounded-2xl border border-[#C58A46]/40 bg-[#F8F0E5] p-5 sm:p-6 space-y-3" aria-label="Review preparation">
      <p className="text-xs uppercase tracking-widest text-[#79552E]">Human review pending</p><h2 className="font-display text-2xl">{bellissima ? profile?.facts.length ? 'More information, under review' : 'Passenger information, under review' : 'The next layer: cabins & dining'}</h2>
      <p className="text-sm leading-relaxed">{bellissima ? profile?.facts.length ? 'Published facts appear below with their source trace. Other observations remain under review; pending details are withheld until their own evidence, review and publication gates are satisfied.' : 'Source observations about dining, entertainment and practical orientation are prepared for human review. Pending details are not published facts and stay withheld until the evidence, review and publication gates are satisfied.' : 'Source observations are prepared for independent human review. Pending details remain withheld from this public profile until their evidence, review and publication gates are satisfied.'}</p>
      <p className="text-sm">Not confirmed. No current capacity, geometry, accessibility or availability is inferred.</p>
    </section>}
    <div className="grid sm:grid-cols-2 gap-4">{sections.map(section => {
      const facts = profile?.facts.filter(f => f.section === section) ?? [];
      return <section key={section} id={`${ship.slug}-${section}`} className="min-w-0 scroll-mt-24 rounded-2xl border bg-white p-4 sm:p-6 space-y-3">
        <h2 className="font-display text-2xl">{bellissima ? bellissimaSections[section] : section === 'identity' ? 'Ship identity' : section}</h2>
        {facts.length ? facts.map(f => {
          const location = deckLocation(f);
          return <article key={f.statement_id} className="text-sm break-words space-y-2 border-t pt-3">
            <p className="font-semibold capitalize">{f.entity_id.split(':').at(-1)?.replaceAll('-', ' ')}</p>
            {location && <p className="text-xs text-[#5B6570]">Published deck location</p>}
            <p>{location ?? (typeof f.value === 'string' ? f.value : JSON.stringify(f.value))}</p>
            {location && f.source_edition && <p className="text-xs text-[#5B6570]">Source edition: {f.source_edition}. Describes this plan edition, not current operations.</p>}
            <details><summary className="min-h-11 cursor-pointer">Source and publication trace</summary><p>{f.statement_id} · {f.question_id} · {f.artifact_id}, page {f.page ?? 'not specified'}</p><p>{f.statement_type}</p><p>{f.locator}</p></details>
          </article>;
        }) : <p className="text-sm text-[#5B6570]">No published {section} information available. Nothing is inferred from another ship.</p>}
      </section>;
    })}</div>
    <section className="rounded-2xl border bg-white p-4 space-y-3"><h2 className="font-display text-2xl">Sources & publication</h2><p className="text-sm">{profile ? `${profile.candidate_count} candidate statements; ${profile.facts.length} currently exported answers. Source labels and review candidates are not publication approval.` : 'The canonical publication snapshot could not be loaded. Profile facts remain unavailable.'}</p>{profile?.sources.map(s => <p key={s.artifact_id} className="text-xs break-all">{s.artifact_id} · {s.filename} · SHA-256 {s.sha256}</p>)}<p className="text-xs">Build-time publication snapshot. No source artwork is redistributed here. Coverage does not grant geometry, routing or accessibility admission.</p></section>
    {ship.slug === 'msc-bellissima' && <details className="border rounded-2xl p-4"><summary className="min-h-11 cursor-pointer font-semibold">Bellissima reference tools — separate from published facts</summary><BellissimaGuide onNavigate={onNavigate} /></details>}
  </section>;
}

export default function FleetDiscovery({ selectedSlug, onNavigate }: { selectedSlug?: string; onNavigate: Navigate }) {
  const data = usePublicationSnapshot();
  const [query, setQuery] = useState('');
  const selected = getFleetShip(selectedSlug);
  return <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
    {selected ? <FleetProfile key={selected.slug} ship={selected} profile={data?.ships[selected.slug]} onNavigate={onNavigate} /> : selectedSlug ? <section><h1 className="text-3xl">Ship unavailable</h1><p>No catalog match. We do not substitute another vessel.</p><button className="min-h-11 border rounded-xl px-4" onClick={() => onNavigate('ships')}>All ships</button></section> : <>
      <header className="space-y-3"><h1 className="font-display text-4xl font-bold">Explore ships</h1><p>Choose a ship. Published knowledge and missing coverage stay visible.</p><p className="text-sm">Launch collection: MSC. Catalog inclusion is not verification of a ship profile.</p></header>
      <label className="block">Find a ship<input className="block w-full max-w-md min-w-0 border rounded-xl p-3 mt-2" value={query} onChange={e => setQuery(e.target.value)} placeholder="Ship name" /></label>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{FLEET.filter(s => s.label.toLowerCase().includes(query.trim().toLowerCase())).map(ship => <article key={ship.slug} className="min-w-0 rounded-2xl border bg-white overflow-hidden flex flex-col">
        <ShipPhoto slug={ship.slug} label={ship.label} compact />
        <button className="text-left p-5 pt-3 space-y-3 flex-1 hover:bg-[#FBF8F3] focus-visible:outline-offset-[-4px]" onClick={() => onNavigate('ships', ship.slug)}><h2 className="font-display text-2xl break-words">{ship.label}</h2><p className="text-sm">{data ? `Level ${data.ships[ship.slug].level}/3 · ${data.ships[ship.slug].facts.length} published answers` : 'Publication data unavailable'}</p><span className="block text-sm underline">Explore ship →</span></button>
      </article>)}</div>
      {!FLEET.some(s => s.label.toLowerCase().includes(query.trim().toLowerCase())) && <p role="status">No matching ship in this launch collection.</p>}
    </>}
    <details className="text-sm border rounded-xl p-4"><summary className="min-h-11 cursor-pointer">What coverage levels mean</summary><ul className="list-disc pl-5 space-y-2"><li>Level 1: at least one published identity answer.</li><li>Level 2: Level 1 plus published deck and venue answers.</li><li>Level 3: Level 2 plus published cabin answers. Not full ship coverage.</li></ul><p className="mt-3">Level 0 means Level 1 is not yet reached. Levels describe available categories, not completeness, geometry or current operations.</p></details>
    {data && <p className="text-xs text-[#5B6570]">Canonical build snapshot: {data.as_of}. Reviews completed later require a new build.</p>}
  </div>;
}
