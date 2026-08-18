import { useState, useEffect, useRef } from 'react';
import { Search, X, Ship, MapPin, DoorClosed, Utensils, Layers, ArrowRight } from 'lucide-react';
import { FLEET_REGISTRY } from '../fleet';
import { PORTS_REGISTRY } from '../ports';
import { knowledgeRepository } from '../knowledge';

interface SearchResultItem {
  id: string;
  type: 'ship' | 'cabin' | 'port' | 'venue' | 'deck';
  title: string;
  subtitle: string;
  badge: string;
  action: () => void;
}

interface UniversalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectShip: (slug: string) => void;
  onSelectCabin: (shipSlug: string, cabinNum: string) => void;
  onSelectPort: (slug: string) => void;
}

export function UniversalSearchModal({
  isOpen,
  onClose,
  onSelectShip,
  onSelectCabin,
  onSelectPort,
}: UniversalSearchModalProps) {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Build searchable index
  const results: SearchResultItem[] = [];
  const q = query.trim().toLowerCase();

  if (q.length > 0) {
    // 1. Ships
    FLEET_REGISTRY.forEach((v) => {
      if (v.name.toLowerCase().includes(q) || v.slug.includes(q) || v.shipClass.toLowerCase().includes(q)) {
        results.push({
          id: `ship:${v.slug}`,
          type: 'ship',
          title: v.name,
          subtitle: `${v.roleTitle} · ${v.operator}`,
          badge: 'Vessel',
          action: () => {
            onSelectShip(v.slug);
            onClose();
          },
        });
      }
    });

    // 2. Ports
    PORTS_REGISTRY.forEach((p) => {
      if (p.name.toLowerCase().includes(q) || p.slug.includes(q) || p.unLocode.toLowerCase().includes(q) || p.country.toLowerCase().includes(q)) {
        results.push({
          id: `port:${p.slug}`,
          type: 'port',
          title: p.name,
          subtitle: `${p.region} (${p.unLocode})`,
          badge: 'Port',
          action: () => {
            onSelectPort(p.slug);
            onClose();
          },
        });
      }
    });

    // 3. Cabins (e.g. numeric search)
    if (/^[0-9]+$/.test(q)) {
      results.push({
        id: `cabin:bellissima:${q}`,
        type: 'cabin',
        title: `Cabin ${q} (MSC Bellissima)`,
        subtitle: 'Open the stateroom geometry and orientation dossier',
        badge: 'Stateroom',
        action: () => {
          onSelectCabin('msc-bellissima', q);
          onClose();
        },
      });
      if (q === '301' || q.startsWith('1') || q.startsWith('2') || q.startsWith('3')) {
        results.push({
          id: `cabin:andorinha:${q}`,
          type: 'cabin',
          title: `Cabin ${q} (MS Andorinha)`,
          subtitle: 'Open Douro River stateroom geometry',
          badge: 'Stateroom',
          action: () => {
            onSelectCabin('ms-andorinha', q);
            onClose();
          },
        });
      }
    }

    // 4. Venues - Dynamically sourced from Knowledge Layer
    const bellissimaPublic = knowledgeRepository.getPublicAreas('msc-bellissima').map((v) => ({
      name: v.name,
      ship: 'msc-bellissima',
      desc: v.description,
    }));
    const bellissimaDining = knowledgeRepository.getRestaurants('msc-bellissima').map((v) => ({
      name: v.name,
      ship: 'msc-bellissima',
      desc: v.description,
    }));
    const bellissimaEnt = knowledgeRepository.getEntertainment('msc-bellissima').map((v) => ({
      name: v.name,
      ship: 'msc-bellissima',
      desc: v.description,
    }));

    const otherVenues = [
      { name: 'The Compass Rose Restaurant', ship: 'ms-andorinha', desc: 'River Dining Room Emerald Deck' },
      { name: 'Panorama Lounge & Bar', ship: 'ms-andorinha', desc: 'Forward River Lounge Deck 3' },
    ];

    const allVenues = [...bellissimaPublic, ...bellissimaDining, ...bellissimaEnt, ...otherVenues];

    allVenues.forEach((venue) => {
      if (venue.name.toLowerCase().includes(q) || venue.desc.toLowerCase().includes(q)) {
        results.push({
          id: `venue:${venue.name}`,
          type: 'venue',
          title: venue.name,
          subtitle: venue.desc,
          badge: 'Venue',
          action: () => {
            onSelectShip(venue.ship);
            onClose();
          },
        });
      }
    });
  }

  const getIcon = (type: SearchResultItem['type']) => {
    switch (type) {
      case 'ship':
        return <Ship className="w-4 h-4 text-gold" />;
      case 'port':
        return <MapPin className="w-4 h-4 text-sky-700" />;
      case 'cabin':
        return <DoorClosed className="w-4 h-4 text-amber-700" />;
      case 'venue':
        return <Utensils className="w-4 h-4 text-emerald-700" />;
      default:
        return <Layers className="w-4 h-4 text-muted" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink/70 backdrop-blur-sm grid place-items-start p-4 sm:p-6 pt-20 overflow-y-auto">
      <div className="bg-white border border-ink/15 rounded-xs shadow-xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 p-4 border-b border-ink/8">
          <Search className="w-5 h-5 text-muted shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search vessels, cabins (e.g. 14122, 301), ports (Genoa), or venues..."
            className="flex-1 text-sm text-ink placeholder:text-muted/60 outline-none font-sans"
          />
          {query && (
            <button onClick={() => setQuery('')} className="p-1 hover:bg-paper rounded-xs text-muted cursor-pointer">
              <X className="w-4 h-4" />
            </button>
          )}
          <button onClick={onClose} className="px-2.5 py-1 text-xs font-mono text-muted hover:text-ink border border-ink/10 rounded-xs cursor-pointer">
            ESC
          </button>
        </div>

        {/* Results Body */}
        <div className="max-h-96 overflow-y-auto p-2">
          {query.trim().length === 0 ? (
            <div className="p-6 text-center text-xs text-muted">
              <p className="font-mono uppercase tracking-widest text-muted/60 mb-2">Universal Search</p>
              <p>Type any ship name (<em>Bellissima, Andorinha</em>), cabin number (<em>14122</em>), or port (<em>Genoa, Barcelona</em>).</p>
            </div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted">
              No records match "{query}". Try a cabin number or port name.
            </div>
          ) : (
            <div className="space-y-1">
              {results.map((item) => (
                <button
                  key={item.id}
                  onClick={item.action}
                  className="w-full p-3 rounded-xs hover:bg-paper/70 transition-colors flex items-center justify-between text-left group cursor-pointer border border-transparent hover:border-ink/6"
                >
                  <div className="flex items-center gap-3">
                    <span className="p-2 bg-paper rounded-xs border border-ink/6 shrink-0">
                      {getIcon(item.type)}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-ink group-hover:text-gold transition-colors">
                          {item.title}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 bg-paper text-muted border border-ink/6 rounded-xs">
                          {item.badge}
                        </span>
                      </div>
                      <p className="text-xs text-muted mt-0.5">{item.subtitle}</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-muted group-hover:text-ink transition-transform group-hover:translate-x-1" />
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
