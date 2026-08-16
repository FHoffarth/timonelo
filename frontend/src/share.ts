/**
 * Sharing, canonical links, and social preview metadata for a cabin briefing.
 * Presentation-layer only — no backend, no routing framework. The cabin is
 * carried in a query param so the link loads the same briefing when opened.
 */
import type { ShipData, CabinData } from './types';
import { cabinPath } from './routing';

export function shipSlug(ship: ShipData): string {
  return ship.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

/** The canonical, permanent public path: /{ship}/cabin/{number}. */
export function canonicalPath(ship: ShipData, cabinNumber: string): string {
  return cabinPath(shipSlug(ship), cabinNumber);
}

/** Absolute canonical URL that reopens this cabin. */
export function cabinUrl(ship: ShipData, cabinNumber: string): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : 'https://timonelo.com';
  return `${origin}${canonicalPath(ship, cabinNumber)}`;
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
    ES: 'Emerald Riverview Stateroom',
    RFB: 'Ruby French Balcony Stateroom',
    DSU: 'Diamond Master Suite',
    DFB: 'Diamond French Balcony Stateroom',
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

/**
 * Update document title + OpenGraph/Twitter/canonical for the current cabin.
 * History (the address-bar URL) is owned by the router in App, not here.
 */
export function updateSocialHead(ship: ShipData, cabin: CabinData) {
  const title = briefingTitle(ship, cabin);
  const desc = briefingDescription(cabin);
  const url = cabinUrl(ship, cabin.cabin_number);
  document.title = `${title} — Timonelo`;
  setMeta('meta[name="description"]', desc);
  setMeta('meta[property="og:title"]', title);
  setMeta('meta[property="og:description"]', desc);
  setMeta('meta[name="twitter:title"]', title);
  setMeta('meta[name="twitter:description"]', desc);
  setLink('canonical-url', url);
  const og = document.getElementById('og-url');
  if (og) og.setAttribute('content', url);
}

export type ShareResult = 'shared' | 'copied' | 'unavailable';

/** Native share with graceful fallback to copying the link. */
export async function shareBriefing(ship: ShipData, cabin: CabinData): Promise<ShareResult> {
  const data = {
    title: briefingTitle(ship, cabin),
    text: `${briefingTitle(ship, cabin)} — ${briefingDescription(cabin)}`,
    url: cabinUrl(ship, cabin.cabin_number),
  };
  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      await navigator.share(data);
      return 'shared';
    } catch {
      return 'unavailable';
    }
  }
  return (await copyLink(ship, cabin.cabin_number)) ? 'copied' : 'unavailable';
}

export async function copyLink(ship: ShipData, cabinNumber: string): Promise<boolean> {
  const url = cabinUrl(ship, cabinNumber);
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
