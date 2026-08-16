/**
 * Canonical public URL structure and route parsing for Timonelo.
 *
 * Supported URL patterns:
 *   /                                      -> Fleet Landing
 *   /fleet                                 -> Fleet Gallery View
 *   /vessels/{ship-slug}                   -> Dedicated Ship Landing Page
 *   /ships/{ship-slug}                     -> Dedicated Ship Landing Page
 *   /{ship-slug}                           -> Dedicated Ship Landing Page
 *   /{ship-slug}/cabin/{cabin-number}      -> Specific Stateroom Dossier
 *   /{ship-slug}/deck/{deck-number}        -> Specific Deck Explorer
 *   /ports                                 -> Port Explorer
 *   /ports/{port-slug}                     -> Specific Port Dossier
 *   /crew                                  -> Verified Crew Contributor Programme
 *   /mission                               -> Why Timonelo Exists
 *   /why-timonelo                          -> Why Timonelo Exists
 *   /intelligence                          -> Cruise Intelligence Section
 *   /about                                 -> Constitutional & Platform Philosophy
 */

export interface ParsedRoute {
  viewMode: 'landing' | 'vessel' | 'cabin' | 'port' | 'crew' | 'mission';
  shipSlug?: string;
  cabinNumber?: string;
  deckNumber?: number;
  portSlug?: string;
  sectionTarget?: 'fleet' | 'intelligence' | 'about';
}

const CABIN_PATH = /^\/([a-z0-9][a-z0-9-]*)\/cabin\/([A-Za-z0-9]+)\/?$/;
const DECK_PATH = /^\/([a-z0-9][a-z0-9-]*)\/deck\/([0-9]+)\/?$/;
const VESSEL_PATH = /^\/(?:vessels|ships)\/([a-z0-9][a-z0-9-]*)\/?$/;
const PORT_PATH = /^\/ports\/([a-z0-9][a-z0-9-]*)\/?$/;
const SHORT_SHIP_PATH = /^\/([a-z0-9][a-z0-9-]*)\/?$/;

/** Known standalone view paths */
const SPECIAL_PATHS = ['fleet', 'intelligence', 'about', 'ports', 'crew', 'mission', 'why-timonelo'];

/** Build the canonical path for a cabin */
export function cabinPath(shipSlug: string, cabinNumber: string): string {
  return `/${shipSlug}/cabin/${cabinNumber}`;
}

/** Build the canonical path for a deck */
export function deckPath(shipSlug: string, deckNumber: number): string {
  return `/${shipSlug}/deck/${deckNumber}`;
}

/** Build the canonical path for a vessel overview */
export function vesselPath(shipSlug: string): string {
  return `/vessels/${shipSlug}`;
}

/** Build the canonical path for a port */
export function portPath(portSlug: string): string {
  return `/ports/${portSlug}`;
}

/** Parse any supported route from a pathname */
export function parseRoute(pathname: string): ParsedRoute {
  const cleanPath = pathname.replace(/\/+$/, '') || '/';

  if (cleanPath === '/' || cleanPath === '/index.html') {
    return { viewMode: 'landing' };
  }

  if (cleanPath === '/fleet') {
    return { viewMode: 'landing', sectionTarget: 'fleet' };
  }

  if (cleanPath === '/intelligence') {
    return { viewMode: 'landing', sectionTarget: 'intelligence' };
  }

  if (cleanPath === '/about') {
    return { viewMode: 'landing', sectionTarget: 'about' };
  }

  if (cleanPath === '/ports') {
    return { viewMode: 'port' };
  }

  const portMatch = cleanPath.match(PORT_PATH);
  if (portMatch) {
    return {
      viewMode: 'port',
      portSlug: portMatch[1],
    };
  }

  if (cleanPath === '/crew') {
    return { viewMode: 'crew' };
  }

  if (cleanPath === '/mission' || cleanPath === '/why-timonelo') {
    return { viewMode: 'mission' };
  }

  const cabinMatch = cleanPath.match(CABIN_PATH);
  if (cabinMatch) {
    return {
      viewMode: 'cabin',
      shipSlug: cabinMatch[1],
      cabinNumber: cabinMatch[2],
    };
  }

  const deckMatch = cleanPath.match(DECK_PATH);
  if (deckMatch) {
    return {
      viewMode: 'cabin',
      shipSlug: deckMatch[1],
      deckNumber: parseInt(deckMatch[2], 10),
    };
  }

  const vesselMatch = cleanPath.match(VESSEL_PATH);
  if (vesselMatch) {
    return {
      viewMode: 'vessel',
      shipSlug: vesselMatch[1],
    };
  }

  const shortMatch = cleanPath.match(SHORT_SHIP_PATH);
  if (shortMatch && !SPECIAL_PATHS.includes(shortMatch[1])) {
    return {
      viewMode: 'vessel',
      shipSlug: shortMatch[1],
    };
  }

  return { viewMode: 'landing' };
}

/** Parse current browser location into a ParsedRoute */
export function routeFromLocation(loc: Location): ParsedRoute {
  return parseRoute(loc.pathname);
}
