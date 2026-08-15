/**
 * Sharing, canonical links, and social preview metadata for a cabin briefing.
 * Presentation-layer only — no backend, no routing framework. The cabin is
 * carried in a query param so the link loads the same briefing when opened.
 */
import type { ShipData, CabinData } from './types';

export function shipSlug(ship: ShipData): string {
  return ship.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

/** Functional shareable URL that reopens this cabin (?cabin=NNNN). */
export function cabinUrl(cabinNumber: string): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : 'https://timonelo.com';
  return `${origin}/?cabin=${encodeURIComponent(cabinNumber)}`;
}

/** The canonical, human-readable path form (intended production URL). */
export function canonicalPath(ship: ShipData, cabinNumber: string): string {
  return `/${shipSlug(ship)}/cabin/${cabinNumber}`;
}

export function briefingTitle(ship: ShipData, cabin: CabinData): string {
  return `${ship.name} · Cabin ${cabin.cabin_number}`;
}

export function briefingDescription(cabin: CabinData): string {
  return `Deck ${cabin.deck_number} · ${categoryLabel(cabin)} · Spatial Orientation Report`;
}

export function categoryLabel(cabin: CabinData): string {
  const map: Record<string, string> = {
    BA: 'Balcony Stateroom',
    BA_ACC: 'Accessible Balcony Stateroom',
    IB: 'Interior Stateroom',
    OV: 'Ocean View Stateroom',
    YC: 'Yacht Club Suite',
  };
  return map[cabin.category_code] ?? `Category ${cabin.category_code}`;
}

function setMeta(selector: string, value: string) {
  const el = document.querySelector(selector);
  if (el) el.setAttribute('content', value);
}
function setLink(id: string, href: string) {
  const el = document.getElementById(id);
  if (el) el.setAttribute('href', href);
}

/** Update document title + OpenGraph/Twitter/canonical for the current cabin. */
export function updateSocialHead(ship: ShipData, cabin: CabinData) {
  const title = briefingTitle(ship, cabin);
  const desc = briefingDescription(cabin);
  const url = cabinUrl(cabin.cabin_number);
  document.title = `${title} — Timonelo`;
  setMeta('meta[name="description"]', desc);
  setMeta('meta[property="og:title"]', title);
  setMeta('meta[property="og:description"]', desc);
  setMeta('meta[name="twitter:title"]', title);
  setMeta('meta[name="twitter:description"]', desc);
  setLink('canonical-url', url);
  setMeta('#og-url', url); // guarded: only if present
  const og = document.getElementById('og-url');
  if (og) og.setAttribute('content', url);
  // Keep the address bar shareable without a full navigation.
  try {
    window.history.replaceState(null, '', `/?cabin=${cabin.cabin_number}`);
  } catch {
    /* no-op */
  }
}

export type ShareResult = 'shared' | 'copied' | 'unavailable';

/** Native share with graceful fallback to copying the link. */
export async function shareBriefing(ship: ShipData, cabin: CabinData): Promise<ShareResult> {
  const data = {
    title: briefingTitle(ship, cabin),
    text: `${briefingTitle(ship, cabin)} — ${briefingDescription(cabin)}`,
    url: cabinUrl(cabin.cabin_number),
  };
  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      await navigator.share(data);
      return 'shared';
    } catch {
      return 'unavailable';
    }
  }
  return (await copyLink(cabin.cabin_number)) ? 'copied' : 'unavailable';
}

export async function copyLink(cabinNumber: string): Promise<boolean> {
  const url = cabinUrl(cabinNumber);
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(url);
      return true;
    }
  } catch {
    /* fall through */
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = url;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

/** Read a cabin number from the URL (?cabin= or /ship/cabin/NNNN path). */
export function cabinFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  const q = params.get('cabin');
  if (q) return q;
  const m = window.location.pathname.match(/\/cabin\/([A-Za-z0-9]+)/);
  return m ? m[1] : null;
}
