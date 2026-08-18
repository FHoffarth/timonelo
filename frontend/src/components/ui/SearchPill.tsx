import React, { useState } from "react";
import { Search } from "lucide-react";

interface SearchPillProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  className?: string;
}

export default function SearchPill({
  placeholder = "Search any ship, port, route, or cabin...",
  onSearch,
  className = "",
}: SearchPillProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`relative flex items-center w-full max-w-2xl bg-white border border-[#0C1B2A]/10 rounded-full p-1.5 shadow-[0_8px_24px_-4px_rgba(12,27,42,0.08)] transition-all focus-within:border-[#C58A46] focus-within:ring-2 focus-within:ring-[#C58A46]/20 ${className}`}
    >
      <div className="pl-4 pr-2 text-[#5B6570]">
        <Search className="w-4 h-4 text-[#C58A46]" />
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="w-full py-2.5 text-sm text-[#0C1B2A] placeholder-[#5B6570]/70 bg-transparent focus:outline-none font-sans"
      />
      <button
        type="submit"
        className="px-6 py-2.5 rounded-full bg-[#0C1B2A] hover:bg-[#132238] text-white text-xs font-semibold tracking-wide transition-all shrink-0 active:scale-95 cursor-pointer"
      >
        Search
      </button>
    </form>
  );
}
