import { ArrowRight, Waves, Ship } from 'lucide-react';
import { getPlatformPrinciplesSummary } from '../fleet';
import { FleetGallery } from './FleetGallery';
import { PlatformPrinciples } from './PlatformPrinciples';
import { ComingSoonSection } from './ComingSoonSection';

interface FleetLandingProps {
  onSelectVessel: (slug: string) => void;
  onExploreDefaultOcean: () => void;
  onExploreDefaultRiver: () => void;
}

export function FleetLanding({
  onSelectVessel,
  onExploreDefaultOcean,
  onExploreDefaultRiver,
}: FleetLandingProps) {
  const principles = getPlatformPrinciplesSummary();

  const scrollToGallery = () => {
    const el = document.getElementById('fleet-gallery');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="animate-in fade-in duration-300">
      {/* Editorial Hero */}
      <section className="relative ground-navy chart-lines text-white overflow-hidden pt-24 pb-20 md:pt-36 md:pb-28">
        <div className="relative page-shell">
          <div className="max-w-3xl">
            <p className="text-xs font-mono text-gold tracking-wide uppercase mb-6 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-gold" />
              <span>Independent Cruise Intelligence</span>
            </p>

            <h1 className="font-display text-4xl sm:text-6xl md:text-7xl lg:text-8xl leading-[1.0] tracking-tight font-normal text-white">
              Decision intelligence for passenger vessels.
            </h1>

            <p className="text-white/80 text-lg sm:text-xl leading-relaxed mt-6 font-display italic max-w-2xl">
              Understand every deck, cabin, and corridor with certainty before you travel.
            </p>

            <p className="text-white/60 text-sm md:text-base leading-relaxed mt-4 max-w-xl">
              From 330-meter ocean resorts with 19 decks to 80-meter luxury riverboats on the Douro: Timonelo replaces subjective marketing with calm, measured spatial truth.
            </p>

            {/* Quiet Hero Actions */}
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <button
                onClick={scrollToGallery}
                className="px-6 py-3.5 bg-white text-ink font-medium text-xs rounded-xs hover:bg-gold transition-colors inline-flex items-center gap-2 cursor-pointer shadow-xs"
              >
                <span>Explore the Fleet</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              <button
                onClick={onExploreDefaultOcean}
                className="px-5 py-3.5 bg-white/8 text-white hover:bg-white/16 border border-white/15 text-xs rounded-xs transition-colors inline-flex items-center gap-2 cursor-pointer"
              >
                <Ship className="w-3.5 h-3.5 text-amber-200" />
                <span>MSC Bellissima (Ocean)</span>
              </button>

              <button
                onClick={onExploreDefaultRiver}
                className="px-5 py-3.5 bg-white/8 text-white hover:bg-white/16 border border-white/15 text-xs rounded-xs transition-colors inline-flex items-center gap-2 cursor-pointer"
              >
                <Waves className="w-3.5 h-3.5 text-sky-300" />
                <span>MS Andorinha (River)</span>
              </button>
            </div>
          </div>

          {/* 3 Core Trust Pillars */}
          <div className="mt-20 grid md:grid-cols-3 gap-px bg-white/10 border border-white/10">
            {principles.map((item) => (
              <div key={item.title} className="bg-ink/75 backdrop-blur-xs p-6 sm:p-7">
                <div className="font-display text-xl sm:text-2xl text-white font-normal">
                  {item.title}
                </div>
                <div className="text-[13px] text-white/60 mt-2 leading-relaxed font-sans">
                  {item.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Editorial Fleet Gallery */}
      <FleetGallery onSelectVessel={onSelectVessel} />

      {/* Constitutional & Decision-First Principles */}
      <PlatformPrinciples />

      {/* Quiet Future Horizon */}
      <ComingSoonSection />
    </div>
  );
}
