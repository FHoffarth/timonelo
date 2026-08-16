/**
 * Canonical public URL structure and route parsing for Timonelo.
 *
 * Supported URL patterns:
 *   /{ship-slug}/cabin/{cabin-number}      e.g. /ms-andorinha/cabin/214
 *   /{ship-slug}/deck/{deck-number}        e.g. /ms-andorinha/deck/3
 *   /{ship-slug}                           e.g. /ms-andorinha
 *
 * Query parameter fallbacks:
 *   ?ship=ms-andorinha&cabin=214
 *   ?ship=ms-andorinha&deck=3
 */

export interface ParsedRoute {
  shipSlug: string;
  cabinNumber?: string;
  deckNumber?: number;
}

const CABIN_PATH = /^\/([a-z0-9][a-z0-9-]*)\/cabin\/([A-Za-z0-9]+)\/?$/;
const DECK_PATH = /^\/([a-z0-9][a-z0-9-]*)\/deck\/([0-9]+)\/?$/;
const SHIP_ONLY_PATH = /^\/([a-z0-9][a-z0-9-]*)\/?$/;

/** Build the canonical path for a cabin. */
export function cabinPath(shipSlug: string, cabinNumber: string): string {
  return `/${shipSlug}/cabin/${cabinNumber}`;
}

/** Build the canonical path for a deck. */
export function deckPath(shipSlug: string, deckNumber: number): string {
  return `/${shipSlug}/deck/${deckNumber}`;
}

/** Build the canonical path for a ship. */
export function shipPath(shipSlug: string): string {
  return `/${shipSlug}`;
}

/** Parse any supported route from a pathname. */
export function parseRoute(pathname: string): ParsedRoute | null {
  const cabinMatch = pathname.match(CABIN_PATH);
  if (cabinMatch) {
    return { shipSlug: cabinMatch[1], cabinNumber: cabinMatch[2] };
  }

  const deckMatch = pathname.match(DECK_PATH);
  if (deckMatch) {
    return { shipSlug: deckMatch[1], deckNumber: parseInt(deckMatch[2], 10) };
  }

  const shipMatch = pathname.match(SHIP_ONLY_PATH);
  if (shipMatch && shipMatch[1] !== 'index.html') {
    return { shipSlug: shipMatch[1] };
  }

  return null;
}

/** Backward-compatible helper for cabin routes. */
export function parseCabinRoute(pathname: string): { shipSlug: string; cabinNumber: string } | null {
  const route = parseRoute(pathname);
  if (route && route.cabinNumber) {
    return { shipSlug: route.shipSlug, cabinNumber: route.cabinNumber };
  }
  return null;
}

/** Query fallbacks: ?ship=SLUG, ?cabin=NNNN, ?deck=NN. */
export function routeFromLocation(loc: { pathname: string; search: string }): ParsedRoute {
  const parsed = parseRoute(loc.pathname);
  const searchParams = new URLSearchParams(loc.search);
  const queryShip = searchParams.get('ship');
  const queryCabin = searchParams.get('cabin');
  const queryDeck = searchParams.get('deck');

  const shipSlug = parsed?.shipSlug || queryShip || 'msc-bellissima';
  const cabinNumber = parsed?.cabinNumber || queryCabin || undefined;
  const deckNumber = parsed?.deckNumber || (queryDeck ? parseInt(queryDeck, 10) : undefined);

  return { shipSlug, cabinNumber, deckNumber };
}

/** Resolve the cabin number from the current location. */
export function cabinFromLocation(loc: { pathname: string; search: string }): string | null {
  const route = routeFromLocation(loc);
  return route.cabinNumber ?? null;
}
