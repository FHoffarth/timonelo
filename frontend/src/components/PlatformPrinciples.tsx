export function PlatformPrinciples() {
  return (
    <section id="platform-principles" className="section-space border-t border-ink/8 bg-paper">
      <div className="page-shell">
        {/* Core Principle Quote */}
        <div className="card p-8 md:p-14 bg-white border border-ink/8 shadow-xs mb-20">
          <p className="eyebrow text-gold tracking-widest uppercase">Platform Constitution</p>
          <blockquote className="font-display text-2xl sm:text-3xl md:text-4xl text-ink mt-3 leading-snug tracking-tight max-w-3xl font-normal">
            "Great software does not maximize interaction. It minimizes future regret."
          </blockquote>
          <p className="text-muted text-[15px] sm:text-base leading-relaxed mt-4 max-w-2xl">
            Timonelo is not a booking engine or an advertising portal. It is a decision companion designed to eliminate uncertainty before you make a non-refundable travel choice.
          </p>
        </div>

        {/* 3 Pillars */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <div className="card p-7 md:p-8 bg-white border border-ink/8">
            <span className="font-mono text-xs text-gold uppercase tracking-wider block mb-3">
              Negative Intelligence
            </span>
            <h3 className="font-display text-2xl text-ink font-normal">Decisions Avoided</h3>
            <p className="text-[14px] text-muted leading-relaxed mt-3">
              True value is measured by bad choices prevented: noisy galleys directly above your bed, obstructed lifeboat views, and long dead-end walks to the elevator.
            </p>
          </div>

          <div className="card p-7 md:p-8 bg-white border border-ink/8">
            <span className="font-mono text-xs text-gold uppercase tracking-wider block mb-3">
              Fast Orientation
            </span>
            <h3 className="font-display text-2xl text-ink font-normal">15-Second Clarity</h3>
            <p className="text-[14px] text-muted leading-relaxed mt-3">
              No searching through hundred-page deck PDFs. Entering any cabin number gives you its exact elevation, vessel side, vertical surroundings, and step counts.
            </p>
          </div>

          <div className="card p-7 md:p-8 bg-white border border-ink/8">
            <span className="font-mono text-xs text-gold uppercase tracking-wider block mb-3">
              Verifiable Evidence
            </span>
            <h3 className="font-display text-2xl text-ink font-normal">Zero Speculation</h3>
            <p className="text-[14px] text-muted leading-relaxed mt-3">
              Every detail is anchored in official naval blueprints and physical onboard measurements. Timonelo never sounds more certain than its evidence.
            </p>
          </div>
        </div>

        {/* 12-Phase Cruise Journey */}
        <div id="cruise-intelligence-section" className="pt-12 border-t border-ink/8">
          <div className="max-w-2xl mb-10">
            <p className="eyebrow text-muted/70 tracking-widest uppercase">Cruise Intelligence</p>
            <h3 className="section-title text-3xl sm:text-4xl md:text-5xl mt-2 font-normal">
              Certainty at every step of your journey.
            </h3>
            <p className="text-muted text-[15px] leading-relaxed mt-3">
              From the quiet moment before booking at home to your return, Timonelo provides calm, evidence-based orientation.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { num: '01', title: 'Dream & Select', desc: 'Evaluating ship size & class' },
              { num: '02', title: 'Booking', desc: 'Stateroom location verification' },
              { num: '03', title: 'Preparation', desc: 'Packing, sockets & deck rules' },
              { num: '04', title: 'Travel Day', desc: 'Terminal transfers & luggage drop' },
              { num: '05', title: 'Embarkation', desc: 'Boarding pass & muster routes' },
              { num: '06', title: 'First Hour', desc: '15-second stateroom orientation' },
              { num: '07', title: 'Dining', desc: 'Assigned dining room & buffet' },
              { num: '08', title: 'Evenings', desc: 'Theatre & lounge wayfinding' },
              { num: '09', title: 'Port Days', desc: 'Berth vs tender & gangway decks' },
              { num: '10', title: 'Excursions', desc: 'Walkable sights & meeting points' },
              { num: '11', title: 'Disembarkation', desc: 'Luggage tags & customs timing' },
              { num: '12', title: 'Journey Home', desc: 'Seamless onward transit' },
            ].map((phase) => (
              <div key={phase.num} className="card p-4 bg-white border border-ink/8">
                <span className="font-mono text-xs text-gold block">{phase.num}</span>
                <h4 className="font-display text-base text-ink mt-1 font-normal">{phase.title}</h4>
                <p className="text-[11px] text-muted mt-1 leading-snug">{phase.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
