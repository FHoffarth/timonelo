import { ArrowRight, Check } from 'lucide-react';
import { FLEET_REGISTRY, type FleetVessel } from '../fleet';

interface FleetGalleryProps {
  onSelectVessel: (slug: string) => void;
}

export function FleetGallery({ onSelectVessel }: FleetGalleryProps) {
  const bellissima = FLEET_REGISTRY.find((v) => v.slug === 'msc-bellissima')!;
  const andorinha = FLEET_REGISTRY.find((v) => v.slug === 'ms-andorinha')!;
  const grandiosa = FLEET_REGISTRY.find((v) => v.slug === 'msc-grandiosa')!;
  const meraviglia = FLEET_REGISTRY.find((v) => v.slug === 'msc-meraviglia')!;

  return (
    <section id="fleet-gallery" className="section-space">
      <div className="page-shell">
        <div className="max-w-2xl mb-16">
          <p className="eyebrow text-muted/70 tracking-widest uppercase">The Fleet</p>
          <h2 className="section-title text-4xl sm:text-5xl md:text-6xl mt-2 font-normal">
            Four ships. Two distinct worlds.
          </h2>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-4">
            From 19-deck Mediterranean flagships to intimate 84-guest Douro river yachts. Every space mapped directly from authentic shipyard drawings.
          </p>
        </div>

        {/* Group 1: Reference Vessels */}
        <div className="mb-14">
          <div className="text-xs font-mono uppercase tracking-widest text-muted/70 mb-6 pb-2 border-b border-ink/6 flex items-center justify-between">
            <span>Reference Platforms</span>
            <span>Ocean & River</span>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            <EditorialCoverCard vessel={bellissima} onSelect={() => onSelectVessel(bellissima.slug)} />
            <EditorialCoverCard vessel={andorinha} onSelect={() => onSelectVessel(andorinha.slug)} />
          </div>
        </div>

        {/* Group 2: The Meraviglia Family Evolution */}
        <div className="mt-16">
          <div className="text-xs font-mono uppercase tracking-widest text-muted/70 mb-6 pb-2 border-b border-ink/6 flex items-center justify-between">
            <span>Meraviglia Family Evolution</span>
            <span>Original Class Prototype & Plus Subclass</span>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            <EditorialCoverCard vessel={meraviglia} onSelect={() => onSelectVessel(meraviglia.slug)} />
            <EditorialCoverCard vessel={grandiosa} onSelect={() => onSelectVessel(grandiosa.slug)} />
          </div>
        </div>
      </div>
    </section>
  );
}

function EditorialCoverCard({
  vessel,
  onSelect,
}: {
  vessel: FleetVessel;
  onSelect: () => void;
}) {
  return (
    <article className="group bg-white border border-ink/8 hover:border-ink/20 transition-all duration-500 flex flex-col justify-between overflow-hidden rounded-xs shadow-xs hover:shadow-md">
      <div>
        {/* Cover Photo */}
        <div className="relative aspect-[16/10] overflow-hidden bg-ink/5">
          <img
            src={vessel.heroImageUrl}
            alt={vessel.name}
            loading="eager"
            decoding="async"
            className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-[1.02]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/15 to-transparent opacity-80" />
          
          <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-white text-[11px] font-mono">
            <span className="bg-ink/60 backdrop-blur-md px-2.5 py-1 rounded-xs border border-white/10 uppercase tracking-wider text-gold">
              {vessel.roleTitle}
            </span>
            <span className="bg-white/15 backdrop-blur-md px-2 py-0.5 rounded-xs inline-flex items-center gap-1">
              <Check className="w-3 h-3 text-emerald-300" /> {vessel.statusLabel}
            </span>
          </div>

          <div className="absolute bottom-4 left-4 right-4 text-white">
            <p className="text-xs font-mono uppercase tracking-widest text-white/70">
              {vessel.operator} · {vessel.shipClass}
            </p>
            <h3 className="font-display text-3xl sm:text-4xl text-white font-normal leading-tight mt-0.5">
              {vessel.name}
            </h3>
          </div>
        </div>

        {/* Story & Details */}
        <div className="p-6 sm:p-7">
          <p className="font-display text-lg text-ink/85 italic leading-snug mb-3">
            "{vessel.tagline}"
          </p>

          <p className="text-[13px] text-muted leading-relaxed mb-6">
            {vessel.description}
          </p>

          {/* Minimal Clean Stats */}
          <div className="grid grid-cols-4 gap-2 bg-paper/60 p-3 rounded-xs border border-ink/6 text-center mb-5">
            <div>
              <span className="text-[10px] text-muted/70 uppercase block font-sans">Decks</span>
              <span className="font-display text-lg text-ink mt-0.5 block leading-none">{vessel.totalDecks}</span>
            </div>
            <div>
              <span className="text-[10px] text-muted/70 uppercase block font-sans">Cabins</span>
              <span className="font-display text-lg text-ink mt-0.5 block leading-none">{vessel.cabinCount}</span>
            </div>
            <div>
              <span className="text-[10px] text-muted/70 uppercase block font-sans">Length</span>
              <span className="font-display text-lg text-ink mt-0.5 block leading-none">{vessel.lengthM}m</span>
            </div>
            <div>
              <span className="text-[10px] text-muted/70 uppercase block font-sans">Guests</span>
              <span className="font-display text-lg text-ink mt-0.5 block leading-none">{vessel.passengerCapacity}</span>
            </div>
          </div>

          {/* Key Spaces */}
          <div>
            <div className="flex flex-wrap gap-1.5">
              {vessel.highlights.map((h) => (
                <span
                  key={h}
                  className="text-[11px] bg-paper text-ink/75 px-2.5 py-0.5 rounded-xs border border-ink/6 font-medium"
                >
                  {h}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-6 sm:p-7 pt-0 border-t border-ink/6 flex items-center justify-between gap-4 mt-auto">
        <span className="text-[11px] text-muted font-mono">
          {vessel.region}
        </span>

        <button
          onClick={onSelect}
          className="px-5 py-2.5 bg-ink text-white hover:bg-gold hover:text-ink transition-colors text-xs font-medium rounded-xs inline-flex items-center gap-2 cursor-pointer shadow-xs"
        >
          <span>Explore Ship</span>
          <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
        </button>
      </div>
    </article>
  );
}
