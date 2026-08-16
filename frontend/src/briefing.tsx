import { useState } from 'react';
import {
  Anchor,
  ShieldCheck,
  MapPin,
  FileCheck,
  CreditCard,
  ChevronRight,
  Sun,
} from 'lucide-react';
import type { ShipData, CabinData } from './types';

interface CruiseBriefingProps {
  ship: ShipData;
  cabin: CabinData;
  onClose?: () => void;
}

export function CruiseBriefingView({ ship, cabin, onClose }: CruiseBriefingProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'ship' | 'port' | 'travel'>('summary');

  const cabinNumStr = String(cabin.cabin_number || '14122');
  const isStarboard = parseInt(cabinNumStr.slice(-1), 10) % 2 === 0;
  const isForward = (cabin.zone ?? '').toLowerCase().includes('forward');
  const musterStation = isForward
    ? isStarboard ? 'Muster Station A (Forward Starboard)' : 'Muster Station D (Forward Port)'
    : isStarboard ? 'Muster Station C (Aft Starboard)' : 'Muster Station F (Aft Port)';
  const musterDeck = isStarboard ? 6 : 7;
  const deckNum = cabin.deck_number ?? 14;

  const isRiver = ship.total_decks <= 5;
  const portName = isRiver ? 'Porto (Douro Valley), Portugal' : 'Genoa (Genova), Italy';
  const diningVenue = isRiver ? "The Compass Rose (Emerald Deck)" : "Il Ciliegio (Deck 06 Aft)";

  return (
    <section className="bg-white border border-ink/8 rounded-xs p-7 sm:p-10 shadow-xs text-ink">
      {/* Top Banner: Bridge Officer Voice */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4 border-b border-ink/6 pb-6">
        <div>
          <p className="eyebrow text-gold">Morning Guidance · Bridge Officer</p>
          <h2 className="font-display text-3xl sm:text-4xl text-ink mt-1 font-normal">
            Today’s Cruise Briefing
          </h2>
          <p className="text-sm text-muted mt-1.5 font-display italic">
            {ship.name} · Day 01: {portName} · Cabin {cabinNumStr} (Deck {deckNum})
          </p>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-xs font-mono uppercase tracking-wider text-muted hover:text-ink px-3 py-1.5 rounded-xs border border-ink/10 transition-colors self-start sm:self-auto cursor-pointer"
          >
            Close Briefing
          </button>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-ink/6 mt-6 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-4 py-2 text-xs font-medium rounded-xs transition-colors cursor-pointer ${
            activeTab === 'summary'
              ? 'bg-ink text-white shadow-xs'
              : 'text-muted hover:text-ink hover:bg-paper'
          }`}
        >
          The Three Clearances
        </button>
        <button
          onClick={() => setActiveTab('ship')}
          className={`px-4 py-2 text-xs font-medium rounded-xs transition-colors cursor-pointer ${
            activeTab === 'ship'
              ? 'bg-ink text-white shadow-xs'
              : 'text-muted hover:text-ink hover:bg-paper'
          }`}
        >
          Ship & Safety
        </button>
        <button
          onClick={() => setActiveTab('port')}
          className={`px-4 py-2 text-xs font-medium rounded-xs transition-colors cursor-pointer ${
            activeTab === 'port'
              ? 'bg-ink text-white shadow-xs'
              : 'text-muted hover:text-ink hover:bg-paper'
          }`}
        >
          Port & Gangway
        </button>
        <button
          onClick={() => setActiveTab('travel')}
          className={`px-4 py-2 text-xs font-medium rounded-xs transition-colors cursor-pointer ${
            activeTab === 'travel'
              ? 'bg-ink text-white shadow-xs'
              : 'text-muted hover:text-ink hover:bg-paper'
          }`}
        >
          Travel & Etiquette
        </button>
      </div>

      {/* Tab 1: The Three Clearances */}
      {activeTab === 'summary' && (
        <div className="space-y-6 mt-6">
          <div className="bg-paper/60 border border-ink/6 rounded-xs p-5">
            <p className="eyebrow text-muted/70">Officer Summary</p>
            <p className="font-display text-lg text-ink/90 mt-1 leading-relaxed italic">
              "Good morning. For today in {isRiver ? 'Porto' : 'Genoa'}, there are strictly three timeframes that require your attention. Everything else is taken care of."
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Clearance 1 */}
            <div className="border border-ink/8 rounded-xs p-6 bg-white flex flex-col justify-between shadow-xs">
              <div>
                <span className="text-[11px] font-mono text-amber-800 uppercase tracking-wider block font-medium">
                  1. Mandatory Safety Drill
                </span>
                <h3 className="font-display text-xl text-ink mt-2 font-normal">
                  {musterStation}
                </h3>
                <p className="text-xs text-muted mt-1 font-mono">
                  Deck {String(musterDeck).padStart(2, '0')} · Before 16:30
                </p>
                <p className="text-[13px] text-muted leading-relaxed mt-3">
                  Take your nearest elevator core down to Deck {String(musterDeck).padStart(2, '0')}. Follow emergency pathfinding to validate your check.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-ink/6 text-[11px] font-mono text-muted">
                ✓ Mandatory statutory compliance
              </div>
            </div>

            {/* Clearance 2 */}
            <div className="border border-ink/8 rounded-xs p-6 bg-white flex flex-col justify-between shadow-xs">
              <div>
                <span className="text-[11px] font-mono text-sky-800 uppercase tracking-wider block font-medium">
                  2. All-Aboard Deadline
                </span>
                <h3 className="font-display text-xl text-ink mt-2 font-normal">
                  {isRiver ? '18:00 Pier Gangway' : '17:30 Gangway Deck 05'}
                </h3>
                <p className="text-xs text-muted mt-1 font-mono">
                  {isRiver ? 'Ribeira Pier · Downtown' : 'Berth 10 · 450m from center'}
                </p>
                <p className="text-[13px] text-muted leading-relaxed mt-3">
                  {isRiver
                    ? 'The historic Ribeira riverbank promenade is right at the foot of the gangway.'
                    : 'The Old Port and Piazza Principe are an easy 8-minute level walk via the skybridge.'}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-ink/6 text-[11px] font-mono text-muted">
                Estimated return timing · class reference model
              </div>
            </div>

            {/* Clearance 3 */}
            <div className="border border-ink/8 rounded-xs p-6 bg-white flex flex-col justify-between shadow-xs">
              <div>
                <span className="text-[11px] font-mono text-emerald-800 uppercase tracking-wider block font-medium">
                  3. Dinner Logistics
                </span>
                <h3 className="font-display text-xl text-ink mt-2 font-normal">
                  {diningVenue}
                </h3>
                <p className="text-xs text-muted mt-1 font-mono">
                  Dress: Casual Elegant · Level walk
                </p>
                <p className="text-[13px] text-muted leading-relaxed mt-3">
                  {isRiver
                    ? 'Dinner is served in one open seating with regional Douro wine pairings.'
                    : 'Direct lift down to Deck 06 Aft. The Marketplace Buffet on Deck 15 is also open.'}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-ink/6 text-[11px] font-mono text-muted">
                Modelled evening dining route · class reference model
              </div>
            </div>
          </div>

          {/* Negative Intelligence Section */}
          <div className="border border-ink/8 rounded-xs p-6 bg-paper/50">
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-ink font-semibold">
              <ShieldCheck className="w-4 h-4 text-emerald-700" />
              <span>Negative Intelligence · Friction Prevented Today</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 text-[13px] text-muted">
              <div className="flex items-start gap-2 bg-white p-3.5 rounded-xs border border-ink/6">
                <ChevronRight className="w-3.5 h-3.5 text-gold shrink-0 mt-0.5" />
                <span><strong>No roaming shock:</strong> Turn on Airplane Mode upon departure from port waters to block satellite cellular fees.</span>
              </div>
              <div className="flex items-start gap-2 bg-white p-3.5 rounded-xs border border-ink/6">
                <ChevronRight className="w-3.5 h-3.5 text-gold shrink-0 mt-0.5" />
                <span><strong>Step-free access:</strong> Route to the gangway is 100% step-free via the central elevator core.</span>
              </div>
              <div className="flex items-start gap-2 bg-white p-3.5 rounded-xs border border-ink/6">
                <ChevronRight className="w-3.5 h-3.5 text-gold shrink-0 mt-0.5" />
                <span><strong>Dress guidance:</strong> Smart casual recommended for tonight’s welcome dinner.</span>
              </div>
              <div className="flex items-start gap-2 bg-white p-3.5 rounded-xs border border-ink/6">
                <ChevronRight className="w-3.5 h-3.5 text-gold shrink-0 mt-0.5" />
                <span><strong>Transit clarity:</strong> Official municipality flat fare from pier into center is €15.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Ship & Safety */}
      {activeTab === 'ship' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <Anchor className="w-4 h-4 text-gold" /> Stateroom Orientation
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Cabin:</strong> {cabinNumStr} (Deck {deckNum})</li>
              <li><strong>Side:</strong> {isStarboard ? 'Starboard (Right)' : 'Port (Left)'}</li>
              <li><strong>Door Width:</strong> {cabin.door_width_mm ?? 800} mm clear doorway</li>
              <li><strong>Sockets:</strong> {cabin.sockets?.eu_count ?? 2}x EU, {cabin.sockets?.us_count ?? 2}x US, {cabin.sockets?.usb_a_count ?? 2}x USB-A</li>
            </ul>
          </div>

          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <ShieldCheck className="w-4 h-4 text-emerald-700" /> Life Safety Logistics
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Assembly Point:</strong> {musterStation}</li>
              <li><strong>Assembly Deck:</strong> Deck {String(musterDeck).padStart(2, '0')}</li>
              <li><strong>Drill Deadline:</strong> 16:30 (Mandatory Maritime Drill)</li>
              <li><strong>Route:</strong> Step-free via central elevator core</li>
            </ul>
          </div>
        </div>
      )}

      {/* Tab 3: Port & Gangway */}
      {activeTab === 'port' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <MapPin className="w-4 h-4 text-gold" /> Port Navigation · {portName}
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Berth:</strong> {isRiver ? 'Ribeira Pier 2' : 'Stazione Marittima, Berth 10'}</li>
              <li><strong>Gangway:</strong> {isRiver ? 'Emerald Deck (Fwd)' : 'Deck 05 (Midship Starboard)'}</li>
              <li><strong>All-Aboard:</strong> {isRiver ? '18:00' : '17:30'} Prompt</li>
              <li><strong>Distance to Town:</strong> {isRiver ? '0 m (Downtown)' : '450 m (8 min walk via skybridge)'}</li>
            </ul>
          </div>

          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <Sun className="w-4 h-4 text-gold" /> Weather & Sea Conditions
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Forecast:</strong> 24.5°C, Sunny with gentle breeze</li>
              <li><strong>Water State:</strong> {isRiver ? 'Calm river waters' : '0.6 m swell (Beaufort 2 - Smooth)'}</li>
              <li><strong>Stabilization:</strong> {isRiver ? 'River flat hull' : 'Active fin stabilizers deployed'}</li>
              <li><strong>Sunlight:</strong> Afternoon sun on {isStarboard ? 'Starboard' : 'Port'} beam</li>
            </ul>
          </div>
        </div>
      )}

      {/* Tab 4: Travel & Etiquette */}
      {activeTab === 'travel' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <FileCheck className="w-4 h-4 text-gold" /> Customs & Border Entry
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Country:</strong> {isRiver ? 'Portugal' : 'Italy'} (Schengen Zone)</li>
              <li><strong>Passport:</strong> 6 months validity recommended</li>
              <li><strong>Visa:</strong> EU/EEA/US/UK/CAN visa-free transit</li>
              <li><strong>Currency Rule:</strong> Declaration for ≥ €10,000 in cash</li>
            </ul>
          </div>

          <div className="border border-ink/8 rounded-xs p-6 bg-white">
            <h3 className="font-display text-xl text-ink flex items-center gap-2 font-normal">
              <CreditCard className="w-4 h-4 text-gold" /> Currency & Local Customs
            </h3>
            <ul className="mt-4 space-y-2 text-xs text-muted font-mono">
              <li><strong>Currency:</strong> Euro (€ / EUR)</li>
              <li><strong>Payment:</strong> 98% Contactless / Apple Pay accepted</li>
              <li><strong>Tipping:</strong> Service included; 5–10% optional for excellence</li>
              <li><strong>Emergency Phone:</strong> 112 (European Emergency Number)</li>
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
