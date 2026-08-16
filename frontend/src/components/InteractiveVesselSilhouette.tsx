import type { ShipData, CabinData } from '../types';

interface InteractiveVesselSilhouetteProps {
  ship: ShipData;
  cabin: CabinData;
  onSelectCabin?: (cabinNum: string) => void;
}

export function InteractiveVesselSilhouette({
  ship,
  cabin,
}: InteractiveVesselSilhouetteProps) {
  const isRiver = ship.total_decks <= 5;
  const currentDeckNum = cabin.deck_number;

  // Deck elevation calculations
  const deckElevations = Object.values(ship.decks).map((d) => d.elevation_m);
  const maxElevation = Math.max(...deckElevations, 1);
  const currentElev = ship.decks[currentDeckNum]?.elevation_m ?? 0;

  // Longitudinal position fraction (0.0 = Aft, 1.0 = Bow)
  let zoneFrac = 0.5;
  if (cabin.zone === 'FORWARD') zoneFrac = 0.82;
  else if (cabin.zone === 'MIDSHIP') zoneFrac = 0.50;
  else if (cabin.zone === 'AFT') zoneFrac = 0.22;

  // Calculate pixel percentages for vector canvas (ViewBox: 800 x 240)
  const shipLeft = 60;
  const shipRight = 740;
  const shipWidth = shipRight - shipLeft;
  const pinX = shipLeft + zoneFrac * shipWidth;

  // Deck Y calculation (Superstructure spans Y: 40 to Y: 170, Waterline at Y: 190)
  const superstructureTop = isRiver ? 80 : 40;
  const mainDeckY = 165;
  const elevationRatio = currentElev / (maxElevation || 1);
  const pinY = mainDeckY - elevationRatio * (mainDeckY - superstructureTop);

  return (
    <div className="bg-white border border-ink/8 p-6 md:p-8 rounded-xs shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-widest text-gold font-medium block">
            Architectural Cross-Section
          </span>
          <h3 className="font-display text-2xl text-ink font-normal mt-0.5">
            Stateroom Position on {ship.name}
          </h3>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono text-muted">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-gold animate-pulse" />
            <strong className="text-ink">Cabin {cabin.cabin_number}</strong>
          </span>
          <span className="text-ink/40">·</span>
          <span>Deck {currentDeckNum} ({currentElev}m above water)</span>
        </div>
      </div>

      {/* Interactive Vector Canvas */}
      <div className="relative w-full aspect-[800/240] bg-[#0c1b2a] rounded-xs overflow-hidden border border-ink/10 shadow-inner">
        {/* Subtle coordinate grid lines */}
        <div className="absolute inset-0 bg-[radial-gradient(#c99a5b15_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

        <svg
          viewBox="0 0 800 240"
          className="w-full h-full select-none"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Gradients */}
            <linearGradient id="hullGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#1e3246" />
              <stop offset="100%" stopColor="#0f1e2d" />
            </linearGradient>
            <linearGradient id="superstructureGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2c445c" />
              <stop offset="100%" stopColor="#182838" />
            </linearGradient>
            <linearGradient id="waterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#0c1b2a" stopOpacity="0.8" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Water Surface Line */}
          <path
            d="M 0 190 Q 200 188 400 190 T 800 190 L 800 240 L 0 240 Z"
            fill="url(#waterGrad)"
          />
          <line
            x1="0"
            y1="190"
            x2="800"
            y2="190"
            stroke="#38bdf8"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.4"
          />
          <text x="15" y="205" fill="#38bdf8" fontSize="9" fontFamily="monospace" opacity="0.6">
            WATERLINE (0.0 m)
          </text>

          {/* Ship Vector Silhouette */}
          {!isRiver ? (
            /* Ocean Mega-Liner Silhouette (MSC Bellissima / Meraviglia Class) */
            <g id="ocean-ship-hull">
              {/* Main Superstructure */}
              <path
                d="M 90 170 L 90 85 L 140 85 L 150 55 L 450 55 L 480 65 L 610 65 L 670 125 L 730 170 Z"
                fill="url(#superstructureGrad)"
                stroke="#476582"
                strokeWidth="1.5"
              />

              {/* Distinctive Funnel Stack */}
              <path
                d="M 320 55 L 345 25 L 385 25 L 375 55 Z"
                fill="#c99a5b"
                stroke="#ffffff"
                strokeWidth="1"
                opacity="0.9"
              />
              <circle cx="355" cy="40" r="6" fill="#0c1b2a" />

              {/* Lower Hull (Dark Maritime Steel) */}
              <path
                d="M 70 170 L 90 205 L 140 212 L 670 212 L 720 202 L 745 170 Z"
                fill="url(#hullGrad)"
                stroke="#334d66"
                strokeWidth="1.5"
              />

              {/* Bulbous Bow underwater contour */}
              <path
                d="M 720 202 Q 748 206 742 195 Q 735 185 745 170"
                fill="none"
                stroke="#476582"
                strokeWidth="1.5"
              />
            </g>
          ) : (
            /* Luxury Riverboat Silhouette (MS Andorinha) */
            <g id="river-ship-hull">
              {/* Riverboat Superstructure */}
              <path
                d="M 90 170 L 95 105 L 640 105 L 725 155 L 740 170 Z"
                fill="url(#superstructureGrad)"
                stroke="#476582"
                strokeWidth="1.5"
              />
              {/* Sun Deck Shade Awning */}
              <rect x="220" y="88" width="320" height="15" fill="#c99a5b" opacity="0.85" rx="2" />
              {/* Wheelhouse */}
              <rect x="580" y="90" width="35" height="15" fill="#ffffff" opacity="0.9" rx="2" />

              {/* Shallow River Hull */}
              <path
                d="M 75 170 L 90 198 L 710 198 L 740 170 Z"
                fill="url(#hullGrad)"
                stroke="#334d66"
                strokeWidth="1.5"
              />
            </g>
          )}

          {/* Active Deck Elevation Glow Line */}
          <line
            x1="85"
            y1={pinY}
            x2="710"
            y2={pinY}
            stroke="#c99a5b"
            strokeWidth="1.5"
            strokeDasharray="6 3"
            opacity="0.85"
            filter="url(#glow)"
          />
          <text
            x="718"
            y={pinY + 3}
            fill="#c99a5b"
            fontSize="9"
            fontFamily="monospace"
            fontWeight="bold"
          >
            DECK {currentDeckNum}
          </text>

          {/* Stateroom Pinpoint Beacon */}
          <g transform={`translate(${pinX}, ${pinY})`}>
            {/* Animated Ping Wave */}
            <circle cx="0" cy="0" r="14" fill="none" stroke="#c99a5b" strokeWidth="1.5" opacity="0.6">
              <animate
                attributeName="r"
                values="4;18;24"
                dur="2s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                values="0.9;0.3;0"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>

            {/* Glowing Core Pin */}
            <circle cx="0" cy="0" r="5" fill="#c99a5b" stroke="#ffffff" strokeWidth="2" filter="url(#glow)" />

            {/* Vertical Marker Line */}
            <line x1="0" y1="5" x2="0" y2={190 - pinY} stroke="#c99a5b" strokeWidth="1" strokeDasharray="2 2" opacity="0.5" />

            {/* Badge Tooltip */}
            <g transform="translate(0, -18)">
              <rect
                x="-32"
                y="-14"
                width="64"
                height="16"
                fill="#ffffff"
                rx="2"
                stroke="#0c1b2a"
                strokeWidth="1"
              />
              <text
                x="0"
                y="-3"
                textAnchor="middle"
                fill="#0c1b2a"
                fontSize="9.5"
                fontFamily="monospace"
                fontWeight="bold"
              >
                #{cabin.cabin_number}
              </text>
            </g>
          </g>

          {/* Longitudinal Scale Labels */}
          <text x="100" y="230" fill="#ffffff" fontSize="9" fontFamily="monospace" opacity="0.5">
            ◀ AFT / STERN
          </text>
          <text x="375" y="230" fill="#ffffff" fontSize="9" fontFamily="monospace" opacity="0.5" textAnchor="middle">
            MIDSHIP
          </text>
          <text x="690" y="230" fill="#ffffff" fontSize="9" fontFamily="monospace" opacity="0.5" textAnchor="end">
            BOW / FORWARD ▶
          </text>
        </svg>
      </div>

      {/* Orientation Quick Facts */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
        <div className="bg-paper/50 border border-ink/6 rounded-xs p-3 text-center">
          <span className="text-[10px] uppercase font-mono text-muted block">Vertical Level</span>
          <span className="font-display text-lg text-ink font-normal mt-0.5 block">
            Deck {currentDeckNum} ({cabin.deck_name})
          </span>
        </div>
        <div className="bg-paper/50 border border-ink/6 rounded-xs p-3 text-center">
          <span className="text-[10px] uppercase font-mono text-muted block">Ship Section</span>
          <span className="font-display text-lg text-ink font-normal mt-0.5 block">
            {cabin.zone}
          </span>
        </div>
        <div className="bg-paper/50 border border-ink/6 rounded-xs p-3 text-center">
          <span className="text-[10px] uppercase font-mono text-muted block">Vessel Side</span>
          <span className="font-display text-lg text-ink font-normal mt-0.5 block">
            {cabin.hull_side === 'STARBOARD' ? 'Starboard (Right)' : cabin.hull_side === 'PORT' ? 'Port (Left)' : 'Centerline'}
          </span>
        </div>
        <div className="bg-paper/50 border border-ink/6 rounded-xs p-3 text-center">
          <span className="text-[10px] uppercase font-mono text-muted block">Elevation</span>
          <span className="font-display text-lg text-gold font-normal mt-0.5 block">
            +{currentElev} m above sea
          </span>
        </div>
      </div>
    </div>
  );
}
