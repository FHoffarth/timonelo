import { useState } from 'react';
import manifest from '../../public/media/ships/manifest.json';

export const getShipMedia = (slug: string) => manifest.ships.find(m => m.ship === slug && m.publication_status === 'LICENSE_DOCUMENTED');

/** Media provenance is separate from canonical statement/publication authority. */
export function ShipPhoto({ slug, label, priority = false, compact = false }: { slug: string; label: string; priority?: boolean; compact?: boolean }) {
  const media = getShipMedia(slug);
  const [failed, setFailed] = useState(false);
  if (!media || failed) return <div className="bg-[#E8ECEE] p-8 text-sm text-[#5B6570] rounded-xl">Photograph unavailable for {label}. No substitute ship is shown.</div>;
  const largest = media.variants.at(-1)!;
  return <figure className="min-w-0">
    <div className={`overflow-hidden bg-[#E8ECEE] ${compact ? 'aspect-[16/10]' : 'rounded-2xl'}`}>
      <img src={largest.src} srcSet={media.variants.map(v => `${v.src} ${v.width}w`).join(', ')}
        sizes={compact ? '(min-width: 1024px) 360px, (min-width: 640px) 50vw, 100vw' : '(min-width: 1152px) 1104px, 100vw'}
        width={largest.width} height={largest.height} alt={`${label} — ${slug === 'msc-euribia' ? 'cropped superstructure detail' : 'historical ship photograph'}`}
        loading={priority ? 'eager' : 'lazy'} decoding="async" onError={() => setFailed(true)}
        className={compact ? 'h-full w-full object-contain' : 'w-full h-auto max-h-[500px] object-contain'} />
    </div>
    <figcaption className={`text-xs leading-relaxed text-[#5B6570] break-words ${compact ? 'px-5 pt-3' : 'pt-3'}`}>
      Photo credit: <a className="underline underline-offset-2" href={media.source_page} target="_blank" rel="noreferrer">{media.author} / Wikimedia Commons</a>
      {' · '}<a className="underline underline-offset-2" href={media.license_url} target="_blank" rel="noreferrer">{media.license}</a>
      <details><summary className="cursor-pointer py-2">Image source & changes</summary>
        <p>{media.title} · file version {media.file_timestamp.slice(0, 10)} · retrieved {media.retrieved_at.slice(0, 10)}.</p>
        <p>{media.changes} Rendition license: {media.rendition_license}.</p>
        <a className="underline" href={`${media.source_page}?oldid=${media.source_revision}`} target="_blank" rel="noreferrer">Recorded source-page revision</a>
        <p>{media.limitations}</p>
      </details>
    </figcaption>
  </figure>;
}
