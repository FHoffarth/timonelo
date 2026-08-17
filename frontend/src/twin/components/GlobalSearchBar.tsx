import React, { useState, useRef, useEffect } from "react";
import { Search, MapPin, X, ArrowRight, Accessibility, Coffee, Sparkles } from "lucide-react";
import { searchTwin, SearchResultItem } from "../twinEngine";

interface GlobalSearchBarProps {
  onSelectResult: (item: SearchResultItem) => void;
}

export default function GlobalSearchBar({ onSelectResult }: GlobalSearchBarProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length > 0) {
      setResults(searchTwin(query));
      setIsOpen(true);
    } else {
      setResults([]);
      setIsOpen(false);
    }
  }, [query]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative w-full max-w-md z-40 pointer-events-auto">
      <div className="relative flex items-center">
        <Search className="absolute left-4 w-4 h-4 text-slate-400 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim().length > 0 && setIsOpen(true)}
          placeholder="Search 2,217 cabins, Marketplace Buffet, London Theatre..."
          className="w-full pl-11 pr-10 py-2.5 bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-2xl text-sm text-white placeholder-slate-400 focus:outline-none focus:border-sky-500/50 focus:ring-2 focus:ring-sky-500/20 shadow-2xl transition-all"
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="absolute right-3.5 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-2 shadow-2xl max-h-96 overflow-y-auto no-scrollbar space-y-1">
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-white/5">
            <span>Matches ({results.length})</span>
            <span className="text-sky-400 font-mono text-[10px]">Instant Navigation</span>
          </div>

          {results.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onSelectResult(item);
                setIsOpen(false);
                setQuery("");
              }}
              className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-400/20 flex items-center justify-center text-sky-400">
                  {item.category === "CABIN" ? (
                    <MapPin className="w-4 h-4" />
                  ) : item.category === "VENUE" ? (
                    <Coffee className="w-4 h-4" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                </div>
                <div>
                  <div className="text-sm font-semibold text-white group-hover:text-sky-300 transition-colors flex items-center gap-2">
                    {item.title}
                    {item.data?.accessible && (
                      <Accessibility className="w-3 h-3 text-sky-400" />
                    )}
                  </div>
                  <div className="text-xs text-slate-400">{item.subtitle}</div>
                </div>
              </div>

              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
