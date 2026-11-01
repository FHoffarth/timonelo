import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { FLEET } from './fleet';
import { FleetProfile } from './FleetDiscovery';
import { ShipPhoto, getShipMedia } from './ShipPhoto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import manifest from '../../public/media/ships/manifest.json';

describe('licensed ship portraits', () => {
  it('has one complete rendition set per catalog ship with exact held hashes', () => {
    expect(manifest.ships.map(m => m.ship).sort()).toEqual(FLEET.map(s => s.slug).sort());
    for (const ship of FLEET) {
      const media = getShipMedia(ship.slug)!;
      expect(media.title.toLowerCase().replace(/[^a-z]/g, '')).toContain(ship.label.toLowerCase().replace(/[^a-z]/g, ''));
      expect(media.source_revision).toBeGreaterThan(0);
      for (const v of media.variants) {
        const bytes = readFileSync(resolve(process.cwd(), 'public', v.src.slice(1)));
        expect(bytes.length).toBe(v.bytes);
        expect(createHash('sha256').update(bytes).digest('hex')).toBe(v.sha256);
        expect(bytes.toString('ascii', 8, 12)).toBe('WEBP');
      }
      const html = renderToStaticMarkup(<ShipPhoto slug={ship.slug} label={ship.label} />);
      expect(html).toContain(media.author);
      expect(html).toContain(media.changes);
      expect(html).toContain(media.rendition_license);
      expect(html).toContain(`oldid=${media.source_revision}`);
    }
  });
  it('keeps each of nine ship photographs and its credits bound to that vessel', () => {
    for (const ship of FLEET) {
      const media = getShipMedia(ship.slug);
      expect(media?.ship).toBe(ship.slug);
      const html = renderToStaticMarkup(<ShipPhoto slug={ship.slug} label={ship.label} />);
      expect(html).toContain(`/media/ships/${ship.slug}-`);
      expect(html).toContain('srcSet=');
      expect(html).toContain(media!.license_url);
      expect(html).toContain('commons.wikimedia.org');
      expect(html).toContain('Photo credit');
    }
    expect(getShipMedia('another-ship')).toBeUndefined();
    expect(renderToStaticMarkup(<ShipPhoto slug="another-ship" label="Unknown ship" />)).not.toContain('<img');
  });
  it('does not turn a missing publication snapshot or a review candidate into ship facts', () => {
    for (const slug of ['msc-bellissima', 'msc-euribia']) {
      const ship = FLEET.find(s => s.slug === slug)!;
      const html = renderToStaticMarkup(<FleetProfile ship={ship} profile={undefined} onNavigate={() => {}} />);
      expect(html).toContain('Human review pending');
      expect(html).toContain('Publication data unavailable');
      expect(html).toContain('No published identity information available');
      expect(html).not.toMatch(/2217|2419|2,217|2,419|SUPPORTED|PUBLISH_ALLOWED|5654|6334/);
      expect(html).toContain('Photo credit');
      if (slug === 'msc-euribia') expect(html).not.toMatch(/Posidonia|Le Cerisier|Lighthouse|14122/);
    }
  });
});
