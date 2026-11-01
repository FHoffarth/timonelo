import { describe, it, expect, vi, afterEach } from 'vitest';
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { FLEET } from './fleet';
import { verifySnapshot, revisionInput, createSnapshotClient } from './publicationSnapshot';
import type { FleetProjection } from './fleet';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';
import { FleetProfile } from './FleetDiscovery';

const now = Date.parse('2026-11-01T10:00:00.000Z');
export async function fixture(blocked = false) {
  const payload = JSON.stringify({ schema: 'timonelo.fleet.v1', as_of: '2026-11-01', ships: Object.fromEntries(FLEET.map(s => [s.slug, { level: 0, candidate_count: 0, facts: [], sources: [] }])) });
  const snapshot = { schema: 'timonelo.fleet.snapshot.v1', generated_at: '2026-11-01T10:00:00.000Z', expires_at: '2026-11-01T10:10:00.000Z', blocked, payload, revision: '' };
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(revisionInput(snapshot)));
  snapshot.revision = Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  return snapshot;
}
async function revise(snapshot: Awaited<ReturnType<typeof fixture>>, generated: number, value?: string) {
  const data: FleetProjection = JSON.parse(snapshot.payload);
  if (value) {
    // Synthetic transport only, never written to canonical data or used in production.
    data.ships['msc-bellissima'] = { level: 1, candidate_count: 1,
      sources: [{ artifact_id: 'ART-TEST', filename: 'transport-test.pdf', sha256: 'a'.repeat(64) }],
      facts: [{ statement_id: 'STM-TEST', entity_id: 'vessel:MSC-BELLISSIMA', question_id: 'Q-TEST', statement_type: 'vessel.test',
        section: 'identity', value, artifact_id: 'ART-TEST', page: 1, locator: 'Synthetic source locator', publish_status: 'PUBLISH_ALLOWED' }] };
  }
  const next = { ...snapshot, generated_at: new Date(generated).toISOString(), expires_at: new Date(generated + 600_000).toISOString(), payload: JSON.stringify(data) };
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(revisionInput(next)));
  next.revision = Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  return next;
}

describe('publication snapshot transport', () => {
  it('accepts an intact fresh snapshot and recognizes the explicit block', async () => {
    expect((await verifySnapshot(await fixture(), now)).data.schema).toBe('timonelo.fleet.v1');
    expect((await verifySnapshot(await fixture(true), now)).blocked).toBe(true);
  });
  it('rejects expiry, future generation, tampering and malformed input', async () => {
    const s = await fixture();
    await expect(verifySnapshot(s, now + 600_000)).rejects.toThrow();
    await expect(verifySnapshot(s, now - 1)).rejects.toThrow();
    await expect(verifySnapshot({ ...s, payload: s.payload + ' ' }, now)).rejects.toThrow();
    await expect(verifySnapshot({ ...s, expires_at: '2026-11-01T11:00:00.000Z' }, now)).rejects.toThrow();
    await expect(verifySnapshot({ ...s, expires_at: '2026-11-01T10:09:00.000Z' }, now)).rejects.toThrow(/integrity/);
    await expect(verifySnapshot(null, now)).rejects.toThrow();
  });
  it('verifies the actual Python envelope encoding, including Unicode', async () => {
    const data = JSON.parse((await fixture()).payload);
    data.test_unicode = '東京';
    const raw = execFileSync('python', ['-B', '-c',
      "import sys,json;sys.path.insert(0,'src');from datetime import datetime,timezone;from timonelo.evidence.publication_snapshot import make_snapshot;print(json.dumps(make_snapshot(json.load(sys.stdin),now=datetime(2026,11,1,10,0,tzinfo=timezone.utc)),ensure_ascii=False))"],
      { cwd: resolve(process.cwd(), '..'), input: JSON.stringify(data), encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
    expect((await verifySnapshot(JSON.parse(raw), now)).data.ships['msc-bellissima'].level).toBe(0);
  });
});

describe('snapshot refresh lifecycle', () => {
  afterEach(() => { vi.useRealTimers(); });
  it('retains the observed revocation across client disposal and recreation', async () => {
    const good = await fixture(), blocked = await fixture(true);
    let saved: string | null = null;
    const stateStore = { read: () => saved, write: (value: string) => { saved = value; } };
    let displayed: FleetProjection | null = null;
    const first = createSnapshotClient({ now: () => now, stateStore, load: async () => blocked, onChange: v => { displayed = v; } });
    await first.refresh(); first.stop();
    const second = createSnapshotClient({ now: () => now, stateStore, load: async () => good, onChange: v => { displayed = v; } });
    try { await second.refresh(); expect(displayed).toBeNull(); }
    finally { second.stop(); }
  });
  it('replaces profile facts and source traces, clears on revocation, and admits only a newer recovery', async () => {
    let wall = now;
    const a = await revise(await fixture(), now, 'TEST FIRST VALUE');
    const b = await revise(await fixture(), now + 1000, 'TEST REPLACEMENT VALUE');
    const blocked = await revise(await fixture(true), now + 2000);
    const recovered = await revise(await fixture(), now + 3000, 'TEST RECOVERY VALUE');
    let response = a; let html = '';
    const client = createSnapshotClient({ now: () => wall, load: async () => response,
      onChange: data => { html = renderToStaticMarkup(createElement(FleetProfile, { ship: FLEET[0], profile: data?.ships[FLEET[0].slug], onNavigate: () => {} })); } });
    try {
      await client.refresh(); expect(html).toContain('TEST FIRST VALUE'); expect(html).toContain('ART-TEST');
      wall += 1000; response = b; await client.refresh(); expect(html).toContain('TEST REPLACEMENT VALUE'); expect(html).not.toContain('TEST FIRST VALUE');
      wall += 1000; response = blocked; await client.refresh(); expect(html).not.toContain('TEST REPLACEMENT VALUE'); expect(html).not.toContain('ART-TEST');
      expect(html).toContain('Publication data unavailable');
      response = b; await client.refresh(); expect(html).not.toContain('TEST REPLACEMENT VALUE');
      wall += 1000; response = recovered; await client.refresh(); expect(html).toContain('TEST RECOVERY VALUE');
    } finally { client.stop(); }
  });
  it('fails closed for corrupt or unavailable persisted state', async () => {
    for (const stateStore of [
      { read: () => '{bad JSON', write: () => {} },
      { read: () => null, write: () => { throw new Error('Storage unavailable'); } },
      { read: () => JSON.stringify({ generated: now }), write: () => {} },
    ]) {
      let displayed: FleetProjection | null = null;
      const good = await fixture();
      const client = createSnapshotClient({ now: () => now, stateStore, load: async () => good, onChange: v => { displayed = v; } });
      try { await client.refresh(); expect(displayed).toBeNull(); } finally { client.stop(); }
    }
  });
  it('clears on refresh error, explicit block and replay of a pre-block revision', async () => {
    const good = await fixture(), blocked = await fixture(true);
    let response: unknown = good;
    let fail = false;
    let displayed: FleetProjection | null = null;
    const client = createSnapshotClient({ now: () => now, load: async () => { if (fail) throw new Error('offline'); return response; }, onChange: v => { displayed = v; } });
    try {
      await client.refresh(); expect(displayed).not.toBeNull();
      fail = true; await client.refresh(); expect(displayed).toBeNull();
      fail = false; await client.refresh(); expect(displayed).not.toBeNull();
      response = blocked; await client.refresh(); expect(displayed).toBeNull();
      response = good; await client.refresh(); expect(displayed).toBeNull();
    } finally { client.stop(); }
  });
  it('expires against wall and monotonic clocks without extending the same revision', async () => {
    const good = await fixture();
    let wall = now, mono = 0;
    let displayed: FleetProjection | null = null;
    const client = createSnapshotClient({ now: () => wall, monotonic: () => mono, load: async () => good, onChange: v => { displayed = v; } });
    try {
      await client.refresh(); expect(displayed).not.toBeNull();
      wall += 300_000; mono += 300_000; await client.refresh(); expect(displayed).not.toBeNull();
      wall = now + 1000; mono = 600_000; client.checkExpiry(); expect(displayed).toBeNull();
      await client.refresh(); expect(displayed).toBeNull();
    } finally { client.stop(); }
  });
  it('clears at the deadline and times out a stalled refresh', async () => {
    const good = await fixture();
    vi.useFakeTimers(); vi.setSystemTime(now);
    let displayed: FleetProjection | null = null;
    let stall = false;
    const client = createSnapshotClient({ monotonic: () => Date.now() - now,
      load: async () => stall ? new Promise(() => {}) : good, onChange: v => { displayed = v; } });
    try {
      await client.refresh(); expect(displayed).not.toBeNull();
      stall = true; const request = client.refresh();
      await vi.advanceTimersByTimeAsync(5000); await request; expect(displayed).toBeNull();
      stall = false; await client.refresh(); expect(displayed).not.toBeNull();
      vi.setSystemTime(now + 600_000); client.checkExpiry(); expect(displayed).toBeNull();
    } finally { client.stop(); }
  });
  it('suppresses late responses across hidden/offline state and disposal', async () => {
    const good = await fixture();
    let finish: (value: unknown) => void = () => {};
    const change = vi.fn();
    const client = createSnapshotClient({ now: () => now, load: () => new Promise(resolve => { finish = resolve; }), onChange: change });
    const request = client.refresh();
    client.suspend(); finish(good); await request;
    expect(change.mock.calls.every(([v]) => v === null)).toBe(true);
    client.stop(); const calls = change.mock.calls.length;
    await client.refresh(); expect(change).toHaveBeenCalledTimes(calls);
  });
  it('polls on the declared interval and stops polling while suspended', async () => {
    vi.useFakeTimers(); vi.setSystemTime(now);
    const load = vi.fn(async () => { throw new Error('test outage'); });
    const client = createSnapshotClient({ load, onChange: () => {} });
    try {
      await vi.advanceTimersByTimeAsync(30_000); expect(load).toHaveBeenCalledTimes(1);
      client.suspend(); await vi.advanceTimersByTimeAsync(60_000); expect(load).toHaveBeenCalledTimes(1);
      client.resume(); expect(load).toHaveBeenCalledTimes(2);
    } finally { client.stop(); }
  });
});
