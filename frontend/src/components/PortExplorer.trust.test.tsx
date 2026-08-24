import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { PortExplorer } from './PortExplorer';
import { LanguageProvider } from '../i18n';
import { PORTS_REGISTRY, getPortBySlug } from '../ports';
import { PORTS_REGISTRY as RAW_PORTS } from '../generated/ports';

/**
 * Passenger-surface trust boundary (audit U-1).
 *
 * The port page is where an evidence gap becomes a decision. Someone reads a
 * walking time and leaves the ship without a shuttle; reads an emergency
 * number and dials it. So the rule for this surface is stricter than "do not
 * display wrong data": it must not convert an absent value into advice.
 *
 * The specific defect these cover: `(walkingTimeMin ?? 0) > 0` collapsed
 * "unknown" and "zero" into one branch and answered both with "Shuttle
 * transfer or taxi recommended". Not knowing how far the centre is does not
 * imply a shuttle exists, and it does not imply walking is impractical.
 *
 * Assertions run against real rendered markup rather than against the model,
 * because the claim under test is what a passenger sees.
 */

const render = (slug: string) =>
  renderToStaticMarkup(
    <LanguageProvider>
      <PortExplorer initialPortSlug={slug} onSelectShip={() => {}} />
    </LanguageProvider>,
  );

const ALL_SLUGS = PORTS_REGISTRY.map((p) => p.slug);

/** Advice that must never appear as a consequence of a missing value. */
const OPERATIONAL_ADVICE = [
  'Shuttle transfer or taxi recommended',
  'Shuttle-Transfer oder Taxi empfohlen',
  'shuttle recommended',
  'taxi recommended',
  'Taxi empfohlen',
  'walking not recommended',
  'Gehen nicht empfohlen',
];

describe('PortExplorer — unknown values stay unknown', () => {
  it('never renders transport advice for any port', () => {
    for (const slug of ALL_SLUGS) {
      const html = render(slug);
      for (const phrase of OPERATIONAL_ADVICE) {
        expect(
          html.toLowerCase(),
          `port "${slug}" renders operational advice: ${phrase}`,
        ).not.toContain(phrase.toLowerCase());
      }
    }
  });

  it('states walking time as unknown rather than inferring a transfer', () => {
    for (const slug of ALL_SLUGS) {
      const port = getPortBySlug(slug);
      if (port?.distanceToCenterKm == null) continue; // panel not rendered
      const html = render(slug);
      const known =
        typeof port.walkingTimeMin === 'number' && port.walkingTimeMin > 0;
      if (!known) {
        expect(
          html.includes('Walking time unknown') ||
            html.includes('Gehzeit unbekannt'),
          `port "${slug}" has no walking time but does not say so`,
        ).toBe(true);
      }
    }
  });

  it('renders a known positive walking time verbatim', () => {
    // Guards against fixing the leak by suppressing real values too.
    const withWalk = PORTS_REGISTRY.find(
      (p) =>
        typeof p.walkingTimeMin === 'number' &&
        p.walkingTimeMin > 0 &&
        p.distanceToCenterKm != null,
    );
    if (!withWalk) {
      // Correct current state: every curated walking time was unsourced and
      // has been failed closed. Nothing to assert until one is sourced.
      expect(
        PORTS_REGISTRY.every((p) => p.walkingTimeMin == null),
      ).toBe(true);
      return;
    }
    const html = render(withWalk.slug);
    expect(html).toContain(String(withWalk.walkingTimeMin));
  });

  it('treats walkingTimeMin === 0 as unknown, not as "too far to walk"', () => {
    // 0 was an undocumented sentinel. Nothing may read meaning into it.
    const zeroed = PORTS_REGISTRY.filter((p) => p.walkingTimeMin === 0);
    for (const port of zeroed) {
      const html = render(port.slug);
      expect(
        html.includes('Walking time unknown') ||
          html.includes('Gehzeit unbekannt'),
      ).toBe(true);
    }
  });
});

describe('PortExplorer — earlier U-1 fixes stay fixed', () => {
  it('never renders a slug-derived UN/LOCODE', () => {
    for (const slug of ALL_SLUGS) {
      const html = render(slug);
      expect(
        html,
        `port "${slug}" renders its slug as a UN/LOCODE`,
      ).not.toContain(`UN/LOCODE: ${slug.toUpperCase()}`);
    }
  });

  it('never claims step-free access', () => {
    for (const slug of ALL_SLUGS) {
      const html = render(slug);
      expect(html).not.toContain('step-free');
      expect(html).not.toContain('stufenlos');
    }
  });

  it('never cites Timonelo as an official source', () => {
    for (const slug of ALL_SLUGS) {
      expect(render(slug)).not.toContain('timonelo.com');
    }
  });
});

describe('CURATED_PORT_STORIES cannot inject unsourced operational facts', () => {
  const OPERATIONAL_FIELDS = [
    'walkingTimeMin',
    'distanceToCenterKm',
    'gangwayDeck',
    'terminalPier',
    'emergencyPhone',
    'policePhone',
    'transitNoteDe',
    'transitNoteEn',
    'airportTransitDe',
    'airportTransitEn',
    'stepFreeAccess',
  ] as const;

  it.each(OPERATIONAL_FIELDS)(
    '%s is null for every port until sourced upstream',
    (field) => {
      for (const port of PORTS_REGISTRY) {
        expect(
          port[field],
          `port "${port.slug}" carries an unsourced ${field}`,
        ).toBeNull();
      }
    },
  );

  it('does not override a null upstream value with a curated one', () => {
    // The shim may narrow an upstream value to null; it may never widen null
    // into a value. Checked against the generated bridge output directly.
    for (const port of PORTS_REGISTRY) {
      const raw = RAW_PORTS.find((r) => r.slug === port.slug);
      if (!raw) continue;
      if (raw.walkingTimeMin == null) expect(port.walkingTimeMin).toBeNull();
      if (raw.gangwayDeckDefault == null) expect(port.gangwayDeck).toBeNull();
      if (raw.stepFreeAccess == null) expect(port.stepFreeAccess).toBeNull();
      if (raw.emergencyPhone == null) expect(port.emergencyPhone).toBeNull();
    }
  });

  it('emits no bullet list of unsourced port essentials', () => {
    for (const port of PORTS_REGISTRY) {
      expect(port.timEssentialsDe).toHaveLength(0);
      expect(port.timEssentialsEn).toHaveLength(0);
    }
  });

  it('keeps descriptive editorial copy', () => {
    // Fail-closed applies to operational facts, not to framing. Deleting the
    // narrative would be over-correction, and the page still needs to read.
    for (const port of PORTS_REGISTRY) {
      expect(port.shortName.length).toBeGreaterThan(0);
      expect(port.headlineEn.length).toBeGreaterThan(0);
      expect(port.storyEn.length).toBeGreaterThan(0);
    }
  });
});

describe('getPortBySlug', () => {
  it('returns undefined for an unknown slug rather than another port', () => {
    expect(getPortBySlug('not-a-real-port')).toBeUndefined();
  });
});
