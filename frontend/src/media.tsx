/**
 * Photography system (Plane 5 presentation): reserved image locations for every
 * spatial entity, with elegant placeholders when an image is missing. Availability
 * is driven by a manifest (public/media/manifest.json); when an asset is not
 * listed, a placeholder renders directly — no <img> request, so there are never
 * broken images or 404s. Entity-keyed, so any future ship works unchanged.
 */
import { useEffect, useState, type CSSProperties } from 'react';
import { Ship, Layers, DoorClosed, Waves, Map as MapIcon } from 'lucide-react';

export type MediaKind = 'ship' | 'deck' | 'cabin' | 'view' | 'plan';
type Manifest = Record<string, string>;

let cache: Manifest | null = null;
let inflight: Promise<Manifest> | null = null;
function loadManifest(): Promise<Manifest> {
  if (cache) return Promise.resolve(cache);
  if (!inflight) {
    inflight = fetch('/media/manifest.json')
      .then((r) => (r.ok ? r.json() : {}))
      .catch(() => ({}))
      .then((m: Manifest) => (cache = m ?? {}));
  }
  return inflight;
}

export function useMedia() {
  const [manifest, setManifest] = useState<Manifest>(cache ?? {});
  useEffect(() => {
    let alive = true;
    loadManifest().then((m) => alive && setManifest(m));
    return () => {
      alive = false;
    };
  }, []);
  return (id: string): string | null => manifest[id] ?? null;
}

const ICON: Record<MediaKind, typeof Ship> = {
  ship: Ship,
  deck: Layers,
  cabin: DoorClosed,
  view: Waves,
  plan: MapIcon,
};

export function Photo({
  src,
  kind,
  label,
  ratio = '16 / 9',
  priority = false,
  className = '',
}: {
  src: string | null;
  kind: MediaKind;
  label?: string;
  ratio?: string;
  priority?: boolean;
  className?: string;
}) {
  const style: CSSProperties = { aspectRatio: ratio };
  if (src) {
    return (
      <img
        src={src}
        alt={label ?? ''}
        style={style}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        className={`w-full object-cover rounded-xs ${className}`}
      />
    );
  }
  const Icon = ICON[kind];
  return (
    <div
      style={style}
      role="img"
      aria-label={label ? `${label} — photography coming soon` : 'Photography coming soon'}
      className={`media-placeholder relative w-full overflow-hidden grid place-items-center rounded-xs ${className}`}
    >
      <div className="flex flex-col items-center gap-2 text-white/70">
        <Icon className="w-6 h-6" aria-hidden strokeWidth={1.4} />
        {label && <span className="text-[10px] uppercase tracking-[0.22em] text-white/55">{label}</span>}
      </div>
    </div>
  );
}
