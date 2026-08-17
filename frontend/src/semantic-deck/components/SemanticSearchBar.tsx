import React, { useState, useRef, useEffect } from "react";
import { Search, MapPin, X, ArrowRight, Accessibility } from "lucide-react";
import { SemanticObject } from "../types";

interface SemanticSearchBarProps {
  onSearch: (query: string) => SemanticObject[];
  onSelectObject: (obj: SemanticObject) => void;
}

export default function SemanticSearchBar({
  onSearch,
  onSelectObject,
}: SemanticSearchBarProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<SemanticObject[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length > 0) {
      setResults(onSearch(query));
      setIsOpen(true);
    } else {
      setResults([]);
      setIsOpen(false);
    }
  }, [query, onSearch]);

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
    <div ref={containerRef} className="relative w-full max-w-md z-40 select-none">
      <div className="relative flex items-center">
        <Search className="absolute left-4 w-4 h-4 text-slate-400 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim().length > 0 && setIsOpen(true)}
          placeholder="Search cabin 14122, Marketplace Buffet, Suites..."
          className="w-full pl-11 pr-10 py-2 bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-2xl text-xs text-white placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 shadow-2xl transition-all font-sans"
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="absolute right-3 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-2 shadow-2xl max-h-96 overflow-y-auto no-scrollbar space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-white/5">
            <span>Semantic Results ({results.length})</span>
            <span className="text-sky-400 font-mono">Select & Focus</span>
          </div>

          {results.map((obj) => (
            <button
              key={obj.id}
              onClick={() => {
                onSelectObject(obj);
                setIsOpen(false);
                setQuery("");
              }}
              className="w-full px-3 py-2 rounded-xl text-left hover:bg-white/5 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-lg bg-sky-500/10 border border-sky-400/20 flex items-center justify-center text-sky-400 font-mono font-bold text-xs">
                  {obj.deck}
                </div>
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-sky-300 transition-colors flex items-center gap-1.5">
                    {obj.label}
                    {obj.accessible && (
                      <span className="text-[10px] text-sky-400 font-bold">H</span>
                    )}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    {obj.category_label} • {obj.zone.replace("_", " ")}
                  </div>
                </div>
              </div>

              <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
