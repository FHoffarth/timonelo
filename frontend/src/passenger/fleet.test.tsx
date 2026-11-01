import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { FLEET, getFleetShip, parseFleetProjection, type FleetProjection } from './fleet';
import { FleetProfile } from './FleetDiscovery';
import { searchPassengerDestinations } from './search';

describe('fleet discovery boundary', () => {
  it('offers exactly the nine requested catalog entries, without claiming identity admission', () => {
    expect(FLEET).toHaveLength(9);
    expect(new Set(FLEET.map(s => s.slug)).size).toBe(9);
    for (const ship of FLEET) {
      expect(searchPassengerDestinations(ship.label)[0]).toMatchObject({ route: 'ships', param: ship.slug });
      expect(getFleetShip(ship.slug)).toEqual(ship);
    }
    expect(getFleetShip('another-ship')).toBeUndefined();
  });
  it('refuses incomplete or malformed projection input', () => {
    expect(parseFleetProjection(null)).toBeNull();
    expect(parseFleetProjection({ schema: 'wrong', ships: {} })).toBeNull();
    expect(parseFleetProjection({ schema: 'timonelo.fleet.v1', ships: { 'msc-meraviglia': { level: 3 } } })).toBeNull();
  });
  it('keeps cabin requests scoped to the selected vessel', () => {
    const request = searchPassengerDestinations('14122', 'msc-meraviglia')[0];
    expect(request.vesselSlug).toBe('msc-meraviglia');
    expect(request.detail).toContain('MSC Meraviglia');
    expect(request.detail).not.toContain('Bellissima');
  });
  it('renders a transported canonical answer with its source and refuses cross-vessel transport', () => {
    // Synthetic transport fixture, never written into the canonical evidence store.
    const projection: FleetProjection = { schema: 'timonelo.fleet.v1', as_of: '2026-11-01', ships: {} };
    for (const s of FLEET) projection.ships[s.slug] = { candidate_count: 0, level: 0, facts: [], sources: [] };
    projection.ships['msc-bellissima'] = { candidate_count: 1, level: 0,
      sources: [{ artifact_id: 'ART-TEST', filename: 'test-map.pdf', sha256: 'a'.repeat(64) }],
      facts: [{ statement_id: 'STM-TEST', entity_id: 'venue:MSC-BELLISSIMA:test-restaurant', question_id: 'Q-TEST',
        statement_type: 'deck.venue_present', section: 'venues', value: [6], artifact_id: 'ART-TEST', page: 4,
        locator: 'Test table row', publish_status: 'PUBLISH_ALLOWED' }] };
    expect(parseFleetProjection(projection)).not.toBeNull();
    const html = renderToStaticMarkup(<FleetProfile ship={FLEET[0]} profile={projection.ships[FLEET[0].slug]} onNavigate={() => {}} />);
    expect(html).toContain('test restaurant');
    expect(html).toContain('ART-TEST');
    expect(html).toContain('Test table row');
    projection.ships['msc-meraviglia'] = projection.ships['msc-bellissima'];
    expect(parseFleetProjection(projection)).toBeNull();
  });
  it('does not borrow Bellissima material for another ship or for a failed projection', () => {
    for (const ship of FLEET.filter(s => s.slug !== 'msc-bellissima')) {
      const html = renderToStaticMarkup(<FleetProfile ship={ship} profile={undefined} onNavigate={() => {}} />);
      expect(html).toContain(ship.label);
      expect(html).toContain('Publication data unavailable');
      expect(html).not.toMatch(/Posidonia|14122|Shanghai|Deck 14|Bellissima/);
    }
  });
});
