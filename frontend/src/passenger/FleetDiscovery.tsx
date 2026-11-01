import { useState } from 'react';
import type { NavRoute } from '../components/ui/MainNavbar';
import BellissimaGuide from './BellissimaGuide';
import { FLEET, getFleetShip, type FleetShip, type FleetProfileData } from './fleet';
import { usePublicationSnapshot } from './usePublicationSnapshot';

type Navigate = (route: NavRoute | 'cabin', param?: string) => void;
const sections = ['identity', 'decks', 'venues', 'cabins'] as const;

export function FleetProfile({ ship, profile, onNavigate }: { ship: FleetShip; profile: FleetProfileData | undefined; onNavigate: Navigate }) {
  return <section className="space-y-6" aria-label={`${ship.label} profile`}>
    <header className="space-y-3"><button className="min-h-11 border rounded-xl px-4" onClick={() => onNavigate('ships')}>All ships</button><h1 className="font-display text-4xl font-bold break-words">{ship.label}</h1><p className="text-sm">Discovery catalog entry · verified vessel identity and class are shown only when published below.</p><p>{profile ? `Coverage level ${profile.level}/3 · ${profile.facts.length} published answers in this build` : 'Publication data unavailable'}</p></header>
    <div className="grid sm:grid-cols-2 gap-4">{sections.map(section => {
      const facts = profile?.facts.filter(f => f.section === section) ?? [];
      return <section key={section} className="min-w-0 rounded-2xl border bg-white p-4 space-y-3"><h2 className="font-display text-2xl capitalize">{section === 'identity' ? 'Ship identity' : section}</h2>{facts.length ? facts.map(f => <article key={f.statement_id} className="text-sm break-words"><p className="font-semibold">{f.entity_id.split(':').at(-1)?.replaceAll('-', ' ')} · {f.statement_type}</p><p>{typeof f.value === 'string' ? f.value : JSON.stringify(f.value)}</p><details><summary className="min-h-11 cursor-pointer">Source and publication trace</summary><p>{f.statement_id} · {f.question_id} · {f.artifact_id}, page {f.page ?? 'not specified'}</p><p>{f.locator}</p></details></article>) : <p className="text-sm text-[#5B6570]">No published {section} information available. Nothing is inferred from another ship.</p>}</section>;
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
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{FLEET.filter(s => s.label.toLowerCase().includes(query.trim().toLowerCase())).map(ship => <button key={ship.slug} className="min-w-0 text-left rounded-2xl border bg-white p-5 min-h-32 space-y-3" onClick={() => onNavigate('ships', ship.slug)}><h2 className="font-display text-2xl break-words">{ship.label}</h2><p className="text-sm">{data ? `Level ${data.ships[ship.slug].level}/3 · ${data.ships[ship.slug].facts.length} published answers` : 'Publication data unavailable'}</p><span className="block text-sm underline">Open profile</span></button>)}</div>
      {!FLEET.some(s => s.label.toLowerCase().includes(query.trim().toLowerCase())) && <p role="status">No matching ship in this launch collection.</p>}
    </>}
    <details className="text-sm border rounded-xl p-4"><summary className="min-h-11 cursor-pointer">What coverage levels mean</summary><ul className="list-disc pl-5 space-y-2"><li>Level 1: at least one published identity answer.</li><li>Level 2: Level 1 plus published deck and venue answers.</li><li>Level 3: Level 2 plus published cabin answers. Not full ship coverage.</li></ul><p className="mt-3">Level 0 means Level 1 is not yet reached. Levels describe available categories, not completeness, geometry or current operations.</p></details>
    {data && <p className="text-xs text-[#5B6570]">Canonical build snapshot: {data.as_of}. Reviews completed later require a new build.</p>}
  </div>;
}
