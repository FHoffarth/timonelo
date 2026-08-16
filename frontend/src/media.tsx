/**
 * Photography system (Plane 5 presentation): authentic maritime visual assets
 * with automatic fallback resolution and graceful placeholders.
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

  return (id: string, isRiver: boolean = false): string | null => {
    if (manifest[id]) return manifest[id];

    // Fallbacks
    if (id.startsWith('view:')) {
      return isRiver
        ? manifest['default:river_view'] ?? '/media/douro-river-view.jpg'
        : manifest['default:ocean_view'] ?? '/media/balcony-ocean-view.jpg';
    }
    if (id.startsWith('cabin:')) {
      return manifest['default:stateroom'] ?? '/media/stateroom-interior.jpg';
    }
    if (id.startsWith('ship:')) {
      const slug = id.replace('ship:', '').toLowerCase();
      if (manifest[id]) return manifest[id];
      if (manifest[`ship:${slug}`]) return manifest[`ship:${slug}`];
      return isRiver ? '/media/ms-andorinha-hero.jpg' : '/media/msc-bellissima-hero.jpg';
    }

    return null;
  };
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
      aria-label={label ? `${label} — archival illustration` : 'Shipyard illustration'}
      className={`media-placeholder relative w-full overflow-hidden grid place-items-center rounded-xs ${className}`}
    >
      <div className="flex flex-col items-center gap-2 text-white/70">
        <Icon className="w-6 h-6" aria-hidden strokeWidth={1.4} />
        {label && <span className="text-[10px] uppercase tracking-[0.22em] text-white/55">{label}</span>}
      </div>
    </div>
  );
}
