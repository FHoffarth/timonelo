import { type CSSProperties, type FormEvent, type ReactNode, useEffect, useRef, useState } from 'react';

import chevronRight from './assets/chevron-right.svg';
import Explorer from './explorer/Explorer';

const heroCruise = '/hero-cruise-golden-hour.webp';

const intelligenceAreas = [
  {
    number: '01',
    title: 'Structural context',
    text: 'The cabin, its deck, and the spaces that surround it—kept specific to the ship being examined.',
  },
  {
    number: '02',
    title: 'Evidence boundaries',
    text: 'What the available sources support, how the finding was reached, and where the evidence stops.',
  },
  {
    number: '03',
    title: 'Material unknowns',
    text: 'What cannot be concluded remains visible instead of being softened into certainty.',
  },
];

const cabinDifferences = [
  ['Position', 'Forward, midship, or aft changes the physical context.'],
  ['Surroundings', 'What sits above, below, and beside a cabin matters.'],
  ['Access', 'Routes to lifts, stairs, and public spaces are not interchangeable.'],
  ['Evidence', 'The source and its limits determine what can responsibly be said.'],
];

const trustPrinciples = [
  ['Traceable', 'Material statements retain a clear path back to the sources and evidence that support them.'],
  ['Bounded', 'Evidence limits and alternative interpretations remain visible where they matter.'],
  ['Explicit', 'Unknowns stay unknown. Timonelo does not quietly replace missing knowledge with assumptions.'],
];

export default function App() {
  if (window.location.pathname.startsWith('/explore')) {
    return <Explorer />;
  }

  return (
    <div className="min-h-screen bg-paper text-ink selection:bg-gold selection:text-ink">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <Hero />
      <main id="main-content">
        <DecisionComplexity />
        <CabinStory />
        <ExplainableIntelligence />
        <CabinIntelligence />
        <Trust />
        <Vision />
        <Waitlist />
      </main>
      <Footer />
    </div>
  );
}

function Hero() {
  return (
    <header className="relative min-h-[100svh] overflow-hidden bg-ink text-white" data-node-id="5:16" id="top">
      <img
        alt="Cruise ship sailing across calm water at golden hour"
        className="absolute inset-0 h-full w-full object-cover object-[57%_center] sm:object-center"
        fetchPriority="high"
        height="1024"
        src={heroCruise}
        width="1440"
      />
      <div className="hero-overlay absolute inset-0" aria-hidden="true" />
      <Navigation />

      <div className="page-shell relative z-10 flex min-h-[100svh] items-end pb-14 pt-32 sm:pb-20 lg:pb-24">
        <div className="hero-content max-w-4xl">
          <p className="eyebrow mb-6 text-white/85">Independent cabin intelligence</p>
          <h1 className="max-w-[13ch] text-balance font-display text-[clamp(3.35rem,11vw,7.5rem)] leading-[0.93] tracking-[-0.045em]">
            Understand your cruise cabin before you book.
          </h1>
          <p className="mt-7 max-w-2xl text-pretty text-base leading-7 text-white/88 sm:text-lg sm:leading-8">
            Travel decisions have become easier to search—but harder to understand. Timonelo brings evidence,
            context, and clear limits to the cabin decision.
          </p>
          <div className="mt-10 flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:gap-8">
            <a className="button button-light" href="#waitlist">
              Join the waitlist
            </a>
            <a className="text-link text-white" href="#intelligence">
              See how it works
              <img alt="" aria-hidden="true" className="h-4 w-4" src={chevronRight} />
            </a>
          </div>
        </div>
      </div>

      <div className="absolute bottom-5 right-5 z-10 hidden text-[0.65rem] uppercase tracking-[0.18em] text-white/70 sm:block lg:bottom-8 lg:right-10">
        Evidence before opinion
      </div>
    </header>
  );
}

function Navigation() {
  return (
    <nav aria-label="Primary navigation" className="absolute inset-x-0 top-0 z-20 border-b border-white/15">
      <div className="page-shell flex h-20 items-center justify-between sm:h-24">
        <a className="font-display text-2xl tracking-[-0.02em] text-white" href="#top" aria-label="Timonelo home">
          Timonelo
        </a>
        <div className="hidden items-center gap-8 text-xs font-medium tracking-[0.02em] text-white/90 md:flex">
          <a className="nav-link" href="#why">The problem</a>
          <a className="nav-link" href="#intelligence">How it works</a>
          <a className="nav-link" href="#trust">Trust</a>
          <a className="nav-link" href="/explore/ships/msc-bellissima">Explore ship</a>
          <a className="nav-link" href="#vision">Vision</a>
        </div>
        <a className="nav-cta" href="#waitlist">Join waitlist</a>
      </div>
    </nav>
  );
}

function DecisionComplexity() {
  return (
    <section className="section-space bg-paper" id="why">
      <div className="page-shell">
        <Reveal>
          <SectionHeading
            eyebrow="01 — The decision"
            title="The booking looks simple. The context is not."
            text="Cabin selection is a high-information decision presented through low-information interfaces. A number, a category, and a deck plan rarely explain the physical reality around a cabin."
          />
        </Reveal>
        <Reveal className="mt-16 border-y border-ink/15 py-8 sm:mt-24 sm:py-10" delay={0.08}>
          <div className="grid gap-8 sm:grid-cols-3 sm:gap-0">
            <DecisionLayer value="Cabin" label="A specific physical place" />
            <DecisionLayer value="Category" label="A commercial grouping" bordered />
            <DecisionLayer value="Context" label="The difference between them" bordered />
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function CabinStory() {
  return (
    <section className="section-space bg-white" id="story">
      <div className="page-shell grid gap-16 lg:grid-cols-[0.8fr_1.2fr] lg:gap-24">
        <Reveal>
          <p className="eyebrow text-muted">02 — Every cabin is specific</p>
          <h2 className="section-title mt-5 max-w-[12ch]">Every cabin tells a different story.</h2>
        </Reveal>
        <div className="border-t border-ink/20">
          {cabinDifferences.map(([title, text], index) => (
            <Reveal key={title} delay={index * 0.04}>
              <div className="grid gap-3 border-b border-ink/20 py-7 sm:grid-cols-[10rem_1fr] sm:gap-8 sm:py-9">
                <h3 className="text-sm font-semibold tracking-[-0.01em] text-ink">{title}</h3>
                <p className="max-w-xl text-base leading-7 text-muted">{text}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function ExplainableIntelligence() {
  const steps = ['Source', 'Evidence', 'Finding', 'Assessment'];

  return (
    <section className="section-space overflow-hidden bg-ink text-white" id="intelligence">
      <div className="page-shell">
        <Reveal>
          <SectionHeading
            dark
            eyebrow="03 — How Timonelo works"
            title="A conclusion should show its working."
            text="Timonelo separates what a source says, what the evidence supports, what can be established as fact, and what remains interpretation. Each layer keeps the limits of the one before it."
          />
        </Reveal>
        <Reveal className="mt-16 sm:mt-24" delay={0.1}>
          <ol className="trace-grid" aria-label="Explainability chain">
            {steps.map((step, index) => (
              <li className="trace-step" key={step}>
                <span className="text-[0.65rem] tracking-[0.18em] text-white/38">0{index + 1}</span>
                <span className="mt-4 font-display text-3xl sm:text-4xl">{step}</span>
              </li>
            ))}
          </ol>
        </Reveal>
        <Reveal className="mt-12 border-l border-gold/70 pl-6 sm:ml-auto sm:mt-16 sm:max-w-xl sm:pl-8" delay={0.16}>
          <p className="font-display text-2xl leading-snug text-white/88 sm:text-3xl">
            Never sound more certain than the evidence.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

function Trust() {
  return (
    <section className="section-space bg-white" id="trust">
      <div className="page-shell">
        <Reveal>
          <SectionHeading
            eyebrow="05 — Why trust Timonelo"
            title="Trust is a chain, not a claim."
            text="Timonelo earns confidence by making the basis and limits of each material assessment inspectable. Certainty is never added for presentation."
          />
        </Reveal>
        <div className="mt-16 border-t border-ink/20 sm:mt-24">
          {trustPrinciples.map(([title, text], index) => (
            <Reveal key={title} delay={index * 0.05}>
              <div className="grid gap-4 border-b border-ink/20 py-9 sm:grid-cols-[5rem_0.75fr_1.25fr] sm:items-baseline sm:gap-8 sm:py-12">
                <span className="text-xs tracking-[0.14em] text-muted">0{index + 1}</span>
                <h3 className="font-display text-3xl leading-tight sm:text-4xl">{title}</h3>
                <p className="max-w-xl text-base leading-7 text-muted">{text}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function CabinIntelligence() {
  return (
    <section className="section-space bg-paper" id="cabin-intelligence">
      <div className="page-shell">
        <Reveal>
          <div className="grid gap-8 border-b border-ink/20 pb-12 lg:grid-cols-[1fr_1fr] lg:items-end">
            <div>
              <p className="eyebrow text-muted">04 — Cabin intelligence</p>
              <h2 className="section-title mt-5 max-w-[13ch]">Not a score. A clearer account of place.</h2>
            </div>
            <p className="max-w-xl text-base leading-7 text-muted lg:justify-self-end sm:text-lg sm:leading-8">
              Cabin intelligence preserves the difference between structural fact, supported finding, and bounded
              assessment. It does not turn uncertainty into a rating.
            </p>
          </div>
        </Reveal>
        <div className="mt-4">
          {intelligenceAreas.map((area, index) => (
            <Reveal key={area.number} delay={index * 0.05}>
              <article className="grid gap-4 border-b border-ink/20 py-9 sm:grid-cols-[5rem_0.8fr_1.2fr] sm:items-baseline sm:gap-8 sm:py-12">
                <span className="text-xs tracking-[0.14em] text-muted">{area.number}</span>
                <h3 className="font-display text-3xl leading-tight sm:text-4xl">{area.title}</h3>
                <p className="max-w-xl text-base leading-7 text-muted">{area.text}</p>
              </article>
            </Reveal>
          ))}
        </div>
        <Reveal className="mt-10 flex flex-col items-start gap-4 border-l-2 border-gold pl-6 sm:flex-row sm:items-center sm:justify-between sm:pl-8" delay={0.08}>
          <p className="max-w-xl text-sm leading-6 text-muted">
            Explore the first canonical Knowledge Pack with complete source provenance.
          </p>
          <a className="button button-dark" href="/explore/ships/msc-bellissima">Explore MSC Bellissima</a>
        </Reveal>
      </div>
    </section>
  );
}

function Vision() {
  return (
    <section className="section-space bg-sand" id="vision">
      <div className="page-shell">
        <Reveal>
          <p className="eyebrow text-ink/55">06 — The vision</p>
          <blockquote className="mt-8 max-w-5xl font-display text-[clamp(2.6rem,7vw,6.5rem)] leading-[0.98] tracking-[-0.04em]">
            “The long-term value is not a universal cabin score.”
          </blockquote>
        </Reveal>
        <Reveal className="mt-12 grid gap-8 border-t border-ink/20 pt-8 sm:mt-16 sm:grid-cols-2 sm:pt-10" delay={0.08}>
          <p className="max-w-lg text-base leading-7 text-ink/70 sm:text-lg sm:leading-8">
            It is a durable body of cabin-specific knowledge: independent, reproducible, and appropriately cautious as
            coverage grows.
          </p>
          <p className="max-w-lg text-base leading-7 text-ink/70 sm:justify-self-end sm:text-lg sm:leading-8">
            A traveler should see the physical context, the evidence behind each statement, and the limit of what can be
            concluded.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

function Waitlist() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // This is the intentional integration boundary for the future waitlist service.
    setSubmitted(true);
  }

  return (
    <section className="section-space bg-white" id="waitlist">
      <div className="page-shell grid gap-12 lg:grid-cols-[1fr_0.85fr] lg:items-end lg:gap-24">
        <Reveal>
          <p className="eyebrow text-muted">07 — Early access</p>
          <h2 className="section-title mt-5 max-w-[11ch]">Make the cabin decision legible.</h2>
          <p className="mt-7 max-w-xl text-base leading-7 text-muted sm:text-lg sm:leading-8">
            Join the early-access list for product updates and the first cabin briefings.
          </p>
        </Reveal>
        <Reveal delay={0.08}>
          {submitted ? (
            <div className="border-l-2 border-gold py-2 pl-6" aria-live="polite">
              <p className="font-display text-3xl">The form is ready.</p>
              <p className="mt-2 text-sm leading-6 text-muted">
                No address was transmitted or stored in this preview.
              </p>
            </div>
          ) : (
            <form className="space-y-5" data-integration="waitlist" onSubmit={handleSubmit}>
              <label className="block text-xs font-semibold tracking-[0.04em] text-ink" htmlFor="waitlist-email">
                Email address
              </label>
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  autoComplete="email"
                  aria-describedby="waitlist-privacy"
                  className="min-h-14 flex-1 border border-ink/25 bg-paper px-4 text-base text-ink outline-none transition focus:border-ink focus:ring-2 focus:ring-gold/60"
                  id="waitlist-email"
                  name="email"
                  placeholder="you@example.com"
                  required
                  type="email"
                />
                <button className="button button-dark min-h-14" type="submit">Request access</button>
              </div>
              <p className="text-xs leading-5 text-muted" id="waitlist-privacy">
                Product updates only. No booking offers or sponsored rankings. This preview does not transmit data.
              </p>
            </form>
          )}
        </Reveal>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-ink/15 bg-white py-8">
      <div className="page-shell flex flex-col gap-4 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} Timonelo</p>
        <p className="max-w-md sm:text-right">Independent cabin intelligence. Evidence before opinion.</p>
      </div>
    </footer>
  );
}

function SectionHeading({ eyebrow, title, text, dark = false }: { eyebrow: string; title: string; text: string; dark?: boolean }) {
  return (
    <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end lg:gap-20">
      <div>
        <p className={`eyebrow ${dark ? 'text-white/48' : 'text-muted'}`}>{eyebrow}</p>
        <h2 className="section-title mt-5 max-w-[14ch]">{title}</h2>
      </div>
      <p className={`max-w-xl text-base leading-7 sm:text-lg sm:leading-8 ${dark ? 'text-white/62' : 'text-muted'}`}>{text}</p>
    </div>
  );
}

function DecisionLayer({ value, label, bordered = false }: { value: string; label: string; bordered?: boolean }) {
  return (
    <div className={`sm:px-8 ${bordered ? 'sm:border-l sm:border-ink/15' : ''}`}>
      <p className="font-display text-4xl tracking-[-0.03em] sm:text-5xl">{value}</p>
      <p className="mt-2 text-sm leading-6 text-muted">{label}</p>
    </div>
  );
}

function Reveal({ children, className = '', delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const elementRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: '0px 0px -10% 0px' },
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      className={`reveal ${isVisible ? 'reveal-visible' : ''} ${className}`}
      ref={elementRef}
      style={{ '--reveal-delay': `${delay}s` } as CSSProperties}
    >
      {children}
    </div>
  );
}
