/**
 * The one passenger trip context Beta 0.1 has.
 *
 * Timonelo's reachable surfaces used to each pick their own voyage: the ship
 * page opened on Bellissima, the port pillar on Santorini, the route page on a
 * Western Mediterranean loop, Cruise Math on Virtuosa. Four surfaces, four
 * voyages, one build, and nothing to reconcile them because no shared context
 * existed. This is that context, and it is deliberately small: one trip, the
 * fields the current surfaces actually read, and nothing built for a second
 * passenger who does not exist yet.
 *
 * WHAT THIS IS NOT
 *
 * These values are product/live-test context. They are not governed truth.
 * They are read from the same fixture My Cruise has always rendered, and that
 * fixture cites STM-0403..STM-0410 -- the eight statements the backend no
 * longer admits, because their only source is a private booking confirmation
 * whose bytes are not held, and because the two inferred port linkages cite a
 * rule this repository cannot resolve. The fixture also carries
 * `publishability: PUBLISH_ALLOWED`, which was true when it was written and is
 * not true now.
 *
 * So that field is deliberately not read here and not exposed. Nothing in this
 * module may be presented to a passenger as verified, publication-approved or
 * governed. It exists so surfaces agree on which voyage the tester is on --
 * not to tell them that voyage has been proven.
 */

import referenceVoyageFixture from '../fixtures/reference_voyage_bellissima.json';

const pack = referenceVoyageFixture.passenger_pack;

export interface LiveTestPortContext {
  /** Passenger-facing place name, e.g. "Shanghai, China". */
  readonly location: string;
  /** City alone, for compact labels. */
  readonly city: string;
  /** UN/LOCODE as the fixture records it. */
  readonly unlocode: string;
  /** ISO date, e.g. "2026-10-04". */
  readonly date: string;
}

export interface LiveTestTripContext {
  readonly voyageEntity: string;
  readonly vesselName: string;
  /** The slug the ship surfaces route by. */
  readonly vesselSlug: string;
  readonly departure: LiveTestPortContext;
  readonly arrival: LiveTestPortContext;
  readonly checkInTime: string;
  /** One short label for chrome that needs to name the trip. */
  readonly shortLabel: string;
}

function cityOf(location: string): string {
  return location.split(',')[0]?.trim() || location;
}

export const LIVE_TEST_TRIP: LiveTestTripContext = {
  voyageEntity: pack.voyage_entity,
  vesselName: pack.vessel_name,
  // The fixture records the vessel by display name; the ship surfaces route by
  // slug. Derived rather than hardcoded a second time, so the two cannot drift.
  vesselSlug: pack.vessel_name.toLowerCase().replace(/\s+/g, '-'),
  departure: {
    location: pack.departure_location,
    city: cityOf(pack.departure_location),
    unlocode: pack.departure_port_unlocode,
    date: pack.departure_date,
  },
  arrival: {
    location: pack.arrival_location,
    city: cityOf(pack.arrival_location),
    unlocode: pack.arrival_port_unlocode,
    date: pack.arrival_date,
  },
  checkInTime: pack.check_in_time,
  shortLabel: `${pack.vessel_name} · ${cityOf(pack.departure_location)} → ${cityOf(pack.arrival_location)}`,
};

/**
 * Whether a surface is being asked about the trip the tester is actually on.
 *
 * Used by surfaces that hold data for some other voyage. They may not show it
 * as this passenger's, and they may not quietly show it anyway: the answer to
 * "do you have this voyage?" is either yes or an explicit no.
 */
export function isLiveTestVoyage(vesselSlugOrName: string | undefined | null): boolean {
  if (!vesselSlugOrName) return false;
  const normalized = vesselSlugOrName.trim().toLowerCase().replace(/\s+/g, '-');
  return normalized === LIVE_TEST_TRIP.vesselSlug;
}
