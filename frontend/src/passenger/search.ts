import { LIVE_TEST_TRIP } from '../trip-shell/liveTestContext';
import { knowledgeRepository } from '../knowledge';
import type { NavRoute } from '../components/ui/MainNavbar';

export interface PassengerDestination {
  kind: 'page' | 'ship' | 'port' | 'cabin' | 'venue';
  label: string;
  detail: string;
  route: NavRoute | 'cabin';
  param?: string;
}

export const PORT_SLUGS = ['barcelona', 'marseille', 'genoa', 'naples', 'messina', 'valletta'] as const;
export const referenceVenues = knowledgeRepository.getRestaurants(LIVE_TEST_TRIP.vesselSlug)
  .map((venue: { id: string; name: string }) => ({ id: venue.id, name: venue.name }));

const destinations: PassengerDestination[] = [
  { kind: 'ship', label: 'MSC Bellissima', detail: 'Ship guide and data availability', route: 'ships', param: LIVE_TEST_TRIP.vesselSlug },
  { kind: 'page', label: 'My Cruise', detail: 'Past Shanghai → Tokyo reference voyage', route: 'my-cruise' },
  { kind: 'page', label: 'Routes', detail: 'Shanghai → Tokyo itinerary availability', route: 'routes' },
  { kind: 'page', label: 'Travel Info', detail: 'Entry requirements availability', route: 'travel-info' },
  { kind: 'page', label: 'Cruise Math', detail: 'Example pricing calculator; drink packages and costs', route: 'cruise-math' },
  { kind: 'page', label: 'Ports', detail: 'Reference library; not this voyage’s itinerary', route: 'ports' },
  ...PORT_SLUGS.map(param => ({ kind: 'port' as const, label: param[0].toUpperCase() + param.slice(1), detail: 'Port reference guide; not a stop on the reference voyage', route: 'ports' as const, param })),
  ...referenceVenues.map(venue => ({ kind: 'venue' as const, label: venue.name, detail: 'Unverified restaurant reference — ship directory', route: 'ships' as const, param: LIVE_TEST_TRIP.vesselSlug })),
];

export function searchPassengerDestinations(query: string): PassengerDestination[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const cabin = q.match(/^(?:cabin\s*)?(\d{4,5})$/);
  if (cabin) return [{ kind: 'cabin', label: `Cabin ${cabin[1]}`, detail: 'Check availability; this search does not confirm cabin identity', route: 'cabin', param: cabin[1] }];
  return destinations.filter(item => `${item.label} ${item.detail}`.toLowerCase().includes(q)).slice(0, 12);
}
