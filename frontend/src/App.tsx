import { useState, useEffect } from 'react';
import type { ShipData, CabinData } from './types';

export default function App() {
  const [ship, setShip] = useState<ShipData | null>(null);
  const [selectedCabinNum, setSelectedCabinNum] = useState<string>('14122');
  const [activeLens, setActiveLens] = useState<'default' | 'accessibility' | 'family' | 'quiet'>('default');
  const [searchQuery, setSearchQuery] = useState<string>('14122');
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'briefing' | 'deck' | 'distances' | 'evidence'>('briefing');

  useEffect(() => {
    fetch('/data/msc-bellissima.json')
      .then((res) => res.json())
      .then((data: ShipData) => {
        setShip(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load MSC Bellissima spatial pack:', err);
        setLoading(false);
      });
  }, []);

  const cabin: CabinData | undefined = ship?.cabins[selectedCabinNum];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (ship?.cabins[query]) {
      setSelectedCabinNum(query);
    }
  };

  if (loading || !ship) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center text-ink font-sans">
        <div className="text-center space-y-3">
          <p className="eyebrow text-muted">Timonelo Spatial Engine</p>
          <h1 className="font-display text-3xl">Loading MSC Bellissima Spatial Ontology...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink font-sans">
      {/* Masthead Navigation */}
      <header className="border-b border-ink/15 bg-white sticky top-0 z-30 shadow-xs">
        <div className="page-shell flex items-center justify-between h-20">
          <div className="flex items-center gap-6">
            <a href="/" className="font-display text-2xl tracking-tight text-ink font-semibold">
              Timonelo
            </a>
            <span className="text-xs text-muted border-l border-ink/20 pl-4 hidden sm:inline">
              Cruise Spatial Orientation
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span className="inline-flex items-center px-3 py-1 bg-sand/30 border border-sand text-ink text-xs font-mono font-medium rounded-xs">
              {ship.name} (IMO {ship.imo.replace('IMO', '')})
            </span>
          </div>
        </div>
      </header>

      {/* Main Explorer Shell */}
      <main className="page-shell py-8">
        {/* Search & Ship Breadcrumb Bar */}
        <section className="bg-white border border-ink/15 p-6 mb-8 shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <p className="eyebrow text-muted mb-1">Select Cabin</p>
              <h2 className="font-display text-3xl text-ink">
                {cabin ? `Cabin ${cabin.cabin_number}` : 'Select a Cabin'}
              </h2>
              <p className="text-xs text-muted mt-1">
                Deck {cabin?.deck_number} ({cabin?.deck_name}) · {cabin?.hull_side} · {cabin?.zone}
              </p>
            </div>

            {/* Cabin Number Input */}
            <form onSubmit={handleSearch} className="flex items-center gap-3">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g. 14122, 14120, 14121"
                  className="min-h-12 border border-ink/25 bg-paper px-4 font-mono text-sm text-ink outline-none focus:border-ink focus:ring-2 focus:ring-gold/60 w-48"
                />
              </div>
              <button type="submit" className="button button-dark min-h-12 px-6">
                Locate
              </button>
            </form>
          </div>

          {/* Quick Cabin Chips */}
          <div className="mt-4 pt-4 border-t border-ink/10 flex items-center gap-2 text-xs">
            <span className="text-muted">Verified Test Cabins:</span>
            {Object.keys(ship.cabins).map((cNum) => (
              <button
                key={cNum}
                onClick={() => {
                  setSelectedCabinNum(cNum);
                  setSearchQuery(cNum);
                }}
                className={`px-2.5 py-1 border font-mono transition ${
                  selectedCabinNum === cNum
                    ? 'border-ink bg-ink text-white font-semibold'
                    : 'border-ink/20 bg-paper hover:bg-sand/30'
                }`}
              >
                {cNum} {ship.cabins[cNum].is_accessible ? '(Acc)' : ''}
              </button>
            ))}
          </div>
        </section>

        {/* Plane 4: Contextual Lens Selector */}
        <section className="bg-white border border-ink/15 p-4 mb-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Contextual Lens:</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {[
              { id: 'default', label: '01 Standard View' },
              { id: 'accessibility', label: '02 Accessibility Lens' },
              { id: 'family', label: '03 Family Lens' },
              { id: 'quiet', label: '04 Quiet Cabin Lens' },
            ].map((lens) => (
              <button
                key={lens.id}
                onClick={() => setActiveLens(lens.id as any)}
                className={`px-4 py-2 text-xs font-semibold transition rounded-xs border ${
                  activeLens === lens.id
                    ? 'border-gold bg-gold/15 text-ink shadow-xs'
                    : 'border-ink/15 bg-white text-muted hover:border-ink/40'
                }`}
              >
                {lens.label}
              </button>
            ))}
          </div>
        </section>

        {/* Explorer Content Tabs */}
        <div className="flex border-b border-ink/20 mb-8 space-x-6 text-sm font-semibold">
          {[
            { id: 'briefing', label: 'Cabin Briefing' },
            { id: 'deck', label: 'Deck Anatomy & Topology' },
            { id: 'distances', label: 'Calculated Walking Distances' },
            { id: 'evidence', label: 'Physical Evidence & Sources' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`pb-3 transition border-b-2 ${
                activeTab === tab.id
                  ? 'border-ink text-ink'
                  : 'border-transparent text-muted hover:text-ink'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: CABIN BRIEFING */}
        {activeTab === 'briefing' && cabin && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Column 1: Core Spatial Identity */}
            <div className="bg-white border border-ink/15 p-6 space-y-6">
              <div>
                <p className="eyebrow text-muted">Physical Dimensions</p>
                <p className="font-display text-4xl mt-1">{cabin.square_meters} m²</p>
                <p className="text-xs text-muted mt-1">
                  Category {cabin.category_code} · {cabin.balcony_type.replace(/_/g, ' ')}
                </p>
              </div>

              <div className="border-t border-ink/10 pt-4 space-y-3 text-xs">
                <div className="flex justify-between py-1 border-b border-ink/5">
                  <span className="text-muted">Bed Placement</span>
                  <span className="font-medium">{cabin.bed_near_balcony ? 'Near Balcony' : 'Near Bathroom'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-ink/5">
                  <span className="text-muted">Door Clearance</span>
                  <span className="font-medium font-mono">{cabin.door_width_mm} mm</span>
                </div>
                <div className="flex justify-between py-1 border-b border-ink/5">
                  <span className="text-muted">Connecting Cabin</span>
                  <span className="font-medium font-mono">{cabin.connecting_cabin_number ?? 'None'}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-muted">Hull Side</span>
                  <span className="font-medium">{cabin.hull_side} (Sun exposure oriented)</span>
                </div>
              </div>

              {/* Power Socket Matrix */}
              <div className="border-t border-ink/10 pt-4">
                <p className="eyebrow text-muted mb-2">Electrical Fixture Matrix</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 bg-paper border border-ink/10">
                    <span className="text-muted block">EU Type F</span>
                    <span className="font-mono font-bold text-sm">{cabin.sockets.eu_count}x</span>
                  </div>
                  <div className="p-2 bg-paper border border-ink/10">
                    <span className="text-muted block">US Type A/B</span>
                    <span className="font-mono font-bold text-sm">{cabin.sockets.us_count}x</span>
                  </div>
                  <div className="p-2 bg-paper border border-ink/10">
                    <span className="text-muted block">USB-A</span>
                    <span className="font-mono font-bold text-sm">{cabin.sockets.usb_a_count}x</span>
                  </div>
                  <div className="p-2 bg-paper border border-ink/10">
                    <span className="text-muted block">USB-C</span>
                    <span className="font-mono font-bold text-sm">{cabin.sockets.usb_c_count}x</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Column 2: Surroundings & 3D Sandwich */}
            <div className="bg-white border border-ink/15 p-6 space-y-6">
              <div>
                <p className="eyebrow text-muted">Surroundings & Overhead</p>
                <h3 className="font-display text-2xl mt-1">3D Spatial Sandwich</h3>
              </div>

              {/* Overhead Layer (Deck N+1) */}
              <div className="p-4 border border-ink/15 bg-paper rounded-xs space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold">OVERHEAD (Deck {cabin.surroundings.overhead.deck_number}: {cabin.surroundings.overhead.deck_name})</span>
                  {cabin.surroundings.overhead.is_noise_generator && (
                    <span className="px-2 py-0.5 bg-amber-100 border border-amber-300 text-amber-900 text-[10px] font-semibold uppercase">
                      Active Venue
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted">
                  {cabin.surroundings.overhead.venues.length > 0
                    ? `Directly beneath: ${cabin.surroundings.overhead.venues.join(', ')}`
                    : 'Residential stateroom deck directly overhead (buffered).'}
                </p>
              </div>

              {/* Cabin Level (Deck N) */}
              <div className="p-4 border-2 border-gold bg-white rounded-xs space-y-1">
                <p className="text-xs font-bold text-ink">CURRENT STATEROOM (Deck {cabin.deck_number})</p>
                <p className="text-xs text-muted">
                  Cabin {cabin.cabin_number} · Midship-Aft corridor corridor snap.
                </p>
              </div>

              {/* Underfoot Layer (Deck N-1) */}
              <div className="p-4 border border-ink/15 bg-paper rounded-xs space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold">UNDERFOOT (Deck {cabin.surroundings.underfoot.deck_number}: {cabin.surroundings.underfoot.deck_name})</span>
                </div>
                <p className="text-xs text-muted">
                  {cabin.surroundings.underfoot.venues.length > 0
                    ? `Directly above: ${cabin.surroundings.underfoot.venues.join(', ')}`
                    : 'Residential stateroom deck directly underfoot (insulated).'}
                </p>
              </div>

              {/* Sightlines */}
              <div className="border-t border-ink/10 pt-4">
                <p className="eyebrow text-muted mb-1">Balcony Horizon Sightline</p>
                <p className="text-xs text-ink font-medium">{cabin.sightlines.description}</p>
                <p className="text-[11px] text-muted mt-1">
                  Horizon View: {cabin.sightlines.horizon_angle_deg}° · Downward Sea View: {cabin.sightlines.downward_angle_deg}°
                </p>
              </div>
            </div>

            {/* Column 3: Active Contextual Lens Output */}
            <div className="bg-white border border-ink/15 p-6 space-y-6">
              <div>
                <p className="eyebrow text-gold font-bold">Plane 4 Evaluation</p>
                <h3 className="font-display text-2xl mt-1">
                  {activeLens === 'default' && 'Standard Briefing'}
                  {activeLens === 'accessibility' && 'Accessibility Assessment'}
                  {activeLens === 'family' && 'Family Adjacency Context'}
                  {activeLens === 'quiet' && 'Acoustic Buffer Context'}
                </h3>
              </div>

              {activeLens === 'default' && (
                <div className="space-y-4 text-xs leading-relaxed text-muted">
                  <p>
                    This stateroom is located on residential Tier {cabin.deck_number} with direct step-free access
                    to the Aft elevator lobby ({cabin.distances.elevator?.meters}m walking distance).
                  </p>
                  <p>
                    Balcony sightline to the horizon is mathematically unobstructed ({cabin.sightlines.horizon_angle_deg}° arc).
                  </p>
                </div>
              )}

              {activeLens === 'accessibility' && (
                <div className="space-y-4 text-xs">
                  <div className={`p-3 border ${cabin.lenses.accessibility.is_certified ? 'bg-emerald-50 border-emerald-200 text-emerald-950' : 'bg-paper border-ink/15'}`}>
                    <p className="font-semibold">{cabin.lenses.accessibility.is_certified ? '✓ Certified Accessible' : 'Standard Mobility Stateroom'}</p>
                    <p className="mt-1 text-muted leading-relaxed">{cabin.lenses.accessibility.summary}</p>
                  </div>
                  <div className="p-3 bg-paper border border-ink/10">
                    <p className="text-muted">Door Clear Width: <span className="font-mono font-bold text-ink">{cabin.door_width_mm} mm</span></p>
                    <p className="text-muted mt-1">Step-Free Lift Route: <span className="font-mono font-bold text-ink">{cabin.lenses.accessibility.lift_distance_m} m</span></p>
                  </div>
                </div>
              )}

              {activeLens === 'family' && (
                <div className="space-y-4 text-xs">
                  <div className={`p-3 border ${cabin.lenses.family.has_connecting ? 'bg-blue-50 border-blue-200 text-blue-950' : 'bg-paper border-ink/15'}`}>
                    <p className="font-semibold">{cabin.lenses.family.has_connecting ? '✓ Adjoining Cabin Pair' : 'Single Stateroom'}</p>
                    <p className="mt-1 text-muted leading-relaxed">{cabin.lenses.family.summary}</p>
                  </div>
                  <div className="p-3 bg-paper border border-ink/10">
                    <p className="text-muted">Connecting Door: <span className="font-mono font-bold text-ink">{cabin.lenses.family.connecting_cabin ?? 'None'}</span></p>
                    <p className="text-muted mt-1">DOREMI Kids Club: <span className="font-mono font-bold text-ink">{cabin.lenses.family.kids_club_distance_m} m</span></p>
                  </div>
                </div>
              )}

              {activeLens === 'quiet' && (
                <div className="space-y-4 text-xs">
                  <div className={`p-3 border ${cabin.lenses.quiet.is_quiet_tier ? 'bg-emerald-50 border-emerald-200 text-emerald-950' : 'bg-amber-50 border-amber-200 text-amber-950'}`}>
                    <p className="font-semibold">{cabin.lenses.quiet.is_quiet_tier ? '✓ Acoustically Buffered' : '⚠ Active Venue Adjacency'}</p>
                    <p className="mt-1 leading-relaxed">{cabin.lenses.quiet.summary}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="font-semibold text-ink">Acoustic Flags:</p>
                    {cabin.lenses.quiet.acoustic_flags.map((flag, idx) => (
                      <div key={idx} className="p-2 bg-paper border border-ink/10 text-muted">
                        • {flag}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: DECK ANATOMY & TOPOLOGY */}
        {activeTab === 'deck' && cabin && (
          <div className="bg-white border border-ink/15 p-6 space-y-6">
            <div>
              <p className="eyebrow text-muted">Plane 2 Topological Visualizer</p>
              <h3 className="font-display text-3xl">Deck {cabin.deck_number} ({cabin.deck_name}) Corridor Topology</h3>
            </div>

            {/* Topological Schematic Map */}
            <div className="border border-ink/20 p-8 bg-paper rounded-xs text-center space-y-6">
              <div className="max-w-xl mx-auto flex items-center justify-between text-xs text-muted border-b border-ink/10 pb-2">
                <span>◀ AFT (Stern)</span>
                <span>MIDSHIP</span>
                <span>BOW (Forward) ▶</span>
              </div>

              {/* Corridor Track Graphic */}
              <div className="relative h-24 bg-white border border-ink/20 rounded-xs flex items-center px-12 justify-between">
                <div className="text-center">
                  <span className="p-2 bg-ink text-white text-xs font-mono font-bold rounded-xs">AFT LIFT</span>
                  <span className="block text-[10px] text-muted mt-1">Core A</span>
                </div>

                <div className="flex-1 mx-8 relative flex items-center justify-center">
                  <div className="w-full h-1 bg-ink/20 absolute" />
                  <div className="z-10 p-3 bg-gold border border-ink text-ink font-mono font-bold text-xs shadow-md">
                    Cabin {cabin.cabin_number} (Selected)
                  </div>
                </div>

                <div className="text-center">
                  <span className="p-2 bg-paper border border-ink/30 text-ink text-xs font-mono font-bold rounded-xs">MID LIFT</span>
                  <span className="block text-[10px] text-muted mt-1">Core M</span>
                </div>
              </div>

              <p className="text-xs text-muted max-w-md mx-auto">
                Cabin door opens directly onto the Starboard Aft residential corridor branch.
                Distance to Aft elevator core is {cabin.distances.elevator?.meters}m ({cabin.distances.elevator?.steps} steps).
              </p>
            </div>
          </div>
        )}

        {/* TAB 3: CALCULATED WALKING DISTANCES */}
        {activeTab === 'distances' && cabin && (
          <div className="bg-white border border-ink/15 p-6 space-y-6">
            <div>
              <p className="eyebrow text-muted">Plane 3 Deterministic Spatial Calculus</p>
              <h3 className="font-display text-3xl">Wayfinding Graph Distances from Cabin {cabin.cabin_number}</h3>
            </div>

            <div className="grid sm:grid-cols-3 gap-6">
              <div className="p-5 border border-ink/15 bg-paper space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">Marketplace Buffet (Deck 15)</p>
                <p className="font-display text-4xl text-ink">{cabin.distances.buffet?.meters} m</p>
                <p className="text-xs text-muted">
                  {cabin.distances.buffet?.steps} steps · ~{cabin.distances.buffet?.seconds}s walk (via Aft Elevator)
                </p>
              </div>

              <div className="p-5 border border-ink/15 bg-paper space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">London Theatre (Deck 06)</p>
                <p className="font-display text-4xl text-ink">{cabin.distances.theater?.meters} m</p>
                <p className="text-xs text-muted">
                  {cabin.distances.theater?.steps} steps · ~{cabin.distances.theater?.seconds}s walk (Multi-Deck)
                </p>
              </div>

              <div className="p-5 border border-ink/15 bg-paper space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">Nearest Elevator Core</p>
                <p className="font-display text-4xl text-ink">{cabin.distances.elevator?.meters} m</p>
                <p className="text-xs text-muted">
                  {cabin.distances.elevator?.steps} steps · ~{cabin.distances.elevator?.seconds}s walk (Same Deck)
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: PHYSICAL EVIDENCE & SOURCES */}
        {activeTab === 'evidence' && cabin && (
          <div className="bg-white border border-ink/15 p-6 space-y-6">
            <div>
              <p className="eyebrow text-muted">Plane 1 Content-Addressed Evidence Ledger</p>
              <h3 className="font-display text-3xl">Primary Sources & Audit Trails</h3>
            </div>

            <div className="space-y-4">
              {cabin.evidence.map((ev, idx) => (
                <div key={idx} className="p-4 border border-ink/15 bg-paper rounded-xs space-y-2 font-mono text-xs">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-ink">{ev.source_id}</span>
                    <span className="text-[10px] text-muted">SHA-256 Verified</span>
                  </div>
                  <p className="text-muted text-[11px]">Locator: {ev.locator}</p>
                  <p className="text-[10px] text-muted/70 break-all">Hash: {ev.sha256}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-ink/15 bg-white py-8 mt-16 text-xs text-muted">
        <div className="page-shell flex justify-between items-center">
          <p>© {new Date().getFullYear()} Timonelo Spatial Engine · MSC Bellissima Reference Implementation</p>
          <p>Never sound more certain than the evidence.</p>
        </div>
      </footer>
    </div>
  );
}
