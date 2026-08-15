import { useState } from 'react';
import {
  Compass,
  Anchor,
  ShieldCheck,
  Clock,
  Waves,
  Utensils,
  MapPin,
  FileCheck,
  CreditCard,
  AlertCircle,
  Sparkles,
  ChevronRight,
  Sun,
  ShieldAlert,
} from 'lucide-react';
import type { ShipData, CabinData } from './types';

interface CruiseBriefingProps {
  ship: ShipData;
  cabin: CabinData;
  onClose?: () => void;
}

export function CruiseBriefingView({ ship, cabin, onClose }: CruiseBriefingProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'ship' | 'port' | 'travel'>('summary');

  const isStarboard = parseInt(cabin.number.slice(-1), 10) % 2 === 0;
  const isForward = (cabin.bounds[0]?.[0] || 0.5) > 0.55;
  const musterStation = isForward
    ? isStarboard ? 'Muster Station A (Forward)' : 'Muster Station D (Forward Port)'
    : isStarboard ? 'Muster Station C (Aft)' : 'Muster Station F (Aft Port)';
  const musterDeck = isStarboard ? 6 : 7;

  return (
    <section className="bg-paper border border-mist/30 rounded-2xl p-6 sm:p-8 shadow-sm my-8 text-ink">
      {/* Top Banner: Bridge Officer Voice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-mist/20 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-mist">
            <Compass className="w-4 h-4 text-ink" />
            Plane 6 · Cruise Intelligence Runtime
          </div>
          <h2 className="font-display text-2xl sm:text-3xl text-ink mt-2">
            Today's Cruise Briefing
          </h2>
          <p className="text-sm text-mist mt-1 font-serif italic">
            {ship.name} · Day 01: Genoa (Genova), Italy · Stateroom {cabin.number} (Deck {cabin.deck})
          </p>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-xs font-mono uppercase tracking-wider text-mist hover:text-ink px-3 py-1.5 rounded-lg border border-mist/20 hover:border-mist/50 transition-colors self-start sm:self-auto"
          >
            Close Briefing
          </button>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-mist/15 mt-6 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === 'summary'
              ? 'bg-ink text-paper font-semibold shadow-xs'
              : 'text-mist hover:text-ink hover:bg-mist/10'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          The Three Clearances
        </button>
        <button
          onClick={() => setActiveTab('ship')}
          className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === 'ship'
              ? 'bg-ink text-paper font-semibold shadow-xs'
              : 'text-mist hover:text-ink hover:bg-mist/10'
          }`}
        >
          <Anchor className="w-3.5 h-3.5" />
          Ship & Safety
        </button>
        <button
          onClick={() => setActiveTab('port')}
          className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === 'port'
              ? 'bg-ink text-paper font-semibold shadow-xs'
              : 'text-mist hover:text-ink hover:bg-mist/10'
          }`}
        >
          <MapPin className="w-3.5 h-3.5" />
          Port & Gangway
        </button>
        <button
          onClick={() => setActiveTab('travel')}
          className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === 'travel'
              ? 'bg-ink text-paper font-semibold shadow-xs'
              : 'text-mist hover:text-ink hover:bg-mist/10'
          }`}
        >
          <CreditCard className="w-3.5 h-3.5" />
          Travel & Etiquette
        </button>
      </div>

      {/* Tab 1: The Three Clearances (Decision First & Negative Intelligence) */}
      {activeTab === 'summary' && (
        <div className="space-y-6 mt-6">
          <div className="bg-paper-light border border-mist/25 rounded-xl p-5">
            <p className="text-xs font-mono uppercase tracking-widest text-mist">
              Bridge Officer Perspective
            </p>
            <p className="font-serif text-base text-ink mt-2 leading-relaxed">
              "Good morning. For today in Genoa, there are strictly three timeframes that require your attention. Everything else is taken care of."
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Clearance 1 */}
            <div className="border border-mist/20 rounded-xl p-5 bg-paper flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-amber-700 font-medium">
                  <ShieldAlert className="w-4 h-4" />
                  1. Mandatory Safety Drill
                </div>
                <h3 className="font-display text-lg text-ink mt-2">
                  {musterStation}
                </h3>
                <p className="text-xs text-mist mt-1 font-mono">
                  Deck {String(musterDeck).padStart(2, '0')} · Before 16:30
                </p>
                <p className="text-sm text-ink/80 mt-3 leading-normal">
                  Take your nearest elevator core down to Deck {String(musterDeck).padStart(2, '0')}. Follow emergency pathfinding to validate your safety check.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-mist/15 text-[11px] font-mono text-mist">
                ✓ Solves SOLAS statutory compliance
              </div>
            </div>

            {/* Clearance 2 */}
            <div className="border border-mist/20 rounded-xl p-5 bg-paper flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-blue-700 font-medium">
                  <Clock className="w-4 h-4" />
                  2. All-Aboard Deadline
                </div>
                <h3 className="font-display text-lg text-ink mt-2">
                  17:30 Gangway Deck 05
                </h3>
                <p className="text-xs text-mist mt-1 font-mono">
                  Berth 10 · 450m from center
                </p>
                <p className="text-sm text-ink/80 mt-3 leading-normal">
                  Piazza Principe and the Old Port are an easy 8-minute level walk via the pedestrian skybridge.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-mist/15 text-[11px] font-mono text-mist">
                ✓ Solves port return timing
              </div>
            </div>

            {/* Clearance 3 */}
            <div className="border border-mist/20 rounded-xl p-5 bg-paper flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-emerald-700 font-medium">
                  <Utensils className="w-4 h-4" />
                  3. Dinner Logistics
                </div>
                <h3 className="font-display text-lg text-ink mt-2">
                  Il Ciliegio (Deck 06 Aft)
                </h3>
                <p className="text-xs text-mist mt-1 font-mono">
                  Dress: Casual Elegant · 45m walk
                </p>
                <p className="text-sm text-ink/80 mt-3 leading-normal">
                  Direct lift down to Deck 06 Aft. The Marketplace Buffet (Deck 15) is also open 06:00–01:30.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-mist/15 text-[11px] font-mono text-mist">
                ✓ Solves evening dining route
              </div>
            </div>
          </div>

          {/* Negative Intelligence Section (Decisions Avoided) */}
          <div className="border border-ink/15 rounded-xl p-5 bg-paper-light">
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-ink font-semibold">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Negative Intelligence · Friction Prevented Today
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3 text-xs text-ink/80">
              <div className="flex items-start gap-2 bg-paper p-3 rounded-lg border border-mist/15">
                <ChevronRight className="w-3.5 h-3.5 text-mist shrink-0 mt-0.5" />
                <span><strong>No roaming shock:</strong> Turn on Airplane Mode upon departure from port waters to block satellite cellular costs.</span>
              </div>
              <div className="flex items-start gap-2 bg-paper p-3 rounded-lg border border-mist/15">
                <ChevronRight className="w-3.5 h-3.5 text-mist shrink-0 mt-0.5" />
                <span><strong>No stair barrier:</strong> Route to Gangway Deck 05 is 100% step-free via midship elevator core.</span>
              </div>
              <div className="flex items-start gap-2 bg-paper p-3 rounded-lg border border-mist/15">
                <ChevronRight className="w-3.5 h-3.5 text-mist shrink-0 mt-0.5" />
                <span><strong>No dress code mismatch:</strong> Collared shirts/dresses recommended for Deck 6 dining tonight.</span>
              </div>
              <div className="flex items-start gap-2 bg-paper p-3 rounded-lg border border-mist/15">
                <ChevronRight className="w-3.5 h-3.5 text-mist shrink-0 mt-0.5" />
                <span><strong>No taxi surcharge:</strong> Official municipality flat fare from pier into center is €15.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Ship & Safety */}
      {activeTab === 'ship' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <Anchor className="w-4 h-4 text-mist" /> Stateroom Orientation
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Cabin:</strong> {cabin.number} (Deck {cabin.deck})</li>
              <li><strong>Side:</strong> {cabin.side.toUpperCase()} ({isStarboard ? 'Starboard / Right' : 'Port / Left'})</li>
              <li><strong>Door Width:</strong> {cabin.doorWidthMm} mm clear aperture</li>
              <li><strong>Sockets:</strong> {cabin.sockets.euStandard}x EU, {cabin.sockets.usStandard}x US, {cabin.sockets.usbA}x USB-A</li>
            </ul>
          </div>

          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" /> Life Safety Logistics
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Assembly Point:</strong> {musterStation}</li>
              <li><strong>Deck:</strong> Deck {String(musterDeck).padStart(2, '0')}</li>
              <li><strong>Drill Deadline:</strong> 16:30 (Mandatory SOLAS)</li>
              <li><strong>Accessibility:</strong> 100% step-free via central elevator core</li>
            </ul>
          </div>
        </div>
      )}

      {/* Tab 3: Port & Gangway */}
      {activeTab === 'port' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <MapPin className="w-4 h-4 text-mist" /> Port Navigation · Genoa
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Berth:</strong> Stazione Marittima, Berth 10</li>
              <li><strong>Gangway Deck:</strong> Deck 05 (Midship Starboard)</li>
              <li><strong>All-Aboard:</strong> 17:30 Prompt</li>
              <li><strong>Distance to Town:</strong> 450 m (8 min walk via skybridge)</li>
            </ul>
          </div>

          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-600" /> Weather & Sea State
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Forecast:</strong> 24.5°C, Gentle coastal breeze</li>
              <li><strong>Sea Swell:</strong> 0.6 m (Beaufort 2 - Smooth)</li>
              <li><strong>Stabilizers:</strong> Active Fin Stabilizers Deployed</li>
              <li><strong>Sun Exposure:</strong> Starboard afternoon sun</li>
            </ul>
          </div>
        </div>
      )}

      {/* Tab 4: Travel & Etiquette */}
      {activeTab === 'travel' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-mist" /> Sovereign Entry & Customs
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Country:</strong> Italy (Schengen Zone)</li>
              <li><strong>Passport Validity:</strong> 6 months required</li>
              <li><strong>Visa:</strong> EU/EEA/US/UK/CAN visa-free transit</li>
              <li><strong>Currency Limit:</strong> Declarations required for ≥ €10,000</li>
            </ul>
          </div>

          <div className="border border-mist/20 rounded-xl p-5 bg-paper">
            <h3 className="font-display text-lg text-ink flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-mist" /> Currency & Etiquette
            </h3>
            <ul className="mt-3 space-y-2 text-xs text-ink/80 font-mono">
              <li><strong>Currency:</strong> Euro (€ / EUR)</li>
              <li><strong>Card Acceptance:</strong> 98% Contactless / Apple Pay</li>
              <li><strong>Tipping:</strong> Service included (Coperto); 5–10% optional</li>
              <li><strong>Emergency Phone:</strong> 112 (European Emergency)</li>
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
