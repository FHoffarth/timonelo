import { parseFleetProjection, type FleetProjection } from './fleet';
import policy from './publicationPolicy.json';

interface SnapshotEnvelope {
  schema: string; generated_at: string; expires_at: string;
  blocked: boolean; payload: string; revision: string;
}
export interface VerifiedSnapshot {
  data: FleetProjection; blocked: boolean; generated: number; expires: number; revision: string;
}
export function revisionInput(s: Omit<SnapshotEnvelope, 'revision'>): string {
  return [s.schema, s.generated_at, s.expires_at, s.blocked ? 'blocked' : 'active', s.payload].join('\n');
}
const timestamp = (v: unknown): v is string => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(v);

// Transport integrity and freshness only; no Evidence/Review/Admission policy here.
export async function verifySnapshot(raw: unknown, now = Date.now()): Promise<VerifiedSnapshot> {
  if (!raw || typeof raw !== 'object') throw new Error('Snapshot missing');
  const s = raw as Partial<SnapshotEnvelope>;
  if (s.schema !== 'timonelo.fleet.snapshot.v1' || !timestamp(s.generated_at) || !timestamp(s.expires_at) ||
      typeof s.blocked !== 'boolean' || typeof s.payload !== 'string' ||
      typeof s.revision !== 'string' || !/^[a-f0-9]{64}$/.test(s.revision)) throw new Error('Snapshot contract invalid');
  const generated = Date.parse(s.generated_at), expires = Date.parse(s.expires_at);
  if (!Number.isFinite(generated) || !Number.isFinite(expires) || generated > now || expires <= now ||
      expires <= generated || expires - generated > policy.max_age_seconds * 1000 ||
      new Date(generated).toISOString() !== s.generated_at || new Date(expires).toISOString() !== s.expires_at) throw new Error('Snapshot expired or invalid time');
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(revisionInput(s as SnapshotEnvelope)));
  const revision = Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  if (revision !== s.revision) throw new Error('Snapshot integrity mismatch');
  const data = parseFleetProjection(JSON.parse(s.payload));
  if (!data) throw new Error('Projection invalid');
  if (s.blocked && Object.values(data.ships).some(p => p.facts.length || p.sources.length || p.level)) throw new Error('Blocked snapshot carries facts');
  return { data, blocked: s.blocked, generated, expires, revision };
}

export interface SnapshotClientOptions {
  load: (signal: AbortSignal) => Promise<unknown>;
  onChange: (value: FleetProjection | null) => void;
  now?: () => number;
  monotonic?: () => number;
  stateStore?: { read: () => string | null; write: (value: string) => void };
}

/** A bounded fetch lifecycle, not a publication authority. */
export function createSnapshotClient({ load, onChange, now = Date.now, monotonic = () => performance.now(), stateStore }: SnapshotClientOptions) {
  let stopped = false, paused = false, sequence = 0;
  let highestGenerated = -Infinity, highestRevision = '';
  let highestBlocked = false;
  let highestDeadline = -Infinity;
  let expiryTimer: ReturnType<typeof setTimeout> | undefined;
  let requestTimer: ReturnType<typeof setTimeout> | undefined;
  let active: AbortController | undefined;
  let expires = -Infinity, deadline = -Infinity;
  const clearDisplay = () => { clearTimeout(expiryTimer); expires = deadline = -Infinity; onChange(null); };
  const checkExpiry = () => { if (!stopped && !paused && (now() >= expires || monotonic() >= deadline)) clearDisplay(); };
  const invalidate = () => { sequence++; active?.abort(); clearTimeout(requestTimer); clearDisplay(); };
  const refresh = async () => {
    if (stopped || paused) return;
    checkExpiry();
    const request = ++sequence;
    active?.abort(); clearTimeout(requestTimer);
    const controller = new AbortController(); active = controller;
    const timeout = new Promise<never>((_, reject) => {
      requestTimer = setTimeout(() => { controller.abort(); reject(new Error('Snapshot refresh timed out')); }, policy.request_timeout_seconds * 1000);
    });
    try {
      const next = await Promise.race([load(controller.signal).then(raw => verifySnapshot(raw, now())), timeout]);
      if (stopped || paused || request !== sequence) return;
      const stored = stateStore?.read();
      if (stored !== null && stored !== undefined) {
        const mark: unknown = JSON.parse(stored);
        if (!mark || typeof mark !== 'object' || !('generated' in mark) || !Number.isSafeInteger(mark.generated) ||
            !('revision' in mark) || typeof mark.revision !== 'string' || !/^[a-f0-9]{64}$/.test(mark.revision) ||
            !('blocked' in mark) || typeof mark.blocked !== 'boolean') throw new Error('Snapshot watermark invalid');
        const generated = Number(mark.generated);
        if (generated > highestGenerated || (generated === highestGenerated && mark.blocked && !highestBlocked)) {
          highestGenerated = generated; highestRevision = mark.revision; highestBlocked = mark.blocked;
        }
      }
      if (now() < next.generated || now() >= next.expires || next.generated < highestGenerated ||
          (next.generated === highestGenerated && highestRevision && next.revision !== highestRevision && !next.blocked)) throw new Error('Stale snapshot revision');
      if (next.revision !== highestRevision || !Number.isFinite(highestDeadline)) highestDeadline = monotonic() + (next.expires - now());
      highestGenerated = next.generated; highestRevision = next.revision; highestBlocked = next.blocked;
      // Metadata only: never cache publication payloads. A storage failure refuses display.
      stateStore?.write(JSON.stringify({ generated: highestGenerated, revision: highestRevision, blocked: highestBlocked }));
      if (next.blocked) { clearDisplay(); return; }
      if (monotonic() >= highestDeadline) throw new Error('Snapshot exceeded monotonic lifetime');
      clearTimeout(expiryTimer);
      expires = next.expires;
      deadline = highestDeadline;
      expiryTimer = setTimeout(clearDisplay, Math.max(0, Math.min(expires - now(), deadline - monotonic())));
      onChange(next.data);
    } catch {
      if (!stopped && request === sequence) clearDisplay();
    } finally {
      if (request === sequence) clearTimeout(requestTimer);
    }
  };
  const interval = setInterval(() => { void refresh(); }, policy.refresh_interval_seconds * 1000);
  // Check wall-clock jumps as well as the monotonic expiry timer.
  const clockCheck = setInterval(checkExpiry, 1000);
  return {
    refresh,
    checkExpiry,
    suspend() { paused = true; invalidate(); },
    resume() { if (!stopped) { paused = false; clearDisplay(); void refresh(); } },
    stop() { stopped = true; sequence++; active?.abort(); clearTimeout(requestTimer); clearTimeout(expiryTimer); clearInterval(interval); clearInterval(clockCheck); },
  };
}
