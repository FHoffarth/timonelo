import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { searchPassengerDestinations } from './search';
import BellissimaGuide from './BellissimaGuide';

describe('passenger destinations', () => {
  it('keeps cabin requests, reference ports and restaurant references distinct', () => {
    expect(searchPassengerDestinations('14122')[0]).toMatchObject({ kind: 'cabin', route: 'cabin', param: '14122' });
    expect(searchPassengerDestinations('Genoa')[0]).toMatchObject({ kind: 'port', route: 'ports', param: 'genoa' });
    expect(searchPassengerDestinations('Posidonia')[0]).toMatchObject({ kind: 'venue', route: 'ships' });
    expect(searchPassengerDestinations('Posidonia')[0].detail).toMatch(/Unverified/);
  });
  it('does not invent a cabin fallback or voyage when nothing matches', () => {
    expect(searchPassengerDestinations('cabin')).toEqual([]);
    expect(searchPassengerDestinations('Santorini')).toEqual([]);
    expect(searchPassengerDestinations('not-a-destination')).toEqual([]);
    expect(searchPassengerDestinations('cabin 99999')[0].detail).toMatch(/does not confirm cabin identity/);
  });
  it('finds existing tools and explains unavailable vessel facts', () => {
    expect(searchPassengerDestinations('drink packages')[0].route).toBe('cruise-math');
    const html = renderToStaticMarkup(<BellissimaGuide onNavigate={() => {}} />);
    expect(html).toContain('Ship information');
    expect(html).toContain('not available in this beta');
    expect(html).toContain('Restaurant reference directory');
    expect(html).toContain('Unverified reference');
    expect(html).not.toMatch(/PUBLISH_ALLOWED|SUPPORTED|verified restaurants|step-free/);
    expect(html).toContain('Check cabin');
    expect(html).toContain('Deck 14 — availability');
  });
});
