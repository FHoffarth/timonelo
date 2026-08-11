/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from 'motion/react';
import type { ReactNode } from 'react';
import { Anchor, DoorClosed, Eye, Footprints, Map, ShieldCheck, Volume2, Waves } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-[#F5F7F9] text-[#1A1C1E] font-sans selection:bg-[#102A43] selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <CabinPreview />
        <TrustSection />
      </main>
      <Footer />
    </div>
  );
}

function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-white border-b border-[#DDE2E7]">
      <div className="max-w-7xl mx-auto px-12 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-[#102A43] flex items-center justify-center">
            <div className="w-1 h-3 bg-white rotate-45"></div>
          </div>
          <span className="font-semibold text-lg tracking-tight uppercase text-[#102A43]">Timonelo</span>
        </div>
        <div className="hidden sm:flex items-center gap-8 text-[10px] font-bold uppercase tracking-[0.15em] text-[#627D98]">
          <a href="#preview" className="hover:text-[#102A43] transition-colors">Cabin Briefing</a>
          <a href="#methodology" className="hover:text-[#102A43] transition-colors">Methodology</a>
          <a href="#how-it-works" className="hover:text-[#102A43] transition-colors">How it Works</a>
          <button className="bg-transparent text-[#627D98] hover:text-[#102A43] transition-colors uppercase tracking-[0.15em] text-[10px] font-bold ml-4">
            Join Waitlist
          </button>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="pt-56 pb-40 px-12 relative overflow-hidden">
      <div className="max-w-5xl mx-auto text-center relative z-10 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col items-center"
        >
          <span className="inline-block py-1.5 px-4 border border-[#BCCCDC] text-[10px] font-bold tracking-[0.2em] uppercase mb-12 text-[#627D98] bg-white">
            Independent Cabin Intelligence
          </span>
          <h1 className="font-serif text-5xl md:text-7xl lg:text-[5.5rem] leading-[1.05] text-[#102A43] mb-8 max-w-4xl mx-auto tracking-tight">
            Know your cabin<br />before you book.
          </h1>
          <p className="text-lg md:text-xl text-[#486581] max-w-2xl mx-auto leading-relaxed mb-16 font-light">
            Independent cabin intelligence that helps you make better cruise booking decisions through objective spatial evidence.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <button className="w-full sm:w-auto px-8 py-4 bg-[#102A43] text-white text-[13px] font-medium tracking-wide flex items-center justify-center gap-2 hover:bg-[#1A1C1E] transition-colors">
              Join the waitlist
            </button>
            <button className="w-full sm:w-auto px-8 py-4 bg-transparent text-[#102A43] border border-[#BCCCDC] text-[13px] font-medium tracking-wide hover:bg-white transition-colors">
              See an example Briefing
            </button>
          </div>

          <div className="flex items-center justify-center gap-4 text-[10px] uppercase tracking-[0.2em] text-[#627D98] font-bold">
            <span>Built on evidence.</span>
            <span className="w-1 h-1 bg-[#DDE2E7] rounded-full"></span>
            <span>Not advertising.</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function CabinPreview() {
  return (
    <section id="preview" className="py-40 px-12 bg-white border-y border-[#DDE2E7]">
      <div className="max-w-[85rem] mx-auto">
        <div className="mb-24 text-center max-w-2xl mx-auto">
          <h2 className="font-serif text-4xl md:text-5xl text-[#102A43] mb-6">The Cabin Briefing</h2>
          <p className="text-[#486581] font-normal text-lg">A premium editorial report replacing marketing ambiguity with architectural truth.</p>
        </div>

        <div className="grid lg:grid-cols-12 gap-20 items-start">

          {/* Briefing Mockup */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
            className="lg:col-span-7 xl:col-span-8 bg-white border border-[#DDE2E7] shadow-xl relative overflow-hidden flex flex-col"
          >
            <div className="relative z-10">
              <header className="border-b border-[#F0F4F8] p-10 pb-8">
                <div className="flex justify-between items-end mb-4">
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#9FB3C8] font-bold">Cabin Briefing ID: 8204-CB-VY</span>
                  <span className="text-[11px] font-mono tracking-wide text-[#627D98]">Deck 7 • Midship</span>
                </div>
                <h3 className="font-serif text-4xl text-[#102A43] mt-2">Veranda Stateroom</h3>
                <p className="text-[#627D98] mt-2 text-sm tracking-wide">Viking Ocean Cruises • Viking Star class</p>
              </header>

              <div className="p-10 space-y-10 bg-[#F5F7F9]">
                <BriefingSection
                  icon={<Volume2 className="w-4 h-4" />}
                  title="Noise Profile"
                  status="Quiet"
                  content="Located between passenger decks. No public venues immediately above or below. Negligible engine vibration due to mid-forward placement."
                />
                <BriefingSection
                  icon={<Waves className="w-4 h-4" />}
                  title="Motion & Stability"
                  status="Optimal"
                  content="Close to the ship's center of gravity. Minimal pitch and roll felt during standard sea conditions. Highly recommended for sensitive passengers."
                />
                <BriefingSection
                  icon={<Eye className="w-4 h-4" />}
                  title="View & Balcony"
                  status="Unobstructed"
                  content="Clear sightlines straight down to the waterline. No lifeboat obstructions. Balcony depth is 1.2m (standard), fully shaded by Deck 8 overhang."
                />
                <div className="grid sm:grid-cols-2 gap-10 border-t border-[#DDE2E7] pt-10">
                  <BriefingSection
                    icon={<Footprints className="w-4 h-4" />}
                    title="Walking Distance"
                    content="45m to midship elevators. 120m to main dining."
                    compact
                  />
                  <BriefingSection
                    icon={<DoorClosed className="w-4 h-4" />}
                    title="Privacy"
                    content="Not adjacent to crew stairs or high-traffic corridors."
                    compact
                  />
                </div>
              </div>

              <div className="bg-[#102A43] p-10 text-white flex justify-between items-center">
                <div>
                  <h4 className="text-[10px] uppercase tracking-[0.15em] font-bold text-[#9FB3C8] mb-2">Final Intelligence Verdict</h4>
                  <p className="text-2xl font-serif">Highly Recommended</p>
                </div>
                <div className="text-right">
                  <h4 className="text-[10px] uppercase tracking-[0.15em] font-bold text-[#9FB3C8] mb-2">Evidence Confidence</h4>
                  <p className="text-[13px] font-semibold tracking-wide uppercase text-white">Extensive Evidence</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Context / Explanation */}
          <div className="lg:col-span-5 xl:col-span-4 space-y-16 lg:sticky lg:top-32 mt-12 lg:mt-0">
            <div>
              <h3 className="font-serif text-3xl md:text-4xl text-[#102A43] mb-6 leading-tight">Never sound more certain than the evidence.</h3>
              <p className="text-[#486581] font-normal leading-relaxed text-lg">
                Brochures sell a fantasy. We provide the architectural reality. Our briefings analyze deck plans, structural blueprints, and historical vessel data to give you absolute clarity on what you are booking.
              </p>
            </div>

            <ul className="space-y-8">
              {[
                "Exact distances to elevators and venues.",
                "Analysis of adjacent and vertical noise sources.",
                "Truthful assessment of balcony obstructions.",
                "Pitch and roll stability ratings."
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-[#102A43]"
                    style={{ borderLeft: '2px solid #DDE2E7', paddingLeft: '1.25rem' }}>
                  <span className="font-light text-base leading-relaxed tracking-wide">{item}</span>
                </li>
              ))}
            </ul>
          </div>

        </div>
      </div>
    </section>
  );
}

function BriefingSection({ icon, title, status, content, compact = false }: { icon: ReactNode, title: string, status?: string, content: string, compact?: boolean }) {
  return (
    <div className={compact ? "" : "border-b border-[#DDE2E7] pb-10 last:border-0 last:pb-0"}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-[#627D98]">{icon}</div>
          <h4 className="text-[10px] uppercase tracking-widest font-bold text-[#486581]">{title}</h4>
        </div>
        {status && (
          <span className="text-[10px] font-bold px-2.5 py-1 bg-white border border-[#DDE2E7] text-[#102A43] uppercase tracking-[0.15em]">
            {status}
          </span>
        )}
      </div>
      <p className="text-[#627D98] text-[13px] leading-relaxed pl-7">
        {content}
      </p>
    </div>
  );
}

function TrustSection() {
  const cards = [
    {
      icon: <Map className="w-5 h-5" />,
      title: "Spatial Evidence",
      description: "Verification through technical deck plans and architect blueprints, not marketing renders.",
      borderColor: "#102A43"
    },
    {
      icon: <ShieldCheck className="w-5 h-5" />,
      title: "Independent Analysis",
      description: "Zero commission-based links. We are funded by travelers, not the cruise lines we analyze.",
      borderColor: "#BCCCDC"
    },
    {
      icon: <Anchor className="w-5 h-5" />,
      title: "No Sponsored Rankings",
      description: "Rankings are purely mathematical based on vibration, noise, and spatial geometry.",
      borderColor: "#BCCCDC"
    }
  ];

  return (
    <section id="trust" className="py-40 px-12 bg-[#F5F7F9]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-24 max-w-2xl mx-auto">
          <h2 className="font-serif text-4xl md:text-5xl text-[#102A43] mb-6">Independent by design.</h2>
          <p className="text-[#486581] font-normal text-lg">Our only loyalty is to objective truth and the traveler.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {cards.map((card, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white p-10 shadow-sm border-y border-r border-[#DDE2E7] flex flex-col"
              style={{ borderLeft: `2px solid ${card.borderColor}` }}
            >
              <div className="w-12 h-12 border border-[#DDE2E7] flex items-center justify-center text-[#102A43] mb-8 bg-[#F5F7F9]">
                {card.icon}
              </div>
              <h3 className="text-[11px] font-bold uppercase tracking-widest text-[#102A43] mb-4">{card.title}</h3>
              <p className="text-[#627D98] text-[13px] leading-relaxed">
                {card.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 border-t border-[#DDE2E7] px-12 flex flex-col md:flex-row items-center justify-between bg-white text-[10px] uppercase tracking-[0.15em] font-medium text-[#9FB3C8]">
      <div className="flex items-center gap-3 mb-6 md:mb-0">
        <div className="w-4 h-4 bg-[#102A43] flex items-center justify-center opacity-40">
          <div className="w-0.5 h-2 bg-white rotate-45"></div>
        </div>
        <span>© {new Date().getFullYear()} Timonelo Intelligence</span>
      </div>
      <div className="mb-6 md:mb-0 text-center tracking-[0.2em] opacity-80">
        Never sound more certain than the evidence.
      </div>
      <div className="flex gap-6 text-center">
        <a href="#" className="hover:text-[#102A43] transition-colors">Privacy</a>
        <span>•</span>
        <a href="#" className="hover:text-[#102A43] transition-colors">Terms</a>
        <span>•</span>
        <a href="#" className="hover:text-[#102A43] transition-colors">Ethics Statement</a>
      </div>
    </footer>
  );
}
