import { knowledgeRepository } from "../../knowledge";

const bellissimaName = knowledgeRepository.getShip("msc-bellissima").vessel_name;

interface LivingBottomBarProps {
  activeDeck: number;
  deckName: string;
  selectedCabin: LivingCabin | null;
  onOpenEvidence: () => void;
}

export default function LivingBottomBar({
  activeDeck,
  deckName,
  selectedCabin,
  onOpenEvidence,
}: LivingBottomBarProps) {
  return (
    <div className="absolute bottom-4 inset-x-6 z-20 pointer-events-auto flex items-center justify-between px-5 py-2.5 bg-slate-900/85 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl text-xs text-slate-300 select-none">
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-bold text-white tracking-wide uppercase text-[11px]">
            LIVING DECK PLAN
          </span>
          <span className="text-slate-500 font-mono">{bellissimaName}</span>
        </div>

        <div className="h-4 w-px bg-white/10" />

        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-slate-500">DECK:</span>
          <span className="text-sky-400 font-bold">{activeDeck}</span>
          <span className="text-slate-400">({deckName})</span>
        </div>

        <div className="h-4 w-px bg-white/10 hidden md:block" />

        <div className="items-center gap-2 font-mono text-[11px] hidden md:flex">
          <span className="text-slate-500">SOURCE:</span>
          <span className="text-slate-200 font-semibold">
            Official MSC Deck Plan 11.2025 (Native Vectors)
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {selectedCabin && (
          <button
            onClick={onOpenEvidence}
            className="px-3 py-1 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-400/30 font-semibold text-[11px] flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
            Ground Truth (0.99)
          </button>
        )}

        <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px]">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>60 FPS</span>
        </div>
      </div>
    </div>
  );
}
