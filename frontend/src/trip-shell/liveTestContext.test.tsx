/**
 * BC-2 — one voyage, everywhere, or an explicit refusal.
 *
 * Before this, each reachable surface picked its own voyage and none of them
 * knew about the others. The ship page opened on Bellissima; the landing page's
 * Ship Intelligence pillar navigated to MSC Virtuosa and hit the "not mapped"
 * dead end; Travel Info printed Schengen visa guidance under a promise that it
 * had been researched for your itinerary; Route Intelligence presented a
 * 7-night Western Mediterranean loop, rated "5/5 Verified" by a hardcoded
 * string, as the passenger's route; Cruise Math totalled a Mediterranean
 * holiday aboard Virtuosa. The live tester sails Bellissima, Shanghai to Tokyo,
 * 4-7 October 2026.
 *
 * These tests assert what a passenger can see. Each surface must either work
 * inside that one context or say plainly that it does not have this voyage --
 * never quietly show a different one.
 */

import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

import { LIVE_TEST_TRIP, isLiveTestVoyage } from './liveTestContext';
import HomePage from '../components/pages/HomePage';
import TravelInfoPage from '../components/pages/TravelInfoPage';
import RouteIntelligencePage from '../components/pages/RouteIntelligencePage';
import CruiseMathPage from '../components/pages/CruiseMathPage';
import PortGuidePage from '../components/pages/PortGuidePage';
import { ReferenceTripShellPreview } from '../components/pages/TripShellPage';

const here = dirname(fileURLToPath(import.meta.url));
const appSource = readFileSync(resolve(here, '../App.tsx'), 'utf8');

/** Anything that would tell a passenger they are on a different voyage. */
const OTHER_VOYAGE = [
  /virtuosa/i,
  /western mediterranean/i,
  /adriatic/i,
  /aegean/i,
  /schengen/i,
];

function expectNoOtherVoyage(html: string) {
  for (const pattern of OTHER_VOYAGE) {
    expect(html).not.toMatch(pattern);
  }
}

describe('BC-2: the shared live-test context', () => {
  it('is the Bellissima Shanghai to Tokyo trip, read from the existing fixture', () => {
    expect(LIVE_TEST_TRIP.vesselName).toBe('MSC BELLISSIMA');
    expect(LIVE_TEST_TRIP.vesselSlug).toBe('msc-bellissima');
    expect(LIVE_TEST_TRIP.departure.city).toBe('Shanghai');
    expect(LIVE_TEST_TRIP.arrival.city).toBe('Tokyo');
    expect(LIVE_TEST_TRIP.departure.date).toBe('2026-10-04');
    expect(LIVE_TEST_TRIP.arrival.date).toBe('2026-10-07');
    expect(LIVE_TEST_TRIP.departure.unlocode).toBe('CNSGH');
    expect(LIVE_TEST_TRIP.arrival.unlocode).toBe('JPTYO');
  });

  it('does not carry the fixture\'s stale PUBLISH_ALLOWED assertion', () => {
    // The backend no longer admits STM-0403..STM-0410, so the fixture's
    // publishability field is a claim this context must not relay. Product
    // context, not governed truth.
    expect(JSON.stringify(LIVE_TEST_TRIP)).not.toMatch(/PUBLISH_ALLOWED/);
    expect(Object.keys(LIVE_TEST_TRIP)).not.toContain('publishability');
  });

  it('recognises only the live-test vessel', () => {
    expect(isLiveTestVoyage('msc-bellissima')).toBe(true);
    expect(isLiveTestVoyage('MSC Bellissima')).toBe(true);
    expect(isLiveTestVoyage('msc-virtuosa')).toBe(false);
    expect(isLiveTestVoyage(undefined)).toBe(false);
  });
});

describe('BC-2 A: Home targets the live-test vessel', () => {
  const html = renderToStaticMarkup(
    <HomePage onNavigate={() => undefined} onSearch={() => undefined} />,
  );

  it('Ship Intelligence navigates to Bellissima, not Virtuosa', () => {
    let target: string | undefined;
    renderToStaticMarkup(
      <HomePage
        onNavigate={(_route, param) => { target = param; }}
        onSearch={() => undefined}
      />,
    );
    // The pillar's handler is what matters; assert the source wiring reaches
    // the shared context rather than a hardcoded slug.
    const homeSource = readFileSync(
      resolve(here, '../components/pages/HomePage.tsx'), 'utf8');
    expect(homeSource).not.toMatch(/msc-virtuosa/);
    expect(homeSource).toMatch(/LIVE_TEST_TRIP\.vesselSlug/);
    expect(target).toBeUndefined(); // nothing navigates on render
  });

  it('names no other vessel or region', () => {
    expectNoOtherVoyage(html);
  });

  it('does not present an unrelated port as the passenger\'s', () => {
    const homeSource = readFileSync(
      resolve(here, '../components/pages/HomePage.tsx'), 'utf8');
    expect(homeSource).not.toMatch(/onNavigate\("ports",\s*"santorini"\)/);
  });
});

describe('BC-2 B: app defaults establish no other voyage', () => {
  it('does not default to another voyage\'s port or route', () => {
    expect(appSource).not.toMatch(/useState<string>\("santorini"\)/);
    expect(appSource).not.toMatch(/useState<string>\("7-night-adriatic-aegean"\)/);
    expect(appSource).toMatch(/LIVE_TEST_TRIP\.vesselSlug/);
  });

  it('names MSC Virtuosa nowhere in the reachable app shell', () => {
    expect(appSource).not.toMatch(/virtuosa/i);
  });
});

describe('BC-2 C: My Cruise renders the live-test trip', () => {
  const html = renderToStaticMarkup(<ReferenceTripShellPreview />);

  it('shows the vessel, both ports and the dates', () => {
    expect(html).toMatch(/Bellissima/i);
    expect(html).toMatch(/Shanghai/);
    expect(html).toMatch(/Tokyo/);
    expect(html).toMatch(/2026/);
  });

  it('is framed as a live-test trip, not a demo preview', () => {
    expect(html).toMatch(/Live-test trip/i);
    expect(html).not.toMatch(/Reference Voyage Preview/i);
  });

  it('does not claim the voyage is verified or publication-approved', () => {
    expect(html).not.toMatch(/publication[- ]approved/i);
    expect(html).not.toMatch(/verified voyage/i);
  });

  it('keeps terminal and berth assignments pending rather than inventing them', () => {
    expect(html).toMatch(/Not confirmed yet/i);
  });

  it('names no other voyage', () => {
    expectNoOtherVoyage(html);
  });
});

describe('BC-2 D/E: Travel Info refuses rather than misleads', () => {
  const html = renderToStaticMarkup(<TravelInfoPage />);

  it('shows no Mediterranean or Schengen guidance for this voyage', () => {
    expectNoOtherVoyage(html);
    expect(html).not.toMatch(/zero advance visa/i);
    expect(html).not.toMatch(/Dubrovnik|Corfu|Mykonos|Venice|Bari/);
  });

  it('no longer claims the content was researched for this itinerary', () => {
    expect(html).not.toMatch(/researched for your specific itinerary/i);
  });

  it('states explicitly that requirements are unavailable and must be verified', () => {
    expect(html).toMatch(/do not have travel requirements for this voyage yet/i);
    expect(html).toMatch(/verify/i);
  });

  it('names the passenger\'s actual voyage', () => {
    expect(html).toMatch(/Shanghai/);
    expect(html).toMatch(/Tokyo/);
  });
});

describe('BC-2 F/G: Route Intelligence shows no other route', () => {
  const html = renderToStaticMarkup(
    <RouteIntelligencePage onSelectPort={() => undefined} />,
  );

  it('does not present the Western Mediterranean loop as the live-test route', () => {
    expectNoOtherVoyage(html);
    expect(html).not.toMatch(/EMBARKATION \/ HOMEPORT/);
  });

  it('does not render an unsupported confidence rating', () => {
    expect(html).not.toMatch(/5\s*\/\s*5/);
    expect(html).not.toMatch(/Verified/);
  });

  it('says plainly that this route is not mapped yet', () => {
    expect(html).toMatch(/have not mapped this route yet/i);
    expect(html).toMatch(/Shanghai/);
    expect(html).toMatch(/Tokyo/);
  });
});

describe('BC-2 H: Cruise Math implies no vessel and quotes no fare', () => {
  const html = renderToStaticMarkup(<CruiseMathPage />);

  it('does not present Virtuosa or the Mediterranean as the current trip', () => {
    expectNoOtherVoyage(html);
    expect(html).not.toMatch(/Selected Ship/i);
  });

  it('labels its pricing as an example, not the passenger\'s booking', () => {
    expect(html).toMatch(/example/i);
    expect(html).toMatch(/not your booking|not quoted prices|not your fare/i);
  });
});

describe('BC-2 I: Port guides are reference material', () => {
  const html = renderToStaticMarkup(
    <PortGuidePage onSelectPort={() => undefined} />,
  );

  it('frames itself as a reference library rather than the itinerary', () => {
    expect(html).toMatch(/PORT REFERENCE LIBRARY/i);
    expect(html).toMatch(/not a stop on\s*your voyage/i);
  });

  it('does not claim an unrelated port belongs to this voyage', () => {
    expect(html).toMatch(/have not yet researched/i);
    expect(html).toMatch(/Shanghai/);
  });
});

describe('BC-2 J: search entries inherit the same context', () => {
  it('port keywords open reference browsing, not a preselected port', () => {
    expect(appSource).not.toMatch(/handleNavigate\("ports",\s*q\.includes\("genoa"\)/);
    expect(appSource).toMatch(/handleNavigate\("ports"\)/);
  });

  it('route keywords no longer resolve to another voyage\'s itinerary', () => {
    expect(appSource).not.toMatch(/handleNavigate\("routes",\s*"7-night-adriatic-aegean"\)/);
    expect(appSource).toMatch(/handleNavigate\("routes"\)/);
  });

  it('the unmatched fallback and entity select both use the live-test vessel', () => {
    expect(appSource).not.toMatch(/handleNavigate\("ships",\s*"msc-bellissima"\)/);
    expect(appSource).toMatch(/handleNavigate\("ships",\s*LIVE_TEST_TRIP\.vesselSlug\)/);
    expect(appSource).toMatch(/setSelectedShipSlug\(LIVE_TEST_TRIP\.vesselSlug\)/);
  });
});
