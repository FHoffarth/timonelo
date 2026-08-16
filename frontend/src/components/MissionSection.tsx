import { ArrowRight } from 'lucide-react';
import { useI18n } from '../i18n';

interface MissionSectionProps {
  onExploreFleet: () => void;
}

export function MissionSection({ onExploreFleet }: MissionSectionProps) {
  const { t } = useI18n();

  return (
    <div className="section-space">
      <div className="page-shell max-w-4xl mx-auto">
        {/* Header */}
        <div className="max-w-2xl mb-14">
          <p className="eyebrow text-gold">{t.mission.badge}</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            {t.mission.title}
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-4 font-display italic">
            "{t.mission.subtitle}"
          </p>
          <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xs text-xs text-slate-800 font-serif italic">
            {t.mission.officerObservation}
          </div>
        </div>

        {/* 4 Constitutional Articles */}
        <div className="space-y-6 bg-white border border-ink/8 p-8 sm:p-12 rounded-xs shadow-xs">
          <div className="border-b border-ink/8 pb-6 space-y-2">
            <h2 className="font-display text-2xl text-ink font-normal">{t.mission.article1Title}</h2>
            <p className="text-[14px] text-muted leading-relaxed font-light">{t.mission.article1Desc}</p>
          </div>

          <div className="border-b border-ink/8 pb-6 space-y-2">
            <h2 className="font-display text-2xl text-ink font-normal">{t.mission.article2Title}</h2>
            <p className="text-[14px] text-muted leading-relaxed font-light">{t.mission.article2Desc}</p>
          </div>

          <div className="border-b border-ink/8 pb-6 space-y-2">
            <h2 className="font-display text-2xl text-ink font-normal">{t.mission.article3Title}</h2>
            <p className="text-[14px] text-muted leading-relaxed font-light">{t.mission.article3Desc}</p>
          </div>

          <div className="pt-2 space-y-2">
            <h2 className="font-display text-2xl text-ink font-normal">{t.mission.article4Title}</h2>
            <p className="text-[14px] text-muted leading-relaxed font-light">{t.mission.article4Desc}</p>
          </div>

          <div className="pt-8 border-t border-ink/8 text-center sm:text-left">
            <button
              onClick={onExploreFleet}
              className="inline-flex items-center gap-2 px-6 py-3 bg-ink text-white text-xs font-medium hover:bg-gold transition-colors rounded-xs cursor-pointer shadow-xs"
            >
              <span>{t.common.stepAboard}</span>
              <ArrowRight className="w-4 h-4 text-gold" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
