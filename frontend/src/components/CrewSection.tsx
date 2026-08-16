import { useState } from 'react';
import {
  ShieldCheck,
  Lock,
  Anchor,
  Check,
  Award,
  HeartHandshake,
  Compass,
} from 'lucide-react';

export function CrewSection() {
  const [accessCode, setAccessCode] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    if (accessCode.trim().toUpperCase() === 'BELLISSIMA-2026' || accessCode.trim().toUpperCase() === 'OCTOBER-2026') {
      setIsVerified(true);
      setFeedbackMsg('Invitation accepted. Welcome to the MSC Bellissima Maritime Contributor Circle.');
    } else {
      setFeedbackMsg('Invitation code not recognized. If you received a printed card on board, use code: BELLISSIMA-2026');
    }
  };

  return (
    <div className="section-space">
      <div className="page-shell max-w-4xl mx-auto">
        {/* Masthead */}
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="eyebrow text-gold">Maritime Professional Collaboration</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            An Invitation to the Crew
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-3 font-display italic">
            You know this ship better than anyone in the world. Help future passengers experience its architecture with calm clarity.
          </p>
        </div>

        {/* 3 Value Pillars */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <HeartHandshake className="w-6 h-6 text-emerald-700 mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              Prevent Day 1 Confusion
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              Most front-desk questions on embarkation day are simple navigation problems. Contributing accurate gangway and lift facts solves guest confusion before they step on board.
            </p>
          </div>

          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <Lock className="w-6 h-6 text-gold mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              Protected & Confidential
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              Completely anonymous to the public. Contributions are attributed cryptographically so you can freely share factual layout corrections without social media exposure.
            </p>
          </div>

          <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
            <Compass className="w-6 h-6 text-sky-700 mb-3" />
            <h3 className="font-display text-xl text-ink font-normal mb-2">
              Honoring Your Ship
            </h3>
            <p className="text-[13px] text-muted leading-relaxed">
              No subjective ratings or complaint boards. Structured factual corrections that celebrate the true naval craftsmanship and accessibility of your ship.
            </p>
          </div>
        </div>

        {/* Valuable Observations */}
        <div className="bg-paper/70 border border-ink/8 p-8 rounded-xs shadow-xs mb-12">
          <h2 className="font-display text-2xl text-ink font-normal mb-4">
            Real Insights That Help Guests
          </h2>
          <div className="grid sm:grid-cols-2 gap-4 text-[13px] text-muted">
            <div className="bg-white p-4 rounded-xs border border-ink/6">
              <strong className="text-ink block mb-1">🚪 Wheelchair Doorway Clearances:</strong>
              Exact doorway widths and step-free bathroom thresholds that help guests with limited mobility.
            </div>
            <div className="bg-white p-4 rounded-xs border border-ink/6">
              <strong className="text-ink block mb-1">⚓ Turnaround Gangway Decks:</strong>
              Which deck the passenger gangway connects to in major turnaround ports like Genoa or Barcelona.
            </div>
            <div className="bg-white p-4 rounded-xs border border-ink/6">
              <strong className="text-ink block mb-1">🌙 Quiet Corridor Zones:</strong>
              Identifying staterooms that stay wonderfully peaceful throughout sea days and turnaround mornings.
            </div>
            <div className="bg-white p-4 rounded-xs border border-ink/6">
              <strong className="text-ink block mb-1">🚶 Elevator Flow Tips:</strong>
              Direct lift cores vs. stairwell connections during embarkation rush hours.
            </div>
          </div>
        </div>

        {/* Invitation Access Card */}
        <div className="bg-white border border-ink/10 p-8 rounded-xs shadow-sm max-w-xl mx-auto text-center">
          <Anchor className="w-8 h-8 text-gold mx-auto mb-3" />
          <h3 className="font-display text-2xl text-ink font-normal">
            Onboard Invitation Entry
          </h3>
          <p className="text-xs text-muted mt-1 mb-6">
            Enter the invitation phrase from your printed card to join the onboard contributor circle.
          </p>

          {!isVerified ? (
            <form onSubmit={handleVerify} className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  placeholder="e.g. BELLISSIMA-2026"
                  className="flex-1 px-4 py-2.5 font-mono text-xs border border-ink/20 rounded-xs outline-none focus:border-gold uppercase"
                  required
                />
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-ink text-white text-xs font-medium rounded-xs hover:bg-gold hover:text-ink transition-colors cursor-pointer"
                >
                  Join Circle
                </button>
              </div>
              {feedbackMsg && (
                <p className="text-xs text-amber-800 font-mono text-left bg-amber-50 p-2.5 rounded-xs border border-amber-200">
                  {feedbackMsg}
                </p>
              )}
            </form>
          ) : (
            <div className="bg-emerald-50 border border-emerald-200 p-5 rounded-xs text-emerald-900 text-left space-y-3">
              <div className="flex items-center gap-2 font-medium text-xs font-mono text-emerald-800">
                <Check className="w-4 h-4 text-emerald-700" />
                <span>Active Contributor Session (MSC Bellissima)</span>
              </div>
              <p className="text-xs text-emerald-900 leading-relaxed">
                Welcome aboard. During your October voyage, you can share factual layout observations directly with the Lead Knowledge Architect on board or via your private session token.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
