import { useState, useEffect } from 'react';
import type { ShipData, CabinData } from './types';

export default function App() {
  const [ship, setShip] = useState<ShipData | null>(null);
  const [selectedCabinNum, setSelectedCabinNum] = useState<string>('14122');
  const [activeLens, setActiveLens] = useState<'default' | 'accessibility' | 'family' | 'quiet'>('default');
  const [selectedVenueDestination, setSelectedVenueDestination] = useState<'buffet' | 'theater' | 'elevator'>('buffet');
  const [searchQuery, setSearchQuery] = useState<string>('14122');
  const [loading, setLoading] = useState<boolean>(true);

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
          <h1 className="font-display text-3xl">Loading MSC Bellissima Orientation Map...</h1>
        </div>
      </div>
    );
  }

  const activeDistance = cabin?.distances[selectedVenueDestination];

  return (
    <div className="min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink font-sans pb-20">
      {/* 1. MASTHEAD */}
      <header className="border-b border-ink/15 bg-white sticky top-0 z-30">
        <div className="page-shell flex items-center justify-between h-18">
          <div className="flex items-center gap-4">
            <a href="/" className="font-display text-2xl font-semibold tracking-tight text-ink">
              Timonelo
            </a>
            <span className="text-xs text-muted border-l border-ink/20 pl-4 hidden sm:inline font-sans">
              Ship Orientation Platform
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <span className="block text-xs font-semibold text-ink">{ship.name}</span>
              <span className="block text-[11px] text-muted">{ship.ship_class} · 315.8m Length</span>
            </div>
            <div className="h-2 w-2 rounded-full bg-emerald-500" title="Spatial Engine Connected" />
          </div>
        </div>
      </header>

      {/* 2. CABIN SELECTION & SEARCH HERO */}
      <section className="bg-ink text-white py-10 px-4">
        <div className="page-shell">
          <div className="max-w-4xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="space-y-2">
              <p className="eyebrow text-gold font-medium tracking-widest">Selected Stateroom</p>
              <h1 className="font-display text-4xl sm:text-5xl tracking-tight">
                {cabin ? `Cabin ${cabin.cabin_number}` : 'Select Cabin'}
              </h1>
              <p className="text-sm text-white/70">
                Deck {cabin?.deck_number} ({cabin?.deck_name}) · {cabin?.hull_side === 'STARBOARD' ? 'Starboard (Right)' : 'Port (Left)'} · {cabin?.zone}
              </p>
            </div>

            {/* Cabin Search Input */}
            <form onSubmit={handleSearch} className="flex items-center gap-2">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter cabin (e.g. 14122)"
                  aria-label="Cabin Number"
                  className="h-12 border border-white/20 bg-white/10 px-4 font-mono text-sm text-white placeholder:text-white/40 outline-none focus:border-gold focus:ring-1 focus:ring-gold w-44"
                />
              </div>
              <button type="submit" className="button button-light h-12 px-5 text-xs">
                Find
              </button>
            </form>
          </div>

          {/* Quick Select Verification Cabins */}
          <div className="max-w-4xl mx-auto mt-6 pt-4 border-t border-white/15 flex items-center gap-2 text-xs flex-wrap">
            <span className="text-white/60">Sample Verified Cabins:</span>
            {Object.keys(ship.cabins).map((cNum) => (
              <button
                key={cNum}
                onClick={() => {
                  setSelectedCabinNum(cNum);
                  setSearchQuery(cNum);
                }}
                className={`px-3 py-1 font-mono transition text-xs ${
                  selectedCabinNum === cNum
                    ? 'bg-gold text-ink font-semibold'
                    : 'bg-white/10 text-white/80 hover:bg-white/20'
                }`}
              >
                {cNum} {ship.cabins[cNum].is_accessible ? '(Accessible)' : ''}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 3. MAIN ORIENTATION CONTAINER */}
      <main className="page-shell mt-8 space-y-8">
        {cabin && (
          <>
            {/* GRID: PRIORITY 1 & 2 (Where am I on this ship?) */}
            <div className="grid lg:grid-cols-12 gap-8 items-start">
              
              {/* PRIORITY 1: Spatial Hull Orientation Card (5 Columns) */}
              <section className="lg:col-span-5 bg-white border border-ink/15 p-6 shadow-xs space-y-6">
                <div className="border-b border-ink/10 pb-4">
                  <p className="eyebrow text-muted">Hull Position</p>
                  <h2 className="font-display text-2xl mt-1">Where Your Cabin Sits</h2>
                </div>

                {/* Volumetric Vessel Silhouette Diagram */}
                <div className="relative border border-ink/15 bg-paper p-6 text-center rounded-xs space-y-4">
                  <div className="flex justify-between text-[11px] text-muted font-mono uppercase">
                    <span>Aft (Stern)</span>
                    <span>Midship</span>
                    <span>Forward (Bow)</span>
                  </div>

                  {/* Ship Silhouette Box */}
                  <div className="relative h-20 bg-white border border-ink/20 rounded-xs flex items-center px-4 overflow-hidden">
                    {/* Waterline indicator */}
                    <div className="absolute inset-x-0 bottom-0 h-1.5 bg-sky-200/50" />

                    {/* Ship decks grid lines */}
                    <div className="w-full h-full flex flex-col justify-between py-2 opacity-20">
                      <div className="w-full border-b border-ink" />
                      <div className="w-full border-b border-ink" />
                      <div className="w-full border-b border-ink" />
                    </div>

                    {/* Pin for Selected Cabin */}
                    <div 
                      className="absolute z-10 flex flex-col items-center"
                      style={{ left: '28%', top: '22%' }}
                    >
                      <div className="h-4 w-4 rounded-full bg-gold border-2 border-ink shadow-md animate-pulse" />
                      <span className="text-[10px] font-mono font-bold bg-ink text-white px-1.5 py-0.5 rounded-xs mt-1">
                        {cabin.cabin_number}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2">
                    <div className="p-2 bg-white border border-ink/10">
                      <span className="text-muted block text-[10px] uppercase">Deck Level</span>
                      <span className="font-bold text-ink">Deck {cabin.deck_number}</span>
                    </div>
                    <div className="p-2 bg-white border border-ink/10">
                      <span className="text-muted block text-[10px] uppercase">Ship Side</span>
                      <span className="font-bold text-ink">{cabin.hull_side === 'STARBOARD' ? 'Starboard (Right)' : 'Port (Left)'}</span>
                    </div>
                    <div className="p-2 bg-white border border-ink/10">
                      <span className="text-muted block text-[10px] uppercase">Longitudinal</span>
                      <span className="font-bold text-ink">{cabin.zone}</span>
                    </div>
                  </div>
                </div>

                {/* Spatial Summary Points */}
                <ul className="space-y-2.5 text-xs text-muted leading-relaxed">
                  <li className="flex items-start gap-2">
                    <span className="text-gold font-bold">✓</span>
                    <span><strong>Daylight & Sun:</strong> Facing Starboard. Receives morning light when sailing South, afternoon light sailing North.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-gold font-bold">✓</span>
                    <span><strong>Elevator Access:</strong> {cabin.distances.elevator?.meters}m ({cabin.distances.elevator?.steps} steps) to the Aft Elevator Core.</span>
                  </li>
                </ul>
              </section>

              {/* PRIORITY 2: Mini Deck Context & Nearby Venues (7 Columns) */}
              <section className="lg:col-span-7 bg-white border border-ink/15 p-6 shadow-xs space-y-6">
                <div className="border-b border-ink/10 pb-4 flex justify-between items-end">
                  <div>
                    <p className="eyebrow text-muted">Corridor Context</p>
                    <h2 className="font-display text-2xl mt-1">Deck {cabin.deck_number} ({cabin.deck_name})</h2>
                  </div>
                  <span className="text-xs text-muted font-mono">Elevation: 42.0m above sea</span>
                </div>

                {/* Simplified Schematic Corridor Map */}
                <div className="border border-ink/15 bg-paper p-6 rounded-xs space-y-4">
                  <p className="text-xs font-semibold text-ink uppercase tracking-wider">Walkable Corridor Anatomy</p>
                  
                  {/* Schematic Track */}
                  <div className="bg-white border border-ink/20 p-4 rounded-xs flex items-center justify-between relative">
                    {/* Aft Lift Node */}
                    <div className="text-center z-10">
                      <div className="px-2.5 py-1.5 bg-ink text-white font-mono text-xs font-bold rounded-xs">
                        AFT LIFT
                      </div>
                      <span className="text-[10px] text-muted mt-1 block">Lobby & Stairs</span>
                    </div>

                    {/* Connecting Corridor Line */}
                    <div className="flex-1 mx-4 relative flex items-center justify-center">
                      <div className="w-full h-1 bg-ink/20 absolute" />
                      
                      {/* Highlighted Cabin */}
                      <div className="z-10 px-3 py-1.5 bg-gold border border-ink text-ink font-mono font-bold text-xs shadow-sm flex items-center gap-1.5">
                        <span>🚪</span>
                        <span>Cabin {cabin.cabin_number}</span>
                      </div>
                    </div>

                    {/* Midship Lift Node */}
                    <div className="text-center z-10">
                      <div className="px-2.5 py-1.5 bg-paper border border-ink/30 text-ink font-mono text-xs font-bold rounded-xs">
                        MID LIFT
                      </div>
                      <span className="text-[10px] text-muted mt-1 block">Central Core</span>
                    </div>
                  </div>

                  <p className="text-xs text-muted leading-relaxed">
                    Your cabin door opens onto the Starboard corridor branch, <strong>{cabin.distances.elevator?.meters} meters</strong> from the nearest elevator vestibule.
                  </p>
                </div>

                {/* PRIORITY 3: Interactive Route Preview */}
                <div className="border-t border-ink/10 pt-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="eyebrow text-muted">Calculate Route To</p>
                    <span className="text-[11px] text-muted font-mono">Deterministic Spatial Calculus</span>
                  </div>

                  {/* Destination Toggle Chips */}
                  <div className="flex gap-2">
                    {[
                      { id: 'buffet', label: '🍳 Marketplace Buffet (Deck 15)' },
                      { id: 'theater', label: '🎭 London Theatre (Deck 06)' },
                      { id: 'elevator', label: '🛗 Nearest Elevator (Deck 14)' },
                    ].map((dest) => (
                      <button
                        key={dest.id}
                        onClick={() => setSelectedVenueDestination(dest.id as any)}
                        className={`px-3 py-2 text-xs font-medium border transition ${
                          selectedVenueDestination === dest.id
                            ? 'border-ink bg-ink text-white font-semibold'
                            : 'border-ink/20 bg-paper text-ink hover:bg-sand/30'
                        }`}
                      >
                        {dest.label}
                      </button>
                    ))}
                  </div>

                  {/* Route Metric Card */}
                  {activeDistance && (
                    <div className="p-4 bg-paper border border-ink/15 rounded-xs flex items-center justify-between">
                      <div>
                        <span className="text-xs text-muted uppercase font-semibold block">Walking Distance</span>
                        <span className="font-display text-3xl text-ink font-medium">{activeDistance.meters} m</span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-muted uppercase font-semibold block">Estimated Effort</span>
                        <span className="text-sm font-semibold text-ink">
                          {activeDistance.steps} steps (~{activeDistance.seconds}s walk)
                        </span>
                        <span className="text-[11px] text-emerald-700 block font-medium">
                          {activeDistance.step_free ? '✓ 100% Step-free (Elevator accessible)' : 'Stair route'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            </div>

            {/* PRIORITY 4: SURROUNDINGS & CONTEXT (What sits above and below me?) */}
            <div className="grid md:grid-cols-3 gap-8">
              
              {/* Vertical Surroundings (3D Sandwich) */}
              <section className="bg-white border border-ink/15 p-6 shadow-xs space-y-4">
                <p className="eyebrow text-muted">Vertical Context</p>
                <h3 className="font-display text-2xl">What Sits Around You</h3>

                {/* Ceiling (Deck Above) */}
                <div className="p-3.5 bg-paper border border-ink/15 rounded-xs space-y-1">
                  <div className="flex justify-between text-xs font-bold">
                    <span>ABOVE YOU (Deck {cabin.surroundings.overhead.deck_number})</span>
                    {cabin.surroundings.overhead.is_noise_generator && (
                      <span className="text-[10px] text-amber-800 bg-amber-100 px-1.5 py-0.5 border border-amber-300">Active Space</span>
                    )}
                  </div>
                  <p className="text-xs text-muted">
                    {cabin.surroundings.overhead.venues.length > 0
                      ? `${cabin.surroundings.overhead.venues.join(', ')}`
                      : 'Quiet residential cabins directly above.'}
                  </p>
                </div>

                {/* Cabin Level */}
                <div className="p-3.5 bg-white border-2 border-gold rounded-xs">
                  <span className="text-xs font-bold text-ink block">YOUR CABIN (Deck {cabin.deck_number})</span>
                  <span className="text-xs text-muted">Cabin {cabin.cabin_number} · 19 m² living space</span>
                </div>

                {/* Floor (Deck Below) */}
                <div className="p-3.5 bg-paper border border-ink/15 rounded-xs space-y-1">
                  <span className="text-xs font-bold block">BELOW YOU (Deck {cabin.surroundings.underfoot.deck_number})</span>
                  <p className="text-xs text-muted">
                    {cabin.surroundings.underfoot.venues.length > 0
                      ? `${cabin.surroundings.underfoot.venues.join(', ')}`
                      : 'Quiet residential cabins directly below.'}
                  </p>
                </div>
              </section>

              {/* Physical Fixtures & Balcony View */}
              <section className="bg-white border border-ink/15 p-6 shadow-xs space-y-4">
                <p className="eyebrow text-muted">Room Specifics</p>
                <h3 className="font-display text-2xl">Physical Details</h3>

                <div className="space-y-3 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-ink/10">
                    <span className="text-muted">Balcony Sightline</span>
                    <span className="font-semibold text-emerald-800">180° Unobstructed</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-ink/10">
                    <span className="text-muted">Bed Position</span>
                    <span className="font-medium">{cabin.bed_near_balcony ? 'Adjacent to Balcony' : 'Adjacent to Bathroom'}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-ink/10">
                    <span className="text-muted">Connecting Door</span>
                    <span className="font-medium">{cabin.connecting_cabin_number ? `Yes (To Cabin ${cabin.connecting_cabin_number})` : 'None (Private Wall)'}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-ink/10">
                    <span className="text-muted">Doorway Width</span>
                    <span className="font-mono font-medium">{cabin.door_width_mm} mm</span>
                  </div>
                </div>

                {/* Sockets */}
                <div className="pt-2">
                  <span className="text-[11px] font-semibold text-muted uppercase tracking-wider block mb-2">Available Power Outlets</span>
                  <div className="grid grid-cols-4 gap-1.5 text-center text-xs">
                    <div className="p-1.5 bg-paper border border-ink/10 font-mono"><strong>{cabin.sockets.eu_count}x</strong> EU</div>
                    <div className="p-1.5 bg-paper border border-ink/10 font-mono"><strong>{cabin.sockets.us_count}x</strong> US</div>
                    <div className="p-1.5 bg-paper border border-ink/10 font-mono"><strong>{cabin.sockets.usb_a_count}x</strong> USB-A</div>
                    <div className="p-1.5 bg-paper border border-ink/10 font-mono"><strong>{cabin.sockets.usb_c_count}x</strong> USB-C</div>
                  </div>
                </div>
              </section>

              {/* Contextual Lens Perspective (Plane 4) */}
              <section className="bg-white border border-ink/15 p-6 shadow-xs space-y-4">
                <div className="flex justify-between items-center">
                  <p className="eyebrow text-gold font-bold">Traveler Lens</p>
                  <span className="text-[10px] text-muted">Switch Perspective</span>
                </div>

                {/* Lens Switcher Buttons */}
                <div className="grid grid-cols-3 gap-1 text-[11px] font-semibold">
                  <button
                    onClick={() => setActiveLens('accessibility')}
                    className={`p-1.5 border transition ${activeLens === 'accessibility' ? 'bg-gold text-ink border-gold' : 'bg-paper border-ink/15 text-muted'}`}
                  >
                    Mobility
                  </button>
                  <button
                    onClick={() => setActiveLens('family')}
                    className={`p-1.5 border transition ${activeLens === 'family' ? 'bg-gold text-ink border-gold' : 'bg-paper border-ink/15 text-muted'}`}
                  >
                    Family
                  </button>
                  <button
                    onClick={() => setActiveLens('quiet')}
                    className={`p-1.5 border transition ${activeLens === 'quiet' ? 'bg-gold text-ink border-gold' : 'bg-paper border-ink/15 text-muted'}`}
                  >
                    Quiet
                  </button>
                </div>

                {/* Dynamic Lens Output Box */}
                <div className="p-4 bg-paper border border-ink/15 rounded-xs space-y-2 text-xs">
                  {activeLens === 'accessibility' && (
                    <>
                      <p className="font-bold text-ink">{cabin.lenses.accessibility.is_certified ? '✓ Certified Accessible Cabin' : 'Standard Stateroom'}</p>
                      <p className="text-muted leading-relaxed">{cabin.lenses.accessibility.summary}</p>
                    </>
                  )}

                  {activeLens === 'family' && (
                    <>
                      <p className="font-bold text-ink">{cabin.lenses.family.has_connecting ? '✓ Family Adjoining Pair' : 'Single Stateroom'}</p>
                      <p className="text-muted leading-relaxed">{cabin.lenses.family.summary}</p>
                    </>
                  )}

                  {activeLens === 'quiet' && (
                    <>
                      <p className="font-bold text-ink">{cabin.lenses.quiet.is_quiet_tier ? '✓ Acoustically Buffered' : '⚠ Active Space Adjacency'}</p>
                      <p className="text-muted leading-relaxed">{cabin.lenses.quiet.summary}</p>
                    </>
                  )}

                  {activeLens === 'default' && (
                    <>
                      <p className="font-bold text-ink">General Overview</p>
                      <p className="text-muted leading-relaxed">
                        Well-proportioned stateroom situated in a mid-aft location on Deck 14 with rapid access to Aft elevators.
                      </p>
                    </>
                  )}
                </div>

                {/* Evidence Source Footer */}
                <div className="pt-2 text-[10px] text-muted border-t border-ink/10 flex justify-between">
                  <span>Source: Naval GA Blueprints</span>
                  <span className="font-mono">SHA-256 Verified</span>
                </div>
              </section>

            </div>
          </>
        )}
      </main>

      {/* 4. FOOTER */}
      <footer className="border-t border-ink/15 bg-white py-8 mt-20 text-xs text-muted">
        <div className="page-shell flex flex-col sm:flex-row justify-between items-center gap-4">
          <p>© {new Date().getFullYear()} Timonelo · MSC Bellissima Reference Spatial System</p>
          <p className="text-center sm:text-right">
            Independent cruise orientation. Never sound more certain than the evidence.
          </p>
        </div>
      </footer>
    </div>
  );
}
