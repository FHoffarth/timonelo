import { ShieldCheck, Compass, Anchor, Scale, Check, ArrowRight } from 'lucide-react';

interface MissionSectionProps {
  onExploreFleet: () => void;
}

export function MissionSection({ onExploreFleet }: MissionSectionProps) {
  return (
    <div className="section-space">
      <div className="page-shell max-w-4xl mx-auto">
        {/* Header */}
        <div className="max-w-2xl mb-14">
          <p className="eyebrow text-gold">Platform Constitution</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            Why Timonelo Exists
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-4 font-display italic">
            "Great software does not maximize interaction. It minimizes future regret."
          </p>
        </div>

        {/* Story Section */}
        <div className="space-y-8 text-[15px] text-ink/85 leading-relaxed bg-white border border-ink/8 p-8 sm:p-12 rounded-xs shadow-xs">
          <p className="first-letter:text-5xl first-letter:font-display first-letter:float-left first-letter:mr-3 first-letter:text-ink font-serif text-lg leading-relaxed">
            Booking a cruise is among the most significant non-refundable vacation investments a traveler makes. Yet travelers are routinely forced to make stateroom choices using flat, promotional marketing diagrams that obscure vertical noise sources, obstructed lifeboat railings, and 300-meter dead-end hallway walks.
          </p>

          <p>
            Timonelo replaces promotional marketing with <strong>spatial certainty</strong>. We do not sell cruises. We do not accept advertising. We do not earn referral commissions. We compile official shipyard blueprints, general arrangement drawings, and verified physical measurements into calm, evidence-based orientation.
          </p>

          <div className="my-10 border-y border-ink/8 py-8">
            <h2 className="font-display text-2xl text-ink font-normal mb-3">
              The Principle of Negative Intelligence (Article VII)
            </h2>
            <p className="text-muted text-[14px] leading-relaxed">
              Traditional travel software measures value by what happens: clicks, views, bookings. Timonelo measures value by what <em>never happens</em> because you had the facts before you traveled:
            </p>
            <ul className="grid sm:grid-cols-2 gap-3 mt-4 text-xs font-mono text-ink/90">
              <li className="flex items-center gap-2 bg-paper/60 p-3 rounded-xs border border-ink/6">
                <Check className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Wrong cabin avoided</span>
              </li>
              <li className="flex items-center gap-2 bg-paper/60 p-3 rounded-xs border border-ink/6">
                <Check className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Obstructed view prevented</span>
              </li>
              <li className="flex items-center gap-2 bg-paper/60 p-3 rounded-xs border border-ink/6">
                <Check className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Noisy vertical galley avoided</span>
              </li>
              <li className="flex items-center gap-2 bg-paper/60 p-3 rounded-xs border border-ink/6">
                <Check className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Cellular roaming shock stopped</span>
              </li>
            </ul>
          </div>

          <h2 className="font-display text-2xl text-ink font-normal">
            Zero Speculation Policy
          </h2>
          <p>
            Timonelo never sounds more certain than its evidence. If an elevator connection is not mapped, we state that it is unknown. If a sightline angle is calculated from deck alignments, we mark its geometric provenance. True trust comes from honest boundaries.
          </p>

          <div className="pt-6 border-t border-ink/8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <span className="text-xs font-mono text-muted">
              Founded 2026 · Ready for Maiden Voyage October 2026
            </span>
            <button
              onClick={onExploreFleet}
              className="px-6 py-3 bg-ink text-white hover:bg-gold hover:text-ink transition-colors text-xs font-medium rounded-xs inline-flex items-center gap-2 cursor-pointer shadow-xs"
            >
              <span>Explore the Fleet</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
