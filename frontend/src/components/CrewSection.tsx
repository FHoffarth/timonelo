import { useState } from 'react';
import {
  Lock,
  Anchor,
  Check,
  Award,
  HeartHandshake,
} from 'lucide-react';
import { useI18n } from '../i18n';

export function CrewSection() {
  const { t } = useI18n();
  const [accessCode, setAccessCode] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    if (accessCode.trim().toUpperCase() === 'BELLISSIMA-2026' || accessCode.trim().toUpperCase() === 'OCTOBER-2026') {
      setIsVerified(true);
      setFeedbackMsg('Invitation accepted. Welcome to the Maritime Contributor Circle.');
    } else {
      setFeedbackMsg('Invitation code not recognized. If you received a printed card on board, use code: BELLISSIMA-2026');
    }
  };

  return (
    <div className="section-space">
      <div className="page-shell max-w-4xl mx-auto">
        {/* Masthead */}
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="eyebrow text-gold">{t.crew.badge}</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            {t.crew.title}
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-3 font-display italic">
            {t.crew.subtitle}
          </p>
          <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xs text-xs text-slate-800 font-serif italic max-w-xl mx-auto">
            {t.crew.officerObservation}
          </div>
        </div>

        {/* 3 Value Pillars */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <HeartHandshake className="w-6 h-6 text-emerald-700 mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              {t.crew.pillar1Title}
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              {t.crew.pillar1Desc}
            </p>
          </div>

          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <Lock className="w-6 h-6 text-gold mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              {t.crew.pillar2Title}
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              {t.crew.pillar2Desc}
            </p>
          </div>

          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <Award className="w-6 h-6 text-indigo-700 mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              {t.crew.pillar3Title}
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              {t.crew.pillar3Desc}
            </p>
          </div>
        </div>

        {/* Verification Code Box */}
        <div className="bg-[#0c1b2a] text-white p-8 md:p-10 rounded-xs shadow-md border border-white/10 text-center">
          <Anchor className="w-8 h-8 text-gold mx-auto mb-3" />
          <h2 className="font-display text-2xl md:text-3xl font-normal">Officer Access Code</h2>
          <p className="text-sm text-white/70 max-w-md mx-auto mt-2 leading-relaxed font-light">
            If you are a deck officer, guest relations officer, or naval engineer, enter your access code below.
          </p>

          {!isVerified ? (
            <form onSubmit={handleVerify} className="mt-6 max-w-md mx-auto flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value)}
                placeholder="Enter access code (e.g. BELLISSIMA-2026)"
                className="flex-1 bg-white/10 border border-white/20 rounded-xs px-4 py-3 text-sm text-white placeholder:text-white/40 outline-none focus:border-gold font-mono uppercase"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-white text-ink text-sm font-medium hover:bg-gold transition-colors rounded-xs cursor-pointer"
              >
                Verify
              </button>
            </form>
          ) : (
            <div className="mt-6 p-4 bg-emerald-950/60 border border-emerald-500/40 rounded-xs text-sm text-emerald-300 font-mono">
              <Check className="w-4 h-4 inline mr-2 text-emerald-400" />
              Preview access · contributor verification is not yet live
            </div>
          )}

          {feedbackMsg && !isVerified && (
            <p className="text-xs text-amber-300 mt-3 font-mono">{feedbackMsg}</p>
          )}
        </div>
      </div>
    </div>
  );
}
