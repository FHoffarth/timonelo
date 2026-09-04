/**
 * BC-1 — the landing page may not assert quantities the repository cannot support.
 *
 * "50,000+ verified passenger reports" appeared nowhere in this repository except
 * the sentence that claimed it. "340+ cruise ports worldwide" was asserted while
 * six ports were reachable. Neither was replaced with a smaller invented number;
 * both became qualitative copy.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const homePage = readFileSync(resolve(here, 'HomePage.tsx'), 'utf8');

describe('BC-1: landing claims are supported', () => {
  it('does not claim a passenger-report corpus that does not exist', () => {
    expect(homePage).not.toMatch(/50,?000/);
    expect(homePage).not.toMatch(/verified passenger reports/i);
  });

  it('does not claim a port count the product does not serve', () => {
    expect(homePage).not.toMatch(/340\s*\+/);
    expect(homePage).not.toMatch(/\d{3,}\s*\+?\s*cruise ports/i);
  });

  it('did not substitute a different unsupported number', () => {
    // Any "N+ <noun>" superlative in the pillar copy would be the same defect
    // wearing a smaller number.
    const pillars = homePage.slice(homePage.indexOf('Ship Intelligence'));
    expect(pillars).not.toMatch(/\d[\d,]*\s*\+/);
  });
});
