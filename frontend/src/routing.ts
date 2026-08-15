/**
 * Canonical public URL structure for Timonelo.
 *
 *   /{ship-slug}/cabin/{cabin-number}      e.g. /msc-bellissima/cabin/14122
 *
 * This is the permanent public URL shape. The functions here are pure and
 * framework-free: the same `parseCabinRoute` can be run on the server later to
 * adopt SSR without changing any public URL. Client-side today, no backend
 * routing — the static host serves index.html for these paths (SPA fallback).
 */

export interface CabinRoute {
  shipSlug: string;
  cabinNumber: string;
}

const CABIN_PATH = /^\/([a-z0-9][a-z0-9-]*)\/cabin\/([A-Za-z0-9]+)\/?$/;

/** Build the canonical path for a cabin. */
export function cabinPath(shipSlug: string, cabinNumber: string): string {
  return `/${shipSlug}/cabin/${cabinNumber}`;
}

/** Parse a canonical cabin path. Returns null if the path is not a cabin route. */
export function parseCabinRoute(pathname: string): CabinRoute | null {
  const m = pathname.match(CABIN_PATH);
  return m ? { shipSlug: m[1], cabinNumber: m[2] } : null;
}

/** Legacy/query fallbacks so old links keep working: ?cabin=NNNN. */
export function cabinFromQuery(search: string): string | null {
  return new URLSearchParams(search).get('cabin');
}

/** Resolve the cabin number from the current location (path first, then query). */
export function cabinFromLocation(loc: { pathname: string; search: string }): string | null {
  return parseCabinRoute(loc.pathname)?.cabinNumber ?? cabinFromQuery(loc.search);
}
